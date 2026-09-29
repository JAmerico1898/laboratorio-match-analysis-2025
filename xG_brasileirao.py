#%%
# Apply trained xG model to Brasileirão 2025 events parquet.
# Penalties are scored from their coordinates (model-driven), but flagged
# via the is_penalty column so downstream code can filter to non-penalty xG.

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

EVENTS_PARQUET = Path(r"D:\jose_americo\laboratorio-match-analysis-2025\brasileirao_2025_events.parquet")
MODEL_JSON = Path("xG_model.json")
OUT_PARQUET = Path("xG_brasileirao_2025.parquet")

QUALIFIER_FLAGS = [
    "Head", "LeftFoot", "RightFoot", "OtherBodyPart",
    "RegularPlay", "FromCorner", "DirectFreekick", "SetPiece", "FastBreak",
    "BigChance", "Volley", "OneOnOne", "FirstTouch", "Assisted",
    "Blocked",
]
GEOM_FEATURES = ["Angle", "Distance", "X", "C", "X2", "C2", "AX"]
ALL_FEATURES = GEOM_FEATURES + QUALIFIER_FLAGS

#%%
# ------------------------------------------------------------------------
# Load events and trained model
# ------------------------------------------------------------------------

df = pd.read_parquet(EVENTS_PARQUET)
print(f"Loaded events: {len(df):,}  games: {df['game_id'].nunique()}")

with open(MODEL_JSON, "r") as f:
    bundle = json.load(f)
print(f"Loaded model kind={bundle['kind']}")

#%%
# ------------------------------------------------------------------------
# Feature engineering — same logic as xG_model.py
# ------------------------------------------------------------------------

def extract_qualifier_set(qualifiers):
    """Qualifiers in this parquet are JSON-encoded strings; in JSONs they're lists of dicts."""
    if qualifiers is None:
        return set()
    if isinstance(qualifiers, str):
        try:
            qualifiers = json.loads(qualifiers)
        except Exception:
            return set()
    try:
        if len(qualifiers) == 0:
            return set()
    except TypeError:
        return set()
    out = set()
    for q in qualifiers:
        try:
            out.add(q.get("type", {}).get("displayName", ""))
        except Exception:
            pass
    return out

shots = df.loc[df["isShot"] == True].copy()
print(f"Shots: {len(shots):,}")

shots["_qset"] = shots["qualifiers"].apply(extract_qualifier_set)
shots["is_penalty"] = shots["_qset"].apply(lambda s: "Penalty" in s)

shots["X"] = (100 - shots["x"]) * 105 / 100
shots["Y"] = shots["y"] * 68 / 100
shots["C"] = (shots["y"] - 50).abs() * 68 / 100
shots["Distance"] = np.sqrt(shots["X"] ** 2 + shots["C"] ** 2)
raw_angle = np.arctan(7.32 * shots["X"] / (shots["X"] ** 2 + shots["C"] ** 2 - (7.32 / 2) ** 2))
shots["Angle"] = np.where(raw_angle > 0, raw_angle, raw_angle + np.pi)
shots["X2"] = shots["X"] ** 2
shots["C2"] = shots["C"] ** 2
shots["AX"] = shots["Angle"] * shots["X"]

for flag in QUALIFIER_FLAGS:
    shots[flag] = shots["_qset"].apply(lambda s, f=flag: int(f in s))

shots["Goal"] = shots["isGoal"].apply(lambda x: 1 if x is True else 0)
shots = shots.drop(columns=["_qset"])

#%%
# ------------------------------------------------------------------------
# Predict
# ------------------------------------------------------------------------

if bundle["kind"] == "glm":
    params = bundle["params"]
    intercept = params.get("Intercept", 0.0)
    coefs = np.array([params[f] for f in ALL_FEATURES])
    Z = intercept + shots[ALL_FEATURES].values @ coefs
    shots["xG"] = 1.0 / (1.0 + np.exp(-Z))
elif bundle["kind"] == "gbm_isotonic":
    import onnxruntime as ort

    onnx_path = MODEL_JSON.parent / bundle["model_path"]
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    X = shots[ALL_FEATURES].values.astype(np.float32)
    probs = session.run(None, {input_name: X})[1]
    shots["xG"] = probs[:, 1]
else:
    raise RuntimeError(f"unknown model kind: {bundle['kind']}")

print(shots["xG"].describe())

#%%
# ------------------------------------------------------------------------
# Save parquet (schema-additive: adds is_penalty)
# ------------------------------------------------------------------------

out = shots[["game_id", "teamId", "id", "xG", "Goal", "is_penalty"]]
out.to_parquet(OUT_PARQUET, index=False)
print(f"Saved {OUT_PARQUET.resolve()}  rows={len(out):,}")

#%%
# ------------------------------------------------------------------------
# Sanity checks
# ------------------------------------------------------------------------

print("\n=== Vasco x Chapecoense (1955953) ===")
g = shots[shots["game_id"] == 1955953]
if len(g):
    summary = (
        g.groupby("teamId")
        .agg(
            shots=("xG", "size"),
            goals=("Goal", "sum"),
            xG_all=("xG", "sum"),
            xG_np=("xG", lambda s: s[~g.loc[s.index, "is_penalty"]].sum()),
            pens=("is_penalty", "sum"),
        )
    )
    print(summary)

print("\n=== Brasileirão aggregate sanity ===")
agg_all = shots["xG"].sum()
agg_np = shots.loc[~shots["is_penalty"], "xG"].sum()
goals_all = shots["Goal"].sum()
goals_np = shots.loc[~shots["is_penalty"], "Goal"].sum()
print(f"Total shots: {len(shots):,}  (pens: {int(shots['is_penalty'].sum())})")
print(f"Sum xG (all):  {agg_all:.1f}   actual goals (all): {goals_all}")
print(f"Sum xG (np):   {agg_np:.1f}   actual goals (np):  {goals_np}")
print(f"Inflation (all):  {(agg_all - goals_all)/goals_all*100:+.1f}%")
print(f"Inflation (np):   {(agg_np - goals_np)/goals_np*100:+.1f}%")
