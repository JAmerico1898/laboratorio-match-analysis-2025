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

#Collecting data

ws = sd.WhoScored(leagues="BRA-Brasileirão", seasons=2025)

# Scrape all games and return a OptaLoader object
loader = ws.read_events(output_fmt='loader')

# Game events
events = ws.read_events()

# Game schedule
df_schedule = ws.read_schedule()

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
# CARRIES & PROGRESSIVE CARRIES — plataforma-scouting rule (docs/variable_consistency_decisions.md D1), taken from
# the reference stage-01 frame that possession_chain.py writes (ref_pipeline.REF_STAGE01):
#   carry (2000): same game/period/chain/team, forward x gain > 5 Opta units, gap <= 30 s, not after a failed pass,
#     not into a defensive action/duel or a committed foul;
#   progressive carry (1000): a carry that starts at x >= 50.
# A reference carry row carries the WhoScored id of the event it leads into; it is inserted just before that event.
# Reference chain columns (chain_id, is_chain_team, chain_first, chain_last) are attached to every row; events the
# reference preprocess drops (e.g. saves, admin events) get chain_id NaN.
import team_concepts as tc
from ref_pipeline import REF_STAGE01

progcarry_df = df.copy()
progcarry_df.sort_values(["game_id", "period_id", "time", "event_id"], kind="mergesort", inplace=True)
progcarry_df.reset_index(drop=True, inplace=True)
progcarry_df["event_index"] = np.arange(len(progcarry_df), dtype=float)

_ref = pd.read_parquet(REF_STAGE01, columns=["game_id", "id", "event_idx", "type_id", "team_id", "period_id", "x", "y",
                                             "end_x", "end_y", "chain_id", "is_chain_team", "chain_first", "chain_last"])
_ref = _ref.rename(columns={"id": "event_id"})
_ref_carry = _ref["type_id"].isin(tc.CARRY_TYPES)
_chain_cols = ["chain_id", "is_chain_team", "chain_first", "chain_last"]

progcarry_df = progcarry_df.merge(_ref.loc[~_ref_carry, ["game_id", "event_id", "event_idx"] + _chain_cols],
                                  on=["game_id", "event_id"], how="left", validate="one_to_one")
# Reference event order (event_idx = JSON order): the loss/regain definitions look at the next and previous event, so
# same-second events must be in the reference's order. An event the reference drops keeps its place after the
# preceding event.
_idx = progcarry_df["event_idx"].astype(float)
progcarry_df["event_index"] = _idx.fillna(_idx.groupby(progcarry_df["game_id"]).ffill() + 0.25).fillna(-1.0)
progcarry_df.drop(columns="event_idx", inplace=True)

_c = _ref.loc[_ref_carry].reset_index(drop=True)
_lead = progcarry_df.drop_duplicates(["game_id", "event_id"]).set_index(["game_id", "event_id"])
_keys = pd.MultiIndex.from_frame(_c[["game_id", "event_id"]])
_missing = ~_keys.isin(_lead.index)
if _missing.any():
    raise RuntimeError(f"{int(_missing.sum())} reference carries lead into events missing from progcarry_df")
_l = _lead.loc[_keys]

carry_rows = pd.DataFrame({
    "type_name":     np.where(_c["type_id"] == 1000, "progressive carry", "carry"),
    "type_id":       _c["type_id"].to_numpy(),
    "start_x":       _c["x"].to_numpy(),
    "start_y":       _c["y"].to_numpy(),
    "end_x":         _c["end_x"].to_numpy(),
    "end_y":         _c["end_y"].to_numpy(),
    "team_id":       _c["team_id"].to_numpy(),
    "team_name":     _l["team_name"].to_numpy(),
    "game_id":       _c["game_id"].to_numpy(),
    "fixture":       _l["fixture"].to_numpy(),
    "period_id":     _c["period_id"].to_numpy(),
    "event_id":      _c["event_id"].to_numpy(),
    "outcome":       True,  # reference sets carry outcome = 1 (B11)
    "touch":         True,
    "goal":          False,
    "shot":          False,
    "timestamp":     _l["timestamp"].to_numpy(),
    "minute":        _l["minute"].to_numpy(),
    "second":        _l["second"].to_numpy(),
    "time":          _l["time"].to_numpy(),
    "event_index":   _l["event_index"].to_numpy() - 0.5,
    "chain_id":      _c["chain_id"].to_numpy(),
    "is_chain_team": _c["is_chain_team"].to_numpy(),
    "chain_first":   False,
    "chain_last":    False,
})

progcarry_df = pd.concat([progcarry_df, carry_rows], ignore_index=True)
progcarry_df.sort_values(["game_id", "period_id", "event_index"], kind="mergesort", inplace=True)
progcarry_df.reset_index(drop=True, inplace=True)
progcarry_df = tc.add_qualifier_flags(progcarry_df)

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
#xa_df = pd.read_parquet("xA_brasileirao_2025.parquet")
#xa_df.rename(columns={"teamId": "team_id", "id": "event_id"}, inplace=True)

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xG — loaded from pre-built parquet (produced by xG_brasileirao.py)
xg_df = pd.read_parquet("xG_brasileirao_2025.parquet")
xg_df.rename(columns={"teamId": "team_id", "id": "event_id"}, inplace=True)

# Merge xG once, onto shot rows only (type_id 13-16): a carry row shares its event_id with the event it
# leads into and must not inherit that shot's xG. Own goals are not in xg_df and get 0.
progcarry_df = progcarry_df.merge(
    xg_df[["game_id", "event_id", "xG"]],
    on=["game_id", "event_id"],
    how="left",
)
progcarry_df["xG"] = progcarry_df["xG"].where(progcarry_df["type_id"].isin([13, 14, 15, 16])).fillna(0.0)
if (progcarry_df["xG"] != 0).sum() == 0:
    raise RuntimeError("xG merge produced all-zero xG column — event_id key space drift between xg_df and progcarry_df")

##########################################################################
##########################################################################
##########################################################################
##########################################################################

# xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###xThreat###

progcarry_df["game_id"] = pd.to_numeric(progcarry_df["game_id"], errors="coerce").astype("Int64")

# xT — loaded from pre-built parquet (produced by xT_brasileirao.py, plataforma-scouting models)
xt_df = pd.read_parquet("xT_brasileirao_2025.parquet")
xt_df.rename(columns={"teamId": "team_id", "id": "event_id"}, inplace=True)

