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
columns.remove('team_name')         # Remove 'time' from its current position
columns.insert(4, 'team_name')      # Insert 'time' as the ninth column (index 8)

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

# Possession chains, distances, angles, and possession time
#
# Builds the following columns on progcarry_df:
#   - possessionId    : per-(game_id, team_id) sequential id (1..N) for each
#                       contiguous same-team run of >= 2 events. Events that
#                       fall in runs shorter than 2 get possessionId = 0.
#   - first_chain     : 1 on the first event of each valid possession, else 0.
#   - last_chain      : 1 on the last event of each valid possession, else 0.
#   - distance        : event displacement in meters (UEFA pitch: 105 x 68 m).
#   - angle           : "forwardness" in [0, pi]; pi = pure forward,
#                       0 = pure backward, pi/2 = sideways.
#   - possession_time : total seconds of the possession, written only on the
#                       last_chain row of each valid possession.
#
# Also returns a view progcarry_chains_df = progcarry_df[possessionId != 0],
# so possession-scoped downstream metrics can use it without progcarry_df
# being destructively filtered.
#
# Opta F24 coordinate note (reference/Opta-f24_appendices.md, Appendix 11
# line 950): start_x/y and end_x/y are 0-100 percentages on a pitch whose
# physical length is ~105 m (x) and width is ~68 m (y). Distances and
# angles must scale each axis to meters before combining.

PITCH_LENGTH_M = 105.0  # UEFA standard length (x-axis)
PITCH_WIDTH_M  = 68.0   # UEFA standard width  (y-axis)
MIN_CHAIN_LEN  = 2      # per task spec: chain of >= 2 events by the same team

# --------------------------------------------------------------------------
# 0. Sort chronologically before any shift / loop work
# --------------------------------------------------------------------------
progcarry_df = progcarry_df.sort_values(
    ["game_id", "period_id", "event_index"]
).reset_index(drop=True)

# --------------------------------------------------------------------------
# 1. possessionId — contiguous same-team runs, broken on game/period/team
# --------------------------------------------------------------------------
game_shift   = progcarry_df["game_id"].shift()
period_shift = progcarry_df["period_id"].shift()
team_shift   = progcarry_df["team_id"].shift()

# New chain starts when game OR period OR team changes. `ne` treats NaN as
# unequal, so the first row of the dataframe is also flagged as a new chain.
new_chain = (
    progcarry_df["game_id"].ne(game_shift)
    | progcarry_df["period_id"].ne(period_shift)
    | progcarry_df["team_id"].ne(team_shift)
)
raw_chain_id = new_chain.cumsum()

# Events in raw chains shorter than MIN_CHAIN_LEN get possessionId = 0.
chain_sizes = raw_chain_id.map(raw_chain_id.value_counts())
valid_chain_mask = chain_sizes >= MIN_CHAIN_LEN

# For valid chains, number them 1..N within each (game_id, team_id).
valid_chain_lookup = (
    progcarry_df.loc[valid_chain_mask]
    .assign(_raw=raw_chain_id[valid_chain_mask])
    [["game_id", "team_id", "_raw"]]
    .drop_duplicates("_raw")
)
valid_chain_lookup["possessionId"] = (
    valid_chain_lookup.groupby(["game_id", "team_id"]).cumcount() + 1
)
raw_to_possession = dict(
    zip(valid_chain_lookup["_raw"], valid_chain_lookup["possessionId"])
)

progcarry_df["possessionId"] = (
    raw_chain_id.map(raw_to_possession).fillna(0).astype(int)
)

# --------------------------------------------------------------------------
# 2. first_chain and last_chain — boundary markers for each valid chain
# --------------------------------------------------------------------------
prev_game   = progcarry_df["game_id"].shift(1)
prev_period = progcarry_df["period_id"].shift(1)
prev_team   = progcarry_df["team_id"].shift(1)
next_game   = progcarry_df["game_id"].shift(-1)
next_period = progcarry_df["period_id"].shift(-1)
next_team   = progcarry_df["team_id"].shift(-1)

in_chain = progcarry_df["possessionId"] != 0

# first_chain: chain boundary at the start (or first row of dataframe).
progcarry_df["first_chain"] = (
    in_chain
    & (
        progcarry_df["game_id"].ne(prev_game)
        | progcarry_df["period_id"].ne(prev_period)
        | progcarry_df["team_id"].ne(prev_team)
    )
).astype(int)

# last_chain: chain boundary at the end. Includes end-of-period, end-of-game,
# and the very last row of the dataframe — previously these were silently
# dropped, so half-ending possessions got possession_time = 0.
progcarry_df["last_chain"] = (
    in_chain
    & (
        progcarry_df["game_id"].ne(next_game)
        | progcarry_df["period_id"].ne(next_period)
        | progcarry_df["team_id"].ne(next_team)
    )
).astype(int)

# --------------------------------------------------------------------------
# 3. distance — event displacement in meters, UEFA-scaled
# --------------------------------------------------------------------------
# For point-events where start == end (tackles, interceptions, fouls), fall
# back to the previous event's end coordinates — BUT only when that previous
# event was the same team in the same period and same game. The original
# code had these guards commented out, which pulled "start" coordinates from
# the opponent's last event on the other half of the pitch.
prev_end_x = progcarry_df["end_x"].shift(1)
prev_end_y = progcarry_df["end_y"].shift(1)

zero_displacement = (
    (progcarry_df["start_x"] == progcarry_df["end_x"])
    & (progcarry_df["start_y"] == progcarry_df["end_y"])
)
same_context = (
    (progcarry_df["team_id"] == prev_team)
    & (progcarry_df["period_id"] == prev_period)
    & (progcarry_df["game_id"] == prev_game)
)
use_fallback = zero_displacement & same_context

start_x_eff = np.where(use_fallback, prev_end_x, progcarry_df["start_x"])
start_y_eff = np.where(use_fallback, prev_end_y, progcarry_df["start_y"])

dx_m = (progcarry_df["end_x"] - start_x_eff) * (PITCH_LENGTH_M / 100.0)
dy_m = (progcarry_df["end_y"] - start_y_eff) * (PITCH_WIDTH_M  / 100.0)
progcarry_df["distance"] = np.hypot(dx_m, dy_m)

# --------------------------------------------------------------------------
# 4. angle — progress angle in [0, pi]; computed in meter-scaled coordinates
#    so that x/y asymmetry doesn't distort the direction.
# --------------------------------------------------------------------------
raw_angle = np.pi - np.abs(np.arctan2(dy_m, dx_m))
progcarry_df["angle"] = np.where(
    progcarry_df["distance"] > 0, raw_angle, 0.0
)

# --------------------------------------------------------------------------
# 5. possession_time — duration of each valid possession, written on its
#    last_chain row (downstream code sums these with last_chain == 1).
# --------------------------------------------------------------------------
progcarry_df["possession_time"] = 0

if in_chain.any():
    chain_time_stats = (
        progcarry_df.loc[in_chain]
        .groupby(["game_id", "team_id", "possessionId"])["time"]
        .agg(min_time="min", max_time="max")
        .reset_index()
    )
    chain_time_stats["duration"] = (
        chain_time_stats["max_time"] - chain_time_stats["min_time"]
    )

    last_rows_mask = in_chain & (progcarry_df["last_chain"] == 1)
    merged = (
        progcarry_df.loc[last_rows_mask, ["game_id", "team_id", "possessionId"]]
        .merge(
            chain_time_stats[["game_id", "team_id", "possessionId", "duration"]],
            on=["game_id", "team_id", "possessionId"],
            how="left",
        )
    )
    progcarry_df.loc[last_rows_mask, "possession_time"] = merged["duration"].values

# --------------------------------------------------------------------------
# 6. Non-destructive chain-only view for downstream possession-scoped metrics
# --------------------------------------------------------------------------
progcarry_chains_df = progcarry_df[progcarry_df["possessionId"] != 0].copy()


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

# Create the "cross" column
passes_df["cross"] = passes_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(2, False) else 0
)

###############################################################################

# Create the "header" column
passes_df["header"] = passes_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(3, False) else 0
)

###############################################################################

# Create the "through" column
passes_df["through"] = passes_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(4, False) else 0
)

###############################################################################

# Create the "open_play" column
passes_df["open_play"] = passes_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(22, False) else 0
)

###############################################################################

# Create the "set_piece" column
passes_df["set_piece"] = passes_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(24, False) else 0
)

###############################################################################

# Create the "corner" column
passes_df["corner"] = passes_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(25, False) else 0
)

###############################################################################

# Create the "throw_in" column
passes_df["throw_in"] = passes_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(160, False) else 0
)

###############################################################################

# Create the target_xA column
passes_df["target_xA"] = (
    (passes_df["period_id"] == passes_df["period_id"].shift(-1)) &  # Same period as the next row
    (passes_df["team_id"] == passes_df["team_id"].shift(-1)) &      # Same team as the next row
    (passes_df["type_id"] == 1) &                                  # Current row's type_id is 1
    (passes_df["type_id"].shift(-1) == 16)                         # Next row's type_id is 16
).astype(int)


###############################################################################
###############################################################################

#Preparing the data
xa_df = passes_df[passes_df["type_id"] == 1].copy()
xa_df = xa_df.iloc[:, np.r_[[0, 2, 3, 4, 5, 6, 31, 29, 32, 33, 34, 35, 36, 37, 38, 43]]]
xa_df.to_csv('xa_df.csv', index=True)
# Load the model for application on other datasets (example)

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np

class StatsmodelsLogitWrapper:
    def __init__(self, sk_model, sk_scaler, feature_names):
        self.sk_model      = sk_model
        self.sk_scaler     = sk_scaler
        self.feature_names = feature_names

    def predict(self, X_with_const):
        if hasattr(X_with_const, 'columns'):
            cols  = [c for c in X_with_const.columns if c != 'const']
            X_raw = X_with_const[cols].values
        else:
            X_raw = np.asarray(X_with_const)[:, 1:]
        X_sc = self.sk_scaler.transform(X_raw)
        return self.sk_model.predict_proba(X_sc)[:, 1]

# Now this works:
with open('xA_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)



# Example: Applying the model to a new dataset
X_new = xa_df.iloc[:, np.r_[6:15]]
X_new = sm.add_constant(X_new)
y_new_pred = loaded_model.predict(X_new)

# Concatenate 'best_NonEPL' and 'y_proba' along the columns
y_proba_df = pd.DataFrame(y_new_pred, index=xa_df.index, columns=['xA'])
xa_df = pd.concat([xa_df, y_proba_df], axis=1)

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xG xG xG xG xG xG xG xG xG xG xG xG xG xG xG xG xG xG xG xG xG
#Create shot_df
shot_df = df.copy()

shot_df["head"] = shot_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(15) == True else 0
)

# Create the "foot" column
shot_df["foot"] = shot_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and any(q.get(k, False) == True for k in [20, 72]) else 0
)

# Create the "big_chance" column
shot_df["big_chance"] = shot_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(214) == True else 0
)

# Create the "set_piece" column
shot_df["set_piece"] = shot_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(24) == True else 0
)

# Create the "regular_play" column
shot_df["regular_play"] = shot_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(22) == True else 0
)

# Create the "throw_in" column
shot_df["throw_in"] = shot_df["qualifiers"].apply(
    lambda q: 1 if isinstance(q, dict) and q.get(160) == True else 0
)

# Create the "type_assist" column
shot_df["type_assist"] = shot_df.apply(
    lambda row: shot_df.loc[row.name - 1, "type_name"] 
    if row["type_id"] in [13, 14, 15, 16] and isinstance(row["qualifiers"], dict) and 29 in row["qualifiers"] and row.name > 0 
    else None,
    axis=1
)

# Adjust start_y column
shot_df["start_y"] = abs(50 - shot_df["start_y"])

#Dummyfying type_assist column
# Generate dummy columns from the "type_assist" column
dummies = pd.get_dummies(shot_df["type_assist"], prefix="assist", drop_first=True).astype(int)

# Define the columns to retain
columns_to_keep = ["assist_ball recovery", "assist_ball touch", "assist_challenge", 
                   "assist_error", "assist_pass", "assist_take on"]

# Filter the dataframe to exclude other "assist" prefixed columns
dummies = dummies[columns_to_keep]

# Concatenate the dummy columns to the original dataframe
shot_df = pd.concat([shot_df, dummies], axis=1)


# Create the shot_angle column
# Define the goal posts' coordinates (assuming standard soccer field dimensions)
goal_post_A = (100, 36)  # Left goal post (x=100, y=36)
goal_post_C = (100, 64)  # Right goal post (x=100, y=64)

# Calculate the angle for each shot
def calculate_shot_angle(shot_x, shot_y, goal_post_A, goal_post_C):
    # Vectors from shot location O to goal posts A and C
    vector_A = np.array([goal_post_A[0] - shot_x, goal_post_A[1] - shot_y])
    vector_C = np.array([goal_post_C[0] - shot_x, goal_post_C[1] - shot_y])
    
    # Calculate the angle using dot product and cross product
    dot_product = np.dot(vector_A, vector_C)
    cross_product = np.abs(np.cross(vector_A, vector_C))
    
    # Calculate the angle in radians and convert to degrees
    angle_radians = np.arctan2(cross_product, dot_product)
    
    return angle_radians

# Apply the function to calculate angles for all shots
shot_df["shot_angle"] = shot_df.apply(
    lambda row: calculate_shot_angle(row["start_x"], row["start_y"], goal_post_A, goal_post_C),
    axis=1
)

# Create the "target_xG" column
shot_df["target_xG"] = shot_df["type_id"].apply(lambda x: 1 if x == 16 else (0 if x in [13, 14, 15] else None))

# Copy the "start_x" column and rename it as "pass_start_x", adding it to the end of the DataFrame
shot_df["shot_start_x"] = shot_df["start_x"]

# Copy the "start_x" column and rename it as "pass_start_x", adding it to the end of the DataFrame
shot_df["shot_start_y"] = shot_df["start_y"]


# Calculate the Euclidean distance to the center of the goal
def calculate_shot_distance(shot_x, shot_y, goal_center=(100, 50)):
    return np.sqrt((goal_center[0] - shot_x)**2 + (goal_center[1] - shot_y)**2)

# Apply the function to calculate distances
shot_df["shot_distance"] = shot_df.apply(
    lambda row: calculate_shot_distance(row["start_x"], row["start_y"]),
    axis=1
)

##########################################################################
##########################################################################

#Preparing the data
# Filter shot events
xg_df2 = shot_df[
    shot_df["type_id"].isin([13, 14, 15, 16]) & 
    ~shot_df["qualifiers"].apply(lambda q: isinstance(q, dict) and 9 in q)
].copy()

##########################################################################


# Selecting columns
xg_df = xg_df2.iloc[:, np.r_[0, 2, 3, 4, 5, 6, 16, 12, 13, 14, 15, 20, 22, 24, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 36]]
xg_df['shot_distance2'] = xg_df['shot_distance']**2

