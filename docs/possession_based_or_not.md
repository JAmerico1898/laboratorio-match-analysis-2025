Here's the distinction:                                                                                                      
                    
  progcarry_df — the full event stream. Every event from the match is here, including events that fall outside valid possession   chains (possessionId == 0). Use this when you need all events regardless of possession context — e.g., counting total         passes, total carries, or when the metric's logic handles possession filtering internally.                                   
                                                                                                                               
  progcarry_chains_df — a filtered view containing only events inside valid possession chains (2+ consecutive same-team
  events). Use this when the metric is inherently possession-scoped — e.g., possession-based passing sequences, build-up play
  analysis, or anything where isolated one-off events (clearances after a turnover, stray touches) would be noise.

  For xA specifically: progcarry_df is the right choice, and the code already uses it correctly. Here's why:

  1. xA checks whether a pass (type_id == 1) is immediately followed by a goal (type_id == 16) by the same team in the same
  period. This is a sequential event-pair check, not a possession-scoped aggregation.
  2. If you used progcarry_chains_df, you'd miss assists from short sequences that don't form a valid 2-event chain (e.g., a
  single pass directly from a set piece leading to a goal where the possession chain is too short to qualify).
  3. The shift(-1) logic already enforces same-team and same-period guards, which is all xA needs — it doesn't require the
  broader possession context.

  Rule of thumb: use progcarry_chains_df when computing per-possession aggregates (possession duration, build-up speed,        
  sequence length). Use progcarry_df when computing per-event features or event-pair relationships like xA.