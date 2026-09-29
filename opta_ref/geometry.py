# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/geometry.py
# Unchanged except imports (opta. -> opta_ref.). Do not edit here; re-copy from the reference.
"""Coordenadas em metros para modelos e métricas (spec §5.4; B3.1 passo 4; ajuste A9)."""
from __future__ import annotations

import pandas as pd

from opta_ref.conventions import SHOT_TYPES, TAKE_ON

X_METRES = 1.05
Y_METRES = 0.68


def add_model_coords(ev: pd.DataFrame) -> pd.DataFrame:
    x0 = ev["x"] * X_METRES
    c0 = (50 - ev["y"]).abs() * Y_METRES
    shot = ev["type_id"].isin(SHOT_TYPES)
    take_on = ev["type_id"] == TAKE_ON
    x1 = (ev["end_x"] * X_METRES).mask(shot, 105.0).mask(take_on, x0)
    c1 = ((50 - ev["end_y"]).abs() * Y_METRES).mask(shot, 0.0).mask(take_on, c0)
    return ev.assign(x0=x0, c0=c0, x1=x1, c1=c1)