# Merge xT into progcarry_df so all downstream variables have it:
#   xthreat          action xT (completed pass / take-on / carry; failed pass / take-on = 0)
#   xt_delta_cadeia  xT added over the team's previous completed action in the chain (missing = not scored)
# Carry rows are the reference carries themselves (D1), so each one matches its own xT row.
progcarry_df["is_carry"] = progcarry_df["type_id"].isin([1000, 2000])
progcarry_df = progcarry_df.merge(
    xt_df[["game_id", "team_id", "event_id", "is_carry", "xthreat", "xt_delta_cadeia"]],
    on=["game_id", "team_id", "event_id", "is_carry"],
    how="left",
    validate="many_to_one",
)
progcarry_df.drop(columns="is_carry", inplace=True)
progcarry_df["xthreat"] = progcarry_df["xthreat"].fillna(0.0)
if (progcarry_df["xthreat"] != 0).sum() == 0:
    raise RuntimeError("xT merge produced all-zero xthreat column — event_id key space drift between xt_df and progcarry_df")

# Every reference carry now has its own xT row (D1): none may be left unscored.
_carry_rows = progcarry_df["type_id"].isin(tc.CARRY_TYPES)
if progcarry_df.loc[_carry_rows, "xt_delta_cadeia"].isna().all():
    raise RuntimeError("no carry row matched an xT row — check the (game_id, team_id, event_id, is_carry) keys")

# Shared event sets (docs/variable_consistency_decisions.md D3, D4) used by every variable below.
play_df = tc.play_frame(progcarry_df)
LOSS_ROWS = pd.Series(progcarry_df.index.isin(play_df.index[tc.loss_mask(play_df).to_numpy()]),
                      index=progcarry_df.index)
REGAIN_ROWS = pd.Series(progcarry_df.index.isin(play_df.index[tc.possession_won_mask(play_df).to_numpy()]),
                        index=progcarry_df.index)
GAME_TEAMS = progcarry_df[["game_id", "team_id"]].drop_duplicates()

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

# Helper: True if qualifier id `val` is on the event, whatever the storage (dict, list or ndarray of dicts) — B3.
def has_qualifier(q, val):
    return val in tc.qualifier_ids(q)

# Crosses (pass with qualifier 2)
progcarry_df["cross"] = (
    (progcarry_df["type_id"] == 1) &
    progcarry_df["qualifiers"].apply(lambda q: has_qualifier(q, 2))
).astype(int)

###############################################################################
###############################################################################

# Progressive pass / ball progression — reference `progressive()` (D1): length >= 10 Opta units and x gain >= 25%
# of the distance left to the goal line. Ball progression = progressive carries (types 1000 and 2000).
_is_progressive = tc.progressive(progcarry_df)
progcarry_df["progressive_pass"] = ((progcarry_df["type_id"] == 1) & _is_progressive).astype(int)
progcarry_df["ball_progression"] = (progcarry_df["type_id"].isin(tc.CARRY_TYPES) & _is_progressive).astype(int)

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
#   / (A's tackles + interceptions + challenges + fouls committed in that same physical area) — D5
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

challenges = (
    df_press_zone[df_press_zone["type_id"] == 45]
    .groupby(["game_id", "team_id"])
    .size()
    .reset_index(name="challenges")
)

defensive_actions = (
    tackles
    .merge(interceptions, on=["game_id", "team_id"], how="outer")
    .merge(fouls, on=["game_id", "team_id"], how="outer")
    .merge(challenges, on=["game_id", "team_id"], how="outer")
    .fillna(0)
)

