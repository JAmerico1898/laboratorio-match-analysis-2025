"""Parity of this repo's chains / xG / xT outputs with plataforma-scouting @ c027daa.

The output parquets must already exist (run MatchAnalysis_PlayStyle_2025.py, or possession_chain.py,
xG_brasileirao.py and xT_brasileirao.py in that order). Parity tests rebuild 5 games with the *unmodified*
reference code from a clone: set PLATAFORMA_SCOUTING_DIR to it (git clone ... && git checkout c027daa).
"""
import os
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
JSON_DIR = ROOT / "Brasileirão_2025"
CHAINS = ROOT / "possesion_chains_brasileirao_2025.parquet"
XG = ROOT / "xG_brasileirao_2025.parquet"
XT = ROOT / "xT_brasileirao_2025.parquet"
MODELS = ROOT / "opta_ref" / "models"
VERSION = "20260924"
PENALTY = 0.7938986307950997

OLD_COLUMNS = ["teamId", "period_value", "x", "y", "endX", "endY", "type_value", "eventId", "possesion_chain",
               "possesion_chain_team", "outcomeType_value", "type_displayName", "isTouch", "isGoal", "isShot",
               "qualifiers", "minute", "second", "game_id"]


@pytest.fixture(scope="module")
def ref():
    """The reference `opta` package from the clone, imported unmodified."""
    base = os.environ.get("PLATAFORMA_SCOUTING_DIR")
    if not base:
        pytest.skip("PLATAFORMA_SCOUTING_DIR not set: parity tests need a clone of plataforma-scouting @ c027daa")
    sys.path.insert(0, str(Path(base) / "pipelines" / "opta" / "processing"))
    # onnx_io imports skl2onnx for model export only; loading models does not use it.
    sys.modules.setdefault("skl2onnx", types.ModuleType("skl2onnx")).to_onnx = None
    from opta import carries, chains, geometry, ingest
    from opta.models import apply, onnx_io
    return types.SimpleNamespace(chains=chains, carries=carries, geometry=geometry, ingest=ingest,
                                 apply=apply, onnx_io=onnx_io)


