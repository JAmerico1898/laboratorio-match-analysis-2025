#%%
# MatchAnalysis 2025 — Orchestrator
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


###############################################################################
###############################################################################
# Variáveis
# 1
# PPDA
"""PPDA stands for Passes Per Defensive Action. It is a metric used to measure the intensity of a
team's pressing by calculating the number of passes allowed by a team IN THE OPPONNET'S 60% OF THE FIELD before attempting a
defensive action such as a tackle, interception, or foul. A lower PPDA value indicates a higher
pressing intensity"""

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

variable_df1 = ppda_df[[
    "game_id",
    "team_id",
    "tackles",
    "interceptions",
    "fouls",
    "total_def_actions",
    "opponent_passes_in_def_60",
    "PPDA",
]].copy()

variable_df1.head(100).to_csv("variable_df1.csv", index=True)

variable_df = variable_df.merge(
    variable_df1[["game_id", "team_id", "PPDA"]],
    on=["game_id", "team_id"],
    how="left",
)

variable_df["team_id"] = variable_df["team_id"].fillna(0)


# Variáveis
# 2
# Defensive intensity
"""Defensive intensity is defined as the number of defensive duels, loose ball duels, interceptions,
tackles, and fouls when out of possession, adjusted by the opponent's possession. It measures how
actively a player or team engages in defensive actions relative to the amount of time the opponent
has the ball."""

# Defensive Intensity (unadjusted)
#
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


variable_df2 = calculate_defensive_intensity(progcarry_df)
variable_df2.head(100).to_csv("variable_df2.csv", index=True)

