#%%
# MatchAnalysis 2026 — Orchestrator
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
#import socceraction.xthreat as xthreat
from shapely.geometry import Point, Polygon
from scipy.spatial import ConvexHull
from scipy.stats import zscore
from scipy.stats import rankdata
#from sklearn.model_selection import train_test_split
#import pickle
from tqdm import tqdm
from scipy.stats import poisson

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')

###############################################################################
###############################################################################


game_ids = [
    1955748, 1955750, 1955752, 1955753, 1955755, 1955756, 1955758, 1955759,
    1955761, 1955762, 1955764, 1955765, 1955767, 1955768, 1955770, 1955771,
    1955773, 1955774, 1955776, 1955777, 1955779, 1955782, 1955785, 1955788,
    1955791, 1955794, 1955797, 1955800, 1955804, 1955806, 1955809, 1955812,
    1955815, 1955818, 1955821, 1955824, 1955827, 1955830, 1955833, 1955836,
    1955839, 1955842, 1955845, 1955848, 1955851, 1955854, 1955857, 1955860,
    1955862, 1955865, 1955868, 1955872, 1955875, 1955878, 1955881, 1955884,
    1955887, 1955890, 1955893, 1955896, 1955899, 1955902, 1955905, 1955908,
    1955911, 1955925, 1955926, 1955927, 1955928, 1955929, 1955930, 1955931,
    1955933, 1955934, 1955936, 1955937, 1955938, 1955940, 1955941, 1955943,
    1955944, 1955945, 1955947, 1955948, 1955950, 1955951, 1955952, 1955953,
    1955955, 1955956, 1955959, 1955962, 1955963, 1955965, 1955966, 1955968,
    1955969, 1955971, 1955972, 1955975, 1955977, 1955981, 1955983, 1955985,
    1955987, 1955989, 1955991, 1955993, 1955995, 1955996, 1955998, 1956000,
    1956002, 1956004, 1956006, 1956008, 1956010, 1956012, 1956014, 1956016,
    1956018, 1956020, 1956022, 1956024, 1956026, 1956028, 1956030, 1956032,
    1956034, 1956036, 1956037, 1956039, 1956041, 1956043, 1956046, 1956048,
    1956049
]

import subprocess, sys

