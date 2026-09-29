#%%
#Training xT model (action-based) on Premier League data
"""Train action-based Expected Threat models on PL possession chains.
Step 1: GradientBoostingClassifier to predict P(chain ends with shot)
Step 2: LinearRegression to predict E[xG | shot]
Models are saved for use on Brasileirão data."""

import pandas as pd
import numpy as np
import json
import os
import glob
import gc
import pathlib
import warnings
import time
import logging
import shutil
import sys
import tempfile

from sklearn.metrics import brier_score_loss, log_loss, mean_squared_error
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
LOG_DIR    = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH   = LOG_DIR / f"xT_retrain_{time.strftime('%H%M')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)
log = logging.getLogger("xT_model")
log.info("[boot] imports done; log file = %s", LOG_PATH)


def _log_uncaught(exc_type, exc, tb):
    log.error("Uncaught exception", exc_info=(exc_type, exc, tb))

sys.excepthook = _log_uncaught

#%%
# Loading PL training data
"""Load all european match JSONs from xG_Training_data/."""

game_ids = None  # discovered via glob below

TRAIN_DIR  = r"D:/jose_americo/laboratorio-match-analysis-2026/xG_Training_data"
SHARD_DIR  = SCRIPT_DIR / "_shards"
if SHARD_DIR.exists():
    shutil.rmtree(SHARD_DIR)
SHARD_DIR.mkdir(parents=True, exist_ok=True)
log.info("[shard] writing per-file shards to %s", SHARD_DIR)
t0 = time.time()
log.info("[scan] globbing %s ...", TRAIN_DIR)
paths = sorted(glob.glob(os.path.join(TRAIN_DIR, "*.json")))
log.info("[scan] found %d JSONs in %.1fs", len(paths), time.time()-t0)

# Prune to columns we actually use INSIDE the loop. Full json_normalize output
# carries 70+ columns including very heavy object fields (per-event
# satisfiedEvents arrays, nested tags, etc.) — accumulating those across 1826
# matches OOMs before concat is even reached.
NEEDED_COLS = [
    "game_id", "teamId", "period_value", "type_displayName", "type_value",
    "outcomeType_value",
    "is_dead_ball_restart", "qset",
    "isShot", "isGoal",
    "x", "y", "endX", "endY",
]

skipped = 0
t0 = time.time()
for i, path in enumerate(paths):
    if i % 100 == 0:
        log.info("[load] %d/%d (%.0fs elapsed, skipped=%d)", i, len(paths), time.time()-t0, skipped)
        gc.collect()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, MemoryError):
        skipped += 1
        continue
    if not data or "events" not in data or not data["events"]:
        skipped += 1
        continue
    temp_df = pd.json_normalize(data["events"], sep="_")
    temp_df["game_id"] = int(os.path.splitext(os.path.basename(path))[0])
    if "qualifiers" in temp_df.columns:
        temp_df["is_dead_ball_restart"] = temp_df["qualifiers"].apply(
            lambda qs: isinstance(qs, list) and any(
                q.get("type", {}).get("value") in (5, 107) for q in qs
            )
        )
        # Per-shot qualifier display-name set (small set of strings) so
        # the heavy raw qualifiers list can be dropped before sharding.
        is_shot_mask = temp_df.get("isShot", pd.Series(False, index=temp_df.index)).astype(bool)
        qset_col = pd.Series([None] * len(temp_df), index=temp_df.index, dtype=object)
        if is_shot_mask.any():
            qset_col.loc[is_shot_mask] = temp_df.loc[is_shot_mask, "qualifiers"].apply(
                lambda qs: tuple(sorted({q.get("type", {}).get("displayName", "") for q in qs}))
                if isinstance(qs, list) else tuple()
            )
        temp_df["qset"] = qset_col
    else:
        temp_df["is_dead_ball_restart"] = False
        temp_df["qset"] = None
    # Per-frame prune so peak memory stays bounded regardless of file count.
    keep = [c for c in NEEDED_COLS if c in temp_df.columns]
    temp_df = temp_df[keep]
    shard_path = SHARD_DIR / f"{int(temp_df['game_id'].iloc[0])}.parquet"
    temp_df.to_parquet(shard_path, index=False, compression="snappy")
    del temp_df, data
log.info("[load] done in %.0fs; reading shard dataset ...", time.time()-t0)

log.info("[shard] all shards written; reading dataset back ...")
t0 = time.time()
df = pd.read_parquet(SHARD_DIR, engine="pyarrow")
df = df.reset_index(drop=True)
log.info("[shard] dataset loaded in %.0fs: %d rows, mem~%.0fMB",
         time.time() - t0, len(df), df.memory_usage(deep=True).sum() / 1e6)