@pytest.fixture(scope="module")
def game_ids():
    ids = sorted(pd.read_parquet(CHAINS, columns=["game_id"])["game_id"].unique())
    return [int(g) for g in ids[:: max(1, len(ids) // 5)][:5]]


@pytest.fixture(scope="module")
def ref_stage01(ref, game_ids):
    """Reference s01 order: preprocess -> isolate_chains -> prepare_chains -> add_carries -> add_model_coords,
    then apply_models' xG / chain_xg / xT steps."""
    parts = [ref.ingest.parse_game(ref.ingest.load_json(JSON_DIR / f"{g}.json"), g, "BRA1", 2025)["events"]
             for g in game_ids]
    events = ref.ingest.concat_tables({"events": parts})["events"]
    kept, _ = ref.chains.preprocess(events)
    chained = ref.chains.prepare_chains(ref.chains.isolate_chains(kept))
    ev = ref.geometry.add_model_coords(ref.carries.add_carries(chained))
    load = lambda name: ref.onnx_io.load_bundle(MODELS, name, VERSION)  # noqa: E731
    xg, xg_meta = load("xg")
    ev = ev.assign(xG=ref.apply.apply_xg(ev, xg, xg_meta["features"], float(load("penalty")[1]["valor"])))
    ev = ref.apply.add_chain_xg(ev)
    ev["xthreat"] = ref.apply.apply_xt(ev, load("xt_p")[0], load("xt_v")[0])
    ev["xt_delta_singh"] = ref.apply.apply_xt_delta_singh(ev, load("xt_s_p")[0], load("xt_s_v")[0])
    ev["xt_delta_cadeia"] = ref.apply.apply_xt_delta_cadeia(ev, ev["xthreat"], load("xt_s_p")[0], load("xt_s_v")[0])
    return chained, ev


# ---------------------------------------------------------------- chains

def test_chains_keeps_old_column_names():
    cols = pd.read_parquet(CHAINS).columns
    missing = [c for c in OLD_COLUMNS + ["chain_team_id", "shot_end", "chain_xg"] if c not in cols]
    assert not missing


def test_chains_rows_are_chain_team_and_possession_id_is_chain_plus_one():
    ch = pd.read_parquet(CHAINS)
    assert (ch["teamId"] == ch["chain_team_id"]).all()
    assert (ch["possesion_chain_team"] == ch["chain_team_id"]).all()
    assert (ch["possesion_chain"] >= 1).all()  # the main file's `possessionId != 0` filters keep every chain


def test_chains_match_reference(ref_stage01, game_ids):
    chained, _ = ref_stage01
    exp = chained[chained["is_chain_team"]]
    got = pd.read_parquet(CHAINS)
    got = got[got["game_id"].isin(game_ids)]
    assert len(got) == len(exp)
    np.testing.assert_array_equal(got["game_id"].to_numpy(), exp["game_id"].to_numpy())
    np.testing.assert_array_equal(got["event_idx"].to_numpy(), exp["event_idx"].to_numpy())
    np.testing.assert_array_equal(got["possesion_chain"].to_numpy() - 1, exp["chain_id"].to_numpy())
    np.testing.assert_array_equal(got["chain_team_id"].to_numpy(), exp["chain_team_id"].to_numpy())
    np.testing.assert_array_equal(got["shot_end"].to_numpy(), exp["shot_end"].to_numpy())


# ---------------------------------------------------------------- xG

def test_xg_parquet_columns():
    assert list(pd.read_parquet(XG).columns) == ["game_id", "teamId", "id", "xG", "Goal", "is_penalty"]


def test_penalties_get_the_constant():
    xg = pd.read_parquet(XG)
    assert xg["is_penalty"].sum() > 0
    assert (xg.loc[xg["is_penalty"], "xG"] == PENALTY).all()


def test_own_goals_have_no_xg():
    raw = pd.read_parquet(ROOT / "brasileirao_2025_events.parquet", columns=["game_id", "id", "isOwnGoal"])
    own = raw[raw["isOwnGoal"] == True]  # noqa: E712
    assert len(own) > 0
    assert not own.merge(pd.read_parquet(XG), on=["game_id", "id"]).shape[0]


def test_xg_matches_reference(ref_stage01, game_ids):
    _, ev = ref_stage01
    exp = ev[ev["xG"].notna()]
    got = pd.read_parquet(XG)
    got = got[got["game_id"].isin(game_ids)]
    np.testing.assert_array_equal(got["id"].to_numpy(), exp["id"].to_numpy())
    np.testing.assert_array_equal(got["xG"].to_numpy(), exp["xG"].to_numpy())


def test_chain_xg_matches_reference(ref_stage01, game_ids):
    chained, ev = ref_stage01
    exp = ev[~ev["is_carry"] & ev["is_chain_team"]]
    got = pd.read_parquet(CHAINS)
    got = got[got["game_id"].isin(game_ids)]
    np.testing.assert_array_equal(got["event_idx"].to_numpy(), exp["event_idx"].to_numpy())
    np.testing.assert_array_equal(got["chain_xg"].to_numpy(), exp["chain_xg"].to_numpy())


# ---------------------------------------------------------------- xT

XT_VALUES = ["xthreat", "xt_delta_singh", "xt_delta_cadeia"]


def _xt_with_types():
    xt = pd.read_parquet(XT)
    raw = pd.read_parquet(ROOT / "brasileirao_2025_events.parquet",
                          columns=["game_id", "id", "type_value", "outcomeType_value"])
    raw = raw[raw["type_value"].isin([1, 3])]  # pass / take-on ids are unique within a game
    return xt[~xt["is_carry"]].merge(raw, on=["game_id", "id"], how="left", validate="one_to_one")


def test_xt_parquet_columns():
    assert list(pd.read_parquet(XT).columns) == ["game_id", "teamId", "id", "is_carry", *XT_VALUES]


def test_failed_passes_and_take_ons_are_zero():
    xt = _xt_with_types()
    failed = xt[xt["outcomeType_value"] == 0]
    assert len(failed) > 0
    assert (failed[XT_VALUES] == 0).all().all()


def test_take_ons_are_scored():
    xt = _xt_with_types()
    done = xt[(xt["type_value"] == 3) & (xt["outcomeType_value"] == 1)]
    assert len(done) > 0
    assert done["xthreat"].notna().all() and (done["xthreat"] > 0).any()


def test_xt_matches_reference(ref_stage01, game_ids):
    _, ev = ref_stage01
    got = pd.read_parquet(XT)
    got = got[got["game_id"].isin(game_ids)]
    for is_carry in (False, True):
        exp = ev[(ev["is_carry"] == is_carry) & ev["xthreat"].notna()]
        g = got[got["is_carry"] == is_carry]
        np.testing.assert_array_equal(g["id"].to_numpy(), exp["id"].to_numpy())
        for col in XT_VALUES:
            np.testing.assert_array_equal(g[col].to_numpy(), exp[col].to_numpy(), err_msg=col)


def test_xg_step_can_be_rerun_alone():
    import subprocess
    run = subprocess.run([sys.executable, "xG_brasileirao.py"], cwd=ROOT, capture_output=True, text=True,
                         env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert run.returncode == 0, run.stderr[-500:]
    cols = pd.read_parquet(ROOT / "_ref_stage01_2025.parquet").columns
    assert "chain_xg" in cols and not {"chain_xg_x", "chain_xg_y", "xG_x", "xG_y"} & set(cols)
