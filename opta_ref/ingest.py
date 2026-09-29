# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/ingest.py
# Unchanged except imports (opta. -> opta_ref.). Do not edit here; re-copy from the reference.
"""JSON do WhoScored → tabelas de 00_ingest (spec §3.2–§3.3)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from opta_ref.conventions import QUALIFIERS_NUMERIC, QUALIFIERS_USED

TABLES = ("games", "teams", "players", "formations", "events")
COLUMNS = {
    "games": ["game_id", "liga", "temporada", "date", "home_team_id", "away_team_id",
              "home_score", "away_score", "expanded_max_minute", "has_events"],
    "teams": ["game_id", "team_id", "team_name", "side"],
    "players": ["game_id", "team_id", "player_id", "player_name", "position_json", "is_starter", "shirt_no"],
    "formations": ["game_id", "team_id", "segment", "period", "start_min", "end_min", "formation_name",
                   "slot", "player_id", "vertical", "horizontal"],
    "events": ["game_id", "event_uid", "id", "event_idx", "event_id", "period_id", "minute", "second", "expanded_minute",
               "team_id", "player_id", "type_id", "outcome", "x", "y", "end_x", "end_y",
               "related_event_id", "related_player_id", "is_touch", "is_shot", "is_goal", "is_own_goal"]
              + [f"q{q}" for q in QUALIFIERS_USED] + [f"q{q}" for q in QUALIFIERS_NUMERIC],
}
DTYPES = {
    "games": {"game_id": "int64", "temporada": "int64", "home_team_id": "Int64", "away_team_id": "Int64",
              "home_score": "Int16", "away_score": "Int16", "expanded_max_minute": "Int32", "has_events": "bool"},
    "teams": {"game_id": "int64", "team_id": "int64"},
    "players": {"game_id": "int64", "team_id": "int64", "player_id": "int64", "is_starter": "bool",
                "shirt_no": "Int16"},
    "formations": {"game_id": "int64", "team_id": "int64", "segment": "int16", "period": "Int16",
                   "start_min": "int32", "end_min": "int32", "slot": "int16", "player_id": "int64",
                   "vertical": "float64", "horizontal": "float64"},
    "events": {"game_id": "int64", "event_uid": "int64", "id": "int64", "event_idx": "int32", "event_id": "int64",
               "period_id": "int16", "minute": "int32", "second": "float64", "expanded_minute": "Int32",
               "team_id": "int64", "player_id": "Int64", "type_id": "int32", "outcome": "int8",
               "x": "float64", "y": "float64", "end_x": "float64", "end_y": "float64",
               "related_event_id": "Int64", "related_player_id": "Int64",
               "is_touch": "bool", "is_shot": "bool", "is_goal": "bool", "is_own_goal": "bool",
               **{f"q{q}": "bool" for q in QUALIFIERS_USED},
               **{f"q{q}": "float64" for q in QUALIFIERS_NUMERIC}},
}


def load_json(path: Path) -> dict | None:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _score(text) -> tuple[int | None, int | None]:
    try:
        home, away = (int(part) for part in str(text).split(":"))
        return home, away
    except (TypeError, ValueError):
        return None, None


def _float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def _event_row(e: dict, game_id: int, idx: int) -> dict:
    """`idx` = posição no array `events` do JSON: a ordem causal do jogo (o `id` não é cronológico)."""
    quals = {q["type"]["value"]: q.get("value") for q in e.get("qualifiers", [])}
    row = {
        "game_id": game_id, "event_uid": e["id"], "id": e["id"], "event_idx": idx, "event_id": e.get("eventId", 0),
        "period_id": (e.get("period") or {}).get("value", 0), "minute": e["minute"], "second": e.get("second", np.nan),
        "expanded_minute": e.get("expandedMinute"), "team_id": e["teamId"], "player_id": e.get("playerId"),
        "type_id": e["type"]["value"], "outcome": e["outcomeType"]["value"],
        "x": e.get("x", np.nan), "y": e.get("y", np.nan),
        "end_x": e.get("endX", np.nan), "end_y": e.get("endY", np.nan),
        "related_event_id": e.get("relatedEventId"), "related_player_id": e.get("relatedPlayerId"),
        "is_touch": bool(e.get("isTouch", False)), "is_shot": bool(e.get("isShot", False)),
        "is_goal": bool(e.get("isGoal", False)), "is_own_goal": bool(e.get("isOwnGoal", False)),
    }
    for q in QUALIFIERS_USED:
        row[f"q{q}"] = q in quals
    for q in QUALIFIERS_NUMERIC:
        row[f"q{q}"] = _float(quals.get(q))
    return row


def parse_game(g: dict | None, game_id: int, liga: str, temporada: int) -> dict[str, pd.DataFrame]:
    events = (g or {}).get("events") or []
    rows: dict[str, list] = {name: [] for name in TABLES}
    home_score, away_score = _score((g or {}).get("ftScore") or (g or {}).get("score"))
    rows["games"].append({
        "game_id": game_id, "liga": liga, "temporada": temporada, "date": (g or {}).get("startDate"),
        "home_team_id": g["home"]["teamId"] if g else None, "away_team_id": g["away"]["teamId"] if g else None,
        "home_score": home_score, "away_score": away_score,
        "expanded_max_minute": (g or {}).get("expandedMaxMinute"), "has_events": bool(events),
    })
    if g:
        names = {int(k): v for k, v in ((g.get("playerIdNameDictionary") or {}).items())}
        for side in ("home", "away"):
            team = g[side]
            tid = team["teamId"]
            rows["teams"].append({"game_id": game_id, "team_id": tid, "team_name": team.get("name"), "side": side})
            for p in team.get("players", []):
                rows["players"].append({
                    "game_id": game_id, "team_id": tid, "player_id": p["playerId"],
                    "player_name": p.get("name") or names.get(p["playerId"]),
                    "position_json": p.get("position"), "is_starter": bool(p.get("isFirstEleven", False)),
                    "shirt_no": p.get("shirtNo"),
                })
            for segment, fo in enumerate(team.get("formations", [])):
                positions = fo.get("formationPositions", [])
                for pid, slot in zip(fo["playerIds"], fo["formationSlots"]):
                    pos = positions[slot - 1] if 0 < slot <= len(positions) else {}
                    rows["formations"].append({
                        "game_id": game_id, "team_id": tid, "segment": segment, "period": fo.get("period"),
                        "start_min": fo["startMinuteExpanded"], "end_min": fo["endMinuteExpanded"],
                        "formation_name": fo.get("formationName"), "slot": slot, "player_id": pid,
                        "vertical": pos.get("vertical", np.nan), "horizontal": pos.get("horizontal", np.nan),
                    })
    rows["events"] = [_event_row(e, game_id, i) for i, e in enumerate(events)]
    return {name: pd.DataFrame(r, columns=COLUMNS[name]) for name, r in rows.items()}


def concat_tables(parts: dict[str, list[pd.DataFrame]]) -> dict[str, pd.DataFrame]:
    out = {}
    for name in TABLES:
        frames = [f for f in parts.get(name, []) if len(f)]
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS[name])
        out[name] = df.astype(DTYPES.get(name, {}))
    return out