#%%
# Preparing data
"""Same pipeline as possession_chain.py: filter admin events, lost aerials,
corners, goalkeeper events. Mark kickedOut and chain boundaries."""

# Shift only the columns we actually need — full-frame shift OOMs on
# object dtypes when fill_value=0 forces a re-allocation across all blocks.
next_type      = df["type_displayName"].shift(-1)
next_type_val  = df["type_value"].shift(-1)
next_game      = df["game_id"].shift(-1)
next_period    = df["period_value"].shift(-1)

df["nextEvent"] = next_type
next_dead_ball = df["is_dead_ball_restart"].shift(-1, fill_value=False).astype(bool)
df["kickedOut"] = ((next_type_val == 6) | next_dead_ball).astype(int)

# force chain break at half-time and game boundaries
boundary = (df["game_id"] != next_game) | (df["period_value"] != next_period)
df.loc[boundary, "kickedOut"] = 1
df.loc[boundary, "nextEvent"] = None

# Single boolean mask combining every drop. Avoids materialising the full
# RangeIndex four times via .drop and is much lighter on memory.
type_name = df["type_displayName"]
keep = ~(
    type_name.isin([
        "Start", "End", "FormationSet", "FormationChange",
        "Card", "SubstitutionOff", "SubstitutionOn",
        "OffsideGiven", "OffsideProvoked",
        "CornerAwarded",
        "Save", "Claim", "Punch", "KeeperPickup",
        "KeeperSweeper", "PenaltyFaced",
    ])
    | ((type_name == "Aerial") & (df["outcomeType_value"] == 0))
)
df = df.loc[keep].reset_index(drop=True)
log.info("After filtering: %d events", len(df))

#%%
# Isolating possession chains

def isolateChains(df):
    """Vectorised pass over numpy arrays — same logic as the original
    iterrows version, ~50x faster. Chain id depends on running stop counter,
    so it remains a Python loop, but it operates only on raw numpy arrays
    and writes the chain/team columns once at the end."""
    df = df.reset_index(drop=True)
    # single-column shift — full-frame shift OOMs on object dtypes at scale
    df["nextTeamId"] = df["teamId"].shift(-1, fill_value=0)

    teamId       = df["teamId"].values
    nextTeamId   = df["nextTeamId"].values
    period       = df["period_value"].values
    game         = df["game_id"].values
    type_name    = df["type_displayName"].values
    outcome      = df["outcomeType_value"].values
    kickedOut    = df["kickedOut"].values

    pass_aerial  = np.isin(type_name, ("Pass", "Aerial"))
    ball_touch   = np.isin(type_name, ("BallTouch", "BallRecovery"))
    shot_or_foul = np.isin(type_name, (
        "MissedShots", "SavedShot", "Goal", "ShotOnPost", "Foul", "OffsidePass"
    ))

    n = len(df)
    chain_arr = np.zeros(n, dtype=np.int64)
    team_arr  = np.zeros(n, dtype=teamId.dtype)

    cur_chain  = 0
    cur_team   = teamId[0]
    cur_period = period[0]
    cur_game   = game[0]
    stop = 0

    for i in range(n):
        if period[i] != cur_period or game[i] != cur_game:
            cur_chain += 1
            stop = 0
            cur_team   = teamId[i]
            cur_period = period[i]
            cur_game   = game[i]

        chain_arr[i] = cur_chain
        team_arr[i]  = cur_team

        if pass_aerial[i]:
            if teamId[i] == cur_team and outcome[i] == 0:
                stop += 1
            if teamId[i] != cur_team and outcome[i] == 1:
                stop += 1
        if ball_touch[i] and teamId[i] == nextTeamId[i]:
            stop += 2
        if shot_or_foul[i]:
            stop += 2
        if kickedOut[i] == 1:
            stop += 2

        if stop >= 2:
            cur_chain += 1
            stop = 0
            cur_team = nextTeamId[i]

    df["possesion_chain"]      = chain_arr
    df["possesion_chain_team"] = team_arr
    return df

df = isolateChains(df)
log.info("Total chains: %d", df['possesion_chain'].nunique())




print("rows:", len(df))
print("dtype isShot:", df["isShot"].dtype)
print("shots:", (df["isShot"] == True).sum())
import psutil; print("RAM %:", psutil.virtual_memory().percent)

import time
t = time.time()
import onnxruntime as ort
print("import ort:", round(time.time()-t, 2), "s")
print("ort version:", ort.__version__)
print("providers available:", ort.get_available_providers())

