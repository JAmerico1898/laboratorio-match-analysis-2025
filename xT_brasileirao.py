#%%
#Applying xT model to Brasileirão 2025 data
"""Load the trained xT models and apply them to Brasileirão possession chains."""

import json
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import onnxruntime as ort

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).resolve().parent

#%%
# Loading data and trained models

df = pd.read_parquet(r"D:/jose_americo/laboratorio-match-analysis-2025/possesion_chains_brasileirao_2025.parquet")
df = df.reset_index(drop=True)

gbc_session = ort.InferenceSession(str(SCRIPT_DIR / "xT_gbc_model.onnx"), providers=["CPUExecutionProvider"])
lr_session = ort.InferenceSession(str(SCRIPT_DIR / "xT_lr_model.onnx"), providers=["CPUExecutionProvider"])
with open(SCRIPT_DIR / "xT_model_vars.json", "r") as f:
    var = json.load(f)

print(f"Loaded {len(df)} events, {len(var)} model variables")

#%%
# Predicting xT for actions present in the upstream parquet.
"""The upstream possession-chain parquet contains Pass events plus a few
shot/dead-ball types. Carries are NOT synthesised here on purpose:
MatchAnalysis_PlayStyle_2025.py already builds its own carry rows in
progcarry_df (lines 245–317) and the merge by (game_id, team_id, event_id)
broadcasts our per-event xT to both the real Pass row and the synthetic
carry row. Adding carries on this side too would double-count.
Carries DO appear in xT_model.py training (synthesised on raw JSONs) so the
trained model still benefits from that signal."""

ACTION_TYPES = ("Pass", "TakeOn")
passes = df.loc[df["type_displayName"].isin(ACTION_TYPES)].copy()
passes = passes.dropna(subset=var)
X = passes[var].values.astype(np.float32)

# Step 1: shot probability
gbc_input = gbc_session.get_inputs()[0].name
passes["shot_prob"] = gbc_session.run(None, {gbc_input: X})[1][:, 1]

# Step 2: xG prediction — HGBR rarely predicts <0, but we still clip for safety.
lr_input = lr_session.get_inputs()[0].name
raw_xg = np.asarray(lr_session.run(None, {lr_input: X})[0]).reshape(-1)
n_neg = int((raw_xg < 0).sum())
print(f"xG_pred raw negatives: {n_neg}/{len(raw_xg)} "
      f"(min={raw_xg.min():.4f}, max={raw_xg.max():.4f})")
passes["xG_pred"] = np.clip(raw_xg, 0.0, 1.0)

# xT
passes["xT"] = passes["xG_pred"] * passes["shot_prob"]

print(f"Actions with xT: {len(passes)}  by type:")
print(passes["type_displayName"].value_counts().to_string())
print(passes[["xG_pred", "shot_prob", "xT"]].describe())

#%%
# Team and game-level xT summary
"""Aggregate xT by team and game for downstream analysis."""

team_game_summary = passes[["teamId", "game_id", "xT"]].groupby(["teamId", "game_id"]).agg(
    total_xT=("xT", "sum"),
    mean_xT=("xT", "mean"),
    action_count=("xT", "count")
).reset_index()
team_game_summary = team_game_summary.sort_values(["game_id", "total_xT"], ascending=[True, False])
print(f"Shape: {team_game_summary.shape}")
print(team_game_summary.head(10))

#%%
# Save xT results to parquet for downstream use in the orchestrator
passes[["game_id", "teamId", "id", "xT"]].to_parquet(
    "xT_brasileirao_2025.parquet", index=False
)
print(f"Saved xT_brasileirao_2025.parquet  rows={len(passes)}  "
      f"sum_xT={passes['xT'].sum():.2f}  max_xT={passes['xT'].max():.4f}")
