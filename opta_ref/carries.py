# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/carries.py
# Unchanged except imports (opta. -> opta_ref.). Do not edit here; re-copy from the reference.
"""Conduções sintéticas dentro da mesma cadeia e do mesmo time (spec §5.2; A3.1)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from opta_ref.conventions import (
    CARRY_BREAKING_TYPES, CARRY_MAX_GAP_S, CARRY_MIN_GAIN, CARRY_PROG_X, CARRY_TYPE, FOUL, FOUL_COMMITTED_OUTCOME,
    PASS, PROG_CARRY_TYPE, QUALIFIERS_NUMERIC, QUALIFIERS_USED,
)


def add_carries(ev: pd.DataFrame) -> pd.DataFrame:
    """Condução entre dois eventos seguidos do mesmo jogo, período, cadeia e time, com ganho > 5 em x. Não há
    condução até ação defensiva/disputa ou falta cometida, a partir de passe errado, nem com pausa > 30 s (A8)."""
    n = len(ev)
    base = ev.assign(is_carry=False, carry_kind=None, _seq=np.arange(n) * 2)
    if n == 0:
        return base.drop(columns="_seq")
    x = ev["x"].to_numpy(dtype=float)
    y = ev["y"].to_numpy(dtype=float)
    raw_end_x = ev["end_x"].to_numpy(dtype=float)
    raw_end_y = ev["end_y"].to_numpy(dtype=float)
    end_x = np.where(np.isnan(raw_end_x), x, raw_end_x)
    end_y = np.where(np.isnan(raw_end_y), y, raw_end_y)

    same = np.ones(n, dtype=bool)
    same[0] = False
    for col in ("game_id", "period_id", "chain_id", "team_id"):
        values = ev[col].to_numpy()
        same[1:] &= values[1:] == values[:-1]
    prev_x = np.full(n, np.nan)
    prev_y = np.full(n, np.nan)
    prev_x[1:] = end_x[:-1]
    prev_y[1:] = end_y[:-1]
    t = ev["type_id"].to_numpy()
    outcome = ev["outcome"].to_numpy()
    time_s = ev["time_s"].to_numpy(dtype=float)
    prev_failed_pass = np.zeros(n, dtype=bool)
    prev_failed_pass[1:] = (t[:-1] == PASS) & (outcome[:-1] == 0)
    gap = np.full(n, np.inf)
    gap[1:] = time_s[1:] - time_s[:-1]
    breaks = np.isin(t, CARRY_BREAKING_TYPES) | ((t == FOUL) & (outcome == FOUL_COMMITTED_OUTCOME))
    is_carry = (same & ((x - prev_x) > CARRY_MIN_GAIN) & ~breaks & ~prev_failed_pass
                & (gap <= CARRY_MAX_GAP_S))

    carries = base.loc[is_carry].copy()
    progressive = prev_x[is_carry] >= CARRY_PROG_X
    carries["type_id"] = np.where(progressive, PROG_CARRY_TYPE, CARRY_TYPE).astype(ev["type_id"].dtype)
    carries["carry_kind"] = np.where(progressive, "progressive carry", "carry")
    carries["end_x"] = carries["x"]
    carries["end_y"] = carries["y"]
    carries["x"] = prev_x[is_carry]
    carries["y"] = prev_y[is_carry]
    carries["event_uid"] = -carries["event_uid"]
    carries["event_id"] = -1
    carries["outcome"] = np.int8(1)
    carries["is_touch"] = True
    for col in ("is_shot", "is_goal", "is_own_goal", "chain_first", "chain_last"):
        carries[col] = False
    carries["kicked_out"] = np.int8(0)
    for col in ("related_event_id", "related_player_id"):
        carries[col] = pd.Series(pd.NA, index=carries.index, dtype="Int64")
    for q in QUALIFIERS_USED:
        carries[f"q{q}"] = False
    for q in QUALIFIERS_NUMERIC:
        carries[f"q{q}"] = np.nan
    carries["is_carry"] = True
    carries["_seq"] = carries["_seq"] - 1

    out = pd.concat([base, carries], ignore_index=True).sort_values("_seq", kind="mergesort")
    return out.drop(columns="_seq").reset_index(drop=True)
