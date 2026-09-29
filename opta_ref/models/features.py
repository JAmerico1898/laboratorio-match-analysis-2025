# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/models/features.py
# Unchanged except imports (opta. -> opta_ref.). Do not edit here; re-copy from the reference.
"""Features e rótulos de xG, xA e xT (spec §6; ajustes A9, A10)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from opta_ref.conventions import (
    CARRY_TYPE, GOAL, PASS, PROG_CARRY_TYPE, Q_OWN_GOAL, Q_PENALTY, SHOT_TYPES, TAKE_ON,
    XA_FLAG_QUALIFIERS, XG_FLAG_QUALIFIERS,
)

GOAL_WIDTH = 7.32
XG_GEOMETRY = ["angle", "distance", "X", "C", "X2", "C2", "AX"]
XG_FLAGS = list(XG_FLAG_QUALIFIERS)
XA_FEATURES = ["x0", "c0", "x1", "c1", *XA_FLAG_QUALIFIERS]
XT_FEATURES = ["x0", "c0", "x1", "c1", "is_pass", "is_take_on", "is_carry"]
XT_STATE_FEATURES = ["x0", "c0"]  # V(início): valor de ter a bola no ponto de partida da ação
CARRY_TYPES = (CARRY_TYPE, PROG_CARRY_TYPE)


def _flags(ev: pd.DataFrame, spec: dict[str, tuple[int, ...]]) -> pd.DataFrame:
    return pd.DataFrame({name: ev[[f"q{q}" for q in qs]].any(axis=1).astype(np.int8) for name, qs in spec.items()},
                        index=ev.index)


def shots(ev: pd.DataFrame) -> pd.DataFrame:
    s = ev[ev["type_id"].isin(SHOT_TYPES) & ~ev[f"q{Q_OWN_GOAL}"]]
    X = (100 - s["x"]) * 1.05
    C = (s["y"] - 50).abs() * 0.68
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.arctan(GOAL_WIDTH * X / (X ** 2 + C ** 2 - (GOAL_WIDTH / 2) ** 2))
    out = pd.DataFrame({
        "game_id": s["game_id"], "event_uid": s["event_uid"], "team_id": s["team_id"],
        "is_penalty": s[f"q{Q_PENALTY}"].astype(bool), "goal": (s["type_id"] == GOAL).astype(np.int8),
        "angle": np.where(raw > 0, raw, raw + np.pi), "distance": np.sqrt(X ** 2 + C ** 2),
        "X": X, "C": C, "X2": X ** 2, "C2": C ** 2,
    }, index=s.index)
    out["AX"] = out["angle"] * out["X"]
    return pd.concat([out, _flags(s, XG_FLAG_QUALIFIERS)], axis=1)


def passes_for_xa(ev: pd.DataFrame) -> pd.DataFrame:
    p = ev[(ev["type_id"] == PASS) & (ev["outcome"] == 1) & ~ev["is_carry"]]
    out = pd.concat([p[["game_id", "event_uid", "team_id", "event_id", "x0", "c0", "x1", "c1"]],
                     _flags(p, XA_FLAG_QUALIFIERS)], axis=1)
    s = ev[ev["type_id"].isin(SHOT_TYPES) & ~ev[f"q{Q_OWN_GOAL}"] & ev["q55"].notna()]
    xg = s["xG"].to_numpy() if "xG" in s else np.full(len(s), np.nan)
    links = pd.DataFrame({"game_id": s["game_id"].to_numpy(), "team_id": s["team_id"].to_numpy(),
                          "event_id": s["q55"].astype("int64").to_numpy(), "assist_xg": xg})
    links = links.groupby(["game_id", "team_id", "event_id"], as_index=False)["assist_xg"].max()
    links["is_assist"] = np.int8(1)
    out = out.merge(links, on=["game_id", "team_id", "event_id"], how="left")
    out["is_assist"] = out["is_assist"].fillna(0).astype(np.int8)
    return out


def xt_actions(ev: pd.DataFrame) -> pd.DataFrame:
    """Ações que completaram o deslocamento: passe e drible com outcome 1 e conduções (auditoria B3)."""
    done = (ev["type_id"].isin((PASS, TAKE_ON)) & (ev["outcome"] == 1)) | ev["type_id"].isin(CARRY_TYPES)
    a = ev[done & ev["x1"].notna()]
    cols = ["game_id", "event_uid", "is_chain_team", "shot_end", "x0", "c0", "x1", "c1"]
    out = a[cols + (["chain_xg"] if "chain_xg" in a else [])].copy()
    out["is_pass"] = (a["type_id"] == PASS).astype(np.int8)
    out["is_take_on"] = (a["type_id"] == TAKE_ON).astype(np.int8)
    out["is_carry"] = a["type_id"].isin(CARRY_TYPES).astype(np.int8)
    return out
