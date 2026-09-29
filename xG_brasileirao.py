#%%
# xG for Brasileirão 2025 with plataforma-scouting's model and rules (opta_ref/, @ c027daa):
# open-play shots scored by xg_v20260924, penalties = penalty_v20260924 constant, own goals (q28) get no xG.
# Continues from _ref_stage01_2025.parquet (possession_chain.py): writes xG_brasileirao_2025.parquet, adds xG and
# chain_xg to the intermediate frame and chain_xg to possesion_chains_brasileirao_2025.parquet.

import pandas as pd

from opta_ref.models.apply import add_chain_xg, apply_xg
from opta_ref.models.features import shots
from ref_pipeline import CHAINS_PARQUET, REF_STAGE01, XG_PARQUET, load_model

ev = pd.read_parquet(REF_STAGE01).drop(columns=["xG", "chain_xg"], errors="ignore")  # re-runnable on its own
xg_model, xg_meta = load_model("xg")
penalty = float(load_model("penalty")[1]["valor"])
ev = ev.assign(xG=apply_xg(ev, xg_model, xg_meta["features"], penalty))
ev = add_chain_xg(ev)
ev.to_parquet(REF_STAGE01, index=False)

s = shots(ev)  # own goals excluded
out = pd.DataFrame({"game_id": s["game_id"], "teamId": s["team_id"], "id": ev.loc[s.index, "id"],
                    "xG": ev.loc[s.index, "xG"], "Goal": s["goal"], "is_penalty": s["is_penalty"]})
out.to_parquet(XG_PARQUET, index=False)

chain_xg = ev.drop_duplicates(["game_id", "chain_id"])[["game_id", "chain_id", "chain_xg"]]
chain_xg = chain_xg.assign(possesion_chain=chain_xg["chain_id"] + 1).drop(columns="chain_id")
chains = pd.read_parquet(CHAINS_PARQUET).drop(columns="chain_xg", errors="ignore")
chains = chains.merge(chain_xg, on=["game_id", "possesion_chain"], how="left", validate="many_to_one")
chains.to_parquet(CHAINS_PARQUET, index=False)

pens = out["is_penalty"]
print(f"Saved {XG_PARQUET.name}: {len(out):,} shots ({int(pens.sum())} penalties at {penalty:.3f})")
print(f"Sum xG (all): {out['xG'].sum():.1f}  goals: {int(out['Goal'].sum())}")
print(f"Sum xG (np):  {out.loc[~pens, 'xG'].sum():.1f}  goals: {int(out.loc[~pens, 'Goal'].sum())}")
