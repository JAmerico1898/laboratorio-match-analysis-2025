#%%
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
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for subprocess execution
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')


# Opening the dataset
"""We reset the index to have the indicies sorted."""

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

# Load raw events from parquet (produced by orchestrator)
df = pd.read_parquet("brasileirao_2025_events.parquet")
df = df.reset_index()


# Preparing data (adapted from Wyscout to Opta)
"""
We create a column with the next event type. We mark when the ball was
kicked out (chain stop). We filter out non-ball admin events (Opta
equivalents of Wyscout 'Interruption'). We drop lost aerial duels since
Opta records them for both players (like Wyscout duels). We drop
CornerAwarded events (ball-out-of-play markers). We drop goalkeeper-
specific events since shots were recorded before them.
"""

# helper: check if a row is a dead-ball restart (throw-in qual 107, free kick qual 5)
def _is_dead_ball_restart(qualifiers):
    if not isinstance(qualifiers, list):
        return False
    return any(q['type']['value'] in (5, 107) for q in qualifiers)

next_event = df.shift(-1, fill_value=0)
df["nextEvent"] = next_event["type_displayName"]

# kickedOut = 1 when next event signals ball went out of play:
# CornerAwarded (6), or a pass that is a throw-in (qual 107) or free kick (qual 5)
df["kickedOut"] = (
    (next_event["type_value"] == 6) |
    next_event["qualifiers"].apply(_is_dead_ball_restart)
).astype(int)

# force chain break at half-time and game boundaries
boundary = (df["game_id"] != next_event["game_id"]) | (df["period_value"] != next_event["period_value"])
df.loc[boundary, "kickedOut"] = 1
df.loc[boundary, "nextEvent"] = None

# drop non-ball admin events (Opta equivalent of Wyscout "Interruption")
admin_events = df.loc[df["type_displayName"].isin([
    "Start", "End", "FormationSet", "FormationChange",
    "Card", "SubstitutionOff", "SubstitutionOn",
    "OffsideGiven", "OffsideProvoked"
])]
df = df.drop(admin_events.index)

# drop lost aerial duels - Opta records them for both players (like Wyscout duels)
lost_aerials = df.loc[
    (df["type_displayName"] == "Aerial") & (df["outcomeType_value"] == 0)
]
df = df.drop(lost_aerials.index)

# drop CornerAwarded - ball out of play info is already captured in kickedOut
corners = df.loc[df["type_displayName"] == "CornerAwarded"]
df = df.drop(corners.index)

# drop goalkeeper-specific events - shots were recorded before them
goalies = df.loc[df["type_displayName"].isin([
    "Save", "Claim", "Punch", "KeeperPickup",
    "KeeperSweeper", "PenaltyFaced"
])]
df = df.drop(goalies.index)

# Isolating possesion chain
""" Then, we isolate possesion chain with the rule that if the ball 
was touched once by a different team, it should not change the results. 
If there was a foul, ball kicked out of the field the chain is stopped. 
For others in the ball, if the ball was properly intercepted that is, 
the next team is the one that made the next event, we stop the chain. 
Otherwise, if the ball was only touched, but did not change possesion, 
we treat a pass as an accurate one. Note that this is an approximate 
of true possesion chain. In the industry you will work on datasets with 
possesion chains already isolated."""

def isolateChains(df):
    """
    Parameters
    ----------
    df : dataframe
        dataframe with Opta event data.

    Returns
    -------
    df: dataframe
        dataframe with isolated possesion chains

    """
    df["nextTeamId"] = df.shift(-1, fill_value=0)["teamId"]
    chain_team = df.iloc[0]["teamId"]
    period = df.iloc[0]["period_value"]
    game = df.iloc[0]["game_id"]
    stop_criterion = 0
    chain = 0
    df["possesion_chain"] = 0
    df["possesion_chain_team"] = 0

    for i, row in df.iterrows():
        # criterion for stopping when half or game changed
        if row["period_value"] != period or row["game_id"] != game:
            chain += 1
            stop_criterion = 0
            chain_team = row["teamId"]
            period = row["period_value"]
            game = row["game_id"]

        # add value
        df.at[i, "possesion_chain"] = chain
        df.at[i, "possesion_chain_team"] = chain_team

        # if pass/aerial not accurate by the chain team, add 1 (single touch tolerance)
        if row["type_displayName"] in ("Pass", "Aerial"):
            if row["teamId"] == chain_team and row["outcomeType_value"] == 0:
                stop_criterion += 1
            if row["teamId"] != chain_team and row["outcomeType_value"] == 1:
                stop_criterion += 1

        # if ball touched/recovered and the same team keeps it, add 2 (interception)
        if row["type_displayName"] in ("BallTouch", "BallRecovery"):
            if row["teamId"] == row["nextTeamId"]:
                stop_criterion += 2

        # if shot, foul or offside, add 2
        if row["type_displayName"] in ("MissedShots", "SavedShot", "Goal",
                                        "ShotOnPost", "Foul", "OffsidePass"):
            stop_criterion += 2

        # if ball out of field, add 2
        if row["kickedOut"] == 1:
            stop_criterion += 2

        # possesion chain ended
        if stop_criterion >= 2:
            chain += 1
            stop_criterion = 0
            chain_team = row["nextTeamId"]

    return df