t = time.time()
so = ort.SessionOptions()
so.intra_op_num_threads = 1
so.inter_op_num_threads = 1
sess = ort.InferenceSession(
    r"d:\jose_americo\laboratorio-match-analysis-2025\xG_model.onnx",
    sess_options=so,
    providers=["CPUExecutionProvider"],
)
print("session create:", round(time.time()-t, 2), "s")
print("input:", sess.get_inputs()[0].name, sess.get_inputs()[0].shape)

#%%
# Loading the rebuilt xG model and labelling chain-ending shots
"""Use the production xG bundle (Tier-1 qualifier features + isotonic
calibration) to label shots. Penalties are KEPT — xT downstream is summed
without a penalty filter, so penalty chains belong in the label set, scored
from their own coordinates by the same model."""

XG_DIR = pathlib.Path(__file__).resolve().parent
XG_JSON = XG_DIR / "xG_model.json"
with open(XG_JSON, "r") as f:
    xg_bundle = json.load(f)
log.info("Loaded xG bundle: kind=%s, features=%d",
         xg_bundle['kind'], len(xg_bundle['features']))
#%%
GEOM_FEATURES = xg_bundle["geometry_features"]
QUALIFIER_FLAGS = xg_bundle["qualifier_flags"]
ALL_FEATURES = xg_bundle["features"]

if xg_bundle["kind"] == "gbm_isotonic":
    import onnxruntime as ort
    xg_bundle["_session"] = ort.InferenceSession(
        str(XG_DIR / xg_bundle["model_path"]),
        providers=["CPUExecutionProvider"],
    )

shot_types = ("MissedShots", "SavedShot", "Goal", "ShotOnPost")

def _build_shot_features(shots):
    shots = shots.copy()
    qset = shots["qset"].apply(lambda x: set(x) if x is not None else set())
    shots["is_penalty"] = qset.apply(lambda s: "Penalty" in s)
    shots["X"] = (100 - shots["x"]) * 105 / 100
    shots["C"] = (shots["y"] - 50).abs() * 68 / 100
    shots["Distance"] = np.sqrt(shots["X"] ** 2 + shots["C"] ** 2)
    raw = np.arctan(7.32 * shots["X"] /
                    (shots["X"] ** 2 + shots["C"] ** 2 - (7.32 / 2) ** 2))
    shots["Angle"] = np.where(raw > 0, raw, raw + np.pi)
    shots["X2"] = shots["X"] ** 2
    shots["C2"] = shots["C"] ** 2
    shots["AX"] = shots["Angle"] * shots["X"]
    for flag in QUALIFIER_FLAGS:
        shots[flag] = qset.apply(lambda s, f=flag: int(f in s))
    return shots

def _predict_xg(bundle, feat_df):
    if bundle["kind"] == "gbm_isotonic":
        sess = bundle["_session"]
        X = feat_df[ALL_FEATURES].values.astype(np.float32)
        probs = sess.run(None, {sess.get_inputs()[0].name: X})[1]
        return probs[:, 1]
    # GLM fallback (statsmodels params dict)
    p = bundle["params"]
    z = p["Intercept"] + sum(p[f] * feat_df[f].values for f in ALL_FEATURES)
    return 1.0 / (1.0 + np.exp(-z))

shot_mask = df["isShot"] == True
shots_feat = _build_shot_features(df.loc[shot_mask])
shots_feat["xG"] = _predict_xg(xg_bundle, shots_feat)

df["xG"] = 0.0
df.loc[shots_feat.index, "xG"] = shots_feat["xG"].values
log.info("Shots labelled: %d  (pens: %d)  sum_xG=%.1f",
         int((df['xG'] > 0).sum()),
         int(shots_feat['is_penalty'].sum()),
         df['xG'].sum())

#%%
# Finding chains that ended with shot and preparing chains