# Load the model for application on other datasets (example)
with open('xG_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

# Example: Applying the model to a new dataset
X_new = xg_df.iloc[:, np.r_[12, 13, 15, 17, 19, 20, 21, 22, 23, 25]]
X_new = sm.add_constant(X_new)
y_new_pred = loaded_model.predict(X_new)

# Concatenate 'xg_df' and 'y_proba' along the columns
y_proba_df = pd.DataFrame(y_new_pred, index=xg_df.index, columns=['xG'])
xg_df = pd.concat([xg_df, y_proba_df], axis=1)


# Calculate overall statistics
#print("\nPressure resistance statistics:")
print(xg_df['xG'].describe())

xg_df.to_csv('xg_df.csv', index=True)
##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###

xthreat_df2 = progcarry_df.copy()

# Create the 'possession_shot' column
def create_possession_shot(df):
    # Group by game_id, team_id, possessionId
    grouped = df.groupby(['game_id', 'team_id', 'possessionId'])

    # Check if "shot" == 1 exists within each group
    df['possession_shot'] = grouped['shot'].transform(lambda x: 1 if x.sum() > 0 else 0)

    return df

xthreat_df2 = create_possession_shot(xthreat_df2)

###############################################################################
###############################################################################

# Create the 'possession_goal' column
def create_possession_goal(df):
    # Group by game_id, team_id, possessionId
    grouped = df.groupby(['game_id', 'team_id', 'possessionId'])

    # Check if "goal" == 1 exists within each group
    df['possession_goal'] = grouped['goal'].transform(lambda x: 1 if x.sum() > 0 else 0)

    return df

xthreat_df2 = create_possession_goal(xthreat_df2)

############################################################################################
############################################################################################

# Fitting the xShot model for possession chain
#Preparing the data
# Selecting columns
xshot_df = xthreat_df2.iloc[:, np.r_[0, 2, 3, 4, 5, 6, 16, 12, 13, 14, 15, 28, 29, 31]]
xshot_df['distance2'] = xshot_df['distance']**2

# Example of using saved model in another script
X_new = xshot_df.iloc[:, np.r_[7, 8, 9, 10, 11, 12, 14]]

def predict_xt(data, base_path='models'):
    with open(f'{base_path}/xt_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open(f'{base_path}/xt_scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)

    scaled_data = scaler.transform(data)
    return model.predict_proba(scaled_data)[:, 1]

xthreat_test_df = predict_xt(X_new, base_path='models')
############################################################################################
############################################################################################

#Creating xThreat column in xthreat_df2
xthreat_df2["xthreat"] = xthreat_test_df

############################################################################################
############################################################################################

# Merge the columns from xthreat_df2 into progcarry_df
progcarry_df = progcarry_df.join(xthreat_df2[["xthreat"]], how="left")

############################################################################################
############################################################################################
progcarry_df["game_id"] = pd.to_numeric(progcarry_df["game_id"], errors="coerce").astype("Int64")

############################################################################################
############################################################################################

# Adding dummies to identify future variables based on actions
progcarry_df2 = progcarry_df.copy()

#Create passes inside final third
progcarry_df2["passes_third"] = (
    ((progcarry_df2["period_id"].eq(progcarry_df2["period_id"].shift(-1))) &
     (progcarry_df2["team_id"].eq(progcarry_df2["team_id"].shift(-1))) &  # Check if team_id matches the next row
     (progcarry_df2["type_id"] == 1) & 
     (progcarry_df2["start_x"] >= 66.66) & 
     (progcarry_df2["end_x"] >= 66.66))
    .astype(int)
)

###############################################################################
###############################################################################

#Create passes into final third
progcarry_df2["passes_into_third"] = (
    ((progcarry_df2["period_id"].eq(progcarry_df2["period_id"].shift(-1))) &
     (progcarry_df2["team_id"].eq(progcarry_df2["team_id"].shift(-1))) &  # Check if team_id matches the next row
     (progcarry_df2["type_id"] == 1) & 
     (progcarry_df2["start_x"] < 66.66) & 
     (progcarry_df2["end_x"] >= 66.66))
    .astype(int)
)

###############################################################################
###############################################################################

#Create passes into final third
progcarry_df2["cross"] = (
    (progcarry_df2["period_id"].eq(progcarry_df2["period_id"].shift(-1))) &
    (progcarry_df2["team_id"].eq(progcarry_df2["team_id"].shift(-1))) &  # Check if team_id matches the next row
    (progcarry_df2["type_id"] == 1) &
    progcarry_df2["qualifiers"].apply(lambda q: isinstance(q, dict) and q.get(2) == True)
).astype(int)

###############################################################################
###############################################################################

#Create progressive passes

# Calculate pass_length
progcarry_df2["pass_length"] = np.sqrt(
    (progcarry_df2["end_x"] - progcarry_df2["start_x"])**2 +
    (progcarry_df2["end_y"] - progcarry_df2["start_y"])**2
)

# Calculate remaining_distance
progcarry_df2["remaining_distance"] = 100 - progcarry_df2["start_x"]

# Calculate progressive_condition
progcarry_df2["progressive_condition"] = (
    (progcarry_df2["end_x"] - progcarry_df2["start_x"]) / progcarry_df2["remaining_distance"]
)

# Create progressive_pass column
progcarry_df2["progressive_pass"] = (
    (progcarry_df2["period_id"].eq(progcarry_df2["period_id"].shift(-1))) &
    (progcarry_df2["team_id"].eq(progcarry_df2["team_id"].shift(-1))) &  # Check if team_id matches the next row
    (progcarry_df2["pass_length"] >= 10) &                             # Check pass_length condition
    (progcarry_df2["progressive_condition"] >= 0.25)                  # Check progressive_condition
).astype(int)

# Drop intermediate columns if they are no longer needed
progcarry_df2.drop(columns=["remaining_distance", "progressive_condition"], inplace=True)

###############################################################################
###############################################################################

# Create the ball_progression column
progcarry_df2["ball_progression"] = (
    (progcarry_df2["period_id"].eq(progcarry_df2["period_id"].shift(-1))) &  # Same period as the next row
    (progcarry_df2["team_id"].eq(progcarry_df2["team_id"].shift(-1))) &      # Same team as the next row
    (progcarry_df2["progressive_pass"] == 1) &                              # Progressive pass condition
    (progcarry_df2["type_id"] == 2000)                                      # Type_id is 2000
).astype(int)

###############################################################################
###############################################################################

# Create the deep_runs column
progcarry_df2["deep_runs"] = (
    (progcarry_df2["period_id"] == progcarry_df2["period_id"].shift(1)) &  # Same period as the previous row
    (progcarry_df2["team_id"] == progcarry_df2["team_id"].shift(1)) &      # Same team as the previous row
    (progcarry_df2["qualifiers"].apply(lambda q: isinstance(q, dict) and q.get(4) == True))  # Include rows where qualifiers key 4 is True
).astype(int)

############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################

# Building possession dataframe
# Filter df_games to include rows corresponding to the specified game_ids
filtered_games = df_schedule[df_schedule['game_id'].isin(game_ids)]

# Create a new dataframe for possession with 'home_team_id' and 'away_team_id'
possession = filtered_games[['game_id', 'home_team_id', 'away_team_id']].copy()

# Merge possession dataframe with df_schedule to get 'home_team' and 'away_team' details
possession = possession.merge(
    df_schedule[['game_id', 'home_team', 'away_team']],
    on='game_id',
    how='left'
)

############################################################################################

# Filter progcarry_df based on the given conditions
filtered_progcarry_df = progcarry_df[(progcarry_df["possessionId"] != 0) & (progcarry_df["last_chain"] == 1)]

# Initialize new columns in possession dataframe
possession["home_team_possession"] = 0
possession["away_team_possession"] = 0

# Iterate over each game_id in possession
for index, row in possession.iterrows():
    game_id = row["game_id"]
    
    # Filter rows in progcarry_df for the current game_id and matching home_team_id
    home_possession_time = filtered_progcarry_df[
        (filtered_progcarry_df["game_id"] == game_id) & 
        (filtered_progcarry_df["team_id"] == row["home_team_id"])
    ]["possession_time"].sum()
    
    # Filter rows in progcarry_df for the current game_id and matching away_team_id
    away_possession_time = filtered_progcarry_df[
        (filtered_progcarry_df["game_id"] == game_id) & 
        (filtered_progcarry_df["team_id"] == row["away_team_id"])
    ]["possession_time"].sum()
    
    # Assign calculated values to the possession dataframe
    possession.at[index, "home_team_possession"] = home_possession_time
    possession.at[index, "away_team_possession"] = away_possession_time

############################################################################################

possession["home_team_possession_per"] = ((possession["home_team_possession"]/(possession["home_team_possession"]+possession["away_team_possession"]))*100).round(2)
possession["away_team_possession_per"] = ((possession["away_team_possession"]/(possession["home_team_possession"]+possession["away_team_possession"]))*100).round(2)

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


progcarry_df.head(100).to_csv('progcarry_df_sample.csv', index=True)
df.head(100).to_csv('df_sample.csv', index=True)

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

filtered_df1 = df.copy()

# Define the conditions for is_defensive_height
filtered_df1["is_defensive_height"] = (
    ((filtered_df1["type_id"] == 4) &  
    (filtered_df1["outcome"] == 1)) |
    ((filtered_df1["type_id"] == 7) |
     (filtered_df1["type_id"] == 8) |
     (filtered_df1["type_id"] == 12)|
     (filtered_df1["type_id"] == 49))
    ).astype(int)

# Filter the DataFrame for rows where is_defensive_height is True
df_defensive = filtered_df1[filtered_df1["is_defensive_height"] == True]

# Group by 'game_id' and 'player_id', then compute the mean of 'start_x'
variable_df1 = (
    df_defensive.groupby(['game_id', 'team_id'], as_index=False)["start_x"]
    .mean()  # Compute the mean of the 'start_x' column
    .rename(columns={'start_x': 'defensive_height'})  # Rename the column for clarity
)

# Importing defensive_height
# Merge variable_df with defensive_height based on team_id
variable_df = variable_df.merge(
    variable_df1[['game_id', 'team_id', 'defensive_height']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "defensive_height" column with 0
variable_df["defensive_height"] = variable_df["defensive_height"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 2
# High Recoveries %
"""Recoveries refer to the number of times a team regains possession of the ball 
after losing it. This can include various scenarios such as intercepting passes, 
winning duels, or collecting loose balls. High Recoveries Refers to the percentage 
of recoveries that take place in the attacking third of the pitch.
"""

def calculate_recoveries(progcarry_df):
    """
    Calculate recoveries and high recoveries for each game_id and team_id.
    High recoveries are defined as recoveries that occur in the attacking third (start_x >= 66.7).
    
    Parameters:
    progcarry_df (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - type_id: identifier for the type of action
        - outcome: outcome of the action (1 for successful)
        - first_chain: 1 if possession chain starts, 0 otherwise
        - start_x: x-coordinate of the action (0-100 scale)
    
    Returns:
    pd.DataFrame: DataFrame containing recovery statistics for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df.copy()
    
    # Define valid recovery conditions
    valid_recoveries = df[
        (df['first_chain'] == 1) &  # Must be start of possession chain
        (
            (df['type_id'] == 8) |  # Interception
            ((df['type_id'] == 7) & (df['outcome'] == 1)) |  # Successful tackle
            (df['type_id'] == 49)  # Ball recovery
        )
    ]
    
    # Initialize list to store recovery stats
    recovery_stats = []
    
    # Get unique combinations of game_id and team_id
    groups = valid_recoveries.groupby(['game_id', 'team_id'])
    total_groups = len(groups)
    
    # Create progress bar
    pbar = tqdm(total=total_groups, desc='Analyzing recoveries')
    
    # Calculate recoveries for each game and team
    for (game_id, team_id), group_data in groups:
        # Count recoveries by type
        recoveries_by_type = group_data['type_id'].value_counts().to_dict()
        
        # Calculate total recoveries
        total_recoveries = len(group_data)
        
        # Calculate high recoveries (in attacking third, start_x >= 66.7)
        high_recoveries = len(group_data[group_data['start_x'] >= 66.7])
        
        # Calculate stats
        stats = {
            'game_id': game_id,
            'team_id': team_id,
            'total_recoveries': total_recoveries,
            'high_recoveries': high_recoveries,
            'interceptions': recoveries_by_type.get(8, 0),
            'successful_tackles': recoveries_by_type.get(7, 0),
            'ball_recoveries': recoveries_by_type.get(49, 0)
        }
        
        # Add location-based statistics
        if 'start_x' in group_data.columns and 'start_y' in group_data.columns:
            # Calculate average recovery position
            stats.update({
                'avg_recovery_x': group_data['start_x'].mean().round(2),
                'avg_recovery_y': group_data['start_y'].mean().round(2)
            })
        
        recovery_stats.append(stats)
        
        # Update progress bar
        pbar.update(1)
    
    # Close progress bar
    pbar.close()
    
    # Create DataFrame with recovery statistics
    recovery_df = pd.DataFrame(recovery_stats)
    
    # Calculate percentages
    if len(recovery_df) > 0:
        # Calculate high recoveries percentage
        recovery_df['high_recoveries_pct'] = (
            recovery_df['high_recoveries'] / recovery_df['total_recoveries'] * 100
        ).round(2)
        
        recovery_df['interceptions_pct'] = (
            recovery_df['interceptions'] / recovery_df['total_recoveries'] * 100
        ).round(2)
        
        recovery_df['successful_tackles_pct'] = (
            recovery_df['successful_tackles'] / recovery_df['total_recoveries'] * 100
        ).round(2)
        
        recovery_df['ball_recoveries_pct'] = (
            recovery_df['ball_recoveries'] / recovery_df['total_recoveries'] * 100
        ).round(2)
    
    # Ensure consistent column order
    columns = [
        'game_id', 'team_id', 'total_recoveries', 'high_recoveries', 'high_recoveries_pct',
        'interceptions', 'successful_tackles', 'ball_recoveries',
        'interceptions_pct', 'successful_tackles_pct', 'ball_recoveries_pct'
    ]
    
    # Add location columns if they exist
    if 'avg_recovery_x' in recovery_df.columns:
        columns.extend(['avg_recovery_x', 'avg_recovery_y'])
    
    recovery_df = recovery_df[columns]
    
    return recovery_df

# Use the updated function to calculate recoveries and high recoveries
variable_df2 = calculate_recoveries(progcarry_df)

# Compute recoveries and high recoveries per team per game
variable_df2 = (
    variable_df2.groupby(["game_id", "team_id"])[["total_recoveries", "high_recoveries", "high_recoveries_pct"]]
    .agg({
        "total_recoveries": "sum",
        "high_recoveries": "sum",
        "high_recoveries_pct": "mean"  # Using mean to preserve the calculated percentage
    })
    .reset_index()
    .rename(columns={
        "total_recoveries": "recoveries",
        "high_recoveries": "high_recoveries",
        "high_recoveries_pct": "high_recoveries_pct"
    })
)

# If you need to recalculate the percentage after grouping:
variable_df2["high_recoveries_pct"] = (variable_df2["high_recoveries"] / variable_df2["recoveries"] * 100).round(2)

# Importing high_recoveries_pct
# Merge variable_df with high_recoveries_pct
variable_df = variable_df.merge(
    variable_df2[['game_id', 'team_id', 'high_recoveries_pct']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "high_recoveries_pct" column with 0
variable_df["high_recoveries_pct"] = variable_df["high_recoveries_pct"].fillna(0)

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

import pandas as pd
import numpy as np

# Step 1: Define a function to determine if an action is in the defensive 60% of the field
def is_in_defensive_60_percent(row):
    # Check if the action occurred in the defensive 60% (start_x between 0 and 60)
    return 0 <= row['start_x'] <= 60

# Create the team-opponent mapping first
# Get unique games and teams to identify opponents
games_teams = progcarry_df[["game_id", "team_id"]].drop_duplicates()
# Create a mapping of teams to their opponents within each game
game_teams_grouped = games_teams.groupby("game_id")["team_id"].apply(list).reset_index()

# Function to find the opponent team_id
def get_opponent(game_id, team_id, game_teams_df):
    teams = game_teams_df.loc[game_teams_df["game_id"] == game_id, "team_id"].iloc[0]
    if len(teams) != 2:
        return None  # Handle cases where there aren't exactly 2 teams
    return teams[0] if teams[1] == team_id else teams[1]

# Create a dataframe with team and opponent mappings
team_opponent_mapping = []
for _, row in games_teams.iterrows():
    opponent = get_opponent(row["game_id"], row["team_id"], game_teams_grouped)
    if opponent:
        team_opponent_mapping.append({
            "game_id": row["game_id"],
            "team_id": row["team_id"],
            "opponent_team_id": opponent
        })
team_opponent_df = pd.DataFrame(team_opponent_mapping)

# Create a copy of progcarry_df with opponent information
df_with_opponents = progcarry_df.merge(
    team_opponent_df,
    on=["game_id", "team_id"],
    how="left"
)

# Filter actions in the defensive 60% of the field
df_in_def_60 = df_with_opponents[
    df_with_opponents.apply(lambda row: is_in_defensive_60_percent(row), axis=1)
]

# Count passes for each team in their defensive 60%
passes = (
    df_in_def_60[df_in_def_60["type_id"] == 1]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="passes_in_def_60")
)

# Count defensive actions for each team in opponent's defensive 60%
tackles = (
    df_in_def_60[df_in_def_60["type_id"] == 7]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="tackles")
)

interceptions = (
    df_in_def_60[df_in_def_60["type_id"] == 8]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="interceptions")
)

fouls = (
    df_in_def_60[df_in_def_60["type_id"] == 4]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="fouls")
)

# Merge defensive actions into one dataframe
defensive_actions = (
    tackles
    .merge(interceptions, on=["game_id", "team_id"], how="outer")
    .merge(fouls, on=["game_id", "team_id"], how="outer")
    .fillna(0)
)

# Compute total defensive actions
defensive_actions["total_def_actions"] = (
    defensive_actions["tackles"] + 
    defensive_actions["interceptions"] + 
    defensive_actions["fouls"]
)

# Create a complete dataframe with all necessary information
ppda_base = defensive_actions.merge(
    team_opponent_df, 
    on=["game_id", "team_id"], 
    how="left"
)

# Merge with passes to get opponent passes
ppda_df = ppda_base.merge(
    passes,
    left_on=["game_id", "opponent_team_id"],
    right_on=["game_id", "team_id"],
    how="left",
    suffixes=("", "_opponent")
)

# Rename for clarity
ppda_df = ppda_df.rename(columns={"passes_in_def_60": "opponent_passes_in_def_60"})

# Calculate PPDA - passes the opponent made in their defensive 60% divided by 
# the defensive actions the team made in that same area
ppda_df["PPDA"] = ppda_df["opponent_passes_in_def_60"] / ppda_df["total_def_actions"]

# Clean up the final dataframe
variable_df1 = ppda_df[["game_id", "team_id", "tackles", "interceptions", "fouls", 
                       "total_def_actions", "opponent_passes_in_def_60", "PPDA"]]

# Handle potential division by zero
variable_df1["PPDA"] = variable_df1["PPDA"].replace([np.inf, -np.inf], np.nan)

# Merge variable_df with df_players based on team_id
variable_df = variable_df.merge(
    variable_df1[['game_id', 'team_id', 'PPDA']],
    on=['game_id','team_id'], 
    how='left')

# Replace NaN values in the "team_id" column with 0
variable_df["team_id"] = variable_df["team_id"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 4
# Fouls in attacking half %
"""Represents an important tactical metric that quantifies a team's approach to 
disrupting opposition counter-attacks in advanced areas of the pitch. This metric 
can be precisely defined as:
The percentage of a team's total fouls that occur in the opponent's half of the 
pitch during defensive transition situations: Calculated as: (Number of fouls 
committed in the attacking half during transitions ÷ Total fouls committed during 
transitions) × 100
"""

def calculate_fouls_in_attacking_half(progcarry_df2):
    """
    Calculate the percentage of a team's total fouls that occur in the opponent's half of the pitch
    during defensive transition situations.
    
    For each team (TEAM A):
    - When TEAM B has possession (TEAM A is defensively transitioning)
    - Count fouls TEAM A commits on TEAM B
    - Calculate what percentage of these fouls occur in TEAM B's half (which is TEAM A's attacking half)
    
    Parameters:
    progcarry_df2 (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - possessionId: identifier for possession chains
        - first_chain: 1 if it's the beginning of a chain
        - last_chain: 1 if it's the end of a chain
        - type_id: identifier for the type of action (4 for fouls)
        - outcome: outcome of the action (0 for committed fouls)
        - start_x: x-coordinate of the action (0-100 scale)
    
    Returns:
    pd.DataFrame: DataFrame containing fouls in attacking half (%) for each game_id and team_id
    """
    import pandas as pd
    import numpy as np
    
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df2.copy()
    
    # Step 1: Get all unique game_ids
    games = df['game_id'].unique()
    
    # Initialize results list
    results = []
    
    # Step 2: Process each game
    for game_id in games:
        game_data = df[df['game_id'] == game_id]
        
        # Step 3: Get unique teams in this game
        teams = game_data['team_id'].unique()
        
        if len(teams) != 2:
            # Skip games that don't have exactly 2 teams
            continue
            
        # Step 4: For each team, analyze their fouls when the other team has possession
        for defending_team in teams:
            # The other team that has possession
            attacking_team = [t for t in teams if t != defending_team][0]
            
            # Get possessions where the attacking team has the ball
            attacking_possessions = game_data[game_data['team_id'] == attacking_team]['possessionId'].unique()
            
            # Find fouls in these possessions
            fouls = game_data[
                (game_data['possessionId'].isin(attacking_possessions)) &  # During attacking team's possession
                (game_data['type_id'] == 4) &  # It's a foul
                (game_data['outcome'] == 0)    # Committed foul
            ].copy()
            
            # If no fouls found for this scenario, add a row with zeros
            if len(fouls) == 0:
                results.append({
                    'game_id': game_id,
                    'team_id': defending_team,  # The team committing the fouls
                    'total_fouls': 0,
                    'attacking_half_fouls': 0,
                    'fouls_in_attacking_half_pct': 0.0
                })
                continue
                
            # Mark fouls in attacking half (start_x >= 50)
            # Note: The x-coordinate is from the perspective of the team in possession,
            # so start_x >= 50 means the foul occurred in the attacking team's half,
            # which is the defending team's attacking half
            fouls['in_attacking_half'] = np.where(fouls['start_x'] >= 50, 1, 0)
            
            # Count total fouls and fouls in attacking half
            total_fouls = len(fouls)
            attacking_half_fouls = fouls['in_attacking_half'].sum()
            
            # Calculate percentage
            if total_fouls > 0:
                attacking_half_pct = (attacking_half_fouls / total_fouls) * 100
            else:
                attacking_half_pct = 0.0
                
            # Add to results
            results.append({
                'game_id': game_id,
                'team_id': defending_team,  # The team committing the fouls
                'total_fouls': total_fouls,
                'attacking_half_fouls': attacking_half_fouls,
                'fouls_in_attacking_half_pct': round(attacking_half_pct, 2)
            })
    
    # Create DataFrame from results
    result_df = pd.DataFrame(results)
    
    return result_df

# Example usage
variable_df4 = calculate_fouls_in_attacking_half(progcarry_df2)

# Display the result
#print(variable_df4[['game_id', 'team_id', 'total_fouls', 'attacking_half_fouls', 'fouls_in_attacking_half_pct']])

# Merge variable_df with df_players based on team_id
variable_df = variable_df.merge(
    variable_df4[['game_id', 'team_id', 'fouls_in_attacking_half_pct']],
    on=['game_id','team_id'], 
    how='left')

# Replace NaN values in the "fouls_in_attacking_half_pct" column with 0
variable_df["fouls_in_attacking_half_pct"] = variable_df["fouls_in_attacking_half_pct"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 5
# Defensive intensity
"""Defensive intensity is defined as the number of defensive duels, loose ball duels, interceptions,
tackles, and fouls when out of possession, adjusted by the opponent's possession. It measures how
actively a player or team engages in defensive actions relative to the amount of time the opponent
has the ball."""

def calculate_defensive_intensity(progcarry_df):
    """
    Calculate defensive intensity based on defensive actions for each game_id and team_id.
    
    Parameters:
    progcarry_df (pd.DataFrame): DataFrame containing:
        - game_id: match identifier
        - team_id: team identifier
        - type_id: event type
        - outcome: event outcome
    
    Returns:
    pd.DataFrame: DataFrame containing defensive intensity statistics
    """
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df.copy()
    
    # Define defensive action types
    DEFENSIVE_TYPES = {
        'tackles': 7,
        'interceptions': 8,
        'clearances': 12,
        'aerials': 44,
        'ball_recoveries': 49
    }
    
    # Initialize list to store defensive stats
    defensive_stats = []
    
    # Get unique combinations for progress bar
    combinations = df.groupby(['game_id', 'team_id']).groups.keys()
    
    # Create progress bar
    pbar = tqdm(total=len(combinations), desc='Calculating defensive intensity')
    
    # Process each game and team
    for game_id, team_id in combinations:
        # Get team's actions
        team_data = df[
            (df['game_id'] == game_id) & 
            (df['team_id'] == team_id)
        ]
        
        # Initialize stats dictionary
        stats = {
            'game_id': game_id,
            'team_id': team_id
        }
        
        # Count each type of defensive action
        for action_name, type_id in DEFENSIVE_TYPES.items():
            action_count = len(team_data[team_data['type_id'] == type_id])
            stats[action_name] = action_count
        
        # Count fouls (type_id 4 with outcome 0)
        fouls = len(team_data[
            (team_data['type_id'] == 4) & 
            (team_data['outcome'] == 0)
        ])
        stats['fouls'] = fouls
        
        # Calculate total defensive actions
        total_actions = sum([
            stats[action] for action in [
                'tackles', 'interceptions', 'clearances', 
                'aerials', 'ball_recoveries', 'fouls'
            ]
        ])
        
        stats['total_defensive_actions'] = total_actions
        
        # Calculate percentages for each action type
        if total_actions > 0:
            for action in ['tackles', 'interceptions', 'clearances', 
                          'aerials', 'ball_recoveries', 'fouls']:
                stats[f'{action}_percentage'] = (
                    stats[action] / total_actions * 100
                )
        
        # Calculate defensive intensity score
        stats['defensive_intensity'] = total_actions
        
        # Add temporal analysis if time exists in data
        if 'time' in team_data.columns:
            # Split game into 15-minute segments
            def get_time_segment(time):
                return 15 * (time // (15 * 60))
            
            team_data['time_segment'] = team_data['time'].apply(get_time_segment)
            
            # Calculate defensive actions per segment
            segment_actions = team_data[
                team_data['type_id'].isin(list(DEFENSIVE_TYPES.values()) + [4])
            ].groupby('time_segment').size()
            
            if len(segment_actions) > 0:
                stats.update({
                    'max_intensity_segment': segment_actions.max(),
                    'min_intensity_segment': segment_actions.min(),
                    'avg_intensity_segment': segment_actions.mean()
                })
        
        defensive_stats.append(stats)
        
        # Update progress bar
        pbar.update(1)
    
    # Close progress bar
    pbar.close()
    
    # Create DataFrame with defensive statistics
    defensive_df = pd.DataFrame(defensive_stats)
    
    # Ensure consistent column order
    base_columns = [
        'game_id',
        'team_id',
        'defensive_intensity',
        'total_defensive_actions'
    ]
    
    action_columns = []
    for action in ['tackles', 'interceptions', 'clearances', 
                   'aerials', 'ball_recoveries', 'fouls']:
        action_columns.extend([
            action,
            f'{action}_percentage'
        ])
    
    temporal_columns = [
        'max_intensity_segment',
        'min_intensity_segment',
        'avg_intensity_segment'
    ]
    
    # Combine available columns
    columns = base_columns + action_columns + [
        col for col in temporal_columns if col in defensive_df.columns
    ]
    
    defensive_df = defensive_df[columns]
    
    return defensive_df

variable_df5 = calculate_defensive_intensity(progcarry_df)

# Importing defensive_intensity
# Merge variable_df with defensive_intensity
variable_df = variable_df.merge(
    variable_df5[['game_id', 'team_id', 'defensive_intensity']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "defensive_intensity" column with 0
variable_df["defensive_intensity"] = variable_df["defensive_intensity"].fillna(0)

#variable_df = variable_df.drop(columns=["defensive_intensity", "defensive_intensity_x", "defensive_intensity_y"], errors="ignore")

###############################################################################
###############################################################################
###############################################################################
###############################################################################

# Variáveis
# DEFENCE TRANSITION
# 6
# Time to First Defensive Action (s)
"""
Time to defensive action (s) refers to the time taken for a player or team to 
perform a defensive action, such as a tackle, interception, or clearance, after 
losing possession. This metric helps in understanding the responsiveness and 
reaction time of a player or team in defensive situations.
"""

filtered_df6 = variable_df.copy()

# Step 1: Define defensive action type_ids
defensive_event_types = [7, 8, 4, 12, 44, 49]

# Step 2: Identify possession losses (last event in a possession)
possession_losses = progcarry_df[progcarry_df["last_chain"] == 1][["game_id", "team_id", "time"]]
possession_losses.rename(columns={"time": "loss_time"}, inplace=True)

# Step 3: Identify defensive actions (valid type_id)
defensive_actions = progcarry_df[
    progcarry_df["type_id"].isin(defensive_event_types)
][["game_id", "team_id", "time"]]
defensive_actions.rename(columns={"time": "defensive_time"}, inplace=True)

# Step 4: Merge possession losses and defensive actions on game_id and team_id
merged_df = possession_losses.merge(defensive_actions, on=["game_id", "team_id"], how="outer")

# Step 5: Ensure each defensive action is paired with the closest preceding possession loss
merged_df = merged_df[merged_df["defensive_time"] > merged_df["loss_time"]]
merged_df["time_diff"] = merged_df["defensive_time"] - merged_df["loss_time"]

# Step 6: Keep only the closest preceding loss for each defensive action
merged_df = merged_df.sort_values(by=["game_id", "team_id", "defensive_time", "time_diff"])
merged_df = merged_df.drop_duplicates(subset=["game_id", "team_id", "defensive_time"], keep="first")

# Step 7: Compute average time to defensive action per team per game
variable_df6 = (
    merged_df.groupby(["game_id", "team_id"])["time_diff"]
    .mean()
    .reset_index()
    .rename(columns={"time_diff": "avg_time_to_defensive_action"})
)

# Importing avg_time_to_defensive_action
# Merge variable_df with avg_time_to_defensive_action
variable_df = variable_df.merge(
    variable_df6[['game_id', 'team_id', 'avg_time_to_defensive_action']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "turnover_line_height" column with 0
variable_df["avg_time_to_defensive_action"] = variable_df["avg_time_to_defensive_action"].fillna(0)


###############################################################################
###############################################################################

# Variáveis
# 7
# Counter-Press Success Rate %
"""
This metric is defined as:
The percentage of counter-pressing sequences that successfully result in the team 
regaining possession within a specified timeframe (typically 5-8 (up to 8s) seconds) after 
losing the ball. Evaluates the effectiveness of a team's immediate pressing actions 
after losing possession.
Calculated as: (Number of successful counter-presses ÷ Total counter-press attempts) × 100
"""

# Step 1: Define valid recovery type_ids
valid_type_ids = [3, 4, 7, 44, 45, 54]

# Step 2: Identify possession losses (last event in a possession)
possession_losses = progcarry_df[progcarry_df["last_chain"] == 1][["game_id", "team_id", "time"]]
possession_losses.rename(columns={"time": "loss_time"}, inplace=True)

# Step 3: Identify valid recoveries (first event in a possession with valid type_id)
recoveries = progcarry_df[
    (progcarry_df["first_chain"] == 1) & (progcarry_df["type_id"].isin(valid_type_ids))
][["game_id", "team_id", "time"]]
recoveries.rename(columns={"time": "recovery_time"}, inplace=True)

# Step 4: Merge and ensure correct pairing (loss before recovery, within 5s)
recoveries_within_5s = possession_losses.merge(
    recoveries, 
    on=["game_id", "team_id"], 
    how="outer"
)

# Step 5: Keep only cases where loss_time < recovery_time and within 5 seconds
recoveries_within_5s = recoveries_within_5s[
    (recoveries_within_5s["loss_time"] < recoveries_within_5s["recovery_time"]) & 
    ((recoveries_within_5s["recovery_time"] - recoveries_within_5s["loss_time"]) <= 5)
]

# Step 6: Count recoveries within 5s and total recoveries
total_recoveries = recoveries.groupby(["game_id", "team_id"]).size().reset_index(name="total_recoveries")
recoveries_within_5s_count = recoveries_within_5s.groupby(["game_id", "team_id"]).size().reset_index(name="recoveries_within_5s")

# Step 7: Merge both counts
recoveries_df = total_recoveries.merge(recoveries_within_5s_count, on=["game_id", "team_id"], how="left").fillna(0)

# Step 8: Calculate counter_press_Success_Rate_%
recoveries_df["counter_press_Success_Rate_%"] = (recoveries_df["recoveries_within_5s"] / recoveries_df["total_recoveries"]) * 100

# Keep only relevant columns
variable_df7 = recoveries_df[["game_id", "team_id", "counter_press_Success_Rate_%"]]

# Importing counter_press_Success_Rate_%
# Merge variable_df with counter_press_Success_Rate_%
variable_df = variable_df.merge(
    variable_df7[['game_id', 'team_id', 'counter_press_Success_Rate_%']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "counter_press_Success_Rate_%" column with 0
variable_df["counter_press_Success_Rate_%"] = variable_df["counter_press_Success_Rate_%"].fillna(0)


###############################################################################
###############################################################################

# Variáveis
# 8
# Transition Vulnerability Index
"""
Ratio of opposition progressive passes completed in first 10 seconds after 
possession loss. quantifies a team's susceptibility to opposition counter-attacks 
following possession loss.
"""

def calculate_transition_vulnerability_index(progcarry_df2):
    """
    Calculate the Transition Vulnerability Index for each team in each game.
    
    Transition Vulnerability Index is the ratio of progressive passes to total passes
    completed by the opposition in the first 8 seconds after a team loses possession.
    
    Parameters:
    progcarry_df2 (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - possessionId: identifier for possession chains
        - first_chain: 1 if it's the beginning of a chain
        - last_chain: 1 if it's the end of a chain
        - time: game time in seconds
        - type_id: identifier for the type of action (1 for passes)
        - progressive_pass: 1 if the pass is progressive, 0 otherwise
    
    Returns:
    pd.DataFrame: DataFrame containing Transition Vulnerability Index for each game_id and team_id
    """
    
def calculate_transition_vulnerability_index(progcarry_df2):
    """
    Calculate the Transition Vulnerability Index for each team in each game.
    
    Transition Vulnerability Index is the ratio of progressive passes to total passes
    completed by the opposition in the first 8 seconds after a team loses possession.
    
    Parameters:
    progcarry_df2 (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - possessionId: identifier for possession chains
        - first_chain: 1 if it's the beginning of a chain
        - last_chain: 1 if it's the end of a chain
        - time: game time in seconds
        - type_id: identifier for the type of action (1 for passes)
        - progressive_pass: 1 if the pass is progressive, 0 otherwise
    
    Returns:
    pd.DataFrame: DataFrame containing Transition Vulnerability Index for each game_id and team_id
    """
    
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df2.copy()
    
    # Initialize results list
    results = []
    
    # Get all unique game IDs
    games = df['game_id'].unique()
    
    for game_id in games:
        # Filter data for current game
        game_data = df[df['game_id'] == game_id]
        
        # Get unique teams in this game
        teams = game_data['team_id'].unique()
        
        # Skip games that don't have exactly 2 teams
        if len(teams) != 2:
            continue
        
        # Process each team
        for vulnerable_team in teams:
            # The other team (opposition)
            opposition_team = [t for t in teams if t != vulnerable_team][0]
            
            # Find possession loss events (last_chain == 1) for the vulnerable team
            possession_losses = game_data[
                (game_data['team_id'] == vulnerable_team) & 
                (game_data['last_chain'] == 1)
            ][['possessionId', 'time']].copy()
            
            if len(possession_losses) == 0:
                # If no possession losses found, add a row with zeros
                results.append({
                    'game_id': game_id,
                    'team_id': vulnerable_team,
                    'total_passes_after_loss': 0,
                    'progressive_passes_after_loss': 0,
                    'transition_vulnerability_index': 0.0
                })
                continue
            
            # For each possession loss, find opposition passes in the next 8 seconds
            total_passes = 0
            progressive_passes = 0
            
            for _, loss in possession_losses.iterrows():
                loss_time = loss['time']
                
                # Find opposition passes in the 8-second window after possession loss
                opposition_passes = game_data[
                    (game_data['team_id'] == opposition_team) & 
                    (game_data['time'] > loss_time) & 
                    (game_data['time'] <= loss_time + 8) & 
                    (game_data['type_id'] == 1)  # Passes only
                ]
                
                # Count total passes and progressive passes
                total_passes += len(opposition_passes)
                progressive_passes += opposition_passes['progressive_pass'].sum()
            
            # Calculate the Transition Vulnerability Index
            if total_passes > 0:
                vulnerability_index = progressive_passes / total_passes
            else:
                vulnerability_index = 0.0
            
            # Add to results
            results.append({
                'game_id': game_id,
                'team_id': vulnerable_team,
                'total_passes_after_loss': total_passes,
                'progressive_passes_after_loss': progressive_passes,
                'transition_vulnerability_index': round(vulnerability_index, 3)
            })
    
    # Create DataFrame from results
    result_df = pd.DataFrame(results)
    
    return result_df

# Example usage
variable_df8 = calculate_transition_vulnerability_index(progcarry_df2)

# Display the result
print(variable_df8[['game_id', 'team_id', 'total_passes_after_loss', 
                          'progressive_passes_after_loss', 'transition_vulnerability_index']])

# Importing counter_press_Success_Rate_%
# Merge variable_df with counter_press_Success_Rate_%
variable_df = variable_df.merge(
    variable_df8[['game_id', 'team_id', 'transition_vulnerability_index']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "transition_vulnerability_index" column with 0
variable_df["transition_vulnerability_index"] = variable_df["transition_vulnerability_index"].fillna(0)


###############################################################################
###############################################################################

# Variáveis
# 9
# Opposition Final third entries within 10s after recovery
"""Opp. Final third entries within 10s after recovery refers to the number of times the opposing team 
successfully enters the final third of the pitch within 10 seconds after recovering possession. This 
metric helps in understanding how quickly and effectively the opposition can transition from defense 
to attack and create potential scoring opportunities.
"""

def calculate_opposition_entries(progcarry_df):
    """
    Calculate opposition final third entries within 10s after recovery for each game_id, team_id, and period_id.
    
    Parameters:
    progcarry_df (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - period_id: identifier for game period (half)
        - possessionId: identifier for each possession chain
        - first_chain: 1 if possession chain starts, 0 otherwise
        - last_chain: 1 if possession chain ends, 0 otherwise
        - time: time in seconds
        - start_x, start_y: initial coordinates
        - end_x, end_y: final coordinates
    
    Returns:
    pd.DataFrame: DataFrame containing entry statistics for each game_id, team_id, and period_id
    """
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df.copy()
    
    # Define final third threshold (assuming pitch coordinates are normalized 0-100)
    FINAL_THIRD_THRESHOLD = 66.7  # Two-thirds of the pitch length
    TIME_WINDOW = 10  # seconds
    
    # Initialize list to store entry events
    entries_after_recovery = []
    
    # Get unique combinations of game_id, team_id, and period_id
    groups = df.groupby(['game_id', 'team_id', 'period_id'])
    total_groups = len(groups)
    
    # Create progress bar
    pbar = tqdm(total=total_groups, desc='Analyzing final third entries')
    
    # Group by game_id, team_id, and period_id
    for (game_id, team_id, period_id), group_data in groups:
        # Sort by time to ensure chronological order
        group_data = group_data.sort_values('time')
        
        # Find possession recovery events (first_chain == 1)
        recovery_events = group_data[group_data['first_chain'] == 1]
        
        for idx, recovery_event in recovery_events.iterrows():
            recovery_time = recovery_event['time']
            
            # Find opposition events within 10s after recovery
            opposition_events = df[
                (df['game_id'] == game_id) &
                (df['team_id'] != team_id) &  # Opposition team
                (df['period_id'] == period_id) &
                (df['time'] > recovery_time) &
                (df['time'] <= recovery_time + TIME_WINDOW)
            ]
            
            # Check for final third entries
            # An entry is counted if the action crosses into the final third
            final_third_entries = opposition_events[
                ((opposition_events['start_x'] < FINAL_THIRD_THRESHOLD) & 
                 (opposition_events['end_x'] >= FINAL_THIRD_THRESHOLD)) |
                # Also count actions that both start and end in final third
                ((opposition_events['start_x'] >= FINAL_THIRD_THRESHOLD) & 
                 (opposition_events['end_x'] >= FINAL_THIRD_THRESHOLD))
            ]
            
            if len(final_third_entries) > 0:
                entries_after_recovery.append({
                    'game_id': game_id,
                    'team_id': team_id,  # Team that lost possession
                    'period_id': period_id,
                    'recovery_time': recovery_time,
                    'entries_count': len(final_third_entries),
                    'fastest_entry_time': min(final_third_entries['time']) - recovery_time
                })
        
        # Update progress bar
        pbar.update(1)
    
    # Close progress bar
    pbar.close()
    
    # Create DataFrame with entry events
    entries_df = pd.DataFrame(entries_after_recovery)
    
    # Calculate summary statistics for each game_id, team_id, and period_id
    if len(entries_df) > 0:
        summary_stats = entries_df.groupby(['game_id', 'team_id', 'period_id']).agg({
            'entries_count': ['sum', 'count'],
            'fastest_entry_time': 'min'
        }).round(2)
        
        # Flatten column names
        summary_stats.columns = [
            'total_entries',
            'total_recoveries_leading_to_entries',
            'fastest_entry_time'
        ]
        
        summary_stats = summary_stats.reset_index()
        
        # Calculate percentage of recoveries leading to entries
        total_recoveries = df[df['first_chain'] == 1].groupby(
            ['game_id', 'team_id', 'period_id']).size().reset_index(name='total_recoveries')
        
        summary_stats = summary_stats.merge(total_recoveries, 
                                          on=['game_id', 'team_id', 'period_id'])
        
        summary_stats['entry_percentage'] = (
            summary_stats['total_entries'] / summary_stats['total_recoveries'] * 100
        ).round(2)
        
    else:
        # Create empty DataFrame with correct columns if no entries found
        summary_stats = pd.DataFrame(columns=[
            'game_id', 'team_id', 'period_id', 'total_entries',
            'total_recoveries_leading_to_entries', 'fastest_entry_time',
            'total_recoveries', 'entry_percentage'
        ])
    
    return summary_stats

variable_df9 = calculate_opposition_entries(progcarry_df)

# Step 7: Compute average time to defensive action per team per game
variable_df9 = (
    variable_df9.groupby(["game_id", "team_id"])["total_recoveries_leading_to_entries"]
    .sum()
    .reset_index()
    .rename(columns={"total_recoveries_leading_to_entries": "opposition_final_third_entries_10s"})
)

# Importing opposition_final_third_entries_10s
# Merge variable_df with opposition_final_third_entries_10s
variable_df = variable_df.merge(
    variable_df9[['game_id', 'team_id', 'opposition_final_third_entries_10s']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "turnover_line_height" column with 0
variable_df["opposition_final_third_entries_10s"] = variable_df["opposition_final_third_entries_10s"].fillna(0)



###############################################################################
###############################################################################
# Variáveis
# 10
#Opposition Box entries within 10s after recovery
"""Opp. Box entries within 10s after recovery refers to the number of times the opposing team 
successfully enters the penalty box within 10 seconds after recovering possession. This metric
helps in understanding how quickly and effectively the opposition can transition from defense 
to attack and create potential scoring opportunities in the penalty area."""

filtered_df10 = variable_df.copy()

def calculate_opposition_box_entries(progcarry_df):
    """
    Calculate opposition box entries within 10s after recovery for each game_id, team_id, and period_id.
    
    Parameters:
    progcarry_df (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - period_id: identifier for game period (half)
        - possessionId: identifier for each possession chain
        - first_chain: 1 if possession chain starts, 0 otherwise
        - last_chain: 1 if possession chain ends, 0 otherwise
        - time: time in seconds
        - start_x, start_y: initial coordinates
        - end_x, end_y: final coordinates
    
    Returns:
    pd.DataFrame: DataFrame containing box entry statistics for each game_id, team_id, and period_id
    """
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df.copy()
    
    # Define box coordinates
    BOX_X = 83.0
    BOX_Y_MIN = 21.1
    BOX_Y_MAX = 78.9
    TIME_WINDOW = 10  # seconds
    
    def is_in_box(x, y):
        """Check if coordinates are in the penalty box"""
        return (x >= BOX_X) and (BOX_Y_MIN <= y <= BOX_Y_MAX)
    
    def is_box_entry(start_x, start_y, end_x, end_y):
        """Check if the action represents a box entry"""
        # Case 1: Action crosses into box
        if not is_in_box(start_x, start_y) and is_in_box(end_x, end_y):
            return True
        # Case 2: Both start and end are in box
        if is_in_box(start_x, start_y) and is_in_box(end_x, end_y):
            return True
        return False
    
    # Initialize list to store entry events
    entries_after_recovery = []
    
    # Get unique combinations of game_id, team_id, and period_id
    groups = df.groupby(['game_id', 'team_id', 'period_id'])
    total_groups = len(groups)
    
    # Create progress bar
    pbar = tqdm(total=total_groups, desc='Analyzing box entries')
    
    # Group by game_id, team_id, and period_id
    for (game_id, team_id, period_id), group_data in groups:
        # Sort by time to ensure chronological order
        group_data = group_data.sort_values('time')
        
        # Find possession recovery events (first_chain == 1)
        recovery_events = group_data[group_data['first_chain'] == 1]
        
        for idx, recovery_event in recovery_events.iterrows():
            recovery_time = recovery_event['time']
            
            # Find opposition events within 10s after recovery
            opposition_events = df[
                (df['game_id'] == game_id) &
                (df['team_id'] != team_id) &  # Opposition team
                (df['period_id'] == period_id) &
                (df['time'] > recovery_time) &
                (df['time'] <= recovery_time + TIME_WINDOW)
            ]
            
            # Check for box entries
            box_entries = opposition_events[
                opposition_events.apply(lambda row: is_box_entry(
                    row['start_x'], row['start_y'], 
                    row['end_x'], row['end_y']
                ), axis=1)
            ]
            
            if len(box_entries) > 0:
                entries_after_recovery.append({
                    'game_id': game_id,
                    'team_id': team_id,  # Team that lost possession
                    'period_id': period_id,
                    'recovery_time': recovery_time,
                    'entries_count': len(box_entries),
                    'fastest_entry_time': min(box_entries['time']) - recovery_time
                })
        
        # Update progress bar
        pbar.update(1)
    
    # Close progress bar
    pbar.close()
    
    # Create DataFrame with entry events
    entries_df = pd.DataFrame(entries_after_recovery)
    
    # Calculate summary statistics for each game_id, team_id, and period_id
    if len(entries_df) > 0:
        summary_stats = entries_df.groupby(['game_id', 'team_id', 'period_id']).agg({
            'entries_count': ['sum', 'count'],
            'fastest_entry_time': 'min'
        }).round(2)
        
        # Flatten column names
        summary_stats.columns = [
            'total_box_entries',
            'total_recoveries_leading_to_entries',
            'fastest_entry_time'
        ]
        
        summary_stats = summary_stats.reset_index()
        
        # Calculate percentage of recoveries leading to entries
        total_recoveries = df[df['first_chain'] == 1].groupby(
            ['game_id', 'team_id', 'period_id']).size().reset_index(name='total_recoveries')
        
        summary_stats = summary_stats.merge(total_recoveries, 
                                          on=['game_id', 'team_id', 'period_id'])
        
        summary_stats['entry_percentage'] = (
            summary_stats['total_box_entries'] / summary_stats['total_recoveries'] * 100
        ).round(2)
        
    else:
        # Create empty DataFrame with correct columns if no entries found
        summary_stats = pd.DataFrame(columns=[
            'game_id', 'team_id', 'period_id', 'total_box_entries',
            'total_recoveries_leading_to_entries', 'fastest_entry_time',
            'total_recoveries', 'entry_percentage'
        ])
    
    return summary_stats

variable_df10 = calculate_opposition_box_entries(progcarry_df)

# Compute average time to defensive action per team per game
variable_df10 = (
    variable_df10.groupby(["game_id", "team_id"])["total_box_entries"]
    .sum()
    .reset_index()
    .rename(columns={"total_box_entries": "opposition_box_entries_10s"})
)

# Importing opposition_box_entries_10s
# Merge variable_df with opposition_box_entries_10s
variable_df = variable_df.merge(
    variable_df10[['game_id', 'team_id', 'opposition_box_entries_10s']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "opposition_box_entries_10s" column with 0
variable_df["opposition_box_entries_10s"] = variable_df["opposition_box_entries_10s"].fillna(0)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
# Variáveis
# ATTACKING TRANSITION
# 11
#Time to progression after own half recovery (s)
"""
The average time (in seconds) between regaining possession in one's own half 
and successfully progressing the ball into the opponent's half or a more advanced 
attacking position. It specifically focuses on transitions initiated in the 
defensive half, emphasizing a team's ability to move from defense to attack quickly.
"""

def calculate_time_to_progression(progcarry_df2):
    """
    Calculate the average time (in seconds) between regaining possession in one's own half
    and successfully progressing the ball into the opponent's half.
    
    Parameters:
    progcarry_df2 (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - possessionId: identifier for possession chains
        - first_chain: 1 if it's the beginning of a chain
        - last_chain: 1 if it's the end of a chain
        - time: game time in seconds
        - start_x: x-coordinate of the action (0-100 scale)
    
    Returns:
    pd.DataFrame: DataFrame containing average time to progression for each game_id and team_id
    """
    import pandas as pd
    import numpy as np
    
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df2.copy()
    
    # Initialize results list
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), team_data in df.groupby(['game_id', 'team_id']):
        # Sort by possessionId and time to ensure chronological order
        team_data = team_data.sort_values(['possessionId', 'time'])
        
        # Get unique possession chains for this team
        possession_chains = team_data['possessionId'].unique()
        
        # Initialize list to store progression times for this team
        progression_times = []
        total_own_half_recoveries = 0
        
        # Analyze each possession chain
        for possession_id in possession_chains:
            # Get actions in this possession chain
            possession_data = team_data[team_data['possessionId'] == possession_id].copy()
            
            # Check if this possession starts with recovery in own half
            # Look for the first action in this possession chain
            first_actions = possession_data[possession_data['first_chain'] == 1]
            
            if len(first_actions) == 0:
                continue  # Skip if no clear starting action
                
            first_action = first_actions.iloc[0]
            
            # Check if recovery is in own half
            if first_action['start_x'] < 50:
                # This possession starts with recovery in own half
                total_own_half_recoveries += 1
                recovery_time = first_action['time']
                
                # Find the first action in opponent's half within this possession
                progression_events = possession_data[possession_data['start_x'] >= 50]
                
                if len(progression_events) > 0:
                    # If the ball reached the opponent's half, calculate the time it took
                    first_progression = progression_events.iloc[0]
                    progression_time = first_progression['time']
                    
                    # Calculate time difference
                    time_to_progression = progression_time - recovery_time
                    
                    # Add to list of progression times
                    progression_times.append(time_to_progression)
        
        # Calculate average time to progression for this team in this game
        if len(progression_times) > 0:
            avg_time_to_progression = sum(progression_times) / len(progression_times)
        else:
            avg_time_to_progression = np.nan  # No progressions found
        
        # Add to results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'recoveries_in_own_half': total_own_half_recoveries,
            'successful_progressions': len(progression_times),
            'progression_success_rate': round(len(progression_times) / total_own_half_recoveries * 100, 2) if total_own_half_recoveries > 0 else 0,
            'time_to_progression_seconds': round(avg_time_to_progression, 2) if not np.isnan(avg_time_to_progression) else np.nan
        })
    
    # Create DataFrame from results
    result_df = pd.DataFrame(results)
    
    return result_df

# Example usage
progression_times = calculate_time_to_progression(progcarry_df2)

# Display the result
print(progression_times[['game_id', 'team_id', 'recoveries_in_own_half', 
                         'successful_progressions', 'progression_success_rate',
                         'time_to_progression_seconds']])

# Compute average time to defensive action per team per game
variable_df11 = (
    progression_times.groupby(["game_id", "team_id"])["time_to_progression_seconds"]
    .sum()
    .reset_index()
)

# Importing opposition_box_entries_10s
# Merge variable_df with opposition_box_entries_10s
variable_df = variable_df.merge(
    variable_df11[['game_id', 'team_id', 'time_to_progression_seconds']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "time_to_progression_seconds" column with 0
variable_df["time_to_progression_seconds"] = variable_df["time_to_progression_seconds"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 12
#First pass forward %
"""
Quantifies a team's immediate intent to progress play after regaining possession.
The percentage of possession recoveries where the very first pass made by the team 
is played in a forward direction.
Calculated as: (Number of forward first passes after recovery ÷ Total number of 
recoveries with a pass) × 100
"""

def calculate_first_pass_forward_percentage(progcarry_df2):
    """
    Calculate the percentage of possession recoveries where the very first pass 
    made by the team is played in a forward direction.
    
    First pass forward % = (Number of forward first passes after recovery ÷ 
                           Total number of recoveries with a pass) × 100
    
    Parameters:
    progcarry_df2 (pd.DataFrame): DataFrame containing possession data with columns:
        - game_id: unique identifier for each game
        - team_id: identifier for the team in possession
        - possessionId: identifier for possession chains
        - first_chain: 1 if it's the beginning of a chain
        - last_chain: 1 if it's the end of a chain
        - type_id: identifier for the type of action (assuming 1 for passes)
        - start_x: x-coordinate of the start of the action
        - end_x: x-coordinate of the end of the action
    
    Returns:
    pd.DataFrame: DataFrame containing first pass forward % for each game_id and team_id
    """
    import pandas as pd
    import numpy as np
    from tqdm import tqdm
    
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df2.copy()
    
    # Initialize results list
    results = []
    
    # Get unique game and team combinations
    game_team_combos = df[['game_id', 'team_id']].drop_duplicates().reset_index(drop=True)
    
    # Create progress bar
    progress_bar = tqdm(total=len(game_team_combos), desc="Analyzing first pass direction")
    
    # Process each game and team combination
    for idx, row in game_team_combos.iterrows():
        game_id = row['game_id']
        team_id = row['team_id']
        
        # Filter data for current game and team
        team_data = df[(df['game_id'] == game_id) & (df['team_id'] == team_id)]
        
        # Find all possession chains that start with a recovery (first_chain == 1)
        possession_starts = team_data[team_data['first_chain'] == 1]['possessionId'].unique()
        
        # Track statistics
        total_recoveries_with_pass = 0
        forward_first_passes = 0
        
        # Analyze each possession
        for possession_id in possession_starts:
            # Get all actions in this possession chain
            possession_data = team_data[team_data['possessionId'] == possession_id].sort_values('time')
            
            # Find the first event in this possession
            first_event = possession_data[possession_data['first_chain'] == 1].iloc[0]
            
            # Find the next pass in this possession after the recovery
            next_passes = possession_data[
                (possession_data['time'] > first_event['time']) & 
                (possession_data['type_id'] == 1)  # Assuming type_id 1 is for passes
            ]
            
            # If there's at least one pass in this possession
            if len(next_passes) > 0:
                total_recoveries_with_pass += 1
                
                # Get the first pass
                first_pass = next_passes.iloc[0]
                
                # Check if the pass is forward (end_x > start_x)
                if first_pass['end_x'] > first_pass['start_x']:
                    forward_first_passes += 1
        
        # Calculate the percentage
        if total_recoveries_with_pass > 0:
            first_pass_forward_pct = (forward_first_passes / total_recoveries_with_pass) * 100
        else:
            first_pass_forward_pct = 0
        
        # Add to results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_recoveries_with_pass': total_recoveries_with_pass,
            'forward_first_passes': forward_first_passes,
            'first_pass_forward_pct': round(first_pass_forward_pct, 2)
        })
        
        # Update progress bar
        progress_bar.update(1)
    
    # Close progress bar
    progress_bar.close()
    
    # Create DataFrame from results
    result_df = pd.DataFrame(results)
    
    return result_df

# Example usage
first_pass_stats = calculate_first_pass_forward_percentage(progcarry_df2)

# Display the result
print(first_pass_stats[['game_id', 'team_id', 'total_recoveries_with_pass', 
                        'forward_first_passes', 'first_pass_forward_pct']])

# Compute first_pass_forward_pct per team per game
variable_df12 = (
    first_pass_stats.groupby(["game_id", "team_id"])["first_pass_forward_pct"]
    .sum()
    .reset_index()
)

# Importing first_pass_forward_pct
# Merge variable_df with first_pass_forward_pct
variable_df = variable_df.merge(
    variable_df12[['game_id', 'team_id', 'first_pass_forward_pct']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "first_pass_forward_pct" column with 0
variable_df["first_pass_forward_pct"] = variable_df["first_pass_forward_pct"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 13
#Final third entries within 10s after own half recovery %
"""Final third entries within 10s after recovery refers to the number of times 
a team successfully moves the ball into the final third of the pitch within 10 
seconds after regaining possession IN ITS OWN HALF. This metric helps in 
understanding the effectiveness and speed of a team's transition from defense to
attack. It indicates how quickly a team can create potential scoring opportunities 
after recovering the ball."""

filtered_df13 = variable_df.copy()

def calculate_final_third_entries_own_half(progcarry_df, time_window=10):
    """
    Calculate final third entries within specified time window after recovery IN OWN HALF.
    
    Parameters:
    progcarry_df (pd.DataFrame): DataFrame containing possession data
    time_window (float): Time window in seconds to consider after recovery (default: 10s)
    
    Returns:
    pd.DataFrame: DataFrame containing entry statistics for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df.copy()
    
    # Define final third threshold (assuming pitch coordinates 0-100)
    FINAL_THIRD_THRESHOLD = 66.7  # Two-thirds of the pitch length
    
    # Define valid recovery conditions - UPDATED to include own half condition
    valid_recoveries = df[
        (df['first_chain'] == 1) &  # Must be start of possession chain
        (df['start_x'] < 50) &      # Must be in own half (added this condition)
        (
            (df['type_id'] == 8) |  # Interception
            ((df['type_id'] == 7) & (df['outcome'] == 1)) |  # Successful tackle
            (df['type_id'] == 49)  # Ball recovery
        )
    ]
    
    # Initialize list to store entry events
    entries_after_recovery = []
    
    # Get unique combinations of game_id and team_id
    groups = valid_recoveries.groupby(['game_id', 'team_id'])
    total_groups = len(groups)
    
    # Create progress bar
    pbar = tqdm(total=total_groups, desc='Analyzing final third entries after own half recovery')
    
    # Analyze entries for each game and team
    for (game_id, team_id), group_data in groups:
        # Sort by time to ensure chronological order
        group_data = group_data.sort_values('time')
        
        total_recoveries = len(group_data)
        entries_data = []
        
        # Analyze each recovery
        for idx, recovery in group_data.iterrows():
            recovery_time = recovery['time']
            recovery_type = recovery['type_id']
            
            # Find team events within time window after recovery
            subsequent_events = df[
                (df['game_id'] == game_id) &
                (df['team_id'] == team_id) &
                (df['time'] > recovery_time) &
                (df['time'] <= recovery_time + time_window)
            ].sort_values('time')
            
            # Check for final third entries
            # An entry is counted if the action crosses into the final third
            final_third_entries = subsequent_events[
                ((subsequent_events['start_x'] < FINAL_THIRD_THRESHOLD) & 
                 (subsequent_events['end_x'] >= FINAL_THIRD_THRESHOLD)) |
                # Also count actions that both start and end in final third
                ((subsequent_events['start_x'] >= FINAL_THIRD_THRESHOLD) & 
                 (subsequent_events['end_x'] >= FINAL_THIRD_THRESHOLD))
            ]
            
            if len(final_third_entries) > 0:
                first_entry = final_third_entries.iloc[0]
                entries_data.append({
                    'recovery_time': recovery_time,
                    'entry_time': first_entry['time'],
                    'time_to_entry': first_entry['time'] - recovery_time,
                    'recovery_type': recovery_type,
                    'entry_start_x': first_entry['start_x'],
                    'entry_end_x': first_entry['end_x']
                })
        
        # Calculate stats for this game and team
        if entries_data:
            entries_df = pd.DataFrame(entries_data)
            
            stats = {
                'game_id': game_id,
                'team_id': team_id,
                'total_own_half_recoveries': total_recoveries,
                'total_entries': len(entries_df),
                'entry_rate_pct': round((len(entries_df) / total_recoveries * 100), 2),
                'avg_time_to_entry': round(entries_df['time_to_entry'].mean(), 2),
                'min_time_to_entry': round(entries_df['time_to_entry'].min(), 2),
                'entries_from_interceptions': len(entries_df[entries_df['recovery_type'] == 8]),
                'entries_from_tackles': len(entries_df[entries_df['recovery_type'] == 7]),
                'entries_from_ball_recoveries': len(entries_df[entries_df['recovery_type'] == 49])
            }
        else:
            stats = {
                'game_id': game_id,
                'team_id': team_id,
                'total_own_half_recoveries': total_recoveries,
                'total_entries': 0,
                'entry_rate_pct': 0,
                'avg_time_to_entry': np.nan,
                'min_time_to_entry': np.nan,
                'entries_from_interceptions': 0,
                'entries_from_tackles': 0,
                'entries_from_ball_recoveries': 0
            }
        
        entries_after_recovery.append(stats)
        
        # Update progress bar
        pbar.update(1)
    
    # Close progress bar
    pbar.close()
    
    # Create DataFrame with entry statistics
    entries_df = pd.DataFrame(entries_after_recovery)
    
    # Calculate percentages for each type of entry
    if len(entries_df) > 0 and entries_df['total_entries'].sum() > 0:
        for type_name, type_col in [
            ('interceptions', 'entries_from_interceptions'),
            ('tackles', 'entries_from_tackles'),
            ('ball_recoveries', 'entries_from_ball_recoveries')
        ]:
            entries_df[f'{type_name}_entry_pct'] = (
                entries_df[type_col] / entries_df['total_entries'] * 100
            ).round(2)
    
    # Ensure consistent column order
    columns = [
        'game_id', 'team_id', 'total_own_half_recoveries', 'total_entries',
        'entry_rate_pct', 'avg_time_to_entry', 'min_time_to_entry',
        'entries_from_interceptions', 'entries_from_tackles',
        'entries_from_ball_recoveries'
    ]
    
    # Add percentage columns if they exist
    if 'interceptions_entry_pct' in entries_df.columns:
        columns.extend([
            'interceptions_entry_pct',
            'tackles_entry_pct',
            'ball_recoveries_entry_pct'
        ])
    
    entries_df = entries_df[columns]
    
    return entries_df

# Example usage
own_half_entries = calculate_final_third_entries_own_half(progcarry_df2)

# Display the result
print(own_half_entries[['game_id', 'team_id', 'total_own_half_recoveries', 
                        'total_entries', 'entry_rate_pct']])
# Compute recoveries per team per game
variable_df13 = (
    own_half_entries.groupby(["game_id", "team_id"])["entry_rate_pct"]
    .sum()
    .reset_index()
    .rename(columns={"entry_rate_pct": "final_third_entries_10s_pct"})
)

# Importing recoveries
# Merge variable_df with recoveries
variable_df = variable_df.merge(
    variable_df13[['game_id', 'team_id', 'final_third_entries_10s_pct']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "final_third_entries_10s_pct" column with 0
variable_df["final_third_entries_10s_pct"] = variable_df["final_third_entries_10s_pct"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 14
# Box entries within 10s after attacking half recovery %
"""Box entries within 10s after recovery refers to the number of times a team 
successfully moves the ball into the opponent's penalty area within 10 seconds 
after regaining possession IN ITS ATTACKING HALF. This metric helps in 
understanding the effectiveness and speed of a team's transition from defense 
to attack. It indicates how quickly a team can create potential scoring 
opportunities in the penalty area after recovering the ball."""

###ADJUST CONDITIONS FOR ATTACKING HALF. THE CODE BELOW IS THE DENOMINATOR!!!!!
###ADJUST CONDITIONS FOR ATTACKING HALF. THE CODE BELOW IS THE DENOMINATOR!!!!!
###ADJUST CONDITIONS FOR ATTACKING HALF. THE CODE BELOW IS THE DENOMINATOR!!!!!
###ADJUST CONDITIONS FOR ATTACKING HALF. THE CODE BELOW IS THE DENOMINATOR!!!!!
###ADJUST CONDITIONS FOR ATTACKING HALF. THE CODE BELOW IS THE DENOMINATOR!!!!!


filtered_df14 = variable_df.copy()

def calculate_box_entries_attacking_half(progcarry_df2, time_window=10):
    """
    Calculate box entries within specified time window after recovery IN ATTACKING HALF.
    
    Parameters:
    progcarry_df2 (pd.DataFrame): DataFrame containing possession data
    time_window (float): Time window in seconds to consider after recovery (default: 10s)
    
    Returns:
    pd.DataFrame: DataFrame containing box entry statistics for each game_id and team_id
    """
    import pandas as pd
    import numpy as np
    from tqdm import tqdm
    
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df2.copy()
    
    # Define box coordinates
    BOX_X = 83.0
    BOX_Y_MIN = 21.1
    BOX_Y_MAX = 78.9
    
    def is_in_box(x, y):
        """Check if coordinates are in the penalty box"""
        return (x >= BOX_X) and (BOX_Y_MIN <= y <= BOX_Y_MAX)
    
    def is_box_entry(start_x, start_y, end_x, end_y):
        """Check if the action represents a box entry"""
        # Case 1: Action crosses into box
        if not is_in_box(start_x, start_y) and is_in_box(end_x, end_y):
            return True
        # Case 2: Both start and end are in box
        if is_in_box(start_x, start_y) and is_in_box(end_x, end_y):
            return True
        return False
    
    # Define valid recovery conditions - MODIFIED to include attacking half condition
    valid_recoveries = df[
        (df['first_chain'] == 1) &  # Must be start of possession chain
        (df['start_x'] >= 50) &     # Must be in attacking half (added this condition)
        (
            (df['type_id'] == 8) |  # Interception
            ((df['type_id'] == 7) & (df['outcome'] == 1)) |  # Successful tackle
            (df['type_id'] == 49)  # Ball recovery
        )
    ]
    
    # Initialize list to store entry events
    entries_after_recovery = []
    
    # Get unique combinations of game_id and team_id
    groups = valid_recoveries.groupby(['game_id', 'team_id'])
    total_groups = len(groups)
    
    # Create progress bar
    pbar = tqdm(total=total_groups, desc='Analyzing box entries after attacking half recovery')
    
    # Analyze entries for each game and team
    for (game_id, team_id), group_data in groups:
        # Sort by time to ensure chronological order
        group_data = group_data.sort_values('time')
        
        total_recoveries = len(group_data)
        entries_data = []
        
        # Analyze each recovery
        for idx, recovery in group_data.iterrows():
            recovery_time = recovery['time']
            recovery_type = recovery['type_id']
            
            # Find team events within time window after recovery
            subsequent_events = df[
                (df['game_id'] == game_id) &
                (df['team_id'] == team_id) &
                (df['time'] > recovery_time) &
                (df['time'] <= recovery_time + time_window)
            ].sort_values('time')
            
            # Check for box entries
            box_entries = subsequent_events[
                subsequent_events.apply(lambda row: is_box_entry(
                    row['start_x'], row['start_y'], 
                    row['end_x'], row['end_y']
                ), axis=1)
            ]
            
            if len(box_entries) > 0:
                first_entry = box_entries.iloc[0]
                entries_data.append({
                    'recovery_time': recovery_time,
                    'entry_time': first_entry['time'],
                    'time_to_entry': first_entry['time'] - recovery_time,
                    'recovery_type': recovery_type,
                    'entry_start_x': first_entry['start_x'],
                    'entry_end_x': first_entry['end_x']
                })
        
        # Calculate stats for this game and team
        if entries_data:
            entries_df = pd.DataFrame(entries_data)
            
            stats = {
                'game_id': game_id,
                'team_id': team_id,
                'attacking_half_recoveries': total_recoveries,
                'total_box_entries': len(entries_df),
                'box_entry_rate_pct': round((len(entries_df) / total_recoveries * 100), 2),
                'avg_time_to_entry': round(entries_df['time_to_entry'].mean(), 2),
                'min_time_to_entry': round(entries_df['time_to_entry'].min(), 2),
                'entries_from_interceptions': len(entries_df[entries_df['recovery_type'] == 8]),
                'entries_from_tackles': len(entries_df[entries_df['recovery_type'] == 7]),
                'entries_from_ball_recoveries': len(entries_df[entries_df['recovery_type'] == 49])
            }
        else:
            stats = {
                'game_id': game_id,
                'team_id': team_id,
                'attacking_half_recoveries': total_recoveries,
                'total_box_entries': 0,
                'box_entry_rate_pct': 0,
                'avg_time_to_entry': np.nan,
                'min_time_to_entry': np.nan,
                'entries_from_interceptions': 0,
                'entries_from_tackles': 0,
                'entries_from_ball_recoveries': 0
            }
        
        entries_after_recovery.append(stats)
        
        # Update progress bar
        pbar.update(1)
    
    # Close progress bar
    pbar.close()
    
    # Create DataFrame with entry statistics
    entries_df = pd.DataFrame(entries_after_recovery)
    
    # Calculate percentages for each type of entry
    if len(entries_df) > 0 and entries_df['total_box_entries'].sum() > 0:
        for type_name, type_col in [
            ('interceptions', 'entries_from_interceptions'),
            ('tackles', 'entries_from_tackles'),
            ('ball_recoveries', 'entries_from_ball_recoveries')
        ]:
            entries_df[f'{type_name}_entry_pct'] = (
                entries_df[type_col] / entries_df['total_box_entries'] * 100
            ).round(2)
    
    # Ensure consistent column order
    columns = [
        'game_id', 'team_id', 'attacking_half_recoveries', 'total_box_entries',
        'box_entry_rate_pct', 'avg_time_to_entry', 'min_time_to_entry',
        'entries_from_interceptions', 'entries_from_tackles',
        'entries_from_ball_recoveries'
    ]
    
    # Add percentage columns if they exist
    if 'interceptions_entry_pct' in entries_df.columns:
        columns.extend([
            'interceptions_entry_pct',
            'tackles_entry_pct',
            'ball_recoveries_entry_pct'
        ])
    
    entries_df = entries_df[columns]
    
    return entries_df

# Example usage
attacking_half_box_entries = calculate_box_entries_attacking_half(progcarry_df2)

# Display the result
print(attacking_half_box_entries[['game_id', 'team_id', 'attacking_half_recoveries', 
                                 'total_box_entries', 'box_entry_rate_pct']])

# Compute box_entries_10s_pct per team per game
variable_df14 = (
    attacking_half_box_entries.groupby(["game_id", "team_id"])["box_entry_rate_pct"]
    .sum()
    .reset_index()
    .rename(columns={"box_entry_rate_pct": "box_entries_10s_pct"})
)

# Importing recoveries
# Merge variable_df with recoveries
variable_df = variable_df.merge(
    variable_df14[['game_id', 'team_id', 'box_entries_10s_pct']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "box_entries_10s_pct" column with 0
variable_df["box_entries_10s_pct"] = variable_df["box_entries_10s_pct"].fillna(0)

###############################################################################
###############################################################################

# Variáveis
# 15
# Possessions retained after 5s %
"""Possessions retained after 5s % refers to the percentage of times a team 
successfully maintains possession of the ball for at least 5 seconds after 
initially gaining control. This metric helps in understanding the ability to 
hold onto the ball under pressure and avoid immediate turnovers. It is an 
indicator of effective ball control and composure in maintaining possession.
"""

#Calculating Retained Possessions First
filtered_df15 = variable_df.copy()

def calculate_retained_possessions(progcarry_df, retention_threshold=5):
    """
    Calculate possessions retained after specified threshold for each game_id and team_id.
    
    Parameters:
    progcarry_df (pd.DataFrame): DataFrame containing possession data
    retention_threshold (float): Time in seconds to consider possession retained (default: 5s)
    
    Returns:
    pd.DataFrame: DataFrame containing retention statistics
    """
    # Create a copy to avoid modifying the original DataFrame
    df = progcarry_df.copy()
    
    # Define valid recovery conditions
    valid_recoveries = df[
        (df['first_chain'] == 1) &  # Must be start of possession chain
        (
            (df['type_id'] == 8) |  # Interception
            ((df['type_id'] == 7) & (df['outcome'] == 1)) |  # Successful tackle
            (df['type_id'] == 49)  # Ball recovery
        )
    ]
    
    # Initialize list to store retention stats
    retention_stats = []
    
    # Get unique combinations of game_id and team_id
    groups = valid_recoveries.groupby(['game_id', 'team_id'])
    total_groups = len(groups)
    
    # Create progress bar
    pbar = tqdm(total=total_groups, desc='Analyzing possession retention')
    
    # Analyze retentions for each game and team
    for (game_id, team_id), group_data in groups:
        # Sort by time to ensure chronological order
        group_data = group_data.sort_values('time')
        
        total_recoveries = len(group_data)
        retained_possessions = 0
        retained_by_type = {8: 0, 7: 0, 49: 0}  # Counter for each type_id
        retention_durations = []
        
        # Analyze each recovery
        for idx, recovery in group_data.iterrows():
            recovery_time = recovery['time']
            
            # Find next possession loss (if any) for this team
            next_loss = df[
                (df['game_id'] == game_id) &
                (df['team_id'] == team_id) &
                (df['last_chain'] == 1) &
                (df['time'] > recovery_time)
            ].iloc[0] if len(df[
                (df['game_id'] == game_id) &
                (df['team_id'] == team_id) &
                (df['last_chain'] == 1) &
                (df['time'] > recovery_time)
            ]) > 0 else None
            
            if next_loss is not None:
                possession_duration = next_loss['time'] - recovery_time
                retention_durations.append(possession_duration)
                
                if possession_duration >= retention_threshold:
                    retained_possessions += 1
                    # Increment counter for specific recovery type
                    if recovery['type_id'] in retained_by_type:
                        retained_by_type[recovery['type_id']] += 1
        
        # Calculate stats
        stats = {
            'game_id': game_id,
            'team_id': team_id,
            'total_recoveries': total_recoveries,
            'retained_possessions': retained_possessions,
            'retention_rate': (retained_possessions / total_recoveries * 100) if total_recoveries > 0 else 0,
            'retained_interceptions': retained_by_type[8],
            'retained_tackles': retained_by_type[7],
            'retained_ball_recoveries': retained_by_type[49]
        }
        
        # Add duration statistics if we have any retention durations
        if retention_durations:
            stats.update({
                'avg_possession_duration': np.mean(retention_durations).round(2),
                'median_possession_duration': np.median(retention_durations).round(2),
                'min_possession_duration': min(retention_durations).round(2),
                'max_possession_duration': max(retention_durations).round(2)
            })
        
        retention_stats.append(stats)
        
        # Update progress bar
        pbar.update(1)
    
    # Close progress bar
    pbar.close()
    
    # Create DataFrame with retention statistics
    retention_df = pd.DataFrame(retention_stats)
    
    # Calculate percentages for each type of retained possession
    if len(retention_df) > 0:
        for type_name in ['interceptions', 'tackles', 'ball_recoveries']:
            retention_df[f'retained_{type_name}_pct'] = (
                retention_df[f'retained_{type_name}'] / retention_df['total_recoveries'] * 100
            ).round(2)
    
    # Ensure consistent column order
    columns = [
        'game_id', 'team_id', 'total_recoveries', 'retained_possessions',
        'retention_rate', 'retained_interceptions', 'retained_tackles',
        'retained_ball_recoveries', 'retained_interceptions_pct',
        'retained_tackles_pct', 'retained_ball_recoveries_pct'
    ]
    
    # Add duration columns if they exist
    duration_columns = [
        'avg_possession_duration', 'median_possession_duration',
        'min_possession_duration', 'max_possession_duration'
    ]
    columns.extend([col for col in duration_columns if col in retention_df.columns])
    
    retention_df = retention_df[columns]
    
    return retention_df

variable_dfN = calculate_retained_possessions(progcarry_df)

# Compute recoveries per team per game
possession_retained_5s = (
    variable_dfN.groupby(["game_id", "team_id"])["retained_possessions"]
    .sum()
    .reset_index()
    .rename(columns={"retained_possessions": "retained_possessions_5s"})
)

# Compute recoveries per team per game
total_recoveries_df = (
    variable_dfN.groupby(["game_id", "team_id"])["total_recoveries"]
    .sum()
    .reset_index()
)

# Importing recoveries
# Merge variable_df with recoveries
total_recoveries_df = total_recoveries_df.merge(
    possession_retained_5s[['game_id', 'team_id', 'retained_possessions_5s']],
    on=['game_id', 'team_id'], 
    how='left')


# Create Retention Rate
total_recoveries_df["retention_rate"] = total_recoveries_df["retained_possessions_5s"]/total_recoveries_df["total_recoveries"]

variable_df15 = total_recoveries_df.copy()

# Importing recoveries
# Merge variable_df with recoveries
variable_df = variable_df.merge(
    variable_df15[['game_id', 'team_id', 'retention_rate']],
    on=['game_id', 'team_id'], 
    how='left')

# Rename retention_rate column to retained_possessions_5s_pct
variable_df = variable_df.rename(columns={'retention_rate': 'retained_possessions_5s_pct'})

# Replace NaN values in the "recovery_height" column with 0
variable_df["retained_possessions_5s_pct"] = variable_df["retained_possessions_5s_pct"].fillna(0)


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

filtered_df16 = variable_df.copy()

def calculate_long_ball_percentage(df):
    """
    Calculate the percentage of successful long balls relative to total successful passes.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing pass data with:
        - game_id: match identifier
        - team_id: team identifier
        - type_id: event type (1 for passes)
        - outcome: pass success (True/False)
        - qualifiers: dictionary of qualifiers
    
    Returns:
    pd.DataFrame: DataFrame containing long ball statistics for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Filter for all successful passes
    successful_passes = data[
        (data['type_id'] == 1) & 
        (data['outcome'] == True)
    ]
    
    # Filter for successful long balls
    # Add check for non-null and iterable qualifiers before applying the lambda
    successful_long_balls = data[
        (data['type_id'] == 1) & 
        (data['outcome'] == True) &
        (data['qualifiers'].notna()) &  # Check for non-null values
        (data['qualifiers'].apply(lambda x: isinstance(x, (dict, list)) and 1 in x and x[1] == True))
    ]
    
    # Group by game and team to get counts
    pass_counts = successful_passes.groupby(['game_id', 'team_id']).size().reset_index(name='total_passes')
    long_ball_counts = successful_long_balls.groupby(['game_id', 'team_id']).size().reset_index(name='long_balls')
    
    # Merge the counts
    stats = pd.merge(
        pass_counts,
        long_ball_counts,
        on=['game_id', 'team_id'],
        how='left'
    )
    
    # Fill NaN values with 0 for teams that had no long balls
    stats['long_balls'] = stats['long_balls'].fillna(0)
    
    # Calculate percentages
    stats['long_ball_percentage'] = (
        stats['long_balls'] / stats['total_passes'] * 100
    ).round(2)
    
    # Add long ball ratio
    stats['long_ball_ratio'] = (
        stats['long_balls'] / stats['total_passes']
    ).round(3)
    
    # Ensure consistent column order
    columns = [
        'game_id',
        'team_id',
        'total_passes',
        'long_balls',
        'long_ball_percentage',
        'long_ball_ratio'
    ]
    
    stats = stats[columns]
    
    return stats

long_ball_percent = calculate_long_ball_percentage(df)

# Compute long_ball_% per team per game
variable_df16 = (
    long_ball_percent.groupby(["game_id", "team_id"])["long_ball_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"long_ball_percentage": "long_ball_%"})  # Fix column renaming
)

# Importing long_ball_%
# Merge variable_df with long_ball_%
variable_df = variable_df.merge(
    variable_df16[['game_id', 'team_id', 'long_ball_%']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "long_ball_%" column with 0
variable_df["long_ball_%"] = variable_df["long_ball_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 17
# Buildup from goalkick %
"""
Quantifies a team's approach to initiating possession from goal kicks and their 
effectiveness in establishing controlled possession from these situations. 
Calculated as the percentage of goal kicks that successfully lead to established 
possession beyond the initial receiving phase.Established possession is at least 
8 sec, 3 passes and 4 different players.
"""

filtered_df17 = variable_df.copy()

def calculate_buildup_from_goalkick_percentage(df):
    """
    Calculate the percentage of goal kicks that successfully lead to established possession.
    
    Established possession is defined as:
    - At least 8 seconds of possession
    - At least 4 passes
    - At least 4 different players involved (NOTE: player tracking removed as player_id not available)
    
    Parameters:
    df (pd.DataFrame): DataFrame containing event data with:
        - game_id: match identifier
        - team_id: team identifier
        - time: game time in seconds
        - type_id: event type (1 for passes)
        - qualifiers: dictionary containing event qualifiers (124 indicates goal kick)
        - outcome: pass success (True/False)
    
    Returns:
    pd.DataFrame: DataFrame containing buildup from goalkick statistics for each game_id and team_id
    """
    print("Starting buildup from goalkick percentage calculation...")
    
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Ensure data is sorted by game_id, team_id, and time for sequence analysis
    data = data.sort_values(['game_id', 'team_id', 'time'])
    
    goal_kicks = data[
        (data['type_id'] == 1) & 
        (data['qualifiers'].notna()) &  # Check for non-null values
        (data['qualifiers'].apply(lambda x: isinstance(x, (dict, list)) and 124 in x))
    ]
    print(f"Found {len(goal_kicks)} goal kicks in the dataset")
    
    # Initialize result container
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), group in data.groupby(['game_id', 'team_id']):
        print(f"Processing game_id: {game_id}, team_id: {team_id}")
        
        # Find all goal kicks for this team in this game
        team_goal_kicks = goal_kicks[
            (goal_kicks['game_id'] == game_id) & 
            (goal_kicks['team_id'] == team_id)
        ]
        total_goal_kicks = len(team_goal_kicks)
        
        # Skip if there are no goal kicks
        if total_goal_kicks == 0:
            print(f"No goal kicks found for game_id: {game_id}, team_id: {team_id}")
            results.append({
                'game_id': game_id,
                'team_id': team_id,
                'total_goal_kicks': 0,
                'successful_buildups': 0,
                'buildup_percentage': 0.0
            })
            continue
        
        print(f"Analyzing {total_goal_kicks} goal kicks for game_id: {game_id}, team_id: {team_id}")
        
        # Track successful buildups
        successful_buildups = 0
        
        # Get all events for this team in this game
        team_events = group.copy()
        
        # Analyze each goal kick
        for idx, goal_kick in team_goal_kicks.iterrows():
            kick_time = goal_kick['time']
            
            # Find all events for this team after the goal kick within a reasonable time window
            # (using 120 seconds as a generous upper bound for establishing possession)
            post_kick_events = team_events[
                (team_events['time'] > kick_time) & 
                (team_events['time'] <= kick_time + 120)
            ]
            
            # Skip if no events after the goal kick
            if len(post_kick_events) == 0:
                continue
            
            # Identify possession sequences after the goal kick
            possession_start_time = kick_time
            possession_pass_count = 1  # Start with 1 for the goal kick itself
            
            # Track if this goal kick led to established possession
            established_possession = False
            
            for _, event in post_kick_events.iterrows():
                current_time = event['time']
                
                # Check for possession break - if too much time has passed
                if current_time - possession_start_time > 60:
                    break
                
                # Check if this is another goal kick - using a safer approach
                is_another_goalkick = False
                if event['type_id'] == 1:
                    # Safely check if qualifiers exists and contains 124
                    qualifiers = event.get('qualifiers', None)
                    if qualifiers is not None and isinstance(qualifiers, (dict, list)) and 124 in qualifiers:
                        is_another_goalkick = True
                
                if is_another_goalkick:
                    break
                
                # Count passes
                if event['type_id'] == 1 and event.get('outcome', True):  # Default to True if outcome not available
                    possession_pass_count += 1
                
                # Check if we have established possession
                # Modified to remove player count check since player_id is not available
                possession_duration = current_time - possession_start_time
                if (possession_duration >= 8 and 
                    possession_pass_count >= 4):
                    established_possession = True
                    break
            
            # If this goal kick led to established possession, count it as successful
            if established_possession:
                successful_buildups += 1
                print(f"  Goal kick at time {kick_time} led to established possession")
        
        # Calculate the percentage
        buildup_percentage = (successful_buildups / total_goal_kicks * 100) if total_goal_kicks > 0 else 0.0
        
        # Store the results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_goal_kicks': total_goal_kicks,
            'successful_buildups': successful_buildups,
            'buildup_percentage': round(buildup_percentage, 2)
        })
        
        print(f"Game {game_id}, Team {team_id}: {successful_buildups}/{total_goal_kicks} successful buildups ({buildup_percentage:.2f}%)")
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    print("Buildup from goalkick percentage calculation completed.")
    
    return results_df

# Example usage:
buildup_stats = calculate_buildup_from_goalkick_percentage(progcarry_df2)

# Compute long_ball_% per team per game
variable_df17 = (
    buildup_stats.groupby(["game_id", "team_id"])["buildup_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"buildup_percentage": "buildup_%"})  # Fix column renaming
)

# Remove both columns
#variable_df = variable_df.drop(columns=["buildup_%_x", "buildup_%_y"])

# Importing long_ball_%
# Merge variable_df with long_ball_%
variable_df = variable_df.merge(
    variable_df17[['game_id', 'team_id', 'buildup_%']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "long_ball_%" column with 0
variable_df["buildup_%"] = variable_df["buildup_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 18
# Progressive passes from middle third %
"""
Quantifies a team's ability to advance play forward through passing from the 
central zone of the pitch. It is the percentage of passes initiated in the 
middle third of the pitch that successfully progress the ball toward the 
opponent's goal. 
Calculated as: (Number of progressive passes from middle third ÷ Total passes 
                attempted from middle third) × 100
"""

def calculate_progressive_passes_middle_third(df):
    """
    Calculate the percentage of progressive passes from the middle third of the pitch.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing pass data with:
        - game_id: match identifier
        - team_id: team identifier
        - start_x: x-coordinate of pass origin
        - end_x: x-coordinate of pass destination
        - progressive_pass: binary indicator (1 if pass is progressive, 0 otherwise)
        - type_id: event type (assuming 1 for passes)
    
    Returns:
    pd.DataFrame: DataFrame containing progressive pass statistics for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Filter only for passes (assuming type_id = 1 represents passes)
    passes = data[data['type_id'] == 1].copy()
    
    # Determine the middle third of the pitch
    # Assuming the pitch coordinates are normalized between 0-100
    # Middle third would be roughly between 33.3 and 66.7
    min_x = passes['start_x'].min()
    max_x = passes['start_x'].max()
    pitch_length = max_x - min_x
    
    middle_third_start = min_x + (pitch_length / 3)
    middle_third_end = min_x + (2 * pitch_length / 3)
    
    # Create flags for passes from the middle third
    passes['from_middle_third'] = (
        (passes['start_x'] >= middle_third_start) & 
        (passes['start_x'] < middle_third_end)
    )
    
    # Initialize result container
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), group in passes.groupby(['game_id', 'team_id']):
        # Get passes from the middle third
        middle_third_passes = group[group['from_middle_third']]
        
        # Calculate total passes from middle third
        total_middle_third_passes = len(middle_third_passes)
        
        # Skip if there are no passes from middle third
        if total_middle_third_passes == 0:
            results.append({
                'game_id': game_id,
                'team_id': team_id,
                'total_middle_third_passes': 0,
                'progressive_middle_third_passes': 0,
                'progressive_passes_percentage': 0.0
            })
            continue
        
        # Calculate progressive passes from middle third
        progressive_middle_third_passes = middle_third_passes['progressive_pass'].sum()
        
        # Calculate the percentage
        progressive_passes_percentage = (
            progressive_middle_third_passes / total_middle_third_passes * 100
        )
        
        # Store the results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_middle_third_passes': total_middle_third_passes,
            'progressive_middle_third_passes': int(progressive_middle_third_passes),
            'progressive_passes_percentage': round(progressive_passes_percentage, 2)
        })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by game_id and team_id for readability
    results_df = results_df.sort_values(['game_id', 'team_id']).reset_index(drop=True)
    
    return results_df

# Example usage:
progressive_passes_stats = calculate_progressive_passes_middle_third(progcarry_df2)

# Compute long_ball_% per team per game
variable_df18 = (
    progressive_passes_stats.groupby(["game_id", "team_id"])["progressive_passes_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"progressive_passes_percentage": "progressive_passes_%"})  # Fix column renaming
)

# Importing long_ball_%
# Merge variable_df with long_ball_%
variable_df = variable_df.merge(
    variable_df18[['game_id', 'team_id', 'progressive_passes_%']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "long_ball_%" column with 0
variable_df["progressive_passes_%"] = variable_df["progressive_passes_%"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 19
# Crosses per final third entry
"""
Quantifies a team's crossing tendency relative to their total attacking entries 
into the final third of the pitch. It is the frequency with which a team opts 
for crossing as an attacking strategy once they've entered the final third.
Calculated as: (Total number of crosses attempted ÷ Total number of final third 
entries)
"""

def calculate_crosses_per_final_third_entry(df):
    """
    Calculate 'crosses per final third entry' for each game and team.
    
    This metric quantifies a team's crossing tendency relative to their total attacking 
    entries into the final third of the pitch.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing event data with:
        - game_id: match identifier
        - team_id: team identifier
        - type_id: event type (1 for passes)
        - qualifiers: dictionary containing event qualifiers (2 indicates a cross)
        - start_x: x-coordinate of event origin
        - end_x: x-coordinate of event destination
    
    Returns:
    pd.DataFrame: DataFrame containing crosses per final third entry for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Determine the pitch dimensions for final third calculation
    min_x = data['start_x'].min()
    max_x = data['start_x'].max()
    pitch_length = max_x - min_x
    
    # Define the final third threshold (last 1/3 of the pitch)
    final_third_threshold = min_x + (2 * pitch_length / 3)
    
    # Initialize result container
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), group in data.groupby(['game_id', 'team_id']):
        # Identify final third entries
        # An entry is when an event starts outside the final third and ends inside the final third
        final_third_entries = group[
            (group['start_x'] < final_third_threshold) & 
            (group['end_x'] >= final_third_threshold)
        ]
        
        total_final_third_entries = len(final_third_entries)
        
        # Identify crosses (passes with qualifier 2)
        crosses = group[
            (group['type_id'] == 1) & 
            (group['qualifiers'].notna()) &
            (group['qualifiers'].apply(lambda x: isinstance(x, (dict, list)) and 2 in x))
        ]
        
        total_crosses = len(crosses)
        
        # Calculate crosses per final third entry
        # If there are no final third entries, set the metric to 0
        if total_final_third_entries > 0:
            crosses_per_entry = total_crosses / total_final_third_entries
        else:
            crosses_per_entry = 0.0
        
        # Store the results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_crosses': total_crosses,
            'total_final_third_entries': total_final_third_entries,
            'crosses_per_final_third_entry': round(crosses_per_entry, 3)
        })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by game_id and team_id for readability
    results_df = results_df.sort_values(['game_id', 'team_id']).reset_index(drop=True)
    
    return results_df

# Example usage:
crosses_stats = calculate_crosses_per_final_third_entry(progcarry_df2)
print(crosses_stats)


# Compute crosses_per_final_third_entry per team per game
variable_df19 = (
    crosses_stats.groupby(["game_id", "team_id"])["crosses_per_final_third_entry"]
    .sum()
    .reset_index()
)

# Importing crosses_per_final_third_entry
# Merge variable_df with crosses_per_final_third_entry
variable_df = variable_df.merge(
    variable_df19[['game_id', 'team_id', 'crosses_per_final_third_entry']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "crosses_per_final_third_entry" column with 0
variable_df["crosses_per_final_third_entry"] = variable_df["crosses_per_final_third_entry"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 20
# Dribbles per final third entry
"""
Quantifies a team's propensity to use individual dribbling skills as an attacking 
tool once they've advanced into the final third of the pitch. It is the frequency 
with which a team's players attempt to beat defenders through dribbling after 
entering the final third.
Calculated as: (Total number of dribble attempts in final third ÷ 
                Total number of final third entries)
"""

def calculate_dribbles_per_final_third_entry(df):
    """
    Calculate 'dribbles per final third entry' for each game and team.
    
    This metric quantifies a team's propensity to use individual dribbling skills 
    as an attacking tool once they've advanced into the final third of the pitch.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing event data with:
        - game_id: match identifier
        - team_id: team identifier
        - type_id: event type (4 for dribbles)
        - outcome: outcome of event (1 for successful dribbles)
        - start_x: x-coordinate of event origin
        - end_x: x-coordinate of event destination
    
    Returns:
    pd.DataFrame: DataFrame containing dribbles per final third entry for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Determine the pitch dimensions for final third calculation
    min_x = data['start_x'].min()
    max_x = data['start_x'].max()
    pitch_length = max_x - min_x
    
    # Define the final third threshold (last 1/3 of the pitch)
    final_third_threshold = min_x + (2 * pitch_length / 3)
    
    # Initialize result container
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), group in data.groupby(['game_id', 'team_id']):
        # Identify final third entries
        # An entry is when an event starts outside the final third and ends inside the final third
        final_third_entries = group[
            (group['start_x'] < final_third_threshold) & 
            (group['end_x'] >= final_third_threshold)
        ]
        
        total_final_third_entries = len(final_third_entries)
        
        # Identify successful dribbles in the final third
        final_third_dribbles = group[
            (group['type_id'] == 4) & 
            (group['outcome'] == 1) &
            (group['start_x'] >= final_third_threshold)  # Dribble starts in final third
        ]
        
        total_final_third_dribbles = len(final_third_dribbles)
        
        # Calculate dribbles per final third entry
        # If there are no final third entries, set the metric to 0
        if total_final_third_entries > 0:
            dribbles_per_entry = total_final_third_dribbles / total_final_third_entries
        else:
            dribbles_per_entry = 0.0
        
        # Store the results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_final_third_dribbles': total_final_third_dribbles,
            'total_final_third_entries': total_final_third_entries,
            'dribbles_per_final_third_entry': round(dribbles_per_entry, 3)
        })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by game_id and team_id for readability
    results_df = results_df.sort_values(['game_id', 'team_id']).reset_index(drop=True)
    
    return results_df

# Example usage:
dribbles_stats = calculate_dribbles_per_final_third_entry(progcarry_df2)
print(dribbles_stats)

# Compute dribbles_per_final_third_entry per team per game
variable_df20 = (
    dribbles_stats.groupby(["game_id", "team_id"])["dribbles_per_final_third_entry"]
    .sum()
    .reset_index()
)

# Importing dribbles_per_final_third_entry
# Merge variable_df with dribbles_per_final_third_entry
variable_df = variable_df.merge(
    variable_df20[['game_id', 'team_id', 'dribbles_per_final_third_entry']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "dribbles_per_final_third_entry" column with 0
variable_df["dribbles_per_final_third_entry"] = variable_df["dribbles_per_final_third_entry"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 21
# Box entries from crosses %
"""
It quantifies the proportion of a team's penalty area entries that come specifically 
from crossing situations rather than other attacking methods.It is the percentage 
of all successful entries into the opposition penalty box that originate from crosses
Calculated as: (Number of penalty box entries via crosses ÷ 
                Total number of penalty box entries) × 100
"""


def calculate_box_entries_from_crosses_percentage(df):
    """
    Calculate 'Box entries from crosses %' for each game and team.
    
    This metric quantifies the proportion of a team's penalty area entries
    that come specifically from crossing situations.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing event data with:
        - game_id: match identifier
        - team_id: team identifier
        - type_id: event type (1 for passes)
        - outcome: outcome of event (1 for successful passes)
        - qualifiers: dictionary containing event qualifiers (2 indicates a cross)
        - start_x: x-coordinate of event origin
        - end_x: x-coordinate of event destination
    
    Returns:
    pd.DataFrame: DataFrame containing box entries from crosses percentage for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Determine the pitch dimensions
    min_x = data['start_x'].min()
    max_x = data['start_x'].max()
    pitch_length = max_x - min_x
    
    # Define the penalty box threshold 
    # Typically 83% of the pitch length from the team's own goal
    # (standard penalty area is ~16-18% of pitch length from goal line)
    penalty_box_threshold = min_x + (0.83 * pitch_length)
    
    # Initialize result container
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), group in data.groupby(['game_id', 'team_id']):
        # Identify all penalty box entries
        # An entry is when an event ends inside the penalty box
        box_entries = group[group['end_x'] >= penalty_box_threshold]
        
        total_box_entries = len(box_entries)
        
        # Identify successful crosses that end in the penalty box
        cross_box_entries = group[
            (group['type_id'] == 1) & 
            (group['outcome'] == 1) &
            (group['qualifiers'].notna()) &
            (group['qualifiers'].apply(lambda x: isinstance(x, (dict, list)) and 2 in x)) &
            (group['end_x'] >= penalty_box_threshold)
        ]
        
        total_cross_box_entries = len(cross_box_entries)
        
        # Calculate box entries from crosses percentage
        # If there are no box entries, set the percentage to 0
        if total_box_entries > 0:
            cross_entries_percentage = (total_cross_box_entries / total_box_entries * 100)
        else:
            cross_entries_percentage = 0.0
        
        # Store the results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_box_entries': total_box_entries,
            'box_entries_from_crosses': total_cross_box_entries,
            'box_entries_from_crosses_percentage': round(cross_entries_percentage, 2)
        })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by game_id and team_id for readability
    results_df = results_df.sort_values(['game_id', 'team_id']).reset_index(drop=True)
    
    return results_df

# Example usage:
box_entries_stats = calculate_box_entries_from_crosses_percentage(progcarry_df2)
print(box_entries_stats)

# Compute box_entries_from_crosses per team per game
variable_df21 = (
    box_entries_stats.groupby(["game_id", "team_id"])["box_entries_from_crosses_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"box_entries_from_crosses_percentage": "box_entries_from_crosses"})
    
)

# Importing box_entries_from_crosses
# Merge variable_df with box_entries_from_crosses
variable_df = variable_df.merge(
    variable_df21[['game_id', 'team_id', 'box_entries_from_crosses']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "box_entries_from_crosses" column with 0
variable_df["box_entries_from_crosses"] = variable_df["box_entries_from_crosses"].fillna(0)

###############################################################################
###############################################################################
# Variáveis
# 22
# Box entries from carries %
"""
Quantifies the proportion of a team's penalty area entries that come specifically 
from players dribbling or carrying the ball into the box rather than other 
attacking methods. It is the percentage of all successful entries into the 
opposition penalty box that occur via a player carrying the ball (dribbling) 
across the boundary.
Calculated as: (Number of penalty box entries via carries/dribbles ÷ 
                Total number of penalty box entries) × 100
"""

def calculate_box_entries_from_carries_percentage(df):
    """
    Calculate 'Box entries from carries %' for each game and team.
    
    This metric quantifies the proportion of a team's penalty area entries
    that come specifically from players dribbling or carrying the ball into the box.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing event data with:
        - game_id: match identifier
        - team_id: team identifier
        - type_id: event type (4 for dribbles, 1000 for progressive carries, 2000 for carries)
        - outcome: outcome of event (1 for successful)
        - start_x: x-coordinate of event origin
        - end_x: x-coordinate of event destination
    
    Returns:
    pd.DataFrame: DataFrame containing box entries from carries percentage for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Determine the pitch dimensions
    min_x = data['start_x'].min()
    max_x = data['start_x'].max()
    pitch_length = max_x - min_x
    
    # Define the penalty box threshold 
    # Typically 83% of the pitch length from the team's own goal
    # (standard penalty area is ~16-18% of pitch length from goal line)
    penalty_box_threshold = min_x + (0.83 * pitch_length)
    
    # Initialize result container
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), group in data.groupby(['game_id', 'team_id']):
        # Identify all penalty box entries
        # An entry is when an event starts outside the penalty box and ends inside it
        box_entries = group[
            (group['start_x'] < penalty_box_threshold) & 
            (group['end_x'] >= penalty_box_threshold)
        ]
        
        total_box_entries = len(box_entries)
        
        # Identify box entries from carries/dribbles
        carry_box_entries = group[
            # Event starts outside the box and ends inside it
            (group['start_x'] < penalty_box_threshold) & 
            (group['end_x'] >= penalty_box_threshold) &
            # Event is either a dribble or a carry
            (
                # Successful dribbles
                ((group['type_id'] == 4) & (group['outcome'] == 1)) |
                # Progressive carries
                (group['type_id'] == 1000) |
                # Regular carries
                (group['type_id'] == 2000)
            )
        ]
        
        total_carry_box_entries = len(carry_box_entries)
        
        # Calculate box entries from carries percentage
        # If there are no box entries, set the percentage to 0
        if total_box_entries > 0:
            carry_entries_percentage = (total_carry_box_entries / total_box_entries * 100)
        else:
            carry_entries_percentage = 0.0
        
        # Store the results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_box_entries': total_box_entries,
            'box_entries_from_carries': total_carry_box_entries,
            'box_entries_from_carries_percentage': round(carry_entries_percentage, 2)
        })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by game_id and team_id for readability
    results_df = results_df.sort_values(['game_id', 'team_id']).reset_index(drop=True)
    
    return results_df

# Example usage:
carry_entries_stats = calculate_box_entries_from_carries_percentage(progcarry_df2)
print(carry_entries_stats)


# Compute box_entries_from_crosses per team per game
variable_df22 = (
    carry_entries_stats.groupby(["game_id", "team_id"])["box_entries_from_carries_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"box_entries_from_carries_percentage": "box_entries_from_carries"})
    
)

# Importing box_entries_from_carries
# Merge variable_df with box_entries_from_carries
variable_df = variable_df.merge(
    variable_df22[['game_id', 'team_id', 'box_entries_from_carries']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "box_entries_from_carries" column with 0
variable_df["box_entries_from_carries"] = variable_df["box_entries_from_carries"].fillna(0)



###############################################################################
###############################################################################
###############################################################################
###############################################################################
# Variáveis
# Chance creation
# 23
# Shots from sustained attacks %
"""
Quantifies the proportion of a team's shots that originate from methodical, 
controlled possession sequences rather than from transitions, set pieces, or 
direct play. It is the percentage of total shots that result from extended 
possession-based attacking sequences.
Calculated as: (Number of shots from sustained possession ÷ 
                Total shots taken) × 100
Sustained attack: possession lasting min 9 seconds before the shot, involves 
min 4 consecutive completed passes prior to the shot.
"""

def calculate_shots_from_sustained_attacks(df):
    """
    Calculate 'Shots from sustained attacks %' for each game and team.
    
    This metric quantifies the proportion of a team's shots that originate 
    from methodical, controlled possession sequences rather than from 
    transitions, set pieces, or direct play.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing event data with:
        - game_id: match identifier
        - team_id: team identifier
        - possessionId: identifier for each possession chain
        - first_chain: marks beginning of possession chain (1)
        - last_chain: marks end of possession chain (1)
        - time: game time in seconds
        - type_id: event type (13, 14, 15, 16 for shots)
        - qualifiers: dictionary containing event qualifiers (9 for penalties)
    
    Returns:
    pd.DataFrame: DataFrame containing shots from sustained attacks percentage for each game_id and team_id
    """
    # Create a copy to avoid modifying the original DataFrame
    data = df.copy()
    
    # Ensure data is sorted properly for sequence analysis
    data = data.sort_values(['game_id', 'team_id', 'possessionId', 'time'])
    
    # Initialize result container
    results = []
    
    # Process each game and team combination
    for (game_id, team_id), group in data.groupby(['game_id', 'team_id']):
        print(f"Processing game_id: {game_id}, team_id: {team_id}")
        
        # Identify all shots (excluding penalties)
        shots = group[group['type_id'].isin([13, 14, 15, 16])]
        
        # Filter out penalties
        np_shots = shots[
            ~shots['qualifiers'].apply(
                lambda x: isinstance(x, (dict, list)) and 9 in x and x[9] == True
            )
        ]
        
        total_shots = len(np_shots)
        
        if total_shots == 0:
            print(f"No shots found for game_id: {game_id}, team_id: {team_id}")
            results.append({
                'game_id': game_id,
                'team_id': team_id,
                'total_shots': 0,
                'shots_from_sustained_attacks': 0,
                'sustained_attacks_percentage': 0.0
            })
            continue
        
        # Counter for shots from sustained attacks
        sustained_attack_shots = 0
        
        # Analyze each shot
        for _, shot in np_shots.iterrows():
            shot_time = shot['time']
            possession_id = shot['possessionId']
            
            # Get all events in this possession chain
            possession_events = group[group['possessionId'] == possession_id].sort_values('time')
            
            # If no events found, skip
            if len(possession_events) == 0:
                continue
            
            # Find the start of the possession
            possession_start = possession_events.iloc[0]['time']
            
            # Calculate possession duration before the shot
            possession_duration = shot_time - possession_start
            
            # Count passes in this possession before the shot
            passes_before_shot = possession_events[
                (possession_events['type_id'] == 1) &  # Pass events
                (possession_events['time'] < shot_time)  # Before the shot
            ]
            
            # Count consecutive successful passes
            consecutive_passes = 0
            max_consecutive_passes = 0
            
            for _, pass_event in passes_before_shot.iterrows():
                # If pass is successful (assuming outcome=1 means success)
                if pass_event.get('outcome', 1) == 1:  # Default to 1 if outcome not available
                    consecutive_passes += 1
                else:
                    # Reset consecutive passes counter if pass fails
                    consecutive_passes = 0
                
                # Update maximum consecutive passes
                max_consecutive_passes = max(max_consecutive_passes, consecutive_passes)
            
            # Check if this shot came from a sustained attack
            if possession_duration >= 9 and max_consecutive_passes >= 5:
                sustained_attack_shots += 1
                print(f"  Shot at time {shot_time} came from sustained attack " +
                      f"(duration: {possession_duration:.1f}s, max consecutive passes: {max_consecutive_passes})")
        
        # Calculate percentage
        sustained_attacks_percentage = (sustained_attack_shots / total_shots * 100)
        
        # Store the results
        results.append({
            'game_id': game_id,
            'team_id': team_id,
            'total_shots': total_shots,
            'shots_from_sustained_attacks': sustained_attack_shots,
            'sustained_attacks_percentage': round(sustained_attacks_percentage, 2)
        })
        
        print(f"Game {game_id}, Team {team_id}: {sustained_attack_shots}/{total_shots} " +
              f"shots from sustained attacks ({sustained_attacks_percentage:.2f}%)")
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by game_id and team_id for readability
    results_df = results_df.sort_values(['game_id', 'team_id']).reset_index(drop=True)
    
    print("Shots from sustained attacks calculation completed.")
    
    return results_df

# Example usage:
sustained_shots_stats = calculate_shots_from_sustained_attacks(progcarry_df2)
print(sustained_shots_stats)


# Compute box_entries_from_crosses per team per game
variable_df23 = (
    sustained_shots_stats.groupby(["game_id", "team_id"])["sustained_attacks_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"sustained_attacks_percentage": "sustained_attacks"})
    
)

# Importing sustained_attacks
# Merge variable_df with sustained_attacks
variable_df = variable_df.merge(
    variable_df23[['game_id', 'team_id', 'sustained_attacks']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "sustained_attacks" column with 0
variable_df["sustained_attacks"] = variable_df["sustained_attacks"].fillna(0)



###############################################################################
###############################################################################
# Variáveis
# 24
# Shots from direct attacks %
"""
Quantifies the proportion of a team's shots that originate from rapid, vertical 
progression with minimal possession phases rather than methodical build-up play.
It is the percentage of total shots that result from direct attacking sequences 
characterized by vertical progression and minimal passing.
Calculated as: (Number of shots from direct attacks ÷ Total shots taken) × 100
Direct attack: takes max 8 seconds from possession gain to shot, max 
3 passes.
"""

def calculate_direct_attack_shots_percentage(progcarry_df2):
    # Create a copy to avoid modifying the original dataframe
    df = progcarry_df2.copy()
    
    # Step 1: Identify the start time of each possession chain
    possession_starts = df[df['first_chain'] == 1][['game_id', 'team_id', 'possessionId', 'time']].copy()
    possession_starts.rename(columns={'time': 'possession_start_time'}, inplace=True)
    
    # Step 2: Identify the end time of each possession chain
    possession_ends = df[df['last_chain'] == 1][['game_id', 'team_id', 'possessionId', 'time']].copy()
    possession_ends.rename(columns={'time': 'possession_end_time'}, inplace=True)
    
    # Step 3: Merge start and end times for each possession chain
    possession_times = pd.merge(
        possession_starts, 
        possession_ends, 
        on=['game_id', 'team_id', 'possessionId'], 
        how='inner'
    )
    
    # Step 4: Count passes in each possession chain
    pass_counts = df.groupby(['game_id', 'team_id', 'possessionId']).size().reset_index(name='pass_count')
    
    # Step 5: Merge pass counts with possession times
    possession_data = pd.merge(
        possession_times, 
        pass_counts, 
        on=['game_id', 'team_id', 'possessionId'], 
        how='inner'
    )
    
    # Step 6: Calculate possession duration
    possession_data['duration'] = possession_data['possession_end_time'] - possession_data['possession_start_time']
    
    # Step 7: Identify shots in the dataframe
    # Filter for events that are shots (type_id in [13, 14, 15, 16])
    shots = df[df['type_id'].isin([13, 14, 15, 16])].copy()
    
    # Exclude penalties (qualifiers contains 9)
    np_shots = shots[~shots['qualifiers'].apply(lambda x: 9 in x and x[9] == True if isinstance(x, dict) and 9 in x else False)]
    
    # Step 8: Add possession information to shots
    shot_possessions = []
    
    for idx, shot in np_shots.iterrows():
        game_id = shot['game_id']
        team_id = shot['team_id']
        shot_time = shot['time']
        
        # Find the possession that contains this shot
        matching_possessions = possession_data[
            (possession_data['game_id'] == game_id) &
            (possession_data['team_id'] == team_id) & 
            (possession_data['possession_start_time'] <= shot_time) & 
            (possession_data['possession_end_time'] >= shot_time)
        ]
        
        if not matching_possessions.empty:
            possession_id = matching_possessions.iloc[0]['possessionId']
            duration = matching_possessions.iloc[0]['duration']
            pass_count = matching_possessions.iloc[0]['pass_count']
            
            # Check if this is a direct attack (≤8 seconds, ≤4 passes)
            is_direct = (duration <= 8) and (pass_count <= 4)
            
            shot_possessions.append({
                'game_id': game_id,
                'team_id': team_id,
                'possessionId': possession_id,
                'is_direct_attack': is_direct
            })
    
    if not shot_possessions:
        return pd.DataFrame(columns=['game_id', 'team_id', 'total_shots', 'direct_attack_shots', 'direct_attack_percentage'])
    
    # Step 9: Create a dataframe of shots with possession data
    shots_possession_df = pd.DataFrame(shot_possessions)
    
    # Step 10: Calculate direct attack shots percentage for each game and team
    result = shots_possession_df.groupby(['game_id', 'team_id']).agg(
        total_shots=('possessionId', 'count'),
        direct_attack_shots=('is_direct_attack', 'sum')
    ).reset_index()
    
    # Step 11: Calculate the percentage
    result['direct_attack_percentage'] = (result['direct_attack_shots'] / result['total_shots'] * 100).round(2)
    
    return result

# Example usage:
direct_attack_stats = calculate_direct_attack_shots_percentage(progcarry_df2)
print(direct_attack_stats)

# Compute box_entries_from_crosses per team per game
variable_df24 = (
    direct_attack_stats.groupby(["game_id", "team_id"])["direct_attack_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"direct_attack_percentage": "direct_attack"})
    
)

# Importing direct_attack
# Merge variable_df with direct_attack
variable_df = variable_df.merge(
    variable_df24[['game_id', 'team_id', 'direct_attack']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "direct_attack" column with 0
variable_df["direct_attack"] = variable_df["direct_attack"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 25
# Shots per final third pass
"""
Quantifies a team's directness and shot generation rate relative to their passing 
volume in advanced areas. It is the ratio of shots generated compared to the 
number of passes a team completes in the final third.
Calculated as: (Total shots taken ÷ Total passes completed in the final third)
"""

def calculate_shots_per_final_third_pass(data_df):
    # Create a copy of the dataframe to work with
    df = data_df.copy()
    
    # Define the final third of the pitch (assuming pitch length is standardized to 100)
    final_third_threshold = 66.7  # Represents 2/3 of the pitch length
    
    # Filter for successful passes in the final third
    final_third_passes = df[(df['type_id'] == 1) & 
                            (df['outcome'] == 1) & 
                            (df['end_x'] >= final_third_threshold)]
    
    # Count final third passes by game_id and team_id
    final_third_pass_counts = final_third_passes.groupby(['game_id', 'team_id']).size().reset_index(name='final_third_passes')
    
    # Filter for shots (excluding penalties)
    shots = df[df['type_id'].isin([13, 14, 15, 16])]
    
    # Exclude penalties
    np_shots = shots[~shots['qualifiers'].apply(lambda x: 9 in x and x[9] == True)]
    
    # Count shots by game_id and team_id
    shot_counts = np_shots.groupby(['game_id', 'team_id']).size().reset_index(name='shots')
    
    # Merge the final third passes and shots dataframes
    merged_df = pd.merge(final_third_pass_counts, shot_counts, on=['game_id', 'team_id'], how='outer').fillna(0)
    
    # Calculate shots per final third pass
    merged_df['shots_per_final_third_pass'] = merged_df['shots'] / merged_df['final_third_passes']
    
    # Handle division by zero cases
    merged_df['shots_per_final_third_pass'] = merged_df['shots_per_final_third_pass'].replace([np.inf, -np.inf], np.nan)
    
    return merged_df[['game_id', 'team_id', 'shots', 'final_third_passes', 'shots_per_final_third_pass']]

# Example usage:
result = calculate_shots_per_final_third_pass(progcarry_df2)
print(result)
    
# Compute box_entries_from_crosses per team per game
variable_df25 = (
    result.groupby(["game_id", "team_id"])["shots_per_final_third_pass"]
    .sum()
    .reset_index()
    
)

# Importing shots_per_final_third_pass
# Merge variable_df with shots_per_final_third_pass
variable_df = variable_df.merge(
    variable_df25[['game_id', 'team_id', 'shots_per_final_third_pass']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "shots_per_final_third_pass" column with 0
variable_df["shots_per_final_third_pass"] = variable_df["shots_per_final_third_pass"].fillna(0)


###############################################################################
###############################################################################
# Variáveis
# 26
# Shots from outside the box %
"""
Quantifies the proportion of a team's total shots that are taken from beyond 
the penalty area boundary. It is the percentage of a team's total shots that 
originate from positions outside the 18-yard box.
Calculated as: (Number of shots taken from outside the penalty area ÷ 
                Total shots taken) × 100
"""

def calculate_shots_from_outside_box_percentage(data_df):
    # Create a copy of the dataframe to work with
    df = data_df.copy()
    
    # Filter for shots (excluding penalties)
    shots = df[df['type_id'].isin([13, 14, 15, 16])]
    np_shots = shots[~shots['qualifiers'].apply(lambda x: 9 in x and x[9] == True)]
    
    # Define the penalty box dimensions (standard dimensions in a normalized 100x100 pitch)
    # Assuming coordinates are normalized where x goes from 0 to 100 (left to right)
    # and y goes from 0 to 100 (bottom to top)
    # The penalty box typically extends 16.5 yards from the goal line, which is about 18% of field length
    # Width is typically 44 yards which is about 40% of field width
    
    box_x_threshold = 83  # Assuming penalty box starts at x=83 (adjust based on your coordinate system)
    box_y_min = 30  # Lower y-boundary of penalty box
    box_y_max = 70  # Upper y-boundary of penalty box
    
    # Identify shots from outside the box
    # A shot is outside the box if:
    # 1. It starts before the penalty box (x < box_x_threshold)
    # OR
    # 2. It starts outside the y-range of the penalty box
    np_shots['is_outside_box'] = (
        (np_shots['start_x'] < box_x_threshold) | 
        (np_shots['start_y'] < box_y_min) | 
        (np_shots['start_y'] > box_y_max)
    )
    
    # Group by game_id and team_id to count shots
    shot_stats = np_shots.groupby(['game_id', 'team_id']).agg(
        total_shots=('type_id', 'count'),
        outside_box_shots=('is_outside_box', 'sum')
    ).reset_index()
    
    # Calculate percentage of shots from outside the box
    shot_stats['shots_outside_box_percentage'] = (
        shot_stats['outside_box_shots'] / shot_stats['total_shots'] * 100
    ).round(2)
    
    # Handle cases where total_shots is 0
    shot_stats['shots_outside_box_percentage'] = shot_stats['shots_outside_box_percentage'].replace([np.inf, -np.inf], np.nan)
    
    return shot_stats[['game_id', 'team_id', 'total_shots', 'outside_box_shots', 'shots_outside_box_percentage']]

# Example usage:
result = calculate_shots_from_outside_box_percentage(progcarry_df2)
print(result)


# Compute box_entries_from_crosses per team per game
variable_df26 = (
    result.groupby(["game_id", "team_id"])["shots_outside_box_percentage"]
    .sum()
    .reset_index()
    .rename(columns={"shots_outside_box_percentage": "shots_outside_box"})
)

# Importing shots_outside_box
# Merge variable_df with shots_outside_box
variable_df = variable_df.merge(
    variable_df26[['game_id', 'team_id', 'shots_outside_box']],
    on=['game_id', 'team_id'], 
    how='left')

# Replace NaN values in the "shots_outside_box" column with 0
variable_df["shots_outside_box"] = variable_df["shots_outside_box"].fillna(0)


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
variable_df_new = variable_df.copy()

def add_possession_percentage(variable_df_new, possession_df):
    """
    Add possession percentage and opponent possession percentage to variable_df_new.
    
    Parameters:
    variable_df_new (pd.DataFrame): DataFrame containing game and team data
    possession_df (pd.DataFrame): DataFrame containing possession data
    
    Returns:
    pd.DataFrame: variable_df_new with added possession percentage columns
    """
    # Create a copy to avoid modifying the original DataFrame
    df = variable_df_new.copy()
    
    # Initialize possession percentage columns
    df['possession_percentage'] = None
    df['opponent_possession_percentage'] = None
    
    # For each row in variable_df_new
    for idx, row in df.iterrows():
        game_id = row['game_id']
        team_id = row['team_id']
        
        # Get corresponding possession data
        game_possession = possession_df[possession_df['game_id'] == game_id]
        
        if len(game_possession) > 0:
            possession_row = game_possession.iloc[0]
            
            # If team is home team
            if team_id == possession_row['home_team_id']:
                df.at[idx, 'possession_percentage'] = possession_row['home_team_possession_per']
                df.at[idx, 'opponent_possession_percentage'] = possession_row['away_team_possession_per']
            
            # If team is away team
            elif team_id == possession_row['away_team_id']:
                df.at[idx, 'possession_percentage'] = possession_row['away_team_possession_per']
                df.at[idx, 'opponent_possession_percentage'] = possession_row['home_team_possession_per']
    
    return df

variable_df_new = add_possession_percentage(variable_df_new, possession)

# Reorder "opponent_possession" to be the third column
columns = variable_df_new.columns.tolist()
columns.remove("opponent_possession_percentage")  # Remove it from the original spot
columns.insert(5, "opponent_possession_percentage")  # Insert it as the third column
variable_df_new = variable_df_new[columns]

# Reordering "team_possession", "opponent_possession" 
columns = variable_df_new.columns.tolist()
columns.remove("possession_percentage")  # Remove it from the original spot
columns.insert(5, "possession_percentage")  # Insert it as the third column
variable_df_new = variable_df_new[columns]

#Renaming possession columns
variable_df_new = variable_df_new.rename(columns={
    "opponent_possession_percentage": "opponent_possession",
    "possession_percentage": "team_possession"
})


# Sort variable_df_new by "game_id" and "team_id" in ascending order
#variable_df_new = variable_df_new.sort_values(by=["game_id", "team_id"], ascending=[True, True]).reset_index(drop=True)

############################################################################################
############################################################################################

# REMOVED Adjusting for Possession
# REMOVED Adjusting for Possession
# REMOVED Adjusting for Possession
# REMOVED Adjusting for Possession
# REMOVED Adjusting for Possession
# REMOVED Adjusting for Possession
# REMOVED Adjusting for Possession

###########################################################################
###########################################################################
# Adding season and league columns

# Add "Temporada" column with the value 2024 as the first column in the dataframe
variable_df_new.insert(0, "Temporada", 2024)

# Add "Temporada" column with the value 2024 as the first column in the dataframe
#variable_df_new.insert(0, "Liga", "BRA1")

###########################################################################
###########################################################################

# Numbering rounds
# 1. Sort the dataframe by 'game_id' and reset the index
variable_df_new = variable_df_new.sort_values(['date', 'game_id'], ascending=[True, True]).reset_index(drop=True)

# 2. Create the 'round' column (each round covers 20 rows)
variable_df_new['round'] = (variable_df_new.index // 20) + 1

# 3. Relocate the 'round' column to column position 1 (i.e., the second column)
cols = list(variable_df_new.columns)
cols.remove('round')      # Remove 'round' from its current position
cols.insert(1, 'round')   # Insert 'round' at index 1
variable_df_new = variable_df_new[cols]

###########################################################################
###########################################################################


#Add Place

# Creating place column
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

# Relocate place column 
all_columns = list(variable_df_new.columns)
place_column = all_columns.pop(-1)  # Remove from last position
all_columns.insert(9, place_column)  # Insert at position 8
variable_df_new = variable_df_new[all_columns]  # Reorder dataframe with new column order

# Create .csv file
variable_df_new.to_csv("play_style_metrics.csv")

###########################################################################
###########################################################################


#Bulding team_id game analysis (same club analysis)

# Initialize the result dataframe outside the loop
variable_df_team_z = pd.DataFrame()

# Group by 'team_id' and apply z-score transformation independently
for team_id, group in variable_df_new.groupby("team_id"):
    # Repeat columns [0:9] (you were using :9 which includes 9 columns, not 8)
    base_columns = group.iloc[:, :10].copy()
    
    # Apply z-score transformation to columns [9:] with error handling
    numeric_columns = group.iloc[:, 10:].select_dtypes(include=np.number)
    
    # Check if there are numeric columns before applying zscore
    if not numeric_columns.empty:
        # Apply zscore with nan_policy='omit' to handle NaN values
        try:
            zscore_columns = numeric_columns.apply(lambda x: zscore(x, nan_policy='omit'))
            zscore_columns = pd.DataFrame(zscore_columns, index=group.index)
            zscore_columns.rename(columns=lambda col: f"{col}_z", inplace=True)
            
            # Combine the repeated columns with the z-score transformed columns
            função_z = pd.concat([base_columns, zscore_columns], axis=1)
            
            # Append to the final dataframe
            variable_df_team_z = pd.concat([variable_df_team_z, função_z], axis=0)
        except Exception as e:
            print(f"Error in team_id {team_id}: {e}")
            # For columns that cause errors, you can either skip them or handle differently
            # Here we're just printing the error
    else:
        print(f"No numeric columns found for team_id {team_id}")
# Reset index after concatenation
variable_df_team_z.reset_index(drop=True, inplace=True)

###########################################################################
###########################################################################

# Inverting the sign of inverted metrics
variable_df_team_z["PPDA_z"] = -1*variable_df_team_z["PPDA_z"]
variable_df_team_z["avg_time_to_defensive_action_z"] = -1*variable_df_team_z["avg_time_to_defensive_action_z"]
variable_df_team_z["transition_vulnerability_index_z"] = -1*variable_df_team_z["transition_vulnerability_index_z"]
variable_df_team_z["opposition_final_third_entries_10s_z"] = -1*variable_df_team_z["opposition_final_third_entries_10s_z"]
variable_df_team_z["opposition_box_entries_10s_z"] = -1*variable_df_team_z["opposition_box_entries_10s_z"]
variable_df_team_z["time_to_progression_seconds_z"] = -1*variable_df_team_z["time_to_progression_seconds_z"]

###########################################################################
###########################################################################

# Creating qualities columns
# Define the columns to average for each metric
defence_metrics = ["defensive_height_z", "high_recoveries_pct_z", "PPDA_z", "fouls_in_attacking_half_pct_z",
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
variable_df_team_z["defence_z"] = variable_df_team_z[defence_metrics].mean(axis=1)
variable_df_team_z["defensive_transition_z"] = variable_df_team_z[defensive_transition_metrics].mean(axis=1)
variable_df_team_z["attacking_transition_z"] = variable_df_team_z[attacking_transition_metrics].mean(axis=1)
variable_df_team_z["attacking_z"] = variable_df_team_z[attacking_metrics].mean(axis=1)
variable_df_team_z["chance_creation_z"] = variable_df_team_z[chance_creation_metrics].mean(axis=1)

# Get a list of the current columns
cols = list(variable_df_team_z.columns)

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
variable_df_team_z = variable_df_team_z[cols]

# Renaming columns
columns_to_rename = ["round", "date", "fixture", "team_name",
                     "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                     "attacking_transition_z", "attacking_z", "chance_creation_z", "defensive_height_z", 
                     "high_recoveries_pct_z", "PPDA_z", "fouls_in_attacking_half_pct_z","defensive_intensity_z",	
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

# Rename columns in variable_df_team_z
variable_df_team_z = variable_df_team_z.rename(columns=rename_dict)

# Sort the dataframe by 'game_id' and reset the index
variable_df_team_z = variable_df_team_z.sort_values(['rodada', 'data'], ascending=[False, False]).reset_index(drop=True)

#Making a csv file
variable_df_team_z.to_csv("play_style_team.csv")
###########################################################################
###########################################################################

# Rerunning columns from Master Code
# Calculating z-scores per round
# Create a new dataframe for z-scores
variable_df_round_z = pd.DataFrame()

###########################################################################
###########################################################################

#Bulding round game analysis (all club analysis)

# Group by 'round' and apply z-score transformation independently
for round, group in variable_df_new.groupby("team_id"):
    # Repeat columns [0:15]
    base_columns = group.iloc[:, :10].copy()
    # Apply z-score transformation to columns [7:] and rename with '_z' suffix
    zscore_columns = group.iloc[:, 10:].apply(zscore)
    zscore_columns.rename(columns=lambda col: f"{col}_z", inplace=True)
    # Combine the repeated columns with the z-score transformed columns
    função_z = pd.concat([base_columns, zscore_columns], axis=1)
    # Append to the final dataframe
    variable_df_round_z = pd.concat([variable_df_round_z, função_z], axis=0)

# Reset index after concatenation
variable_df_round_z.reset_index(drop=True, inplace=True)

###########################################################################
###########################################################################

# Inverting the sign of inverted metrics
variable_df_round_z["PPDA_z"] = -1*variable_df_round_z["PPDA_z"]
variable_df_round_z["avg_time_to_defensive_action_z"] = -1*variable_df_round_z["avg_time_to_defensive_action_z"]
variable_df_round_z["transition_vulnerability_index_z"] = -1*variable_df_round_z["transition_vulnerability_index_z"]
variable_df_round_z["opposition_final_third_entries_10s_z"] = -1*variable_df_round_z["opposition_final_third_entries_10s_z"]
variable_df_round_z["opposition_box_entries_10s_z"] = -1*variable_df_round_z["opposition_box_entries_10s_z"]
variable_df_round_z["time_to_progression_seconds_z"] = -1*variable_df_round_z["time_to_progression_seconds_z"]

###########################################################################
###########################################################################

# Creating qualities columns
# Define the columns to average for each metric
defence_metrics = ["defensive_height_z", "high_recoveries_pct_z", "fouls_in_attacking_half_pct_z",
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
variable_df_round_z["defence_z"] = variable_df_round_z[defence_metrics].mean(axis=1)
variable_df_round_z["defensive_transition_z"] = variable_df_round_z[defensive_transition_metrics].mean(axis=1)
variable_df_round_z["attacking_transition_z"] = variable_df_round_z[attacking_transition_metrics].mean(axis=1)
variable_df_round_z["attacking_z"] = variable_df_round_z[attacking_metrics].mean(axis=1)
variable_df_round_z["chance_creation_z"] = variable_df_round_z[chance_creation_metrics].mean(axis=1)

# Get a list of the current columns
cols = list(variable_df_round_z.columns)

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
variable_df_round_z = variable_df_round_z[cols]

# Renaming columns
# Renaming columns
# Renaming columns
columns_to_rename = ["round", "date", "fixture", "team_name",
                     "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                     "attacking_transition_z", "attacking_z", "chance_creation_z", "defensive_height_z", 
                     "high_recoveries_pct_z", "PPDA_z", "fouls_in_attacking_half_pct_z","defensive_intensity_z",	
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

# Rename columns in variable_df_z_team
variable_df_round_z = variable_df_round_z.rename(columns=rename_dict)

# Sort the dataframe by 'game_id' and reset the index
variable_df_round_z = variable_df_round_z.sort_values(['rodada', 'data'], ascending=[False, False]).reset_index(drop=True)

#Making a csv file
variable_df_round_z.to_csv("play_style_round.csv")

###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################