df = isolateChains(df)


#investigate a chain
df.loc[df["possesion_chain"] == 4][["type_displayName", "possesion_chain"]]

# Calculating xG value
""" To calculate xG value of shots, we use the function from xG_model.py. 
However, this time we treat penalties as shots from the penalty spot. 
Then, we assign xG value to shots in df with all events."""

def _train_xg_model():
    """Train the xG model on Premier League data (xG_Training_data/)
    using the 7-variable logistic regression from xG_model.py.
    Returns the fitted params (b) and the model variable list."""
    train_ids = (
    list(range(1575781, 1576161))  # 380 jogos
    + list(range(1557324, 1557630))  # 306 jogos
    + list(range(1558305, 1558685))  # 380 jogos
    + list(range(1549539, 1549919))  # 380 jogos
    + list(range(1491953, 1492333))  # 380 jogos
    )
    train_base = os.path.join(str(pathlib.Path().resolve()), "xG_Training_data")

    train_dfs = []
    missing, bad, ok = 0, 0, 0
    for gid in train_ids:
        p = os.path.join(train_base, f"{gid}.json")
        if not os.path.exists(p):
            missing += 1
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)
        except (json.JSONDecodeError, OSError):
            bad += 1
            continue
        if not isinstance(d, dict) or "events" not in d or not d["events"]:
            bad += 1
            continue
        train_dfs.append(pd.json_normalize(d["events"], sep="_"))
        ok += 1

    print(f"xG training data: {ok} OK, {missing} missing, {bad} invalid (total train_ids: {len(train_ids)})")

    if not train_dfs:
        raise RuntimeError(
            "No valid xG training files found. Check xG_Training_data/ folder."
        )

    train_df = pd.concat(train_dfs, ignore_index=True)

    def _is_penalty(qualifiers):
        if isinstance(qualifiers, list):
            for q in qualifiers:
                if q.get("type", {}).get("value") == 9:
                    return True
        return False

    shots = train_df.loc[
        (train_df["isShot"] == True) & (~train_df["qualifiers"].apply(_is_penalty))
    ].copy()
    shots["X"] = (100 - shots["x"]) * 105 / 100
    shots["C"] = abs(shots["y"] - 50) * 68 / 100
    shots["Distance"] = np.sqrt(shots["X"]**2 + shots["C"]**2)
    shots["Angle"] = np.where(
        np.arctan(7.32 * shots["X"] / (shots["X"]**2 + shots["C"]**2 - (7.32/2)**2)) > 0,
        np.arctan(7.32 * shots["X"] / (shots["X"]**2 + shots["C"]**2 - (7.32/2)**2)),
        np.arctan(7.32 * shots["X"] / (shots["X"]**2 + shots["C"]**2 - (7.32/2)**2)) + np.pi
    )
    shots["Goal"] = shots["isGoal"].apply(lambda x: 1 if x == True else 0)
    shots["X2"] = shots["X"]**2
    shots["C2"] = shots["C"]**2
    shots["AX"] = shots["Angle"] * shots["X"]

    model_vars = ["Angle", "Distance", "X", "C", "X2", "C2", "AX"]
    formula = "Goal ~ " + " + ".join(model_vars)
    model = smf.glm(formula=formula, data=shots, family=sm.families.Binomial()).fit()
    return model.params, model_vars


