"""Shared team-metric concepts for MatchAnalysis_PlayStyle_2025.py — one definition per concept.

Decisions: docs/variable_consistency_decisions.md (D1–D13). Definitions follow plataforma-scouting @ c027daa,
pipelines/opta/processing/opta/metrics/{context,impl_contagem,impl_sequencia,area}.py, in this repo's column names:
start_x/start_y/end_x/end_y (Opta 0–100), type_id, outcome (bool or 0/1), team_id, period_id, time (s), q<N> flags,
chain_id / is_chain_team / chain_first / chain_last (reference chains, via _ref_stage01_2025.parquet).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FINAL_THIRD_X = 66.67
HALF_X = 50.0
LOW_BLOCK_X = 40.0
BOX_X, BOX_Y_MIN, BOX_Y_MAX = 83.0, 21.1, 78.9
X_METRES = 1.05  # Opta x unit -> metres on a 105 m pitch
PROG_MIN_LENGTH, PROG_MIN_GAIN = 10.0, 0.25
WINDOW_S = 10.0
COUNTERPRESS_S = 5.0

FOUL = 4
FOUL_COMMITTED = 0  # WhoScored: 0 = committed, 1 = suffered (inverse of the F24 spec)
SHOT_TYPES = (13, 14, 15, 16)
CARRY_TYPES = (1000, 2000)
POSSESSION_TOUCH_TYPES = (1, 13, 14, 15, 16, 3, 61, 42, 50, 1000, 2000)
RESTART_PASS_QUALIFIERS = (107, 124, 5, 6)
XT_SET_PIECE_QUALIFIERS = (6, 107, 124)
SET_PIECE_CHAIN_START_Q = (5, 6, 24, 25, 26)
LOSS_TYPES = ((1, 0), (3, 0), (50, 1), (51, 1), (61, 0))
INTENSITY_TYPES = (7, 8, 44, 45, 49)
HEIGHT_TYPES = (7, 8, 12, 49)
PPDA_TYPES = (7, 8, 45)
QUALIFIER_FLAGS = (1, 2, 4, 5, 6, 9, 24, 25, 26, 28, 107, 124, 214)
PLAY = ["game_id", "period_id"]


# qualifiers -------------------------------------------------------------------------------------------------------
def qualifier_ids(q) -> set[int]:
    """Qualifier ids of one event, whatever the storage: dict keyed by id (socceraction), or a list / ndarray of
    {"type": {"value": id}} dicts (raw WhoScored JSON, chains parquet)."""
    if isinstance(q, dict):
        return {int(k) for k in q}
    if q is None or (isinstance(q, float) and np.isnan(q)):
        return set()
    ids = set()
    for item in q:
        value = item.get("type", {}).get("value") if isinstance(item, dict) else item
        if value is not None:
            ids.add(int(value))
    return ids


def add_qualifier_flags(frame: pd.DataFrame, ids=QUALIFIER_FLAGS) -> pd.DataFrame:
    sets = frame["qualifiers"].map(qualifier_ids)
    return frame.assign(**{f"q{q}": sets.map(lambda s, q=q: q in s).astype(bool) for q in ids})


# event classes ----------------------------------------------------------------------------------------------------
def _outcome(f: pd.DataFrame) -> pd.Series:
    return f["outcome"].astype(float)


def in_box(x: pd.Series, y: pd.Series) -> pd.Series:
    return (x >= BOX_X) & (y >= BOX_Y_MIN) & (y <= BOX_Y_MAX)


def in_final_third(x: pd.Series) -> pd.Series:
    return x >= FINAL_THIRD_X


def completed_pass(f: pd.DataFrame) -> pd.Series:
    return (f["type_id"] == 1) & (_outcome(f) == 1)


def restart_pass(f: pd.DataFrame) -> pd.Series:
    """Throw-in, goal kick, free kick or corner pass (reference `restart_pass`)."""
    return (f["type_id"] == 1) & f[[f"q{q}" for q in RESTART_PASS_QUALIFIERS]].any(axis=1)


def progressive(f: pd.DataFrame) -> pd.Series:
    """Length >= 10 Opta units and x gain >= 25% of the distance left to the goal line (reference `progressive`)."""
    dx, dy = f["end_x"] - f["start_x"], f["end_y"] - f["start_y"]
    with np.errstate(divide="ignore", invalid="ignore"):
        gain = dx / (100 - f["start_x"])
    return (np.hypot(dx, dy) >= PROG_MIN_LENGTH) & (gain >= PROG_MIN_GAIN)


def possession_touch(f: pd.DataFrame) -> pd.Series:
    """On-ball possession action (reference `possession_touch`): pass, shot, take-on, ball touch, carry…; no
    restart pass, penalty, direct free-kick shot or own goal."""
    t = f["type_id"]
    shot = t.isin(SHOT_TYPES)
    return t.isin(POSSESSION_TOUCH_TYPES) & ~restart_pass(f) & ~f["q9"] & ~(shot & f["q26"]) & ~f["q28"]


def npxg_shots(f: pd.DataFrame) -> pd.Series:
    """Shots 13–16 without penalties (q9) and own goals (q28)."""
    return f["type_id"].isin(SHOT_TYPES) & ~f["q9"] & ~f["q28"]


def committed_foul(f: pd.DataFrame) -> pd.Series:
    return (f["type_id"] == FOUL) & (_outcome(f) == FOUL_COMMITTED)


def intensity_mask(f: pd.DataFrame) -> pd.Series:
    """D5 defensive intensity (reference #35): tackle, interception, aerial, challenge, ball recovery, committed foul."""
    return f["type_id"].isin(INTENSITY_TYPES) | committed_foul(f)


def height_mask(f: pd.DataFrame) -> pd.Series:
    """D5 defensive height (reference area.py): tackle, interception, clearance, ball recovery, committed foul."""
    return f["type_id"].isin(HEIGHT_TYPES) | committed_foul(f)


def ppda_action_mask(f: pd.DataFrame) -> pd.Series:
    """D5 PPDA denominator: tackle, interception, challenge, committed foul."""
    return f["type_id"].isin(PPDA_TYPES) | committed_foul(f)


def ground_duels(f: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """(won, lost) defensive ground duels (reference `ground_duels`): won = tackle (7), lost = dribbled past (45)."""
    return f["type_id"] == 7, f["type_id"] == 45


def recovery_mask(f: pd.DataFrame) -> pd.Series:
    """Interception, tackle won, ball recovery (8, 7/1, 49)."""
    t = f["type_id"]
    return (t == 8) | ((t == 7) & (_outcome(f) == 1)) | (t == 49)


def set_piece_chain_rows(f: pd.DataFrame) -> pd.Series:
    """Rows of chains whose first event is a free kick / corner / set-piece shot (reference area.py)."""
    heads = f.drop_duplicates(["game_id", "chain_id"])
    flagged = heads.loc[heads[[f"q{q}" for q in SET_PIECE_CHAIN_START_Q]].any(axis=1), ["game_id", "chain_id"]]
    keys = pd.MultiIndex.from_frame(f[["game_id", "chain_id"]])
    return pd.Series(keys.isin(pd.MultiIndex.from_frame(flagged)), index=f.index)


# sequence helpers -------------------------------------------------------------------------------------------------
def neighbour(frame: pd.DataFrame, column: str, step: int) -> np.ndarray:
    """Value of `column` on the next (step=1) or previous (step=-1) row of the same game and period, NaN otherwise."""
    n = len(frame)
    same = np.ones(n, dtype=bool)
    for col in PLAY:
        v = frame[col].to_numpy()
        ok = np.zeros(n, dtype=bool)
        if step == 1:
            ok[:-1] = v[:-1] == v[1:]
        else:
            ok[1:] = v[1:] == v[:-1]
        same &= ok
    values = frame[column].to_numpy(dtype=float)
    out = np.full(n, np.nan)
    if step == 1:
        out[:-1] = values[1:]
    else:
        out[1:] = values[:-1]
    return np.where(same, out, np.nan)


def play_frame(ev: pd.DataFrame) -> pd.DataFrame:
    """Real events (no carry rows) that are in the reference chains, in game order — the reference's `df`."""
    return ev[~ev["type_id"].isin(CARRY_TYPES) & ev["chain_id"].notna()]


def loss_mask(play: pd.DataFrame) -> pd.Series:
    """D3 (reference `loss_events`): last own event of a chain, of a losing type, followed by an opponent event."""
    t, o = play["type_id"], _outcome(play)
    kind = np.zeros(len(play), dtype=bool)
    for type_id, outcome in LOSS_TYPES:
        kind |= ((t == type_id) & (o == outcome)).to_numpy()
    nxt = neighbour(play, "team_id", 1)
    changes = ~np.isnan(nxt) & (nxt != play["team_id"].to_numpy())
    return pd.Series(kind & play["chain_last"].fillna(False).to_numpy(dtype=bool) & changes, index=play.index)


def possession_won_mask(play: pd.DataFrame) -> pd.Series:
    """D4 (reference `possession_won_mask`): recovery followed by an own-team event; a recovery right after the same
    team's recovery is the same regain and is not counted again."""
    rec = recovery_mask(play).to_numpy()
    team = play["team_id"].to_numpy()
    won = rec & (neighbour(play, "team_id", 1) == team)
    prev_rec = np.zeros(len(play), dtype=bool)
    prev_rec[1:] = rec[:-1]
    repeat = prev_rec & (neighbour(play, "team_id", -1) == team)
    return pd.Series(won & ~repeat, index=play.index)


def next_event(frame: pd.DataFrame, from_mask, to_mask) -> pd.DataFrame:
    """For each `from_mask` row: position (in `frame`) of the next `to_mask` row of the same team, game and period,
    and the seconds between them (NaN when there is none)."""
    df = frame[["game_id", "period_id", "team_id", "time"]].assign(_pos=np.arange(len(frame), dtype=float))
    a = df[np.asarray(from_mask, dtype=bool)]
    b = df[np.asarray(to_mask, dtype=bool)].rename(columns={"time": "to_time"})
    b = b.assign(to_pos=b["_pos"])
    m = pd.merge_asof(a, b, on="_pos", by=["game_id", "period_id", "team_id"], direction="forward",
                      allow_exact_matches=False)
    return pd.DataFrame({"game_id": m["game_id"].to_numpy(), "team_id": m["team_id"].to_numpy(),
                         "from_pos": m["_pos"].to_numpy(), "to_pos": m["to_pos"].to_numpy(),
                         "seconds": (m["to_time"] - m["time"]).to_numpy()})


def counterpress(play: pd.DataFrame) -> pd.DataFrame:
    """D6 (reference `counterpressing`): one row per loss; regained = the team won the ball back within 5 s."""
    t = next_event(play, loss_mask(play), possession_won_mask(play))
    return t.assign(regained=t["seconds"] <= COUNTERPRESS_S)[["game_id", "team_id", "regained"]]


# zones and chains -------------------------------------------------------------------------------------------------
def _in_zone(x: pd.Series, y: pd.Series, zone: str) -> pd.Series:
    return in_box(x, y) if zone == "box" else in_final_third(x)


def zone_hits(f: pd.DataFrame, zone: str) -> pd.Series:
    """D2: the row is an action located in the zone — its start, or the end of a completed pass or of a carry.
    Shot ends and failed-pass ends never count."""
    end_counts = completed_pass(f) | f["type_id"].isin(CARRY_TYPES)
    return _in_zone(f["start_x"], f["start_y"], zone) | (end_counts & _in_zone(f["end_x"], f["end_y"], zone))


def chain_table(ev: pd.DataFrame) -> pd.DataFrame:
    """One row per reference chain, from its chain-team rows (carries included)."""
    cols = ["game_id", "chain_id", "team_id", "starts_in_third", "starts_in_box", "reaches_third", "reaches_box",
            "has_shot"]
    c = ev[ev["is_chain_team"].fillna(False).astype(bool) & ev["chain_id"].notna()]
    if c.empty:
        return pd.DataFrame(columns=cols)
    keys = [c["game_id"], c["chain_id"]]
    first = c.groupby(keys, sort=False).head(1).set_index(["game_id", "chain_id"])
    out = pd.DataFrame({
        "team_id": first["team_id"],
        "starts_in_third": in_final_third(first["start_x"]),
        "starts_in_box": in_box(first["start_x"], first["start_y"]),
        "reaches_third": zone_hits(c, "third").groupby(keys).any(),
        "reaches_box": zone_hits(c, "box").groupby(keys).any(),
        "has_shot": c["type_id"].isin(SHOT_TYPES).groupby(keys).any(),
    })
    return out.reset_index()[cols]


def after_regain(ev: pd.DataFrame, regain_mask, loss_mask_, window: float = WINDOW_S) -> pd.DataFrame:
    """D2 window: rows of `ev` by the regaining team after a regain, in the same game and period, within `window` s,
    before that team's next loss and inside the recovering chain (the chain of the first such row). Each row belongs
    to the latest regain (`reg_idx`, `reg_time`); regain rows themselves are excluded."""
    regain = np.asarray(regain_mask, dtype=bool)
    e = ev.assign(_pos=np.arange(len(ev), dtype=float))
    if not regain.any():
        return e.iloc[:0].assign(reg_idx=pd.Series(dtype=float), reg_time=pd.Series(dtype=float))
    stop = next_event(e, regain, loss_mask_)["to_pos"].to_numpy()
    reg = e[regain]
    r = reg[["game_id", "period_id", "team_id", "_pos"]].reset_index(drop=True).assign(
        reg_idx=reg.index.to_numpy(), reg_time=reg["time"].to_numpy(), stop=np.where(np.isnan(stop), np.inf, stop))
    m = pd.merge_asof(e.reset_index(names="_label"), r, on="_pos", by=["game_id", "period_id", "team_id"],
                      direction="backward", allow_exact_matches=False)
    keep = (m["reg_idx"].notna() & (m["time"] - m["reg_time"] <= window) & (m["_pos"] < m["stop"])
            & ~regain).to_numpy()
    m = m[keep]
    chain = m["chain_id"].fillna(-1)
    m = m[chain == chain.groupby(m["reg_idx"]).transform("first")]
    return m.set_index("_label").drop(columns=["_pos", "stop"]).rename_axis(ev.index.name)


# teams ------------------------------------------------------------------------------------------------------------
def _opponent_pairs(pairs: pd.DataFrame) -> pd.DataFrame:
    p = pairs[["game_id", "team_id"]].drop_duplicates()
    m = p.merge(p, on="game_id", suffixes=("", "_opp"))
    return m[m["team_id"] != m["team_id_opp"]]


def to_opponent(table: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Re-key a (game_id, team_id, …) table to the opponent of each team_id."""
    m = table.merge(_opponent_pairs(pairs), on=["game_id", "team_id"])
    return m.drop(columns="team_id").rename(columns={"team_id_opp": "team_id"})


def goal_team(f: pd.DataFrame, pairs: pd.DataFrame) -> pd.Series:
    """Team credited with each row's goal: own goals (q28, logged on the conceding team) go to the opponent."""
    opp = f[["game_id", "team_id"]].merge(_opponent_pairs(pairs), on=["game_id", "team_id"], how="left")
    return pd.Series(np.where(f["q28"].to_numpy(), opp["team_id_opp"].to_numpy(), f["team_id"].to_numpy()),
                     index=f.index)
