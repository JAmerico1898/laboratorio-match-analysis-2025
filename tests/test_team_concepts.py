import numpy as np
import pandas as pd
import pytest

import team_concepts as tc

BASE = dict(game_id=1, period_id=1, team_id=10, type_id=1, outcome=1, start_x=50.0, start_y=50.0, end_x=55.0,
            end_y=50.0, time=0.0, chain_id=0.0, is_chain_team=True, chain_first=False, chain_last=False)


def frame(*rows):
    out = pd.DataFrame([{**BASE, **r} for r in rows])
    for q in tc.QUALIFIER_FLAGS:
        out[f"q{q}"] = out.get(f"q{q}", False)
        out[f"q{q}"] = out[f"q{q}"].fillna(False).astype(bool)
    return out


# qualifiers -------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("q, expected", [
    ({56: "Back", 6: None}, {56, 6}),                                      # socceraction loader: dict keyed by id
    ([{"type": {"displayName": "CornerTaken", "value": 6}}], {6}),        # raw WhoScored JSON: list of dicts
    (np.array([{"type": {"value": 107}}], dtype=object), {107}),          # chains parquet: ndarray of dicts (B3)
    (None, set()),
    (float("nan"), set()),
])
def test_qualifier_ids(q, expected):
    assert tc.qualifier_ids(q) == expected


def test_add_qualifier_flags():
    f = pd.DataFrame({"qualifiers": [{9: None}, None, [{"type": {"value": 28}}]]})
    out = tc.add_qualifier_flags(f, ids=(9, 28))
    assert out["q9"].tolist() == [True, False, False]
    assert out["q28"].tolist() == [False, False, True]


# zones, progressive, touches --------------------------------------------------------------------------------------
def test_zones():
    assert tc.in_box(pd.Series([83.0, 82.9, 90.0]), pd.Series([50.0, 50.0, 80.0])).tolist() == [True, False, False]
    assert tc.in_final_third(pd.Series([66.67, 66.6])).tolist() == [True, False]


def test_progressive_reference_rule():
    f = frame(dict(start_x=50, end_x=62.5),   # length 12.5, gain 12.5/50 = 25%  -> progressive
              dict(start_x=50, end_x=59),     # length 9 < 10                    -> not
              dict(start_x=90, end_x=93, start_y=40, end_y=50))  # length 10.4, gain 3/10 = 30% -> progressive
    assert tc.progressive(f).tolist() == [True, False, True]


def test_possession_touch_excludes_restarts_penalties_own_goals():
    f = frame(dict(type_id=1), dict(type_id=1, q6=True), dict(type_id=13, q9=True), dict(type_id=16, q28=True),
              dict(type_id=2000), dict(type_id=7))
    assert tc.possession_touch(f).tolist() == [True, False, False, False, True, False]


def test_npxg_shots():
    f = frame(dict(type_id=13), dict(type_id=16, q9=True), dict(type_id=16, q28=True), dict(type_id=1))
    assert tc.npxg_shots(f).tolist() == [True, False, False, False]


# defensive sets ---------------------------------------------------------------------------------------------------
def test_defensive_sets():
    f = frame(*[dict(type_id=t) for t in (7, 8, 12, 44, 45, 49)], dict(type_id=4, outcome=0), dict(type_id=4, outcome=1))
    assert tc.intensity_mask(f).tolist() == [True, True, False, True, True, True, True, False]
    assert tc.height_mask(f).tolist() == [True, True, True, False, False, True, True, False]
    assert tc.ppda_action_mask(f).tolist() == [True, True, False, False, True, False, True, False]
    won, lost = tc.ground_duels(f)
    assert won.sum() == 1 and lost.sum() == 1


def test_set_piece_chain_rows():
    f = frame(dict(chain_id=0, q6=True), dict(chain_id=0), dict(chain_id=1), dict(chain_id=1))
    assert tc.set_piece_chain_rows(f).tolist() == [True, True, False, False]


# losses, recoveries -----------------------------------------------------------------------------------------------
def test_loss_needs_chain_last_and_opponent_next():
    f = frame(dict(type_id=1, outcome=0, chain_last=True, team_id=10),   # failed pass, opponent next -> loss
              dict(type_id=49, team_id=20),
              dict(type_id=61, outcome=1, chain_last=True, team_id=20),  # 61/1 is not a loss type
              dict(type_id=1, team_id=10, chain_last=True),
              dict(type_id=1, outcome=0, chain_last=True, team_id=10),   # next event same team -> not a loss
              dict(type_id=1, team_id=10))
    assert tc.loss_mask(f).tolist() == [True, False, False, False, False, False]


def test_possession_won_dedups_consecutive_recoveries():
    f = frame(dict(type_id=1, team_id=20),
              dict(type_id=8, team_id=10),        # interception, next own event -> regain
              dict(type_id=49, team_id=10),       # ball recovery right after own interception -> same regain
              dict(type_id=1, team_id=10),
              dict(type_id=7, outcome=1, team_id=10),  # tackle won, next event opponent -> not a regain
              dict(type_id=1, team_id=20))
    assert tc.possession_won_mask(f).tolist() == [False, True, False, False, False, False]