def prepareChains(df):
    """Vectorised. Marks chains that end with a shot, propagates the shot's
    xG to every event in that chain, walks back through preceding
    foul-ending chains and inherits the same xG (penalty/free-kick winning
    sequences), and finally keeps only events whose teamId matches the
    chain's modal team."""
    df = df.sort_values(["game_id", "period_value", "possesion_chain"]).reset_index(drop=True)

    last = df.groupby("possesion_chain", sort=False).tail(1)
    is_shot_end = last["type_displayName"].isin(shot_types)

    # Map chain -> xG of its last event (only for shot-ending chains)
    shot_chain_ids = last.loc[is_shot_end, "possesion_chain"].values
    shot_chain_xg  = last.loc[is_shot_end, "xG"].values
    chain_to_xg = dict(zip(shot_chain_ids, shot_chain_xg))

    # Walk-back: foul-ending chain immediately preceding a shot-ending chain
    # inherits the shot's xG (the foul that earned a free-kick / penalty).
    last_type_by_chain = dict(zip(last["possesion_chain"].values,
                                   last["type_displayName"].values))
    for cid in sorted(shot_chain_ids):
        xg = chain_to_xg[cid]
        k = cid - 1
        while k > 0 and last_type_by_chain.get(k) == "Foul":
            chain_to_xg[k] = xg
            k -= 1

    df["shot_end"] = df["possesion_chain"].isin(chain_to_xg).astype(int)
    df["xG"]       = df["possesion_chain"].map(chain_to_xg).fillna(0.0)

    # Keep only events whose teamId == the chain's modal team
    mode_team = df.groupby("possesion_chain", sort=False)["teamId"].agg(
        lambda s: s.mode().iloc[0]
    ).rename("chain_mode_team")
    df = df.merge(mode_team, on="possesion_chain", how="left")
    df = df.loc[df["teamId"] == df["chain_mode_team"]].drop(columns=["chain_mode_team"])
    return df

df = prepareChains(df)
log.info("Chains ending with shot: %d", df.loc[df['shot_end'] == 1, 'possesion_chain'].nunique())

#%%
# Preparing coordinates and filtering events with end coordinates

df = df.loc[df["endX"].notna() | df["type_displayName"].isin(shot_types)]
df["x0"] = df["x"] * 105 / 100
df["c0"] = abs(50 - df["y"]) * 68 / 100
df["x1"] = df["endX"] * 105 / 100
df["c1"] = abs(50 - df["endY"]) * 68 / 100
df.loc[df["type_displayName"].isin(shot_types), "x1"] = 105
df.loc[df["type_displayName"].isin(shot_types), "c1"] = 0

log.info("Events with coordinates: %d", len(df))

#%%
# Synthesising Carry events between consecutive same-team same-chain events.
"""Opta does not emit a 'Carry' event between touches. We infer one whenever
two consecutive events in the same chain belong to the same team and the
spatial gap between the prior event's release point and the next event's
start exceeds CARRY_MIN_DIST metres. The synthetic Carry inherits the
chain's xG and shot_end label, and goes through the same model as Pass."""

CARRY_MIN_DIST = 5.0  # metres on the 105x68 pitch

def synthesise_carries(df):
    df = df.sort_values(["game_id", "period_value", "possesion_chain"]).reset_index(drop=True)

    chain = df["possesion_chain"].values
    team  = df["teamId"].values
    x0    = df["x0"].values
    c0    = df["c0"].values
    x1    = df["x1"].values
    c1    = df["c1"].values

    same_chain = chain[:-1] == chain[1:]
    same_team  = team[:-1]  == team[1:]
    # release point of prev event (use endpoint if available else start)
    prev_x = np.where(np.isnan(x1[:-1]), x0[:-1], x1[:-1])
    prev_c = np.where(np.isnan(c1[:-1]), c0[:-1], c1[:-1])
    next_x = x0[1:]
    next_c = c0[1:]
    dist = np.sqrt((next_x - prev_x) ** 2 + (next_c - prev_c) ** 2)
    is_carry = same_chain & same_team & (dist >= CARRY_MIN_DIST) & ~np.isnan(prev_x) & ~np.isnan(next_x)

    if not is_carry.any():
        return df

    carries = pd.DataFrame({
        "game_id":           df["game_id"].values[1:][is_carry],
        "teamId":            df["teamId"].values[1:][is_carry],
        "period_value":      df["period_value"].values[1:][is_carry],
        "possesion_chain":   chain[1:][is_carry],
        "type_displayName": "Carry",
        "x0":                prev_x[is_carry],
        "c0":                prev_c[is_carry],
        "x1":                next_x[is_carry],
        "c1":                next_c[is_carry],
        "shot_end":          df["shot_end"].values[1:][is_carry],
        "xG":                df["xG"].values[1:][is_carry],
    })
    out = pd.concat([df, carries], ignore_index=True, sort=False)
    return out

n_before = len(df)
df = synthesise_carries(df)
log.info("Synthesised %d Carry events  (total events: %d)", len(df) - n_before, len(df))

#%%
# Action filter and feature set
"""Train/score on Pass, TakeOn (dribble), and synthetic Carry. The polynomial
basis was dropped: HistGradientBoostingRegressor learns interactions
natively, and the LinearRegression pipeline that needed it was removed."""