def calculatexG(df):
    """
    Parameters
    ----------
    df : dataframe
        dataframe with Opta event data.

    Returns
    -------
    df: dataframe
        dataframe with xG for each shot
    """
    b, model_vars = _train_xg_model()

    def _compute_xg(sh):
        bsum = b.iloc[0]
        for i, v in enumerate(model_vars):
            bsum = bsum + b.iloc[i + 1] * sh[v]
        return 1 / (1 + np.exp(-bsum))

    def _is_penalty(qualifiers):
        if isinstance(qualifiers, list):
            for q in qualifiers:
                if q.get("type", {}).get("value") == 9:
                    return True
        return False

    df["xG"] = 0.0

    # non-penalty shots
    shot_mask = (df["isShot"] == True) & (~df["qualifiers"].apply(_is_penalty))
    shots = df.loc[shot_mask].copy()
    shots["X"] = (100 - shots["x"]) * 105 / 100
    shots["C"] = abs(shots["y"] - 50) * 68 / 100
    shots["Distance"] = np.sqrt(shots["X"]**2 + shots["C"]**2)
    shots["Angle"] = np.where(
        np.arctan(7.32 * shots["X"] / (shots["X"]**2 + shots["C"]**2 - (7.32/2)**2)) > 0,
        np.arctan(7.32 * shots["X"] / (shots["X"]**2 + shots["C"]**2 - (7.32/2)**2)),
        np.arctan(7.32 * shots["X"] / (shots["X"]**2 + shots["C"]**2 - (7.32/2)**2)) + np.pi
    )
    shots["X2"] = shots["X"]**2
    shots["C2"] = shots["C"]**2
    shots["AX"] = shots["Angle"] * shots["X"]
    shots["xG"] = shots.apply(_compute_xg, axis=1)
    for index, row in shots.iterrows():
        df.at[index, "xG"] = row["xG"]

    # penalties: fixed position (11m from goal, centred)
    pen_mask = (df["isShot"] == True) & (df["qualifiers"].apply(_is_penalty))
    penalties = df.loc[pen_mask].copy()
    if len(penalties) > 0:
        penalties["X"] = 11
        penalties["C"] = 0
        penalties["Distance"] = 11
        penalties["Angle"] = np.arctan(7.32 * 11 / (11**2 - (7.32/2)**2))
        penalties["X2"] = 11**2
        penalties["C2"] = 0
        penalties["AX"] = penalties["Angle"] * 11
        penalties["xG"] = penalties.apply(_compute_xg, axis=1)
        for index, row in penalties.iterrows():
            df.at[index, "xG"] = row["xG"]

    return df

df = calculatexG(df)
#investigate a chain
df.loc[df["possesion_chain"].isin([3,4])][["type_displayName", "possesion_chain", "xG"]]

# Finding chains that ended with shot
""" As the next step we find possesion chains that ended with shot. We assgin 1 to them. We also 
assign xG of the shot to all events in the chain. If a chain was stopped by a foul, also chain 
before is considered as one that ended with shot. We also keep only events made by possesion 
team in the chain.
"""

shot_types = ("MissedShots", "SavedShot", "Goal", "ShotOnPost")

def prepareChains(df):
    """
    Parameters
    ----------
    df : dataframe
        dataframe with Opta event data.

    Returns
    -------
    df: dataframe
        dataframe with assigned values for chains

    """
    df["shot_end"] = 0
    #get number of chains
    no_chains = max(df["possesion_chain"].unique())
    indicies = []
    for i in range(no_chains+1):
        #all events in this possesion chain
        possesion_chain_df = df.loc[df["possesion_chain"] == i]
        #check if the possesion chain is not empty
        if len(possesion_chain_df) > 0:
            #if ended with shot
            if possesion_chain_df.iloc[-1]["type_displayName"] in shot_types:
                #assign values
                df.loc[df["possesion_chain"] == i, "shot_end"] = 1
                xG = possesion_chain_df.iloc[-1]["xG"]
                df.loc[df["possesion_chain"] == i, "xG"] = xG
                #check if the previous ones did not end with foul
                k = i-1
                if k > 0:
                    try:
                        prev = df.loc[df["possesion_chain"] == k]
                        #create a loop if e.g. 2 chains before and 1 chain before didn't end with shot
                        while prev.iloc[-1]["type_displayName"] == "Foul":
                            #assign value for them
                            df.loc[df["possesion_chain"] == k, "xG"] = xG
                            df.loc[df["possesion_chain"] == k, "shot_end"] = 1
                            k = k-1
                            prev = df.loc[df["possesion_chain"] == k]
                    except:
                        k = k-1
            #get indices of events made by possesion team
            team_indicies = possesion_chain_df.loc[possesion_chain_df["teamId"] == possesion_chain_df.teamId.mode().iloc[0]].index.values.tolist()
            indicies.extend(team_indicies)

    df = df.loc[indicies]
    return df

