"""Glue between this repo's upstream scripts and opta_ref (plataforma-scouting @ c027daa).

possession_chain.py, xG_brasileirao.py and xT_brasileirao.py call these helpers; the metric logic itself lives
unchanged in opta_ref/. Stage order follows the reference s01/s03: preprocess -> isolate_chains ->
prepare_chains -> add_carries -> add_model_coords, then xG -> chain_xg -> xT.
"""
from pathlib import Path

import pandas as pd

from opta_ref.carries import add_carries
from opta_ref.chains import isolate_chains, prepare_chains, preprocess
from opta_ref.geometry import add_model_coords
from opta_ref.ingest import concat_tables, load_json, parse_game
from opta_ref.models.onnx_io import load_bundle

ROOT = Path(__file__).resolve().parent
JSON_DIR = ROOT / "Brasileirão_2025"
EVENTS_PARQUET = ROOT / "brasileirao_2025_events.parquet"  # written by MatchAnalysis_PlayStyle_2025.py
REF_STAGE01 = ROOT / "_ref_stage01_2025.parquet"  # intermediate: chains + carries + metres (+ xG after xG step)
CHAINS_PARQUET = ROOT / "possesion_chains_brasileirao_2025.parquet"
XG_PARQUET = ROOT / "xG_brasileirao_2025.parquet"
XT_PARQUET = ROOT / "xT_brasileirao_2025.parquet"
MODELS_DIR = ROOT / "opta_ref" / "models"
MODEL_VERSION = "20260924"

# reference column -> old column name read by MatchAnalysis_PlayStyle_2025.py (renamed there at load)
OLD_NAMES = {
    "team_id": "teamId", "period_id": "period_value", "end_x": "endX", "end_y": "endY", "type_id": "type_value",
    "event_id": "eventId", "outcome": "outcomeType_value", "is_touch": "isTouch", "is_goal": "isGoal",
    "is_shot": "isShot",
}


def load_model(name: str):
    return load_bundle(MODELS_DIR, name, MODEL_VERSION)


def reference_events() -> pd.DataFrame:
    """The reference `events` table for the games in EVENTS_PARQUET, parsed from the same JSONs."""
    game_ids = sorted(int(g) for g in pd.read_parquet(EVENTS_PARQUET, columns=["game_id"])["game_id"].unique())
    parts = [parse_game(load_json(JSON_DIR / f"{g}.json"), g, "BRA1", 2025)["events"] for g in game_ids]
    return concat_tables({"events": parts})["events"]


def stage01(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(chains without carries, full s01 frame with carries and metre coordinates), both in game order."""
    kept, _ = preprocess(events)
    chained = prepare_chains(isolate_chains(kept))
    return chained, add_model_coords(add_carries(chained))


def chains_table(chained: pd.DataFrame) -> pd.DataFrame:
    """Chain-team rows under the old column names, plus type_displayName / qualifiers from EVENTS_PARQUET."""
    raw = pd.read_parquet(EVENTS_PARQUET, columns=["game_id", "type_displayName", "qualifiers"])
    raw["event_idx"] = raw.groupby("game_id").cumcount()  # EVENTS_PARQUET keeps each game's JSON event order
    rows = chained[chained["is_chain_team"]]
    out = rows[["game_id", "id", "event_idx", "team_id", "period_id", "minute", "second", "x", "y", "end_x", "end_y",
                "type_id", "event_id", "outcome", "is_touch", "is_goal", "is_shot", "chain_team_id", "shot_end"]]
    out = out.rename(columns=OLD_NAMES).assign(
        possesion_chain=rows["chain_id"] + 1,  # the main file's `possessionId != 0` filters keep every chain
        possesion_chain_team=rows["chain_team_id"],
    )
    out = out.merge(raw, on=["game_id", "event_idx"], how="left", validate="one_to_one")
    assert out["type_displayName"].notna().all(), "event_idx does not line up with EVENTS_PARQUET"
    return out