# Merge raw defensive_intensity into variable_df. Possession adjustment is
# handled downstream in the master pipeline.
variable_df = variable_df.merge(
    variable_df2[["game_id", "team_id", "defensive_intensity"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["defensive_intensity"] = variable_df["defensive_intensity"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 3
# Defensive duels won %
"""Defensive duels won % is defined as the percentage of defensive ground duels that successfully
stop the progression of an opponent or recover possession. It measures a player's effectiveness in
one-on-one defensive challenges on the ground."""

# Defensive Duels Won %
#
# Share of defensive ground duels won by a team — the defender either
# stops progression or recovers possession — out of all defensive ground
# duels contested.
#
# Opta F24 mapping (reference/Opta-f24_appendices.md, Appendix 5 lines
# 503-505 and Appendix 2 outcome tables):
#
#   WON buckets
#     - type_id 7  (Tackle)   outcome == 1   # defender dispossesses attacker
#     - type_id 4  (Foul)     outcome == 1   # defender commits foul to stop
#     - type_id 54 (Smother)  outcome == 1   # GK wins the ball on the ground
#     - type_id 3  (Take On)  outcome == 0   # attacker's failed dribble
#                                            # -> credit the OPPONENT (defender)
#
#   LOST buckets
#     - type_id 7  (Tackle)    outcome == 0  # defender fails to dispossess
#     - type_id 45 (Challenge) any outcome   # defender fails (always lost)
#     - type_id 3  (Take On)   outcome == 1  # attacker beats defender
#                                            # -> credit the OPPONENT (defender)
#
# Exclusions and their reasons:
#   - type_id 8  (Interception) — reading a pass into space, not a 1v1 duel.
#   - type_id 12 (Clearance)    — not a contest, just a release under pressure.
#   - type_id 49 (Ball recovery)— a possession-change marker, not a duel.
#   - type_id 50 (Dispossessed) — attacker-side counterpart of a successful
#                                 tackle; already counted via type 7 and would
#                                 double-book the loss to the wrong team.
#
# Fouls suffered (type 4, outcome == 0) are not a defender's lost duel — they
# describe the attacker being fouled, so they are not counted here.

# Build team <-> opponent mapping per game so take-on events, which store
# team_id as the attacker, can be reattributed to the defending team.
_games_teams = progcarry_df[["game_id", "team_id"]].drop_duplicates()
_game_teams_grouped = (
    _games_teams.groupby("game_id")["team_id"].apply(list).reset_index()
)

def _get_opponent(game_id, team_id, game_teams_df):
    teams = game_teams_df.loc[game_teams_df["game_id"] == game_id, "team_id"].iloc[0]
    if len(teams) != 2:
        return None
    return teams[0] if teams[1] == team_id else teams[1]

_mapping = []
for _, row in _games_teams.iterrows():
    opp = _get_opponent(row["game_id"], row["team_id"], _game_teams_grouped)
    if opp is not None:
        _mapping.append({
            "game_id": row["game_id"],
            "team_id": row["team_id"],
            "opponent_team_id": opp,
        })
team_opponent_df = pd.DataFrame(_mapping)

df = progcarry_df[["game_id", "team_id", "type_id", "outcome"]].merge(
    team_opponent_df,
    on=["game_id", "team_id"],
    how="left",
)

# --- Own-perspective events (team_id already = defender) ---
own_won_mask = (
    ((df["type_id"] == 7)  & (df["outcome"] == 1))
    | ((df["type_id"] == 4)  & (df["outcome"] == 1))
    | ((df["type_id"] == 54) & (df["outcome"] == 1))
)
own_lost_mask = (
    ((df["type_id"] == 7) & (df["outcome"] == 0))
    | (df["type_id"] == 45)
)

own_won = (
    df[own_won_mask]
    .groupby(["game_id", "team_id"])
    .size()
    .rename("own_won")
)
own_lost = (
    df[own_lost_mask]
    .groupby(["game_id", "team_id"])
    .size()
    .rename("own_lost")
)

# --- Take-on events (team_id = attacker, reattribute to defender) ---
takeon = df[(df["type_id"] == 3) & df["opponent_team_id"].notna()].copy()
takeon["defender_team_id"] = takeon["opponent_team_id"]

takeon_won = (
    takeon[takeon["outcome"] == 0]  # attacker failed -> defender won
    .groupby(["game_id", "defender_team_id"])
    .size()
    .rename("takeon_won")
    .rename_axis(index=["game_id", "team_id"])
)
takeon_lost = (
    takeon[takeon["outcome"] == 1]  # attacker succeeded -> defender lost
    .groupby(["game_id", "defender_team_id"])
    .size()
    .rename("takeon_lost")
    .rename_axis(index=["game_id", "team_id"])
)

variable_df3 = (
    pd.concat([own_won, own_lost, takeon_won, takeon_lost], axis=1)
    .fillna(0)
    .astype(int)
    .reset_index()
)

variable_df3["defensive_duels_won"] = (
    variable_df3["own_won"] + variable_df3["takeon_won"]
)
variable_df3["defensive_duels_lost"] = (
    variable_df3["own_lost"] + variable_df3["takeon_lost"]
)

_denom = (
    variable_df3["defensive_duels_won"] + variable_df3["defensive_duels_lost"]
)
variable_df3["defensive_duels_won_%"] = np.where(
    _denom > 0,
    variable_df3["defensive_duels_won"] / _denom,
    np.nan,
)

variable_df3 = variable_df3[[
    "game_id",
    "team_id",
    "defensive_duels_won",
    "defensive_duels_lost",
    "defensive_duels_won_%",
]]
variable_df3.head(100).to_csv("variable_df3.csv", index=True)

variable_df = variable_df.merge(
    variable_df3[["game_id", "team_id", "defensive_duels_won_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["defensive_duels_won_%"] = (
    variable_df["defensive_duels_won_%"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 4
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

variable_df4 = (
    progcarry_df[defensive_mask]
    .groupby(["game_id", "team_id"], as_index=False)["start_x"]
    .mean()
    .rename(columns={"start_x": "defensive_height"})
)

# Convert the 0-100 pitch percentage to meters on a UEFA-standard pitch.
variable_df4["defensive_height"] = (
    variable_df4["defensive_height"] * PITCH_LENGTH_M / 100.0
)

variable_df4.head(100).to_csv("variable_df4.csv", index=True)

variable_df = variable_df.merge(
    variable_df4[["game_id", "team_id", "defensive_height"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["defensive_height"] = variable_df["defensive_height"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 5
#Opp. Pass tempo
"""However, it generally refers to the speed at which the opposing team moves the ball through
passing. This can be influenced by the opposition's playing style, such as direct attacking or
possession-based football.
"""
# Opposition Pass Tempo
#
# pass_tempo = successful passes per minute of possession
#            = total_successful_passes / (total_possession_time_seconds / 60)
#
# opposition_pass_tempo = the opponent's pass_tempo in the same match, joined
# onto each team's row so downstream models see "how fast did the team I was
# playing against move the ball".
#
# Reads from progcarry_chains_df — the non-destructive valid-chain view built
# by possession_chain_code.py (possessionId != 0). In that view:
#   - A chain's total duration in seconds is stored on its last_chain == 1
#     row as `possession_time`.
#   - A team's events during its own possession chains are the events in
#     that view filtered to team_id.

# --- per-team, per-game pass tempo ---

_pass_mask = (
    (progcarry_chains_df["type_id"] == 1)
    & (progcarry_chains_df["outcome"] == 1)
)
successful_passes = (
    progcarry_chains_df.loc[_pass_mask]
    .groupby(["game_id", "team_id"])
    .size()
    .rename("successful_passes")
)

# Derive possession seconds from chain durations (max - min time per chain),
# reusing the same approach as the possession dataframe built earlier.
_chain_time = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations = (
    progcarry_chains_df.assign(_time=_chain_time)
    .loc[progcarry_chains_df["possessionId"] != 0]
    .groupby(["game_id", "team_id", "possessionId"])["_time"]
    .agg(lambda t: t.max() - t.min())
)
possession_seconds = (
    _chain_durations
    .groupby(["game_id", "team_id"])
    .sum()
    .rename("possession_seconds")
)

variable_df5 = (
    pd.concat([successful_passes, possession_seconds], axis=1)
    .fillna(0)
    .reset_index()
)

variable_df5["pass_tempo"] = np.where(
    variable_df5["possession_seconds"] > 0,
    variable_df5["successful_passes"] / (variable_df5["possession_seconds"] / 60.0),
    np.nan,
)

# --- opposition swap: each team's row stores the other team's pass_tempo ---
# Self-merge on game_id, exclude the same-team row, and keep the opponent's
# tempo. For standard two-team fixtures this yields exactly one opposition
# row per team.
_team_tempo = variable_df5[["game_id", "team_id", "pass_tempo"]]
_opposition = (
    _team_tempo.merge(
        _team_tempo.rename(
            columns={
                "team_id": "opponent_team_id",
                "pass_tempo": "opposition_pass_tempo",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opposition_pass_tempo"]]
)

variable_df5 = variable_df5.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)

variable_df5 = variable_df5[[
    "game_id",
    "team_id",
    "successful_passes",
    "possession_seconds",
    "pass_tempo",
    "opposition_pass_tempo",
]]
variable_df5.head(100).to_csv("variable_df5.csv", index=True)

variable_df = variable_df.merge(
    variable_df5[["game_id", "team_id", "opposition_pass_tempo"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["opposition_pass_tempo"] = (
    variable_df["opposition_pass_tempo"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 6
#Opp. Possession to final third %
"""Opp. Possession to final third % is not explicitly defined in the provided information. However,
it generally refers to the percentage of the opposing team's possessions that successfully progress
into the final third of the pitch. This metric helps in understanding how effectively the opposition
can penetrate the defensive setup and advance towards the goal.
"""

# Opp. Possession to Final Third %
#
# Share of the OPPONENT's possessions that successfully advance into the
# final third of the pitch. Computed per team first, then swapped so each
# team's row carries the other team's share.
#
# Reads from progcarry_chains_df (the non-destructive valid-chain view
# built by possession_chain_code.py, where possessionId != 0).
#
# Final-third boundary: per Opta F24 Appendix 11 (reference/Opta-f24_
# appendices.md line 950), start_x and end_x are 0-100 percentages and
# every team attacks from x=0 toward x=100, so the attacking final third
# is start_x >= 200/3 (~66.67).
#
# Denominator choice: a possession counts as "valid" only if its first
# event starts OUTSIDE the final third. Possessions that already begin in
# the final third can't progress INTO it, so they're excluded from both
# numerator and denominator.

FINAL_THIRD = 200.0 / 3.0  # ~66.67

df = progcarry_chains_df[
    ["game_id", "team_id", "possessionId", "start_x", "end_x"]
].copy()

# Per-event: did this single event cross the final-third line on entry?
df["crosses_final_third"] = (
    (df["start_x"] < FINAL_THIRD) & (df["end_x"] >= FINAL_THIRD)
)

# Collapse to one row per possession chain.
possession_stats = (
    df.groupby(["game_id", "team_id", "possessionId"], as_index=False)
    .agg(
        first_start_x=("start_x", "first"),
        any_cross=("crosses_final_third", "any"),
    )
)

# Keep only possessions that started outside the final third.
valid_possessions = possession_stats.loc[
    possession_stats["first_start_x"] < FINAL_THIRD
]

# Aggregate to team-game level.
team_stats = (
    valid_possessions.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_valid_possessions=("possessionId", "count"),
        final_third_entries=("any_cross", "sum"),
    )
)
team_stats["progression_percentage"] = np.where(
    team_stats["total_valid_possessions"] > 0,
    team_stats["final_third_entries"]
    / team_stats["total_valid_possessions"]
    * 100.0,
    np.nan,
)

# Opposition swap: self-merge on game_id, exclude same-team rows, keep the
# opponent's progression as opposition_progression_percentage.
_team_for_swap = team_stats[["game_id", "team_id", "progression_percentage"]]
_opposition = (
    _team_for_swap.merge(
        _team_for_swap.rename(
            columns={
                "team_id": "opponent_team_id",
                "progression_percentage": "opposition_progression_percentage",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opposition_progression_percentage"]]
)

variable_df6 = team_stats.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)[
    [
        "game_id",
        "team_id",
        "total_valid_possessions",
        "final_third_entries",
        "progression_percentage",
        "opposition_progression_percentage",
    ]
]

variable_df6.head(100).to_csv("variable_df6.csv", index=True)

variable_df = variable_df.merge(
    variable_df6[["game_id", "team_id", "opposition_progression_percentage"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["opposition_progression_percentage"] = (
    variable_df["opposition_progression_percentage"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 7
#Opp. Final third to box %
"""Refers to the percentage of possessions or passes that successfully move from the final
third of the pitch into the opponent's penalty box. This metric helps in understanding how
effectively the opposition can penetrate the defensive setup and create scoring opportunities."""

# Opp. Final Third to Box %
#
# Percentage of possessions that successfully move from the final third
# into the penalty box. Computed per team, then swapped so each team's
# row carries the opponent's value.
#
# Reads from progcarry_chains_df (possessionId != 0) since this is a
# per-possession metric.
#
# Opta F24 coordinate reference (Appendix 11, line 957):
#   Final third: start_x >= 66.67 (200/3)
#   Penalty box: x >= 83, 21.1 <= y <= 78.9

FINAL_THIRD = 200.0 / 3.0
BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

df7 = progcarry_chains_df[
    ["game_id", "team_id", "possessionId", "start_x", "start_y"]
].copy()

in_box = (df7["start_x"] >= BOX_X) & (df7["start_y"].between(BOX_Y_MIN, BOX_Y_MAX))
in_final_third_not_box = (df7["start_x"] >= FINAL_THIRD) & ~in_box

df7["in_final_third_not_box"] = in_final_third_not_box
df7["in_box"] = in_box

chain_stats = df7.groupby(["game_id", "team_id", "possessionId"], as_index=False).agg(
    has_final_third=("in_final_third_not_box", "any"),
    has_box=("in_box", "any"),
)

chain_stats["entered_box_from_final_third"] = (
    chain_stats["has_final_third"] & chain_stats["has_box"]
)

valid = chain_stats[chain_stats["has_final_third"]]

team_stats = valid.groupby(["game_id", "team_id"], as_index=False).agg(
    final_third_possessions=("possessionId", "count"),
    box_entries=("entered_box_from_final_third", "sum"),
)

team_stats["progression_percentage"] = np.where(
    team_stats["final_third_possessions"] > 0,
    team_stats["box_entries"] / team_stats["final_third_possessions"] * 100.0,
    np.nan,
)

_swap_cols = team_stats[["game_id", "team_id", "progression_percentage"]]
_opposition = (
    _swap_cols.merge(
        _swap_cols.rename(columns={
            "team_id": "opponent_team_id",
            "progression_percentage": "opp_final_third_to_box_%",
        }),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opp_final_third_to_box_%"]]
)

variable_df7 = team_stats.merge(_opposition, on=["game_id", "team_id"], how="left")

variable_df7 = variable_df7[[
    "game_id",
    "team_id",
    "final_third_possessions",
    "box_entries",
    "progression_percentage",
    "opp_final_third_to_box_%",
]]

variable_df7.head(100).to_csv("variable_df7.csv", index=True)

variable_df = variable_df.merge(
    variable_df7[["game_id", "team_id", "opp_final_third_to_box_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["opp_final_third_to_box_%"] = variable_df["opp_final_third_to_box_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 8
#Opp. xT
"""Opp. xT stands for "Opposition Expected Threat." It is defined as the accumulated action-based
expected threat (xT) per 100 successful opponent passes originating from within the player's
defensive area. This metric helps in understanding how much threat the opposition's passes from
a player's defensive area contribute to potential scoring opportunities."""

# Opp. xT — Opposition Expected Threat from defensive-area successful passes
#
# Accumulated action-based xT from the OPPONENT's successful passes that
# originate in the team's defensive area. A downstream step normalizes this
# per 100 opponent passes; this file outputs the raw accumulated xT (and the
# pass count, in case the downstream normalizer wants it from here).
#
# Filters applied, per the metric definition:
#   1. type_id == 1     Pass only. Opta F24 event type 1 = Pass
#                       (reference/Opta-f24_appendices.md line 43).
#   2. outcome          Successful passes only.
#   3. start_x >= 200/3 Pass originates in the event team's attacking
#                       third (~66.67). Opta F24 Appendix 11 (line 950)
#                       normalizes every event L->R in the event team's
#                       attacking direction, so the OPPONENT's attacking
#                       third is geometrically the team's defensive area.
#
# Note on xthreat: upstream progcarry_df currently exposes `xthreat` as a
# binary flag; the filters below are independent of that and stay correct
# once xthreat is replaced with continuous xT values.

DEFENSIVE_AREA_THRESHOLD = 200.0 / 3.0  # ~66.67

_passes = progcarry_df.loc[
    (progcarry_df["type_id"] == 1)
    & (progcarry_df["outcome"] == 1)
    & (progcarry_df["start_x"] >= DEFENSIVE_AREA_THRESHOLD),
    ["game_id", "team_id", "xthreat"],
]

team_stats = (
    _passes.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        defensive_area_pass_xt=("xthreat", "sum"),
        defensive_area_pass_count=("xthreat", "size"),
    )
)

# Opposition swap: self-merge on game_id, exclude same-team rows, keep the
# opponent's accumulated xT as Opposition_xT.
_opposition = (
    team_stats.merge(
        team_stats.rename(
            columns={
                "team_id": "opponent_team_id",
                "defensive_area_pass_xt": "Opposition_xT",
                "defensive_area_pass_count": "opposition_defensive_area_pass_count",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "Opposition_xT", "opposition_defensive_area_pass_count"]]
)

variable_df8 = team_stats.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)[
    [
        "game_id",
        "team_id",
        "defensive_area_pass_xt",
        "defensive_area_pass_count",
        "Opposition_xT",
        "opposition_defensive_area_pass_count",
    ]
]

variable_df8.head(100).to_csv("variable_df8.csv", index=True)

variable_df = variable_df.merge(
    variable_df8[["game_id", "team_id", "Opposition_xT"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["Opposition_xT"] = variable_df["Opposition_xT"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 9
#Turnovers
"""Turnovers are defined as the number of possessions lost due to failed passes, bad ball touches, or
lost attacking duels. This metric is particularly measured in the context of high turnovers, which
occur in a team's own 40% of the pitch and are adjusted by possession. High turnovers indicate
how frequently a team loses possession in dangerous areas, potentially leading to scoring
opportunities for the opposition."""

# High Turnovers
#
# Count of possession-losing events that occur in the team's own 40% of
# the pitch. Downstream code adjusts this by possession share.
#
# Own-40% filter: per Opta F24 Appendix 11 (reference/Opta-f24_appendices.md
# line 950), every event is normalized L->R in the event team's attacking
# direction, so the team's own goal is at x=0. "Own 40%" therefore means
# start_x <= 40.
#
# Event-type selection, per the metric definition ("possessions lost due to
# failed passes, bad ball touches, or lost attacking duels"):
#
#   type_id 1   Pass,         outcome=False -> failed pass
#   type_id 3   Take On,      outcome=False -> failed dribble attempt
#   type_id 50  Dispossessed                -> player tackled off the ball
#                                              (Opta outcome always 1)
#   type_id 51  Error                       -> mistake losing the ball
#                                              (Opta outcome always 1)
#   type_id 61  Ball touch                  -> bad touch / ball hit player;
#                                              both outcomes lose the ball
#                                              (ref line 830)
#
# Intentionally NOT counted:
#   - type_id 44 (Aerial): a 50/50 ball in the air is not a "lost attacking
#     duel" in the possession sense; counting every lost header in the own
#     40% would over-count defensive clearances.
#   - type_id 45 (Challenge): by Opta's definition (ref line 101) this is a
#     defender failing to win the ball as an opponent dribbles past — the
#     challenging team never had possession, so it is not a turnover.
#
# Note on chain length: the original code gated on `last_chain == 1`, which
# `possession_chain_code.py` only sets on chains of >= 2 events. That
# silently dropped isolated single-event turnovers, i.e. exactly the fast
# losses this metric is meant to capture. The event-type filter already
# carries the "possession lost" semantics, so the chain guard is removed.

OWN_FORTY_THRESHOLD = 40.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_turnover_events = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

filtered_df9 = progcarry_df.loc[
    _turnover_events & (progcarry_df["start_x"] <= OWN_FORTY_THRESHOLD),
    ["game_id", "team_id"],
]

variable_df9 = (
    filtered_df9.groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "high_turnovers"})
)

variable_df9.head(100).to_csv("variable_df9.csv", index=True)

variable_df = variable_df.merge(
    variable_df9[["game_id", "team_id", "high_turnovers"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["high_turnovers"] = variable_df["high_turnovers"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 10
#Turnover line height (m)
"""Turnover line height (m) refers to the average height on the pitch, measured in meters, where turnovers
(possessions lost) occur. This metric helps in understanding at what point on the pitch a team is
losing possession."""

# Turnover Line Height (m)
#
# Average pitch height at which a team loses possession, expressed in
# meters from that team's own goal line. Downstream code uses this to
# characterize how high up the pitch each team gives the ball away.
#
# Coordinate & unit note: per Opta F24 Appendix 11 (reference/Opta-f24_
# appendices.md line 950), start_x is a 0-100 percentage normalized L->R
# in the event team's attacking direction. To report meters we scale by
# the UEFA-standard pitch length (105 m), matching possession_chain_code.py
# (PITCH_LENGTH_M = 105.0).
#
# Event-type selection matches variable_df9_code.py ("possessions lost due
# to failed passes, bad ball touches, or lost attacking duels"):
#
#   type_id 1   Pass,         outcome=False -> failed pass
#   type_id 3   Take On,      outcome=False -> failed dribble attempt
#   type_id 50  Dispossessed                -> player tackled off the ball
#   type_id 51  Error                       -> mistake losing the ball
#   type_id 61  Ball touch                  -> bad touch / ball hit player
#
# Intentionally NOT counted (same reasoning as variable_df9_code.py):
#   - type_id 44 (Aerial): 50/50 air ball, not a possession loss.
#   - type_id 45 (Challenge): defender fails to dispossess a dribbler;
#     the challenging team never had the ball.
#
# Location: start_x is used (not end_x) so the turnover is located at the
# point it originated from. This is consistent with variable_df9_code.py,
# which measures "own 40%" as start_x <= 40.
#
# Chain guard: the original code filtered on `last_chain == 1`, which
# `possession_chain_code.py` only sets on chains of >= 2 events. That
# silently dropped isolated single-event turnovers -- exactly the quick
# losses this metric is meant to characterize -- so the guard is removed.
# The event-type filter alone carries the "possession lost" semantics.
#
# NaN handling: if a team had no qualifying turnovers in a game, the
# merged column is left as NaN rather than filled with 0. A value of 0 m
# would place the turnover line on the team's own goal line and bias any
# downstream averaging. Downstream code should treat NaN explicitly.

PITCH_LENGTH_M = 105.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_turnover_events = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

turnovers = progcarry_df.loc[
    _turnover_events,
    ["game_id", "team_id", "start_x"],
]

variable_df10 = (
    turnovers.groupby(["game_id", "team_id"], as_index=False)["start_x"]
    .mean()
    .rename(columns={"start_x": "turnover_line_height"})
)
variable_df10["turnover_line_height"] = (
    variable_df10["turnover_line_height"] * PITCH_LENGTH_M / 100.0
)

variable_df10.head(100).to_csv("variable_df10.csv", index=True)

variable_df = variable_df.merge(
    variable_df10[["game_id", "team_id", "turnover_line_height"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 11
#Recoveries within 5s %
"""Recoveries within 5s % refers to the percentage of ball recoveries that occur within 5 seconds of
losing possession. This metric highlights a team's or player's ability to quickly regain control of
the ball after losing it, often through effective pressing and counterpressing strategies."""
# Recoveries Within 5s %
#
# Percentage of a team's ball recoveries that happen within 5 seconds of
# that team losing the ball. Captures pressing / counter-pressing speed.
#
# Loss events (matches variable_df9_code.py):
#   type_id 1   Pass,         outcome=False -> failed pass
#   type_id 3   Take On,      outcome=False -> failed dribble attempt
#   type_id 50  Dispossessed                -> player tackled off the ball
#   type_id 51  Error                       -> mistake losing the ball
#   type_id 61  Ball touch                  -> bad touch / ball hit player
#
# Recovery events (Opta "team wins the ball" categories that are present
# in progcarry_df):
#   type_id 49  Ball recovery            (Opta outcome always 1, ref line 818)
#   type_id 7   Tackle,     outcome=True (successful tackle wins possession)
#   type_id 44  Aerial,     outcome=True (wins the aerial duel)
#   type_id 11  Claim,      outcome=True (GK cleanly catches the cross)
#
# Intentionally NOT counted as recoveries:
#   - type_id 3  Take On:   player already has the ball; not a recovery.
#   - type_id 4  Foul:      free kick to fouled player, not a "ball win".
#   - type_id 45 Challenge: defender FAILS to win the ball (outcome always 0
#                           per ref line 816) -- the opposite of a recovery.
#   - type_id 54 Smother:   not present in progcarry_df (upstream filter).
#   - type_id 55 Offside provoked: possession awarded, not a ball win.
#
# Pairing: pd.merge_asof(..., direction="backward", by=[game_id, team_id,
# period_id]) finds, for each recovery, the most recent same-team loss
# with loss_time <= recovery_time inside the same period. Recoveries whose
# prior loss falls within 5s are counted in the numerator; all recoveries
# are in the denominator. Each recovery is paired at most once, so no
# double-counting. Grouping by period_id prevents a loss at the end of H1
# from pairing with a recovery at the start of H2, since `time` is per-
# period seconds per possession_chain_code.py.
#
# Chain guard: the original code gated on last_chain == 1 / first_chain == 1
# which possession_chain_code.py only sets on chains of >= 2 events,
# silently dropping exactly the fast press-recover cycles this metric is
# meant to measure. The event-type filter alone carries the semantics, so
# the chain guard is removed.
#
# NaN: teams with zero recoveries leave the merged column as NaN rather
# than being filled with 0, so "no data" stays distinct from "0%".

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
    | ((_type_id == 8))
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

# For each recovery, find the most recent prior same-team loss in the same
# (game, period).
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

variable_df11 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_recoveries=("recovery_time", "size"),
        recoveries_within_5s=("within_window", "sum"),
    )
)
variable_df11["recoveries_within_5s_%"] = np.where(
    variable_df11["total_recoveries"] > 0,
    variable_df11["recoveries_within_5s"]
    / variable_df11["total_recoveries"]
    * 100.0,
    np.nan,
)

variable_df11 = variable_df11[
    [
        "game_id",
        "team_id",
        "total_recoveries",
        "recoveries_within_5s",
        "recoveries_within_5s_%",
    ]
]

variable_df11.head(100).to_csv("variable_df11.csv", index=True)

variable_df = variable_df.merge(
    variable_df11[["game_id", "team_id", "recoveries_within_5s_%"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 12
#Time to defensive action (s)
"""Time to defensive action (s) refers to the time taken for a player or team to perform a defensive action, 
such as a tackle, interception, or clearance, after losing possession. This metric helps in understanding the
responsiveness and reaction time of a player or team in defensive situations."""

# Time to Defensive Action (s)
#
# Average seconds between a team losing the ball and that same team's
# next defensive action, per team per game. Captures how quickly a side
# reacts once dispossessed.
#
# Loss events (same set as variable_df9_code.py):
#   type_id 1   Pass,         outcome=False -> failed pass
#   type_id 3   Take On,      outcome=False -> failed dribble attempt
#   type_id 50  Dispossessed                -> player tackled off the ball
#   type_id 51  Error                       -> mistake losing the ball
#   type_id 61  Ball touch                  -> bad touch / ball hit player
#
# Defensive-action events (the metric's examples are tackle, interception,
# and clearance):
#   type_id 7   Tackle        -> tackle, both outcomes (attempt counts)
#   type_id 44  Aerial        -> aerial duel, both outcomes (attempt counts)
#   type_id 49  Ball recovery -> Opta "team wins the ball" event
#
# Interception (type_id 8) and Clearance (type_id 12) are included in the
# defensive action set below, matching the metric definition.
#
# Pairing: pd.merge_asof(direction="forward", by=[game_id, team_id,
# period_id]) finds, for each loss, the immediately-next same-team
# defensive action in the same period. Each loss is paired at most once,
# so there is no cross-product inflation. Grouping by period_id prevents
# a loss at the end of H1 from pairing with an event at the start of H2
# (time is per-period seconds in progcarry_df).
#
# Chain guard: the original code used `last_chain == 1` as the loss marker,
# which possession_chain_code.py only sets on chains of >= 2 events and
# thus silently dropped isolated quick losses. Using the event-type loss
# mask directly removes that bias, matching variable_df9_code.py.
#
# NaN: teams with no qualifying losses or no subsequent defensive actions
# leave the merged column as NaN. Filling with 0 would read as "reacted
# instantly," indistinguishable from "no data", and would bias downstream
# averaging.

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_loss_mask = (
    ((_type_id == 1) & ~_outcome)
    | ((_type_id == 3) & ~_outcome)
    | (_type_id == 50)
    | (_type_id == 51)
    | (_type_id == 61)
)

_defensive_mask = (
    (_type_id == 7)
    | (_type_id == 8)
    | (_type_id == 12)
    | (_type_id == 44)
    | (_type_id == 49)
)

_losses = (
    progcarry_df.loc[_loss_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "loss_time"})
    .sort_values("loss_time", kind="mergesort")
    .reset_index(drop=True)
)

_defensive_actions = (
    progcarry_df.loc[_defensive_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "defensive_time"})
    .sort_values("defensive_time", kind="mergesort")
    .reset_index(drop=True)
)

# For each loss, find the next same-team defensive action in the same
# (game, period). `allow_exact_matches=False` ensures defensive_time is
# strictly greater than loss_time (two events can legitimately share a
# `time` value since it is integer seconds).
_paired = pd.merge_asof(
    _losses,
    _defensive_actions,
    left_on="loss_time",
    right_on="defensive_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)

_paired = _paired.loc[_paired["defensive_time"].notna()].copy()
_paired["time_to_defensive_action"] = (
    _paired["defensive_time"] - _paired["loss_time"]
)

variable_df12 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["time_to_defensive_action"]
    .mean()
    .rename(columns={"time_to_defensive_action": "avg_time_to_defensive_action"})
)

variable_df12.head(100).to_csv("variable_df12.csv", index=True)

variable_df = variable_df.merge(
    variable_df12[["game_id", "team_id", "avg_time_to_defensive_action"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 13
#Time to recovery (s)
"""Time to recovery (s) refers to the time taken for a team to recover possession of 
the ball after losing it. This metric helps in understanding the efficiency and speed of a 
team's ability to regain control of the ball"""

# Time to Recovery (s)
#
# Average seconds between a team losing the ball and that same team
# winning it back, per team per game. Captures how quickly a side
# regains possession after giving it away.
#
# Loss events (same set as variable_df9_code.py):
#   type_id 1   Pass,         outcome=False -> failed pass
#   type_id 3   Take On,      outcome=False -> failed dribble attempt
#   type_id 50  Dispossessed                -> player tackled off the ball
#   type_id 51  Error                       -> mistake losing the ball
#   type_id 61  Ball touch                  -> bad touch / ball hit player
#
# Recovery events (same set as variable_df11_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True (successful tackle wins possession)
#   type_id 44  Aerial,     outcome=True (wins the aerial duel)
#   type_id 11  Claim,      outcome=True (GK cleanly catches the cross)
#
# This mirrors variable_df11_code.py's loss / recovery definitions so
# the two metrics stay consistent: df11 is the within-5s share of the
# same distribution this file averages.
#
# Pairing: pd.merge_asof(direction="forward", by=[game_id, team_id,
# period_id]) finds, for each loss, the immediately-next same-team
# recovery in the same period. Each loss is paired at most once, so
# there is no cross-product inflation. `allow_exact_matches=False`
# enforces strictly recovery_time > loss_time (time is integer seconds
# in progcarry_df, so same-second ties are possible). Grouping by
# period_id prevents a loss at the end of H1 from pairing with a
# recovery at the start of H2, since `time` is per-period seconds.
#
# Chain guard: the original code gated on last_chain == 1 / first_chain
# == 1, which possession_chain_code.py only sets on chains of >= 2
# events. That silently dropped isolated quick losses and isolated
# short recoveries -- exactly the fast transitions this metric targets.
# Using the event-type masks directly removes that bias.
#
# "last_chain as loss" framing: the original also treated any chain-end
# as a loss, which included end-of-period / end-of-game / post-shot
# chain ends and inflated the mean. Restricting to actual possession-
# losing event types matches the metric's "after losing it" wording.
#
# NaN: losses with no subsequent recovery in the same period are
# excluded from the per-game mean (merge_asof returns NaN, then the
# groupby mean skips it). Teams with zero usable loss->recovery pairs
# leave the merged column as NaN rather than being filled with 0, so
# "no data" stays distinct from "recovered instantly."

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
    | ((_type_id == 8))
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

# For each loss, find the next same-team recovery in the same
# (game, period). allow_exact_matches=False -> recovery_time strictly > loss_time.
_paired = pd.merge_asof(
    _losses,
    _recoveries,
    left_on="loss_time",
    right_on="recovery_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=False,
)

_paired = _paired.loc[_paired["recovery_time"].notna()].copy()
_paired["time_to_recovery"] = _paired["recovery_time"] - _paired["loss_time"]

variable_df13 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["time_to_recovery"]
    .mean()
    .rename(columns={"time_to_recovery": "avg_recovery_time"})
)

variable_df13.head(100).to_csv("variable_df13.csv", index=True)

variable_df = variable_df.merge(
    variable_df13[["game_id", "team_id", "avg_recovery_time"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 14
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
# Opposition swap: for team T in game G, variable_df14 carries the
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

variable_df14 = _team_stats.merge(
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

variable_df14.head(100).to_csv("variable_df14.csv", index=True)

variable_df = variable_df.merge(
    variable_df14[["game_id", "team_id", "opposition_final_third_entries_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["opposition_final_third_entries_10s"] = (
    variable_df["opposition_final_third_entries_10s"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 15
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

variable_df15 = _team_stats.merge(
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

variable_df15.head(100).to_csv("variable_df15.csv", index=True)

variable_df = variable_df.merge(
    variable_df15[["game_id", "team_id", "opposition_box_entries_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["opposition_box_entries_10s"] = (
    variable_df["opposition_box_entries_10s"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 16
#Opposition xG within 10s after recovery
"""Opposition xG within 10s after recovery refers to the accumulated non-penalty expected goals (xG)
from the opponent's shots that occur within 10 seconds after they recover possession. This metric
helps in understanding the quality of scoring chances the opposition creates quickly after
regaining the ball. It provides insight into the effectiveness of the opponent's counter-attacking
capabilities."""

# Opposition xG Within 10s After Recovery
#
# For each team T, the total non-penalty xG from the OPPONENT's shots
# that occur within 10 seconds of the opponent winning the ball.
# Captures the quality of chances the opposition creates from fast
# counter-attacks. Direct analog of variable_df14_code.py /
# variable_df15_code.py, but accumulates xG on shots instead of
# counting recoveries that reached a zone.
#
# Recovery events (same set as variable_df11_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
# Shot selection: any progcarry_df row with xG > 0. The xG column is
# already present on progcarry_df, so the original code's legacy re-merge
# from a separate `xg_df` is dropped -- that merge collides with the
# existing `xG` column under current pandas behavior and either raises
# or drops the merged column silently.
#
# Non-penalty filter: penalties are flagged by Opta qualifier 9 (ref
# line 213), detected via the has_qualifier helper.
#
# Pairing: for each shot, find the most recent same-team recovery at or
# before the shot (pd.merge_asof direction="backward"). If the gap is
# <= 10s the shot's xG is attributed to that recovery window. This
# shot-side asof is the natural fit for "accumulated xG" -- every shot
# contributes at most once, and a single recovery can carry xG from
# multiple shots within its 10s window. Grouping by period_id prevents
# cross-half pairings (progcarry_df `time` is per-period seconds).
#
# Short-chain bias: the original gated recoveries on `first_chain == 1`,
# which possession_chain_code.py only sets on chains of >= 2 events,
# silently dropping fast transitions. The event-type mask alone carries
# the "team won the ball" semantics.
#
# Semantic fix: the original paired THIS team's recoveries with
# OPPOSITION events in the next 10s, then never applied an opposition
# swap, storing the wrong value against each team. This rewrite sums
# fast-transition xG per team, then swaps so team T's row carries the
# OPPONENT's sum.
#
# NaN -> 0: xG sum; zero is a real, meaningful value.

WINDOW_SECONDS = 10.0

# Merge xG from xg_df onto progcarry_df if the column is missing
if "xG" not in progcarry_df.columns:
    progcarry_df = progcarry_df.merge(
        xg_df[["game_id", "event_id", "xG"]],
        on=["game_id", "event_id"],
        how="left",
    )
    progcarry_df["xG"] = progcarry_df["xG"].fillna(0.0)
    if (progcarry_df["xG"] != 0).sum() == 0:
        raise RuntimeError("xG merge produced all-zero xG column — event_id key space drift between xg_df and progcarry_df")

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | ((_type_id == 8))
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_is_penalty = progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 9))
_shot_mask = (progcarry_df["xG"] > 0) & ~_is_penalty

_recoveries = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_shots = (
    progcarry_df.loc[_shot_mask, ["game_id", "team_id", "period_id", "time", "xG"]]
    .rename(columns={"time": "shot_time"})
    .sort_values("shot_time", kind="mergesort")
    .reset_index(drop=True)
)

# For each shot, find the most recent same-team recovery at or before
# the shot in the same (game, period). Shots with a qualifying recovery
# within 10s contribute their xG; shots outside the window are dropped.
_paired = pd.merge_asof(
    _shots,
    _recoveries,
    left_on="shot_time",
    right_on="recovery_time",
    by=["game_id", "team_id", "period_id"],
    direction="backward",
    allow_exact_matches=True,
)

_paired = _paired.loc[
    _paired["recovery_time"].notna()
    & ((_paired["shot_time"] - _paired["recovery_time"]) <= WINDOW_SECONDS)
].copy()

_team_stats = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["xG"]
    .sum()
    .rename(columns={"xG": "xG_10s"})
)

# Opposition swap: attach each team's total to the OTHER team's row.
_opposition = (
    _team_stats.merge(
        _team_stats.rename(
            columns={
                "team_id": "opponent_team_id",
                "xG_10s": "opposition_xG_10s",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opposition_xG_10s"]]
)

variable_df16 = _team_stats.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)[
    [
        "game_id",
        "team_id",
        "xG_10s",
        "opposition_xG_10s",
    ]
]

variable_df16.head(100).to_csv("variable_df16.csv", index=True)

variable_df = variable_df.merge(
    variable_df16[["game_id", "team_id", "opposition_xG_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["opposition_xG_10s"] = variable_df["opposition_xG_10s"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 17
#Recoveries
"""Recoveries refer to the number of times a team regains possession of the ball after losing
it. This can include various scenarios such as intercepting passes, winning duels, or collecting
loose balls."""

# Recoveries
#
# Count of times a team regains possession of the ball, per team per
# game. Matches the recovery event set used by variable_df11_code.py /
# variable_df13_code.py / variable_df14_code.py / variable_df15_code.py /
# variable_df16_code.py so all "recovery"-based metrics stay consistent.
#
# Recovery events:
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True (successful tackle wins possession)
#   type_id 44  Aerial,     outcome=True (wins the aerial duel)
#   type_id 11  Claim,      outcome=True (GK cleanly catches the cross)
#
# Chain guard: the original code gated on `first_chain == 1`, which
# possession_chain_code.py only sets on chains of >= 2 events. That
# silently dropped isolated single-event recoveries (team wins ball
# then immediately loses it again) and any genuine recovery event that
# happened not to start a valid chain. The event-type mask alone
# carries the "team won the ball" semantics, so the chain guard is
# removed.

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | ((_type_id == 8))
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

variable_df17 = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id"]]
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "recoveries"})
)

variable_df17.head(100).to_csv("variable_df17.csv", index=True)

variable_df = variable_df.merge(
    variable_df17[["game_id", "team_id", "recoveries"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["recoveries"] = variable_df["recoveries"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 18
#Recovery line height (m)
"""Recovery line height (m) refers to the average height on the pitch, measured in meters, where recoveries
(regaining possession) occur. This metric helps in understanding at what point on the pitch a team
or player typically regains possession."""

# Recovery Line Height (m)
#
# Average pitch height at which a team wins the ball back, expressed in
# meters from that team's own goal line. Downstream code uses this to
# characterize how high up the pitch a side recovers possession.
#
# Coordinate & unit note: per Opta F24 Appendix 11 (reference/Opta-f24_
# appendices.md line 950), start_x is a 0-100 percentage normalized L->R
# in the event team's attacking direction. To report meters we scale by
# the UEFA-standard pitch length (105 m), matching possession_chain_code.py
# (PITCH_LENGTH_M = 105.0) and variable_df10_code.py.
#
# Recovery events (same set as variable_df11_code.py / variable_df17_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True (successful tackle wins possession)
#   type_id 44  Aerial,     outcome=True (wins the aerial duel)
#   type_id 11  Claim,      outcome=True (GK cleanly catches the cross)
#
# Location: start_x is used (not end_x) so the recovery is located at
# the point it occurred. This matches variable_df10_code.py's choice for
# turnover line height.
#
# Chain guard: the original code gated on `first_chain == 1`, which
# possession_chain_code.py only sets on chains of >= 2 events, silently
# dropping isolated single-event recoveries. The event-type mask alone
# carries the "team won the ball" semantics.
#
# NaN handling: if a team had no qualifying recoveries in a game, the
# merged column is left as NaN rather than filled with 0. A value of
# 0 m would place the recovery line on the team's own goal line and
# bias any downstream averaging, same as variable_df10_code.py.

PITCH_LENGTH_M = 105.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | ((_type_id == 8))
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

recoveries = progcarry_df.loc[
    _recovery_mask,
    ["game_id", "team_id", "start_x"],
]

variable_df18 = (
    recoveries.groupby(["game_id", "team_id"], as_index=False)["start_x"]
    .mean()
    .rename(columns={"start_x": "recovery_height"})
)
variable_df18["recovery_height"] = (
    variable_df18["recovery_height"] * PITCH_LENGTH_M / 100.0
)

variable_df18.head(100).to_csv("variable_df18.csv", index=True)

variable_df = variable_df.merge(
    variable_df18[["game_id", "team_id", "recovery_height"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 19
#Possessions retained after 5s
"""Possessions retained after 5s refers to the number of times a team successfully maintains
possession of the ball for at least 5 seconds after initially gaining control. This metric helps in
understanding the ability to hold onto the ball under pressure and avoid immediate turnovers. It
is an indicator of effective ball control and composure in maintaining possession."""

# Possessions Retained After 5s
#
# Count of valid possession chains that lasted at least 5 seconds, per
# team per game. "Initially gaining control" is read at the possession
# level -- any chain start counts, regardless of how the team won the
# ball (active recovery, throw-in, goal kick, corner, kick-off, etc.).
#
# Chain duration is derived from progcarry_chains_df as max(time) -
# min(time) per chain, consistent with the possession dataframe and
# pass tempo calculations earlier in the pipeline.
#
# Short-chain note: possession_chain_code.py sets possessionId = 0 for
# chains of < 2 events (MIN_CHAIN_LEN = 2). Single-event "possessions"
# therefore never appear with last_chain == 1 and are excluded here --
# but a 1-event chain has zero duration by construction and could not
# have met the 5s threshold anyway, so this bias is harmless for this
# specific metric.

RETENTION_THRESHOLD_SECONDS = 5.0

# Derive chain duration from progcarry_chains_df (max - min time per chain).
_chain_time = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations = (
    progcarry_chains_df.assign(_time=_chain_time)
    .loc[progcarry_chains_df["possessionId"] != 0]
    .groupby(["game_id", "team_id", "possessionId"])["_time"]
    .agg(lambda t: t.max() - t.min())
    .reset_index(name="chain_duration")
)

_retained = _chain_durations.loc[
    _chain_durations["chain_duration"] >= RETENTION_THRESHOLD_SECONDS,
    ["game_id", "team_id"],
]

variable_df19 = (
    _retained.groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "retained_possessions_5s"})
)

variable_df19.head(100).to_csv("variable_df19.csv", index=True)

variable_df = variable_df.merge(
    variable_df19[["game_id", "team_id", "retained_possessions_5s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["retained_possessions_5s"] = (
    variable_df["retained_possessions_5s"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 20
#Possessions retained after 5s %
"""Possessions retained after 5s % refers to the percentage of times a team or player successfully
maintains possession of the ball for at least 5 seconds after initially gaining control. This metric
helps in understanding the ability to hold onto the ball under pressure and avoid immediate
turnovers. It is an indicator of effective ball control and composure in maintaining possession."""

# Possessions Retained After 5s %
#
# Percentage of a team's valid possession chains that lasted at least
# 5 seconds, per team per game. The rate analog of variable_df19_code.py
# (which outputs the raw count).
#
# Numerator:   chains with possession_time >= 5 seconds
# Denominator: all valid chains in the game-team (last_chain == 1)
#
# Chain duration is derived from progcarry_chains_df as max(time) -
# min(time) per chain, consistent with variable_df19 and the possession
# dataframe calculations earlier in the pipeline.
#
# Short-chain note: possession_chain_code.py sets possessionId = 0 for
# chains of < 2 events (MIN_CHAIN_LEN = 2). Single-event "possessions"
# are excluded from both numerator and denominator. A 1-event chain has
# zero duration so it could never meet the 5s threshold anyway; its
# exclusion only removes it from the denominator, which slightly
# inflates the rate. Document-and-accept, since changing MIN_CHAIN_LEN
# affects every downstream metric.

RETENTION_THRESHOLD_SECONDS = 5.0

# Derive chain duration from progcarry_chains_df (max - min time per chain).
_chain_time_20 = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations_20 = (
    progcarry_chains_df.assign(_time=_chain_time_20)
    .loc[progcarry_chains_df["possessionId"] != 0]
    .groupby(["game_id", "team_id", "possessionId"])["_time"]
    .agg(lambda t: t.max() - t.min())
    .reset_index(name="chain_duration")
)
_chain_durations_20["retained"] = (
    _chain_durations_20["chain_duration"] >= RETENTION_THRESHOLD_SECONDS
)

variable_df20 = (
    _chain_durations_20.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_valid_possessions=("retained", "size"),
        retained_possessions_5s=("retained", "sum"),
    )
)
variable_df20["retained_possessions_5s_%"] = np.where(
    variable_df20["total_valid_possessions"] > 0,
    variable_df20["retained_possessions_5s"]
    / variable_df20["total_valid_possessions"]
    * 100.0,
    np.nan,
)

variable_df20 = variable_df20[
    [
        "game_id",
        "team_id",
        "total_valid_possessions",
        "retained_possessions_5s",
        "retained_possessions_5s_%",
    ]
]

variable_df20.head(100).to_csv("variable_df20.csv", index=True)

variable_df = variable_df.merge(
    variable_df20[["game_id", "team_id", "retained_possessions_5s_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["retained_possessions_5s_%"] = (
    variable_df["retained_possessions_5s_%"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 21
#Final third entries within 10s after recovery
"""Final third entries within 10s after recovery refers to the number of times a team successfully
moves the ball into the final third of the pitch within 10 seconds after regaining possession. This
metric helps in understanding the effectiveness and speed of a team's transition from defense to
attack. It indicates how quickly a team can create potential scoring opportunities after recovering
the ball."""

# Final Third Entries Within 10s After Recovery
#
# Per team per game, the number of the team's OWN recoveries that are
# followed by a final-third event within 10 seconds. Captures how often
# the side converts a regained ball into a fast attack reaching the
# final third. Same machinery as variable_df14_code.py (opposition
# variant), minus the opposition swap.
#
# Recovery events (same set as variable_df11_code.py / variable_df14_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
# Final-third entry event: any event with end_x >= 200/3 (~66.67). Opta
# F24 Appendix 11 (reference/Opta-f24_appendices.md line 950) normalizes
# every event L->R in the event team's attacking direction, so end_x >=
# 2/3 is always the event team's attacking third. This is the single-
# predicate union of the original code's "crossed into" and "already in"
# disjunctions.
#
# Recovery inside the final third: a recovery whose own event already
# lands in the final third (a high press won deep) self-pairs at
# delta=0 via allow_exact_matches=True + direction="forward", matching
# the behavior of variable_df14_code.py.
#
# Pairing: pd.merge_asof(recoveries, entry_events, direction="forward",
# by=[game_id, team_id, period_id]) finds, for each recovery, the
# earliest same-team event at or after recovery_time whose end_x lands
# in the final third. If the gap is <= 10s the recovery is counted as
# a successful fast transition. O(n log n) and exact, versus the
# original nested iterrows + full-frame filter per recovery. Grouping
# by period_id prevents cross-half pairings since progcarry_df `time`
# is per-period seconds.
#
# Short-chain bias: the original gated recoveries on `first_chain == 1`,
# which possession_chain_code.py only sets on chains of >= 2 events,
# silently dropping fast transitions. The event-type mask alone carries
# the "team won the ball" semantics.
#
# NaN -> 0: count metric; zero fast transitions is a real, meaningful
# value.

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
# event already lands in the final third self-pair at delta=0.
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

variable_df21 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["within_window"]
    .sum()
    .rename(columns={"within_window": "final_third_entries_10s"})
)
variable_df21["final_third_entries_10s"] = (
    variable_df21["final_third_entries_10s"].astype(int)
)

variable_df21.head(100).to_csv("variable_df21.csv", index=True)

variable_df = variable_df.merge(
    variable_df21[["game_id", "team_id", "final_third_entries_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["final_third_entries_10s"] = (
    variable_df["final_third_entries_10s"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 22
#Box entries within 10s after recovery
"""Box entries within 10s after recovery refers to the number of times a team successfully moves the
ball into the opponent's penalty area within 10 seconds after regaining possession. This metric
helps in understanding the effectiveness and speed of a team's transition from defense to attack.
It indicates how quickly a team can create potential scoring opportunities in the penalty area after
recovering the ball."""

# Box Entries Within 10s After Recovery
#
# Per team per game, the number of the team's OWN recoveries that are
# followed by a penalty-box entry within 10 seconds. Captures how often
# the side converts a regained ball into a fast attack reaching the box.
# Same machinery as variable_df15_code.py (opposition variant), minus
# the opposition swap.
#
# Recovery events (same set as variable_df11_code.py / variable_df15_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
# Penalty box: Opta F24 Appendix 11 (reference/Opta-f24_appendices.md
# line 957) places the 18-yard box at x >= 83 and 21.1 <= y <= 78.9.
# A box-entry event is any event whose END coordinates land in the box,
# which is the single-predicate union of "crossed in" and "already in,
# stayed in".
#
# Recovery inside the box: a recovery whose own event ends in the box
# (a high press won deep) self-pairs at delta=0 via
# allow_exact_matches=True + direction="forward", matching the behavior
# of variable_df14_code.py / variable_df15_code.py / variable_df21_code.py.
#
# Pairing: pd.merge_asof(recoveries, box_entries, direction="forward",
# by=[game_id, team_id, period_id]) finds, for each recovery, the
# earliest same-team event at or after recovery_time whose end
# coordinates land in the box. If the gap is <= 10s the recovery is
# counted. O(n log n) and exact, versus the original nested iterrows +
# per-event apply. Grouping by period_id prevents cross-half pairings
# since progcarry_df `time` is per-period seconds.
#
# Short-chain bias: the original gated recoveries on `first_chain == 1`,
# which possession_chain_code.py only sets on chains of >= 2 events,
# silently dropping fast transitions. The event-type mask alone carries
# the "team won the ball" semantics.
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

variable_df22 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["within_window"]
    .sum()
    .rename(columns={"within_window": "box_entries_10s"})
)
variable_df22["box_entries_10s"] = variable_df22["box_entries_10s"].astype(int)

variable_df22.head(100).to_csv("variable_df22.csv", index=True)

variable_df = variable_df.merge(
    variable_df22[["game_id", "team_id", "box_entries_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["box_entries_10s"] = variable_df["box_entries_10s"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 23
#xG within 10s after recovery
"""xG within 10s after recovery refers to the accumulated non-penalty expected goals (xG) from
shots taken within 10 seconds after a team regains possession. This metric helps in understanding
the quality of scoring chances created quickly after recovering the ball. It provides insight into
the effectiveness of a team's counter-attacking capabilities."""

# xG Within 10s After Recovery
#
# Per team per game, the total non-penalty xG from the team's OWN shots
# that occur within 10 seconds of the team winning the ball. Captures
# the quality of chances a side creates from fast counter-attacks.
# Same machinery as variable_df16_code.py (opposition variant), minus
# the opposition swap.
#
# Recovery events (same set as variable_df11_code.py / variable_df16_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
# Shot selection: any progcarry_df row with xG > 0. The xG column is
# already present on progcarry_df, so no legacy re-merge from a separate
# `xg_df` is needed.
#
# Non-penalty filter: penalties are flagged by Opta qualifier 9 (ref
# line 213), detected via the has_qualifier helper.
#
# Pairing: for each shot, find the most recent same-team recovery at or
# before the shot (pd.merge_asof direction="backward"). If the gap is
# <= 10s the shot's xG is attributed to that recovery window. This
# shot-side asof is the natural fit for "accumulated xG" -- every shot
# contributes at most once, and a single recovery can carry xG from
# multiple shots within its 10s window. Grouping by period_id prevents
# cross-half pairings since progcarry_df `time` is per-period seconds.
#
# Short-chain bias: the original gated recoveries on `first_chain == 1`,
# which possession_chain_code.py only sets on chains of >= 2 events,
# silently dropping fast transitions. The event-type mask alone carries
# the "team won the ball" semantics.
#
# Double-counting fix: the original iterated recovery-side and, for each
# recovery, added every shot in the next 10s -- so a shot reachable from
# two recoveries had its xG counted twice. Shot-side backward merge_asof
# attributes each shot to exactly one recovery.
#
# NaN -> 0: xG sum; zero is a real, meaningful value.

WINDOW_SECONDS = 10.0

if "xG" not in progcarry_df.columns:
    progcarry_df = progcarry_df.merge(
        xg_df[["game_id", "event_id", "xG"]],
        on=["game_id", "event_id"],
        how="left",
    )
    progcarry_df["xG"] = progcarry_df["xG"].fillna(0.0)
    if (progcarry_df["xG"] != 0).sum() == 0:
        raise RuntimeError("xG merge produced all-zero xG column — event_id key space drift between xg_df and progcarry_df")

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | ((_type_id == 8))
    | ((_type_id == 44) & _outcome)
    | ((_type_id == 11) & _outcome)
)

_is_penalty = progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 9))
_shot_mask = (progcarry_df["xG"] > 0) & ~_is_penalty

_recoveries = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_shots = (
    progcarry_df.loc[_shot_mask, ["game_id", "team_id", "period_id", "time", "xG"]]
    .rename(columns={"time": "shot_time"})
    .sort_values("shot_time", kind="mergesort")
    .reset_index(drop=True)
)

# For each shot, find the most recent same-team recovery at or before
# the shot in the same (game, period). Shots with a qualifying recovery
# within 10s contribute their xG; shots outside the window are dropped.
_paired = pd.merge_asof(
    _shots,
    _recoveries,
    left_on="shot_time",
    right_on="recovery_time",
    by=["game_id", "team_id", "period_id"],
    direction="backward",
    allow_exact_matches=True,
)

_paired = _paired.loc[
    _paired["recovery_time"].notna()
    & ((_paired["shot_time"] - _paired["recovery_time"]) <= WINDOW_SECONDS)
].copy()

variable_df23 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["xG"]
    .sum()
    .rename(columns={"xG": "xG_10s"})
)

variable_df23.head(100).to_csv("variable_df23.csv", index=True)

variable_df = variable_df.merge(
    variable_df23[["game_id", "team_id", "xG_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["xG_10s"] = variable_df["xG_10s"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 24
#xT within 10s after recovery
"""xT within 10s after recovery refers to the accumulated expected threat (xT) generated from actions
such as passes, dribbles, or carries within 10 seconds after a team regains possession. This metric
helps in understanding the potential impact and danger created quickly after recovering the ball.
It provides insight into the effectiveness of a team's counter-attacking capabilities."""

# xT Within 10s After Recovery
#
# Per team per game, the total xT (expected threat) accumulated on the
# team's OWN events that occur within 10 seconds of the team winning
# the ball. Captures the danger a side creates from fast counter-
# attacks. Direct analog of variable_df23_code.py with xthreat
# replacing non-penalty xG.
#
# Recovery events (same set as variable_df11_code.py / variable_df23_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
# xT event selection: any progcarry_df row with xthreat > 0.
# The xthreat column contains continuous xT values merged from
# xT_brasileirao_2025.parquet; events without xT are filled with 0.
#
# Pairing: for each xT-bearing event, find the most recent same-team
# recovery at or before the event (pd.merge_asof direction="backward").
# If the gap is <= 10s the event's xthreat is attributed to that
# recovery window. This event-side asof is the natural fit for
# "accumulated xT" -- every event contributes at most once, and a
# single recovery can carry xT from multiple events within its 10s
# window. Grouping by period_id prevents cross-half pairings since
# progcarry_df `time` is per-period seconds.
#
# Short-chain bias: the original gated recoveries on `first_chain == 1`,
# which possession_chain_code.py only sets on chains of >= 2 events,
# silently dropping fast transitions. The event-type mask alone carries
# the "team won the ball" semantics.
#
# Double-counting fix: the original iterated recovery-side and, for
# each recovery, added every xT event in the next 10s -- so an event
# reachable from two recoveries had its xthreat counted twice.
# Event-side backward merge_asof attributes each event to exactly one
# recovery.
#
# NaN -> 0: xT sum; zero is a real, meaningful value.

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

_xt_mask = progcarry_df["xthreat"] > 0

_recoveries = (
    progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "period_id", "time"]]
    .rename(columns={"time": "recovery_time"})
    .sort_values("recovery_time", kind="mergesort")
    .reset_index(drop=True)
)

_xt_events = (
    progcarry_df.loc[
        _xt_mask, ["game_id", "team_id", "period_id", "time", "xthreat"]
    ]
    .rename(columns={"time": "event_time"})
    .sort_values("event_time", kind="mergesort")
    .reset_index(drop=True)
)

# For each xT event, find the most recent same-team recovery at or
# before the event in the same (game, period). Events with a qualifying
# recovery within 10s contribute their xthreat; events outside the
# window are dropped.
_paired = pd.merge_asof(
    _xt_events,
    _recoveries,
    left_on="event_time",
    right_on="recovery_time",
    by=["game_id", "team_id", "period_id"],
    direction="backward",
    allow_exact_matches=True,
)

_paired = _paired.loc[
    _paired["recovery_time"].notna()
    & ((_paired["event_time"] - _paired["recovery_time"]) <= WINDOW_SECONDS)
].copy()

variable_df24 = (
    _paired.groupby(["game_id", "team_id"], as_index=False)["xthreat"]
    .sum()
    .rename(columns={"xthreat": "xT_10s"})
)

variable_df24.head(100).to_csv("variable_df24.csv", index=True)

variable_df = variable_df.merge(
    variable_df24[["game_id", "team_id", "xT_10s"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["xT_10s"] = variable_df["xT_10s"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 25
#Ball possession %
"""Ball possession % refers to the percentage of time a team has control of the ball during a match.
It is a measure of how much a team is in possession compared to their opponent. This metric helps
in understanding a team's playing style, whether they focus on maintaining possession or prefer a
more direct approach."""

# Ball Possession %
#
# Per team per game, the percentage of match time the team had control
# of the ball. Read directly from the upstream `possession` feed rather
# than derived from progcarry_df -- Opta publishes possession % as a
# match-level stat with one row per game containing both sides.
#
# Upstream `possession` schema (one row per game):
#   game_id
#   home_team_id, home_team_possession_per
#   away_team_id, away_team_possession_per
#
# Reshape: stack the home and away halves into a long view with one
# row per (game_id, team_id, possession) so a single merge onto
# variable_df produces the own-team percentage. Opponent percentage
# comes from a self-merge on game_id with team_id != opponent_team_id,
# the same opposition-swap pattern used in variable_df6_code.py /
# variable_df16_code.py.
#
# Replaces the original iterrows + per-row filter + iloc[0] lookup,
# which was O(n * m) and silently picked the first row on duplicate
# game_ids.
#
# NaN -> 0: preserved from the original to avoid breaking downstream
# averaging. A missing game in the `possession` feed is a data-quality
# signal, not a "team had 0% possession" fact -- flagged here but not
# changed since the zero-fill is the historical contract.

_home = (
    possession[["game_id", "home_team_id", "home_team_possession_per"]]
    .rename(
        columns={
            "home_team_id": "team_id",
            "home_team_possession_per": "possession",
        }
    )
)
_away = (
    possession[["game_id", "away_team_id", "away_team_possession_per"]]
    .rename(
        columns={
            "away_team_id": "team_id",
            "away_team_possession_per": "possession",
        }
    )
)
_long = pd.concat([_home, _away], ignore_index=True)

# Opposition swap: attach each team's possession to the OTHER team's row.
_opposition = (
    _long.merge(
        _long.rename(
            columns={
                "team_id": "opponent_team_id",
                "possession": "opponent_possession",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opponent_possession"]]
)

variable_df25 = _long.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)[["game_id", "team_id", "possession", "opponent_possession"]]

variable_df25.head(100).to_csv("variable_df25.csv", index=True)

variable_df = variable_df.merge(
    variable_df25[["game_id", "team_id", "possession", "opponent_possession"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["possession"] = variable_df["possession"].fillna(0)
variable_df["opponent_possession"] = variable_df["opponent_possession"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 26
#Field tilt %
"""Field tilt % refers to the percentage of time the ball is in the attacking half of the field 
for a particular team compared to their opponent. This metric helps in understanding which team 
is more dominant in terms of territorial control and attacking pressure during a match."""

# Field Tilt %
#
# Per team per game, the share of "time in the attacking half" between
# the two sides. Follows the task definition ("% of time the ball is in
# the attacking half compared to opponent") rather than the alternative
# community definition (share of final-third passes, Caley/StatsBomb).
#
# Coordinate note: per Opta F24 Appendix 11 (reference/Opta-f24_
# appendices.md line 950), start_x / end_x are 0-100 percentages
# normalized L->R in the event team's attacking direction. x >= 50 is
# always the event team's attacking half.
#
# Attribution algorithm: iterate the *global* per-game, per-period
# event timeline (both teams together), sorted by (period_id, time,
# event_index). For each consecutive event pair, the gap
#   delta = next.time - current.time
# is attributed to the team of the *preceding* event, masked by whether
# that event's end_x landed in the attacking half. Sum the gaps per
# (game_id, team_id) to get time_in_attack. Each gap is attributed to
# exactly one team, so the two sides' totals add up to at most the game
# duration.
#
# Field tilt % = time_in_attack / (time_in_attack + opponent_time_in_attack)
# * 100, with opposition time pulled via the self-merge opposition-swap
# pattern used elsewhere in this pipeline.
#
# Fixes vs the original:
#   - Original iterated each team's events in isolation and added the
#     gap to the NEXT same-team event, attributing opponent possession
#     time to us whenever our events bracketed theirs.
#   - Original used `start_x >= 50 OR end_x >= 50`, double-counting any
#     event that merely crossed the halfway line. end_x >= 50 alone
#     matches "ball ended up in the attacking half."
#   - Original did not group by period_id, so the gap from the last
#     event of period 1 to the first event of period 2 produced a
#     negative delta (progcarry_df `time` is per-period seconds).
#   - Original had an O(n^2) iterrows loop; a single global sort +
#     groupby-diff replaces it.
#
# Div-by-zero guard: if total attacking-half time in a game is zero
# (no events in either half -- should not happen but defensively
# handled), field_tilt_% is NaN, then filled with 0 on the final merge.

HALFWAY = 50.0

_events = (
    progcarry_df[
        ["game_id", "team_id", "period_id", "time", "end_x", "event_index"]
    ]
    .sort_values(["game_id", "period_id", "time", "event_index"], kind="mergesort")
    .reset_index(drop=True)
)

# Time to the NEXT event within the same (game, period). The last event
# of a period has no successor -> NaN delta, which drops out of the sum.
_events["delta"] = (
    _events.groupby(["game_id", "period_id"])["time"].shift(-1) - _events["time"]
)

# Only count gaps where the current event ended in the team's
# attacking half.
_events["attack_delta"] = np.where(
    (_events["end_x"] >= HALFWAY) & _events["delta"].notna(),
    _events["delta"],
    0.0,
)

_team_stats = (
    _events.groupby(["game_id", "team_id"], as_index=False)["attack_delta"]
    .sum()
    .rename(columns={"attack_delta": "time_in_attack"})
)

# Opposition swap: attach each team's time_in_attack to the OTHER team.
_opposition = (
    _team_stats.merge(
        _team_stats.rename(
            columns={
                "team_id": "opponent_team_id",
                "time_in_attack": "opponent_time_in_attack",
            }
        ),
        on="game_id",
    )
    .query("team_id != opponent_team_id")
    [["game_id", "team_id", "opponent_time_in_attack"]]
)

variable_df26 = _team_stats.merge(
    _opposition,
    on=["game_id", "team_id"],
    how="left",
)

_total = variable_df26["time_in_attack"] + variable_df26["opponent_time_in_attack"]
variable_df26["field_tilt_%"] = np.where(
    _total > 0,
    variable_df26["time_in_attack"] / _total * 100.0,
    np.nan,
)

variable_df26 = variable_df26[["game_id", "team_id", "field_tilt_%"]]

variable_df26.head(100).to_csv("variable_df26.csv", index=True)

variable_df = variable_df.merge(
    variable_df26[["game_id", "team_id", "field_tilt_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["field_tilt_%"] = variable_df["field_tilt_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 27
#Long ball %
"""Long ball % refers to the percentage of passes that are long balls, which are defined as passes 
that travel a significant distance, typically bypassing the midfield to reach attackers quickly. 
This metric helps in understanding a team's playing style, indicating a preference for a more direct 
approach to advancing the ball up the field."""

# Long Ball %
#
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

variable_df27 = (
    _passes.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_passes=("is_long", "size"),
        long_balls=("is_long", "sum"),
    )
)
variable_df27["long_ball_%"] = np.where(
    variable_df27["total_passes"] > 0,
    variable_df27["long_balls"] / variable_df27["total_passes"] * 100.0,
    np.nan,
)

variable_df27 = variable_df27[["game_id", "team_id", "long_ball_%"]]

variable_df27.head(100).to_csv("variable_df27.csv", index=True)

variable_df = variable_df.merge(
    variable_df27[["game_id", "team_id", "long_ball_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["long_ball_%"] = variable_df["long_ball_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 28
#Pass tempo
"""Pass tempo refers to the speed and frequency at which a team or player moves the ball through passing. 
Higher pass tempo indicates quicker ball movement and more frequent passes, often used to disrupt the
opposition's defensive organization and create scoring opportunities."""

# Pass Tempo
#
# Per team per game, the team's OWN pass tempo:
#   pass_tempo = successful passes per minute of possession
#              = total_successful_passes / (total_possession_seconds / 60)
#
# Direct analog of variable_df5_code.py (Opposition Pass Tempo) minus
# the opposition swap.
#
# Reads from progcarry_chains_df -- the non-destructive valid-chain
# view built by possession_chain_code.py (possessionId != 0). Chain
# duration is derived as max(time) - min(time) per chain, consistent
# with the possession dataframe and pass tempo calculations.
#
# Formula correction vs the original `calculate_pass_tempo`: the
# original defined
#   pass_tempo = (total_distance / total_possession_time)
#              / (passes / possessions)
# which reduces to (meters * possessions) / (seconds * passes) --
# a unit-nonsense quantity that penalizes teams for completing many
# passes per possession, the opposite of the stated metric. The
# cleaner definition above matches the task wording ("speed and
# frequency at which a team moves the ball through passing") and
# matches the df5 rewrite.
#
# Short-chain filter: progcarry_chains_df already excludes
# possessionId == 0 rows (single-event chains, MIN_CHAIN_LEN = 2 in
# possession_chain_code.py). Consistent with the rest of the pipeline.
#
# NaN -> 0: tempo metric; a team with zero qualifying possessions is
# a degenerate case and 0 is the historical contract.

_pass_mask = (
    (progcarry_chains_df["type_id"] == 1)
    & (progcarry_chains_df["outcome"] == 1)
)
successful_passes = (
    progcarry_chains_df.loc[_pass_mask]
    .groupby(["game_id", "team_id"])
    .size()
    .rename("successful_passes")
)

# Derive possession seconds from chain durations (max - min time per chain),
# reusing the same approach as the possession dataframe built earlier.
_chain_time_28 = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations_28 = (
    progcarry_chains_df.assign(_time=_chain_time_28)
    .loc[progcarry_chains_df["possessionId"] != 0]
    .groupby(["game_id", "team_id", "possessionId"])["_time"]
    .agg(lambda t: t.max() - t.min())
)
possession_seconds = (
    _chain_durations_28
    .groupby(["game_id", "team_id"])
    .sum()
    .rename("possession_seconds")
)

variable_df28 = (
    pd.concat([successful_passes, possession_seconds], axis=1)
    .fillna(0)
    .reset_index()
)

variable_df28["pass_tempo"] = np.where(
    variable_df28["possession_seconds"] > 0,
    variable_df28["successful_passes"]
    / (variable_df28["possession_seconds"] / 60.0),
    np.nan,
)

variable_df28 = variable_df28[["game_id", "team_id", "pass_tempo"]]

variable_df28.head(100).to_csv("variable_df28.csv", index=True)

variable_df = variable_df.merge(
    variable_df28[["game_id", "team_id", "pass_tempo"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["pass_tempo"] = variable_df["pass_tempo"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 29
#Possessions to final third %
"""Possessions to final third % refers to the percentage of a team's possessions that successfully
progress into the final third of the pitch. This metric helps in understanding how effectively a
team can advance the ball into attacking areas and create potential scoring opportunities. It
indicates the team's ability to transition from midfield to the attacking third."""

# Possessions to Final Third %
#
# Per team per game, the percentage of the team's valid possessions
# that both started OUTSIDE the final third and later reached the
# final third. Measures the team's ability to progress the ball from
# deeper areas into attacking territory.
#
# Final third threshold: x >= 200/3 (~66.67). Per Opta F24 Appendix 11
# (reference/Opta-f24_appendices.md line 950), coordinates are 0-100
# percentages normalized L->R in the event team's attacking direction,
# so x >= 2/3 is always the attacking third.
#
# Reads from progcarry_chains_df -- the non-destructive valid-chain
# view built by possession_chain_code.py (possessionId != 0 means
# MIN_CHAIN_LEN >= 2). Single-event chains are excluded; they can't
# progress within themselves so the bias for this metric is small.
#
# Algorithm:
#   1. Per possessionId, get
#        chain_start_x  = start_x of the FIRST event (chronological
#                         order, already honored by the chain view's
#                         native sort on period_id / event_index)
#        chain_max_end_x = max(end_x) across all events in the chain
#   2. Denominator: possessions with chain_start_x < 2/3 (started
#      outside the final third).
#   3. Numerator: those same possessions where chain_max_end_x >= 2/3
#      (reached the final third at some point).
#
# Correction vs the original:
#   - The original detected "entered final third" via a single event
#     whose start_x < 2/3 AND end_x >= 2/3 -- a physical line-crossing.
#     A possession that enters incrementally (e.g. pass ending at
#     x=60, then carry ending at x=70) has no single straddling event
#     and would be missed. max(end_x) >= 2/3 captures the intent.
#   - The original used nested for-loops + iterrows. A single
#     groupby-agg replaces it.
#
# NaN -> 0: share metric; a team with zero qualifying possessions is
# a degenerate case and 0 is the historical contract.

FINAL_THIRD = 200.0 / 3.0

_chain_stats = (
    progcarry_chains_df.groupby(
        ["game_id", "team_id", "possessionId"], as_index=False
    ).agg(
        chain_start_x=("start_x", "first"),
        chain_max_end_x=("end_x", "max"),
    )
)

_chain_stats["started_outside"] = _chain_stats["chain_start_x"] < FINAL_THIRD
_chain_stats["reached"] = (
    _chain_stats["started_outside"]
    & (_chain_stats["chain_max_end_x"] >= FINAL_THIRD)
)

variable_df29 = (
    _chain_stats.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_valid_possessions=("started_outside", "sum"),
        final_third_entries=("reached", "sum"),
    )
)

variable_df29["final_third_entries_%"] = np.where(
    variable_df29["total_valid_possessions"] > 0,
    variable_df29["final_third_entries"]
    / variable_df29["total_valid_possessions"]
    * 100.0,
    np.nan,
)

variable_df29 = variable_df29[["game_id", "team_id", "final_third_entries_%"]]

variable_df29.head(100).to_csv("variable_df29.csv", index=True)

variable_df = variable_df.merge(
    variable_df29[["game_id", "team_id", "final_third_entries_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["final_third_entries_%"] = (
    variable_df["final_third_entries_%"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 30
#Final third to box %
"""Final third to box % refers to the percentage of possessions or passes that successfully move from
the final third of the pitch into the opponent's penalty box. This metric helps in understanding
how effectively a team can penetrate the opponent's defensive setup and create potential scoring
opportunities in the most dangerous area of the field."""

# Final Third to Box %
#
# Per team per game, among the team's valid possessions that reached
# the final third, the percentage that also reached the penalty box.
# Measures how effectively a side converts final-third presence into
# box entries.
#
# Zones (Opta F24 Appendix 11, reference/Opta-f24_appendices.md):
#   final third: end_x >= 200/3 (~66.67)   -- line 950
#   penalty box: end_x >= 83 and 21.1 <= end_y <= 78.9  -- line 957
# Box is a strict subset of the final third, so any chain reaching
# the box necessarily also reached the final third.
#
# End-coordinate detection: a carry or pass that DELIVERS the ball
# into a zone has end_x/end_y in the zone and start_x/start_y
# outside -- so zone entry is an end-coordinate test, not a start
# test. Same convention as variable_df14/15/21/22_code.py. The
# original checked start_x/start_y, which missed every delivering
# event (the event whose end_x first crossed x=83 wouldn't have
# start_x in the box until the NEXT event, and "next event" may not
# be in the same chain).
#
# Short-chain bias: progcarry_chains_df excludes possessionId == 0
# (MIN_CHAIN_LEN = 2 in possession_chain_code.py). Consistent with
# the rest of the pipeline.
#
# Simplification vs the original:
#   - Original required a "final-third but NOT in box" event to flip
#     `has_final_third` true, creating a detection gap for chains
#     that jump directly from outside the final third into the box.
#     Box is a subset of final third, so `reached_final_third` is
#     simply "any event ends in final third."
#   - Original walked events in temporal order and required the
#     final-third event to precede the box entry. For real football
#     geometry any chain reaching the box must have entered the
#     final third first, so the temporal-order test is redundant.
#   - Original used nested for-loops + iterrows. Vectorized groupby-
#     any replaces it.
#
# NaN -> 0: share metric; a team with zero final-third possessions
# is a degenerate case and 0 is the historical contract.

FINAL_THIRD = 200.0 / 3.0
BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

_ends_in_final_third = progcarry_chains_df["end_x"] >= FINAL_THIRD
_ends_in_box = (
    (progcarry_chains_df["end_x"] >= BOX_X)
    & (progcarry_chains_df["end_y"] >= BOX_Y_MIN)
    & (progcarry_chains_df["end_y"] <= BOX_Y_MAX)
)

_flags = pd.DataFrame(
    {
        "game_id": progcarry_chains_df["game_id"].values,
        "team_id": progcarry_chains_df["team_id"].values,
        "possessionId": progcarry_chains_df["possessionId"].values,
        "ends_in_final_third": _ends_in_final_third.values,
        "ends_in_box": _ends_in_box.values,
    }
)

_chain_stats = (
    _flags.groupby(
        ["game_id", "team_id", "possessionId"], as_index=False
    ).agg(
        reached_final_third=("ends_in_final_third", "any"),
        reached_box=("ends_in_box", "any"),
    )
)

variable_df30 = (
    _chain_stats.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        final_third_possessions=("reached_final_third", "sum"),
        box_entries=("reached_box", "sum"),
    )
)

variable_df30["final_third_to_box_entries_%"] = np.where(
    variable_df30["final_third_possessions"] > 0,
    variable_df30["box_entries"]
    / variable_df30["final_third_possessions"]
    * 100.0,
    np.nan,
)

variable_df30 = variable_df30[
    ["game_id", "team_id", "final_third_to_box_entries_%"]
]

variable_df30.head(100).to_csv("variable_df30.csv", index=True)

variable_df = variable_df.merge(
    variable_df30[["game_id", "team_id", "final_third_to_box_entries_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["final_third_to_box_entries_%"] = (
    variable_df["final_third_to_box_entries_%"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 31
#xT
"""xT stands for "expected threat," which measures how much a pass or carry contributes to a team's
chance of scoring. It provides a better assessment of a player's contribution by accounting for
where an action takes place on the pitch, with actions closer to the opponent's goal having higher
expected threat. This metric helps in understanding the potential impact and danger created by a
player's actions in advancing the ball and creating scoring opportunities."""

# xT (Expected Threat)
#
# Per team per game, the total accumulated xT from all events. xT
# measures how much each action (pass, carry, dribble) contributes to
# the team's chance of scoring, weighted by pitch location.
#
# The `xthreat` column lives on every progcarry_df row. Summing it per
# (game_id, team_id) gives the team's total threat generation.
#
# NaN -> 0: xT sum; zero is a real, meaningful value.

variable_df31 = (
    progcarry_df.groupby(["game_id", "team_id"], as_index=False)["xthreat"]
    .sum()
    .rename(columns={"xthreat": "xT"})
)

variable_df31.head(100).to_csv("variable_df31.csv", index=True)

variable_df = variable_df.merge(
    variable_df31[["game_id", "team_id", "xT"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["xT"] = variable_df["xT"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 32
#Penalty area touches
"""Penalty area touches refer to the number of times a team makes contact with the ball inside the
opponent's penalty area. This metric helps in understanding a team's activity in
the most dangerous attacking zone on the pitch. It is an indicator of a team's ability to get into
goal-scoring positions and create opportunities."""

# Penalty Area Touches
#
# Per team per game, the number of times the team makes contact with
# the ball inside the opponent's penalty area.
#
# Touch location = start_x / start_y (where the player contacts the
# ball). End coordinates mark where the ball travels AFTER the touch,
# so they are irrelevant for "touch IN the box."
#
# Penalty box (Opta F24 Appendix 11, reference/Opta-f24_appendices.md
# line 957): x >= 83, 21.1 <= y <= 78.9.
#
# NaN -> 0: count metric; zero is a real, meaningful value.

_touch_mask = progcarry_df["touch"] == True

_in_box = (
    (progcarry_df["start_x"] >= 83.0)
    & (progcarry_df["start_y"] >= 21.1)
    & (progcarry_df["start_y"] <= 78.9)
)

variable_df32 = (
    progcarry_df.loc[_touch_mask & _in_box]
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "penalty_area_touches"})
)

variable_df32.head(100).to_csv("variable_df32.csv", index=True)

variable_df = variable_df.merge(
    variable_df32[["game_id", "team_id", "penalty_area_touches"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["penalty_area_touches"] = variable_df["penalty_area_touches"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 33
#Box entries to shot %
"""Box entries to shot % refers to the percentage of times that an entry into the opponent's penalty
area (box) results in a shot. This metric helps in understanding the efficiency and effectiveness of
a team's ability to convert box entries into shooting opportunities. It indicates how
often penetrating the box leads to an attempt on goal."""

# Box Entries to Shot %
#
# Per team per game, the percentage of possession chains that enter the
# opponent's penalty box and also produce a shot. Measures how
# efficiently a team converts box entries into shooting opportunities.
#
# Box entry detection: end_x / end_y in the penalty box — the event
# that DELIVERS the ball into the box, not the one that starts there.
# Same convention as variable_df30_code.py.
#
# Shot detection: shot == True column on progcarry_chains_df.
#
# Penalty box (Opta F24 Appendix 11, reference/Opta-f24_appendices.md
# line 957): x >= 83, 21.1 <= y <= 78.9.
#
# Short-chain bias: progcarry_chains_df excludes possessionId == 0
# (MIN_CHAIN_LEN = 2 in possession_chain_code.py). Consistent with
# the rest of the pipeline.
#
# NaN -> 0: share metric; zero is the historical contract.

BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

_ends_in_box = (
    (progcarry_chains_df["end_x"] >= BOX_X)
    & (progcarry_chains_df["end_y"] >= BOX_Y_MIN)
    & (progcarry_chains_df["end_y"] <= BOX_Y_MAX)
)

_is_shot = progcarry_chains_df["shot"] == True

_chain_flags = (
    pd.DataFrame(
        {
            "game_id": progcarry_chains_df["game_id"].values,
            "team_id": progcarry_chains_df["team_id"].values,
            "possessionId": progcarry_chains_df["possessionId"].values,
            "ends_in_box": _ends_in_box.values,
            "is_shot": _is_shot.values,
        }
    )
    .groupby(["game_id", "team_id", "possessionId"], as_index=False)
    .agg(
        reached_box=("ends_in_box", "any"),
        has_shot=("is_shot", "any"),
    )
)

_box_chains = _chain_flags.loc[_chain_flags["reached_box"]]

variable_df33 = (
    _box_chains.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        box_entries=("reached_box", "sum"),
        entries_with_shot=("has_shot", "sum"),
    )
)

variable_df33["box_entries_to_shot_%"] = np.where(
    variable_df33["box_entries"] > 0,
    variable_df33["entries_with_shot"] / variable_df33["box_entries"] * 100.0,
    np.nan,
)

variable_df33 = variable_df33[["game_id", "team_id", "box_entries_to_shot_%"]]

variable_df33.head(100).to_csv("variable_df33.csv", index=True)

variable_df = variable_df.merge(
    variable_df33[["game_id", "team_id", "box_entries_to_shot_%"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["box_entries_to_shot_%"] = (
    variable_df["box_entries_to_shot_%"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 34
#np Shots
"""np Shots stands for non-penalty shots. It refers to the total number of shots a team takes,
excluding penalty kicks. This metric is used to evaluate a player's shooting performance and 
goalscoring opportunities from open play and set pieces other than penalties."""

# Non-Penalty Shots (np Shots)
#
# Per team per game, the total number of shots excluding penalties.
#
# Shot detection: shot == True column on progcarry_df.
#
# Penalty filter: qualifier 9 (reference/Opta-f24_appendices.md
# line 213), detected via the has_qualifier helper.
#
# NaN -> 0: count metric; zero is a real, meaningful value.

_is_penalty = progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 9))

_np_shot_mask = (progcarry_df["shot"] == True) & ~_is_penalty

variable_df34 = (
    progcarry_df.loc[_np_shot_mask]
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "np_shots"})
)

variable_df34.head(100).to_csv("variable_df34.csv", index=True)

variable_df = variable_df.merge(
    variable_df34[["game_id", "team_id", "np_shots"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["np_shots"] = variable_df["np_shots"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 35
#High opportunity shots
"""High opportunity shots refer to shots taken from positions or situations with a high likelihood of scoring,
typically characterized by higher expected goals (xG) values. These shots are usually taken from
closer to the goal, with fewer defenders in the way, and from more central positions."""

# High Opportunity Shots (Big Chances)
#
# Per team per game, the number of non-penalty shots flagged as "Big
# Chance" by Opta analysts (qualifier 214, reference/Opta-f24_appendices.md
# line 234). A big chance is a clear-cut opportunity to score, e.g.
# one-on-one situations.
#
# Shot detection: shot == True on progcarry_df.
# Penalty exclusion: qualifier 9 (line 213).
# Big chance detection: qualifier 214 (presence-only).
#
# Qualifier detection via has_qualifier helper.
#
# NaN -> 0: count metric; zero is a real, meaningful value.

_is_penalty = progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 9))
_is_big_chance = progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 214))

_mask = (progcarry_df["shot"] == True) & ~_is_penalty & _is_big_chance

variable_df35 = (
    progcarry_df.loc[_mask]
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "high_opportunity_shots"})
)

variable_df35.head(100).to_csv("variable_df35.csv", index=True)

variable_df = variable_df.merge(
    variable_df35[["game_id", "team_id", "high_opportunity_shots"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["high_opportunity_shots"] = (
    variable_df["high_opportunity_shots"].fillna(0)
)

###############################################################################
###############################################################################
# Variáveis
# 36
#np xG
"""np XG stands for non-penalty expected goals. It quantifies the quality of scoring chances 
a team has, excluding penalty kicks. This metric helps in understanding how many goals a player
or team is expected to score based on the quality of their non-penalty shot opportunities."""

# Non-Penalty Expected Goals (np xG)
#
# Per team per game, the sum of xG values from all shots excluding
# penalties.  Quantifies the quality of scoring chances a team creates
# from open play and non-penalty set pieces.
#
# Shot detection: type_id in {13, 14, 15, 16}
#   (reference/Opta-f24_appendices.md lines 55-58).
# Penalty exclusion: qualifier 9 — presence-only
#   (reference/Opta-f24_appendices.md line 213).
#
# xG values come from xg_df, merged into df beforehand.
# Qualifier detection via has_qualifier helper.
#
# NaN -> 0: teams with no non-penalty shots get 0 np_xg.

if "xG" not in progcarry_df.columns:
    progcarry_df = progcarry_df.merge(
        xg_df[["game_id", "event_id", "xG"]],
        on=["game_id", "event_id"],
        how="left",
    )
    progcarry_df["xG"] = progcarry_df["xG"].fillna(0.0)
    if (progcarry_df["xG"] != 0).sum() == 0:
        raise RuntimeError("xG merge produced all-zero xG column — event_id key space drift between xg_df and progcarry_df")

SHOT_TYPES = [13, 14, 15, 16]

_shots = progcarry_df[progcarry_df["type_id"].isin(SHOT_TYPES)].copy()

_is_penalty = _shots["qualifiers"].apply(lambda q: has_qualifier(q, 9))

_np_shots = _shots[~_is_penalty]

variable_df36 = (
    _np_shots
    .groupby(["game_id", "team_id"], as_index=False)["xG"]
    .sum()
    .rename(columns={"xG": "np_xg"})
)

variable_df36.head(100).to_csv("variable_df36.csv", index=True)

variable_df = variable_df.merge(
    variable_df36[["game_id", "team_id", "np_xg"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["np_xg"] = variable_df["np_xg"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 37
#np Goals
"""np Goals stands for non-penalty goals. It refers to the total number of goals a team scores,
excluding penalty kicks. This metric is used to evaluate a team's goal-scoring performance from
open play and set pieces other than penalties."""

# Non-Penalty Goals (np Goals)
#
# Per team per game, the count of goals excluding penalties.
# Evaluates goal-scoring performance from open play and
# non-penalty set pieces.
#
# Goal detection: type_id == 16
#   (reference/Opta-f24_appendices.md line 58).
# Penalty exclusion: qualifier 9 — presence-only
#   (reference/Opta-f24_appendices.md line 213).
#
# Qualifier detection via has_qualifier helper.
#
# NaN -> 0: count metric; zero is a real, meaningful value.

_goals = progcarry_df[progcarry_df["type_id"] == 16].copy()

_is_penalty = _goals["qualifiers"].apply(lambda q: has_qualifier(q, 9))

_np_goals = _goals[~_is_penalty]

variable_df37 = (
    _np_goals
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "np_goals"})
)

variable_df37.head(100).to_csv("variable_df37.csv", index=True)

variable_df = variable_df.merge(
    variable_df37[["game_id", "team_id", "np_goals"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["np_goals"] = variable_df["np_goals"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 38
#xG per shot
"""xG per shot is defined as the accumulated non-penalty expected goals (xG) divided by the number
of shots. This metric helps in understanding the average quality of each shot a team takes,
indicating how likely each shot is to result in a goal based on its location and other factors. It
provides insight into the efficiency and danger of a team's shooting opportunities."""

# xG per Shot
#
# Per team per game, the accumulated non-penalty xG divided by the
# number of non-penalty shots.  Measures the average quality of each
# shot a team takes from open play and non-penalty set pieces.
#
# Shot detection: type_id in {13, 14, 15, 16}
#   (reference/Opta-f24_appendices.md lines 55-58).
# Penalty exclusion: qualifier 9 — presence-only
#   (reference/Opta-f24_appendices.md line 213).
#
# xG values already merged into df (see variable_df36_code.py).
# Qualifier detection via has_qualifier helper.
#
# NaN -> 0: teams with no non-penalty shots get 0 xg_per_shot.

if "xG" not in progcarry_df.columns:
    progcarry_df = progcarry_df.merge(
        xg_df[["game_id", "event_id", "xG"]],
        on=["game_id", "event_id"],
        how="left",
    )
    progcarry_df["xG"] = progcarry_df["xG"].fillna(0.0)
    if (progcarry_df["xG"] != 0).sum() == 0:
        raise RuntimeError("xG merge produced all-zero xG column — event_id key space drift between xg_df and progcarry_df")

SHOT_TYPES = [13, 14, 15, 16]

_shots = progcarry_df[progcarry_df["type_id"].isin(SHOT_TYPES)].copy()

_is_penalty = _shots["qualifiers"].apply(lambda q: has_qualifier(q, 9))

_np_shots = _shots[~_is_penalty]

_agg = _np_shots.groupby(["game_id", "team_id"], as_index=False).agg(
    total_np_xg=("xG", "sum"),
    np_shot_count=("xG", "size"),
)

_agg["xg_per_shot"] = _agg["total_np_xg"] / _agg["np_shot_count"]

variable_df38 = _agg[["game_id", "team_id", "xg_per_shot"]]

variable_df38.head(100).to_csv("variable_df38.csv", index=True)

variable_df = variable_df.merge(
    variable_df38[["game_id", "team_id", "xg_per_shot"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["xg_per_shot"] = variable_df["xg_per_shot"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 39
#Ball-in-play minutes
"""Ball-in-play minutes refer to the total amount of time during a match when the ball is actively in
play. This excludes any stoppages such as injuries, substitutions, fouls, and other interruptions. It
measures the actual duration of active gameplay."""

# Ball-in-Play Minutes
#
# Per team per game, the total time the ball was actively in play
# during that team's possession chains, converted to minutes.
# Excludes stoppages (injuries, substitutions, fouls, etc.).
#
# Chain duration is derived from progcarry_chains_df as max(time) -
# min(time) per chain, consistent with the possession dataframe and
# pass tempo calculations earlier in the pipeline.
#
# NaN -> 0: teams with no recorded possession get 0 minutes.

_chain_time_39 = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations_39 = (
    progcarry_chains_df.assign(_time=_chain_time_39)
    .loc[progcarry_chains_df["possessionId"] != 0]
    .groupby(["game_id", "team_id", "possessionId"])["_time"]
    .agg(lambda t: t.max() - t.min())
    .reset_index(name="chain_duration")
)

variable_df39 = (
    _chain_durations_39.loc[_chain_durations_39["chain_duration"] > 0]
    .groupby(["game_id", "team_id"], as_index=False)["chain_duration"]
    .sum()
)

variable_df39["ball_in_play"] = variable_df39["chain_duration"] / 60
variable_df39 = variable_df39[["game_id", "team_id", "ball_in_play"]]

variable_df39.head(100).to_csv("variable_df39.csv", index=True)

variable_df = variable_df.merge(
    variable_df39[["game_id", "team_id", "ball_in_play"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["ball_in_play"] = variable_df["ball_in_play"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 40
#Field tilt %
"""Field tilt % refers to the percentage of time the ball is in the attacking half of the field 
for a particular team compared to their opponent. This metric helps in understanding which team 
is more dominant in terms of territorial control and attacking pressure during a match."""

#Calculated in variable_df26

###############################################################################
###############################################################################
# Variáveis
# 44
#xG
"""xG stands for expected goals. It quantifies the quality of scoring chances by calculating the
likelihood that a given shot will result in a goal based on various factors such as shot location,
shot type, and the position of defenders and the goalkeeper. This metric helps in understanding a
team's or player's attacking efficiency and can be a more reliable indicator of future performance
than traditional metrics like shots or goals."""

# Total Expected Goals (xG)
#
# Per team per game, the sum of xG values from all shots (including
# penalties).  Quantifies the overall quality of scoring chances a
# team creates, regardless of shot origin.
#
# Shot detection: type_id in {13, 14, 15, 16}
#   (reference/Opta-f24_appendices.md lines 55-58).
#
# xG values come from xg_df, merged into df beforehand.
#
# NaN -> 0: teams with no shots get 0 total_xg.

if "xG" not in progcarry_df.columns:
    progcarry_df = progcarry_df.merge(
        xg_df[["game_id", "event_id", "xG"]],
        on=["game_id", "event_id"],
        how="left",
    )
    progcarry_df["xG"] = progcarry_df["xG"].fillna(0.0)
    if (progcarry_df["xG"] != 0).sum() == 0:
        raise RuntimeError("xG merge produced all-zero xG column — event_id key space drift between xg_df and progcarry_df")

SHOT_TYPES = [13, 14, 15, 16]

_shots = progcarry_df[progcarry_df["type_id"].isin(SHOT_TYPES)]

variable_df44 = (
    _shots
    .groupby(["game_id", "team_id"], as_index=False)["xG"]
    .sum()
    .rename(columns={"xG": "total_xg"})
)

variable_df44.head(100).to_csv("variable_df44.csv", index=True)

variable_df = variable_df.merge(
    variable_df44[["game_id", "team_id", "total_xg"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["total_xg"] = variable_df["total_xg"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 45
#Goal difference
"""Goal difference is the numerical difference between the number of goals a team has scored and
the number of goals it has conceded. It is calculated by subtracting the total goals conceded from
the total goals scored. This metric is often used in league standings to rank teams that have the
same number of points."""

# Goal Difference
#
# Per team per game, goals scored minus goals conceded.
# Uses the boolean "goal" column which flags goal events.
# Goals conceded = goals scored by the opponent in the same game.
#
# NaN -> 0: teams with no goal events on either side get 0.

# Start from all (game_id, team_id) pairs so teams with 0 goals are included.
_all_teams = progcarry_df[["game_id", "team_id"]].drop_duplicates()

_goals_per_team = (
    progcarry_df[progcarry_df["goal"] == True]
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "goals_scored"})
)

# Left merge ensures teams with 0 goals get goals_scored = 0.
_merged = _all_teams.merge(_goals_per_team, on=["game_id", "team_id"], how="left")
_merged["goals_scored"] = _merged["goals_scored"].fillna(0).astype(int)

_goals_per_game = (
    _merged
    .groupby("game_id", as_index=False)["goals_scored"]
    .sum()
    .rename(columns={"goals_scored": "game_total_goals"})
)

_merged = _merged.merge(_goals_per_game, on="game_id", how="left")
_merged["goals_conceded"] = _merged["game_total_goals"] - _merged["goals_scored"]
_merged["goal_difference"] = _merged["goals_scored"] - _merged["goals_conceded"]

variable_df45 = _merged[["game_id", "team_id", "goal_difference"]]

variable_df45.head(100).to_csv("variable_df45.csv", index=True)

variable_df = variable_df.merge(
    variable_df45[["game_id", "team_id", "goal_difference"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["goal_difference"] = variable_df["goal_difference"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 46
#Opp. Goals
"""Opp. Goals refers to the total number of goals scored by the opposing team in a match. This metric
helps in understanding the defensive performance of a team by indicating how many goals they
have conceded to their opponents. It is a key factor in evaluating a team's ability to prevent the
opposition from scoring."""

# Opposition Goals (Goals Conceded)
#
# Per team per game, the number of goals scored by the opposing team.
# Measures defensive performance — how many goals a team concedes.
#
# Computed as: total goals in the game minus the team's own goals.
# Uses the boolean "goal" column which flags goal events.
#
# NaN -> 0: teams in goalless draws get 0.

# Start from all (game_id, team_id) pairs so teams with 0 goals are included.
_all_teams_46 = progcarry_df[["game_id", "team_id"]].drop_duplicates()

_goals_per_team = (
    progcarry_df[progcarry_df["goal"] == True]
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "goals_scored"})
)

_merged = _all_teams_46.merge(_goals_per_team, on=["game_id", "team_id"], how="left")
_merged["goals_scored"] = _merged["goals_scored"].fillna(0).astype(int)

_goals_per_game = (
    _merged
    .groupby("game_id", as_index=False)["goals_scored"]
    .sum()
    .rename(columns={"goals_scored": "game_total_goals"})
)

_merged = _merged.merge(_goals_per_game, on="game_id", how="left")
_merged["goals_conceded"] = _merged["game_total_goals"] - _merged["goals_scored"]

variable_df46 = _merged[["game_id", "team_id", "goals_conceded"]]

variable_df46.head(100).to_csv("variable_df46.csv", index=True)

variable_df = variable_df.merge(
    variable_df46[["game_id", "team_id", "goals_conceded"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["goals_conceded"] = variable_df["goals_conceded"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 47
#Goals
"""Goals refer to the total number of times a team or player successfully scores by getting the ball
into the opponent's net during a match. This metric is used to measure the effectiveness of a team's
or player's attacking performance. Goals are a fundamental aspect of football, as they determine
the outcome of matches and contribute to the team's overall success."""

# Goals Scored
#
# Per team per game, the total number of goals scored.
# Uses the boolean "goal" column which flags goal events.
#
# NaN -> 0: teams that did not score get 0.

variable_df47 = (
    progcarry_df[progcarry_df["goal"] == True]
    .groupby(["game_id", "team_id"], as_index=False)
    .size()
    .rename(columns={"size": "goals_scored"})
)

variable_df47.head(100).to_csv("variable_df47.csv", index=True)

variable_df = variable_df.merge(
    variable_df47[["game_id", "team_id", "goals_scored"]],
    on=["game_id", "team_id"],
    how="left",
)
variable_df["goals_scored"] = variable_df["goals_scored"].fillna(0)


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
############################################################################################

# Copying
variable_df.to_csv("variable_df_new.csv")
variable_df_new = variable_df.copy()

# Add place 
# Assign "home" or "away" to the "place" column in oponnent_analysis
def determine_place(row):
    game_id = row['game_id']
    clube = row['team_name']
    
    if (df_schedule.loc[df_schedule['game_id'] == game_id, 'home_team'].values == clube).any():
        return "Casa"
    elif (df_schedule.loc[df_schedule['game_id'] == game_id, 'away_team'].values == clube).any():
        return "Fora"
    return None  # If no match found

variable_df_new['place'] = variable_df_new.apply(determine_place, axis=1)

# Reorder "opponent_possession" to be the third column
columns = variable_df_new.columns.tolist()
columns.remove("place")  # Remove it from the original spot
columns.insert(5, "place")  # Insert it as the third column
variable_df_new = variable_df_new[columns]


# Reorder "opponent_possession" to be the third column
columns = variable_df_new.columns.tolist()
columns.remove("opponent_possession")  # Remove it from the original spot
columns.insert(5, "opponent_possession")  # Insert it as the third column
variable_df_new = variable_df_new[columns]

# Reordering "team_possession", "opponent_possession" 
columns = variable_df_new.columns.tolist()
columns.remove("possession")  # Remove it from the original spot
columns.insert(5, "possession")  # Insert it as the third column
variable_df_new = variable_df_new[columns]

############################################################################################
############################################################################################

# Adjusting for Possession
# List of variables to be adjusted for opponent possession
# List of variables to be adjusted for team possession
# Drop the xg_shot_y column

#variable_df2.to_csv = ("variable_df2.csv")

columns_opp_pos = [
    "defensive_intensity", "recoveries"
    ]

columns_team_pos = [
    "high_turnovers"]



############################################################################################
############################################################################################
# Adjusting variable_df_adj columns
# Normalizing by opposition possession:
def normalize_opponent_possession_stats(df, columns_to_normalize):
    """
    Normalize defensive statistics by opponent possession and scale by 50
    
    Parameters:
    df: DataFrame with defensive statistics
    columns_to_normalize: List of columns to normalize
    
    Returns:
    DataFrame with normalized statistics
    """
    # Create copy to avoid modifying original
    df_normalized = df.copy()
    
    try:
        # First, check if all columns exist in the dataframe
        existing_columns = [col for col in columns_to_normalize if col in df_normalized.columns]
        
        if len(existing_columns) != len(columns_to_normalize):
            missing_columns = set(columns_to_normalize) - set(existing_columns)
            print(f"Warning: Some columns do not exist in the dataframe: {missing_columns}")
        
        if len(existing_columns) == 0:
            print("No valid columns to normalize. Returning original dataframe.")
            return df_normalized
        
        # Avoid division by zero by replacing 0s with NaN
        opponent_possession = df_normalized["opponent_possession"].replace(0, np.nan)
        
        # Apply normalization column by column to avoid alignment issues
        for col in existing_columns:
            df_normalized[col] = (df_normalized[col] / opponent_possession) * 50
        
        # Replace any resulting infinite values with NaN
        df_normalized[existing_columns] = df_normalized[existing_columns].replace([np.inf, -np.inf], np.nan)
        
        return df_normalized
        
    except Exception as e:
        print(f"Error during normalization: {str(e)}")
        return df
    
# Normalizing by team possession:

def normalize_team_possession_stats(df, columns_to_normalize):
    """
    Normalize offensive statistics by team possession and scale by 50
    
    Parameters:
    df: DataFrame with team statistics
    columns_to_normalize: List of columns to normalize
    
    Returns:
    DataFrame with normalized statistics
    """
    # Create copy to avoid modifying original
    df_normalized = df.copy()
    
    try:
        # Avoid division by zero by replacing 0s with NaN
        team_possession = df_normalized["possession"].replace(0, np.nan)
        
        # Apply transformation
        df_normalized[columns_to_normalize] = (
            df_normalized[columns_to_normalize]
            .divide(team_possession, axis=0)
            .multiply(50)
        )
        
        # Replace any resulting infinite values with NaN
        df_normalized[columns_to_normalize] = df_normalized[columns_to_normalize].replace([np.inf, -np.inf], np.nan)
        
        return df_normalized
        
    except Exception as e:
        print(f"Error during normalization: {str(e)}")
        return df


# Transform the data
variable_df_new = normalize_opponent_possession_stats(variable_df_new, columns_opp_pos)
variable_df_new = normalize_team_possession_stats(variable_df_new, columns_team_pos)

###########################################################################
###########################################################################
# Adding season and league columns

# Add "Temporada" column with the value 2025 as the first column in the dataframe
variable_df_new.insert(0, "Temporada", 2025)

# Add "Temporada" column with the value 2025 as the first column in the dataframe
#variable_df_new.insert(0, "Liga", "BRA1")

###########################################################################
###########################################################################

# Building round column
# Numbering rounds
# 1. Load the rounds reference file and keep only the keys we need
rodada_df = pd.read_excel('rodada_2025.xlsx')[['game_id', 'round']]

# 2. Merge the 'round' column into variable_df_new based on 'game_id'
variable_df_new = variable_df_new.merge(rodada_df, on='game_id', how='left')

# 3. Sort the dataframe by date and game_id
variable_df_new = variable_df_new.sort_values(['date', 'game_id'], ascending=[True, True]).reset_index(drop=True)

# 4. Relocate the 'round' column to column position 1 (i.e., the second column)
cols = list(variable_df_new.columns)
cols.remove('round')      # Remove 'round' from its current position
cols.insert(1, 'round')   # Insert 'round' at index 1
variable_df_new = variable_df_new[cols]

variable_df_new.to_csv("variable_df_new.csv")
variable_df_new.to_csv("performance_metrics.csv")
###########################################################################
###########################################################################

# Rerunning columns from Master Code
# Calculating z-scores
# Create a new dataframe for z-scores
variable_df_z_team = pd.DataFrame()

###########################################################################
###########################################################################

#Bulding team_id game analysis (same club analysis)

# Group by 'função' and apply z-score transformation independently
for team_id, group in variable_df_new.groupby("team_id"):
    # Repeat columns [0:15]
    base_columns = group.iloc[:, :10].copy()
    # Apply z-score transformation to columns [11:] and rename with '_z' suffix
    zscore_columns = group.iloc[:, 10:].apply(zscore)
    zscore_columns.rename(columns=lambda col: f"{col}_z", inplace=True)
    # Combine the repeated columns with the z-score transformed columns
    função_z = pd.concat([base_columns, zscore_columns], axis=1)
    # Append to the final dataframe
    variable_df_z_team = pd.concat([variable_df_z_team, função_z], axis=0)

# Reset index after concatenation
variable_df_z_team.reset_index(drop=True, inplace=True)

###########################################################################
###########################################################################

# Inverting the sign of inverted metrics
variable_df_z_team["PPDA_z"] = -1*variable_df_z_team["PPDA_z"]
variable_df_z_team["opposition_pass_tempo_z"] = -1*variable_df_z_team["opposition_pass_tempo_z"]
variable_df_z_team["opposition_progression_percentage_z"] = -1*variable_df_z_team["opposition_progression_percentage_z"]
variable_df_z_team["opp_final_third_to_box_%_z"] = -1*variable_df_z_team["opp_final_third_to_box_%_z"]
variable_df_z_team["Opposition_xT_z"] = -1*variable_df_z_team["Opposition_xT_z"]
variable_df_z_team["high_turnovers_z"] = -1*variable_df_z_team["high_turnovers_z"]
variable_df_z_team["avg_time_to_defensive_action_z"] = -1*variable_df_z_team["avg_time_to_defensive_action_z"]
variable_df_z_team["avg_recovery_time_z"] = -1*variable_df_z_team["avg_recovery_time_z"]
variable_df_z_team["opposition_final_third_entries_10s_z"] = -1*variable_df_z_team["opposition_final_third_entries_10s_z"]
variable_df_z_team["opposition_box_entries_10s_z"] = -1*variable_df_z_team["opposition_box_entries_10s_z"]
variable_df_z_team["opposition_xG_10s_z"] = -1*variable_df_z_team["opposition_xG_10s_z"]
variable_df_z_team["goals_conceded_z"] = -1*variable_df_z_team["goals_conceded_z"]

###########################################################################
###########################################################################

# Creating qualities columns
# Define the columns to average for each metric
defence_metrics = ["PPDA_z", "defensive_intensity_z", "defensive_duels_won_%_z",
                   "defensive_height_z", "opposition_pass_tempo_z",	
                   "opposition_progression_percentage_z", "opp_final_third_to_box_%_z",	
                   "Opposition_xT_z"]

defensive_transition_metrics = ["high_turnovers_z", "turnover_line_height_z", "recoveries_within_5s_%_z", 
                                "avg_time_to_defensive_action_z", "opposition_final_third_entries_10s_z", 
                                "opposition_box_entries_10s_z", "opposition_xG_10s_z"]

attacking_transition_metrics = ["recoveries_z",	"recovery_height_z", "retained_possessions_5s_z",
                                "retained_possessions_5s_%_z", "final_third_entries_10s_z",
                                "box_entries_10s_z", "xG_10s_z", "xT_10s_z"]

attacking_metrics = ["field_tilt_%_z",	"long_ball_%_z", "pass_tempo_z", 
                  "final_third_entries_%_z", "final_third_to_box_entries_%_z", "xT_z"]

chance_creation_metrics = ["penalty_area_touches_z", "box_entries_to_shot_%_z", "np_shots_z", 
                           "high_opportunity_shots_z", "np_xg_z", "np_goals_z", "xg_per_shot_z"]

# Compute the arithmetic mean for each metric and assign to the respective column
variable_df_z_team["defence_z"] = variable_df_z_team[defence_metrics].mean(axis=1)
variable_df_z_team["defensive_transition_z"] = variable_df_z_team[defensive_transition_metrics].mean(axis=1)
variable_df_z_team["attacking_transition_z"] = variable_df_z_team[attacking_transition_metrics].mean(axis=1)
variable_df_z_team["attacking_z"] = variable_df_z_team[attacking_metrics].mean(axis=1)
variable_df_z_team["chance_creation_z"] = variable_df_z_team[chance_creation_metrics].mean(axis=1)

# Get a list of the current columns
cols = list(variable_df_z_team.columns)

# List of columns to be relocated
cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                  "attacking_z", "chance_creation_z"]#, "outcome_z"]

# Remove these columns from the list
for col in cols_to_remove:
    cols.remove(col)

# Insert the columns in the desired order at index 9, adjusting the index as we go
for i, col in enumerate(cols_to_remove):
    cols.insert(10 + i, col)

# Reorder the dataframe columns accordingly
variable_df_z_team = variable_df_z_team[cols]

# Renaming columns
columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                     "possession_z", "opponent_possession_z", "defence_z", "defensive_transition_z",
                     "attacking_transition_z", "attacking_z", "chance_creation_z", "PPDA_z",
                     "defensive_intensity_z",
                     "defensive_duels_won_%_z", "defensive_height_z", "opposition_pass_tempo_z",
                     "opposition_progression_percentage_z", "opp_final_third_to_box_%_z",
                     "Opposition_xT_z", "high_turnovers_z", "turnover_line_height_z",
                     "recoveries_within_5s_%_z", "avg_time_to_defensive_action_z", 
                     "opposition_final_third_entries_10s_z", "opposition_box_entries_10s_z",
                     "opposition_xG_10s_z", "recoveries_z", "recovery_height_z", "retained_possessions_5s_z",
                     "retained_possessions_5s_%_z", "final_third_entries_10s_z", "box_entries_10s_z", 
                     "xG_10s_z", "xT_10s_z", "field_tilt_%_z", "long_ball_%_z", "pass_tempo_z",
                     "final_third_entries_%_z", "final_third_to_box_entries_%_z", "xT_z", "penalty_area_touches_z",
                     "box_entries_to_shot_%_z", "np_shots_z", "high_opportunity_shots_z", "np_xg_z", "np_goals_z",
                     "xg_per_shot_z", "ball_in_play_z", "total_xg_z",
                     "goal_difference_z", "goals_conceded_z", "goals_scored_z"
                     ]

columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                   "Posse adversário (%)", "Defesa", "Transição defensiva",
                   "Transição ofensiva", "Ataque", "Criação de chances",
                   "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                   "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                   "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                   "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)",
                   "Entradas do adversário no último terço em 10s da recuperação da posse",
                   "Entradas do adversário na área em 10s da recuperação da posse",
                   "xG do adversário em 10s da recuperação da posse", "Recuperações de posse",
                   "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                   "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                   "xT em 10s da recuperação da posse", "Field tilt (%)", "Bola longa (%)",
                   "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                   "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                   "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                   "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                   "xG (Total)", "Diferença de gols",
                    "Gols sofridos", "Gols marcados"
                    ]

# Create a dictionary mapping old names to new names
rename_dict = dict(zip(columns_to_rename, columns_renamed))

# Rename columns in variable_df_z_team
variable_df_z_team = variable_df_z_team.rename(columns=rename_dict)

# Sort the dataframe by 'game_id' and reset the index
variable_df_z_team = variable_df_z_team.sort_values(['rodada', 'data'], ascending=[False, False]).reset_index(drop=True)

#Making a csv file
variable_df_z_team.to_csv("variable_df_z_team.csv")
variable_df_z_team.to_csv("performance_team.csv")
###########################################################################
###########################################################################

# Rerunning columns from Master Code
# Calculating z-scores per round
# Create a new dataframe for z-scores
variable_df_z_round = pd.DataFrame()

###########################################################################
###########################################################################

#Bulding round game analysis (all club analysis)

# Group by 'round' and apply z-score transformation independently
for round, group in variable_df_new.groupby("round"):
    # Repeat columns [0:15]
    base_columns = group.iloc[:, :10].copy()
    # Apply z-score transformation to columns [7:] and rename with '_z' suffix
    zscore_columns = group.iloc[:, 10:].apply(zscore)
    zscore_columns.rename(columns=lambda col: f"{col}_z", inplace=True)
    # Combine the repeated columns with the z-score transformed columns
    função_z = pd.concat([base_columns, zscore_columns], axis=1)
    # Append to the final dataframe
    variable_df_z_round = pd.concat([variable_df_z_round, função_z], axis=0)

# Reset index after concatenation
variable_df_z_round.reset_index(drop=True, inplace=True)

###########################################################################
###########################################################################
#variable_df_z_round = variable_df_z_round.rename(columns={"opposition_final_third_entries_z": "opposition_final_third_entries_10s_z"})

# Inverting the sign of inverted metrics
variable_df_z_round["PPDA_z"] = -1*variable_df_z_round["PPDA_z"]
variable_df_z_round["opposition_pass_tempo_z"] = -1*variable_df_z_round["opposition_pass_tempo_z"]
variable_df_z_round["opposition_progression_percentage_z"] = -1*variable_df_z_round["opposition_progression_percentage_z"]
variable_df_z_round["opp_final_third_to_box_%_z"] = -1*variable_df_z_round["opp_final_third_to_box_%_z"]
variable_df_z_round["Opposition_xT_z"] = -1*variable_df_z_round["Opposition_xT_z"]
variable_df_z_round["high_turnovers_z"] = -1*variable_df_z_round["high_turnovers_z"]
variable_df_z_round["avg_time_to_defensive_action_z"] = -1*variable_df_z_round["avg_time_to_defensive_action_z"]
variable_df_z_round["avg_recovery_time_z"] = -1*variable_df_z_round["avg_recovery_time_z"]
variable_df_z_round["opposition_final_third_entries_10s_z"] = -1*variable_df_z_round["opposition_final_third_entries_10s_z"]
variable_df_z_round["opposition_box_entries_10s_z"] = -1*variable_df_z_round["opposition_box_entries_10s_z"]
variable_df_z_round["opposition_xG_10s_z"] = -1*variable_df_z_round["opposition_xG_10s_z"]
variable_df_z_round["goals_conceded_z"] = -1*variable_df_z_round["goals_conceded_z"]

###########################################################################
###########################################################################

# Creating qualities columns
# Define the columns to average for each metric
defence_metrics = ["PPDA_z", "defensive_intensity_z", "defensive_duels_won_%_z",
                   "defensive_height_z", "opposition_pass_tempo_z",	
                   "opposition_progression_percentage_z", "opp_final_third_to_box_%_z",	
                   "Opposition_xT_z"]

defensive_transition_metrics = ["high_turnovers_z", "turnover_line_height_z", "recoveries_within_5s_%_z", 
                                "avg_time_to_defensive_action_z", "opposition_final_third_entries_10s_z", 
                                "opposition_box_entries_10s_z", "opposition_xG_10s_z"]

attacking_transition_metrics = ["recoveries_z",	"recovery_height_z", "retained_possessions_5s_z",
                                "retained_possessions_5s_%_z", "final_third_entries_10s_z",
                                "box_entries_10s_z", "xG_10s_z", "xT_10s_z"]

attacking_metrics = ["field_tilt_%_z",	"long_ball_%_z", "pass_tempo_z", 
                  "final_third_entries_%_z", "final_third_to_box_entries_%_z", "xT_z"]

chance_creation_metrics = ["penalty_area_touches_z", "box_entries_to_shot_%_z", "np_shots_z", 
                           "high_opportunity_shots_z", "np_xg_z", "np_goals_z", "xg_per_shot_z"]

# Compute the arithmetic mean for each metric and assign to the respective column
variable_df_z_round["defence_z"] = variable_df_z_round[defence_metrics].mean(axis=1)
variable_df_z_round["defensive_transition_z"] = variable_df_z_round[defensive_transition_metrics].mean(axis=1)
variable_df_z_round["attacking_transition_z"] = variable_df_z_round[attacking_transition_metrics].mean(axis=1)
variable_df_z_round["attacking_z"] = variable_df_z_round[attacking_metrics].mean(axis=1)
variable_df_z_round["chance_creation_z"] = variable_df_z_round[chance_creation_metrics].mean(axis=1)

# Get a list of the current columns
cols = list(variable_df_z_round.columns)

# List of columns to be relocated
cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                  "attacking_z", "chance_creation_z"]#, "outcome_z"]

# Remove these columns from the list
for col in cols_to_remove:
    cols.remove(col)

# Insert the columns in the desired order at index 9, adjusting the index as we go
for i, col in enumerate(cols_to_remove):
    cols.insert(10 + i, col)

# Reorder the dataframe columns accordingly
variable_df_z_round = variable_df_z_round[cols]

# Renaming columns
# Renaming columns
columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                     "possession_z", "opponent_possession_z", "defence_z", "defensive_transition_z",
                     "attacking_transition_z", "attacking_z", "chance_creation_z", "PPDA_z",
                     "defensive_intensity_z",
                     "defensive_duels_won_%_z", "defensive_height_z", "opposition_pass_tempo_z",
                     "opposition_progression_percentage_z", "opp_final_third_to_box_%_z",
                     "Opposition_xT_z", "high_turnovers_z", "turnover_line_height_z",
                     "recoveries_within_5s_%_z", "avg_time_to_defensive_action_z", 
                     "opposition_final_third_entries_10s_z", "opposition_box_entries_10s_z",
                     "opposition_xG_10s_z", "recoveries_z", "recovery_height_z", "retained_possessions_5s_z",
                     "retained_possessions_5s_%_z", "final_third_entries_10s_z", "box_entries_10s_z", 
                     "xG_10s_z", "xT_10s_z", "field_tilt_%_z", "long_ball_%_z", "pass_tempo_z",
                     "final_third_entries_%_z", "final_third_to_box_entries_%_z", "xT_z", "penalty_area_touches_z",
                     "box_entries_to_shot_%_z", "np_shots_z", "high_opportunity_shots_z", "np_xg_z", "np_goals_z",
                     "xg_per_shot_z", "ball_in_play_z", "total_xg_z",
                     "goal_difference_z", "goals_conceded_z", "goals_scored_z"
                     ]

columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                   "Posse adversário (%)", "Defesa", "Transição defensiva",
                   "Transição ofensiva", "Ataque", "Criação de chances",
                   "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                   "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                   "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                   "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)",
                   "Entradas do adversário no último terço em 10s da recuperação da posse",
                   "Entradas do adversário na área em 10s da recuperação da posse",
                   "xG do adversário em 10s da recuperação da posse", "Recuperações de posse",
                   "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                   "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                   "xT em 10s da recuperação da posse", "Field tilt (%)", "Bola longa (%)",
                   "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                   "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                   "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                   "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                   "xG (Total)", "Diferença de gols",
                    "Gols sofridos", "Gols marcados"
                    ]

# Create a dictionary mapping old names to new names
rename_dict = dict(zip(columns_to_rename, columns_renamed))

# Rename columns in variable_df_z_team
variable_df_z_round = variable_df_z_round.rename(columns=rename_dict)

# Sort the dataframe by 'game_id' and reset the index
variable_df_z_round = variable_df_z_round.sort_values(['rodada', 'data'], ascending=[False, False]).reset_index(drop=True)

#Making a csv file
variable_df_z_round.to_csv("variable_df_z_round.csv")
variable_df_z_round.to_csv("performance_round.csv")


###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################

"""
#Code to build opposition analysis file
import pandas as pd

# Load the CSV files
df_schedule = pd.read_csv("df_schedule.csv")
oponnent_analysis = pd.read_csv("variable_df_new.csv")

# Ensure column names are consistent
#df_schedule = df_schedule[['game_id', 'home_team', 'away_team']]
#oponnent_analysis = oponnent_analysis[['game_id', 'clube']]

# Assign "home" or "away" to the "place" column in oponnent_analysis
def determine_place(row):
    game_id = row['game_id']
    clube = row['team_name']
    
    if (df_schedule.loc[df_schedule['game_id'] == game_id, 'home_team'].values == clube).any():
        return "Casa"
    elif (df_schedule.loc[df_schedule['game_id'] == game_id, 'away_team'].values == clube).any():
        return "Fora"
    return None  # If no match found

oponnent_analysis['place'] = oponnent_analysis.apply(determine_place, axis=1)

# Save the updated dataframe to a CSV file
oponnent_analysis.to_csv("oponnent_analysis.csv", index=False)
"""

#Creating performance_metrics_2

performance_metrics_2 = pd.read_csv("performance_metrics.csv")

# Creating qualities columns
# Define the columns to average for each metric
defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                   "defensive_height", "opposition_pass_tempo",	
                   "opposition_progression_percentage", "opp_final_third_to_box_%",	
                   "Opposition_xT"]

defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                "opposition_box_entries_10s", "opposition_xG_10s"]

attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                "retained_possessions_5s_%", "final_third_entries_10s",
                                "box_entries_10s", "xG_10s", "xT_10s"]

attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                  "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                           "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

# Compute the arithmetic mean for each metric and assign to the respective column
performance_metrics_2["defence"] = performance_metrics_2[defence_metrics].mean(axis=1)
performance_metrics_2["defensive_transition"] = performance_metrics_2[defensive_transition_metrics].mean(axis=1)
performance_metrics_2["attacking_transition"] = performance_metrics_2[attacking_transition_metrics].mean(axis=1)
performance_metrics_2["attacking"] = performance_metrics_2[attacking_metrics].mean(axis=1)
performance_metrics_2["chance_creation"] = performance_metrics_2[chance_creation_metrics].mean(axis=1)

# Get a list of the current columns
cols = list(performance_metrics_2.columns)

# List of columns to be relocated
cols_to_remove = ["defence", "defensive_transition", "attacking_transition", 
                  "attacking", "chance_creation"]

# Remove these columns from the list
for col in cols_to_remove:
    cols.remove(col)

# Insert the columns in the desired order at index 9, adjusting the index as we go
for i, col in enumerate(cols_to_remove):
    cols.insert(10 + i, col)

# Reorder the dataframe columns accordingly
performance_metrics_2 = performance_metrics_2[cols]

# Renaming columns
columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                     "possession", "opponent_possession", "defence", "defensive_transition",
                     "attacking_transition", "attacking", "chance_creation", "PPDA",
                     "defensive_intensity",
                     "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                     "opposition_progression_percentage", "opp_final_third_to_box_%",
                     "Opposition_xT", "high_turnovers", "turnover_line_height",
                     "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                     "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                     "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                     "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                     "xG_10s", "xT_10s", "field_tilt_%", "long_ball_%", "pass_tempo",
                     "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                     "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                     "xg_per_shot", "ball_in_play", "total_xg",
                     "goal_difference", "goals_conceded", "goals_scored"
                     ]

columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                   "Posse adversário (%)", "Defesa", "Transição defensiva",
                   "Transição ofensiva", "Ataque", "Criação de chances",
                   "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                   "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                   "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                   "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                   "Entradas do adversário no último terço em 10s da recuperação da posse",
                   "Entradas do adversário na área em 10s da recuperação da posse", 
                   "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                   "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                   "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                   "xT em 10s da recuperação da posse", "Field tilt (%)", "Bola longa (%)", 
                   "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                   "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                   "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                   "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                   "xG (Total)", "Diferença de gols",
                    "Gols sofridos", "Gols marcados"
                    ]

# Create a dictionary mapping old names to new names
rename_dict = dict(zip(columns_to_rename, columns_renamed))

# Rename columns in performance_metrics_2
performance_metrics_2 = performance_metrics_2.rename(columns=rename_dict)

# Sort the dataframe by 'game_id' and reset the index
performance_metrics_2 = performance_metrics_2.sort_values(['rodada', 'data'], ascending=[False, False]).reset_index(drop=True)

# Assumindo que performance_metrics_2 já é um DataFrame
performance_metrics_2 = performance_metrics_2.drop(performance_metrics_2.columns[0], axis=1)

#Making a csv file
performance_metrics_2.to_csv("performance_metrics_2.csv")

