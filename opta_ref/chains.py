# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/chains.py
# Unchanged except imports (opta. -> opta_ref.). Do not edit here; re-copy from the reference.
"""Cadeias de posse Soccermatics adaptadas à Opta F24 / WhoScored (spec §5.1; B3.1–B3.2)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from opta_ref.conventions import (
    ADMIN_TYPES, AERIAL, CLAIM, CORNER_AWARDED, DEFENSIVE_IF_NEXT_SAME, FOUL, FOUL_COMMITTED_OUTCOME,
    KEEPER_HANDS, OFFSIDE_TYPES, OPP_GOOD_IF_OUTCOME1, OWN_BAD_ALWAYS, OWN_BAD_IF_OUTCOME0, PASS,
    PLAY_PERIODS, REMOVED_AFTER_SHOT, RESTART_PASS_QUALIFIERS, SHOT_TYPES, TACKLE,
)

SORT_COLS = ["game_id", "period_id", "minute", "second", "event_idx"]  # event_idx = ordem do JSON (auditoria A4)
CHAIN_KEY = ["game_id", "chain_id"]


def sort_events(ev: pd.DataFrame) -> pd.DataFrame:
    return ev.sort_values(SORT_COLS, kind="mergesort").reset_index(drop=True)


def same_group_next(game: np.ndarray, period: np.ndarray) -> np.ndarray:
    same = np.zeros(len(game), dtype=bool)
    same[:-1] = (game[1:] == game[:-1]) & (period[1:] == period[:-1])
    return same


def preprocess(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ordena, remove administrativos, marca kicked_out e remove CornerAwarded (§4.2 passo 2)."""
    ev = sort_events(events)
    t = ev["type_id"]
    admin = t.isin(ADMIN_TYPES) | ~ev["period_id"].isin(PLAY_PERIODS)
    neutral = ~admin & (t.isin(REMOVED_AFTER_SHOT) | ((t == AERIAL) & (ev["outcome"] == 0)))
    stream = ev[~(admin | neutral)].reset_index(drop=True)
    corner = (stream["type_id"] == CORNER_AWARDED).to_numpy()
    kept = stream[~corner].reset_index(drop=True)

    game = kept["game_id"].to_numpy()
    same_next = same_group_next(game, kept["period_id"].to_numpy())
    corners_seen = np.cumsum(corner)[~corner]
    corner_follows = np.zeros(len(kept), dtype=bool)
    corner_follows[:-1] = (corners_seen[1:] > corners_seen[:-1]) & (game[1:] == game[:-1])
    restart = ((kept["type_id"].to_numpy() == PASS)
               & kept[[f"q{q}" for q in RESTART_PASS_QUALIFIERS]].any(axis=1).to_numpy())
    restart_next = np.zeros(len(kept), dtype=bool)
    restart_next[:-1] = restart[1:]
    kept["kicked_out"] = (corner_follows | (restart_next & same_next)).astype(np.int8)
    kept["time_s"] = kept["minute"].astype("float64") * 60 + kept["second"].fillna(0)

    removed = pd.concat([
        ev[admin].assign(removed_reason="administrativo"),
        ev[neutral].assign(removed_reason="pos_chute_ou_aereo"),
        stream[corner].assign(removed_reason="corner_awarded"),
    ], ignore_index=True)
    return kept, removed


def isolate_chains(ev: pd.DataFrame) -> pd.DataFrame:
    """Contador `stop` de §5.1 sobre listas; `ev` deve vir de preprocess (ordenado, RangeIndex).
    Chute (sem q28) de um time diferente do time da cadeia em curso abre cadeia nova antes dele (auditoria B2)."""
    n = len(ev)
    game = ev["game_id"].to_numpy()
    team = ev["team_id"].to_numpy()
    t = ev["type_id"].to_numpy()
    outcome = ev["outcome"].to_numpy()
    same_next = same_group_next(game, ev["period_id"].to_numpy())
    same_prev = np.zeros(n, dtype=bool)
    same_prev[1:] = same_next[:-1]
    next_team = np.full(n, -1, dtype=np.int64)
    next_team[:-1] = team[1:]
    next_team[~same_next] = -1
    is_offside = np.isin(t, OFFSIDE_TYPES)
    prev_offside = np.zeros(n, dtype=bool)
    prev_offside[1:] = is_offside[:-1]
    prev_offside &= same_prev

    own_bad = (np.isin(t, OWN_BAD_IF_OUTCOME0) & (outcome == 0)) | np.isin(t, OWN_BAD_ALWAYS)
    opp_good = np.isin(t, OPP_GOOD_IF_OUTCOME1) & (outcome == 1)
    defensive = np.isin(t, DEFENSIVE_IF_NEXT_SAME) | ((t == TACKLE) & (outcome == 0))
    plus2 = ((defensive & (next_team == team))
             | ((t == CLAIM) & (outcome == 1)) | np.isin(t, KEEPER_HANDS)
             | np.isin(t, SHOT_TYPES)
             | ((t == FOUL) & (outcome == FOUL_COMMITTED_OUTCOME))
             | (is_offside & ~prev_offside)
             | (ev["kicked_out"].to_numpy() == 1))

    shot_open = np.isin(t, SHOT_TYPES) & ~ev["q28"].to_numpy(dtype=bool)
    game_l, team_l, next_l, shot_l = game.tolist(), team.tolist(), next_team.tolist(), shot_open.tolist()
    own_l, opp_l, plus2_l = own_bad.tolist(), opp_good.tolist(), plus2.tolist()
    same_prev_l, same_next_l = same_prev.tolist(), same_next.tolist()
    chain = np.empty(n, dtype=np.int64)
    cur_chain, cur_team, stop, size = 0, None, 0, 0
    for i in range(n):
        if i == 0 or game_l[i] != game_l[i - 1]:
            cur_chain, cur_team, stop, size = 0, team_l[i], 0, 0
        elif not same_prev_l[i]:
            cur_chain, cur_team, stop, size = cur_chain + 1, team_l[i], 0, 0
        elif shot_l[i] and team_l[i] != cur_team and size > 0:
            cur_chain, cur_team, stop, size = cur_chain + 1, team_l[i], 0, 0
        chain[i] = cur_chain
        size += 1
        stop += own_l[i] if team_l[i] == cur_team else opp_l[i]
        stop += 2 * plus2_l[i]
        if stop >= 2:
            stop = 0
            if same_next_l[i]:
                cur_chain, cur_team, size = cur_chain + 1, next_l[i], 0
    out = ev.copy()
    out["chain_id"] = chain
    return out