# Save raw events as parquet for upstream scripts (avoids re-parsing 380 JSON files)
raw_dfs = []
data_dir = os.path.join(
    str(pathlib.Path().resolve()),
    'Brasileirão_2026'
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
raw_events_df.to_parquet("brasileirao_2026_events.parquet", index=False)
print(f"Saved brasileirao_2026_events.parquet ({len(raw_events_df)} events)")

# Run upstream scripts to produce model outputs
upstream_scripts = [
    "possession_chain.py",
    "xG_brasileirao.py",
    #"xA_brasileirao.py",
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

ws = sd.WhoScored(leagues="BRA-Brasileirão", seasons=2026)

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

progcarry_chains_df = pd.read_parquet("possesion_chains_brasileirao_2026.parquet")

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
#xa_df = pd.read_parquet("xA_brasileirao_2026.parquet")
#xa_df.rename(columns={"teamId": "team_id", "id": "event_id"}, inplace=True)

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xG — loaded from pre-built parquet (produced by xG_brasileirao.py)
xg_df = pd.read_parquet("xG_brasileirao_2026.parquet")
xg_df.rename(columns={"teamId": "team_id", "id": "event_id"}, inplace=True)

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###

progcarry_df["game_id"] = pd.to_numeric(progcarry_df["game_id"], errors="coerce").astype("Int64")

# xT — loaded from pre-built parquet (produced by xT_brasileirao.py)
xt_df = pd.read_parquet("xT_brasileirao_2026.parquet")
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
#     (opponent B's open-play passes in B's defensive 60% of the pitch)
#   / (A's tackles + interceptions + fouls committed in that same physical area)
#
# Opta F24 coordinates are normalized so each team attacks from x=0 (own goal)
# toward x=100 (opponent's goal). The "opponent's defensive 60%" is therefore:
#   - from the passing team's perspective (opponent B):      start_x <= 60
#   - from the pressing team's perspective (team A):         start_x >= 40
# These describe the same physical zone but from each team's own frame.
#
# Set-piece passes are excluded from the numerator (standard PPDA): qualifier
# 5 (free kick taken), 6 (corner taken), 107 (throw-in), 124 (goal kick).
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled
# Only outcome == 0 fouls (defensive fouls by the pressing team) feed PPDA.

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

# Passes leg: opponent's open-play passes in opponent's own defensive 60%.
# The passing team's frame has its own goal at x=0, so its defensive 60% is
# start_x <= 60. Set pieces (FK 5, corner 6, throw-in 107, goal kick 124) are
# excluded — only open-play passes count toward PPDA.
SET_PIECE_QUALIFIERS = (5, 6, 107, 124)

_is_set_piece_pass = df_with_opponents["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)

passes = (
    df_with_opponents[
        (df_with_opponents["type_id"] == 1)
        & (df_with_opponents["start_x"] <= 60)
        & (~_is_set_piece_pass)
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
    df_press_zone[(df_press_zone["type_id"] == 4) & (df_press_zone["outcome"] == 0)]
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

#######################################################
#######################################################

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
#   fouls committed  -> type_id 4 AND outcome = 0  (outcome 1 = fouled)
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled

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

    # Fouls committed: type 4 with outcome == 0 in this dataset
    # (WhoScored convention is inverted from the F24 spec — see header).
    fouls = (
        df[(df["type_id"] == 4) & (df["outcome"] == 0)]
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
# Opta F24 mapping (reference/Opta-f24_appendices.md, Appendix 1 line 49 for
# Tackle outcome semantics; Appendix 1 line 45 for Take On's overrun caveat):
#
#   WON buckets
#     - type_id 7  (Tackle)   any outcome    # defender dispossesses attacker
#                                            #   (outcome 1 = won + retained,
#                                            #    outcome 0 = won + ball lost
#                                            #    to a third player / out of
#                                            #    play — both stop the attack)
#     - type_id 4  (Foul)     outcome == 0   # defender commits foul to stop
#                                            #   (WhoScored convention: 0=committed)
#     - type_id 54 (Smother)  outcome == 1   # GK wins the ball on the ground
#     - type_id 3  (Take On)  outcome == 0   # attacker's failed dribble
#                                            # -> credit the OPPONENT (defender)
#
#   LOST buckets
#     - type_id 45 (Challenge) any outcome   # defender fails (always lost)
#     - type_id 3  (Take On)   outcome == 1  # attacker beats defender
#                                            # -> credit the OPPONENT (defender)
#
# Take-On filter:
#   Type-3 events with qualifier 211 ("overrun") are excluded — per Appendix 1
#   line 45 these are bad-touch overruns, not always a duel event.
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled
# Only outcome == 0 fouls (defensive fouls by the defender) feed the WON bucket.
#
# Exclusions and their reasons:
#   - type_id 8  (Interception) — reading a pass into space, not a 1v1 duel.
#   - type_id 12 (Clearance)    — not a contest, just a release under pressure.
#   - type_id 49 (Ball recovery)— a possession-change marker, not a duel.
#   - type_id 50 (Dispossessed) — attacker-side counterpart of a successful
#                                 tackle; already counted via type 7 and would
#                                 double-book the loss to the wrong team.
#
# Fouls suffered (type 4, outcome == 1 in this dataset) are not a defender's
# lost duel — they describe the attacker being fouled, so they are not counted.

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

df = progcarry_df[["game_id", "team_id", "type_id", "outcome", "qualifiers"]].merge(
    team_opponent_df,
    on=["game_id", "team_id"],
    how="left",
)

# --- Own-perspective events (team_id already = defender) ---
own_won_mask = (
    (df["type_id"] == 7)                                      # Tackle, any outcome
    | ((df["type_id"] == 4)  & (df["outcome"] == 0))          # Foul committed
    | ((df["type_id"] == 54) & (df["outcome"] == 1))          # Smother won
)
own_lost_mask = (df["type_id"] == 45)                         # Challenge (always lost)

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
# Exclude overruns (qualifier 211) — per Appendix 1 line 45 they are bad-touch
# events that are not always duels.
_is_overrun = df["qualifiers"].apply(lambda q: has_qualifier(q, 211))
takeon = df[
    (df["type_id"] == 3)
    & df["opponent_team_id"].notna()
    & (~_is_overrun)
].copy()
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
#   - type_id 4  (Foul)         outcome == 0  # foul committed by defender
#                                             #   (WhoScored convention: 0=committed)
#   - type_id 7  (Tackle)       any outcome
#   - type_id 8  (Interception)
#   - type_id 12 (Clearance)
#   - type_id 44 (Aerial duel)
#   - type_id 45 (Challenge)
#   - type_id 49 (Ball recovery)
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled
# Only outcome == 0 fouls (defensive fouls) feed the height calculation —
# fouls received describe the team's attacking positions and would bias the
# defensive line upward.
#
# Smother (type 54) is intentionally excluded: it always happens near the
# defender's own goal and would skew height downward.

PITCH_LENGTH_M = 105.0  # UEFA standard pitch length

defensive_mask = (
    ((progcarry_df["type_id"] == 4) & (progcarry_df["outcome"] == 0))
    | progcarry_df["type_id"].isin([7, 8, 12, 44, 45, 49])
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
# Leave defensive_height as NaN for (game_id, team_id) rows that had no
# defensive events. Filling with 0 would put them at the own-goal line and
# skew downstream Z-score calculations.

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

# Set-piece passes are excluded from the numerator: free-kicks (qualifier 5),
# corners (6), throw-ins (107), and goal kicks (124). These passes occur at
# stoppages and don't reflect in-play ball circulation tempo.
SET_PIECE_QUALIFIERS = (5, 6, 107, 124)

_is_set_piece_pass = progcarry_chains_df["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)

_pass_mask = (
    (progcarry_chains_df["type_id"] == 1)
    & (progcarry_chains_df["outcome"] == 1)
    & (~_is_set_piece_pass)
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
# Leave opposition_pass_tempo as NaN for rows without an opponent record or
# with zero opponent possession seconds. Filling with 0 would imply
# "infinitely slow opponent" and skew downstream Z-score calculations.

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
# Reads from progcarry_chains_df (the chain-tagged event view built by
# possession_chain.py — chain numbering starts at 0 and chain 0 is a real
# possession, not a sentinel).
#
# Final-third boundary: per Opta F24 Appendix 11 (reference/Opta-f24_
# appendices.md line 950), start_x and end_x are 0-100 percentages and
# every team attacks from x=0 toward x=100, so the attacking final third
# is start_x >= 200/3 (~66.67).
#
# Reach test: a chain "reaches the final third" if ANY of its events has
# start_x >= FT or end_x >= FT. This catches both pass-led entries (the
# pass event itself crosses the line in start_x→end_x) and carry-led
# entries (the carry happens between events, but the destination event's
# start_x is then >= FT). possession_chain.py does not insert synthetic
# carry rows, so a strict per-event "start_x < FT & end_x >= FT" test
# under-counts carry-led entries.
#
# Denominator choice: a possession counts as "valid" only if its first
# event starts OUTSIDE the final third. Possessions that already begin in
# the final third can't progress INTO it, so they're excluded from both
# numerator and denominator.

FINAL_THIRD = 200.0 / 3.0  # ~66.67

df = progcarry_chains_df[
    ["game_id", "team_id", "possessionId", "start_x", "end_x"]
].copy()

# Per-event: does this event itself sit at or beyond the final-third line
# (either at the start or at the end of the action)?
df["reaches_final_third"] = (
    (df["start_x"] >= FINAL_THIRD) | (df["end_x"] >= FINAL_THIRD)
)

# Collapse to one row per possession chain.
possession_stats = (
    df.groupby(["game_id", "team_id", "possessionId"], as_index=False)
    .agg(
        first_start_x=("start_x", "first"),
        any_reach=("reaches_final_third", "any"),
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
        final_third_entries=("any_reach", "sum"),
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
# Leave opposition_progression_percentage as NaN for rows where the opponent
# had no valid possessions. Filling with 0 would imply "opponent reached the
# final third in 0% of their possessions" and skew downstream Z-score
# calculations.


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
# Reads from progcarry_chains_df (the chain-tagged event view built by
# possession_chain.py — chain numbering starts at 0 and chain 0 is a real
# possession, not a sentinel).
#
# Opta F24 coordinate reference (Appendix 11, line 957):
#   Final third: x >= 66.67 (200/3)
#   Penalty box: x >= 83, 21.1 <= y <= 78.9
#
# Reach tests use BOTH start and end coordinates:
#   - in_box (per event): start in box OR end in box. Catches passes that
#     end in the box even when no recipient event is recorded (e.g., the
#     pass is intercepted at the box edge and the chain ends there).
#   - in_ft (per event): start_x >= FT OR end_x >= FT. Catches carry-led
#     entries (between events) and pass-led entries — possession_chain.py
#     does not insert synthetic carry rows.
#
# Denominator filter:
#   - has_ft (chain reached FT) AND
#   - NOT first_in_box (chain didn't START already inside the box)
# Excluding chains starting in the box guards against treating already-
# in-box chains as "moves from FT into box".

FINAL_THIRD = 200.0 / 3.0
BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

df7 = progcarry_chains_df[
    ["game_id", "team_id", "possessionId", "start_x", "start_y", "end_x", "end_y"]
].copy()

# Per-event geometry flags.
_start_in_box = (df7["start_x"] >= BOX_X) & df7["start_y"].between(BOX_Y_MIN, BOX_Y_MAX)
_end_in_box = (df7["end_x"] >= BOX_X) & df7["end_y"].between(BOX_Y_MIN, BOX_Y_MAX)
df7["start_in_box"] = _start_in_box
df7["in_box"] = _start_in_box | _end_in_box
df7["in_ft"] = (df7["start_x"] >= FINAL_THIRD) | (df7["end_x"] >= FINAL_THIRD)

# Collapse to one row per possession chain.
chain_stats = df7.groupby(["game_id", "team_id", "possessionId"], as_index=False).agg(
    first_in_box=("start_in_box", "first"),
    has_ft=("in_ft", "any"),
    has_box=("in_box", "any"),
)

# Valid: chain reached the final third and didn't already start in the box.
valid = chain_stats[chain_stats["has_ft"] & (~chain_stats["first_in_box"])]

team_stats = valid.groupby(["game_id", "team_id"], as_index=False).agg(
    final_third_possessions=("possessionId", "count"),
    box_entries=("has_box", "sum"),
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
# Leave opp_final_third_to_box_% as NaN for rows where the opponent had no
# valid FT-reaching possessions. Filling with 0 would imply "opponent
# converted 0% of their FT possessions into box entries" and skew downstream
# Z-score calculations.

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
#   4. NOT a set piece  Exclude corners (qualifier 6) and throw-ins
#                       (107). These are restart-context deliveries
#                       that the underlying xT model can rate as high-
#                       threat purely on coordinates (e.g. corner into
#                       the box) and would inflate the conceded xT for
#                       teams that simply face many corners. Free kicks
#                       (5) and goal kicks (124) are KEPT because their
#                       threat values reflect real in-play decision-
#                       making. This policy is mirrored in xT.py so
#                       own-team and conceded xT use the same
#                       convention.
#
# `xthreat` carries the continuous action-based xT value: orchestrator
# lines 388-401 merge xT_brasileirao_2026.parquet onto progcarry_df and
# raise if the merge produces an all-zero column.

DEFENSIVE_AREA_THRESHOLD = 200.0 / 3.0  # ~66.67
SET_PIECE_QUALIFIERS = (6, 107)

_is_set_piece_pass = progcarry_df["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)

_passes = progcarry_df.loc[
    (progcarry_df["type_id"] == 1)
    & (progcarry_df["outcome"] == 1)
    & (progcarry_df["start_x"] >= DEFENSIVE_AREA_THRESHOLD)
    & (~_is_set_piece_pass),
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
# Leave Opposition_xT as NaN for rows without an opponent record. Filling
# with 0 would imply "opponent generated zero threat from defensive-area
# passes" and skew downstream Z-score calculations.

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
#   type_id 1   Pass,         outcome=False -> failed pass (open-play only;
#                                              set-piece passes excluded —
#                                              see set-piece note below)
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
# Set-piece exclusion on failed passes: a failed throw-in, corner, free
# kick, or goal kick in the own 40% is a routine restart, not the open-play
# turnover the downstream pressing/quality score is meant to capture.
# Qualifier IDs match the convention used across the rest of the defensive
# metric suite: 5 (free kick), 6 (corner), 107 (throw-in), 124 (goal kick).
#
# Note on chain length: the original code gated on `last_chain == 1`, which
# `possession_chain_code.py` only sets on chains of >= 2 events. That
# silently dropped isolated single-event turnovers, i.e. exactly the fast
# losses this metric is meant to capture. The event-type filter already
# carries the "possession lost" semantics, so the chain guard is removed.
#
# NaN preservation: the post-merge `fillna(0)` is intentionally NOT applied.
# Missing-team rows must propagate as NaN through the downstream Z-score
# step (a 0 there would be a real, extreme value and skew the Z).

OWN_FORTY_THRESHOLD = 40.0
SET_PIECE_QUALIFIERS = (5, 6, 107, 124)

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)
_is_set_piece_pass = progcarry_df["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)

_turnover_events = (
    ((_type_id == 1) & ~_outcome & ~_is_set_piece_pass)
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

###############################################################################
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
#   type_id 1   Pass,         outcome=False -> failed pass (open-play only;
#                                              set-piece passes excluded —
#                                              see set-piece note below)
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
# Set-piece exclusion on failed passes: set-piece restart locations are
# stereotyped — failed goal kicks sit at start_x ~ 0, failed corners at
# start_x ~ 100, throw-ins on the sideline, free kicks at the foul site.
# Including them turns the average into a function of how many goal kicks
# vs corners a team takes, not the open-play "where do we lose the ball"
# picture this metric is meant to capture. Qualifier IDs match the rest
# of the defensive metric suite: 5 (free kick), 6 (corner), 107 (throw-in),
# 124 (goal kick).
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
SET_PIECE_QUALIFIERS = (5, 6, 107, 124)

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)
_is_set_piece_pass = progcarry_df["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)

_turnover_events = (
    ((_type_id == 1) & ~_outcome & ~_is_set_piece_pass)
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
#   type_id 8   Interception             (Opta outcome always 1, ref line 772
#                                         of Opta-f24_appendices.md; verified
#                                         empirically on 1955764.json: 21/21
#                                         type-8 events with outcome=1)
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
# and clearance; the metric measures reactivity, so attempts count too):
#   type_id 7   Tackle              -> tackle, both outcomes (attempt counts)
#   type_id 8   Interception        -> Opta outcome always 1 (ref line 772)
#   type_id 12  Clearance           -> both outcomes valid (ref line 776)
#   type_id 44  Aerial              -> aerial duel, both outcomes (attempt
#                                      counts; each duel produces two type-44
#                                      rows, one per player)
#   type_id 45  Challenge           -> defender attempts to win the ball and
#                                      fails (Opta outcome always 0). Counted
#                                      because the metric measures speed of
#                                      defensive engagement, not success.
#   type_id 49  Ball recovery       -> Opta "team wins the ball" event
#   type_id 4   Foul, outcome == 0  -> committed foul (defensive disruption,
#                                      e.g. tactical foul). NOTE: WhoScored
#                                      JSON inverts the F24 foul outcome —
#                                      outcome == 0 means the foul was
#                                      COMMITTED (verified empirically on
#                                      1955764.json via next-FK trace and
#                                      post-foul card test).
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
    | (_type_id == 45)
    | (_type_id == 49)
    | ((_type_id == 4) & ~_outcome)
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
#   type_id 49  Ball recovery            (Opta outcome always 1, ref line 818)
#   type_id 8   Interception             (Opta outcome always 1, ref line 772
#                                         of Opta-f24_appendices.md; verified
#                                         empirically on 1955764.json: 21/21
#                                         type-8 events with outcome=1)
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
#   type_id 49  Ball recovery            (Opta outcome always 1, ref line 818)
#   type_id 8   Interception             (Opta outcome always 1, ref line 772
#                                         of Opta-f24_appendices.md; verified
#                                         empirically on 1955764.json: 21/21
#                                         type-8 events with outcome=1)
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
# NaN preservation: the post-merge `fillna(0)` is intentionally NOT
# applied. The Z-score pipeline can't distinguish "opponent had 0 fast
# transitions" (a legitimate league extreme) from "team was missing
# entirely from progcarry_df" — a 0 in the second case sits at the
# league mean and biases the Z. Same reasoning as the rest of the
# defensive-metric suite (e.g. perdas_posse_linha_baixa.py).

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
#   type_id 49  Ball recovery            (Opta outcome always 1, ref line 818)
#   type_id 8   Interception             (Opta outcome always 1, ref line 772
#                                         of Opta-f24_appendices.md; verified
#                                         empirically on 1955764.json: 21/21
#                                         type-8 events with outcome=1)
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
# NaN preservation: the post-merge `fillna(0)` is intentionally NOT
# applied. The Z-score pipeline can't distinguish "opponent had 0 fast
# box entries" (a legitimate league extreme) from "team was missing
# entirely from progcarry_df" — a 0 in the second case sits at the
# league mean and biases the Z. Same reasoning as the rest of the
# defensive-metric suite (e.g. variable_df14_code.py).

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
#   type_id 49  Ball recovery            (Opta outcome always 1, ref line 818)
#   type_id 8   Interception             (Opta outcome always 1, ref line 772
#                                         of Opta-f24_appendices.md; verified
#                                         empirically on 1955764.json: 21/21
#                                         type-8 events with outcome=1)
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
# NaN preservation: the post-merge `fillna(0)` is intentionally NOT
# applied. The Z-score pipeline can't distinguish "opponent generated
# 0 fast-transition xG" (a legitimate league extreme) from "team was
# missing entirely from progcarry_df" — a 0 in the second case sits
# at the league mean and biases the Z. Same reasoning as the rest of
# the defensive-metric suite (e.g. variable_df14_code.py).

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

###############################################################################
###############################################################################

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
# game. Matches the recovery event set used by variable_df11 / df13 /
# df14 / df15 / df16 (the recovery-based transition metrics) so all
# "recovery"-based metrics stay consistent.
#
# Recovery events:
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True (successful tackle wins possession)
#   type_id 8   Interception             (Opta outcome always 1 in sample)
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
###############################################################################
###############################################################################

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
# Recovery events (same set as variable_df11 / variable_df17):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True (successful tackle wins possession)
#   type_id 8   Interception             (Opta outcome always 1 in sample)
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
# 5 seconds, per team per game. The rate analog of variable_df19
# (which outputs the raw count).
#
# Numerator:   chains with possession_time >= 5 seconds
# Denominator: all chains in the game-team (one row per chain via
#              groupby)
#
# Chain duration is derived from progcarry_chains_df as max(time) -
# min(time) per chain, consistent with variable_df19 and the possession
# dataframe calculations earlier in the pipeline.
#
# Note on possession chain coverage: possession_chain.py has no
# MIN_CHAIN_LEN logic -- it does not exclude short chains, so this
# metric counts every chain (including any single-event chains) for
# that team-game. The previous implementation filtered possessionId
# != 0, which silently dropped only the very first chain of the
# entire parquet (one chain in one game out of ~380); removed for
# cleanliness. A single-event chain contributes 0 duration so it
# trivially fails the 5s threshold and only affects the denominator.

RETENTION_THRESHOLD_SECONDS = 5.0

# Derive chain duration from progcarry_chains_df (max - min time per chain).
_chain_time_20 = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations_20 = (
    progcarry_chains_df.assign(_time=_chain_time_20)
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

variable_df = variable_df.merge(
    variable_df20[["game_id", "team_id", "retained_possessions_5s_%"]],
    on=["game_id", "team_id"],
    how="left",
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
# final third. Same machinery as variable_df14 (opposition variant),
# minus the opposition swap.
#
# Recovery events (same set as variable_df11 / variable_df14):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 8   Interception             (Opta outcome always 1 in sample)
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
# NaN preserved: missing-team rows in the merge are ambiguous between
# "real zero" and "missing data". Per project convention, leave NaN so
# the downstream Z-score step skips them rather than treating missing
# data as a far-low outlier.

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
# Same machinery as variable_df15 (opposition variant), minus the
# opposition swap.
#
# Recovery events (same set as variable_df11 / variable_df15):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 8   Interception             (Opta outcome always 1 in sample)
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
# of variable_df14 / variable_df15 / variable_df21.
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
# NaN preserved: missing-team rows in the merge are ambiguous between
# "real zero" and "missing data". Per project convention, leave NaN so
# the downstream Z-score step skips them rather than treating missing
# data as a far-low outlier.

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
# Same machinery as variable_df16 (opposition variant), minus the
# opposition swap.
#
# Recovery events (same set as variable_df11 / variable_df16):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 8   Interception             (Opta outcome always 1 in sample)
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
# NaN preserved: missing-team rows in the merge are ambiguous between
# "real zero" and "missing data". Per project convention, leave NaN so
# the downstream Z-score step skips them rather than treating missing
# data as a far-low outlier.

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
# attacks. Direct analog of variable_df23 with xthreat replacing
# non-penalty xG.
#
# Recovery events (same set as variable_df11 / variable_df23):
#   type_id 49  Ball recovery            (Opta outcome always 1)
#   type_id 7   Tackle,     outcome=True
#   type_id 8   Interception             (Opta outcome always 1 in sample)
#   type_id 44  Aerial,     outcome=True
#   type_id 11  Claim,      outcome=True
#
# xT event selection: any progcarry_df row with xthreat > 0.
# The xthreat column contains continuous xT values merged from
# xT_brasileirao_2026.parquet; events without xT are filled with 0.
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
# NaN preserved: missing-team rows in the merge are ambiguous between
# "real zero" and "missing data". Per project convention, leave NaN so
# the downstream Z-score step skips them rather than treating missing
# data as a far-low outlier.

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
# the same opposition-swap pattern used elsewhere in this pipeline.
#
# Replaces the original iterrows + per-row filter + iloc[0] lookup,
# which was O(n * m) and silently picked the first row on duplicate
# game_ids.
#
# NaN preservation: a missing game in the `possession` feed is a
# data-quality signal, not a "team had 0% possession" fact. Possession
# %'s natural neutral is 50, so filling with 0 would inject a real
# extreme value and bias the downstream Z-score. NaN is left to
# propagate, consistent with the project-wide convention.

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
# handled), field_tilt_% stays NaN so the Z-score step treats the row
# as missing, consistent with the project-wide NaN-preservation
# convention. Note that the metric's natural neutral is 50%, so filling
# with 0 would inject a real extreme value and bias league-wide Z.

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
# Set-piece handling: free kicks (qualifier 5), corners (6), and
# throw-ins (107) are excluded from both numerator and denominator --
# corners are long by definition, most direct free kicks are long, and
# throw-ins from the defensive third inflate the long-ball share for
# every team in a way that masks actual playing-style differences.
# Goal kicks (qualifier 124) are KEPT: a team that consistently plays
# short out of the back vs. one that always launches it long is the
# exact direct-vs-possession signal this metric is meant to capture,
# and excluding goal kicks would erase that.
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
# NaN preservation: the internal np.where guard returns NaN when a
# team-game has zero qualifying passes, and the final merge leaves
# missing team-games as NaN so the downstream Z-score step treats them
# as missing rather than as a real 0% long-ball share (which would
# bias the league mean and the team's Z-score downward).

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)
_qualifiers = progcarry_df["qualifiers"]

# Exclude free kicks (5), corners (6), and throw-ins (107). Goal kicks
# (124) are intentionally kept -- see header comment.
_is_set_piece = _qualifiers.apply(
    lambda q: any(has_qualifier(q, qid) for qid in (5, 6, 107))
)

_pass_mask = (_type_id == 1) & _outcome & ~_is_set_piece

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
# Direct analog of Velocidade_passe_adversário.py (Opposition Pass
# Tempo) minus the opposition swap.
#
# Reads from progcarry_chains_df -- the chain-annotated event view
# built by possession_chain.py. Chain duration is derived as
# max(time) - min(time) per chain, consistent with the possession
# dataframe and pass tempo calculations.
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
# Possession-chain note: possession_chain.py initializes the counter at
# 0 and increments it after each stop criterion. possessionId == 0 is
# the first chain of the dataset, not a short-chain sentinel, so it is
# NOT filtered out -- the prior `possessionId != 0` filter has been
# removed in lockstep with the orchestrator pipeline-wide cleanup.
#
# NaN preservation: the np.where guard returns NaN when a team-game
# has zero possession seconds, and the final merge leaves missing
# team-games as NaN so the downstream Z-score step treats them as
# missing rather than as a real 0-passes-per-minute team (which would
# be a real extreme low value and bias both the league mean and the
# team's Z-score downward).

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
# view built by possession_chain.py (possessionId != 0 means
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
# NaN preservation: the np.where guard returns NaN when a team-game
# has zero qualifying possessions, and the final merge leaves missing
# team-games as NaN so the downstream Z-score step treats them as
# missing rather than as a real 0% final-third-entry team (which would
# be a real extreme low value and bias both the league mean and the
# team's Z-score downward).

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
# test. Same convention used elsewhere in this pipeline. The
# original checked start_x/start_y, which missed every delivering
# event (the event whose end_x first crossed x=83 wouldn't have
# start_x in the box until the NEXT event, and "next event" may not
# be in the same chain).
#
# Short-chain bias: progcarry_chains_df excludes possessionId == 0
# (MIN_CHAIN_LEN = 2 in possession_chain.py). Consistent with the
# rest of the pipeline.
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
# NaN preservation: the np.where guard returns NaN when a team-game
# has zero final-third possessions, and the final merge leaves
# missing team-games as NaN so the downstream Z-score step treats
# them as missing rather than as a real 0% box-entry team (which
# would be a real extreme low value and bias both the league mean
# and the team's Z-score downward).

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
# Set-piece filter: corners (qualifier 6) and throw-ins (107) are
# excluded -- these are restart-context deliveries that the underlying
# xT model can rate as high-threat purely on coordinates (e.g. corner
# delivered into the box) and would inflate teams that earn many of
# them. Free kicks (5) and goal kicks (124) are KEPT because their
# threat values reflect real in-play decision-making (where to launch,
# whom to find). This policy is mirrored in xT_adversário.py so own-
# team xT and conceded xT use the same convention.
#
# NaN preservation: missing team-games left as NaN by the final merge
# so the downstream Z-score step treats them as missing rather than as
# a real 0-xT team (which would be a real extreme low value and bias
# both the league mean and the team's Z-score downward).

SET_PIECE_QUALIFIERS = (6, 107)

_is_set_piece = progcarry_df["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)

variable_df31 = (
    progcarry_df.loc[~_is_set_piece]
    .groupby(["game_id", "team_id"], as_index=False)["xthreat"]
    .sum()
    .rename(columns={"xthreat": "xT"})
)

variable_df31.head(100).to_csv("variable_df31.csv", index=True)

variable_df = variable_df.merge(
    variable_df31[["game_id", "team_id", "xT"]],
    on=["game_id", "team_id"],
    how="left",
)
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
# NaN preservation: missing team-games are left as NaN by the final
# merge so the downstream Z-score step treats them as missing rather
# than as a real 0-touches team (which would be a real extreme low
# value and bias both the league mean and the team's Z-score downward).

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
# Same convention as variable_df30 (entradas_área(%).py).
#
# Shot detection: shot == True column on progcarry_chains_df.
#
# Penalty box (Opta F24 Appendix 11, reference/Opta-f24_appendices.md
# line 957): x >= 83, 21.1 <= y <= 78.9.
#
# Short-chain bias: progcarry_chains_df excludes possessionId == 0
# (MIN_CHAIN_LEN = 2 in possession_chain.py). Consistent with the
# rest of the pipeline.
#
# NaN preservation: the np.where guard returns NaN when a team-game
# has zero box entries, and the final merge leaves missing team-games
# as NaN so the downstream Z-score step treats them as missing rather
# than as a real 0% box-conversion team (which would be a real extreme
# low value and bias both the league mean and the team's Z-score
# downward).

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
# NaN preservation: missing team-games are left as NaN by the final
# merge so the downstream Z-score step treats them as missing rather
# than as a real 0-shots team (which would be a real extreme low value
# and bias both the league mean and the team's Z-score downward).

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
# NaN preservation: missing team-games are left as NaN by the final
# merge so the downstream Z-score step treats them as missing rather
# than as a real 0-big-chances team (which would be a real extreme low
# value and bias both the league mean and the team's Z-score downward).

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
# NaN preservation: missing team-games are left as NaN by the final
# merge so the downstream Z-score step treats them as missing rather
# than as a real 0-xG team (which would be a real extreme low value
# and bias both the league mean and the team's Z-score downward).

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
# NaN preservation: missing team-games are left as NaN by the final
# merge so the downstream Z-score step distinguishes "team played and
# scored zero non-penalty goals" (a real 0) from "team-game absent
# from progcarry_df entirely" (missing data). Filling with 0 would
# collapse those into one extreme low value and bias both the league
# mean and the team's Z-score downward.

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
# xG values already merged into df (see variable_df36).
# Qualifier detection via has_qualifier helper.
#
# NaN preservation: missing team-games are left as NaN by the final
# merge so the downstream Z-score step treats them as missing rather
# than as a real 0-xG-per-shot team (which would be below the lowest
# realistic value and bias both the league mean and the team's Z-score
# downward).

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

# Since all NaN are actually zeros...
# 1. Replace all NaN with 0 (since you confirmed NaN means zero in your data)
variable_df_new = variable_df_new.fillna(0)

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

# Add "Temporada" column with the value 2026 as the first column in the dataframe
variable_df_new.insert(0, "Temporada", 2026)

# Add "Temporada" column with the value 2026 as the first column in the dataframe
#variable_df_new.insert(0, "Liga", "BRA1")

###########################################################################
###########################################################################

# Building round column
# Numbering rounds
# 1. Load the rounds reference file and keep only the keys we need
rodada_df = pd.read_excel('rodada_2026.xlsx')[['game_id', 'round']]

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
#defence_metrics = ["PPDA_z", "defensive_intensity_z", "defensive_duels_won_%_z",
#                   "defensive_height_z", "opposition_pass_tempo_z",	
#                   "opposition_progression_percentage_z", "opp_final_third_to_box_%_z",	
#                   "Opposition_xT_z"]


# Drop weak/ambiguous contributors
defence_metrics_outcome = ["Opposition_xT_z", "opposition_progression_percentage_z", 
                   "opp_final_third_to_box_%_z"]
defence_metrics_process = ["PPDA_z", "defensive_intensity_z", "defensive_height_z"]

# Weighed mean:
defence_metrics = (0.6 * variable_df_z_team[defence_metrics_outcome].mean(axis=1) +
                   0.4 * variable_df_z_team[defence_metrics_process].mean(axis=1))

#defensive_transition_metrics = ["high_turnovers_z", "turnover_line_height_z", "recoveries_within_5s_%_z", 
#                                "avg_time_to_defensive_action_z", "opposition_final_third_entries_10s_z", 
#                                "opposition_box_entries_10s_z", "opposition_xG_10s_z"]

defensive_transition_core = ["high_turnovers_z", "turnover_line_height_z",
                       "opposition_final_third_entries_10s_z",
                       "opposition_box_entries_10s_z"]

defensive_transition_metrics = variable_df_z_team[defensive_transition_core].mean(axis=1)

#attacking_transition_metrics = ["recoveries_z",	"recovery_height_z", "retained_possessions_5s_z",
#                                "retained_possessions_5s_%_z", "final_third_entries_10s_z",
#                                "box_entries_10s_z", "xG_10s_z", "xT_10s_z"]

attacking_transition_core = ["recoveries_z", "recovery_height_z",
                             "retained_possessions_5s_z",
                             "final_third_entries_10s_z",
                             "box_entries_10s_z", "xT_10s_z"]

attacking_transition_metrics = variable_df_z_team[attacking_transition_core].mean(axis=1)    

#attacking_metrics = ["field_tilt_%_z",	"long_ball_%_z", "pass_tempo_z", 
#                  "final_third_entries_%_z", "final_third_to_box_entries_%_z", "xT_z"]

attacking_core = ["field_tilt_%_z", 
                  "final_third_entries_%_z",
                  "final_third_to_box_entries_%_z", "xT_z"]

attacking_metrics = variable_df_z_team[attacking_core].mean(axis=1)

#chance_creation_metrics = ["penalty_area_touches_z", "box_entries_to_shot_%_z", "np_shots_z", 
#                           "high_opportunity_shots_z", "np_xg_z", "np_goals_z", "xg_per_shot_z"]

# Volume of chances created
chance_creation_volume = ["penalty_area_touches_z", "np_shots_z", 
                   "high_opportunity_shots_z", "np_xg_z"]

# Quality and outcome
chance_creation_quality_outcome = ["xg_per_shot_z", "np_goals_z", 
                            "box_entries_to_shot_%_z"]

chance_creation_metrics = 0.7 * variable_df_z_team[chance_creation_volume].mean(axis=1) + 0.3 * variable_df_z_team[chance_creation_quality_outcome].mean(axis=1)


# Compute the arithmetic mean for each metric and assign to the respective column
#variable_df_z_team["defence_z"] = variable_df_z_team[defence_metrics].mean(axis=1)
#variable_df_z_team["defensive_transition_z"] = variable_df_z_team[defensive_transition_metrics].mean(axis=1)
#variable_df_z_team["attacking_transition_z"] = variable_df_z_team[attacking_transition_metrics].mean(axis=1)
#variable_df_z_team["attacking_z"] = variable_df_z_team[attacking_metrics].mean(axis=1)
#variable_df_z_team["chance_creation_z"] = variable_df_z_team[chance_creation_metrics].mean(axis=1)

variable_df_z_team["defence_z"] = defence_metrics
variable_df_z_team["defensive_transition_z"] = defensive_transition_metrics
variable_df_z_team["attacking_transition_z"] = attacking_transition_metrics
variable_df_z_team["attacking_z"] = attacking_metrics
variable_df_z_team["chance_creation_z"] = chance_creation_metrics

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
                     "avg_recovery_time_z",
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
                   "Tempo médio para recuperação de posse",
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
#defence_metrics = ["PPDA_z", "defensive_intensity_z", "defensive_duels_won_%_z",
#                   "defensive_height_z", "opposition_pass_tempo_z",	
#                   "opposition_progression_percentage_z", "opp_final_third_to_box_%_z",	
#                   "Opposition_xT_z"]


# Drop weak/ambiguous contributors
defence_metrics_outcome = ["Opposition_xT_z", "opposition_progression_percentage_z", 
                   "opp_final_third_to_box_%_z"]
defence_metrics_process = ["PPDA_z", "defensive_intensity_z", "defensive_height_z"]

# Weighed mean:
defence_metrics = (0.6 * variable_df_z_round[defence_metrics_outcome].mean(axis=1) +
                   0.4 * variable_df_z_round[defence_metrics_process].mean(axis=1))

#defensive_transition_metrics = ["high_turnovers_z", "turnover_line_height_z", "recoveries_within_5s_%_z", 
#                                "avg_time_to_defensive_action_z", "opposition_final_third_entries_10s_z", 
#                                "opposition_box_entries_10s_z", "opposition_xG_10s_z"]

defensive_transition_core = ["high_turnovers_z", "turnover_line_height_z",
                       "opposition_final_third_entries_10s_z",
                       "opposition_box_entries_10s_z"]

defensive_transition_metrics = variable_df_z_round[defensive_transition_core].mean(axis=1)

#attacking_transition_metrics = ["recoveries_z",	"recovery_height_z", "retained_possessions_5s_z",
#                                "retained_possessions_5s_%_z", "final_third_entries_10s_z",
#                                "box_entries_10s_z", "xG_10s_z", "xT_10s_z"]

attacking_transition_core = ["recoveries_z", "recovery_height_z",
                             "retained_possessions_5s_z",
                             "final_third_entries_10s_z",
                             "box_entries_10s_z", "xT_10s_z"]

attacking_transition_metrics = variable_df_z_round[attacking_transition_core].mean(axis=1)    

#attacking_metrics = ["field_tilt_%_z",	"long_ball_%_z", "pass_tempo_z", 
#                  "final_third_entries_%_z", "final_third_to_box_entries_%_z", "xT_z"]

attacking_core = ["field_tilt_%_z", 
                  "final_third_entries_%_z",
                  "final_third_to_box_entries_%_z", "xT_z"]

attacking_metrics = variable_df_z_round[attacking_core].mean(axis=1)

#chance_creation_metrics = ["penalty_area_touches_z", "box_entries_to_shot_%_z", "np_shots_z", 
#                           "high_opportunity_shots_z", "np_xg_z", "np_goals_z", "xg_per_shot_z"]

# Volume of chances created
chance_creation_volume = ["penalty_area_touches_z", "np_shots_z", 
                   "high_opportunity_shots_z", "np_xg_z"]

# Quality and outcome
chance_creation_quality_outcome = ["xg_per_shot_z", "np_goals_z", 
                            "box_entries_to_shot_%_z"]

chance_creation_metrics = 0.7 * variable_df_z_round[chance_creation_volume].mean(axis=1) + 0.3 * variable_df_z_round[chance_creation_quality_outcome].mean(axis=1)



variable_df_z_round["defence_z"] = defence_metrics
variable_df_z_round["defensive_transition_z"] = defensive_transition_metrics
variable_df_z_round["attacking_transition_z"] = attacking_transition_metrics
variable_df_z_round["attacking_z"] = attacking_metrics
variable_df_z_round["chance_creation_z"] = chance_creation_metrics

# Compute the arithmetic mean for each metric and assign to the respective column
#variable_df_z_round["defence_z"] = variable_df_z_round[defence_metrics].mean(axis=1)
#variable_df_z_round["defensive_transition_z"] = variable_df_z_round[defensive_transition_metrics].mean(axis=1)
#variable_df_z_round["attacking_transition_z"] = variable_df_z_round[attacking_transition_metrics].mean(axis=1)
#variable_df_z_round["attacking_z"] = variable_df_z_round[attacking_metrics].mean(axis=1)
#variable_df_z_round["chance_creation_z"] = variable_df_z_round[chance_creation_metrics].mean(axis=1)


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
columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                     "possession_z", "opponent_possession_z", "defence_z", "defensive_transition_z",
                     "attacking_transition_z", "attacking_z", "chance_creation_z", "PPDA_z",
                     "defensive_intensity_z",
                     "defensive_duels_won_%_z", "defensive_height_z", "opposition_pass_tempo_z",
                     "opposition_progression_percentage_z", "opp_final_third_to_box_%_z",
                     "Opposition_xT_z", "high_turnovers_z", "turnover_line_height_z",
                     "recoveries_within_5s_%_z", "avg_time_to_defensive_action_z", 
                     "avg_recovery_time_z",
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
                   "Tempo médio para recuperação de posse",
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
                                "avg_time_to_defensive_action", "avg_recovery_time", "opposition_final_third_entries_10s", 
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
                     "avg_recovery_time",
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
                   "Tempo médio para recuperação de posse",
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

###########################################################
###########################################################
###########################################################
###########################################################
###########################################################
###########################################################
###########################################################
###########################################################

# Início da Construção das Variáveis de Estilo de Jogo
# Variáveis de Play Style
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
#   - type_id 4  (Foul)         outcome == 0  # foul committed by defender
#                                             #   (WhoScored convention: 0=committed)
#   - type_id 7  (Tackle)       any outcome
#   - type_id 8  (Interception)
#   - type_id 12 (Clearance)
#   - type_id 44 (Aerial duel)
#   - type_id 45 (Challenge)
#   - type_id 49 (Ball recovery)
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled
# Only outcome == 0 fouls (defensive fouls) feed the height calculation —
# fouls received describe the team's attacking positions and would bias the
# defensive line upward.
#
# Smother (type 54) is intentionally excluded: it always happens near the
# defender's own goal and would skew height downward.

PITCH_LENGTH_M = 105.0  # UEFA standard pitch length

defensive_mask = (
    ((progcarry_df["type_id"] == 4) & (progcarry_df["outcome"] == 0))
    | progcarry_df["type_id"].isin([7, 8, 12, 44, 45, 49])
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

variable_ps1.head(100).to_csv("variable_ps1.csv", index=True)

variable_ps = variable_ps.merge(
    variable_ps1[["game_id", "team_id", "defensive_height"]],
    on=["game_id", "team_id"],
    how="left",
)
# Leave defensive_height as NaN for (game_id, team_id) rows that had no
# defensive events. Filling with 0 would put them at the own-goal line and
# skew downstream Z-score calculations.


###############################################################################
###############################################################################

# Variáveis
# 2
# High Recoveries %
"""High Recoveries % is the share of a team's open-play ball recoveries
that occur in the attacking third (start_x >= 200/3 ~= 66.667 per Opta
F24 Appendix 11 line 950). A recovery is any event that regains
possession for the team:
  type_id 49  Ball recovery          (Opta outcome always 1, ref line 818)
  type_id 8   Interception           (Opta outcome always 1, ref line 772)
  type_id 7   Tackle with outcome 1  (win + retain possession, ref line 771)
  type_id 44  Aerial with outcome 1  (duel won, ref line 815)

Open-play scope: type_id 11 (Claim) is intentionally NOT included.
Goalkeeper claims are almost exclusively responses to set pieces and
crosses, never reflect pressing activity, and almost never occur in the
attacking third -- so they would only inflate the denominator and depress
the rate for teams with an active goalkeeper. Excluding type 11 is
equivalent to scoping the metric to outfield-player recoveries from open
play. (Opta does not propagate set-piece qualifiers 5/6/107/124 onto the
recovery events themselves, so an additional qualifier-based filter would
be a no-op here.)

No first_chain / possessionId filter: the canonical mask already answers
"did the team actually regain the ball?", and the prior first_chain==1 gate
silently dropped chains of fewer than 2 events -- exactly the fast
press-recover-press cycles this metric should reward.
"""

FINAL_THIRD = 200.0 / 3.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_recovery_mask = (
    (_type_id == 49)
    | ((_type_id == 7) & _outcome)
    | (_type_id == 8)
    | ((_type_id == 44) & _outcome)
)

_recoveries = progcarry_df.loc[_recovery_mask, ["game_id", "team_id", "start_x"]].copy()
_recoveries["high"] = (_recoveries["start_x"] >= FINAL_THIRD).astype(int)

variable_ps2 = (
    _recoveries.groupby(["game_id", "team_id"], as_index=False)
    .agg(
        total_recoveries=("start_x", "size"),
        high_recoveries=("high", "sum"),
    )
)
variable_ps2["high_recoveries_%"] = np.where(
    variable_ps2["total_recoveries"] > 0,
    variable_ps2["high_recoveries"] / variable_ps2["total_recoveries"] * 100.0,
    np.nan,
)

variable_ps2 = variable_ps2[
    ["game_id", "team_id", "total_recoveries", "high_recoveries", "high_recoveries_%"]
]

variable_ps = variable_ps.merge(
    variable_ps2[["game_id", "team_id", "high_recoveries_%"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################

# Variáveis
# 3
# PPDA
"""PPDA stands for Passes Per Defensive Action. It is a metric used to measure the intensity of a
team's pressing by calculating the number of passes allowed by a team IN THE OPPONNET'S 60% OF THE FIELD before attempting a
defensive action such as a tackle, interception, or foul. A lower PPDA value indicates a higher
pressing intensity"""

# PPDA (Passes Per Defensive Action)
#
# PPDA for team A in a given match =
#     (opponent B's open-play passes in B's defensive 60% of the pitch)
#   / (A's tackles + interceptions + fouls committed in that same physical area)
#
# Opta F24 coordinates are normalized so each team attacks from x=0 (own goal)
# toward x=100 (opponent's goal). The "opponent's defensive 60%" is therefore:
#   - from the passing team's perspective (opponent B):      start_x <= 60
#   - from the pressing team's perspective (team A):         start_x >= 40
# These describe the same physical zone but from each team's own frame.
#
# Set-piece passes are excluded from the numerator (standard PPDA): qualifier
# 5 (free kick taken), 6 (corner taken), 107 (throw-in), 124 (goal kick).
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled
# Only outcome == 0 fouls (defensive fouls by the pressing team) feed PPDA.

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

# Passes leg: opponent's open-play passes in opponent's own defensive 60%.
# The passing team's frame has its own goal at x=0, so its defensive 60% is
# start_x <= 60. Set pieces (FK 5, corner 6, throw-in 107, goal kick 124) are
# excluded — only open-play passes count toward PPDA.
SET_PIECE_QUALIFIERS = (5, 6, 107, 124)

_is_set_piece_pass = df_with_opponents["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)

passes = (
    df_with_opponents[
        (df_with_opponents["type_id"] == 1)
        & (df_with_opponents["start_x"] <= 60)
        & (~_is_set_piece_pass)
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
    df_press_zone[(df_press_zone["type_id"] == 4) & (df_press_zone["outcome"] == 0)]
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

Foul outcome convention -- WhoScored INVERTS the official Opta F24 spec:
  Official Opta F24 (Appendix 8): outcome 1 = committed, outcome 0 = fouled.
  WhoScored JSON we consume:      outcome 0 = committed, outcome 1 = fouled.
The inversion is empirically verified on 1955764.json two independent ways
(next-FK trace and post-foul card test); see METRICS_REVIEW_CONTEXT.md
"Critical empirical finding -- foul outcome is INVERTED" for the proof.
The canonical "team committed a foul" mask is therefore
  (type_id == 4) & (outcome == 0)
with team_id taken directly from the row. Matches variable_df4 in
MatchAnalysis_PlayStyle_2026.py.

No possession-chain / defensive-transition gate: a foul by definition is
committed on an opponent, so the committing team is not in possession;
the prior "during opponent's possessionId" filter was a workaround for
the outcome misreading, not an independent semantic constraint.
"""

_fouls = progcarry_df.loc[
    (progcarry_df["type_id"] == 4) & (progcarry_df["outcome"] == 0),
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
    variable_ps4["attacking_half_fouls"] / variable_ps4["total_fouls"] * 100.0,
    np.nan,
)

variable_ps4 = variable_ps4[
    ["game_id", "team_id", "total_fouls", "attacking_half_fouls", "fouls_in_attacking_half_%"]
]

variable_ps = variable_ps.merge(
    variable_ps4[["game_id", "team_id", "fouls_in_attacking_half_%"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################

# Variáveis
# 5
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
#   fouls committed  -> type_id 4 AND outcome = 0  (outcome 1 = fouled)
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled

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

    # Fouls committed: type 4 with outcome == 0 in this dataset
    # (WhoScored convention is inverted from the F24 spec — see header).
    fouls = (
        df[(df["type_id"] == 4) & (df["outcome"] == 0)]
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
variable_ps5.head(100).to_csv("variable_ps5.csv", index=True)

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
MatchAnalysis_PlayStyle_2026.py, which uses only successful ball-regaining
events). A team that slide-tackles at t=2s but misses scores low on this
metric even though the ball is not yet regained -- that is the intended
meaning.

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
  type_id 4   Foul, outcome=0     foul COMMITTED by this team (WhoScored
                                  INVERTS Opta's foul outcome -- see
                                  METRICS_REVIEW_CONTEXT.md "Critical
                                  empirical finding -- foul outcome is
                                  INVERTED": outcome 0 = committed,
                                  outcome 1 = was fouled, opposite of
                                  Opta F24 Appendix 8)
  type_id 11  Claim, outcome=1    GK cleanly catches a cross (claim
                                  outcomes follow the official Opta spec
                                  -- only foul outcomes are flipped)

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
    | ((_type_id == 4) & ~_outcome)
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
"""Counter-Press Success Rate % is the share of a team's open-play
outfield ball recoveries that occur within 5 seconds of losing the ball
-- i.e. the success rate of immediate counter-pressing. Adapted from
MatchAnalysis_PlayStyle_2026.py variable_df11 (Recoveries within 5s %),
with the recovery mask narrowed to outfield events for pressing
semantics (see "Open-play scope" below).

Loss events (canonical mask, shared with variable_df11 / variable_df13):
  type_id 1   Pass,      outcome=False  (failed pass)
  type_id 3   Take On,   outcome=False  (failed dribble)
  type_id 50  Dispossessed              (Opta outcome always 1)
  type_id 51  Error                     (Opta outcome always 1)
  type_id 61  Ball touch

Recovery events:
  type_id 49  Ball recovery             (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True  (wins possession)
  type_id 8   Interception              (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True  (wins the aerial duel)

Open-play scope: type_id 11 (Claim) is intentionally NOT included even
though it appears in the canonical variable_df11 recovery mask.
Goalkeeper claims are almost exclusively responses to set pieces and
crosses and do not reflect counter-pressing activity by outfield
players, which is what this metric is meant to capture (mirrors the
type-11 exclusion applied in high_recoveries_%.py for the same reason).
Opta does not propagate set-piece qualifiers 5/6/107/124 onto recovery
events themselves, so an additional qualifier-based filter would be a
no-op here.

The prior implementation had three independent bugs corrected here:
  1. Recovery mask used {3, 4, 7, 44, 45, 54}, which includes non-
     recoveries (Take On is an attacking action; Foul hands the ball
     to the opponent; Challenge is always outcome=0 by definition) and
     excludes the canonical Opta recoveries (49 Ball recovery and 8
     Interception -- the two events Opta explicitly tags as recoveries).
  2. Cartesian merge without dedup let one recovery pair to multiple
     prior losses, inflating the numerator and allowing rates > 100%.
     merge_asof(direction="backward", allow_exact_matches=True) pairs
     each recovery with at most one preceding loss; True (the pandas
     default) is the project rule for within-window metrics so a
     same-second recovery still pairs with its loss.
  3. No period_id guard: a loss in H1 could pair to a recovery in H2
     because `time` is per-period seconds. by=[..., period_id] fixes it.

Pairing: for each recovery, find the most recent same-team loss in the
same period; the recovery is "within 5s" if recovery_time - loss_time
<= 5. Denominator = total recoveries (even those with no prior loss
inside the window) -- matches variable_df11's denominator scoping.
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
    variable_ps7["recoveries_within_5s"] / variable_ps7["total_recoveries"] * 100.0,
    np.nan,
)

variable_ps7 = variable_ps7[
    ["game_id", "team_id", "total_recoveries", "recoveries_within_5s", "counter_press_Success_Rate_%"]
]

variable_ps = variable_ps.merge(
    variable_ps7[["game_id", "team_id", "counter_press_Success_Rate_%"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    variable_ps8["progressive_passes_after_loss"] / variable_ps8["total_passes_after_loss"],
    np.nan,
)

variable_ps8 = variable_ps8[
    ["game_id", "team_id", "total_passes_after_loss", "progressive_passes_after_loss", "transition_vulnerability_index"]
]

variable_ps = variable_ps.merge(
    variable_ps8[["game_id", "team_id", "transition_vulnerability_index"]],
    on=["game_id", "team_id"],
    how="left",
)

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
# Recovery events (same set as variable_ps11_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1, ref line 818)
#   type_id 8   Interception             (Opta outcome always 1, ref line 772
#                                         of Opta-f24_appendices.md; verified
#                                         empirically on 1955764.json: 21/21
#                                         type-8 events with outcome=1)
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
# Opposition swap: for team T in game G, variable_ps9 carries the
# other team's count in `opposition_final_third_entries_10s`. Same
# self-merge pattern as variable_ps6_code.py.
#
# NaN preservation: the post-merge `fillna(0)` is intentionally NOT
# applied. The Z-score pipeline can't distinguish "opponent had 0 fast
# transitions" (a legitimate league extreme) from "team was missing
# entirely from progcarry_df" — a 0 in the second case sits at the
# league mean and biases the Z. Same reasoning as the rest of the
# defensive-metric suite (e.g. perdas_posse_linha_baixa.py).

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
# the box. Direct analog of variable_ps14_code.py with the final-third
# zone replaced by the penalty box.
#
# Recovery events (same set as variable_ps11_code.py / variable_ps14_code.py):
#   type_id 49  Ball recovery            (Opta outcome always 1, ref line 818)
#   type_id 8   Interception             (Opta outcome always 1, ref line 772
#                                         of Opta-f24_appendices.md; verified
#                                         empirically on 1955764.json: 21/21
#                                         type-8 events with outcome=1)
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
# variable_ps14_code.py: count fast-transition recoveries per team,
# then swap so team T's row carries the OPPONENT's count.
#
# NaN preservation: the post-merge `fillna(0)` is intentionally NOT
# applied. The Z-score pipeline can't distinguish "opponent had 0 fast
# box entries" (a legitimate league extreme) from "team was missing
# entirely from progcarry_df" — a 0 in the second case sits at the
# league mean and biases the Z. Same reasoning as the rest of the
# defensive-metric suite (e.g. variable_ps14_code.py).

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

Open-play scope: type_id 11 (Claim) is excluded. GK claims are a
different mechanic from outfield ball-winning; the post-claim play is
typically a deliberate slow build-up rather than the fast transition
this metric is designed to capture. Mirrors the convention adopted in
high_recoveries_%.py (variable_ps2) and counter_press_success_rate(%).py
(variable_ps7).

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

variable_ps11 = _own_half_counts.merge(
    _progression_stats,
    on=["game_id", "team_id"],
    how="left",
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

Recovery events (canonical mask, shared with Vars 7/11 -- both of
which also drop type 11 for open-play scope):
  type_id 49  Ball recovery            (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True
  type_id 8   Interception             (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True

Open-play scope: type_id 11 (Claim) is excluded. GK claims are a
different mechanic from outfield ball-winning, and post-claim play is
typically GK distribution rather than the reactive counter-attacking
intent this metric is designed to measure. Mirrors the convention
adopted in high_recoveries_%.py (variable_ps2),
counter_press_success_rate(%).py (variable_ps7), and
time_progression_after_own_half_recovery(s).py (variable_ps11).

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
    variable_ps12["forward_first_passes"] / variable_ps12["recoveries_with_pass"] * 100,
    np.nan,
)

variable_ps12 = variable_ps12[
    ["game_id", "team_id", "recoveries_with_pass", "forward_first_passes", "first_pass_forward_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps12[["game_id", "team_id", "first_pass_forward_pct"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 13
# Final third entries within 10s after own half recovery %
"""Final-third entries within 10s after own-half recovery % is the share
of a team's own-half recoveries that lead to a final-third entry within
10 seconds. Same mechanism as MatchAnalysis_PlayStyle_2026.py
variable_df14 (opposition view) / variable_df21 (own-team view); this
file is the own-team view restricted to recoveries that started in the
team's own half (start_x < 50). Drops type 11 (Claim) for play-style
scope -- see open-play scope note below.

Own-half recovery events (canonical mask + start_x < 50):
  type_id 49  Ball recovery            (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True (wins possession)
  type_id 8   Interception             (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True (wins the aerial duel)

Open-play scope: type_id 11 (Claim) is excluded -- this diverges from
the df14 / df21 reference (which keep it). GK claims are a different
mechanic from outfield ball-winning, and a within-10s FT entry after a
GK claim reflects GK distribution rather than transition speed.
Mirrors the play-style family convention adopted in
high_recoveries_%.py (variable_ps2),
counter_press_success_rate(%).py (variable_ps7),
time_progression_after_own_half_recovery(s).py (variable_ps11), and
first_pass_forward_%.py (variable_ps12).

Final-third entry event: any event with end_x >= 200/3 (~66.67). Opta
F24 Appendix 11 normalizes every event left-to-right in the event
team's attacking direction, so end_x >= 2/3 is always the event team's
attacking third. The old code's two disjunctions (crossed-in OR
already-in) simplify algebraically to this single condition. No
outcome filter: the ball entered the final third, which is what the
metric measures -- transition reach, not transition success. Same
end-coordinate convention as MatchAnalysis variable_df14 / df21.

Window: 10 seconds only. No possession-continuity (next-loss) guard --
follows the MatchAnalysis variable_df14 / df21 convention for
"after-recovery within Ns" rate metrics. The 10s window is tight
enough that lost-and-regained possessions within it are rare; adding
a loss boundary would diverge from the canonical MA pattern without
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
    variable_ps13["final_third_entries"] / variable_ps13["own_half_recoveries"] * 100,
    np.nan,
)

variable_ps13 = variable_ps13[
    ["game_id", "team_id", "own_half_recoveries", "final_third_entries", "final_third_entries_10s_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps13[["game_id", "team_id", "final_third_entries_10s_pct"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 14
# Box entries within 10s after attacking half recovery %
"""Box entries within 10s after attacking-half recovery % is the share
of a team's attacking-half recoveries (high-press wins with start_x >=
50) that lead to a penalty-box entry within 10 seconds. Same mechanism
as MatchAnalysis_PlayStyle_2026.py variable_df15 (opposition view) /
variable_df22 (own-team view); this file is the own-team view
restricted to recoveries that started in the team's attacking half
(start_x >= 50), and outputs a percentage. Drops type 11 (Claim) for
play-style scope -- see open-play scope note below.

Attacking-half recovery events (canonical mask + start_x >= 50):
  type_id 49  Ball recovery            (Opta outcome always 1)
  type_id 7   Tackle,     outcome=True (wins possession)
  type_id 8   Interception             (Opta outcome always 1)
  type_id 44  Aerial,     outcome=True (wins the aerial duel)

Open-play scope: type_id 11 (Claim) is excluded -- this diverges from
the df15 / df22 reference (which keep it). GK claims are a different
mechanic from outfield ball-winning, and would in any case be filtered
out by the start_x >= 50 attacking-half restriction in nearly every
case (Opta normalizes left-to-right in the event team's attacking
direction, so a GK claim has start_x ~ 0-10). Listed as DROPPED for
consistency with the play-style family convention adopted in
high_recoveries_%.py (variable_ps2),
counter_press_success_rate(%).py (variable_ps7),
time_progression_after_own_half_recovery(s).py (variable_ps11),
first_pass_forward_%.py (variable_ps12), and
final_third_entries_within_10s_after_own_half_recovery(%).py
(variable_ps13).

Penalty box (Opta F24 Appendix 11): x >= 83.0 and 21.1 <= y <= 78.9.
A box-entry event is any event whose END coordinates land in the box.
The old code's disjunction "crossed into box OR both ends in box"
simplifies algebraically to this single condition. No outcome filter:
the ball reached the box, which is the territorial signal the metric
measures -- same end-coordinate convention as MA variable_df15 / df22.

Self-pairing: allow_exact_matches=True lets a recovery whose own event
already lands in the box (e.g. a tackle won or interception inside the
opp box itself) self-pair at delta=0 and count as a successful fast
box entry. Winning the ball in the box is the ultimate fast transition;
MA Vars 15 / 22 document and rely on this behavior.

Window: 10 seconds only. No possession-continuity (next-loss) guard --
follows the MA variable_df14/15/21/22 canonical pattern for
"after-recovery within Ns" rate metrics (see Var 13 docstring for
rationale).

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
    variable_ps14["box_entries"] / variable_ps14["attacking_half_recoveries"] * 100,
    np.nan,
)

variable_ps14 = variable_ps14[
    ["game_id", "team_id", "attacking_half_recoveries", "box_entries", "box_entries_10s_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps14[["game_id", "team_id", "box_entries_10s_pct"]],
    on=["game_id", "team_id"],
    how="left",
)

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
Denominator: all chains for that team-game

Chain duration is derived from progcarry_chains_df as max(time) -
min(time) per chain, same source and arithmetic as the possession
dataframe earlier in the pipeline.

Note on possession chain coverage: possession_chain.py has no
MIN_CHAIN_LEN logic -- it does not exclude short chains, so this
metric counts every chain (including any single-event chains) for
that team-game. The previous implementation filtered possessionId
!= 0, which silently dropped only the very first chain of the
entire parquet (one chain in one game out of ~380); removed for
cleanliness. A single-event chain contributes 0 duration so it
trivially fails the 5s threshold and only affects the denominator.
"""

RETENTION_THRESHOLD_SECONDS = 5.0

_chain_time_v15 = progcarry_chains_df["minute"] * 60 + progcarry_chains_df["second"]
_chain_durations_v15 = (
    progcarry_chains_df.assign(_time=_chain_time_v15)
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
    variable_ps15["retained_possessions_5s"] / variable_ps15["total_valid_possessions"] * 100,
    np.nan,
)

variable_ps15 = variable_ps15[
    ["game_id", "team_id", "total_valid_possessions", "retained_possessions_5s", "retained_possessions_5s_pct"]
]

variable_ps = variable_ps.merge(
    variable_ps15[["game_id", "team_id", "retained_possessions_5s_pct"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
# Variáveis
# ATTACK
# 16
# Long ball (%)
"""Long ball % is the percentage of a team's successful open-play passes
that are long balls (qualifier 1 present), per team per game. Indicates
a preference for direct, vertical play that bypasses the midfield.

Companion to bola_longa(%).py (variable_df27, in Ataque\ subdirectory) --
same successful-only choice and same set-piece policy. This file is the
play-style copy living in the project root.
"""

# Per team per game, the share of the team's SUCCESSFUL OPEN-PLAY
# passes that are long balls. Opta F24 Appendix defines a long ball
# as a pass over 35 yards (reference/Opta-f24_appendices.md line 138),
# flagged by qualifier 1 on a type_id == 1 Pass event. "Longball" is
# a presence-only qualifier -- no value attached -- so the predicate
# is "qualifier 1 is present on the pass row", not "qualifier 1
# equals True".
#
# Successful-only choice: the metric definition is ambiguous between
# "share of all passes" and "share of successful passes". Original
# code used successful-only and downstream consumers expect that, so
# the rewrite keeps it. Mirrors variable_df27. (For an all-passes
# variant, drop the outcome gate from both numerator and denominator.)
#
# Set-piece policy (mirrors variable_df27): exclude qualifiers
#   5   (Free kick taken)
#   6   (Corner taken)
#   107 (Throw-in)
# but KEEP qualifier 124 (Goal kick). Goal kicks ARE the direct-vs-
# possession signal this metric is designed to capture. Free kicks,
# corners, and throw-ins are pre-planned restart deliveries by a
# specialist taker and do not reflect the team's in-play tactical
# preference. Without this filter, teams that take many long set-piece
# deliveries get inflated long-ball percentages.
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
# NaN preservation: teams with zero open-play successful passes (a
# degenerate case) keep NaN through the np.where guard AND the left
# merge into variable_ps. Filling 0 here would bias the Z-score
# downward (long ball % natural range is 8-25%, neutral ~15).

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

SET_PIECE_QUALIFIERS = (5, 6, 107)  # FK taken, corner taken, throw-in -- KEEP 124 (goal kicks)

_is_set_piece = progcarry_df["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in SET_PIECE_QUALIFIERS)
)
_pass_mask = (_type_id == 1) & _outcome & ~_is_set_piece

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

variable_ps = variable_ps.merge(
    variable_ps16[["game_id", "team_id", "long_ball_%"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    The loss merge uses allow_exact_matches=True so a FAILED goal kick
    (which is itself in the canonical loss mask) pairs with itself,
    giving window_end = kick_time and correctly excluding subsequent
    same-team passes after opposition's brief possession from being
    attributed to that failed kick. The next-kick merge keeps
    allow_exact_matches=False (a kick is not its own next-kick).
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
# allow_exact_matches=True so a FAILED goal kick (itself in the loss
# mask) pairs with itself -> window_end = kick_time -> no subsequent
# regained-possession passes get attributed to it. A successful kick
# is NOT in the loss mask, so its self-pair is unaffected.
_gk_next_loss = pd.merge_asof(
    _goal_kicks_v17,
    _losses_v17,
    left_on="kick_time",
    right_on="loss_time",
    by=["game_id", "team_id", "period_id"],
    direction="forward",
    allow_exact_matches=True,
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
    variable_ps17["successful_buildups"] / variable_ps17["total_goal_kicks"] * 100,
    np.nan,
)

variable_ps17 = variable_ps17[
    ["game_id", "team_id", "total_goal_kicks", "successful_buildups", "buildup_%"]
]

variable_ps = variable_ps.merge(
    variable_ps17[["game_id", "team_id", "buildup_%"]],
    on=["game_id", "team_id"],
    how="left",
)

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

`progressive_pass` column source: MatchAnalysis_PlayStyle_2026.py
infrastructure (line ~463), which defines progressive = (type_id==1)
& (pass_length >= 10m) & (forward_progress_ratio >= 25%).
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
    variable_ps18["progressive_middle_third_passes"] / variable_ps18["total_middle_third_passes"] * 100,
    np.nan,
)

variable_ps18 = variable_ps18[
    ["game_id", "team_id", "total_middle_third_passes", "progressive_middle_third_passes", "progressive_passes_%"]
]

variable_ps = variable_ps.merge(
    variable_ps18[["game_id", "team_id", "progressive_passes_%"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    variable_ps19["total_crosses"] / variable_ps19["total_final_third_entries"],
    np.nan,
)

variable_ps19 = variable_ps19[
    ["game_id", "team_id", "total_crosses", "total_final_third_entries", "crosses_per_final_third_entry"]
]

variable_ps = variable_ps.merge(
    variable_ps19[["game_id", "team_id", "crosses_per_final_third_entry"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    variable_ps20["total_final_third_dribbles"] / variable_ps20["total_final_third_entries"],
    np.nan,
)

variable_ps20 = variable_ps20[
    ["game_id", "team_id", "total_final_third_dribbles", "total_final_third_entries", "dribbles_per_final_third_entry"]
]

variable_ps = variable_ps.merge(
    variable_ps20[["game_id", "team_id", "dribbles_per_final_third_entry"]],
    on=["game_id", "team_id"],
    how="left",
)

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

Box-entry events (denominator): successful OPEN-PLAY passes or carries
that bring the ball IN from outside the box:
  type_id IN {1, 1000, 2000} & outcome == 1
  & (start NOT in box) & (end in box)
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
The "NOT in box at start" clause restricts to crossing-the-boundary
events, consistent with Var 19's final-third-entry semantics, and
excludes intra-box passes from the denominator (they do not
represent a new entry moment). Both numerator and denominator are
scoped to OPEN PLAY (no set-piece deliveries) so the metric reads
as "% of open-play box entries that came from open-play crosses",
a pure tactical-mix signal.

Carry types: type_id 1000 (progressive carry) and 2000 (regular
carry) are MUTUALLY EXCLUSIVE in the MA infrastructure (orchestrator
line 293: `np.where(prog_carry == 1, 1000, 2000)`; line 241 explicitly
documents the mutual exclusivity). The denominator includes BOTH so
it captures every carry-led box entry, not just the non-progressive
ones. The project-wide [1, 2000] default silently undercounts the
long-distance carry-led entries that are MOST likely to cross the
box boundary.

Cross-entry events (numerator): successful open-play crosses crossing
the box boundary:
  (type_id == 1) & outcome == 1 & qualifier 2 (Cross)
  & (start NOT in box) & (end in box)
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
Crosses are by definition pass events (type_id == 1) -- carries
cannot be crosses, so 1000/2000 are not in the numerator type mask.
The set-piece exclusion now matches the denominator (see above);
corners would also fail the "start not in box" clause anyway (they
originate at x~=100, in box), so excluding them is mostly redundant
but kept explicit for consistency.

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
  (6) Carry types broadened: was [1, 2000] (passes + REGULAR carries
      only); now [1, 1000, 2000] (passes + ALL carries). 1000 and 2000
      are mutually exclusive type_ids in the MA infrastructure, so the
      prior mask silently missed every progressive-carry box entry.
  (7) Set-piece exclusion symmetrized: applied to BOTH numerator and
      denominator so the metric is "% of open-play box entries that
      came from open-play crosses". Previously only the numerator
      excluded set-pieces; teams with many set-piece deliveries got
      artificially low percentages because those entries swelled the
      denominator without contributing to the numerator.
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
    progcarry_df["type_id"].isin([1, 1000, 2000])
    & _outcome_v21
    & ~_is_set_piece_v21
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
    variable_ps21["box_entries_from_crosses_count"] / variable_ps21["total_box_entries"] * 100,
    np.nan,
)

variable_ps21 = variable_ps21[
    ["game_id", "team_id", "total_box_entries", "box_entries_from_crosses_count", "box_entries_from_crosses"]
]

variable_ps = variable_ps.merge(
    variable_ps21[["game_id", "team_id", "box_entries_from_crosses"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
# Variáveis
# 22
# Box entries from carries %
"""Box entries from carries % is the share of a team's open-play
penalty-box entries that occur via a player carrying or dribbling the
ball over the box boundary, rather than passing it in. Companion
metric to Var 21 (box entries from crosses); uses the SAME denominator
so the two metrics are directly comparable and sum to <= 100%, with
the residual being non-cross open-play passes that cross the boundary.

Penalty box (Opta F24 Appendix 11): x >= 83.0 AND 21.1 <= y <= 78.9.

Box-entry events (denominator, same as Var 21): successful OPEN-PLAY
passes or carries crossing the box boundary:
  type_id IN {1, 1000, 2000} & outcome == 1
  & (start NOT in box) & (end in box)
  AND NOT qualifier 5   (Free kick taken)
  AND NOT qualifier 6   (Corner taken)
  AND NOT qualifier 107 (Throw-in)
Both numerator and denominator are scoped to OPEN PLAY, matching
Var 21, so the metric reads as "% of open-play box entries that came
from open-play carries or take-ons".

Carry-entry events (numerator): ball-carrying mechanisms crossing the
box boundary. Three event types qualify:
  - Progressive carries: type_id == 1000 & outcome == 1
  - Regular carries:     type_id == 2000 & outcome == 1
    (Both are synthetic events built by the MA infrastructure;
    progressive and regular carries are MUTUALLY EXCLUSIVE per
    orchestrator line 293: `np.where(prog_carry == 1, 1000, 2000)`,
    explicitly documented at line 241.)
  - Successful take-ons: type_id == 3 & outcome == 1
    (Opta F24 Appendix 1 -- dribble past an opponent; can never be
    a set-piece, so the open-play filter is a no-op for take-ons.)
  All require (start NOT in box) & (end in box) and the same set-
  piece exclusion as the denominator (open-play scope).

Fixes versus the prior implementation:
  (1) type_id == 4 used for dribbles in the old code -- that is Foul
      in Opta F24 Appendix 1, NOT a dribble. The correct dribble/take-
      on event is type_id == 3. Same bug existed in Var 20.
  (2) The old code ran on progcarry_df2 (passes-only). Carries (type
      1000 / 2000) and take-ons (type_id == 3) are NOT passes and
      therefore absent from progcarry_df2 -- the numerator was
      silently always zero.
  (3) Box threshold computed from data (min_x + 0.83*pitch_length)
      replaced with canonical 83.0.
  (4) Missing Y constraint added: old "end_x >= threshold" counted
      corner-flag-area events as box entries. Opta penalty area
      requires 21.1 <= y <= 78.9.
  (5) Denominator now matches Var 21 exactly (passes + ALL carries
      crossing the boundary, set-pieces excluded) so the two metrics
      can be summed coherently as a shares-of-entries decomposition.
  (6) Carry types broadened to {1000, 2000} (was {2000} only). An
      earlier patch claimed type_id 1000 was "not a valid Opta F24
      event ID" and removed it from the mask; that claim conflated
      Opta's native type_ids (1-65) with the MA infrastructure's
      synthetic types (1000/2000), and silently excluded every
      progressive-carry box entry. Re-verified on the orchestrator
      (lines 241/293) and added back; same broadening applied to the
      denominator.
  (7) Set-piece exclusion added on BOTH numerator and denominator
      (open-play scope), matching Var 21. Take-ons cannot be set-
      pieces so the filter is a no-op for them; on passes/carries it
      removes pre-planned restart deliveries that don't reflect the
      team's in-play tactical pattern.
"""

BOX_X = 83.0
BOX_Y_MIN = 21.1
BOX_Y_MAX = 78.9

_outcome_v22 = progcarry_df["outcome"].astype(bool)
_is_set_piece_v22 = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107)
)

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
    progcarry_df["type_id"].isin([1, 1000, 2000])
    & _outcome_v22
    & ~_is_set_piece_v22
    & ~_start_in_box_v22
    & _end_in_box_v22
)

_carry_entry_mask_v22 = (
    progcarry_df["type_id"].isin([3, 1000, 2000])
    & _outcome_v22
    & ~_is_set_piece_v22
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
    variable_ps22["box_entries_from_carries_count"] / variable_ps22["total_box_entries"] * 100,
    np.nan,
)

variable_ps22 = variable_ps22[
    ["game_id", "team_id", "total_box_entries", "box_entries_from_carries_count", "box_entries_from_carries"]
]

variable_ps = variable_ps.merge(
    variable_ps22[["game_id", "team_id", "box_entries_from_carries"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    variable_ps23["shots_from_sustained_attacks"] / variable_ps23["total_shots"] * 100,
    np.nan,
)

variable_ps23 = variable_ps23[
    ["game_id", "team_id", "total_shots", "shots_from_sustained_attacks", "sustained_attacks"]
]

variable_ps = variable_ps.merge(
    variable_ps23[["game_id", "team_id", "sustained_attacks"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    variable_ps24["shots_from_direct_attacks"] / variable_ps24["total_shots"] * 100,
    np.nan,
)

variable_ps24 = variable_ps24[
    ["game_id", "team_id", "total_shots", "shots_from_direct_attacks", "direct_attack"]
]

variable_ps = variable_ps.merge(
    variable_ps24[["game_id", "team_id", "direct_attack"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    variable_ps25["total_shots"] / variable_ps25["final_third_passes"],
    np.nan,
)

variable_ps25 = variable_ps25[
    ["game_id", "team_id", "total_shots", "final_third_passes", "shots_per_final_third_pass"]
]

variable_ps = variable_ps.merge(
    variable_ps25[["game_id", "team_id", "shots_per_final_third_pass"]],
    on=["game_id", "team_id"],
    how="left",
)

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
    variable_ps26["outside_box_shots"] / variable_ps26["total_shots"] * 100,
    np.nan,
)

variable_ps26 = variable_ps26[
    ["game_id", "team_id", "total_shots", "outside_box_shots", "shots_outside_box"]
]

variable_ps = variable_ps.merge(
    variable_ps26[["game_id", "team_id", "shots_outside_box"]],
    on=["game_id", "team_id"],
    how="left",
)

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

# Since all NaN are 0...
# 1. Replace all NaN with 0 (since you confirmed NaN means zero in your data)
variable_ps_new = variable_ps_new.fillna(0)


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

# Add "Temporada" column with the value 2026 as the first column in the dataframe
variable_ps_new.insert(0, "Temporada", 2026)


###########################################################################
###########################################################################

# Building round column
# Numbering rounds
# 1. Load the rounds reference file and keep only the keys we need
rodada_df = pd.read_excel('rodada_2026.xlsx')[['game_id', 'round']]

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

