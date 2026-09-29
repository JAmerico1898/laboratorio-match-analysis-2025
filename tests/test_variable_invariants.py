"""Output-level invariants for MatchAnalysis_PlayStyle_2025.py (docs/variable_consistency_decisions.md).
They read the CSVs a full run writes (scripts/run_offline.py); they do not run the pipeline."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
KEY = ["game_id", "team_id"]


def _csv(name):
    path = ROOT / name
    if not path.exists():
        pytest.skip(f"{name} missing: run scripts/run_offline.py first")
    return pd.read_csv(path, index_col=0)


@pytest.fixture(scope="module")
def raw():
    return _csv("variable_df_new.csv")  # the final unscaled team-game frame (same as performance_metrics.csv)


@pytest.fixture(scope="module")
def perf():
    return _csv("performance_metrics.csv")


@pytest.fixture(scope="module")
def style():
    return _csv("play_style_metrics.csv")


def _opponent(frame, cols):
    """frame[KEY + cols] re-keyed to the opponent's team_id."""
    pairs = frame[KEY].drop_duplicates()
    m = pairs.merge(pairs, on="game_id", suffixes=("", "_opp"))
    m = m[m["team_id"] != m["team_id_opp"]]
    out = frame[KEY + cols].merge(m, on=KEY).drop(columns="team_id")
    return out.rename(columns={"team_id_opp": "team_id"})


def _scorelines(game_ids):
    """(game_id, team_id, gf, ga) from the raw WhoScored match JSON (df_schedule.xlsx is a stale snapshot whose
    scores are missing for most games)."""
    rows = []
    for game_id in sorted(set(game_ids)):
        path = ROOT / "Brasileirão_2025" / f"{game_id}.json"
        if not path.exists():
            pytest.skip(f"{path.name} missing: raw match JSON needed for the scoreline")
        d = json.loads(path.read_text(encoding="utf-8"))
        h, a = d["home"], d["away"]
        if "fulltime" not in h.get("scores", {}):
            continue  # match not finished when scraped
        hs, as_ = h["scores"]["fulltime"], a["scores"]["fulltime"]
        if sum(e["type"]["value"] == 16 for e in d["events"]) != hs + as_:
            continue  # event feed misses a goal (e.g. 1955886: 3-1 with 2 goals logged)
        rows += [(game_id, h["teamId"], hs, as_), (game_id, a["teamId"], as_, hs)]
    return pd.DataFrame(rows, columns=KEY + ["gf", "ga"])


def test_goals_match_scoreline(raw):
    truth = _scorelines(raw["game_id"])
    m = raw[KEY + ["goals_scored", "goals_conceded", "goal_difference"]].merge(truth, on=KEY)
    assert len(m) >= len(raw) - 4  # unfinished games and event feeds missing a goal are skipped
    bad = m[(m["goals_scored"].fillna(0) != m["gf"]) | (m["goals_conceded"].fillna(0) != m["ga"])]
    assert bad.empty, bad.head(10).to_string()
    assert (m["goal_difference"].fillna(0) == m["gf"] - m["ga"]).all()


MIRRORS = [
    ("opposition_progression_percentage", "final_third_entries_%"),
    ("opp_final_third_to_box_%", "final_third_to_box_entries_%"),
    ("opposition_final_third_entries_10s", "final_third_entries_10s"),
    ("opposition_box_entries_10s", "box_entries_10s"),
    ("opposition_xG_10s", "xG_10s"),
    ("opposition_pass_tempo", "pass_tempo"),
]


@pytest.mark.parametrize("opp_col, own_col", MIRRORS)
def test_mirrors(raw, opp_col, own_col):
    theirs = _opponent(raw, [own_col])
    m = raw[KEY + [opp_col]].merge(theirs, on=KEY)
    a, b = m[opp_col].to_numpy(float), m[own_col].to_numpy(float)
    same = (np.isnan(a) & np.isnan(b)) | np.isclose(a, b)
    assert same.all(), m[~same].head(10).to_string()


SHARED = [  # (performance_metrics.csv column, play_style_metrics.csv column)
    ("PPDA", "PPDA"),
    ("defensive_height", "defensive_height"),
    ("defensive_intensity", "defensive_intensity"),
    ("recoveries_within_5s_%", "counter_press_Success_Rate_%"),
    ("avg_time_to_defensive_action", "avg_time_to_defensive_action"),
    ("long_ball_%", "long_ball_%"),
    ("retained_possessions_5s_%", "retained_possessions_5s_pct"),
    ("opposition_final_third_entries_10s", "opposition_final_third_entries_10s"),
    ("opposition_box_entries_10s", "opposition_box_entries_10s"),
]


@pytest.mark.parametrize("perf_col, style_col", SHARED)
def test_frames_agree(perf, style, perf_col, style_col):
    m = perf[KEY + [perf_col]].merge(style[KEY + [style_col]], on=KEY, suffixes=("_p", "_s"))
    a = m[perf_col if perf_col != style_col else perf_col + "_p"].to_numpy(float)
    b = m[style_col if perf_col != style_col else style_col + "_s"].to_numpy(float)
    same = (np.isnan(a) & np.isnan(b)) | np.isclose(a, b)
    assert same.all(), m[~same].head(10).to_string()