defensive_actions["total_def_actions"] = (
    defensive_actions["tackles"]
    + defensive_actions["interceptions"]
    + defensive_actions["fouls"]
    + defensive_actions["challenges"]
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
tackles, ball recoveries and fouls committed when out of possession, per game (not adjusted for possession: the
count barely moves with the opponent's possession). It measures how actively a team engages in defensive actions."""

# Defensive Intensity (unadjusted)
#
# Per the definition: number of defensive duels, loose ball duels,
# interceptions, tackles, and fouls committed while out of possession.
# Raw counts per (game_id, team_id); no possession adjustment (see variable_df_new).
#
# Opta F24 mapping (from reference/Opta-f24_appendices.md):
# D5 / reference #35: tackles 7, interceptions 8, aerials 44, challenges 45, ball recoveries 49, fouls committed (4, outcome 0).
#
# Foul outcome convention in the WhoScored-derived JSON used here is the
# OPPOSITE of the official Opta F24 spec (Appendix 8). Verified empirically
# against the next-FK-taker and post-foul card team:
#     outcome == 0  -> player who COMMITTED the foul
#     outcome == 1  -> player who WAS fouled

DEFENSIVE_TYPE_IDS = {
    "tackles": 7,
    "interceptions": 8,
    "defensive_duels": 45,   # challenges (dribbled past)
    "loose_ball_duels": 44,  # aerial duels
    "ball_recoveries": 49,
}

def calculate_defensive_intensity(progcarry_df):
    """
    Calculate raw defensive action counts per (game_id, team_id).

    Returns a DataFrame with one row per team per game containing each
    individual action count and their sum as `defensive_intensity`.
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

# Merge raw defensive_intensity into variable_df (no possession adjustment).
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
# Defensive ground duels (reference `ground_duels`, B2): won = tackle (7, any outcome), lost = dribbled past (45).
# Opponent take-ons are NOT counted: each is the same duel logged from the other side (3,931/3,931 challenges
# sit next to an opponent take-on), so counting them doubled every duel.
_won, _lost = tc.ground_duels(progcarry_df)
variable_df3 = (
    progcarry_df.assign(won=_won, lost=_lost)
    .groupby(["game_id", "team_id"], as_index=False)[["won", "lost"]].sum()
)
_contested = variable_df3["won"] + variable_df3["lost"]
variable_df3["defensive_duels_won_%"] = np.where(_contested > 0, variable_df3["won"] / _contested, np.nan)
variable_df3.head(100).to_csv("variable_df3.csv", index=True)

variable_df = variable_df.merge(
    variable_df3[["game_id", "team_id", "defensive_duels_won_%"]],
    on=["game_id", "team_id"],
    how="left",
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

PITCH_LENGTH_M = 105.0  # UEFA standard pitch length

# D5 / reference area.py: tackles, interceptions, clearances, ball recoveries (7, 8, 12, 49) and fouls committed,
# outside set-piece chains. Aerials (44) and challenges (45) are out: aerials are logged for the attacker too.
_h4 = play_df[tc.height_mask(play_df) & ~tc.set_piece_chain_rows(play_df)]
variable_df4 = (
    _h4.groupby(["game_id", "team_id"], as_index=False)["start_x"].mean()
    .rename(columns={"start_x": "defensive_height"})
)
variable_df4["defensive_height"] = variable_df4["defensive_height"] * PITCH_LENGTH_M / 100.0

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
# by possession_chain.py (chain ids start at 1 (ref_pipeline.chains_table); the != 0 filter keeps every chain). In that view:
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
# Shared zone-reach tables (docs/variable_consistency_decisions.md D2). A chain reaches a zone when a chain-team
# action is located there: its start, or the end of a completed pass or a carry (never a shot end or a failed-pass
# end). Denominators are chains that start outside the zone.
CHAINS = tc.chain_table(progcarry_df)

# 10 s after each regain (D4): rows of the regaining team before its next loss (D3); regains outside the zone only.
AFTER_REGAIN = tc.after_regain(progcarry_df, REGAIN_ROWS, LOSS_ROWS)
_reg_rows = progcarry_df[REGAIN_ROWS]
REGAINS = pd.DataFrame({
    "reg_idx": _reg_rows.index, "game_id": _reg_rows["game_id"].to_numpy(), "team_id": _reg_rows["team_id"].to_numpy(),
    "start_x": _reg_rows["start_x"].to_numpy(),
    "in_third": tc.in_final_third(_reg_rows["start_x"]).to_numpy(),
    "in_box": tc.in_box(_reg_rows["start_x"], _reg_rows["start_y"]).to_numpy(),
}).set_index("reg_idx")
for _zone in ("third", "box"):
    REGAINS[f"reaches_{_zone}"] = (
        tc.zone_hits(AFTER_REGAIN, _zone).groupby(AFTER_REGAIN["reg_idx"]).any()
        .reindex(REGAINS.index, fill_value=False)
    )
_np = AFTER_REGAIN[tc.npxg_shots(AFTER_REGAIN)]
REGAINS["xg"] = _np.groupby("reg_idx")["xG"].sum().reindex(REGAINS.index, fill_value=0.0)
_xt_rows = AFTER_REGAIN[~AFTER_REGAIN[[f"q{q}" for q in tc.XT_SET_PIECE_QUALIFIERS]].any(axis=1)]
REGAINS["xt"] = _xt_rows.groupby("reg_idx")["xt_delta_cadeia"].sum().reindex(REGAINS.index, fill_value=0.0)


def _chain_pct(numerator_col, denominator_mask, name):
    """% of the team's chains in `denominator_mask` that satisfy `numerator_col` (NaN when the denominator is 0)."""
    sub = CHAINS[denominator_mask]
    return sub.groupby(["game_id", "team_id"])[numerator_col].mean().mul(100.0).rename(name).reset_index()


def _regain_count(mask_col, outside_col, name):
    """Regains outside the zone whose next 10 s reach it, counted per team."""
    sub = REGAINS[~REGAINS[outside_col]]
    return sub.groupby(["game_id", "team_id"])[mask_col].sum().rename(name).reset_index()


# Variáveis
# 6
#Opp. Possession to final third %
"""Opp. Possession to final third % is not explicitly defined in the provided information. However,
it generally refers to the percentage of the opposing team's possessions that successfully progress
into the final third of the pitch. This metric helps in understanding how effectively the opposition
can penetrate the defensive setup and advance towards the goal.
"""

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df6 = tc.to_opponent(
    _chain_pct("reaches_third", ~CHAINS["starts_in_third"], "opposition_progression_percentage"), GAME_TEAMS)
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df7 = tc.to_opponent(
    _chain_pct("reaches_box", CHAINS["reaches_third"] & ~CHAINS["starts_in_box"], "opp_final_third_to_box_%"),
    GAME_TEAMS)
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

# Opponent xT per 100 of their completed passes starting in our defensive third (their final third), set pieces
# (q6/q107/q124) excluded (B4; reference #55 uses the absolute xthreat for opposition metrics).
_p8 = progcarry_df[tc.completed_pass(progcarry_df) & tc.in_final_third(progcarry_df["start_x"])
                   & ~progcarry_df[[f"q{q}" for q in tc.XT_SET_PIECE_QUALIFIERS]].any(axis=1)]
_x8 = _p8.groupby(["game_id", "team_id"]).agg(xt=("xthreat", "sum"), n=("xthreat", "size")).reset_index()
_x8["Opposition_xT"] = np.where(_x8["n"] > 0, _x8["xt"] / _x8["n"] * 100.0, np.nan)
variable_df8 = tc.to_opponent(_x8[["game_id", "team_id", "Opposition_xT"]], GAME_TEAMS)
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

# Turnovers in own defensive 40% (D3): reference losses — (1,0) (3,0) (50,1) (51,1) (61,0), last own event of the
# chain, next event by the opponent — with start_x <= 40. Column name kept for the app ("Perdas de posse na linha baixa").
_losses = progcarry_df[LOSS_ROWS]
variable_df9 = (
    _losses[_losses["start_x"] <= tc.LOW_BLOCK_X]
    .groupby(["game_id", "team_id"]).size().rename("high_turnovers").reset_index()
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

# Mean height of the reference losses (D3), metres.
variable_df10 = (
    progcarry_df[LOSS_ROWS].groupby(["game_id", "team_id"])["start_x"].mean()
    .mul(tc.X_METRES).rename("turnover_line_height").reset_index()
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

# Counter-press success (D6, reference `counterpressing`): share of the team's losses won back within 5 s, each loss
# counted once. Column name kept for the app ("Recuperações de posse em 5s (%)").
_cp = tc.counterpress(play_df)
variable_df11 = (
    _cp.groupby(["game_id", "team_id"])["regained"].mean().mul(100.0)
    .rename("recoveries_within_5s_%").reset_index()
)
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

# Seconds from each loss (D3) to the same team's next defensive action (D5 intensity set), same game and period.
_t12 = tc.next_event(play_df, tc.loss_mask(play_df), tc.intensity_mask(play_df))
variable_df12 = (
    _t12.groupby(["game_id", "team_id"])["seconds"].mean()
    .rename("avg_time_to_defensive_action").reset_index()
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

# Seconds from each loss (D3) to the same team's next regain (D4), same game and period.
_t13 = tc.next_event(play_df, tc.loss_mask(play_df), tc.possession_won_mask(play_df))
variable_df13 = (
    _t13.groupby(["game_id", "team_id"])["seconds"].mean()
    .rename("avg_recovery_time").reset_index()
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df14 = tc.to_opponent(_regain_count("reaches_third", "in_third", "opposition_final_third_entries_10s"), GAME_TEAMS)
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df15 = tc.to_opponent(_regain_count("reaches_box", "in_box", "opposition_box_entries_10s"), GAME_TEAMS)
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df16 = tc.to_opponent(REGAINS.groupby(["game_id", "team_id"])["xg"].sum().rename("opposition_xG_10s").reset_index(), GAME_TEAMS)
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

# Regains (D4, reference `possession_won`): interception, tackle won, ball recovery (8, 7/1, 49) followed by an
# own-team event; consecutive recoveries of one regain count once. No GK claims, no aerials.
variable_df17 = (
    progcarry_df[REGAIN_ROWS].groupby(["game_id", "team_id"]).size().rename("recoveries").reset_index()
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

# Mean height of the regains (D4), metres.
variable_df18 = (
    progcarry_df[REGAIN_ROWS].groupby(["game_id", "team_id"])["start_x"].mean()
    .mul(tc.X_METRES).rename("recovery_height").reset_index()
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
# Chain note: chain ids start at 1 (ref_pipeline.chains_table); the != 0 filter keeps every chain.

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
# Chain note: chain ids start at 1 (ref_pipeline.chains_table); the != 0 filter keeps every chain.

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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df21 = _regain_count("reaches_third", "in_third", "final_third_entries_10s")
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df22 = _regain_count("reaches_box", "in_box", "box_entries_10s")
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df23 = REGAINS.groupby(["game_id", "team_id"])["xg"].sum().rename("xG_10s").reset_index()
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df24 = REGAINS.groupby(["game_id", "team_id"])["xt"].sum().rename("xT_10s").reset_index()
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

# Field tilt (D7): the team's share of both teams' final-third (x >= 66.67) possession touches — reference
# `possession_touch` (passes, shots, take-ons, touches, carries; no restarts, penalties, own goals).
_t26 = progcarry_df[tc.possession_touch(progcarry_df) & tc.in_final_third(progcarry_df["start_x"])]
_own26 = GAME_TEAMS.merge(_t26.groupby(["game_id", "team_id"]).size().rename("own").reset_index(),
                          on=["game_id", "team_id"], how="left").fillna({"own": 0})
_own26 = _own26.merge(tc.to_opponent(_own26, GAME_TEAMS).rename(columns={"own": "opp"}), on=["game_id", "team_id"])
_tot26 = _own26["own"] + _own26["opp"]
_own26["field_tilt_%"] = np.where(_tot26 > 0, _own26["own"] / _tot26 * 100.0, np.nan)
variable_df26 = _own26[["game_id", "team_id", "field_tilt_%"]]
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

# Long ball % (D8): q1 passes / all attempted passes; free kicks (q5), corners (q6) and throw-ins (q107) excluded,
# goal kicks kept (a long goal kick is a style choice).
_p27 = progcarry_df[(progcarry_df["type_id"] == 1) & ~progcarry_df[["q5", "q6", "q107"]].any(axis=1)]
variable_df27 = (
    _p27.groupby(["game_id", "team_id"])["q1"].mean().mul(100.0).rename("long_ball_%").reset_index()
)
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
# Chain note: chain ids start at 1 (ref_pipeline.chains_table); the != 0 filter keeps every chain.
#
# NaN preservation: the np.where guard returns NaN when a team-game
# has zero possession seconds, and the final merge leaves missing
# team-games as NaN so the downstream Z-score step treats them as
# missing rather than as a real 0-passes-per-minute team (which would
# be a real extreme low value and bias both the league mean and the
# team's Z-score downward).

# Same definition as #5 (successful open-play passes per minute of own chain time; set pieces 5/6/107/124
# excluded), so opposition_pass_tempo is exactly the opponent's pass_tempo (B10).
variable_df28 = variable_df5[["game_id", "team_id", "pass_tempo"]].copy()
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df29 = _chain_pct("reaches_third", ~CHAINS["starts_in_third"], "final_third_entries_%")
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df30 = _chain_pct("reaches_box", CHAINS["reaches_third"] & ~CHAINS["starts_in_box"], "final_third_to_box_entries_%")
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
# Summed per (game_id, team_id) is `xt_delta_cadeia`: the xT each
# completed pass / take-on / carry adds over the team's previous
# completed action in the same chain (plataforma-scouting). Unlike the
# action xT, it does not re-count threat the team already had.
#
# Set-piece filter: corner (qualifier 6), throw-in (107) and goal kick
# (124) passes are excluded, as plataforma-scouting does for pass xT
# (XT_SET_PIECE_QUALIFIERS): restart deliveries are rated on
# coordinates, not on in-play decision-making. Free kicks (5) stay. The
# defensive-area opposition xT and variable_df24 use the same filter.
#
# NaN preservation: missing team-games left as NaN by the final merge
# so the downstream Z-score step treats them as missing rather than as
# a real 0-xT team (which would be a real extreme low value and bias
# both the league mean and the team's Z-score downward).

_is_xt_set_piece_pass = (progcarry_df["type_id"] == 1) & progcarry_df["qualifiers"].apply(
    lambda q: any(has_qualifier(q, qid) for qid in tc.XT_SET_PIECE_QUALIFIERS)
)

variable_df31 = (
    progcarry_df.loc[~_is_xt_set_piece_pass]
    .groupby(["game_id", "team_id"], as_index=False)["xt_delta_cadeia"]
    .sum()
    .rename(columns={"xt_delta_cadeia": "xT"})
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

# Penalty-area touches (D9): reference `possession_touch` starting inside the box.
variable_df32 = (
    progcarry_df[tc.possession_touch(progcarry_df) & tc.in_box(progcarry_df["start_x"], progcarry_df["start_y"])]
    .groupby(["game_id", "team_id"]).size().rename("penalty_area_touches").reset_index()
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

# Definition: shared zone / 10 s tables built before # 6 (docs/variable_consistency_decisions.md D2, D4).
variable_df33 = _chain_pct("has_shot", CHAINS["reaches_box"] & ~CHAINS["starts_in_box"], "box_entries_to_shot_%")
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

# Non-penalty shots: types 13–16 without penalties (q9) and own goals (q28) — reference `npxg_shots` (B1).
variable_df34 = (
    progcarry_df[tc.npxg_shots(progcarry_df)]
    .groupby(["game_id", "team_id"]).size().rename("np_shots").reset_index()
)
variable_df34.head(100).to_csv("variable_df34.csv", index=True)
variable_df = variable_df.merge(variable_df34[["game_id", "team_id", "np_shots"]], on=["game_id", "team_id"], how="left")

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

# Non-penalty goals: type 16, not q9, not an own goal (reference `non_penalty_goals_mask`, B1).
variable_df37 = (
    progcarry_df[(progcarry_df["type_id"] == 16) & ~progcarry_df["q9"] & ~progcarry_df["q28"]]
    .groupby(["game_id", "team_id"]).size().rename("np_goals").reset_index()
)
variable_df37.head(100).to_csv("variable_df37.csv", index=True)
variable_df = variable_df.merge(variable_df37[["game_id", "team_id", "np_goals"]], on=["game_id", "team_id"], how="left")

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

# np xG per np shot; own goals are not shots of the team (B1). NaN when the team has no np shot.
_s38 = progcarry_df[tc.npxg_shots(progcarry_df)]
variable_df38 = _s38.groupby(["game_id", "team_id"])["xG"].mean().rename("xg_per_shot").reset_index()
variable_df38.head(100).to_csv("variable_df38.csv", index=True)
variable_df = variable_df.merge(variable_df38[["game_id", "team_id", "xg_per_shot"]], on=["game_id", "team_id"], how="left")

###############################################################################
###############################################################################
# Variáveis
# 39
#In-possession ball-in-play minutes
"""In-possession ball-in-play minutes (D10): per team per game, the summed duration of the team's own possession
chains (last event time - first event time of each chain), in minutes. It counts chain time only — the gaps between
chains (restarts, stoppages, transitions) are not counted — so both teams together add up to less than the match's
real ball-in-play time. It is possession in minutes rather than %, so it is not used in any composite."""

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
# Goals are type-16 events; an own goal (q28) is credited to the opponent (B1).
# Goals conceded = goals scored by the opponent in the same game.
#
# NaN -> 0: teams with no goal events on either side get 0.

# Goals credited per team: an own goal (q28) is logged on the conceding team and counts for the opponent (B1).
_goals = progcarry_df[progcarry_df["type_id"] == 16]
_goals_for = (
    _goals.assign(team_id=tc.goal_team(_goals, GAME_TEAMS).astype(progcarry_df["team_id"].dtype))
    .groupby(["game_id", "team_id"]).size().rename("goals_scored").reset_index()
)
_goals_table = GAME_TEAMS.merge(_goals_for, on=["game_id", "team_id"], how="left").fillna({"goals_scored": 0})
_goals_table = _goals_table.merge(
    tc.to_opponent(_goals_table[["game_id", "team_id", "goals_scored"]], GAME_TEAMS)
      .rename(columns={"goals_scored": "goals_conceded"}),
    on=["game_id", "team_id"], how="left")
_goals_table["goal_difference"] = _goals_table["goals_scored"] - _goals_table["goals_conceded"]

variable_df45 = _goals_table[["game_id", "team_id", "goal_difference"]]
variable_df45.head(100).to_csv("variable_df45.csv", index=True)
variable_df = variable_df.merge(variable_df45, on=["game_id", "team_id"], how="left")
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
# Goals are type-16 events; an own goal (q28) is credited to the opponent (B1).
#
# NaN -> 0: teams in goalless draws get 0.

variable_df46 = _goals_table[["game_id", "team_id", "goals_conceded"]]
variable_df46.head(100).to_csv("variable_df46.csv", index=True)
variable_df = variable_df.merge(variable_df46, on=["game_id", "team_id"], how="left")
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
# Goals are type-16 events; an own goal (q28) is credited to the opponent (B1).
#
# NaN -> 0: teams that did not score get 0.

variable_df47 = _goals_table[["game_id", "team_id", "goals_scored"]]
variable_df47.head(100).to_csv("variable_df47.csv", index=True)
variable_df = variable_df.merge(variable_df47, on=["game_id", "team_id"], how="left")
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

# D11: no events -> 0 for counts and sums; ratios, heights and times keep NaN (no denominator = undefined).
COUNT_COLUMNS = ["defensive_intensity", "high_turnovers", "recoveries", "retained_possessions_5s",
                 "final_third_entries_10s", "box_entries_10s", "xG_10s", "xT_10s",
                 "opposition_final_third_entries_10s", "opposition_box_entries_10s", "opposition_xG_10s", "xT",
                 "penalty_area_touches", "np_shots", "high_opportunity_shots", "np_xg", "np_goals", "total_xg",
                 "goal_difference", "goals_conceded", "goals_scored", "ball_in_play"]
variable_df_new[COUNT_COLUMNS] = variable_df_new[COUNT_COLUMNS].fillna(0)

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

# No possession adjustment. Raw defensive_intensity and recoveries barely move with opponent possession (r +0.06,
# -0.17) and high_turnovers already falls as own possession rises (r -0.54); dividing by possession turned all three
# into possession proxies (r -0.83) and pulled four performance composites toward possession. They stay raw counts.

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
    zscore_columns = group.iloc[:, 10:].apply(lambda s: zscore(s, nan_policy="omit"))
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
# Opposition_xT is out: it did not agree with the other defence items (item-rest r +0.07).
defence_metrics_outcome = ["opposition_progression_percentage_z", "opp_final_third_to_box_%_z"]
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
# box_entries_to_shot_% is out: it did not agree with the other chance-creation items (item-rest r +0.25).
chance_creation_quality_outcome = ["xg_per_shot_z", "np_goals_z"]

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
                     "defence_z", "defensive_transition_z",
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

columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube",
                   "Defesa", "Transição defensiva",
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
    zscore_columns = group.iloc[:, 10:].apply(lambda s: zscore(s, nan_policy="omit"))
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
# Opposition_xT is out: it did not agree with the other defence items (item-rest r +0.07).
defence_metrics_outcome = ["opposition_progression_percentage_z", "opp_final_third_to_box_%_z"]
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
# box_entries_to_shot_% is out: it did not agree with the other chance-creation items (item-rest r +0.25).
chance_creation_quality_outcome = ["xg_per_shot_z", "np_goals_z"]

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
                     "defence_z", "defensive_transition_z",
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

columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube",
                   "Defesa", "Transição defensiva",
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
# Same definition and values as performance #4 (D5, B10).

variable_ps1 = variable_df4[["game_id", "team_id", "defensive_height"]].copy()

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

# Share of regains (D4) made in the final third (x >= 66.67; the reference uses x >= 50 — kept at the final third to
# match the label, docs/variable_consistency_decisions.md D4).
_reg = progcarry_df[REGAIN_ROWS]
variable_ps2 = (
    _reg.assign(high=tc.in_final_third(_reg["start_x"]))
    .groupby(["game_id", "team_id"])["high"].mean().mul(100.0).rename("high_recoveries_%").reset_index()
)

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
# Same definition and values as performance #1 (D5, B10).
variable_ps3 = variable_df1[["game_id", "team_id", "PPDA"]].copy()

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
MatchAnalysis_PlayStyle_2025.py.

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
tackles, ball recoveries and fouls committed when out of possession, per game (not adjusted for possession: the
count barely moves with the opponent's possession). It measures how actively a team engages in defensive actions."""

# Defensive Intensity — the performance frame's value (D5 set: 7, 8, 44, 45, 49 and committed fouls), a raw count
# per game (no possession adjustment, see variable_df_new) (B6, B10).

variable_ps5 = variable_df_new[["game_id", "team_id", "defensive_intensity"]].copy()

variable_ps5.head(100).to_csv("variable_ps5.csv", index=True)

# Merge defensive_intensity into variable_ps (no possession adjustment).
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
MatchAnalysis_PlayStyle_2025.py, which uses only successful ball-regaining
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

# Same definition and values as performance #12 (D3 losses, D5 intensity set).
variable_ps6 = variable_df12[["game_id", "team_id", "avg_time_to_defensive_action"]].copy()

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
MatchAnalysis_PlayStyle_2025.py variable_df11 (Recoveries within 5s %),
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
     (time = minute*60+second with WhoScored's expanded minute (cumulative across periods); pairings group by period).

Pairing: for each recovery, find the most recent same-team loss in the
same period; the recovery is "within 5s" if recovery_time - loss_time
<= 5. Denominator = total recoveries (even those with no prior loss
inside the window) -- matches variable_df11's denominator scoping.
"""

# Same definition and values as performance #11 (D6).
variable_ps7 = variable_df11.rename(columns={"recoveries_within_5s_%": "counter_press_Success_Rate_%"})

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
"""Transition Vulnerability Index is the share of the opposition's completed open-play passes, in the 10 seconds
after the team loses the ball, that are progressive. A high value means the team's losses are punished by the
opponent moving the ball forward quickly.

Losses: reference losses (D3, LOSS_ROWS) -- (1,0) (3,0) (50,1) (51,1) (61,0), the last own event of the chain, with
the next event by the opponent.
Opposition passes: completed passes without free kicks (q5), corners (q6), throw-ins (q107) or goal kicks (q124);
"progressive" is the reference progressive() rule (D1: length >= 10 Opta units, x gain >= 25% of the distance left).
Pairing: each opposition pass is matched to the latest loss of the other team in the same game and period
(merge_asof, backward, strict) and counts when it comes within 10 s; each pass counts once. The window is time-based,
not bounded to the opponent's chain. Not used in any play-style composite (D13).
"""

WINDOW_SECONDS = 10.0

_type_id = progcarry_df["type_id"]
_outcome = progcarry_df["outcome"].astype(bool)

_loss_mask = LOSS_ROWS  # D3 reference losses

_is_set_piece = progcarry_df["qualifiers"].apply(
    lambda q: has_qualifier(q, 5) or has_qualifier(q, 6) or has_qualifier(q, 107) or has_qualifier(q, 124)
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

# Same values as performance #14 (D2, B10).
variable_ps9 = variable_df14.copy()
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

# Same values as performance #15 (D2, B10).
variable_ps10 = variable_df15.copy()
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

# Own-half regain (D4, start_x < 50) -> first completed pass or carry of the team ending in the opponent half,
# before the team's next loss (D3). Carries are types 1000 and 2000 (B7).
_ev = progcarry_df
_from = REGAIN_ROWS & (_ev["start_x"] < tc.HALF_X)
_prog = ((tc.completed_pass(_ev) | _ev["type_id"].isin(tc.CARRY_TYPES)) & (_ev["end_x"] >= tc.HALF_X))
_to_prog = tc.next_event(_ev, _from, _prog)
_to_loss = tc.next_event(_ev, _from, LOSS_ROWS)
_to_prog["seconds"] = _to_prog["seconds"].where(~(_to_loss["to_pos"] < _to_prog["to_pos"]))
variable_ps11 = (
    _to_prog.groupby(["game_id", "team_id"])["seconds"].mean()
    .rename("time_to_progression_seconds").reset_index()
)

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

# First open-play pass after each regain (D4) that goes forward (end_x > start_x).
_open_pass = (progcarry_df["type_id"] == 1) & ~tc.restart_pass(progcarry_df)
_nx = tc.next_event(progcarry_df, REGAIN_ROWS, _open_pass).dropna(subset=["to_pos"])
_first = progcarry_df.iloc[_nx["to_pos"].astype(int).to_numpy()]
variable_ps12 = (
    _nx.assign(forward=(_first["end_x"].to_numpy() > _first["start_x"].to_numpy()))
    .groupby(["game_id", "team_id"])["forward"].mean().mul(100.0).rename("first_pass_forward_pct").reset_index()
)

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
10 seconds. Same mechanism as MatchAnalysis_PlayStyle_2025.py
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
H2-start entry (time = minute*60+second with WhoScored's expanded minute (cumulative across periods); pairings group by period).

Denominator = all own-half recoveries for that team-game. Numerator =
own-half recoveries with a within-10s final-third entry. Ratio * 100.
"""

_r13 = REGAINS[(REGAINS["start_x"] < tc.HALF_X) & ~REGAINS["in_third"]]
variable_ps13 = (_r13.groupby(["game_id", "team_id"])["reaches_third"].mean().mul(100.0)
                 .rename("final_third_entries_10s_pct").reset_index())

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
as MatchAnalysis_PlayStyle_2025.py variable_df15 (opposition view) /
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

_r14 = REGAINS[(REGAINS["start_x"] >= tc.HALF_X) & ~REGAINS["in_box"]]
variable_ps14 = (_r14.groupby(["game_id", "team_id"])["reaches_box"].mean().mul(100.0)
                 .rename("box_entries_10s_pct").reset_index())

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

Chain note: chain ids start at 1 (ref_pipeline.chains_table); the != 0 filter keeps every chain.
"""

variable_ps15 = variable_df20.rename(columns={"retained_possessions_5s_%": "retained_possessions_5s_pct"})

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

# Same definition and values as performance #27 (D8, B10).
variable_ps16 = variable_df27[["game_id", "team_id", "long_ball_%"]].copy()

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

# Goal-kick chains (first chain-team event is a q124 pass) that become a build-up: >= 4 completed chain-team passes
# after the kick and >= 8 s of possession. The chain ends at the loss (D3), so no separate loss mask is needed.
_ct = progcarry_df[progcarry_df["is_chain_team"].fillna(False).astype(bool) & progcarry_df["chain_id"].notna()]
_ck = [_ct["game_id"], _ct["chain_id"]]
_head = _ct.groupby(_ck, sort=False).head(1)
_gk = _head[_head["q124"]].set_index(["game_id", "chain_id"])
_passes = (tc.completed_pass(_ct) & ~_ct["q124"]).groupby(_ck).sum()
_dur = _ct.groupby(_ck)["time"].agg(lambda t: t.max() - t.min())
_gk = _gk.assign(buildup=(_passes.reindex(_gk.index) >= 4) & (_dur.reindex(_gk.index) >= 8))
variable_ps17 = (
    _gk.reset_index().groupby(["game_id", "team_id"])["buildup"].mean().mul(100.0).rename("buildup_%").reset_index()
)

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
"""Progressive Passes From Middle Third % is the share of a team's open-play pass attempts starting in the middle
third (100/3 <= start_x < 200/3) that are progressive. It measures forward intent in the central phase of build-up.

Pass mask: type_id 1, any outcome (a failed forward pass is still an attempted progression), without free kicks
(q5), corners (q6) or throw-ins (q107).
Progressive: the reference progressive() rule (D1) -- length >= 10 Opta units and x gain >= 25% of the distance left
to the goal line (progcarry_df["progressive_pass"]).
Ratio * 100; NaN when the team has no middle-third pass.
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
# First action of each chain that reaches the final third / the box (D2) — the "entry" event.
_ct7 = progcarry_df[progcarry_df["is_chain_team"].fillna(False).astype(bool) & progcarry_df["chain_id"].notna()]
_ck7 = ["game_id", "chain_id"]
_entry_third = _ct7[tc.zone_hits(_ct7, "third")].groupby(_ck7, sort=False).head(1)
_entry_box = _ct7[tc.zone_hits(_ct7, "box")].groupby(_ck7, sort=False).head(1)
_from_outside_third = CHAINS.loc[~CHAINS["starts_in_third"], _ck7]
_from_outside_box = CHAINS.loc[~CHAINS["starts_in_box"], _ck7]
_entry_third = _entry_third.merge(_from_outside_third, on=_ck7)
_entry_box = _entry_box.merge(_from_outside_box, on=_ck7)
_ft_entries = _entry_third.groupby(["game_id", "team_id"]).size().rename("ft_entries")
_open = ~progcarry_df[["q5", "q6", "q107"]].any(axis=1)

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

_cross = progcarry_df[(progcarry_df["type_id"] == 1) & progcarry_df["q2"] & _open
                      & tc.in_final_third(progcarry_df["start_x"])]
_c19 = _cross.groupby(["game_id", "team_id"]).size().rename("crosses")
variable_ps19 = pd.concat([_c19, _ft_entries], axis=1).reset_index()
variable_ps19["crosses_per_final_third_entry"] = np.where(
    variable_ps19["ft_entries"] > 0, variable_ps19["crosses"].fillna(0) / variable_ps19["ft_entries"], np.nan)

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

_drib = progcarry_df[(progcarry_df["type_id"] == 3) & tc.in_final_third(progcarry_df["start_x"])]  # attempts
_d20 = _drib.groupby(["game_id", "team_id"]).size().rename("dribbles")
variable_ps20 = pd.concat([_d20, _ft_entries], axis=1).reset_index()
variable_ps20["dribbles_per_final_third_entry"] = np.where(
    variable_ps20["ft_entries"] > 0, variable_ps20["dribbles"].fillna(0) / variable_ps20["ft_entries"], np.nan)

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

variable_ps21 = (
    _entry_box.assign(cross=(_entry_box["type_id"] == 1) & _entry_box["q2"])
    .groupby(["game_id", "team_id"])["cross"].mean().mul(100.0).rename("box_entries_from_crosses").reset_index()
)

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

variable_ps22 = (
    _entry_box.assign(carry=_entry_box["type_id"].isin(tc.CARRY_TYPES))
    .groupby(["game_id", "team_id"])["carry"].mean().mul(100.0).rename("box_entries_from_carries").reset_index()
)

variable_ps = variable_ps.merge(
    variable_ps22[["game_id", "team_id", "box_entries_from_carries"]],
    on=["game_id", "team_id"],
    how="left",
)

###############################################################################
###############################################################################
###############################################################################
###############################################################################
# Open-play shots (B5): np shots (no q9 penalty, no q28 own goal) that are not set-piece shots (q24/q25/q26), each
# measured inside its own reference chain: seconds since the chain's first chain-team event and passes before it.
_ct9 = progcarry_df[progcarry_df["is_chain_team"].fillna(False).astype(bool) & progcarry_df["chain_id"].notna()]
_ct9 = _ct9.assign(_start=_ct9.groupby(["game_id", "chain_id"])["time"].transform("min"),
                   _passes_before=(_ct9["type_id"] == 1).astype(int).groupby([_ct9["game_id"], _ct9["chain_id"]]).cumsum()
                                  - (_ct9["type_id"] == 1).astype(int))
OPEN_SHOTS = _ct9[tc.npxg_shots(_ct9) & ~_ct9[["q24", "q25", "q26"]].any(axis=1)].assign(
    duration=lambda d: d["time"] - d["_start"])

# Variáveis
# Chance creation
# 23
# Shots from sustained attacks %
"""Shots from Sustained Attacks % is the share of a team's open-play shots that end a patient possession: the
shot comes >= 9 s after the start of its reference possession chain and after >= 4 passes of that chain.

Shots (B5, OPEN_SHOTS): np shots (types 13-16 without penalties q9 or own goals q28), excluding set-piece shots
(q24/q25/q26). Each shot is measured inside its own reference chain: duration = shot time - time of the chain's
first chain-team event; passes = chain-team passes (type 1, any outcome) before the shot.
Ratio * 100; NaN when the team has no open-play shot.
"""

# % of open-play shots from sustained possessions: chain >= 9 s old and >= 4 passes before the shot.
variable_ps23 = (
    OPEN_SHOTS.assign(s=(OPEN_SHOTS["duration"] >= 9) & (OPEN_SHOTS["_passes_before"] >= 4))
    .groupby(["game_id", "team_id"])["s"].mean().mul(100.0).rename("sustained_attacks").reset_index()
)

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
"""Shots from Direct Attacks % is the share of a team's open-play shots that end a quick possession: the shot comes
<= 8 s after the start of its reference possession chain and after <= 3 passes of that chain. The mirror of Var 23
(sustained attacks): a shot cannot be both, so the two shares add up to 100 or less.

Shots and chain measures: see Var 23 (OPEN_SHOTS, B5).
Ratio * 100; NaN when the team has no open-play shot.
"""

# % of open-play shots from direct attacks: chain <= 8 s old and <= 3 passes before the shot.
variable_ps24 = (
    OPEN_SHOTS.assign(d=(OPEN_SHOTS["duration"] <= 8) & (OPEN_SHOTS["_passes_before"] <= 3))
    .groupby(["game_id", "team_id"])["d"].mean().mul(100.0).rename("direct_attack").reset_index()
)

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

_s25 = progcarry_df[tc.npxg_shots(progcarry_df)].groupby(["game_id", "team_id"]).size().rename("shots")
_p25 = progcarry_df[(progcarry_df["type_id"] == 1) & ~progcarry_df[["q5", "q6", "q107"]].any(axis=1)
                    & tc.in_final_third(progcarry_df["end_x"])].groupby(["game_id", "team_id"]).size().rename("passes")
variable_ps25 = pd.concat([_s25, _p25], axis=1).rename_axis(["game_id", "team_id"]).reset_index()
variable_ps25["shots_per_final_third_pass"] = np.where(
    variable_ps25["passes"] > 0, variable_ps25["shots"].fillna(0) / variable_ps25["passes"], np.nan)

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

_s26 = progcarry_df[tc.npxg_shots(progcarry_df)]
variable_ps26 = (
    _s26.assign(out=~tc.in_box(_s26["start_x"], _s26["start_y"]))
    .groupby(["game_id", "team_id"])["out"].mean().mul(100.0).rename("shots_outside_box").reset_index()
)

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

# D12/D13: play-style composites are behaviour axes, not quality: each averages its metrics' z-scores signed toward
# a named pole (+ toward the pole, - away from it). Rest-defence outcomes (transition vulnerability, opponent entries
# within 10 s) stay as columns but are not in any composite.
STYLE_POLES = {
    "defence_z": {"+": ["defensive_height_z", "high_recoveries_%_z", "fouls_in_attacking_half_%_z",
                        "defensive_intensity_z"], "-": ["PPDA_z"]},
    "defensive_transition_z": {"+": ["counter_press_Success_Rate_%_z"], "-": ["avg_time_to_defensive_action_z"]},
    "attacking_transition_z": {"+": ["first_pass_forward_pct_z", "final_third_entries_10s_pct_z", "box_entries_10s_pct_z"],
                               "-": ["time_to_progression_seconds_z", "retained_possessions_5s_pct_z"]},
    "directness_z": {"+": ["long_ball_%_z", "progressive_passes_%_z"], "-": ["buildup_%_z"]},
    "wide_play_z": {"+": ["crosses_per_final_third_entry_z", "box_entries_from_crosses_z"],
                    "-": ["dribbles_per_final_third_entry_z", "box_entries_from_carries_z"]},
    "chance_creation_z": {"+": ["direct_attack_z", "shots_per_final_third_pass_z", "shots_outside_box_z"],
                          "-": ["sustained_attacks_z"]},
}
for _name, _p in STYLE_POLES.items():
    _signed = pd.concat([variable_ps_team_z[_p["+"]], -variable_ps_team_z[_p["-"]]], axis=1)
    variable_ps_team_z[_name] = _signed.mean(axis=1)

# Get a list of the current columns
cols = list(variable_ps_team_z.columns)

# List of columns to be relocated
cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", "directness_z", "wide_play_z",
                  "chance_creation_z"]

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
                     "attacking_transition_z", "directness_z", "wide_play_z", "chance_creation_z", "defensive_height_z", 
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
                   "Posse adversário (%)", "Bloco alto / agressivo", "Contrapressão imediata",
                   "Transição vertical", "Jogo direto", "Jogo pelos lados", "Finalização precoce", 
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
assert len(columns_to_rename) == len(columns_renamed)
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

# D12/D13: same STYLE_POLES as the team-level block.
for _name, _p in STYLE_POLES.items():
    _signed = pd.concat([variable_ps_round_z[_p["+"]], -variable_ps_round_z[_p["-"]]], axis=1)
    variable_ps_round_z[_name] = _signed.mean(axis=1)

# Get a list of the current columns
cols = list(variable_ps_round_z.columns)

# List of columns to be relocated
cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", "directness_z", "wide_play_z",
                  "chance_creation_z"]

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
                     "attacking_transition_z", "directness_z", "wide_play_z", "chance_creation_z", "defensive_height_z", 
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
                   "Posse adversário (%)", "Bloco alto / agressivo", "Contrapressão imediata",
                   "Transição vertical", "Jogo direto", "Jogo pelos lados", "Finalização precoce", 
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
assert len(columns_to_rename) == len(columns_renamed)
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

