#%%
# xT for Brasileirão 2025 with plataforma-scouting's models and rules (opta_ref/, @ c027daa).
# Continues from _ref_stage01_2025.parquet (possession_chain.py, then xG_brasileirao.py), in game order.
# xthreat: completed pass / take-on / carry scored by xt_p x xt_v; failed pass / take-on = 0; others missing.
# xt_delta_singh = V(end) - V(start) and xt_delta_cadeia = xthreat minus the team's previous completed action in
# the chain (first one: minus V(start)), with V from the state models xt_s_p x xt_s_v.
# Writes xT_brasileirao_2025.parquet: one row per scored real event (is_carry False) plus one per reference carry
# (is_carry True), whose `id` is the id of the event the carry leads into.

import pandas as pd

from opta_ref.models.apply import apply_xt, apply_xt_delta_cadeia, apply_xt_delta_singh
from ref_pipeline import REF_STAGE01, XT_PARQUET, load_model

ev = pd.read_parquet(REF_STAGE01)
xt_p, xt_v = load_model("xt_p")[0], load_model("xt_v")[0]
xt_s_p, xt_s_v = load_model("xt_s_p")[0], load_model("xt_s_v")[0]
ev["xthreat"] = apply_xt(ev, xt_p, xt_v)
ev["xt_delta_singh"] = apply_xt_delta_singh(ev, xt_s_p, xt_s_v)
ev["xt_delta_cadeia"] = apply_xt_delta_cadeia(ev, ev["xthreat"], xt_s_p, xt_s_v)

scored = ev[ev["xthreat"].notna()]
out = scored[["game_id", "team_id", "id", "is_carry", "xthreat", "xt_delta_singh", "xt_delta_cadeia"]]
out = out.rename(columns={"team_id": "teamId"})
assert not out.duplicated(["game_id", "id", "is_carry"]).any(), "xT key (game_id, id, is_carry) is not unique"
out.to_parquet(XT_PARQUET, index=False)

print(f"Saved {XT_PARQUET.name}: {len(out):,} rows")
print(scored.groupby(ev["type_id"].map({1: "pass", 3: "take-on", 1000: "prog carry", 2000: "carry"}))
      [["xthreat", "xt_delta_cadeia"]].agg(["count", "sum"]).round(1).to_string())
