#%%
# PlayStyle 2025 - Orchestrator
import pandas as pd
import numpy as np
import json
# plotting
import os
import pathlib
import warnings
import statsmodels.api as sm
import statsmodels.formula.api as smf
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import soccerdata as sd
from multimethod import multimethod
from multimethod import overload
from socceraction.data.opta import OptaLoader
import socceraction.spadl as spadl
import socceraction.xthreat as xthreat
from shapely.geometry import Point, Polygon
from scipy.spatial import ConvexHull
from scipy.stats import zscore
from scipy.stats import rankdata
from sklearn.model_selection import train_test_split
import pickle
from tqdm import tqdm
from scipy.stats import poisson

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

###############################################################################
###############################################################################


game_ids = [
    1889883, 1889884, 1889885, 1889886, 1889887, 1889888, 1889889, 1889890,
    1889891, 1889892, 1889893, 1889894, 1889895, 1889896, 1889897, 1889898,
    1889899, 1889900, 1889901, 1889902, 1889903, 1889904, 1889905, 1889906,
    1889907, 1889908, 1889909, 1889910, 1889911, 1889912, 1889913, 1889914,
    1889915, 1889916, 1889917, 1889918, 1889919, 1889920, 1889921, 1889922,
    1889923, 1889924, 1889925, 1889926, 1889927, 1889928, 1889929, 1889930,
    1889931, 1889932, 1889933, 1889934, 1889935, 1889936, 1889937, 1889938,
    1889939, 1889940, 1889941, 1889942, 1889943, 1889944, 1889945, 1889946,
    1889947, 1889948, 1889949, 1889950, 1889951, 1889952, 1889953, 1889954,
    1889955, 1889956, 1889957, 1889958, 1889959, 1889960, 1889961, 1889962,
    1889963, 1889964, 1889965, 1889966, 1889967, 1889968, 1889969, 1889970,
    1889971, 1889972, 1889973, 1889974, 1889975, 1889976, 1889977, 1889978,
    1889979, 1889980, 1889981, 1889982, 1889983, 1889984, 1889985, 1889986,
    1889987, 1889988, 1889989, 1889990, 1889991, 1889992, 1889993, 1889994,
    1889995, 1889996, 1889997, 1889998, 1889999, 1890000, 1890001, 1890002,
    1890003, 1890004, 1890005, 1890006, 1890007, 1890008, 1890009, 1890010,
    1890011, 1890012, 1890013, 1890014, 1890015, 1890016, 1890017, 1890018,
    1890019, 1890020, 1890021, 1890022, 1890023, 1890024, 1890025, 1890026,
    1890027, 1890028, 1890029, 1890030, 1890031, 1890032, 1890033, 1890034,
    1890035, 1890036, 1890037, 1890038, 1890039, 1890040, 1890041, 1890042,
    1890043, 1890044, 1890045, 1890046, 1890047, 1890048, 1890049, 1890050,
    1890051, 1890052, 1890053, 1890054, 1890055, 1890056, 1890057, 1890058,
    1890059, 1890060, 1890061, 1890062, 1890063, 1890064, 1890065, 1890066,
    1890067, 1890068, 1890069, 1890070, 1890071, 1890072, 1890073, 1890074,
    1890075, 1890076, 1890077, 1890078, 1890079, 1890080, 1890081, 1890082,
    1890083, 1890084, 1890085, 1890086, 1890087, 1890088, 1890089, 1890090,
    1890091, 1890092, 1890093, 1890094, 1890095, 1890096, 1890097, 1890098,
    1890099, 1890100, 1890101, 1890102, 1890103, 1890104, 1890105, 1890106,
    1890107, 1890108, 1890109, 1890110, 1890111, 1890112, 1890113, 1890114,
    1890115, 1890116, 1890117, 1890118, 1890119, 1890120, 1890121, 1890122,
    1890123, 1890124, 1890125, 1890126, 1890127, 1890128, 1890129, 1890130,
    1890131, 1890132, 1890133, 1890134, 1890135, 1890136, 1890137, 1890138,
    1890139, 1890140, 1890141, 1890142, 1890143, 1890144, 1890145, 1890146,
    1890147, 1890148, 1890149, 1890150, 1890151, 1890152, 1890153, 1890154,
    1890155, 1890156, 1890157, 1890158, 1890159, 1890160, 1890161, 1890162,
    1890163, 1890164, 1890165, 1890166, 1890167, 1890168, 1890169, 1890170,
    1890171, 1890172, 1890173, 1890174, 1890175, 1890176, 1890177, 1890178,
    1890179, 1890180, 1890181, 1890182, 1890183, 1890184, 1890185, 1890186,
    1890187, 1890188, 1890189, 1890190, 1890191, 1890192, 1890193, 1890194,
    1890195, 1890196, 1890197, 1890198, 1890199, 1890200, 1890201, 1890202,
    1890203, 1890204, 1890205, 1890206, 1890207, 1890208, 1890209, 1890210,
    1890211, 1890212, 1890213, 1890214, 1890215, 1890216, 1890217, 1890218,
    1890219, 1890220, 1890221, 1890222, 1890223, 1890224, 1890225, 1890226,
    1890227, 1890228, 1890229, 1890230, 1890231, 1890232, 1890233, 1890234,
    1890235, 1890236, 1890237, 1890238, 1890239, 1890240, 1890241, 1890242,
    1890243, 1890244, 1890245, 1890246, 1890247, 1890248, 1890249, 1890250,
    1890251, 1890252, 1890253, 1890254, 1890255, 1890256, 1890257, 1890258,
    1890259, 1890260, 1890261, 1890262
]

import subprocess, sys

# Save raw events as parquet for upstream scripts (avoids re-parsing 380 JSON files)
raw_dfs = []
data_dir = os.path.join(
    str(pathlib.Path().resolve()),
    'Brasileirão_2025'
)
for game_id in tqdm(game_ids, desc="Loading JSON files"):
    path = os.path.join(data_dir, f"{game_id}.json")
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    temp_df = pd.json_normalize(data['events'], sep='_')
    temp_df['game_id'] = game_id
    raw_dfs.append(temp_df)
raw_events_df = pd.concat(raw_dfs, ignore_index=True)
raw_events_df.to_parquet("brasileirao_2025_events.parquet", index=False)
print(f"Saved brasileirao_2025_events.parquet ({len(raw_events_df)} events)")

# Run upstream scripts to produce model outputs
upstream_scripts = [
    "possession_chain.py",
    "xG_brasileirao.py",
    "xA_brasileirao.py",
    "xT_brasileirao.py",
]
for script in upstream_scripts:
    print(f"Running {script}...")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True,
        cwd=str(pathlib.Path().resolve()),
    )
    if result.returncode != 0:
        print(f"Error in {script}:\n{result.stderr}")
        raise RuntimeError(f"{script} failed")
    print(f"  {script} completed")

ws = sd.WhoScored(leagues="BRA-Brasileirão", seasons=2025)

# Scrape all games and return a OptaLoader object
loader = ws.read_events(output_fmt='loader')

# Game events
events = ws.read_events()

# Game schedule
df_schedule = ws.read_schedule()

#####################################################################################
#####################################################################################

# Teams
# Collecting all Teams in the league

# Initialize an empty list to store the team dataframes
all_teams = []

# Loop through the game_ids and load teams
for game_id in game_ids:
    df_teams = loader.teams(game_id=game_id)
    df_teams["game_id"] = game_id  # Add the game_id column to each DataFrame
    all_teams.append(df_teams)  # Append the updated DataFrame to the list

# Combine all team dataframes into a single dataframe
all_teams_df = pd.concat(all_teams, ignore_index=True)

# Ensure game_id is the first column
columns_order = ["game_id"] + [col for col in all_teams_df.columns if col != "game_id"]
all_teams_df = all_teams_df[columns_order]

#Rebuild df_teams
df_teams = all_teams_df
###############################################################################
###############################################################################

# Initialize an empty list to store dataframes
event_dataframes = []

# Loop through each game ID and load events
for game_id in game_ids:
    df_events = loader.events(game_id=game_id)  # Load events for each game ID
    event_dataframes.append(df_events)         # Append to the list

# Concatenate all dataframes into one
df = pd.concat(event_dataframes, ignore_index=True)

##########################################################################
##########################################################################

# Create time variable which accumulates time
df["time"] = df["minute"]*60 + df["second"]

# Move 'time' column to the ninth position
columns = df.columns.tolist()  # Get the current column order
columns.remove('time')         # Remove 'time' from its current position
columns.insert(9, 'time')      # Insert 'time' as the ninth column (index 8)

# Reorder the dataframe
df = df[columns]

###############################################################################
###############################################################################

# Bringing teams on
# 1. Merge the team_ column into df_events, matching on game_id
df = df.merge(
    df_teams[['game_id', 'team_id', 'team_name']], 
    on=['game_id', 'team_id'],  
    how='left'
)

# Move 'team_name' column to the fourth position
columns = df.columns.tolist()  # Get the current column order
columns.remove('team_name')
columns.insert(4, 'team_name')

# Reorder the dataframe
df = df[columns]

###############################################################################
###############################################################################
#Load Data

# Create the "fixture" column
df_schedule['fixture'] = (
    df_schedule['home_team'].astype(str) + " " + 
    df_schedule['home_score'].astype(str) + " x " + 
    df_schedule['away_score'].astype(str) + " " + 
    df_schedule['away_team'].astype(str)
)

###############################################################################
###############################################################################

# Bringing fixtures on
# 1. Merge the fixture column into df_events, matching on game_id
df = df.merge(
    df_schedule[['game_id', 'fixture']], 
    on='game_id', 
    how='left'
)

columns = df.columns.tolist()
columns.remove('fixture')
columns.insert(1, 'fixture')

# Reorder the dataframe
df = df[columns]

###############################################################################
###############################################################################

#Dropping player_id from df dataframe
df.drop(columns=["player_id"], inplace=True)

##########################################################################
##########################################################################
###########################################################################################
###########################################################################################

# Adicionar tipos de eventos não cobertos pela Opta
# CARRIES & PROGRESSIVE CARRIES
# Carry: any ball movement by the same team (prev_end != current_start).
# Progressive carry: a carry moving >=5m closer to goal (start outside final 40%,
#   i.e. prev_end_x < 60) or >=2.5m closer (start inside final 40%, prev_end_x >= 60).
# Carry and progressive carry are mutually exclusive: type_id 2000 vs 1000.
# Opta coordinates are 0-100 %; distance-to-goal in meters = (100 - x) * 1.05.

PITCH_LENGTH_M = 105.0

progcarry_df = df.copy()

if 'event_index' not in progcarry_df.columns:
    progcarry_df['event_index'] = np.arange(len(progcarry_df), dtype=float)

# Sort chronologically before any shift work
progcarry_df.sort_values(
    ["game_id", "period_id", "time", "event_id"],
    kind="mergesort",
    inplace=True,
)
progcarry_df.reset_index(drop=True, inplace=True)

# Shifted columns for previous event (within same game & period)
progcarry_df["prev_end_x"]   = progcarry_df.groupby(["game_id", "period_id"])["end_x"].shift(1)
progcarry_df["prev_end_y"]   = progcarry_df.groupby(["game_id", "period_id"])["end_y"].shift(1)
progcarry_df["prev_team_id"] = progcarry_df.groupby(["game_id", "period_id"])["team_id"].shift(1)

# --- Carry detection: same team, ball moved ---
same_team = progcarry_df["team_id"] == progcarry_df["prev_team_id"]
ball_moved = (
    (progcarry_df["start_x"] != progcarry_df["prev_end_x"])
    | (progcarry_df["start_y"] != progcarry_df["prev_end_y"])
)
is_carry = same_team & ball_moved & progcarry_df["prev_end_x"].notna()

# --- Progressive carry: distance-to-goal decreased by threshold ---
dist_to_goal_prev = (100.0 - progcarry_df["prev_end_x"]) * (PITCH_LENGTH_M / 100.0)
dist_to_goal_curr = (100.0 - progcarry_df["start_x"])     * (PITCH_LENGTH_M / 100.0)
gain_m = dist_to_goal_prev - dist_to_goal_curr  # positive = moved closer to goal

outside_final_40 = progcarry_df["prev_end_x"] < 60  # outside final 40% of pitch
is_prog = is_carry & (
    (outside_final_40  & (gain_m >= 5.0))
    | (~outside_final_40 & (gain_m >= 2.5))
)

# --- Mutually exclusive flags ---
progcarry_df["carry"]      = (is_carry & ~is_prog).astype(int)
progcarry_df["prog_carry"] = is_prog.astype(int)

# --- Build synthetic carry rows (vectorized) ---
carry_mask = is_carry  # all carries (both regular and progressive)
carry_src = progcarry_df.loc[carry_mask].copy()

carry_rows = pd.DataFrame({
    "type_name":  np.where(carry_src["prog_carry"] == 1, "progressive carry", "carry"),
    "type_id":    np.where(carry_src["prog_carry"] == 1, 1000, 2000),
    "start_x":    carry_src["prev_end_x"].values,
    "start_y":    carry_src["prev_end_y"].values,
    "end_x":      carry_src["start_x"].values,
    "end_y":      carry_src["start_y"].values,
    "team_id":    carry_src["team_id"].values,
    "team_name":  carry_src["team_name"].values,
    "game_id":    carry_src["game_id"].values,
    "fixture":    carry_src["fixture"].values,
    "period_id":  carry_src["period_id"].values,
    "event_id":   carry_src["event_id"].values,
    "outcome":    carry_src["outcome"].values,
    "touch":      True,
    "goal":       False,
    "shot":       False,
    "timestamp":  carry_src["timestamp"].values,
    "minute":     carry_src["minute"].values,
    "second":     carry_src["second"].values,
    "time":       carry_src["time"].values,
    "event_index": carry_src["event_index"].values - 0.5,
    "carry":      np.where(carry_src["prog_carry"] == 1, 0, np.nan),
    "prog_carry": np.where(carry_src["prog_carry"] == 1, np.nan, 0),
})

# Concatenate and sort
progcarry_df = pd.concat([progcarry_df, carry_rows], ignore_index=True)
progcarry_df.sort_values(
    ["game_id", "period_id", "event_index"],
    kind="mergesort",
    inplace=True,
)
progcarry_df.reset_index(drop=True, inplace=True)

# Drop intermediate columns
progcarry_df.drop(columns=["prev_end_x", "prev_end_y", "prev_team_id"], inplace=True)

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# Possession chains — loaded from pre-built parquet
# Column names are renamed to match the orchestrator convention so all
# downstream variable code works unchanged.

progcarry_chains_df = pd.read_parquet("possesion_chains_brasileirao_2025.parquet")

progcarry_chains_df.rename(columns={
    "teamId":                "team_id",
    "period_value":          "period_id",
    "x":                     "start_x",
    "y":                     "start_y",
    "endX":                  "end_x",
    "endY":                  "end_y",
    "type_value":            "type_id",
    "eventId":               "event_id",
    "possesion_chain":       "possessionId",
    "possesion_chain_team":  "possessionId_team",
    "outcomeType_value":     "outcome",
    "type_displayName":      "type_name",
    "isTouch":               "touch",
    "isGoal":                "goal",
    "isShot":                "shot",
}, inplace=True)


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

# xA — loaded from pre-built parquet (produced by xA_brasileirao.py)
xa_df = pd.read_parquet("xA_brasileirao_2025.parquet")
xa_df.rename(columns={"teamId": "team_id", "id": "event_id"}, inplace=True)

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xG — loaded from pre-built parquet (produced by xG_brasileirao.py)
xg_df = pd.read_parquet("xG_brasileirao_2025.parquet")
xg_df.rename(columns={"teamId": "team_id", "id": "event_id"}, inplace=True)

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###

progcarry_df["game_id"] = pd.to_numeric(progcarry_df["game_id"], errors="coerce").astype("Int64")

# xT — loaded from pre-built parquet (produced by xT_brasileirao.py)
xt_df = pd.read_parquet("xT_brasileirao_2025.parquet")
xt_df.rename(columns={"teamId": "team_id", "id": "event_id", "xT": "xthreat"}, inplace=True)

# Merge continuous xT values into progcarry_df so all downstream variables
# that reference progcarry_df["xthreat"] have the data available.
progcarry_df = progcarry_df.merge(
    xt_df[["game_id", "team_id", "event_id", "xthreat"]],
    on=["game_id", "team_id", "event_id"],
    how="left",
)
progcarry_df["xthreat"] = progcarry_df["xthreat"].fillna(0.0)
if (progcarry_df["xthreat"] != 0).sum() == 0:
    raise RuntimeError("xT merge produced all-zero xthreat column — event_id key space drift between xt_df and progcarry_df")

############################################################################################
############################################################################################


# Passes inside final third (current row's own coordinates — no next-row check needed)
progcarry_df["passes_third"] = (
    (progcarry_df["type_id"] == 1) &
    (progcarry_df["start_x"] >= 66.66) &
    (progcarry_df["end_x"] >= 66.66)
).astype(int)

###############################################################################
###############################################################################

# Passes into final third (start outside, end inside)
progcarry_df["passes_into_third"] = (
    (progcarry_df["type_id"] == 1) &
    (progcarry_df["start_x"] < 66.66) &
    (progcarry_df["end_x"] >= 66.66)
).astype(int)

###############################################################################
###############################################################################

# Helper: check if a qualifier value exists in the list-of-dicts format
# Qualifiers are stored as [{"type": {"displayName": ..., "value": N}, ...}, ...]
def has_qualifier(q, val):
    if isinstance(q, list):
        return any(item.get("type", {}).get("value") == val for item in q)
    if isinstance(q, dict):
        return val in q
    return False

