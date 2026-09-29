#%%
# xG model trainer — European leagues (Opta JSONs)
# Trains two models (logistic GLM + isotonic-calibrated HistGradientBoosting),
# evaluates with game-level 80/20 + leave-one-block-out CV, saves the winner.

import os
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import statsmodels.api as sm
import statsmodels.formula.api as smf

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

TRAIN_DIR = Path(r"D:\jose_americo\laboratorio-match-analysis-2026\xG_Training_data")
OUT_JSON = Path("xG_model.json")
OUT_ONNX = Path("xG_model.onnx")

#%%
# ------------------------------------------------------------------------
# Load all training JSONs
# ------------------------------------------------------------------------

def load_events():
    files = sorted(TRAIN_DIR.glob("*.json"))
    print(f"Loading {len(files)} game files from {TRAIN_DIR}")
    dfs = []
    for p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"skip {p.name}: {e}")
            continue
        if not data or not data.get("events"):
            continue
        ev = pd.json_normalize(data["events"], sep="_")
        ev["game_id"] = int(p.stem)
        dfs.append(ev)
    df = pd.concat(dfs, ignore_index=True)
    return df

df = load_events()
print(f"Total events: {len(df):,}")

#%%
# ------------------------------------------------------------------------
# Feature engineering
# ------------------------------------------------------------------------

QUALIFIER_FLAGS = [
    # body part
    "Head", "LeftFoot", "RightFoot", "OtherBodyPart",
    # play pattern
    "RegularPlay", "FromCorner", "DirectFreekick", "SetPiece", "FastBreak",
    # situational flags
    "BigChance", "Volley", "OneOnOne", "FirstTouch", "Assisted",
    # outcome modifier — defender block before the ball reaches goal
    "Blocked",
]

def extract_qualifier_set(qualifiers):
    """Return set of qualifier displayName strings present on a shot."""
    if not isinstance(qualifiers, list):
        return set()
    return {q.get("type", {}).get("displayName", "") for q in qualifiers}

def is_penalty(qset):
    return "Penalty" in qset

def build_shots(df):
    shots = df.loc[df["isShot"] == True].copy()

    # qualifier set per shot
    shots["_qset"] = shots["qualifiers"].apply(extract_qualifier_set)
    shots["is_penalty"] = shots["_qset"].apply(is_penalty)

    # geometry: Opta 0-100 -> 105x68 pitch, goal at x=0
    shots["X"] = (100 - shots["x"]) * 105 / 100
    shots["Y"] = shots["y"] * 68 / 100
    shots["C"] = (shots["y"] - 50).abs() * 68 / 100
    shots["Distance"] = np.sqrt(shots["X"] ** 2 + shots["C"] ** 2)
    raw_angle = np.arctan(7.32 * shots["X"] / (shots["X"] ** 2 + shots["C"] ** 2 - (7.32 / 2) ** 2))
    shots["Angle"] = np.where(raw_angle > 0, raw_angle, raw_angle + np.pi)
    shots["X2"] = shots["X"] ** 2
    shots["C2"] = shots["C"] ** 2
    shots["AX"] = shots["Angle"] * shots["X"]

    # Tier-1 binary qualifier flags
    for flag in QUALIFIER_FLAGS:
        shots[flag] = shots["_qset"].apply(lambda s, f=flag: int(f in s))

    shots["Goal"] = shots["isGoal"].apply(lambda x: 1 if x is True else 0)

    shots = shots.drop(columns=["_qset"])
    return shots

shots_all = build_shots(df)
print(f"Total shots: {len(shots_all):,}  (pens: {shots_all['is_penalty'].sum():,})")

# train only on non-penalty shots
shots = shots_all.loc[~shots_all["is_penalty"]].copy()
print(f"Training shots (no pens): {len(shots):,}  goals: {shots['Goal'].sum():,}  conv: {shots['Goal'].mean():.3f}")

GEOM_FEATURES = ["Angle", "Distance", "X", "C", "X2", "C2", "AX"]
ALL_FEATURES = GEOM_FEATURES + QUALIFIER_FLAGS

#%%
# ------------------------------------------------------------------------
# Game-level splitter & block helpers
# ------------------------------------------------------------------------

def game_block(gid):
    """Bucket each game into one of 5 blocks based on id prefix."""
    return str(gid)[:4]

shots["block"] = shots["game_id"].apply(game_block)
print("Block sizes:", shots.groupby("block")["game_id"].nunique().to_dict())

def split_games(shots, frac=0.8, seed=42):
    rng = np.random.default_rng(seed)
    games = shots["game_id"].unique()
    rng.shuffle(games)
    cut = int(len(games) * frac)
    train_g = set(games[:cut])
    test_g = set(games[cut:])
    return shots[shots["game_id"].isin(train_g)].copy(), shots[shots["game_id"].isin(test_g)].copy()

#%%
# ------------------------------------------------------------------------
# Model 1 — GLM (statsmodels logit) on geometry + Tier-1 flags
# ------------------------------------------------------------------------

def fit_glm(train):
    formula = "Goal ~ " + " + ".join(ALL_FEATURES)
    m = smf.glm(formula=formula, data=train, family=sm.families.Binomial()).fit()
    return m

def predict_glm(model, X):
    return model.predict(X)

#%%
# ------------------------------------------------------------------------
# Model 2 — HistGradientBoosting + isotonic calibration
# ------------------------------------------------------------------------

def fit_gbm(train):
    base = HistGradientBoostingClassifier(
        max_iter=400,
        max_depth=6,
        learning_rate=0.05,
        l2_regularization=1.0,
        random_state=0,
    )
    cal = CalibratedClassifierCV(base, method="isotonic", cv=5)
    cal.fit(train[ALL_FEATURES].values, train["Goal"].values)
    return cal

