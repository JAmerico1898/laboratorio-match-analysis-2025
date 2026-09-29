# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/models/apply.py
# Unchanged except imports (opta. -> opta_ref.). Do not edit here; re-copy from the reference.
"""Aplicação de xG, xA, xT e chain_xg por execução (spec §4.4; ajustes A7, A10)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from opta_ref.chains import CHAIN_KEY, chain_table, propagate_to_foul_chains
from opta_ref.conventions import PASS, TAKE_ON
from opta_ref.models.features import XA_FEATURES, XT_FEATURES, XT_STATE_FEATURES, passes_for_xa, shots, xt_actions
from opta_ref.models.onnx_io import latest_version, load_bundle

MODEL_NAMES = ("xg", "penalty", "xa_p", "xa_v", "xt_p", "xt_v", "xt_s_p", "xt_s_v")  # xt_s_*: estado, gate "xt"
Predict = Callable[[np.ndarray], np.ndarray]


@dataclass
class Predictors:
    xg: Predict
    xg_features: list[str]
    penalty: float
    xa_p: Predict
    xa_v: Predict
    xt_p: Predict
    xt_v: Predict
    xt_s_p: Predict
    xt_s_v: Predict
    versions: dict[str, str]


def resolve_versions(models_dir: Path, gates: dict) -> dict[str, str]:
    approved = ((gates or {}).get("M") or {}).get("modelos") or {}
    out = {}
    for name in MODEL_NAMES:
        chosen = approved.get(name.split("_")[0]) or latest_version(models_dir, name)
        if chosen is None:
            raise FileNotFoundError(f"modelo {name} ausente em {models_dir}: rode --stage 02")
        out[name] = str(chosen)
    return out


def load_predictors(models_dir: Path, versions: dict[str, str]) -> Predictors:
    xg, xg_meta = load_bundle(models_dir, "xg", versions["xg"])
    _, penalty = load_bundle(models_dir, "penalty", versions["penalty"])
    names = ("xa_p", "xa_v", "xt_p", "xt_v", "xt_s_p", "xt_s_v")
    loaded = {name: load_bundle(models_dir, name, versions[name])[0] for name in names}
    return Predictors(xg, xg_meta["features"], float(penalty["valor"]), loaded["xa_p"], loaded["xa_v"],
                      loaded["xt_p"], loaded["xt_v"], loaded["xt_s_p"], loaded["xt_s_v"], versions)


def apply_xg(ev: pd.DataFrame, predict: Predict, features: list[str], penalty: float) -> pd.Series:
    xg = pd.Series(np.nan, index=ev.index)
    s = shots(ev)
    open_play = s[~s["is_penalty"]]
    xg.loc[open_play.index] = predict(open_play[features].to_numpy())
    xg.loc[s.index[s["is_penalty"].to_numpy()]] = penalty
    return xg


def add_chain_xg(ev: pd.DataFrame) -> pd.DataFrame:
    table = chain_table(ev)
    uid_xg = ev.set_index("event_uid")["xG"]
    shot_xg = uid_xg.reindex(table["last_uid"].astype("int64")).to_numpy()
    values = np.where(table["last_is_shot"].to_numpy(), np.nan_to_num(shot_xg), 0.0)
    table["chain_xg"] = propagate_to_foul_chains(table, values)
    return ev.merge(table[CHAIN_KEY + ["chain_xg"]], on=CHAIN_KEY, how="left", validate="many_to_one")


def apply_xa(ev: pd.DataFrame, p: Predict, v: Predict) -> pd.Series:
    xa = pd.Series(np.nan, index=ev.index)
    passes = ev[(ev["type_id"] == PASS) & ~ev["is_carry"]]
    done = passes_for_xa(ev)
    X = done[XA_FEATURES].to_numpy()
    values = pd.Series(p(X) * np.clip(v(X), 0, None), index=done["event_uid"].to_numpy())
    xa.loc[passes.index] = passes["event_uid"].map(values).fillna(0.0).to_numpy()
    return xa


def apply_xt(ev: pd.DataFrame, p: Predict, v: Predict) -> pd.Series:
    """xT das ações completadas; passe e drible falhados valem 0; demais eventos NaN (auditoria B3)."""
    xt = pd.Series(np.nan, index=ev.index)
    xt.loc[ev["type_id"].isin((PASS, TAKE_ON)) & (ev["outcome"] == 0)] = 0.0
    actions = xt_actions(ev)
    X = actions[XT_FEATURES].to_numpy()
    xt.loc[actions.index] = p(X) * np.clip(v(X), 0, None)
    return xt


def _state_value(p: Predict, v: Predict, X: np.ndarray) -> np.ndarray:
    return p(X) * np.clip(v(X), 0, None)


def _failed_zero(ev: pd.DataFrame) -> pd.Series:
    out = pd.Series(np.nan, index=ev.index)
    out.loc[ev["type_id"].isin((PASS, TAKE_ON)) & (ev["outcome"] == 0)] = 0.0
    return out


def apply_xt_delta_singh(ev: pd.DataFrame, p: Predict, v: Predict) -> pd.Series:
    """Variação de xT de Karun Singh: V(fim) − V(início), com V do modelo de estado. Passe e drible falhados
    valem 0; demais eventos NaN (auditoria xT, 24/09)."""
    delta = _failed_zero(ev)
    actions = xt_actions(ev)
    end = _state_value(p, v, actions[["x1", "c1"]].to_numpy())
    delta.loc[actions.index] = end - _state_value(p, v, actions[XT_STATE_FEATURES].to_numpy())
    return delta


def apply_xt_delta_cadeia(ev: pd.DataFrame, xthreat: pd.Series, p: Predict, v: Predict) -> pd.Series:
    """Variação de xT na cadeia: xT(ação) − xT da ação completada anterior do mesmo time na mesma cadeia; a
    primeira do time na cadeia desconta V(início). `ev` na ordem do jogo. Passe e drible falhados valem 0 e não
    servem de anterior; demais eventos NaN (auditoria xT, 24/09)."""
    delta = _failed_zero(ev)
    actions = xt_actions(ev)
    value = xthreat.loc[actions.index]
    keys = [ev.loc[actions.index, c] for c in ("game_id", "chain_id", "team_id")]
    prev = value.groupby(keys, sort=False).shift(1)
    start = pd.Series(_state_value(p, v, actions[XT_STATE_FEATURES].to_numpy()), index=actions.index)
    delta.loc[actions.index] = value - prev.fillna(start)
    return delta


def apply_models(ev: pd.DataFrame, pred: Predictors) -> pd.DataFrame:
    ev = ev.assign(xG=apply_xg(ev, pred.xg, pred.xg_features, pred.penalty))
    ev = add_chain_xg(ev)
    ev["xA"] = apply_xa(ev, pred.xa_p, pred.xa_v)
    ev["xthreat"] = apply_xt(ev, pred.xt_p, pred.xt_v)
    ev["xt_delta_singh"] = apply_xt_delta_singh(ev, pred.xt_s_p, pred.xt_s_v)
    ev["xt_delta_cadeia"] = apply_xt_delta_cadeia(ev, ev["xthreat"], pred.xt_s_p, pred.xt_s_v)
    return ev