ACTION_TYPES = ("Pass", "TakeOn", "Carry")
var = ["x0", "x1", "c0", "c1"]
log.info("Model variables: %s", var)

#%%
# Training xT models
"""Step 1: HistGradientBoostingClassifier for P(chain ends with shot)
Step 2: HistGradientBoostingRegressor for E[xG | shot]
Both fit on raw (x0, x1, c0, c1). Trees learn interactions natively, so the
polynomial basis is gone. The regressor naturally produces values in the
xG range (no negative-prediction problem) but we still clip on output for
safety."""

actions = df.loc[df["type_displayName"].isin(ACTION_TYPES)].copy()
actions = actions.dropna(subset=var)
log.info("Training rows: %d  by type:", len(actions))
log.info("%s", actions["type_displayName"].value_counts().to_string())

# Game-level 80/20 split for honest evaluation
rng = np.random.default_rng(42)
all_games = actions["game_id"].unique()
rng.shuffle(all_games)
split = int(0.8 * len(all_games))
train_games = set(all_games[:split])
test_games  = set(all_games[split:])
tr = actions["game_id"].isin(train_games)
te = actions["game_id"].isin(test_games)
log.info("Holdout split: %d train games / %d test games", len(train_games), len(test_games))

# Step 1: shot probability model — held-out Brier + log-loss
gbc_model = HistGradientBoostingClassifier(
    max_iter=300, max_depth=6, learning_rate=0.05,
    l2_regularization=1.0, random_state=123
)
gbc_model.fit(actions.loc[tr, var].values, actions.loc[tr, "shot_end"].values)
p_te = gbc_model.predict_proba(actions.loc[te, var].values)[:, 1]
y_te = actions.loc[te, "shot_end"].values
log.info("GBC holdout  Brier=%.5f  logloss=%.4f  base_rate=%.4f",
         brier_score_loss(y_te, p_te), log_loss(y_te, p_te), y_te.mean())

# Step 2: xG-given-shot regressor — held-out RMSE + R²
shot_ended = actions.loc[actions["shot_end"] == 1]
tr2 = shot_ended["game_id"].isin(train_games)
te2 = shot_ended["game_id"].isin(test_games)
lr_model = HistGradientBoostingRegressor(
    max_iter=300, max_depth=6, learning_rate=0.05,
    l2_regularization=1.0, random_state=123
)
lr_model.fit(shot_ended.loc[tr2, var].values, shot_ended.loc[tr2, "xG"].values)
pred_raw = lr_model.predict(shot_ended.loc[te2, var].values)
pred_te  = np.clip(pred_raw, 0.0, 1.0)
y_te2    = shot_ended.loc[te2, "xG"].values
n_neg    = int((pred_raw < 0).sum())
ss_res   = float(((y_te2 - pred_te) ** 2).sum())
ss_tot   = float(((y_te2 - y_te2.mean()) ** 2).sum())
r2       = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
log.info("HGBR holdout RMSE=%.4f  R2=%.3f  raw_negatives=%d/%d",
         np.sqrt(mean_squared_error(y_te2, pred_te)), r2, n_neg, len(y_te2))

# Refit both on the full set for the saved artefacts
gbc_model.fit(actions[var].values, actions["shot_end"].values)
lr_model.fit(shot_ended[var].values, shot_ended["xG"].values)

#%%
# Saving trained models and variable list
"""Save both models and the variable list so xT_brasileirao.py can load them."""

from skl2onnx import to_onnx

gbc_path  = SCRIPT_DIR / "xT_gbc_model.onnx"
lr_path   = SCRIPT_DIR / "xT_lr_model.onnx"
vars_path = SCRIPT_DIR / "xT_model_vars.json"

sample = np.zeros((1, len(var)), dtype=np.float32)

gbc_onx = to_onnx(gbc_model, sample, options={id(gbc_model): {"zipmap": False}})
with open(gbc_path, "wb") as f:
    f.write(gbc_onx.SerializeToString())

lr_onx = to_onnx(lr_model, sample)
with open(lr_path, "wb") as f:
    f.write(lr_onx.SerializeToString())

with open(vars_path, "w") as f:
    json.dump(list(var), f, indent=2)

log.info("Models saved: %s, %s, %s", gbc_path.name, lr_path.name, vars_path.name)

# Clean up shards on success — keep them only if training crashed.
try:
    shutil.rmtree(SHARD_DIR)
    log.info("[shard] cleaned up %s", SHARD_DIR)
except OSError as e:
    log.warning("[shard] could not remove %s: %s", SHARD_DIR, e)