df = prepareChains(df)
#investigate a chain that ended with a shot
shot_chains = df.loc[df["shot_end"] == 1, "possesion_chain"].unique()[:2]
df.loc[df["possesion_chain"].isin(shot_chains)][["type_displayName", "possesion_chain", "shot_end", "xG"]]

# Preparing data for modelling (adapted from Wyscout to Opta)
"""As the next step we prepare data for modelling. We keep only events
that have end coordinates (endX/endY) or are shots. We store coordinates
in separate columns scaled to a 105x68 pitch. Variable c is the distance
from the centre line of the pitch. Shot endpoints are set to (105, 34)
which is the centre of the goal."""

#keep events with end coordinates or shots
df = df.loc[df["endX"].notna() | df["type_displayName"].isin(shot_types)]
#columns with coordinates (Opta 0-100 scale to 105x68 pitch)
df["x0"] = df["x"] * 105 / 100
df["c0"] = abs(50 - df["y"]) * 68 / 100
df["x1"] = df["endX"] * 105 / 100
df["c1"] = abs(50 - df["endY"]) * 68 / 100
#assign (105, 0) to end of the shot (goal centre)
df.loc[df["type_displayName"].isin(shot_types), "x1"] = 105
df.loc[df["type_displayName"].isin(shot_types), "c1"] = 0

#for plotting
df["y0"] = (100 - df["y"]) * 68 / 100
df["y1"] = (100 - df["endY"]) * 68 / 100
df.loc[df["type_displayName"].isin(shot_types), "y1"] = 34

# Possesion chain that ended with a shot
"""Now we can plot possesion chains. Here is one that ended with a shot.
Note that actions that were not passes and not shots are marked with a grey
dotted line."""

#pick first chain that ended with a shot
shot_chain_id = df.loc[df["shot_end"] == 1, "possesion_chain"].iloc[0]
chain = df.loc[df["possesion_chain"] == shot_chain_id]
#get passes
passes = chain.loc[chain["type_displayName"] == "Pass"]
#get events different than pass (excluding the shot at the end)
not_pass = chain.loc[~chain["type_displayName"].isin(["Pass"] + list(shot_types))].iloc[:-1]
#shot is the last event of the chain (or should be)
shot = chain.iloc[-1]
#plot
pitch = Pitch(line_color='black', pitch_type='custom', pitch_length=105, pitch_width=68, line_zorder=2)
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#passes
pitch.arrows(passes.x0, passes.y0,
            passes.x1, passes.y1, color="blue", ax=ax['pitch'], zorder=3)
#shot
pitch.arrows(shot.x0, shot.y0,
            shot.x1, shot.y1, color="red", ax=ax['pitch'], zorder=3)
#other events as dotted lines
pitch.lines(not_pass.x0, not_pass.y0, not_pass.x1, not_pass.y1, color="grey", lw=1.5, ls='dotted', ax=ax['pitch'])
ax['title'].text(0.5, 0.5, 'Passes leading to a shot', ha='center', va='center', fontsize=30)
plt.show()

# Possesion chain that did not end with a shot
"""And here is one that did not end with a shot."""

#pick first chain that did not end with a shot
no_shot_chain_id = df.loc[df["shot_end"] == 0, "possesion_chain"].iloc[0]
chain = df.loc[df["possesion_chain"] == no_shot_chain_id]
passes = chain.loc[chain["type_displayName"] == "Pass"].iloc[:-1]
not_pass = chain.loc[chain["type_displayName"] != "Pass"].iloc[:-1]
bad_pass = chain.iloc[-1]
#plot
pitch = Pitch(line_color='black', pitch_type='custom', pitch_length=105, pitch_width=68, line_zorder=2)
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
pitch.arrows(passes.x0, passes.y0,
            passes.x1, passes.y1, color="blue", ax=ax['pitch'], zorder=3)
pitch.arrows(bad_pass.x0, bad_pass.y0,
            bad_pass.x1, bad_pass.y1, color="purple", ax=ax['pitch'], zorder=3)
pitch.scatter(bad_pass.x1, bad_pass.y1, marker='x', color="red", ax=ax['pitch'], zorder=3, s=200)
pitch.lines(not_pass.x0, not_pass.y0, not_pass.x1, not_pass.y1, color="grey", lw=1.5, ls='dotted', ax=ax['pitch'])
ax['title'].text(0.5, 0.5, 'Passes not ending in a shot', ha='center', va='center', fontsize=30)
plt.show()

#%%
# Save the dataframe with possesion chains for further use
df.to_parquet("possesion_chains_brasileirao_2025.parquet", index=False)
print(f"Saved {len(df)} rows to possesion_chains_brasileirao_2025.parquet")