# Crosses (pass with qualifier 2)
progcarry_df["cross"] = (
    (progcarry_df["type_id"] == 1) &
    progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 2))
).astype(int)

###############################################################################
###############################################################################

# Progressive passes — use meter-scaled distance for consistent thresholds
PITCH_LEN = 105.0  # meters (x-axis)
PITCH_WID = 68.0   # meters (y-axis)

progcarry_df["pass_length"] = np.sqrt(
    ((progcarry_df["end_x"] - progcarry_df["start_x"]) * PITCH_LEN / 100)**2 +
    ((progcarry_df["end_y"] - progcarry_df["start_y"]) * PITCH_WID / 100)**2
)

# Remaining distance to goal line in meters; clamp to avoid division by zero
remaining_distance = ((100 - progcarry_df["start_x"]) * PITCH_LEN / 100).clip(lower=0.1)

# Forward progression ratio
progressive_condition = (
    (progcarry_df["end_x"] - progcarry_df["start_x"]) * PITCH_LEN / 100
) / remaining_distance

# Progressive pass: type_id == 1 (pass), >= 10m length, >= 25% of remaining distance covered
progcarry_df["progressive_pass"] = (
    (progcarry_df["type_id"] == 1) &
    (progcarry_df["pass_length"] >= 10) &
    (progressive_condition >= 0.25)
).astype(int)

###############################################################################
###############################################################################

# Ball progression: progressive carry (type_id == 2000), same thresholds
progcarry_df["ball_progression"] = (
    (progcarry_df["type_id"] == 2000) &
    (progcarry_df["pass_length"] >= 10) &
    (progressive_condition >= 0.25)
).astype(int)

###############################################################################
###############################################################################

# Deep runs: event following a through ball (qualifier 4) by the same team
progcarry_df["deep_runs"] = (
    (progcarry_df["period_id"] == progcarry_df["period_id"].shift(1)) &
    (progcarry_df["team_id"] == progcarry_df["team_id"].shift(1)) &
    (progcarry_df["type_id"].shift(1) == 1) &  # Previous event was a pass
    progcarry_df["qualifiers"].shift(1).apply(lambda q: has_qualifier(q, 4))  # Previous pass had through ball qualifier
).astype(int)

############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################

# Building possession dataframe from progcarry_chains_df (parquet)
# Compute possession time per chain, then aggregate home/away per game.

# Time in seconds per event
progcarry_chains_df["time"] = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]

# Possession duration per chain = max(time) - min(time) within each chain
chain_durations = (
    progcarry_chains_df[progcarry_chains_df["possessionId"] != 0]
    .groupby(["game_id", "team_id", "possessionId"])["time"]
    .agg(duration=lambda t: t.max() - t.min())
    .reset_index()
)

# Total possession time per team per game
team_possession = (
    chain_durations.groupby(["game_id", "team_id"])["duration"]
    .sum()
    .reset_index()
    .rename(columns={"duration": "possession_time"})
)

# Build possession dataframe from df_schedule
filtered_games = df_schedule[df_schedule['game_id'].isin(game_ids)]
possession = filtered_games[['game_id', 'home_team_id', 'away_team_id', 'home_team', 'away_team']].copy()

# Merge home team possession
possession = possession.merge(
    team_possession.rename(columns={"team_id": "home_team_id", "possession_time": "home_team_possession"}),
    on=["game_id", "home_team_id"],
    how="left",
)

# Merge away team possession
possession = possession.merge(
    team_possession.rename(columns={"team_id": "away_team_id", "possession_time": "away_team_possession"}),
    on=["game_id", "away_team_id"],
    how="left",
)

possession["home_team_possession"] = possession["home_team_possession"].fillna(0)
possession["away_team_possession"] = possession["away_team_possession"].fillna(0)

total_possession = possession["home_team_possession"] + possession["away_team_possession"]
possession["home_team_possession_per"] = ((possession["home_team_possession"] / total_possession) * 100).round(2)
possession["away_team_possession_per"] = ((possession["away_team_possession"] / total_possession) * 100).round(2)

###############################################################################
###############################################################################
###############################################################################
###############################################################################

# Build variable_df with unique values of "game_id", "date, "team_id", "fixture"
# Ensure "timestamp" is in datetime format and extract only the date
df["date"] = pd.to_datetime(df["timestamp"]).dt.date  

# Select only unique (game_id, team_id) combinations
variable_df = (
    df[["game_id", "date", "fixture", "team_id", "team_name"]]  # Select relevant columns
    .drop_duplicates(subset=["game_id", "team_id"])  # Ensure only one row per game-team
    .sort_values(by=["date", "game_id"])  # Sort by date first, then game_id
    .reset_index(drop=True)  # Reset index for a clean dataframe
)

variable_ps = variable_df.copy()
###############################################################################
###############################################################################
###############################################################################
###############################################################################

# Variáveis
# DEFENCE
# 1
# Defensive line heigth (m)
"""Defensive line height (m) is defined as the average height on the pitch, measured in meters, of a
player's defensive actions. This metric helps in understanding how high up the pitch a player or
team engages in defensive activities."""

# Defensive Line Height (m)
#
# Average physical height on the pitch (in meters) at which a team's
# defensive actions occur. Higher values indicate a higher defensive line.
#
# Opta F24 coordinate note (reference/Opta-f24_appendices.md, Appendix 11
# line 950): start_x is a 0-100 percentage of pitch length, normalized so
# that every team attacks from x=0 toward x=100. The raw mean of start_x is
# therefore a percentage, not meters — it must be scaled by the physical
# pitch length to produce meters.
#
# Defensive action set (per task definition):
#   - type_id 4  (Foul)         outcome == 1  # foul committed by defender
#   - type_id 7  (Tackle)       any outcome
#   - type_id 8  (Interception)
#   - type_id 12 (Clearance)
#   - type_id 49 (Ball recovery)

PITCH_LENGTH_M = 105.0  # UEFA standard pitch length

defensive_mask = (
    ((progcarry_df["type_id"] == 4) & (progcarry_df["outcome"] == 1))
    | progcarry_df["type_id"].isin([7, 8, 12, 49])
)

variable_ps1 = (
    progcarry_df[defensive_mask]
    .groupby(["game_id", "team_id"], as_index=False)["start_x"]
    .mean()
    .rename(columns={"start_x": "defensive_height"})
)

# Convert the 0-100 pitch percentage to meters on a UEFA-standard pitch.
variable_ps1["defensive_height"] = (
    variable_ps1["defensive_height"] * PITCH_LENGTH_M / 100.0
)

variable_ps1.head(100).to_csv("variable_ps4.csv", index=True)

variable_ps = variable_ps.merge(
    variable_ps1[["game_id", "team_id", "defensive_height"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["defensive_height"] = variable_ps["defensive_height"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 2
# High Recoveries %
"""High Recoveries % is the share of a team's ball recoveries that occur in
the attacking third (start_x >= 66.7). A recovery is any event that regains
possession for the team, per the canonical mask shared with variable_df11 in
MatchAnalysis_2025.py:
  type_id 49  Ball recovery          (Opta outcome always 1, ref line 818)
  type_id 8   Interception           (Opta outcome always 1, ref line 772)
  type_id 7   Tackle with outcome 1  (win + retain possession, ref line 771)
  type_id 44  Aerial with outcome 1  (duel won, ref line 815)
  type_id 11  Claim with outcome 1   (goalkeeper secures a cross)
No first_chain / possessionId filter: the canonical mask already answers
"did the team actually regain the ball?", and the prior first_chain==1 gate
silently dropped chains of fewer than 2 events -- exactly the fast
press-recover-press cycles this metric should reward.
"""

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_recoveries = progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "start_x"]].copy()
_recoveries["high"] = (_recoveries["start_x"] >= 66.7).astype(int)

variable_ps2 = (
    _recoveries.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_recoveries=("start_x", "size"),
        high_recoveries=("high", "sum"),
    )
)
variable_ps2["high_recoveries_%"] = np.where(
    variable_ps2["total_recoveries"] > 0,
    (variable_ps2["high_recoveries"] / variable_ps2["total_recoveries"] * 100).round(2),
    0.0,
)

variable_ps2 = variable_ps2[
    ["game_id", "team_id", "total_recoveries", "high_recoveries", "high_recoveries_%"]
]

variable_ps = variable_ps.merge(
    variable_ps2[["game_id", "team_id", "high_recoveries_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["high_recoveries_%"] = variable_ps["high_recoveries_%"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 3
# PPDA
"""PPDA stands for Passes Per Defensive Action. It is a metric used to measure 
the intensity of a team's pressing by calculating the number of passes allowed 
by a team before attempting a defensive action such as a tackle, interception, 
or foul. A lower PPDA value indicates a higher pressing intensity
"""

# PPDA (Passes Per Defensive Action)
#
# PPDA for team A in a given match =
#     (opponent B's passes in B's defensive 60% of the pitch)
#   / (A's tackles + interceptions + fouls in that same physical area)
#
# Opta F24 coordinates are normalized so each team attacks from x=0 (own goal)
# toward x=100 (opponent's goal). The "opponent's defensive 60%" is therefore:
#   - from the passing team's perspective (opponent B):      start_x <= 60
#   - from the pressing team's perspective (team A):         start_x >= 40
# These describe the same physical zone but from each team's own frame.

# Build team <-> opponent mapping per game
games_teams = progcarry_df[["game_id", "team_id"]].drop_duplicates()
game_teams_grouped = games_teams.groupby("game_id")["team_id"].apply(list).reset_index()

def get_opponent(game_id, team_id, game_teams_df):
    teams = game_teams_df.loc[game_teams_df["game_id"] == game_id, "team_id"].iloc[0]
    if len(teams) != 2:
        return None
    return teams[0] if teams[1] == team_id else teams[1]

team_opponent_mapping = []
for _, row in games_teams.iterrows():
    opponent = get_opponent(row["game_id"], row["team_id"], game_teams_grouped)
    if opponent is not None:
        team_opponent_mapping.append({
            "game_id": row["game_id"],
            "team_id": row["team_id"],
            "opponent_team_id": opponent,
        })
team_opponent_df = pd.DataFrame(team_opponent_mapping)

df_with_opponents = progcarry_df.merge(
    team_opponent_df,
    on=["game_id", "team_id"],
    how="left",
)

# Passes leg: opponent's passes in opponent's own defensive 60%.
# The passing team's frame has its own goal at x=0, so its defensive 60% is
# start_x <= 60.
passes = (
    df_with_opponents[
        (df_with_opponents["type_id"] == 1)
        & (df_with_opponents["start_x"] <= 60)
    ]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="passes_in_def_60")
)

# Defensive-actions leg: pressing team's tackles/interceptions/fouls in the
# same physical zone. From the pressing team's frame, that zone is the
# attacking 60% (start_x >= 40).
df_press_zone = df_with_opponents[df_with_opponents["start_x"] >= 40]

tackles = (
    df_press_zone[df_press_zone["type_id"] == 7]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="tackles")
)

interceptions = (
    df_press_zone[df_press_zone["type_id"] == 8]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="interceptions")
)

fouls = (
    df_press_zone[df_press_zone["type_id"] == 4]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="fouls")
)

defensive_actions = (
    tackles
    .merge(interceptions, on=["game_id", "team_id"], how="outer")
    .merge(fouls, on=["game_id", "team_id"], how="outer")
    .fillna(0)
)

defensive_actions["total_def_actions"] = (
    defensive_actions["tackles"]
    + defensive_actions["interceptions"]
    + defensive_actions["fouls"]
)

ppda_base = defensive_actions.merge(
    team_opponent_df,
    on=["game_id", "team_id"],
    how="left",
)

# Attribute opponent passes to the pressing team via the opponent mapping.
ppda_df = ppda_base.merge(
    passes,
    left_on=["game_id", "opponent_team_id"],
    right_on=["game_id", "team_id"],
    how="left",
    suffixes=("", "_opponent"),
)

ppda_df = ppda_df.rename(columns={"passes_in_def_60": "opponent_passes_in_def_60"})

ppda_df["PPDA"] = (
    ppda_df["opponent_passes_in_def_60"] / ppda_df["total_def_actions"]
)
ppda_df["PPDA"] = ppda_df["PPDA"].replace([np.inf, -np.inf], np.nan)

variable_ps3 = ppda_df[[
    "game_id",
    "team_id",
    "tackles",
    "interceptions",
    "fouls",
    "total_def_actions",
    "opponent_passes_in_def_60",
    "PPDA",
]].copy()

variable_ps3.head(100).to_csv("variable_ps3.csv", index=True)

variable_ps = variable_ps.merge(
    variable_ps3[["game_id", "team_id", "PPDA"]],
    on=["game_id", "team_id"],
    how="left",
)

variable_ps["team_id"] = variable_ps["team_id"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 4
# Fouls in attacking half %
"""Fouls in attacking half % is the share of a team's committed fouls that
occur in the opposition half (start_x >= 50), i.e. high-block / pressing
fouls that disrupt opposition build-up in advanced areas.

Opta F24 outcome semantics for type_id 4 (Foul), per Appendix 8:
  outcome 1  -> Player who committed the foul (team_id == fouler)
  outcome 0  -> Player that was fouled        (team_id == victim)
Opta emits both rows. The canonical "team committed a foul" mask is
therefore (type_id == 4) & (outcome == 1), with team_id taken directly
from the row -- matching variable_df4 in MatchAnalysis_2025.py (line 991).

No possession-chain / defensive-transition gate: a foul by definition is
committed on an opponent, so the committing team is not in possession;
the prior "during opponent's possessionId" filter was a workaround for
the outcome misreading, not an independent semantic constraint.
"""

_fouls = progcarry_df.loc[
    (progcarry_df["type_id"] == 4) & (progcarry_df["outcome"] == 1),
    ["game_id", "team_id", "start_x"],
].copy()
_fouls["attacking_half"] = (_fouls["start_x"] >= 50).astype(int)

variable_ps4 = (
    _fouls.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_fouls=("start_x", "size"),
        attacking_half_fouls=("attacking_half", "sum"),
    )
)
variable_ps4["fouls_in_attacking_half_%"] = np.where(
    variable_ps4["total_fouls"] > 0,
    (variable_ps4["attacking_half_fouls"] / variable_ps4["total_fouls"] * 100).round(2),
    0.0,
)

variable_ps4 = variable_ps4[
    ["game_id", "team_id", "total_fouls", "attacking_half_fouls", "fouls_in_attacking_half_%"]
]