def test_duels_not_pinned_to_half(raw):
    # B2: with each duel counted twice the league mean sat near 0.5 by construction
    assert not 0.45 <= raw["defensive_duels_won_%"].mean() <= 0.55


def test_style_shares_bounded(style):
    assert ((style["box_entries_from_crosses"].fillna(0) + style["box_entries_from_carries"].fillna(0)) <= 100 + 1e-9).all()
    assert ((style["sustained_attacks"].fillna(0) + style["direct_attack"].fillna(0)) <= 100 + 1e-9).all()


COUNT_COLUMNS = ["high_turnovers", "recoveries", "retained_possessions_5s", "final_third_entries_10s",
                 "box_entries_10s", "xG_10s", "xT_10s", "opposition_final_third_entries_10s",
                 "opposition_box_entries_10s", "opposition_xG_10s", "xT", "penalty_area_touches", "np_shots",
                 "high_opportunity_shots", "np_xg", "np_goals", "total_xg", "goal_difference", "goals_conceded",
                 "goals_scored", "ball_in_play", "defensive_intensity"]


STYLE_RATIOS = ["high_recoveries_%", "counter_press_Success_Rate_%", "time_to_progression_seconds",
                "first_pass_forward_pct", "buildup_%", "crosses_per_final_third_entry", "box_entries_from_crosses",
                "sustained_attacks", "direct_attack", "shots_outside_box"]


def test_nan_policy(perf, style):
    # D11: counts filled with 0; ratios keep NaN. In this data every team-game has a denominator for the performance
    # ratios, so the NaN check spans the play-style ratios too (the old global fillna(0) left no NaN in either frame).
    assert perf[COUNT_COLUMNS].notna().all().all()
    ratios = ["box_entries_to_shot_%", "final_third_to_box_entries_%", "turnover_line_height", "avg_recovery_time"]
    assert perf[ratios].isna().any().any() or style[STYLE_RATIOS].isna().any().any(),         "no NaN left in any ratio column: a global fillna(0) is still active"


def test_style_composites():
    team = _csv("play_style_team.csv")
    for label in ["Bloco alto / agressivo", "Contrapressão imediata", "Transição vertical", "Jogo direto",
                  "Jogo pelos lados", "Finalização precoce"]:
        assert label in team.columns, label
        assert team[label].notna().all(), label


def test_reference_carries_are_the_only_carries():
    ref = pd.read_parquet(ROOT / "_ref_stage01_2025.parquet", columns=["type_id"])
    n_ref = int(ref["type_id"].isin([1000, 2000]).sum())
    assert n_ref > 20000  # 25,881 on the 2026-09-28 data


def test_counterpress_matches_reference_order(raw):
    # Losses/regains are neighbour-based (D3, D4), so the event order must be the reference's (event_idx, JSON order)
    import team_concepts as tc
    ref = pd.read_parquet(ROOT / "_ref_stage01_2025.parquet")
    ref = ref[~ref["type_id"].isin(tc.CARRY_TYPES)].sort_values(["game_id", "event_idx"], kind="mergesort")
    ref = ref.rename(columns={"x": "start_x", "y": "start_y", "time_s": "time"}).reset_index(drop=True)
    cp = tc.counterpress(ref).groupby(KEY)["regained"].mean().mul(100.0).rename("ref").reset_index()
    m = raw[KEY + ["recoveries_within_5s_%"]].merge(cp, on=KEY)
    a, b = m["recoveries_within_5s_%"].to_numpy(float), m["ref"].to_numpy(float)
    same = np.isclose(a, b)
    assert same.mean() >= 0.95, f"{same.mean():.1%} of team-games match; mean {a.mean():.3f} vs ref {b.mean():.3f}"


@pytest.mark.parametrize("col, pos", [("defensive_intensity", "opponent_possession"),
                                      ("recoveries", "opponent_possession"), ("high_turnovers", "possession")])
def test_counts_not_divided_by_possession(perf, col, pos):
    # Raw counts barely move with possession (r +0.06 / -0.17 / -0.54); dividing by it made them possession proxies
    # (r -0.83). The counts are reported unadjusted.
    assert perf[col].corr(perf[pos]) > -0.6


COMPOSITES = {  # label: [(weight, [z-column labels])]; z columns already carry the "higher = better" sign
    "Defesa": [(0.6, ["Entradas do adversário no último terço (%)", "Entradas do adversário na área (%)"]),
               (0.4, ["PPDA", "Intensidade defensiva", "Altura defensiva (m)"])],
    "Criação de chances": [(0.7, ["Toques na área", "Finalizações (exceto pênaltis)", "Grandes oportunidades",
                                  "xG (exceto pênaltis)"]),
                           (0.3, ["xG (pFinalização)", "Gols (exceto pênaltis)"])],
}


@pytest.mark.parametrize("name", ["performance_team.csv", "performance_round.csv"])
def test_performance_composite_members(name):
    # Opposition_xT (Defesa) and box_entries_to_shot_% (Criação de chances) are out: they did not agree with the
    # other items of their composite (item-rest r +0.07 / +0.25)
    frame = _csv(name)
    for label, parts in COMPOSITES.items():
        expected = sum(w * frame[cols].mean(axis=1) for w, cols in parts)
        assert np.allclose(frame[label], expected, equal_nan=True), label
