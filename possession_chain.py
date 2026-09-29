#%%
# Possession chains for Brasileirão 2025, built with plataforma-scouting's reference code (opta_ref/, @ c027daa).
# Writes possesion_chains_brasileirao_2025.parquet (chain-team rows, old column names) and the intermediate
# _ref_stage01_2025.parquet (chains + carries + metre coordinates) that xG_brasileirao.py and
# xT_brasileirao.py continue from. chain_xg is added to the chains parquet by xG_brasileirao.py.

from ref_pipeline import CHAINS_PARQUET, REF_STAGE01, chains_table, reference_events, stage01

events = reference_events()
chained, ev = stage01(events)
ev.to_parquet(REF_STAGE01, index=False)

chains = chains_table(chained)
chains.to_parquet(CHAINS_PARQUET, index=False)
print(f"Saved {CHAINS_PARQUET.name}: {len(chains):,} rows, "
      f"{chains.groupby('game_id')['possesion_chain'].nunique().sum():,} chains, "
      f"{int(chains.drop_duplicates(['game_id', 'possesion_chain'])['shot_end'].sum()):,} ending in a shot")
