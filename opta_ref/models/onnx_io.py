# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/models/onnx_io.py
# Unchanged except: export-only code removed (save_model, save_bundle, save_penalty, library_versions and their
# skl2onnx/sklearn imports), since this repo only loads the trained models. Do not edit here; re-copy from the reference.
"""Exportação sklearn → ONNX e carga com onnxruntime (spec §6.2, P7; ajuste A8)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
import onnxruntime as ort


def load_predictor(path: Path, meta: dict) -> Callable[[np.ndarray], np.ndarray]:
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    iso = meta.get("calibrador_isotonico")

    def predict(X) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        if len(X) == 0:
            return np.zeros(0)
        out = session.run(None, {input_name: X})
        if not meta["classificador"]:
            return out[0].ravel().astype(np.float64)
        score = out[1][:, 1].astype(np.float64)
        if iso:
            score = np.clip(np.interp(score, iso["x"], iso["y"]), 0.0, 1.0)
        return score

    return predict


def latest_version(models_dir: Path, name: str) -> str | None:
    versions = sorted(p.stem.rsplit("_v", 1)[1] for p in Path(models_dir).glob(f"{name}_v*.json"))
    return versions[-1] if versions else None


def load_bundle(models_dir: Path, name: str, version: str):
    meta = json.loads((Path(models_dir) / f"{name}_v{version}.json").read_text(encoding="utf-8"))
    if name == "penalty":
        return None, meta
    return load_predictor(Path(models_dir) / f"{name}_v{version}.onnx", meta), meta