def predict_gbm(model, X):
    return model.predict_proba(X[ALL_FEATURES].values)[:, 1]

#%%
# ------------------------------------------------------------------------
# Evaluation helpers
# ------------------------------------------------------------------------

def score(y, p, label=""):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return {
        "label": label,
        "n": len(y),
        "goals": int(y.sum()),
        "sum_xG": float(p.sum()),
        "brier": brier_score_loss(y, p),
        "logloss": log_loss(y, p),
        "auc": roc_auc_score(y, p),
    }

def reliability(y, p, bins=10):
    p = np.asarray(p)
    y = np.asarray(y)
    edges = np.linspace(0, 1, bins + 1)
    rows = []
    for i in range(bins):
        mask = (p >= edges[i]) & (p < edges[i + 1] if i < bins - 1 else p <= edges[i + 1])
        if mask.sum() == 0:
            continue
        rows.append((f"[{edges[i]:.2f},{edges[i+1]:.2f})", int(mask.sum()), float(p[mask].mean()), float(y[mask].mean())))
    return pd.DataFrame(rows, columns=["bucket", "n", "pred_mean", "obs_rate"])

#%%
# ------------------------------------------------------------------------
# 80 / 20 evaluation
# ------------------------------------------------------------------------

train, test = split_games(shots, frac=0.8, seed=42)
print(f"\n=== 80/20 split — train: {len(train):,} shots, test: {len(test):,} shots ===")

glm = fit_glm(train)
gbm = fit_gbm(train)

p_glm = predict_glm(glm, test)
p_gbm = predict_gbm(gbm, test)

res_glm = score(test["Goal"].values, p_glm.values if hasattr(p_glm, "values") else p_glm, "GLM")
res_gbm = score(test["Goal"].values, p_gbm, "GBM+isotonic")

print("\n--- 80/20 test metrics ---")
for r in (res_glm, res_gbm):
    print(f"{r['label']:18s} n={r['n']:5d}  goals={r['goals']:4d}  sum_xG={r['sum_xG']:7.1f}  "
          f"Brier={r['brier']:.5f}  LogLoss={r['logloss']:.5f}  AUC={r['auc']:.4f}")

print("\n--- Reliability (GLM) ---")
print(reliability(test["Goal"].values, np.asarray(p_glm)).to_string(index=False))
print("\n--- Reliability (GBM+isotonic) ---")
print(reliability(test["Goal"].values, p_gbm).to_string(index=False))

#%%
# ------------------------------------------------------------------------
# Leave-one-block-out CV
# ------------------------------------------------------------------------

print("\n=== Leave-one-block-out CV ===")
blocks = sorted(shots["block"].unique())
cv_glm, cv_gbm = [], []
for b in blocks:
    tr = shots[shots["block"] != b]
    te = shots[shots["block"] == b]
    g = fit_glm(tr)
    h = fit_gbm(tr)
    pg = np.asarray(g.predict(te))
    ph = predict_gbm(h, te)
    rg = score(te["Goal"].values, pg, f"GLM/holdout={b}")
    rh = score(te["Goal"].values, ph, f"GBM/holdout={b}")
    cv_glm.append(rg)
    cv_gbm.append(rh)
    print(f"holdout block {b}: GLM Brier={rg['brier']:.5f} LogLoss={rg['logloss']:.5f} AUC={rg['auc']:.4f}  |  "
          f"GBM Brier={rh['brier']:.5f} LogLoss={rh['logloss']:.5f} AUC={rh['auc']:.4f}")

mean_glm_brier = np.mean([r["brier"] for r in cv_glm])
mean_gbm_brier = np.mean([r["brier"] for r in cv_gbm])
mean_glm_ll = np.mean([r["logloss"] for r in cv_glm])
mean_gbm_ll = np.mean([r["logloss"] for r in cv_gbm])
print(f"\nMean CV Brier   GLM={mean_glm_brier:.5f}  GBM={mean_gbm_brier:.5f}")
print(f"Mean CV LogLoss GLM={mean_glm_ll:.5f}  GBM={mean_gbm_ll:.5f}")

#%%
# ------------------------------------------------------------------------
# Pick winner, refit on all data, save
# ------------------------------------------------------------------------

winner = "GBM" if (mean_gbm_brier + mean_gbm_ll) < (mean_glm_brier + mean_glm_ll) else "GLM"
print(f"\nWinner: {winner}")

if winner == "GLM":
    final = fit_glm(shots)
    bundle = {
        "kind": "glm",
        "params": {k: float(v) for k, v in final.params.items()},
        "features": ALL_FEATURES,
        "qualifier_flags": QUALIFIER_FLAGS,
        "geometry_features": GEOM_FEATURES,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(bundle, f, indent=2)
    print(f"Saved {OUT_JSON.resolve()}  (kind={bundle['kind']})")
else:
    final = fit_gbm(shots)
    from skl2onnx import to_onnx

    n_features = len(ALL_FEATURES)
    onx = to_onnx(
        final,
        np.zeros((1, n_features), dtype=np.float32),
        options={id(final): {"zipmap": False}},
    )
    with open(OUT_ONNX, "wb") as f:
        f.write(onx.SerializeToString())
    bundle = {
        "kind": "gbm_isotonic",
        "model_path": OUT_ONNX.name,
        "features": ALL_FEATURES,
        "qualifier_flags": QUALIFIER_FLAGS,
        "geometry_features": GEOM_FEATURES,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(bundle, f, indent=2)
    print(f"Saved {OUT_JSON.resolve()} + {OUT_ONNX.resolve()}  (kind={bundle['kind']})")