def test_next_event_stops_at_period_boundary():
    f = frame(dict(type_id=1, time=10), dict(type_id=2, time=12, team_id=20),
              dict(type_id=49, time=15), dict(type_id=49, period_id=2, time=2700))
    out = tc.next_event(f, f["type_id"] == 1, f["type_id"] == 49)
    assert out["to_pos"].tolist() == [2] and out["seconds"].tolist() == [5.0]
    out2 = tc.next_event(f, f.index == 2, f["type_id"] == 49)
    assert np.isnan(out2["to_pos"].iloc[0]) and np.isnan(out2["seconds"].iloc[0])


def test_counterpress_per_loss():
    f = frame(dict(type_id=1, outcome=0, chain_last=True, time=0),
              dict(type_id=1, team_id=20, time=2),
              dict(type_id=8, time=4),                    # regained 4 s after the loss
              dict(type_id=1, time=5),
              dict(type_id=1, outcome=0, chain_last=True, time=20),
              dict(type_id=1, team_id=20, time=21),
              dict(type_id=49, time=30), dict(type_id=1, time=31))  # 10 s later -> not within 5 s
    cp = tc.counterpress(f)
    assert cp["regained"].tolist() == [True, False]


# chains and windows -----------------------------------------------------------------------------------------------
def test_zone_hits_ignore_failed_pass_and_shot_ends():
    f = frame(dict(start_x=60, end_x=70, outcome=1),          # completed pass ending in the third -> hit
              dict(start_x=60, end_x=70, outcome=0),          # failed pass ending there -> no
              dict(type_id=13, start_x=60, end_x=100),        # shot: its end never counts
              dict(type_id=2000, start_x=60, end_x=67),       # carry into the third -> hit
              dict(type_id=7, start_x=70, end_x=70))          # any action located in the third -> hit
    assert tc.zone_hits(f, "third").tolist() == [True, False, False, True, True]


def test_chain_table():
    f = frame(dict(chain_id=0, start_x=30, end_x=40), dict(chain_id=0, start_x=40, end_x=70),
              dict(chain_id=0, type_id=13, start_x=85, start_y=50),
              dict(chain_id=1, team_id=20, start_x=70, end_x=75),
              dict(chain_id=1, team_id=10, is_chain_team=False, start_x=90))  # non-chain-team row ignored
    t = tc.chain_table(f).set_index("chain_id")
    assert t.loc[0, ["starts_in_third", "reaches_third", "reaches_box", "has_shot"]].tolist() == [False, True, True, True]
    assert t.loc[1, ["team_id", "starts_in_third", "reaches_box"]].tolist() == [20, True, False]
    assert tc.chain_table(f.iloc[:0]).empty


def test_after_regain_stops_at_period_and_loss():
    f = frame(dict(type_id=49, time=0),                                   # regain
              dict(type_id=1, time=3, start_x=70),                        # in window
              dict(type_id=1, outcome=0, chain_last=True, time=5),        # the team's next loss
              dict(type_id=1, time=6, start_x=80),                        # after the loss -> excluded
              dict(type_id=1, time=20),                                   # outside 10 s anyway
              dict(type_id=1, period_id=2, time=2701))                    # other period
    regain = pd.Series([True, False, False, False, False, False])
    loss = pd.Series([False, False, True, False, False, False])
    rows = tc.after_regain(f, regain, loss)
    assert rows.index.tolist() == [1]
    assert rows["reg_idx"].tolist() == [0]
    assert tc.after_regain(f, regain & False, loss).empty


def test_to_opponent_and_goal_team():
    pairs = pd.DataFrame({"game_id": [1, 1], "team_id": [10, 20]})
    t = pd.DataFrame({"game_id": [1, 1], "team_id": [10, 20], "v": [3, 7]})
    assert tc.to_opponent(t, pairs).sort_values("team_id")["v"].tolist() == [7, 3]
    f = frame(dict(type_id=16, team_id=10), dict(type_id=16, team_id=10, q28=True))
    assert tc.goal_team(f, pairs).tolist() == [10, 20]


def test_after_regain_keeps_nullable_game_id():
    # the orchestrator casts game_id to pandas Int64 before the variables are built
    f = frame(dict(type_id=49, time=0), dict(type_id=1, time=3))
    f["game_id"] = f["game_id"].astype("Int64")
    rows = tc.after_regain(f, pd.Series([True, False]), pd.Series([False, False]))
    assert rows.index.tolist() == [1]


def test_after_regain_stays_in_the_recovering_chain():
    # D2: the 10 s window is read inside the recovering team's chain (the chain of its first post-regain row)
    f = frame(dict(type_id=49, time=0, chain_id=0),
              dict(type_id=1, time=2, chain_id=1),
              dict(type_id=1, time=4, chain_id=1),
              dict(type_id=1, time=6, chain_id=2))   # new chain (e.g. a corner after a blocked shot) -> excluded
    rows = tc.after_regain(f, pd.Series([True, False, False, False]), pd.Series([False] * 4))
    assert rows.index.tolist() == [1, 2]