variable_ps = variable_ps.merge(
    variable_ps4[["game_id", "team_id", "fouls_in_attacking_half_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["fouls_in_attacking_half_%"] = variable_ps["fouls_in_attacking_half_%"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 5
# Defensive intensity
"""Defensive intensity is defined as the number of defensive duels, loose ball duels, interceptions,
tackles, and fouls when out of possession, adjusted by the opponent's possession. It measures how
actively a player or team engages in defensive actions relative to the amount of time the opponent
has the ball."""

# Per the definition: number of defensive duels, loose ball duels,
# interceptions, tackles, and fouls committed while out of possession.
# The possession adjustment (dividing by opponent possession) is applied
# downstream in the master pipeline, so this module only produces the raw
# counts per (game_id, team_id).
#
# Opta F24 mapping (from reference/Opta-f24_appendices.md):
#   tackles          -> type_id 7   (all outcomes)
#   interceptions    -> type_id 8
#   defensive duels  -> type_id 45  (Challenge: defender fails to win ball)
#   loose ball duels -> type_id 44  (Aerial 50/50)
#   fouls committed  -> type_id 4 AND outcome = 1  (outcome 0 = fouled)

DEFENSIVE_TYPE_IDS = {
    "tackles": 7,
    "interceptions": 8,
    "defensive_duels": 45,
    "loose_ball_duels": 44,
}

def calculate_defensive_intensity(progcarry_df):
    """
    Calculate raw defensive action counts per (game_id, team_id).

    Returns a DataFrame with one row per team per game containing each
    individual action count and their sum as `defensive_intensity`.
    The possession adjustment is applied later in the master pipeline.
    """
    df = progcarry_df[["game_id", "team_id", "type_id", "outcome"]]

    # Count non-foul defensive action types via a single vectorized groupby.
    non_foul_mask = df["type_id"].isin(DEFENSIVE_TYPE_IDS.values())
    counts = (
        df[non_foul_mask]
        .groupby(["game_id", "team_id", "type_id"])
        .size()
        .unstack(fill_value=0)
    )

    # Ensure every expected column is present even if a type never occurred.
    for name, type_id in DEFENSIVE_TYPE_IDS.items():
        if type_id not in counts.columns:
            counts[type_id] = 0
    counts = counts.rename(columns={v: k for k, v in DEFENSIVE_TYPE_IDS.items()})
    counts = counts[list(DEFENSIVE_TYPE_IDS.keys())]

    # Fouls committed: type 4 with outcome == 1 (per F24 appendix 2).
    fouls = (
        df[(df["type_id"] == 4) & (df["outcome"] == 1)]
        .groupby(["game_id", "team_id"])
        .size()
        .rename("fouls_committed")
    )

    defensive_df = counts.join(fouls, how="outer").fillna(0).astype(int).reset_index()

    action_cols = list(DEFENSIVE_TYPE_IDS.keys()) + ["fouls_committed"]
    defensive_df["defensive_intensity"] = defensive_df[action_cols].sum(axis=1)

    return defensive_df[
        ["game_id", "team_id"] + action_cols + ["defensive_intensity"]
    ]


variable_ps5 = calculate_defensive_intensity(progcarry_df)
variable_ps5.head(100).to_csv("variable_ps2.csv", index=True)

# Merge raw defensive_intensity into variable_ps. Possession adjustment is
# handled downstream in the master pipeline.
variable_ps = variable_ps.merge(
    variable_ps5[["game_id", "team_id", "defensive_intensity"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["defensive_intensity"] = variable_ps["defensive_intensity"].fillna(0)

###############################################################################
###############################################################################
###############################################################################
###############################################################################

# Variáveis
# DEFENCE TRANSITION
# 6
# Time to First Defensive Action (s)
"""Time to First Defensive Action (s) is the average number of seconds
between a team losing the ball and that same team making any defensive
action, successful or not. This is a press-intensity / reactivity signal
and is deliberately distinct from "Time to Recovery" (variable_df13 in
MatchAnalysis_2025.py, which uses only successful ball-regaining events).
A team that slide-tackles at t=2s but misses scores low on this metric
even though the ball is not yet regained -- that is the intended meaning.

Loss events (canonical mask, shared with MatchAnalysis variable_df13):
  type_id 1   Pass,      outcome=False  (failed pass)
  type_id 3   Take On,   outcome=False  (failed dribble)
  type_id 50  Dispossessed              (Opta outcome always 1)
  type_id 51  Error                     (Opta outcome always 1)
  type_id 61  Ball touch                (bad touch / ball hit player)

Defensive actions (broader than the canonical recovery mask; includes
unsuccessful tackles/aerials, clearances, fouls, challenges, GK claims):
  type_id 49  Ball recovery       (Opta outcome always 1)
  type_id 8   Interception        (Opta outcome always 1)
  type_id 7   Tackle              any outcome -- attempt counts
  type_id 44  Aerial              any outcome -- contest counts
  type_id 12  Clearance           any outcome -- clearance counts
  type_id 45  Challenge           Opta outcome always 0 -- attempt counts
  type_id 4   Foul, outcome=1     foul committed by this team (Appendix 8)
  type_id 11  Claim, outcome=1    GK cleanly catches a cross

Pairing: pd.merge_asof(direction="forward", by=[game_id, team_id,
period_id], allow_exact_matches=False) -- for each loss, find the NEXT
same-team defensive action in the same period. Forward pairing (rather
than the original "for each action, nearest preceding loss") avoids
silently dropping un-answered losses, which biased the old mean toward
teams that made fewer defensive actions.

NaN: losses with no subsequent defensive action in the same period are
excluded from the per-game mean (merge_asof returns NaN, groupby mean
skips it). Teams with zero usable pairs keep NaN after the left merge --
"no data" stays distinct from "responded instantly".
"""

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_loss_mask = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

_defensive_action_mask = (
    _type_id.isin([49, 8, 7, 44, 12, 45])
    | ((_type_id == 4) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_losses = (
    progcarry_df.loc[_loss_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "loss_time"})
    .sort_values("loss_time", kind="mergesort")
    .reset_index(drop=True)
)

_actions = (
    progcarry_df.loc[_defensive_action_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "action_time"})
    .sort_values("action_time", kind="mergesort")
    .reset_index(drop=True)
)

_paired = pd.merge_asof(
    _losses,
    _actions,
    left_on="loss_time",
    right_on="action_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)

_paired = _paired.loc[_paired["action_time"].notna()].copy()
_paired["time_to_defensive_action"] = _paired["action_time"] - _paired["loss_time"]

variable_ps6 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["time_to_defensive_action"]
    .mean()
    .rename(columns={"time_to_defensive_action": "avg_time_to_defensive_action"})
)

variable_ps = variable_ps.merge(
    variable_ps6[["game_id", "team_id", "avg_time_to_defensive_action"]],
    on=["game_id", "team_id"],
    how="left",
)


###############################################################################
###############################################################################

# Variáveis
# 7
# Counter-Press Success Rate %
"""Counter-Press Success Rate % is the share of a team's ball recoveries
that occur within 5 seconds of losing the ball -- i.e. the success rate
of immediate counter-pressing. Drop-in of MatchAnalysis_2025.py
variable_df11 (Recoveries within 5s %); the two metrics share a single
computation and differ only in output column name.

Loss events (canonical mask, shared with variable_df11 / variable_df13):
  type_id 1   Pass,      outcome=False  (failed pass)
  type_id 3   Take On,   outcome=False  (failed dribble)
  type_id 50  Dispossessed              (Opta outcome always 1)
  type_id 51  Error                     (Opta outcome always 1)
  type_id 61  Ball touch

Recovery events (canonical mask, shared with variable_df11):
  type_id 49  Ball recovery             (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True  (wins possession)
  type_id 8   Interception              (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True  (wins the aerial duel)
  type_id 11  Claim,      outcome=True  (GK cleanly catches cross)

The prior implementation had three independent bugs corrected here:
  1. Recovery mask used {3, 4, 7, 44, 45, 54}, which includes non-
     recoveries (Take On is an attacking action; Foul hands the ball
     to the opponent; Challenge is always outcome=0 by definition) and
     excludes the canonical Opta recoveries (49 Ball recovery and 8
     Interception -- the two events Opta explicitly tags as recoveries).
  2. Cartesian merge without dedup let one recovery pair to multiple
     prior losses, inflating the numerator and allowing rates > 100%.
     merge_asof(direction="backward", allow_exact_matches=False) pairs
     each recovery with at most one preceding loss.
  3. No period_id guard: a loss in H1 could pair to a recovery in H2
     because `time` is per-period seconds. by=[..., period_id] fixes it.

Pairing: for each recovery, find the most recent same-team loss in the
same period; the recovery is "within 5s" if recovery_time - loss_time
<= 5. Denominator = total recoveries (even those with no prior loss
inside the window) -- matches variable_df11 exactly.
"""

WINDOW_SECONDS = 5.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_loss_mask = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_losses = (
    progcarry_df.loc[_loss_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "loss_time"})
    .sort_values("loss_time", kind="mergesort")
    .reset_index(drop=True)
)

_recoveries = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_paired = pd.merge_asof(
    _recoveries,
    _losses,
    left_on="recovery_time",
    right_on="loss_time",
    by=["game_id", "team_id", "period_id"],
    direction="backward",
)

_paired["within_window"] = (
    _paired["loss_time"].notna()
    & ((_paired["recovery_time"] - _paired["loss_time"]) <= WINDOW_SECONDS)
)

variable_ps7 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_recoveries=("recovery_time", "size"),
        recoveries_within_5s=("within_window", "sum"),
    )
)
variable_ps7["counter_press_Success_Rate_%"] = np.where(
    variable_ps7["total_recoveries"] > 0,
    (variable_ps7["recoveries_within_5s"] / variable_ps7["total_recoveries"] * 100).round(2),
    0.0,
)

variable_ps7 = variable_ps7[
    ["game_id", "team_id", "total_recoveries", "recoveries_within_5s", "counter_press_Success_Rate_%"]
]

variable_ps = variable_ps.merge(
    variable_ps7[["game_id", "team_id", "counter_press_Success_Rate_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["counter_press_Success_Rate_%"] = variable_ps["counter_press_Success_Rate_%"].fillna(0)


###############################################################################
###############################################################################

# Variáveis
# 8
# Transition Vulnerability Index
"""Transition Vulnerability Index is the share of the opposition's
completed open-play passes in the 10 seconds after a team loses the
ball that are progressive. A high value means the team's losses are
consistently punished by the opponent advancing the ball into danger --
i.e. the team is vulnerable in defensive transition.

Loss events (canonical mask, shared with variable_df11 / variable_df13):
  type_id 1   Pass,      outcome=False  (failed pass)
  type_id 3   Take On,   outcome=False  (failed dribble)
  type_id 50  Dispossessed              (Opta outcome always 1)
  type_id 51  Error                     (Opta outcome always 1)
  type_id 61  Ball touch

Opposition pass events (transition threat, open play only):
  (type_id == 1) & (outcome == 1)
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
Set-piece restarts are excluded: they are not transitions, they are
resets, and including them inflates the denominator with passes that
don't reflect how well the team defended the loss.

Pairing: pd.merge_asof(direction="backward", allow_exact_matches=False)
  For each completed opposition pass, find the most recent same-game
  loss by the OTHER team in the same period. A pass enters the numerator
  sample if pass_time - loss_time <= 10. Each pass is counted at most
  once -- fixes the old code's double-counting when rapid consecutive
  losses had overlapping 8s windows.

Team-flip: the canonical loss row is keyed by the vulnerable team; the
pass row is keyed by the opposition. merge_asof requires `by` keys to
match, so we add `opp_team_id` to losses (lookup from a precomputed
game->opposite-team map) and join on [game_id, opp_team_id, period_id]
against the pass's team_id. The output is regrouped by the vulnerable
team for the final per-team-per-game metric.

Window: 10 seconds. The old code hard-coded 8s but the docstring said
10s; 10s aligns with the docstring's intent, matches tactical literature
on opposition transition windows, and parallels MatchAnalysis
variable_df14 which uses the same 10s horizon for its counterpart
metric ("opp. final-third entries within 10s after recovery").
"""

WINDOW_SECONDS = 10.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_loss_mask = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

_is_set_piece = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_pass_mask = (_type_id == 1) & _outcome & ~_is_set_piece

# Team pairs per game via self-merge: for any (game_id, team_id), yield
# the set of opposing team_ids in that game. Robust to games with != 2
# unique teams in progcarry_df (abandoned/restarted matches, data
# artifacts) -- the dict-of-dicts version crashed on such edge cases.
_teams_in_game = progcarry_df[["game_id", "team_id"]].drop_duplicates()
_team_pairs = (
    _teams_in_game.merge(
        _teams_in_game.rename(columns={"team_id": "opp_team_id"}),
        on="game_id",
    )
    .query("team_id != opp_team_id")
    [["game_id", "team_id", "opp_team_id"]]
)

_losses = (
    progcarry_df.loc[_loss_mask, ["game_id", "team_id", "period_id", "time"]]
    .merge(_team_pairs, on=["game_id", "team_id"], how="inner")
    [["game_id", "opp_team_id", "period_id", "time"]]
    .rename(columns={"opp_team_id": "pass_team_id", "time": "loss_time"})
    .sort_values("loss_time", kind="mergesort")
    .reset_index(drop=True)
)

_passes = (
    progcarry_df.loc[_pass_mask, ["game_id", "team_id", "period_id", "time", "progressive_pass"]]
    .rename(columns={"team_id": "pass_team_id", "time": "pass_time"})
    .sort_values("pass_time", kind="mergesort")
    .reset_index(drop=True)
)

_paired = pd.merge_asof(
    _passes,
    _losses,
    left_on="pass_time",
    right_on="loss_time",
    by=["game_id", "pass_team_id", "period_id"],
    direction="backward",
    allow_exact_matches=False,
)

_paired["in_window"] = (
    _paired["loss_time"].notna()
    & ((_paired["pass_time"] - _paired["loss_time"]) <= WINDOW_SECONDS)
)
_in_window = _paired.loc[_paired["in_window"]].copy()

# Flip back to the vulnerable team for output attribution.
_in_window = _in_window.merge(
    _team_pairs.rename(columns={"team_id": "pass_team_id", "opp_team_id": "team_id"}),
    on=["game_id", "pass_team_id"],
    how="left",
)

variable_ps8 = (
    _in_window.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_passes_after_loss=("pass_time", "size"),
        progressive_passes_after_loss=("progressive_pass", "sum"),
    )
)
variable_ps8["transition_vulnerability_index"] = np.where(
    variable_ps8["total_passes_after_loss"] > 0,
    (variable_ps8["progressive_passes_after_loss"] / variable_ps8["total_passes_after_loss"]).round(3),
    0.0,
)

variable_ps8 = variable_ps8[
    ["game_id", "team_id", "total_passes_after_loss", "progressive_passes_after_loss", "transition_vulnerability_index"]
]

variable_ps = variable_ps.merge(
    variable_ps8[["game_id", "team_id", "transition_vulnerability_index"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["transition_vulnerability_index"] = variable_ps["transition_vulnerability_index"].fillna(0)


###############################################################################
###############################################################################

# Variáveis
# 9
#Opposition Final third entries within 10s after recovery
"""Opp. Final third entries within 10s after recovery refers to the number of times the opposing team 
successfully enters the final third of the pitch within 10 seconds after recovering possession. This 
metric helps in understanding how quickly and effectively the opposition can transition from defense 
to attack and create potential scoring opportunities."""

# Opp. Final Third Entries Within 10s After Recovery
#
# For each team T, the number of the OPPONENT's recoveries that are
# followed by a final-third event within 10 seconds. Captures how often
# the opposition converts a regained ball into a fast transition.
#
# Recovery events (same set as variable_df11_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
#
# Final-third entry event: any event with end_x >= 200/3 (~66.67). Opta
# F24 Appendix 11 (reference/Opta-f24_appendices.md line 950) normalizes
# every event L->R in the event team's attacking direction, so end_x >=
# 2/3 is always the event team's attacking third. The original code's
# two disjunctions ("crossed into" | "already in") simplify to the single
# `end_x >= 66.67` condition.
#
# Recovery inside the final third: if the recovery event itself ends in
# the final third (a high press won deep), it self-pairs at delta=0 and
# counts as a successful fast transition. merge_asof with direction=
# "forward" and allow_exact_matches=True gives that behavior for free.
#
# Pairing: pd.merge_asof(recoveries, entry_events, direction="forward",
# by=[game_id, team_id, period_id]) finds, for each recovery, the
# earliest same-team event at or after recovery_time whose end_x lands
# in the final third. If the gap is <= 10s the recovery is counted.
# Replaces the original O(recoveries * frame_size) nested iterrows loop
# with an O(n log n) vectorized pairing. Grouping by period_id prevents
# a recovery at the end of H1 from being paired with an event at the
# start of H2 (time is per-period seconds in progcarry_df).
#
# Short-chain bias: the original gated recoveries on `first_chain == 1`,
# which possession_chain_code.py only sets on chains of >= 2 events, so
# single-event possessions were silently dropped. The event-type mask
# alone carries the "team won the ball" semantics and does not need the
# chain guard.
#
# Opposition swap: for team T in game G, variable_df9 carries the
# other team's count in `opposition_final_third_entries_10s`. Same
# self-merge pattern as variable_df6_code.py.
#
# NaN -> 0: this is a count metric (0 successful transitions is a real,
# meaningful value), so the merged column fills NaN with 0 to match the
# original behavior.

FINAL_THIRD = 200.0 / 3.0
WINDOW_SECONDS = 10.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | ((_type_id == 8))
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_recoveries = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_entry_events = (
    progcarry_df.loc[
        progcarry_df["end_x"] >= FINAL_THIRD,
        ["game_id", "team_id", "period_id", "time"],
    ]
    .rename(columns={"time": "entry_time"})
    .sort_values("entry_time", kind="mergesort")
    .reset_index(drop=True)
)

# For each recovery, find the earliest same-team final-third event at or
# after the recovery. allow_exact_matches=True lets a recovery whose own
# event is in the final third self-pair at delta=0.
_paired = pd.merge_asof(
    _recoveries,
    _entry_events,
    left_on="recovery_time",
    right_on="entry_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=True,
)

_paired["within_window"] = (
    _paired["entry_time"].notna()
    & ((_paired["entry_time"] - _paired["recovery_time"]) <= WINDOW_SECONDS)
)

_team_stats = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["within_window"]
    .sum()
    .rename(columns={"within_window": "final_third_entries_10s"})
)
_team_stats["final_third_entries_10s"] = (
    _team_stats["final_third_entries_10s"].astype(int)
)

# Opposition swap: attach each team's count to the OTHER team's row.
_opposition = (
    _team_stats.merge(
        _team_stats.rename(
            columns={
                "team_id": "opponent_team_id",
                "final_third_entries_10s": "opposition_final_third_entries_10s",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opposition_final_third_entries_10s"]]
)

variable_ps9 = _team_stats.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)[
    [
        "game_id",
        "team_id",
        "final_third_entries_10s",
        "opposition_final_third_entries_10s",
    ]
]

variable_ps9.head(100).to_csv("variable_ps9.csv", index=True)

variable_ps = variable_ps.merge(
    variable_ps9[["game_id", "team_id", "opposition_final_third_entries_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["opposition_final_third_entries_10s"] = (
    variable_ps["opposition_final_third_entries_10s"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 10
#Opposition Box entries within 10s after recovery
"""Opp. Box entries within 10s after recovery refers to the number of times the opposing team 
successfully enters the penalty box within 10 seconds after recovering possession. This metric
helps in understanding how quickly and effectively the opposition can transition from defense 
to attack and create potential scoring opportunities in the penalty area."""

# Opp. Box Entries Within 10s After Recovery
#
# For each team T, the number of the OPPONENT's recoveries that are
# followed by a penalty-box entry within 10 seconds. Captures how often
# the opposition converts a regained ball into a fast attack reaching
# the box. Direct analog of variable_df14_code.py with the final-third
# zone replaced by the penalty box.
#
# Recovery events (same set as variable_df11_code.py / variable_df14_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
# Penalty box: Opta F24 Appendix 11 (reference/Opta-f24_appendices.md
# line 957) places the 18-yard box at x >= 83 and 21.1 <= y <= 78.9.
# A box-entry event is any event whose END coordinates land in the box,
# which is exactly the union of "crossed in" and "already in, stayed in"
# (the two disjuncts in the original code).
#
# Recovery inside the box: if the recovery event itself ends in the box
# (a high press won deep), it self-pairs at delta=0 and counts as a
# successful fast box entry. merge_asof with allow_exact_matches=True
# and direction="forward" gives that behavior for free.
#
# Pairing: pd.merge_asof(recoveries, box_entries, direction="forward",
# by=[game_id, team_id, period_id]) finds, for each recovery, the
# earliest same-team event at or after recovery_time whose end
# coordinates land in the box. If the gap is <= 10s the recovery is
# counted. O(n log n) and exact, versus the original nested iterrows
# + per-event apply. Grouping by period_id prevents a recovery at the
# end of H1 from being paired with an event at the start of H2
# (progcarry_df `time` is per-period seconds).
#
# Short-chain bias: the original gated recoveries on `first_chain == 1`,
# which possession_chain_code.py only sets on chains of >= 2 events, so
# single-event possessions were silently dropped. The event-type mask
# alone carries the "team won the ball" semantics.
#
# Semantic fix: the original iterated (game_id, team_id) groups and
# paired THIS team's recoveries with the OPPOSITION's next 10s of
# events, then never applied an opposition swap at the end. That stored
# the wrong value against each team. This rewrite mirrors
# variable_df14_code.py: count fast-transition recoveries per team,
# then swap so team T's row carries the OPPONENT's count.
#
# NaN -> 0: count metric; zero successful fast box entries is a real,
# meaningful value.

BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9
WINDOW_SECONDS = 10.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | ((_type_id == 8))
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_box_entry_mask = (
    (progcarry_df["end_x"] >= BOX_X)
    & (progcarry_df["end_y"] >= BOX_Y_MIN)
    & (progcarry_df["end_y"] <= BOX_Y_MAX)
)

_recoveries = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_box_entries = (
    progcarry_df.loc[_box_entry_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "entry_time"})
    .sort_values("entry_time", kind="mergesort")
    .reset_index(drop=True)
)

# For each recovery, find the earliest same-team box-entry event at or
# after the recovery. allow_exact_matches=True lets a recovery whose own
# event already lands in the box self-pair at delta=0.
_paired = pd.merge_asof(
    _recoveries,
    _box_entries,
    left_on="recovery_time",
    right_on="entry_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=True,
)

_paired["within_window"] = (
    _paired["entry_time"].notna()
    & ((_paired["entry_time"] - _paired["recovery_time"]) <= WINDOW_SECONDS)
)

_team_stats = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["within_window"]
    .sum()
    .rename(columns={"within_window": "box_entries_10s"})
)
_team_stats["box_entries_10s"] = _team_stats["box_entries_10s"].astype(int)

# Opposition swap: attach each team's count to the OTHER team's row.
_opposition = (
    _team_stats.merge(
        _team_stats.rename(
            columns={
                "team_id": "opponent_team_id",
                "box_entries_10s": "opposition_box_entries_10s",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opposition_box_entries_10s"]]
)

variable_ps10 = _team_stats.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)[
    [
        "game_id",
        "team_id",
        "box_entries_10s",
        "opposition_box_entries_10s",
    ]
]

variable_ps10.head(100).to_csv("variable_ps10.csv", index=True)

variable_ps = variable_ps.merge(
    variable_ps10[["game_id", "team_id", "opposition_box_entries_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["opposition_box_entries_10s"] = (
    variable_ps["opposition_box_entries_10s"].fillna(0)
)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
# Variáveis
# ATTACKING TRANSITION
# 11
# Time to progression after own half recovery (s)
"""Time to progression after own-half recovery (s) is the average number
of seconds between regaining possession in the team's own half and the
first subsequent successful event that propels the ball into the
opposition half, within the same continuous possession (i.e. before the
team's next loss).

Own-half recovery events (canonical recovery mask + start_x < 50):
  type_id 49  Ball recovery            (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True (wins possession)
  type_id 8   Interception             (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True (wins the aerial duel)
  type_id 11  Claim,      outcome=True (GK cleanly catches cross)

Progression events (ball-propelling actions landing in the opposition
half): successful passes or ball-progression carries whose end_x >= 50.
  (type_id == 1 OR type_id == 2000) & outcome == 1 & end_x >= 50
Restricted to pass / carry types because these are the mechanisms that
actually propel the ball forward -- tackles, clearances, and aerials
redistribute possession but do not count as "progression". end_x (not
start_x) matches MatchAnalysis convention for territorial-entry metrics
(see variable_df14).

Possession-continuity guard (replaces the old possessionId constraint):
for each own-half recovery, pair with the first subsequent same-team
progression that occurs BEFORE the team's next loss in the same period.
If the team loses the ball before reaching the opp half, that recovery
did not produce a progression and is excluded from the average.

Pairing: two parallel pd.merge_asof calls from each recovery, both with
direction="forward", allow_exact_matches=False, by=[game_id, team_id,
period_id] -- one to the progression events, one to the loss events.
A recovery contributes a numerator sample iff prog_time.notna() AND
(loss_time.isna() OR prog_time < loss_time).

NaN: recoveries with no valid pair are excluded from the per-game mean
(groupby mean skips NaN). Teams with zero valid pairs keep NaN after
the left merge -- "no data" stays distinct from "progressed instantly".
"""

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_loss_mask = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

_progression_mask = (
    _type_id.isin([1, 2000])
    & _outcome
    & (progcarry_df["end_x"] >= 50)
)

_own_half_recoveries = (
    progcarry_df.loc[_recovery_mask & (progcarry_df["start_x"] < 50), ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_progressions = (
    progcarry_df.loc[_progression_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "prog_time"})
    .sort_values("prog_time", kind="mergesort")
    .reset_index(drop=True)
)

_losses_v11 = (
    progcarry_df.loc[_loss_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "loss_time"})
    .sort_values("loss_time", kind="mergesort")
    .reset_index(drop=True)
)

# For each own-half recovery, next same-team progression in the same period.
_rec_prog = pd.merge_asof(
    _own_half_recoveries,
    _progressions,
    left_on="recovery_time",
    right_on="prog_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)

# For each own-half recovery, next same-team loss in the same period.
_rec_loss = pd.merge_asof(
    _own_half_recoveries,
    _losses_v11,
    left_on="recovery_time",
    right_on="loss_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)

_paired = _rec_prog.copy()
_paired["loss_time"] = _rec_loss["loss_time"].to_numpy()
_paired["valid"] = (
    _paired["prog_time"].notna()
    & (_paired["loss_time"].isna() | (_paired["prog_time"] < _paired["loss_time"]))
)
_paired["time_to_progression"] = _paired["prog_time"] - _paired["recovery_time"]

_valid = _paired.loc[_paired["valid"]].copy()

_own_half_counts = (
    _own_half_recoveries.groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "own_half_recoveries"})
)

_progression_stats = (
    _valid.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        successful_progressions=("time_to_progression", "size"),
        time_to_progression_seconds=("time_to_progression", "mean"),
    )
)
_progression_stats["time_to_progression_seconds"] = (
    _progression_stats["time_to_progression_seconds"].round(2)
)

variable_ps11 = _own_half_counts.merge(
    _progression_stats,
    on=["game_id", "team_id"],
    how="left",
)
variable_ps11["successful_progressions"] = (
    variable_ps11["successful_progressions"].fillna(0).astype(int)
)
variable_ps11 = variable_ps11[
    ["game_id", "team_id", "own_half_recoveries", "successful_progressions", "time_to_progression_seconds"]
]

variable_ps = variable_ps.merge(
    variable_ps11[["game_id", "team_id", "time_to_progression_seconds"]],
    on=["game_id", "team_id"],
    how="left",
)


###############################################################################
###############################################################################
# Variáveis
# 12
# First pass forward %
"""First Pass Forward % is the share of a team's recoveries (that were
followed by a pass) where the very first same-team pass after the
recovery was played forward (end_x > start_x). It captures the team's
counter-attacking intent in the immediate moment after winning the ball.

Recovery events (canonical mask, shared with Vars 7/8/11):
  type_id 49  Ball recovery            (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True
  type_id 8   Interception             (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True
  type_id 11  Claim,      outcome=True

Pass events (open-play attempts, any outcome):
  (type_id == 1) AND NOT qualifier 5   (Free kick taken)
                 AND NOT qualifier 6   (Corner taken)
                 AND NOT qualifier 107 (Throw-in)
Outcome is NOT filtered: the metric measures intent, and a failed
forward pass still expresses the decision to go forward. Set-pieces
are excluded because they are pre-planned restart patterns by a
specialist taker -- they do not reflect the reactive tactical choice
made after a fresh recovery.

Possession-continuity guard (replaces the old possessionId constraint):
for each recovery, take the FIRST subsequent same-team pass that occurs
at or before the team's next canonical loss in the same period. The <=
bound (versus strict < used in Var 11) admits the edge case where the
first post-recovery pass IS the failed pass that ends the chain --
that pass still expresses forward/non-forward intent and counts.

Pairing: two parallel pd.merge_asof calls per recovery, both with
direction="forward", allow_exact_matches=False, by=[game_id, team_id,
period_id] -- one to passes, one to losses. A recovery contributes
iff pass_time.notna() AND (loss_time.isna() OR pass_time <= loss_time).
Recoveries whose next event is a loss WITHOUT any pass in between are
excluded from the denominator, matching the old-code behavior of
"only count recoveries that had a pass".

Forward definition: end_x > start_x (strict). Standard football-
analytics definition. end_x == start_x is lateral, not forward.
"""

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_loss_mask = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

_is_set_piece = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_pass_mask_v12 = (_type_id == 1) & ~_is_set_piece

_recoveries_v12 = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_passes_v12 = (
    progcarry_df.loc[_pass_mask_v12, ["game_id", "team_id", "period_id", "time", "start_x", "end_x"]]
    .rename(columns={"time": "pass_time"})
    .sort_values("pass_time", kind="mergesort")
    .reset_index(drop=True)
)
_passes_v12["is_forward"] = (_passes_v12["end_x"] > _passes_v12["start_x"]).astype(int)

_losses_v12 = (
    progcarry_df.loc[_loss_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "loss_time"})
    .sort_values("loss_time", kind="mergesort")
    .reset_index(drop=True)
)

# Next same-team pass after each recovery, same period.
_rec_pass = pd.merge_asof(
    _recoveries_v12,
    _passes_v12,
    left_on="recovery_time",
    right_on="pass_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)

# Next same-team loss after each recovery, same period.
_rec_loss = pd.merge_asof(
    _recoveries_v12,
    _losses_v12,
    left_on="recovery_time",
    right_on="loss_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)

_paired_v12 = _rec_pass.copy()
_paired_v12["loss_time"] = _rec_loss["loss_time"].to_numpy()
_paired_v12["valid"] = (
    _paired_v12["pass_time"].notna()
    & (_paired_v12["loss_time"].isna() | (_paired_v12["pass_time"] <= _paired_v12["loss_time"]))
)

_valid_v12 = _paired_v12.loc[_paired_v12["valid"]].copy()

variable_ps12 = (
    _valid_v12.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        recoveries_with_pass=("pass_time", "size"),
        forward_first_passes=("is_forward", "sum"),
    )
)
variable_ps12["first_pass_forward_pct"] = np.where(
    variable_ps12["recoveries_with_pass"] > 0,
    (variable_ps12["forward_first_passes"] / variable_ps12["recoveries_with_pass"] * 100).round(2),
    0.0,
)

variable_ps12 = variable_ps12[
    ["game_id", "team_id", "recoveries_with_pass", "forward_first_passes", "first_pass_forward_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps12[["game_id", "team_id", "first_pass_forward_pct"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["first_pass_forward_pct"] = variable_ps["first_pass_forward_pct"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 13
# Final third entries within 10s after own half recovery %
"""Final-third entries within 10s after own-half recovery % is the share
of a team's own-half recoveries that lead to a final-third entry within
10 seconds. Companion to MatchAnalysis_2025.py variable_df14 (same
mechanism, but for the OPPOSITION's recoveries anywhere on the pitch);
here the focus is the team itself and the recovery must start in the
team's own half (start_x < 50).

Own-half recovery events (canonical mask + start_x < 50):
  type_id 49  Ball recovery            (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True (wins possession)
  type_id 8   Interception             (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True (wins the aerial duel)
  type_id 11  Claim,      outcome=True (GK cleanly catches cross)

Final-third entry event: any event with end_x >= 200/3 (~66.67). Opta
F24 Appendix 11 normalizes every event left-to-right in the event
team's attacking direction, so end_x >= 2/3 is always the event team's
attacking third. The old code's two disjunctions (crossed-in OR
already-in) simplify algebraically to this single condition. No
outcome filter: the ball entered the final third, which is what the
metric measures -- transition reach, not transition success. Mirrors
MatchAnalysis variable_df14 exactly.

Window: 10 seconds only. No possession-continuity (next-loss) guard --
follows MatchAnalysis variable_df14's convention for "after-recovery
within Ns" rate metrics. The 10s window is tight enough that
lost-and-regained possessions within it are rare; adding a loss
boundary would diverge from the canonical MA pattern without
meaningfully changing the distribution.

Pairing: pd.merge_asof(direction="forward", by=[game_id, team_id,
period_id], allow_exact_matches=True) finds, for each own-half
recovery, the earliest same-team entry event at or after the recovery
time. If the gap is <= 10s the recovery counts in the numerator. The
period_id guard prevents a H1-end recovery from pairing with an
H2-start entry (time is per-period seconds).

Denominator = all own-half recoveries for that team-game. Numerator =
own-half recoveries with a within-10s final-third entry. Ratio * 100.
"""

FINAL_THIRD = 200.0 / 3.0
WINDOW_SECONDS = 10.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_own_half_recoveries_v13 = (
    progcarry_df.loc[_recovery_mask & (progcarry_df["start_x"] < 50), ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_entry_events_v13 = (
    progcarry_df.loc[progcarry_df["end_x"] >= FINAL_THIRD, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "entry_time"})
    .sort_values("entry_time", kind="mergesort")
    .reset_index(drop=True)
)

_paired_v13 = pd.merge_asof(
    _own_half_recoveries_v13,
    _entry_events_v13,
    left_on="recovery_time",
    right_on="entry_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=True,
)

_paired_v13["within_window"] = (
    _paired_v13["entry_time"].notna()
    & ((_paired_v13["entry_time"] - _paired_v13["recovery_time"]) <= WINDOW_SECONDS)
)

variable_ps13 = (
    _paired_v13.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        own_half_recoveries=("recovery_time", "size"),
        final_third_entries=("within_window", "sum"),
    )
)
variable_ps13["final_third_entries"] = variable_ps13["final_third_entries"].astype(int)
variable_ps13["final_third_entries_10s_pct"] = np.where(
    variable_ps13["own_half_recoveries"] > 0,
    (variable_ps13["final_third_entries"] / variable_ps13["own_half_recoveries"] * 100).round(2),
    0.0,
)

variable_ps13 = variable_ps13[
    ["game_id", "team_id", "own_half_recoveries", "final_third_entries", "final_third_entries_10s_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps13[["game_id", "team_id", "final_third_entries_10s_pct"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["final_third_entries_10s_pct"] = variable_ps["final_third_entries_10s_pct"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 14
# Box entries within 10s after attacking half recovery %
"""Box entries within 10s after attacking-half recovery % is the share
of a team's attacking-half recoveries (high-press wins with start_x >=
50) that lead to a penalty-box entry within 10 seconds. Companion to
MatchAnalysis_2025.py variable_df15 (same mechanism, but MA tracks the
OPPOSITION's box entries after their recoveries and outputs a count;
this metric tracks the team's own box entries after its own attacking-
half recoveries and outputs a percentage).

Attacking-half recovery events (canonical mask + start_x >= 50):
  type_id 49  Ball recovery            (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True (wins possession)
  type_id 8   Interception             (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True (wins the aerial duel)
  type_id 11  Claim,      outcome=True (GK cleanly catches cross)

Penalty box (Opta F24 Appendix 11): x >= 83.0 and 21.1 <= y <= 78.9.
A box-entry event is any event whose END coordinates land in the box.
The old code's disjunction "crossed into box OR both ends in box"
simplifies algebraically to this single condition. No outcome filter:
the ball reached the box, which is the territorial signal the metric
measures -- mirrors MA variable_df15.

Self-pairing: allow_exact_matches=True lets a recovery whose own event
already lands in the box (e.g. a tackle won or interception inside the
opp box itself) self-pair at delta=0 and count as a successful fast
box entry. Winning the ball in the box is the ultimate fast transition;
MA Var 15 documents and relies on this behavior.

Window: 10 seconds only. No possession-continuity (next-loss) guard --
follows MA variable_df14/15's canonical pattern for "after-recovery
within Ns" rate metrics (see Var 13 docstring for rationale).

Pairing: pd.merge_asof(direction="forward", by=[game_id, team_id,
period_id], allow_exact_matches=True) finds, for each attacking-half
recovery, the earliest same-team box-entry event at or after the
recovery time. period_id guard prevents H1-end/H2-start cross-pairing.

Denominator = all attacking-half recoveries for that team-game.
Numerator = attacking-half recoveries with a within-10s box entry.
Ratio * 100.
"""

BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9
WINDOW_SECONDS = 10.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_box_entry_mask = (
    (progcarry_df["end_x"] >= BOX_X)
    & (progcarry_df["end_y"] >= BOX_Y_MIN)
    & (progcarry_df["end_y"] <= BOX_Y_MAX)
)

_att_half_recoveries_v14 = (
    progcarry_df.loc[_recovery_mask & (progcarry_df["start_x"] >= 50), ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_box_entries_v14 = (
    progcarry_df.loc[_box_entry_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "entry_time"})
    .sort_values("entry_time", kind="mergesort")
    .reset_index(drop=True)
)

_paired_v14 = pd.merge_asof(
    _att_half_recoveries_v14,
    _box_entries_v14,
    left_on="recovery_time",
    right_on="entry_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=True,
)

_paired_v14["within_window"] = (
    _paired_v14["entry_time"].notna()
    & ((_paired_v14["entry_time"] - _paired_v14["recovery_time"]) <= WINDOW_SECONDS)
)

variable_ps14 = (
    _paired_v14.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        attacking_half_recoveries=("recovery_time", "size"),
        box_entries=("within_window", "sum"),
    )
)
variable_ps14["box_entries"] = variable_ps14["box_entries"].astype(int)
variable_ps14["box_entries_10s_pct"] = np.where(
    variable_ps14["attacking_half_recoveries"] > 0,
    (variable_ps14["box_entries"] / variable_ps14["attacking_half_recoveries"] * 100).round(2),
    0.0,
)

variable_ps14 = variable_ps14[
    ["game_id", "team_id", "attacking_half_recoveries", "box_entries", "box_entries_10s_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps14[["game_id", "team_id", "box_entries_10s_pct"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["box_entries_10s_pct"] = variable_ps["box_entries_10s_pct"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 15
# Possessions retained after 5s %
"""Possessions retained after 5s % is the percentage of a team's valid
possession chains that lasted at least 5 seconds. A rate metric --
indicates the team's ability to hold onto the ball under pressure and
avoid immediate turnovers. The prior implementation computed only the
raw count (retained_possessions_5s) despite the "%" in the metric name;
this adds the denominator (total valid chains) and emits a percentage,
matching the z-score references downstream (retained_possessions_5s_pct_z).

Numerator:   chains with duration >= 5 seconds
Denominator: all valid chains (possessionId != 0) for that team-game

Chain duration is derived from progcarry_chains_df as max(time) -
min(time) per chain, same source and arithmetic as the possession
dataframe earlier in the pipeline.

Short-chain note: possession_chain_code.py sets possessionId = 0 for
chains of < 2 events. Single-event "possessions" are excluded from both
numerator and denominator. A 1-event chain has zero duration so it
could never cross the 5s threshold anyway; excluding it from the
denominator slightly inflates the rate. Accepted -- changing the
min-chain-length upstream affects every chain-based metric.
"""

RETENTION_THRESHOLD_SECONDS = 5.0

_chain_time_v15 = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations_v15 = (
    progcarry_chains_df.assign(_time=_chain_time_v15)
    .loc[progcarry_chains_df["possessionId"] != 0]
    .groupby(["game_id", "team_id", "possessionId"])["_time"]
    .agg(lambda t: t.max() - t.min())
    .reset_index(name="chain_duration")
)
_chain_durations_v15["retained"] = (
    _chain_durations_v15["chain_duration"] >= RETENTION_THRESHOLD_SECONDS
)

variable_ps15 = (
    _chain_durations_v15.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_valid_possessions=("retained", "size"),
        retained_possessions_5s=("retained", "sum"),
    )
)
variable_ps15["retained_possessions_5s"] = variable_ps15["retained_possessions_5s"].astype(int)
variable_ps15["retained_possessions_5s_pct"] = np.where(
    variable_ps15["total_valid_possessions"] > 0,
    (variable_ps15["retained_possessions_5s"] / variable_ps15["total_valid_possessions"] * 100).round(2),
    0.0,
)

variable_ps15 = variable_ps15[
    ["game_id", "team_id", "total_valid_possessions", "retained_possessions_5s", "retained_possessions_5s_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps15[["game_id", "team_id", "retained_possessions_5s_pct"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["retained_possessions_5s_pct"] = variable_ps["retained_possessions_5s_pct"].fillna(0)


###############################################################################
###############################################################################
###############################################################################
###############################################################################
# Variáveis
# ATTACK
# 16
# Long ball (%)
"""Long ball % refers to the percentage of passes that are long balls, which are 
defined as passes that travel a significant distance, typically bypassing the 
midfield to reach attackers quickly. This metric helps in understanding a team's 
playing style, indicating a preference for a more direct approach to advancing 
the ball up the field.
"""

# Per team per game, the share of the team's SUCCESSFUL passes that
# are long balls. Opta F24 Appendix defines a long ball as a pass
# over 35 yards (reference/Opta-f24_appendices.md line 138), flagged
# by qualifier 1 on a type_id == 1 Pass event. "Longball" is a
# presence-only qualifier -- no value attached -- so the predicate is
# "qualifier 1 is present on the pass row", not "qualifier 1 equals
# True".
#
# Successful-only choice: the metric definition is ambiguous between
# "share of all passes" and "share of successful passes". Original
# code used successful-only and downstream consumers expect that, so
# the rewrite keeps it. (For an all-passes variant, drop the outcome
# gate from both numerator and denominator.)
#
# Qualifier detection: uses the has_qualifier helper to check for
# qualifier 1 (long ball) in the qualifiers list-of-dicts format.
#
# Replaces the original `qualifiers.apply(lambda x: 1 in x and x[1] == True)`
# which (a) assumes `qualifiers` is a dict (it's a string in the
# upstream feed) and (b) checks `== True` on a presence-only qualifier
# that has no value. The original code silently returns zero long
# balls for every team.
#
# Input source: uses `progcarry_df` (pipeline convention) rather than
# the original `df` reference -- progcarry_df is the event source of
# truth across all variable_df* metrics in this pipeline and carries
# type 1 Pass events.
#
# NaN -> 0: share metric; a team with zero successful passes is a
# degenerate case and 0 is the historical contract here.

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_pass_mask = (_type_id == 1) & _outcome

_passes = progcarry_df.loc[_pass_mask, ["game_id", "team_id", "qualifiers"]].copy()
_passes["is_long"] = _passes["qualifiers"].apply(lambda q: has_qualifier(q, 1)).astype(int)
_passes = _passes.drop(columns=["qualifiers"])

variable_ps16 = (
    _passes.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_passes=("is_long", "size"),
        long_balls=("is_long", "sum"),
    )
)
variable_ps16["long_ball_%"] = np.where(
    variable_ps16["total_passes"] > 0,
    variable_ps16["long_balls"] / variable_ps16["total_passes"] * 100.0,
    np.nan,
)

variable_ps16 = variable_ps16[["game_id", "team_id", "long_ball_%"]]

variable_ps16.head(100).to_csv("variable_ps16.csv", index=True)

variable_ps = variable_ps.merge(
    variable_ps16[["game_id", "team_id", "long_ball_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["long_ball_%"] = variable_ps["long_ball_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 17
# Buildup from goalkick %
"""Buildup from Goalkick % is the share of a team's goal kicks that lead
to established possession. A goal kick counts as a successful buildup
iff, within the same continuous possession (bounded by the next same-
team loss, the next goal kick, or the period end):
  (a) the team completes at least 4 successful passes (including the
      goal kick itself as pass #1), AND
  (b) the time span from the kick to the fourth-or-later qualifying
      pass is at least 8 seconds.

Goal kick identification: Opta F24 Appendix 2 -- qualifier 124 on a
type_id == 1 (pass) event marks it as a goal kick.

Pass counting: successful same-team passes only (type_id==1 &
outcome==1). A failed pass is itself a canonical possession loss (see
loss mask below) and terminates the sequence, so failed passes never
contribute to the count. Set-pieces during the buildup (free kicks,
corners, throw-ins that are NOT another goal kick) are not excluded --
they're part of the continuous possession.

Possession-continuity bound (loss mask shared with Vars 6/7/8/11/12):
  type_id 1   Pass,     outcome=False  (failed pass)
  type_id 3   Take On,  outcome=False  (failed dribble)
  type_id 50  Dispossessed             (Opta outcome always 1)
  type_id 51  Error                    (Opta outcome always 1)
  type_id 61  Ball touch
The window also closes at the team's NEXT goal kick (treated as the
start of a new buildup sequence), and at the period end via the
period_id guard in merge_asof.

Fix versus the prior implementation:
  (1) The old code ran on progcarry_df2 (passes-only) and therefore
      could not see Dispossessed / Error / Ball touch events -- passes
      by team T after losing and regaining the ball kept accumulating
      toward the 4-pass threshold even though possession had been lost.
      Using the canonical loss mask on progcarry_df closes this hole.
  (2) The old "4 different players" criterion is dropped -- player_id
      is unavailable post-infrastructure-swap (see MatchAnalysis line
      ~243). Four successful passes in <= N seconds without an
      intervening loss is a strong proxy for multi-player involvement.
  (3) Old 60s hard break is replaced by the canonical loss mask -- the
      "60 seconds" limit was arbitrary and masked possession losses
      that occurred before 60s had elapsed.

Implementation: vectorized via merge_asof.
  - _goal_kicks annotated with their termination time (earliest of the
    next same-team loss and the next same-team goal kick in the same
    period, forward asof joins).
  - _successful_passes attributed to their preceding same-team goal
    kick via a backward asof join (allow_exact_matches=True so the kick
    itself is attributed to itself as pass #1).
  - Passes kept only if pass_time <= kick.window_end.
  - Per kick: pass_count and duration -> established flag.
  - Per team-game: (successful_buildups / total_goal_kicks) * 100.
"""

MIN_PASSES_FOR_BUILDUP = 4
MIN_SECONDS_FOR_BUILDUP = 8.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_goal_kick_mask = (_type_id == 1) & progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 124)
)

_loss_mask = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

_pass_mask_v17 = (_type_id == 1) & _outcome

_goal_kicks_v17 = (
    progcarry_df.loc[_goal_kick_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "kick_time"})
    .sort_values("kick_time", kind="mergesort")
    .reset_index(drop=True)
)
_goal_kicks_v17["kick_id"] = _goal_kicks_v17.index

_losses_v17 = (
    progcarry_df.loc[_loss_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "loss_time"})
    .sort_values("loss_time", kind="mergesort")
    .reset_index(drop=True)
)

_passes_v17 = (
    progcarry_df.loc[_pass_mask_v17, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "pass_time"})
    .sort_values("pass_time", kind="mergesort")
    .reset_index(drop=True)
)

# Termination time: next same-team canonical loss in the same period.
_gk_next_loss = pd.merge_asof(
    _goal_kicks_v17,
    _losses_v17,
    left_on="kick_time",
    right_on="loss_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)[["kick_id", "loss_time"]]

# Termination time: next same-team goal kick in the same period.
_gk_next_kick = pd.merge_asof(
    _goal_kicks_v17,
    _goal_kicks_v17[["game_id", "team_id", "period_id", "kick_time"]].rename(
        columns={"kick_time": "next_kick_time"}
    ),
    left_on="kick_time",
    right_on="next_kick_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)[["kick_id", "next_kick_time"]]

_gk_bounded = (
    _goal_kicks_v17.merge(_gk_next_loss, on="kick_id", how="left")
    .merge(_gk_next_kick, on="kick_id", how="left")
)
# Earliest of next_loss / next_kick; NaN if neither (end-of-period case).
_gk_bounded["window_end"] = _gk_bounded[["loss_time", "next_kick_time"]].min(
    axis=1, skipna=True
)

# Attribute each successful pass to its preceding same-team goal kick.
_pass_to_kick = pd.merge_asof(
    _passes_v17,
    _goal_kicks_v17[["game_id", "team_id", "period_id", "kick_time", "kick_id"]],
    left_on="pass_time",
    right_on="kick_time",
    by=["game_id", "team_id", "period_id"],
    direction="backward",
    allow_exact_matches=True,
)
# Drop passes that have no preceding goal kick (no buildup context).
_pass_to_kick = _pass_to_kick.dropna(subset=["kick_id"])
_pass_to_kick["kick_id"] = _pass_to_kick["kick_id"].astype(int)

# Keep passes that fall at or before their kick's window_end
# (NaN window_end means the sequence runs unbounded to period end, so keep).
_pass_to_kick = _pass_to_kick.merge(
    _gk_bounded[["kick_id", "window_end"]], on="kick_id", how="left"
)
_pass_to_kick = _pass_to_kick.loc[
    _pass_to_kick["window_end"].isna()
    | (_pass_to_kick["pass_time"] <= _pass_to_kick["window_end"])
]

# Per goal kick: pass count and span.
_per_kick = (
    _pass_to_kick.groupby("kick_id", as_index=False)
    .agg(
        pass_count=("pass_time", "size"),
        first_pass_time=("pass_time", "min"),
        last_pass_time=("pass_time", "max"),
    )
)
_per_kick = _gk_bounded[["kick_id", "game_id", "team_id", "kick_time"]].merge(
    _per_kick, on="kick_id", how="left"
)
_per_kick["pass_count"] = _per_kick["pass_count"].fillna(0).astype(int)
_per_kick["duration"] = _per_kick["last_pass_time"] - _per_kick["kick_time"]
_per_kick["established"] = (
    (_per_kick["pass_count"] >= MIN_PASSES_FOR_BUILDUP)
    & (_per_kick["duration"] >= MIN_SECONDS_FOR_BUILDUP)
)

variable_ps17 = (
    _per_kick.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_goal_kicks=("kick_id", "size"),
        successful_buildups=("established", "sum"),
    )
)
variable_ps17["successful_buildups"] = variable_ps17["successful_buildups"].astype(int)
variable_ps17["buildup_%"] = np.where(
    variable_ps17["total_goal_kicks"] > 0,
    (variable_ps17["successful_buildups"] / variable_ps17["total_goal_kicks"] * 100).round(2),
    0.0,
)

variable_ps17 = variable_ps17[
    ["game_id", "team_id", "total_goal_kicks", "successful_buildups", "buildup_%"]
]

variable_ps = variable_ps.merge(
    variable_ps17[["game_id", "team_id", "buildup_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["buildup_%"] = variable_ps["buildup_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 18
# Progressive passes from middle third %
"""Progressive Passes From Middle Third % is the share of a team's
open-play pass attempts originating in the middle third of the pitch
that are progressive. It is a measure of forward intent through the
central phase of buildup.

Pass mask (open-play attempts, any outcome):
  type_id == 1
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
Outcome is NOT filtered: `progressive_pass` (built in the MA
infrastructure as type_id==1 & length >= 10m & forward_ratio >= 25%)
is itself outcome-agnostic -- a failed forward long ball still counts
as an attempted progression. The metric measures tactical choice /
forward intent, not completion success.

Middle third: start_x in [100/3, 200/3), i.e. [~33.33, ~66.67).
Opta F24 Appendix 11 normalizes every event left-to-right in the
event team's attacking direction, so the middle third is a literal
constant interval -- NOT a statistic computed from observed pass
coordinates, which was the prior implementation's bug (it rederived
the boundaries from `passes['start_x'].min()/.max()`, which drifted
the third's location based on which zones the team passed from).

Numerator:   middle-third passes flagged as progressive.
Denominator: all middle-third open-play pass attempts.
Ratio * 100.

`progressive_pass` column source: MatchAnalysis_2025.py infrastructure
(line ~490), which defines progressive = (type_id==1) & (pass_length
>= 10m) & (forward_progress_ratio >= 25%).
"""

MIDDLE_THIRD_START = 100.0 / 3.0
MIDDLE_THIRD_END = 200.0 / 3.0

_is_set_piece_v18 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_mid_third_pass_mask = (
    (progcarry_df["type_id"] == 1)
    & (progcarry_df["start_x"] >= MIDDLE_THIRD_START)
    & (progcarry_df["start_x"] < MIDDLE_THIRD_END)
    & ~_is_set_piece_v18
)

_mid_third_passes_v18 = progcarry_df.loc[
    _mid_third_pass_mask, ["game_id", "team_id", "progressive_pass"]
]

variable_ps18 = (
    _mid_third_passes_v18.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_middle_third_passes=("progressive_pass", "size"),
        progressive_middle_third_passes=("progressive_pass", "sum"),
    )
)
variable_ps18["progressive_middle_third_passes"] = (
    variable_ps18["progressive_middle_third_passes"].astype(int)
)
variable_ps18["progressive_passes_%"] = np.where(
    variable_ps18["total_middle_third_passes"] > 0,
    (variable_ps18["progressive_middle_third_passes"] / variable_ps18["total_middle_third_passes"] * 100).round(2),
    0.0,
)

variable_ps18 = variable_ps18[
    ["game_id", "team_id", "total_middle_third_passes", "progressive_middle_third_passes", "progressive_passes_%"]
]

variable_ps = variable_ps.merge(
    variable_ps18[["game_id", "team_id", "progressive_passes_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["progressive_passes_%"] = variable_ps["progressive_passes_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 19
# Crosses per final third entry
"""Crosses per Final Third Entry is a ratio (NOT a percentage):
    total_crosses / total_final_third_entries
It captures a team's crossing tendency once they are in the final
third -- how often do they opt to cross rather than work a different
attacking pattern?

Final-third entry events (successful passes or carries that bring the
ball in):
  (type_id == 1 OR type_id == 2000) & outcome == 1
  & start_x < 200/3 & end_x >= 200/3
Entry = the ball crossed the 200/3 boundary left-to-right on this
event (NOT merely landed in the final third). Passes and ball-
progression carries are the two mechanisms that count -- tackles,
clearances, recoveries etc. are not "team entered the final third
with possession". Outcome=1 requires the entry to actually land with
the team; a failed pass nominally crossing the line did not bring the
ball in. Canonical 200/3 boundary (Opta Appendix 11), NOT the
data-derived boundary used in the prior implementation.

Cross events (open-play crosses originating in the final third):
  (type_id == 1) & qualifier 2 (Cross)
  & start_x >= 200/3
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
Corners are always crosses and always start at x~=100, so including
them would inflate the numerator without a parallel inflation in the
denominator (corners do not satisfy start_x < 200/3). Set-piece
crosses are pre-planned patterns, not decisions responding to an open-
play final-third entry, which is what this metric measures. The
start_x >= 200/3 restriction ties "crosses" to "crosses from the
final third", aligning numerator and denominator spatially. No outcome
filter on crosses -- the metric measures the tactical decision to
cross, same framing used in Vars 12/18.

Fixes versus the prior implementation:
  (1) Final-third boundary computed from data (min_x + 2*pitch_length/3)
      replaced with the canonical Opta constant (200/3).
  (2) Denominator broadened from passes-only (progcarry_df2) to
      passes+carries -- teams with strong ball-carriers were
      systematically underweighted.
  (3) Crosses restricted to open play and to the final third, so the
      numerator and denominator share a coherent spatial scope.
"""

FINAL_THIRD = 200.0 / 3.0

_outcome_v19 = progcarry_df["outcome"].astype(bool)
_is_set_piece_v19 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_is_cross_v19 = progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 2))

_entry_mask_v19 = (
    progcarry_df["type_id"].isin([1, 2000])
    & _outcome_v19
    & (progcarry_df["start_x"] < FINAL_THIRD)
    & (progcarry_df["end_x"] >= FINAL_THIRD)
)

_cross_mask_v19 = (
    (progcarry_df["type_id"] == 1)
    & _is_cross_v19
    & (progcarry_df["start_x"] >= FINAL_THIRD)
    & ~_is_set_piece_v19
)

_entries_v19 = progcarry_df.loc[_entry_mask_v19, ["game_id", "team_id"]]
_crosses_v19 = progcarry_df.loc[_cross_mask_v19, ["game_id", "team_id"]]

_entry_counts_v19 = (
    _entries_v19.groupby(["game_id", "team_id"]).size().rename("total_final_third_entries")
)
_cross_counts_v19 = (
    _crosses_v19.groupby(["game_id", "team_id"]).size().rename("total_crosses")
)

variable_ps19 = (
    pd.concat([_entry_counts_v19, _cross_counts_v19], axis=1)
    .fillna(0)
    .astype(int)
    .reset_index()
)
variable_ps19["crosses_per_final_third_entry"] = np.where(
    variable_ps19["total_final_third_entries"] > 0,
    (variable_ps19["total_crosses"] / variable_ps19["total_final_third_entries"]).round(3),
    0.0,
)

variable_ps19 = variable_ps19[
    ["game_id", "team_id", "total_crosses", "total_final_third_entries", "crosses_per_final_third_entry"]
]

variable_ps = variable_ps.merge(
    variable_ps19[["game_id", "team_id", "crosses_per_final_third_entry"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["crosses_per_final_third_entry"] = variable_ps["crosses_per_final_third_entry"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 20
# Dribbles per final third entry
"""Dribbles per Final Third Entry is a ratio (NOT a percentage):
    total_final_third_dribbles / total_final_third_entries
It captures a team's propensity to attempt take-ons once they are in
the final third -- how often do individual players try to beat
defenders through dribbling?

Final-third entry events (same definition as Var 19 -- passes or
carries that bring the ball in):
  (type_id == 1 OR type_id == 2000) & outcome == 1
  & start_x < 200/3 & end_x >= 200/3

Dribble events (all take-on ATTEMPTS originating in the final third):
  type_id == 3  (Take On, Opta F24 Appendix 1)
  & start_x >= 200/3
No outcome filter: the metric measures tactical decision (did the
player attempt a dribble), not dribble success rate. Same "intent"
framing used in Vars 12/18/19.

Fixes versus the prior implementation:
  (1) CRITICAL: the old code filtered on type_id == 4, which is Foul
      in Opta F24 Appendix 1, NOT a dribble. Take On is type_id == 3.
      The old metric was returning "fouls committed in final third per
      final-third entry", not dribbles.
  (2) The old code also ran on progcarry_df2 (passes-only), which does
      not contain Take On events at all -- even if the type_id had been
      3 instead of 4, the mask would have returned an empty frame.
      Running on progcarry_df exposes Take On rows.
  (3) Data-derived final-third boundary (min_x + 2*pitch_length/3)
      replaced with the canonical Opta constant (200/3).
  (4) Denominator broadened to passes + carries (Var 19 convention).
  (5) Dropped the outcome == 1 gate on dribbles -- see framing note
      above.
"""

FINAL_THIRD = 200.0 / 3.0

_outcome_v20 = progcarry_df["outcome"].astype(bool)

_entry_mask_v20 = (
    progcarry_df["type_id"].isin([1, 2000])
    & _outcome_v20
    & (progcarry_df["start_x"] < FINAL_THIRD)
    & (progcarry_df["end_x"] >= FINAL_THIRD)
)

_dribble_mask_v20 = (
    (progcarry_df["type_id"] == 3)
    & (progcarry_df["start_x"] >= FINAL_THIRD)
)

_entries_v20 = progcarry_df.loc[_entry_mask_v20, ["game_id", "team_id"]]
_dribbles_v20 = progcarry_df.loc[_dribble_mask_v20, ["game_id", "team_id"]]

_entry_counts_v20 = (
    _entries_v20.groupby(["game_id", "team_id"]).size().rename("total_final_third_entries")
)
_dribble_counts_v20 = (
    _dribbles_v20.groupby(["game_id", "team_id"]).size().rename("total_final_third_dribbles")
)

variable_ps20 = (
    pd.concat([_entry_counts_v20, _dribble_counts_v20], axis=1)
    .fillna(0)
    .astype(int)
    .reset_index()
)
variable_ps20["dribbles_per_final_third_entry"] = np.where(
    variable_ps20["total_final_third_entries"] > 0,
    (variable_ps20["total_final_third_dribbles"] / variable_ps20["total_final_third_entries"]).round(3),
    0.0,
)

variable_ps20 = variable_ps20[
    ["game_id", "team_id", "total_final_third_dribbles", "total_final_third_entries", "dribbles_per_final_third_entry"]
]

variable_ps = variable_ps.merge(
    variable_ps20[["game_id", "team_id", "dribbles_per_final_third_entry"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["dribbles_per_final_third_entry"] = variable_ps["dribbles_per_final_third_entry"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 21
# Box entries from crosses %
"""Box entries from crosses % is the share of a team's penalty-box
entries that originate as crosses rather than other attacking methods.
It captures how crossing-reliant the team's box penetration is.

Penalty box (Opta F24 Appendix 11): x >= 83.0 AND 21.1 <= y <= 78.9.
Same box definition used by PlayStyle Var 14 and MatchAnalysis Var 15.

Box-entry events (denominator): successful passes or ball-progression
carries that bring the ball IN from outside the box:
  (type_id == 1 OR type_id == 2000) & outcome == 1
  & (start NOT in box) & (end in box)
The "NOT in box at start" clause restricts to crossing-the-boundary
events, consistent with Var 19's final-third-entry semantics, and
excludes intra-box passes from the denominator (they do not
represent a new entry moment).

Cross-entry events (numerator): successful open-play crosses crossing
the box boundary:
  (type_id == 1) & outcome == 1 & qualifier 2 (Cross)
  & (start NOT in box) & (end in box)
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
Set-piece exclusion parallels Vars 8/12/17/18/19 -- corners and wide
free-kick crosses are pre-planned restart patterns, not responses to
attacking buildup. Corners would also fail the "start not in box"
clause anyway (they originate at x~=100, in box), so excluding them
is mostly redundant but kept explicit for consistency.

Fixes versus the prior implementation:
  (1) Box threshold computed from data (min_x + 0.83*pitch_length)
      replaced with canonical 83.0.
  (2) Missing Y constraint added: the old code's "end_x >= threshold"
      counted corner-flag-area events (x>=83, y near 0 or 100) as box
      entries. The Opta penalty area requires 21.1 <= y <= 78.9.
  (3) Denominator broadened from passes-only (progcarry_df2) to
      passes + carries -- carries into the box were invisible.
  (4) Denominator restricted to entry events (crossing the box
      boundary), not any event landing in the box, so intra-box passes
      stop inflating the denominator.
  (5) The old code renamed the output column from "..._percentage" to
      "box_entries_from_crosses", masking that the value is a
      percentage. Column name kept to preserve the downstream z-score
      reference (box_entries_from_crosses_z); the docstring here makes
      the percentage nature explicit.
"""

BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

_outcome_v21 = progcarry_df["outcome"].astype(bool)
_is_set_piece_v21 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_is_cross_v21 = progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 2))

_start_in_box_v21 = (
    (progcarry_df["start_x"] >= BOX_X)
    & (progcarry_df["start_y"] >= BOX_Y_MIN)
    & (progcarry_df["start_y"] <= BOX_Y_MAX)
)
_end_in_box_v21 = (
    (progcarry_df["end_x"] >= BOX_X)
    & (progcarry_df["end_y"] >= BOX_Y_MIN)
    & (progcarry_df["end_y"] <= BOX_Y_MAX)
)

_box_entry_mask_v21 = (
    progcarry_df["type_id"].isin([1, 2000])
    & _outcome_v21
    & ~_start_in_box_v21
    & _end_in_box_v21
)

_cross_entry_mask_v21 = (
    (progcarry_df["type_id"] == 1)
    & _outcome_v21
    & _is_cross_v21
    & ~_is_set_piece_v21
    & ~_start_in_box_v21
    & _end_in_box_v21
)

_entries_v21 = progcarry_df.loc[_box_entry_mask_v21, ["game_id", "team_id"]]
_cross_entries_v21 = progcarry_df.loc[_cross_entry_mask_v21, ["game_id", "team_id"]]

_entry_counts_v21 = (
    _entries_v21.groupby(["game_id", "team_id"]).size().rename("total_box_entries")
)
_cross_counts_v21 = (
    _cross_entries_v21.groupby(["game_id", "team_id"]).size().rename("box_entries_from_crosses_count")
)

variable_ps21 = (
    pd.concat([_entry_counts_v21, _cross_counts_v21], axis=1)
    .fillna(0)
    .astype(int)
    .reset_index()
)
variable_ps21["box_entries_from_crosses"] = np.where(
    variable_ps21["total_box_entries"] > 0,
    (variable_ps21["box_entries_from_crosses_count"] / variable_ps21["total_box_entries"] * 100).round(2),
    0.0,
)

variable_ps21 = variable_ps21[
    ["game_id", "team_id", "total_box_entries", "box_entries_from_crosses_count", "box_entries_from_crosses"]
]

variable_ps = variable_ps.merge(
    variable_ps21[["game_id", "team_id", "box_entries_from_crosses"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["box_entries_from_crosses"] = variable_ps["box_entries_from_crosses"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 22
# Box entries from carries %
"""Box entries from carries % is the share of a team's penalty-box
entries that occur via a player carrying or dribbling the ball over
the box boundary, rather than passing it in. Companion metric to
Var 21 (box entries from crosses); uses the SAME denominator so the
two metrics are directly comparable and sum to <= 100%, with the
residual being non-cross passes that cross the boundary.

Penalty box (Opta F24 Appendix 11): x >= 83.0 AND 21.1 <= y <= 78.9.

Box-entry events (denominator, same as Var 21): successful passes or
ball-progression carries crossing the box boundary:
  (type_id == 1 OR type_id == 2000) & outcome == 1
  & (start NOT in box) & (end in box)

Carry-entry events (numerator): ball-carrying mechanisms crossing the
box boundary. Two event types qualify:
  - Ball-progression carries: type_id == 2000 & outcome == 1
    (custom events built by possession_chain.py / MA infrastructure)
  - Successful take-ons: type_id == 3 & outcome == 1
    (Opta F24 Appendix 1 -- dribble past an opponent)
  Both require (start NOT in box) & (end in box).

Fixes versus the prior implementation:
  (1) type_id == 4 used for dribbles in the old code -- that is Foul
      in Opta F24 Appendix 1, NOT a dribble. The correct dribble/take-
      on event is type_id == 3. Same bug existed in Var 20.
  (2) type_id == 1000 used for "progressive carries" in the old code
      -- that is not a valid Opta F24 event ID (Opta uses 1-65). The
      MA infrastructure defines ball-progression carries as type_id
      == 2000, which is what the numerator uses here.
  (3) The old code ran on progcarry_df2 (passes-only). Carries
      (type_id == 2000) and take-ons (type_id == 3) are NOT passes
      and therefore absent from progcarry_df2 -- the numerator was
      silently always zero.
  (4) Box threshold computed from data (min_x + 0.83*pitch_length)
      replaced with canonical 83.0.
  (5) Missing Y constraint added: old "end_x >= threshold" counted
      corner-flag-area events as box entries. Opta penalty area
      requires 21.1 <= y <= 78.9.
  (6) Denominator now matches Var 21 exactly (passes + carries
      crossing the boundary) so the two metrics can be summed
      coherently as a shares-of-entries decomposition.
"""

BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

_outcome_v22 = progcarry_df["outcome"].astype(bool)

_start_in_box_v22 = (
    (progcarry_df["start_x"] >= BOX_X)
    & (progcarry_df["start_y"] >= BOX_Y_MIN)
    & (progcarry_df["start_y"] <= BOX_Y_MAX)
)
_end_in_box_v22 = (
    (progcarry_df["end_x"] >= BOX_X)
    & (progcarry_df["end_y"] >= BOX_Y_MIN)
    & (progcarry_df["end_y"] <= BOX_Y_MAX)
)

_box_entry_mask_v22 = (
    progcarry_df["type_id"].isin([1, 2000])
    & _outcome_v22
    & ~_start_in_box_v22
    & _end_in_box_v22
)

_carry_entry_mask_v22 = (
    progcarry_df["type_id"].isin([3, 2000])
    & _outcome_v22
    & ~_start_in_box_v22
    & _end_in_box_v22
)

_entries_v22 = progcarry_df.loc[_box_entry_mask_v22, ["game_id", "team_id"]]
_carry_entries_v22 = progcarry_df.loc[_carry_entry_mask_v22, ["game_id", "team_id"]]

_entry_counts_v22 = (
    _entries_v22.groupby(["game_id", "team_id"]).size().rename("total_box_entries")
)
_carry_counts_v22 = (
    _carry_entries_v22.groupby(["game_id", "team_id"]).size().rename("box_entries_from_carries_count")
)

variable_ps22 = (
    pd.concat([_entry_counts_v22, _carry_counts_v22], axis=1)
    .fillna(0)
    .astype(int)
    .reset_index()
)
variable_ps22["box_entries_from_carries"] = np.where(
    variable_ps22["total_box_entries"] > 0,
    (variable_ps22["box_entries_from_carries_count"] / variable_ps22["total_box_entries"] * 100).round(2),
    0.0,
)

variable_ps22 = variable_ps22[
    ["game_id", "team_id", "total_box_entries", "box_entries_from_carries_count", "box_entries_from_carries"]
]

variable_ps = variable_ps.merge(
    variable_ps22[["game_id", "team_id", "box_entries_from_carries"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["box_entries_from_carries"] = variable_ps["box_entries_from_carries"].fillna(0)



###############################################################################
###############################################################################
###############################################################################
###############################################################################
# Variáveis
# Chance creation
# 23
# Shots from sustained attacks %
"""Shots from Sustained Attacks % is the share of a team's open-play
shots (excluding penalties) that conclude a methodical possession:
    duration >= 9 seconds AND >= 4 successful open-play passes
between the team's most recent recovery (or period start) and the
shot. It isolates shots created through patient build-up from those
created through transitions, direct play, or set-piece chaos.

Shot events (Opta F24 Appendix 1):
  type_id 13  Miss
  type_id 14  Post
  type_id 15  Attempt Saved
  type_id 16  Goal
  Exclude penalties via qualifier 9 (Opta F24 Appendix 2).

Possession start: the shot-taking team's most recent canonical
recovery in the same period (backward asof join on the shared
recovery mask {49, 7&won, 8, 44&won, 11&won}). If no recovery exists
in the period before the shot -- e.g. a shot built directly from the
kickoff -- the possession start is time = 0 in per-period seconds.

Pass counting: successful same-team open-play passes within
[possession_start, shot_time). Set-pieces (qualifiers 5/6/107) are
excluded so a set-piece restart followed by 3 open-play passes and a
shot does NOT qualify as "sustained". No explicit "consecutive"
logic: the possession_start bound guarantees no intervening same-
team loss (if there were one, a later recovery would exist and
merge_asof would pick that later recovery as possession_start).

Fixes versus the prior implementation:
  (1) The old code ran on progcarry_df2 (passes-only). Shot events
      (type_id 13/14/15/16) are NOT passes and therefore absent from
      progcarry_df2 -- the shot list was always empty, and the metric
      always returned 0.
  (2) Docstring said "4 consecutive completed passes" but the code
      checked >= 5. The 4-pass threshold is used here, matching the
      docstring and the Opta / Wyscout convention for build-up /
      sustained-attack definitions.
  (3) possessionId dependency replaced with the canonical recovery
      mask + merge_asof, same machinery used in Vars 6/7/8/11/12/17.
  (4) Penalty-qualifier check rewritten to use has_qualifier (same
      helper used across Vars 8/12/17/19); old code assumed a dict
      shape that may not match the qualifiers-column serialization.

Implementation: vectorized via merge + range-filter.
  - _shots annotated with their possession_start via backward asof
    to canonical recoveries; NaN -> 0 (period-start fallback).
  - Inner-merge passes x shots on (game_id, team_id, period_id),
    then filter to pass_time in [possession_start, shot_time) and
    groupby-shot to count.
  - Per shot: sustained iff pass_count >= 4 AND duration >= 9s.
  - Per team-game: (sustained_shots / total_shots) * 100.
"""

MIN_PASSES_FOR_SUSTAINED = 4
MIN_SECONDS_FOR_SUSTAINED = 9.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_is_set_piece_v23 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_is_penalty_v23 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 9)
)

_shot_mask_v23 = (
    progcarry_df["type_id"].isin([13, 14, 15, 16])
    & ~_is_penalty_v23
)

_pass_mask_v23 = (
    (progcarry_df["type_id"] == 1)
    & _outcome
    & ~_is_set_piece_v23
)

_shots_v23 = (
    progcarry_df.loc[_shot_mask_v23, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "shot_time"})
    .sort_values("shot_time", kind="mergesort")
    .reset_index(drop=True)
)
_shots_v23["shot_id"] = _shots_v23.index

_recoveries_v23 = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_passes_v23 = (
    progcarry_df.loc[_pass_mask_v23, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "pass_time"})
    .sort_values("pass_time", kind="mergesort")
    .reset_index(drop=True)
)

# Possession start per shot: most recent same-team recovery in same period.
# allow_exact_matches=False ensures recovery strictly precedes shot.
_shot_with_rec = pd.merge_asof(
    _shots_v23,
    _recoveries_v23,
    left_on="shot_time",
    right_on="recovery_time",
    by=["game_id", "team_id", "period_id"],
    direction="backward",
    allow_exact_matches=False,
)
# NaN recovery_time -> period start (0 in per-period seconds).
_shot_with_rec["possession_start"] = _shot_with_rec["recovery_time"].fillna(0.0)
_shot_with_rec["duration"] = _shot_with_rec["shot_time"] - _shot_with_rec["possession_start"]

# Count passes per shot: inner-merge passes x shots on (game, team, period),
# then filter passes inside the possession window and groupby shot.
_pass_shot_join = _passes_v23.merge(
    _shot_with_rec[["shot_id", "game_id", "team_id", "period_id", "shot_time", "possession_start"]],
    on=["game_id", "team_id", "period_id"],
    how="inner",
)
_valid_passes = _pass_shot_join[
    (_pass_shot_join["pass_time"] >= _pass_shot_join["possession_start"])
    & (_pass_shot_join["pass_time"] < _pass_shot_join["shot_time"])
]
_pass_counts_v23 = (
    _valid_passes.groupby("shot_id", as_index=False).size().rename(columns={"size": "pass_count"})
)

_shot_with_rec = _shot_with_rec.merge(_pass_counts_v23, on="shot_id", how="left")
_shot_with_rec["pass_count"] = _shot_with_rec["pass_count"].fillna(0).astype(int)
_shot_with_rec["sustained"] = (
    (_shot_with_rec["pass_count"] >= MIN_PASSES_FOR_SUSTAINED)
    & (_shot_with_rec["duration"] >= MIN_SECONDS_FOR_SUSTAINED)
)

variable_ps23 = (
    _shot_with_rec.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_shots=("shot_id", "size"),
        shots_from_sustained_attacks=("sustained", "sum"),
    )
)
variable_ps23["shots_from_sustained_attacks"] = (
    variable_ps23["shots_from_sustained_attacks"].astype(int)
)
variable_ps23["sustained_attacks"] = np.where(
    variable_ps23["total_shots"] > 0,
    (variable_ps23["shots_from_sustained_attacks"] / variable_ps23["total_shots"] * 100).round(2),
    0.0,
)

variable_ps23 = variable_ps23[
    ["game_id", "team_id", "total_shots", "shots_from_sustained_attacks", "sustained_attacks"]
]

variable_ps = variable_ps.merge(
    variable_ps23[["game_id", "team_id", "sustained_attacks"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["sustained_attacks"] = variable_ps["sustained_attacks"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 24
# Shots from direct attacks %
"""Shots from Direct Attacks % is the share of a team's open-play shots
(excluding penalties) that conclude a rapid, minimal-passing attack:
    duration <= 8 seconds AND <= 3 successful open-play passes
between the team's most recent recovery (or period start) and the
shot. The mirror of Var 23 (sustained attacks). Together they form a
mutually exclusive decomposition on both axes (duration and pass
count), so a shot cannot be counted as both sustained and direct.

All building blocks are identical to Var 23 -- see that section's
docstring for full rationale. The only parameter differences are:
  - duration threshold inverted: <= 8s (direct) vs >= 9s (sustained)
  - pass-count threshold inverted: <= 3 (direct) vs >= 4 (sustained)

Fixes versus the prior implementation:
  (1) The old code ran on progcarry_df2 (passes-only). Shot events
      (type_id 13/14/15/16) are NOT passes and were absent, so the
      shot list was always empty and the metric always returned 0.
      Same silent-kill bug as Var 23.
  (2) Docstring said "max 3 passes", code checked <= 4. The 3-pass
      threshold is used here, matching the docstring and making the
      sustained/direct decomposition internally consistent.
  (3) Old code counted ALL events in the possession chain (.size()
      on grouped events) as "passes" -- it was actually counting
      passes + recoveries + fouls + ball touches. Replaced with an
      explicit pass count (successful type_id==1, set-pieces excluded),
      matching Var 23's definition.
  (4) possessionId dependency replaced with canonical recovery-mask
      merge_asof, identical machinery to Vars 7/8/11/12/17/23.
  (5) Penalty-qualifier check uses has_qualifier helper (same as
      Vars 8/12/17/19/23).
"""

MAX_PASSES_FOR_DIRECT = 3
MAX_SECONDS_FOR_DIRECT = 8.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_is_set_piece_v24 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_is_penalty_v24 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 9)
)

_shot_mask_v24 = (
    progcarry_df["type_id"].isin([13, 14, 15, 16])
    & ~_is_penalty_v24
)

_pass_mask_v24 = (
    (progcarry_df["type_id"] == 1)
    & _outcome
    & ~_is_set_piece_v24
)

_shots_v24 = (
    progcarry_df.loc[_shot_mask_v24, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "shot_time"})
    .sort_values("shot_time", kind="mergesort")
    .reset_index(drop=True)
)
_shots_v24["shot_id"] = _shots_v24.index

_recoveries_v24 = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_passes_v24 = (
    progcarry_df.loc[_pass_mask_v24, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "pass_time"})
    .sort_values("pass_time", kind="mergesort")
    .reset_index(drop=True)
)

_shot_with_rec_v24 = pd.merge_asof(
    _shots_v24,
    _recoveries_v24,
    left_on="shot_time",
    right_on="recovery_time",
    by=["game_id", "team_id", "period_id"],
    direction="backward",
    allow_exact_matches=False,
)
_shot_with_rec_v24["possession_start"] = _shot_with_rec_v24["recovery_time"].fillna(0.0)
_shot_with_rec_v24["duration"] = (
    _shot_with_rec_v24["shot_time"] - _shot_with_rec_v24["possession_start"]
)

_pass_shot_join_v24 = _passes_v24.merge(
    _shot_with_rec_v24[["shot_id", "game_id", "team_id", "period_id", "shot_time", "possession_start"]],
    on=["game_id", "team_id", "period_id"],
    how="inner",
)
_valid_passes_v24 = _pass_shot_join_v24[
    (_pass_shot_join_v24["pass_time"] >= _pass_shot_join_v24["possession_start"])
    & (_pass_shot_join_v24["pass_time"] < _pass_shot_join_v24["shot_time"])
]
_pass_counts_v24 = (
    _valid_passes_v24.groupby("shot_id", as_index=False).size().rename(columns={"size": "pass_count"})
)

_shot_with_rec_v24 = _shot_with_rec_v24.merge(_pass_counts_v24, on="shot_id", how="left")
_shot_with_rec_v24["pass_count"] = _shot_with_rec_v24["pass_count"].fillna(0).astype(int)
_shot_with_rec_v24["direct"] = (
    (_shot_with_rec_v24["pass_count"] <= MAX_PASSES_FOR_DIRECT)
    & (_shot_with_rec_v24["duration"] <= MAX_SECONDS_FOR_DIRECT)
)

variable_ps24 = (
    _shot_with_rec_v24.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_shots=("shot_id", "size"),
        shots_from_direct_attacks=("direct", "sum"),
    )
)
variable_ps24["shots_from_direct_attacks"] = (
    variable_ps24["shots_from_direct_attacks"].astype(int)
)
variable_ps24["direct_attack"] = np.where(
    variable_ps24["total_shots"] > 0,
    (variable_ps24["shots_from_direct_attacks"] / variable_ps24["total_shots"] * 100).round(2),
    0.0,
)

variable_ps24 = variable_ps24[
    ["game_id", "team_id", "total_shots", "shots_from_direct_attacks", "direct_attack"]
]

variable_ps = variable_ps.merge(
    variable_ps24[["game_id", "team_id", "direct_attack"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["direct_attack"] = variable_ps["direct_attack"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 25
# Shots per final third pass
"""Shots per Final Third Pass is a ratio (NOT a percentage):
    total_shots / total_final_third_passes
It captures a team's directness / shot-generation rate relative to
their open-play passing volume in advanced areas. A high value means
the team gets to a shot quickly once they have the ball near the
opposition goal; a low value means possession-heavy play with few
shots per pass volume.

Shot events (non-penalty, same mask as Vars 23/24):
  type_id in {13, 14, 15, 16}
  AND NOT qualifier 9 (Penalty)

Final-third pass events (successful open-play passes landing in the
final third):
  type_id == 1 & outcome == 1 & end_x >= 200/3
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
Set-pieces are excluded from the denominator because a corner is a
pre-planned pass landing in the final third -- including it inflates
the denominator without reflecting open-play buildup volume. Canonical
200/3 boundary (Opta Appendix 11), same constant used in Vars 13/18/
19/20/21.

Fixes versus the prior implementation:
  (1) The old code ran on progcarry_df2 (passes-only). Shot events
      are not passes and were absent -- numerator always zero, metric
      always returned 0 / (denom or NaN). Same silent-kill bug as
      Vars 20/22/23/24. Running on progcarry_df exposes shot rows.
  (2) Penalty-qualifier check rewritten to use has_qualifier helper
      for consistency with Vars 8/12/17/19/23/24.
  (3) Final-third boundary documented as 200/3 (matches old 66.7 to
      within rounding, but avoids the subtle 0.003 drift).
  (4) Set-piece exclusion added on the denominator for open-play
      framing consistency with Vars 18/19/21/22/23/24.
"""

FINAL_THIRD = 200.0 / 3.0

_outcome_v25 = progcarry_df["outcome"].astype(bool)
_is_set_piece_v25 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)
_is_penalty_v25 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 9)
)

_shot_mask_v25 = (
    progcarry_df["type_id"].isin([13, 14, 15, 16])
    & ~_is_penalty_v25
)

_final_third_pass_mask_v25 = (
    (progcarry_df["type_id"] == 1)
    & _outcome_v25
    & (progcarry_df["end_x"] >= FINAL_THIRD)
    & ~_is_set_piece_v25
)

_shots_v25 = progcarry_df.loc[_shot_mask_v25, ["game_id", "team_id"]]
_final_third_passes_v25 = progcarry_df.loc[
    _final_third_pass_mask_v25, ["game_id", "team_id"]
]

_shot_counts_v25 = (
    _shots_v25.groupby(["game_id", "team_id"]).size().rename("total_shots")
)
_ftp_counts_v25 = (
    _final_third_passes_v25.groupby(["game_id", "team_id"]).size().rename("final_third_passes")
)

variable_ps25 = (
    pd.concat([_shot_counts_v25, _ftp_counts_v25], axis=1)
    .fillna(0)
    .astype(int)
    .reset_index()
)
variable_ps25["shots_per_final_third_pass"] = np.where(
    variable_ps25["final_third_passes"] > 0,
    (variable_ps25["total_shots"] / variable_ps25["final_third_passes"]).round(4),
    0.0,
)

variable_ps25 = variable_ps25[
    ["game_id", "team_id", "total_shots", "final_third_passes", "shots_per_final_third_pass"]
]

variable_ps = variable_ps.merge(
    variable_ps25[["game_id", "team_id", "shots_per_final_third_pass"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["shots_per_final_third_pass"] = variable_ps["shots_per_final_third_pass"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 26
# Shots from outside the box %
"""Shots from Outside the Box % is the share of a team's open-play
shots (excluding penalties) taken from outside the opposition penalty
area.

Shot events (non-penalty, same mask as Vars 23/24/25):
  type_id in {13, 14, 15, 16}
  AND NOT qualifier 9 (Penalty)

Penalty box (Opta F24 Appendix 11): x >= 83.0 AND 21.1 <= y <= 78.9.
Same canonical coordinates used in Vars 14/21/22 and MA Var 15. A
shot is "outside the box" iff its START coordinates (where the player
shoots from) are NOT inside that rectangle.

Fixes versus the prior implementation:
  (1) The old code ran on progcarry_df2 (passes-only). Shot events
      are not passes and were absent -- denominator and numerator
      were always empty, metric always returned 0. Same silent-kill
      bug as Vars 20/22/23/24/25. Running on progcarry_df exposes
      shot rows.
  (2) Box Y-range corrected from the old (30, 70) to the canonical
      Opta (21.1, 78.9). The old narrower range misclassified shots
      from the SIDES of the penalty area (y in [21.1, 30] or [70,
      78.9]) as "outside the box" when they were actually inside,
      systematically inflating the percentage.
  (3) Penalty-qualifier check rewritten to use has_qualifier helper
      for consistency with Vars 8/12/17/19/23/24/25.
"""

BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

_is_penalty_v26 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 9)
)

_shot_mask_v26 = (
    progcarry_df["type_id"].isin([13, 14, 15, 16])
    & ~_is_penalty_v26
)

_shots_v26 = progcarry_df.loc[_shot_mask_v26, ["game_id", "team_id", "start_x", "start_y"]].copy()
_shots_v26["is_outside_box"] = (
    (_shots_v26["start_x"] < BOX_X)
    | (_shots_v26["start_y"] < BOX_Y_MIN)
    | (_shots_v26["start_y"] > BOX_Y_MAX)
).astype(int)

variable_ps26 = (
    _shots_v26.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_shots=("start_x", "size"),
        outside_box_shots=("is_outside_box", "sum"),
    )
)
variable_ps26["outside_box_shots"] = variable_ps26["outside_box_shots"].astype(int)
variable_ps26["shots_outside_box"] = np.where(
    variable_ps26["total_shots"] > 0,
    (variable_ps26["outside_box_shots"] / variable_ps26["total_shots"] * 100).round(2),
    0.0,
)

variable_ps26 = variable_ps26[
    ["game_id", "team_id", "total_shots", "outside_box_shots", "shots_outside_box"]
]

variable_ps = variable_ps.merge(
    variable_ps26[["game_id", "team_id", "shots_outside_box"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_ps["shots_outside_box"] = variable_ps["shots_outside_box"].fillna(0)


############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################

# Copying 
variable_ps_new = variable_ps.copy()

# Add per-team possession percentages to variable_ps_new.
# `possession` (built at lines ~533-554) is wide: one row per game
# carrying both teams' possession_per. We reshape to long form so each
# (game_id, team_id) has its own percentage plus the opponent's, then
# left-merge onto variable_ps_new. Replaces the prior iterrows/df.at
# per-row loop with a vectorized pandas merge (~100x faster) and
# produces proper float64 columns instead of object-dtype None-filled
# columns.
_home_long = possession[
    ["game_id", "home_team_id", "home_team_possession_per", "away_team_possession_per"]
].rename(
    columns={
        "home_team_id": "team_id",
        "home_team_possession_per": "possession_percentage",
        "away_team_possession_per": "opponent_possession_percentage",
    }
)
_away_long = possession[
    ["game_id", "away_team_id", "away_team_possession_per", "home_team_possession_per"]
].rename(
    columns={
        "away_team_id": "team_id",
        "away_team_possession_per": "possession_percentage",
        "home_team_possession_per": "opponent_possession_percentage",
    }
)
_possession_long = pd.concat([_home_long, _away_long], ignore_index=True)

variable_ps_new = variable_ps_new.merge(
    _possession_long, on=["game_id", "team_id"], how="left"
)

# Reorder "opponent_possession" to be the third column
columns = variable_ps_new.columns.tolist()
columns.remove("opponent_possession_percentage")  # Remove it from the original spot
columns.insert(5, "opponent_possession_percentage")  # Insert it as the third column
variable_ps_new = variable_ps_new[columns]

# Reordering "team_possession", "opponent_possession" 
columns = variable_ps_new.columns.tolist()
columns.remove("possession_percentage")  # Remove it from the original spot
columns.insert(5, "possession_percentage")  # Insert it as the third column
variable_ps_new = variable_ps_new[columns]

#Renaming possession columns
variable_ps_new = variable_ps_new.rename(columns={
    "opponent_possession_percentage": "opponent_possession",
    "possession_percentage": "team_possession"
})


############################################################################################
############################################################################################

# Adding season column

# Add "Temporada" column with the value 2025 as the first column in the dataframe
variable_ps_new.insert(0, "Temporada", 2025)


###########################################################################
###########################################################################

# Building round column
# Numbering rounds
# 1. Load the rounds reference file and keep only the keys we need
rodada_df = pd.read_excel('rodada_2025.xlsx')[['game_id', 'round']]

# 2. Merge the 'round' column into variable_ps_new based on 'game_id'
variable_ps_new = variable_ps_new.merge(rodada_df, on='game_id', how='left')

# 3. Sort the dataframe by date and game_id
variable_ps_new = variable_ps_new.sort_values(['date', 'game_id'], ascending=[True, True]).reset_index(drop=True)

# 4. Relocate the 'round' column to column position 1 (i.e., the second column)
cols = list(variable_ps_new.columns)
cols.remove('round')      # Remove 'round' from its current position
cols.insert(1, 'round')   # Insert 'round' at index 1
variable_ps_new = variable_ps_new[cols]

###########################################################################
###########################################################################


# Add Place column ("Casa"/"Fora") via a vectorized merge against
# df_schedule. Replaces a per-row .apply/df.loc lookup with a long-
# form map of (game_id, team_name) -> place, consistent with the
# add_possession_percentage vectorization earlier.
_home_place = (
    df_schedule[["game_id", "home_team"]]
    .rename(columns={"home_team": "team_name"})
    .assign(place="Casa")
)
_away_place = (
    df_schedule[["game_id", "away_team"]]
    .rename(columns={"away_team": "team_name"})
    .assign(place="Fora")
)
_place_long = pd.concat([_home_place, _away_place], ignore_index=True)

variable_ps_new = variable_ps_new.merge(
    _place_long, on=["game_id", "team_name"], how="left"
)

# Relocate place column to index 9 (same position as the prior code).
all_columns = list(variable_ps_new.columns)
place_column = all_columns.pop(-1)
all_columns.insert(9, place_column)
variable_ps_new = variable_ps_new[all_columns]

# Create .csv file
variable_ps_new.to_csv("play_style_metrics.csv")

###########################################################################
###########################################################################


#Bulding team_id game analysis (same club analysis)

# Per-team z-score transformation. Each team's metrics are z-scored
# against that team's own season-long distribution (not league-wide).
# Column layout: cols [0:10] are identity/context (Temporada, round,
# game_id, date, fixture, team_id, team_name, possession_percentage,
# opponent_possession_percentage, place); cols [10:] are metrics.
#
# nan_policy='omit' skips NaN per-column -- essential because Vars 6
# and 11 deliberately leave NaN for teams with no usable data.
# select_dtypes(np.number) filters any non-numeric columns defensively
# (none expected in the metric range, but guards against downstream
# column-order drift).
#
# Removed the prior try/except: with the NaN policy and dtype filter
# there is no remaining legitimate failure path, and the catch was
# silently dropping entire teams on any exception -- a dangerous
# silent-data-loss mode. Any real failure now surfaces as a normal
# exception at run time.

variable_ps_team_z = pd.DataFrame()

for team_id, group in variable_ps_new.groupby("team_id"):
    base_columns = group.iloc[:, :10].copy()
    numeric_columns = group.iloc[:, 10:].select_dtypes(include=np.number)

    if numeric_columns.empty:
        print(f"No numeric columns found for team_id {team_id}")
        continue

    zscore_columns = numeric_columns.apply(lambda x: zscore(x, nan_policy='omit'))
    zscore_columns.columns = [f"{col}_z" for col in zscore_columns.columns]

    função_z = pd.concat([base_columns, zscore_columns], axis=1)
    variable_ps_team_z = pd.concat([variable_ps_team_z, função_z], axis=0)

variable_ps_team_z.reset_index(drop=True, inplace=True)

###########################################################################
###########################################################################

# Inverting the sign of inverted metrics
# All metrics in variable_ps_team_z follow the "higher = better" convention
# after this block. The seven metrics below are natively "lower = better":
#   - PPDA: lower passes-per-defensive-action = more aggressive press
#   - avg_time_to_defensive_action: faster response = better
#   - transition_vulnerability_index: less vulnerable = better
#   - opposition_final_third_entries_10s: fewer opp transitions = better
#   - opposition_box_entries_10s: fewer opp box threats = better
#   - time_to_progression_seconds: faster own-half-to-opp-half = better
#   - shots_outside_box: lower share of outside-box shots = better shot
#     quality (higher xG per attempt). Added to the inversion so that
#     chance_creation_z rewards teams that take shots closer to goal.
variable_ps_team_z["PPDA_z"] = -1*variable_ps_team_z["PPDA_z"]
variable_ps_team_z["avg_time_to_defensive_action_z"] = -1*variable_ps_team_z["avg_time_to_defensive_action_z"]
variable_ps_team_z["transition_vulnerability_index_z"] = -1*variable_ps_team_z["transition_vulnerability_index_z"]
variable_ps_team_z["opposition_final_third_entries_10s_z"] = -1*variable_ps_team_z["opposition_final_third_entries_10s_z"]
variable_ps_team_z["opposition_box_entries_10s_z"] = -1*variable_ps_team_z["opposition_box_entries_10s_z"]
variable_ps_team_z["time_to_progression_seconds_z"] = -1*variable_ps_team_z["time_to_progression_seconds_z"]
variable_ps_team_z["shots_outside_box_z"] = -1*variable_ps_team_z["shots_outside_box_z"]

###########################################################################
###########################################################################
# Creating qualities columns
# Define the columns to average for each metric
defence_metrics = ["defensive_height_z", "high_recoveries_%_z", "PPDA_z", "fouls_in_attacking_half_%_z",
                   "defensive_intensity_z"]

defensive_transition_metrics = ["avg_time_to_defensive_action_z", "counter_press_Success_Rate_%_z",
                                "transition_vulnerability_index_z", "opposition_final_third_entries_10s_z",
                                "opposition_box_entries_10s_z"]	

attacking_transition_metrics = ["time_to_progression_seconds_z", "first_pass_forward_pct_z",
                                "final_third_entries_10s_pct_z", "box_entries_10s_pct_z",
                                "retained_possessions_5s_pct_z"]	

attacking_metrics = ["long_ball_%_z", "buildup_%_z", "progressive_passes_%_z", 
                     "crosses_per_final_third_entry_z", "dribbles_per_final_third_entry_z", 
                     "box_entries_from_crosses_z", "box_entries_from_carries_z"]

chance_creation_metrics = ["sustained_attacks_z", "direct_attack_z", 
                           "shots_per_final_third_pass_z", "shots_outside_box_z"]
	
# Compute the arithmetic mean for each metric and assign to the respective column
variable_ps_team_z["defence_z"] = variable_ps_team_z[defence_metrics].mean(axis=1)
variable_ps_team_z["defensive_transition_z"] = variable_ps_team_z[defensive_transition_metrics].mean(axis=1)
variable_ps_team_z["attacking_transition_z"] = variable_ps_team_z[attacking_transition_metrics].mean(axis=1)
variable_ps_team_z["attacking_z"] = variable_ps_team_z[attacking_metrics].mean(axis=1)
variable_ps_team_z["chance_creation_z"] = variable_ps_team_z[chance_creation_metrics].mean(axis=1)

# Get a list of the current columns
cols = list(variable_ps_team_z.columns)

# List of columns to be relocated
cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                  "attacking_z", "chance_creation_z"]

# Remove these columns from the list
for col in cols_to_remove:
    cols.remove(col)

# Insert the columns in the desired order at index 9, adjusting the index as we go
for i, col in enumerate(cols_to_remove):
    cols.insert(10 + i, col)

# Reorder the dataframe columns accordingly
variable_ps_team_z = variable_ps_team_z[cols]

# Renaming columns
columns_to_rename = ["round", "date", "fixture", "team_name",
                     "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                     "attacking_transition_z", "attacking_z", "chance_creation_z", "defensive_height_z", 
                     "high_recoveries_%_z", "PPDA_z", "fouls_in_attacking_half_%_z","defensive_intensity_z",	
                     "avg_time_to_defensive_action_z", "counter_press_Success_Rate_%_z",
                     "transition_vulnerability_index_z", "opposition_final_third_entries_10s_z", 
                     "opposition_box_entries_10s_z", "time_to_progression_seconds_z", "first_pass_forward_pct_z", 
                     "final_third_entries_10s_pct_z", "box_entries_10s_pct_z", "retained_possessions_5s_pct_z", 
                     "long_ball_%_z", "buildup_%_z", "progressive_passes_%_z", "crosses_per_final_third_entry_z", 
                     "dribbles_per_final_third_entry_z", "box_entries_from_crosses_z", "box_entries_from_carries_z", 
                     "sustained_attacks_z", "direct_attack_z", "shots_per_final_third_pass_z", "shots_outside_box_z"
                     ]

columns_renamed = ["rodada", "data", "partida", "clube", "Posse (%)",
                   "Posse adversário (%)", "Defesa", "Transição defensiva",
                   "Transição ofensiva", "Ataque", "Criação de chances", 
                   "Altura defensiva (m)", "Recuperações de posse no último terço (%)", "PPDA", "Faltas no campo de ataque (%)",
                   "Intensidade defensiva", "Tempo médio ação defensiva (s)", "Sucesso da pressão pós perda (5s) (%)",
                   "Índice de Vulnerabilidade na Transição", "Entradas do adversário no último terço em 10s",
                   "Entradas do adversário na área em 10s", "Tempo para progressão (s)", "Primeiro passe à frente (%)",
                   "Entradas no último terço em 10s", "Entradas na área em 10s", "Posse mantida em 5s (%)",
                   "Bola longa (%)", "Buildup do goleiro (%)", "Passes progressivos do terço médio (%)", "Entradas no último terço por Cruzamentos (%)",
                   "Entradas no último terço por Dribles (%)", "Entradas na área por Cruzamentos (%)", "Entradas na área por Conduções (%)",
                   "Finalizações em ataque sustentado (%)", "Finalizações em ataque direto (%)", "Finalizações por passe no último terço (%)", "Finalizações de fora da área (%)"
                    ]

# Create a dictionary mapping old names to new names
rename_dict = dict(zip(columns_to_rename, columns_renamed))

# Rename columns in variable_ps_team_z
variable_ps_team_z = variable_ps_team_z.rename(columns=rename_dict)

# Sort the dataframe by 'game_id' and reset the index
variable_ps_team_z = variable_ps_team_z.sort_values(['rodada', 'data'], ascending=[False, False]).reset_index(drop=True)

#Making a csv file
variable_ps_team_z.to_csv("play_style_team.csv")
###########################################################################
###########################################################################

# Rerunning columns from Master Code
# Calculating z-scores per round
# Create a new dataframe for z-scores
variable_ps_round_z = pd.DataFrame()

###########################################################################
###########################################################################

# Per-round z-score transformation. Each round's metrics are z-scored
# across the 20 team-rows playing that round (league-wide comparison
# within a matchday). Fixes the prior bug where groupby("team_id") made
# this block an exact duplicate of the team-level z-score.
#
# select_dtypes + nan_policy='omit' + empty guard mirror the team-level
# block's robustness. With only 20 samples per round, zero-variance or
# all-NaN columns are more likely than at team-level, so the hardening
# matters more here.
#
# Iteration variable is round_id (not `round`) to avoid shadowing the
# Python builtin.
for round_id, group in variable_ps_new.groupby("round"):
    base_columns = group.iloc[:, :10].copy()
    numeric_columns = group.iloc[:, 10:].select_dtypes(include=np.number)

    if numeric_columns.empty:
        print(f"No numeric columns found for round {round_id}")
        continue

    zscore_columns = numeric_columns.apply(lambda x: zscore(x, nan_policy='omit'))
    zscore_columns.columns = [f"{col}_z" for col in zscore_columns.columns]

    função_z = pd.concat([base_columns, zscore_columns], axis=1)
    variable_ps_round_z = pd.concat([variable_ps_round_z, função_z], axis=0)

variable_ps_round_z.reset_index(drop=True, inplace=True)

###########################################################################
###########################################################################

# Inverting the sign of inverted metrics
variable_ps_round_z["PPDA_z"] = -1*variable_ps_round_z["PPDA_z"]
variable_ps_round_z["avg_time_to_defensive_action_z"] = -1*variable_ps_round_z["avg_time_to_defensive_action_z"]
variable_ps_round_z["transition_vulnerability_index_z"] = -1*variable_ps_round_z["transition_vulnerability_index_z"]
variable_ps_round_z["opposition_final_third_entries_10s_z"] = -1*variable_ps_round_z["opposition_final_third_entries_10s_z"]
variable_ps_round_z["opposition_box_entries_10s_z"] = -1*variable_ps_round_z["opposition_box_entries_10s_z"]
variable_ps_round_z["time_to_progression_seconds_z"] = -1*variable_ps_round_z["time_to_progression_seconds_z"]
variable_ps_round_z["shots_outside_box_z"] = -1*variable_ps_round_z["shots_outside_box_z"]

###########################################################################
###########################################################################

# Creating qualities columns
# Define the columns to average for each metric
defence_metrics = ["defensive_height_z", "high_recoveries_%_z", "PPDA_z", "fouls_in_attacking_half_%_z",
                   "defensive_intensity_z"]

defensive_transition_metrics = ["avg_time_to_defensive_action_z", "counter_press_Success_Rate_%_z",
                                "transition_vulnerability_index_z", "opposition_final_third_entries_10s_z",
                                "opposition_box_entries_10s_z"]	

attacking_transition_metrics = ["time_to_progression_seconds_z", "first_pass_forward_pct_z",
                                "final_third_entries_10s_pct_z", "box_entries_10s_pct_z",
                                "retained_possessions_5s_pct_z"]	

attacking_metrics = ["long_ball_%_z", "buildup_%_z", "progressive_passes_%_z", 
                     "crosses_per_final_third_entry_z", "dribbles_per_final_third_entry_z", 
                     "box_entries_from_crosses_z", "box_entries_from_carries_z"]

chance_creation_metrics = ["sustained_attacks_z", "direct_attack_z", 
                           "shots_per_final_third_pass_z", "shots_outside_box_z"]

    
# Compute the arithmetic mean for each metric and assign to the respective column
variable_ps_round_z["defence_z"] = variable_ps_round_z[defence_metrics].mean(axis=1)
variable_ps_round_z["defensive_transition_z"] = variable_ps_round_z[defensive_transition_metrics].mean(axis=1)
variable_ps_round_z["attacking_transition_z"] = variable_ps_round_z[attacking_transition_metrics].mean(axis=1)
variable_ps_round_z["attacking_z"] = variable_ps_round_z[attacking_metrics].mean(axis=1)
variable_ps_round_z["chance_creation_z"] = variable_ps_round_z[chance_creation_metrics].mean(axis=1)

# Get a list of the current columns
cols = list(variable_ps_round_z.columns)

# List of columns to be relocated
cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                  "attacking_z", "chance_creation_z"]

# Remove these columns from the list
for col in cols_to_remove:
    cols.remove(col)

# Insert the columns in the desired order at index 9, adjusting the index as we go
for i, col in enumerate(cols_to_remove):
    cols.insert(10 + i, col)

# Reorder the dataframe columns accordingly
variable_ps_round_z = variable_ps_round_z[cols]

# Renaming columns
# Renaming columns
# Renaming columns
columns_to_rename = ["round", "date", "fixture", "team_name",
                     "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                     "attacking_transition_z", "attacking_z", "chance_creation_z", "defensive_height_z", 
                     "high_recoveries_%_z", "PPDA_z", "fouls_in_attacking_half_%_z","defensive_intensity_z",	
                     "avg_time_to_defensive_action_z", "counter_press_Success_Rate_%_z",
                     "transition_vulnerability_index_z", "opposition_final_third_entries_10s_z", 
                     "opposition_box_entries_10s_z", "time_to_progression_seconds_z", "first_pass_forward_pct_z", 
                     "final_third_entries_10s_pct_z", "box_entries_10s_pct_z", "retained_possessions_5s_pct_z", 
                     "long_ball_%_z", "buildup_%_z", "progressive_passes_%_z", "crosses_per_final_third_entry_z", 
                     "dribbles_per_final_third_entry_z", "box_entries_from_crosses_z", "box_entries_from_carries_z", 
                     "sustained_attacks_z", "direct_attack_z", "shots_per_final_third_pass_z", "shots_outside_box_z"
                     ]

columns_renamed = ["rodada", "data", "partida", "clube", "Posse (%)",
                   "Posse adversário (%)", "Defesa", "Transição defensiva",
                   "Transição ofensiva", "Ataque", "Criação de chances", 
                   "Altura defensiva (m)", "Recuperações de posse no último terço (%)", "PPDA", "Faltas no campo de ataque (%)",
                   "Intensidade defensiva", "Tempo médio ação defensiva (s)", "Sucesso da pressão pós perda (5s) (%)",
                   "Índice de Vulnerabilidade na Transição", "Entradas do adversário no último terço em 10s",
                   "Entradas do adversário na área em 10s", "Tempo para progressão (s)", "Primeiro passe à frente (%)",
                   "Entradas no último terço em 10s", "Entradas na área em 10s", "Posse mantida em 5s (%)",
                   "Bola longa (%)", "Buildup do goleiro (%)", "Passes progressivos do terço médio (%)", "Entradas no último terço por Cruzamentos (%)",
                   "Entradas no último terço por Dribles (%)", "Entradas na área por Cruzamentos (%)", "Entradas na área por Conduções (%)",
                   "Finalizações em ataque sustentado (%)", "Finalizações em ataque direto (%)", "Finalizações por passe no último terço (%)", "Finalizações de fora da área (%)"
                    ]

# Create a dictionary mapping old names to new names
rename_dict = dict(zip(columns_to_rename, columns_renamed))

# Rename columns in variable_ps_round_z
variable_ps_round_z = variable_ps_round_z.rename(columns=rename_dict)

# Sort by round (descending) then date (descending) and reset the index
variable_ps_round_z = variable_ps_round_z.sort_values(['rodada', 'data'], ascending=[False, False]).reset_index(drop=True)

#Making a csv file
variable_ps_round_z.to_csv("play_style_round.csv")

###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################

