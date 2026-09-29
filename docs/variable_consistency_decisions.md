# MatchAnalysis_PlayStyle_2025.py — variable consistency audit and decisions

Date: 2026-09-28. Branch: `align-plataforma-scouting`.
Status: implemented through commit 6181b4e (plan `docs/superpowers/plans/2026-09-28-variable-consistency.md`); effects in `docs/variable_consistency_before_after.md`.
References: Opta F24 appendices (`docs/Opta-f24_appendices.md`), plataforma-scouting `pipelines/opta/processing/opta/` (`conventions.py`, `carries.py`, `metrics/context.py`, `impl_contagem.py`, `impl_sequencia.py`, `impl_area.py`, `area.py`).

## Summary

The audit covered every variable in the file: the performance frame (#1–47) and the play-style frame (Defence 1 to Chance creation 26), plus scoring. The same concepts (loss, recovery, defensive action, zone entry, carry, touch) are defined differently from one variable to the next. They are often also different from plataforma-scouting. Four bugs change results materially: own goals credited to the wrong team, duels counted twice, a set-piece filter that never runs, and composites built from opposite styles. Thirteen decisions (D1–D13) were settled with the user. Every concept will get one shared helper, used by every variable.

## Decisions

| # | Concept | Decision | Affects |
|---|---|---|---|
| D1 | Carry / progressive | Use the reference `add_carries`: forward x gain > 5 units, same chain and team, gap ≤ 30 s, not after a failed pass, not into a defensive action or committed foul. Type 1000 is a carry that starts at x ≥ 50; type 2000 is any other carry. "Progressive" means the reference `progressive()` (length ≥ 10 units and gain ≥ 25% of the remaining distance) applied to types 1, 1000 and 2000. The local carry synthesis goes away. | carries, `progressive_pass`, `ball_progression` (fixes the type-2000 bug), ps #8, #11, #18–22 |
| D2 | Reaching a zone | One helper. A chain reaches the zone if a chain-team action has its start in it, or the end of a completed pass or a carry. Shot ends, failed-pass ends and the recovery event itself never count. The denominator is chains that start outside the zone. The 10 s variables use the same test inside the recovering team's chain. Final third is x ≥ 66.67; the box is x ≥ 83 and 21.1 ≤ y ≤ 78.9. | #6, #7, #14, #15, #21, #22, #29, #30, #33; ps #9, #10, #13, #14, #19–22 |
| D3 | Loss | Reference: (1,0), (3,0), (50,1), (51,1), (61,0), and the next event belongs to the opponent. No set-piece qualifier filter. #9 is renamed "Turnovers in own defensive 40%" and keeps x ≤ 40. | #9–13; ps #6–8, #11, #17 |
| D4 | Recovery | Reference: 8, (7,1), 49, with the next event by the same team. Consecutive recovery events count as one regain. No GK claims, no aerials. High recoveries % stays at x ≥ 66.67. | #11, #13–24; ps #2, #7, #9–14, #23, #24 |
| D5 | Defensive actions | Intensity: 7, 8, 44, 45, 49 and committed fouls (ref #35). Height: 7, 8, 12, 49 and committed fouls, excluding set-piece chains (ref `area.py`). Time to defensive action: the intensity set. PPDA denominator: 7, 8, 45 and committed fouls. | #1, #2, #4, #12; ps #1, #3, #5, #6 |
| D6 | Counter-press | Losses regained within 5 s ÷ losses, counting each loss once. One metric shared by both frames. | #11, ps #7 |
| D7 | Field tilt | Share of final-third (x ≥ 66.67) open-play touches between the two teams, using the reference `possession_touch`. Delete the duplicate #40 and keep the numbering. | #26, #40 |
| D8 | Long ball % | q1 passes ÷ all attempted passes. Excludes q5, q6 and q107. Goal kicks stay in. | #27, ps #16 |
| D9 | Box touches | Reference `possession_touch` inside the box. | #32 |
| D10 | Ball in play | Renamed "In-possession ball-in-play minutes" (the team's own chain time). The docstring is rewritten to match; it notes that time between chains is not counted. Removed from composites because it duplicates possession. | #39 |
| D11 | Missing values | No events in a count or sum gives 0. A ratio, height or time with no denominator gives NaN. Both global `fillna(0)` calls go (lines 4696 and 8605). Z-scores use `nan_policy="omit"` and composites skip NaN. | scoring |
| D12 | Play-style composites | Style axes toward a named behaviour pole, not "higher = better". Poles describe behaviours, so one pole can fit several styles. The performance frame keeps "higher = better". | ps scoring |
| D13 | Poles | See the table below. Transition vulnerability and the opponent's final-third and box entries within 10 s leave the play-style composites but stay as columns. Attacking splits into two composites (6 in total). | ps scoring |

### D13 poles (+ pushes toward the pole, − pushes away)

| Composite | Pole | + | − |
|---|---|---|---|
| Defence | Aggressive / high block | height, high recoveries %, fouls in attacking half %, intensity | PPDA |
| Defensive transition | Immediate counter-press | counter-press success % | time to defensive action |
| Attacking transition | Vertical / fast transition | first pass forward %, FT entries 10 s %, box entries 10 s % | time to progression, possessions retained 5 s % |
| Directness | Directness | long ball %, progressive passes from middle third % | buildup from goal kick % |
| Wide / crossing | Wide / crossing (vs carrying) | crosses per FT entry, box entries from crosses % | dribbles per FT entry, box entries from carries % |
| Chance creation | Early / direct shooting | direct attack %, shots per FT pass, shots outside box % | sustained attack % |

## Bugs fixed without a decision

| # | Where | Bug | Fix |
|---|---|---|---|
| B1 | #34, #37, #38, #45–47; ps #25, #26 | Own goals (q28, logged on the conceding team) count as the conceding team's goals and shots. Example: game 1955760 is output as 3–1 when the real score was 4–0. | Exclude q28 from shots, xG and np_goals. Credit own goals to the opponent's goals. |
| B2 | #3 | Challenge (45) and the opponent's take-on are the same duel; so are a tackle and a failed take-on. Each is counted twice (3,931 of 3,931). | Reference `ground_duels`: won = 7, lost = 45. |
| B3 | `has_qualifier` | Qualifiers arriving as `numpy.ndarray` are ignored, so every chains-parquet set-piece filter does nothing (0 of 10,383 throw-ins caught). | Handle any iterable. |
| B4 | #8 | The docstring promises "per 100 passes"; the raw sum is used. | Normalise per 100 opponent passes in the zone (ref #55). |
| B5 | ps #23, #24 | Possession start is anchored to the last recovery (median 42 s before the shot); H2 fallback times are about 2,700 s. | Use chain duration and pass count. Exclude q9, q28 and set-piece shots. |
| B6 | ps #5 | The comment says intensity is possession-adjusted, but it isn't. | Apply the same adjustment as the performance frame. |
| B7 | ps #11, #19, #20 | `[1, 2000]` leaves out progressive carries (1000). | Covered by D1 (use 1000 and 2000). |
| B8 | Scoring | `iloc[:, :10]` means possession is never z-scored, so the `Posse (%)` rename does nothing. | **Withdrawn**: the app reads raw possession (see Consumer constraint). Only the dead `possession_z` / `opponent_possession_z` rename entries are removed. |
| B9 | `performance_metrics_2` | Averages raw metrics with mixed units and no sign flips. | Build from z-scores or remove. |
| B10 | Duplicates | PPDA, intensity, height and the 10 s entries are each implemented twice. | One function per concept, called by both frames. |
| B11 | Carries | Synthetic carries copy `outcome` from the next event (16.6% end up as 0). | Covered by D1 (the reference sets outcome 1). |
| B12 | Comments and labels | Stale `possessionId == 0` and MIN_CHAIN_LEN notes, "per-period seconds", "Smother not present". Ratios are labelled "(%)" and `_z` columns carry units. | Correct them. |

## Consumer constraint (found while planning)

The web app `D:\jose_americo\laboratorio-match-analysis` (`scripts/compile-data.ts`) reads `performance_team.csv`, `performance_round.csv`, `performance_metrics.csv` and `play_style_metrics.csv`. It finds columns by their current English names and Portuguese labels, and it reads the **raw** `possession` / `opponent_possession` columns. (The `streamlit_app/` folder is discontinued.) As a result:
- No column name or Portuguese label in those four CSVs changes. The D3 and D10 renames apply only to docstrings and comments.
- **B8 is withdrawn.** Possession stays unscaled on purpose, because the app shows it as context.
- The D13 composites live in `play_style_team.csv` / `play_style_round.csv`, which the app does not read, so they can change freely.

## Unchanged (checked, OK)

- Possession % (#25), which matches the reference `possession()`.
- xT credit (#31: `xt_delta_cadeia`, set pieces excluded).
- np_xG (#36).
- Box bounds.
- Home/away attribution.
- The foul outcome convention (0 = committed), applied consistently.
- The goal kick qualifier q124.
- Crosses exclude q5, q6 and q107.
- Per-club and per-round z-score frames (intentional).
