#%%
#Applying xA model to Brasileirão 2025 data
"""Load the trained xA models and apply them to Brasileirão possession chains."""

import pandas as pd
import numpy as np
import warnings
from itertools import combinations_with_replacement
from joblib import load
from mplsoccer import Pitch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

#%%
# Loading data and trained models

df = pd.read_parquet("possesion_chains_brasileirao_2025.parquet")
df = df.reset_index(drop=True)

xA_gbc = load("xA_gbc_model.joblib")
xA_lr = load("xA_lr_model.joblib")
xA_var = load("xA_model_vars.joblib")

print(f"Loaded {len(df)} events, {len(xA_var)} model variables")

#%%
# Preparing polynomial variables
"""Build the same polynomial features used during training."""

base_var = ["x0", "x1", "c0", "c1"]

inputs = []
inputs.extend(combinations_with_replacement(base_var, 1))
inputs.extend(combinations_with_replacement(base_var, 2))
inputs.extend(combinations_with_replacement(base_var, 3))

for i in inputs:
    if len(i) > 1:
        column = ""
        x = 1
        for c in i:
            column += c
            x = x * df[c]
        df[column] = x

#%%
# Extracting qualifier-based binary features for passes
"""Same extraction function as training."""

def extract_pass_qualifiers(qualifiers):
    """Extract binary features from Opta pass qualifiers."""
    qual_values = set()
    if isinstance(qualifiers, (list, np.ndarray)):
        for q in qualifiers:
            qual_values.add(q["type"]["value"])
    return {
        "is_cross": int(2 in qual_values),
        "is_through_ball": int(4 in qual_values),
        "is_freekick": int(5 in qual_values),
        "is_corner": int(6 in qual_values),
        "is_offensive": int(286 in qual_values),
    }

passes = df.loc[df["type_displayName"] == "Pass"].copy()
qual_features = passes["qualifiers"].apply(extract_pass_qualifiers)
qual_df = pd.DataFrame(qual_features.tolist(), index=passes.index)
passes = pd.concat([passes, qual_df], axis=1)

print(f"Passes: {len(passes)}")

#%%
# Predicting xA for Brasileirão passes
"""Step 1: predict P(this pass assists a shot) using trained GBC
Step 2: predict E[xG | assist] using trained LR
xA = P(assist) * E[xG | assist]"""

X = passes[xA_var].values

# Step 1: assist probability
passes["assist_prob"] = xA_gbc.predict_proba(X)[::, 1]

# Step 2: xG if assist
passes["xG_if_assist"] = np.clip(xA_lr.predict(X), 0, 1)

# xA
passes["xA"] = passes["assist_prob"] * passes["xG_if_assist"]

print(f"Passes with xA: {len(passes)}")
print(passes[["assist_prob", "xG_if_assist", "xA"]].describe())

#%%
# Plotting a possession chain with xA values
"""Plot with arrow widths proportional to xA value."""

shot_types = ("MissedShots", "SavedShot", "Goal", "ShotOnPost")

#pick first chain that ended with a shot
shot_chain_id = df.loc[df["shot_end"] == 1, "possesion_chain"].iloc[0]
chain = df.loc[df["possesion_chain"] == shot_chain_id]

#for plotting we need y coordinates
if "y0" not in df.columns:
    df["y0"] = (100 - df["y"]) * 68 / 100
    df["y1"] = (100 - df["endY"]) * 68 / 100
    df.loc[df["type_displayName"].isin(shot_types), "y1"] = 34
    chain = df.loc[df["possesion_chain"] == shot_chain_id]

passes_in = passes.loc[passes["possesion_chain"] == shot_chain_id]
max_value = passes_in["xA"].max()

not_pass = chain.loc[~chain["type_displayName"].isin(["Pass"] + list(shot_types))].iloc[:-1]
shot = chain.iloc[-1]

pitch = Pitch(line_color="black", pitch_type="custom", pitch_length=105, pitch_width=68, line_zorder=2)
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)

for i, row in passes_in.iterrows():
    value = row["xA"]
    line_width = (value / max_value * 10) if max_value > 0 else 1
    angle = np.arctan((row.y1 - row.y0) / (row.x1 - row.x0 + 1e-6)) * 180 / np.pi
    pitch.arrows(row.x0, row.y0, row.x1, row.y1,
                 alpha=0.6, width=line_width, zorder=2, color="green", ax=ax["pitch"])
    ax["pitch"].text((row.x0 + row.x1 - 8) / 2, (row.y0 + row.y1 - 4) / 2,
                     str(value)[:5], fontweight="bold", color="green", zorder=4,
                     fontsize=20, rotation=int(angle))

pitch.arrows(shot.x0, shot.y0, shot.x1, shot.y1,
             width=2, color="red", ax=ax["pitch"], zorder=3)
pitch.lines(not_pass.x0, not_pass.y0, not_pass.x1, not_pass.y1,
            color="grey", lw=1.5, ls="dotted", ax=ax["pitch"])
ax["title"].text(0.5, 0.5, "Passes leading to a shot - xA values", ha="center", va="center", fontsize=30)
plt.show()

#%%
# Team and game-level xA summary
"""Aggregate xA by team and game for downstream analysis."""

team_game_summary = passes[["teamId", "game_id", "xA"]].groupby(["teamId", "game_id"]).agg(
    total_xA=("xA", "sum"),
    mean_xA=("xA", "mean"),
    pass_count=("xA", "count")
).reset_index()
team_game_summary = team_game_summary.sort_values(["game_id", "total_xA"], ascending=[True, False])
print(f"Shape: {team_game_summary.shape}")
print(team_game_summary.head(10))

#%%
# Save xA results to parquet for downstream use in the orchestrator
passes[["game_id", "teamId", "id", "xA"]].to_parquet(
    "xA_brasileirao_2025.parquet", index=False
)
print("Saved xA_brasileirao_2025.parquet")