def chain_table(ev: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por cadeia: período, time, termina em falta, último evento do time da cadeia é chute sem q28."""
    real = ev[~ev["is_carry"]] if "is_carry" in ev else ev
    tail = real.groupby(CHAIN_KEY, sort=True).tail(1).set_index(CHAIN_KEY)
    team_last = real[real["is_chain_team"]].groupby(CHAIN_KEY, sort=True).tail(1).set_index(CHAIN_KEY)
    table = pd.DataFrame({"period_id": tail["period_id"], "chain_team_id": tail["chain_team_id"],
                          "ends_in_foul": tail["type_id"] == FOUL})
    is_shot = team_last["type_id"].isin(SHOT_TYPES) & ~team_last["q28"]
    table["last_is_shot"] = is_shot.reindex(table.index, fill_value=False).astype(bool)
    table["last_uid"] = team_last["event_uid"].reindex(table.index)
    return table.sort_index().reset_index()


def propagate_to_foul_chains(table: pd.DataFrame, values: np.ndarray) -> np.ndarray:
    """Cadeias terminadas em falta, antes de uma cadeia com valor > 0 no mesmo jogo e período, herdam o valor,
    voltando quantas cadeias de falta houver (B3.1 passo 3). Só herda a cadeia do mesmo time da cadeia de
    origem; a cadeia de falta do outro time não herda e não interrompe a volta (auditoria B1)."""
    g = table["game_id"].to_numpy()
    p = table["period_id"].to_numpy()
    team = table["chain_team_id"].to_numpy()
    foul = table["ends_in_foul"].to_numpy()
    v = np.asarray(values, dtype=float).copy()
    pending = None  # (valor, time) que chega à cadeia i vindo das seguintes
    for i in range(len(v) - 1, -1, -1):
        if i + 1 < len(v) and (g[i] != g[i + 1] or p[i] != p[i + 1]):
            pending = None
        if v[i] > 0:
            pending = (v[i], team[i])
        elif foul[i] and pending is not None:
            if team[i] == pending[1]:
                v[i] = pending[0]
        else:
            pending = None
    return v


def prepare_chains(ev: pd.DataFrame) -> pd.DataFrame:
    counts = ev.groupby(CHAIN_KEY + ["team_id"], sort=False).size().rename("n").reset_index()
    first_team = ev.groupby(CHAIN_KEY, sort=False)["team_id"].first().rename("first_team").reset_index()
    counts = counts.merge(first_team, on=CHAIN_KEY)
    counts["is_first"] = counts["team_id"] == counts["first_team"]
    modal = (counts.sort_values(CHAIN_KEY + ["n", "is_first"], ascending=[True, True, False, False], kind="mergesort")
             .drop_duplicates(CHAIN_KEY)[CHAIN_KEY + ["team_id"]]
             .rename(columns={"team_id": "chain_team_id"}))
    ev = ev.merge(modal, on=CHAIN_KEY, how="left", validate="many_to_one")
    ev["is_chain_team"] = ev["team_id"] == ev["chain_team_id"]

    team_rows = ev[ev["is_chain_team"]]
    first = team_rows.groupby(CHAIN_KEY, sort=False).head(1)
    last = team_rows.groupby(CHAIN_KEY, sort=False).tail(1)
    ev["chain_first"] = False
    ev.loc[first.index, "chain_first"] = True
    ev["chain_last"] = False
    ev.loc[last.index, "chain_last"] = True
    duration = (last.set_index(CHAIN_KEY)["time_s"] - first.set_index(CHAIN_KEY)["time_s"]).rename("chain_duration_s")
    ev = ev.join(duration, on=CHAIN_KEY)

    table = chain_table(ev)
    table["shot_end"] = propagate_to_foul_chains(table, table["last_is_shot"].astype(float).to_numpy()).astype(np.int8)
    return ev.merge(table[CHAIN_KEY + ["shot_end"]], on=CHAIN_KEY, how="left", validate="many_to_one")
