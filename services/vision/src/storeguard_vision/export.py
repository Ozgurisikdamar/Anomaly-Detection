"""Export YOLO weights to CPU acceleration backends (P4).

Uses ultralytics' own exporter to produce an ONNX model or an OpenVINO IR, so the
same `YoloDetector` can benchmark PyTorch vs ONNX vs OpenVINO on the same CPU.
OpenVINO targets Intel CPUs specifically. Exports are cached under ``export_dir``
(gitignored) and reused. Requires the optional ``ml`` extra (ultralytics +
onnx/onnxruntime/openvino).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from storeguard_vision.benchmark import Backend


def export_model(
    base_weights: str,
    backend: Backend,
    imgsz: int = 640,
    export_dir: str = "runs/exports",
) -> Path:
    """Export ``base_weights`` for ``backend`` and return the artifact path (cached)."""
    if backend is Backend.PYTORCH:
        return Path(base_weights)

    out = Path(export_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(base_weights).stem  # e.g. "yolo26n"
    dst = out / (
        f"{stem}.onnx" if backend is Backend.ONNX else f"{stem}_openvino_model"
    )
    if dst.exists():
        return dst

    from ultralytics import YOLO

    fmt = "onnx" if backend is Backend.ONNX else "openvino"
    produced = Path(YOLO(base_weights).export(format=fmt, imgsz=imgsz))
    # ultralytics writes beside the weights; move the artifact into the cache dir.
    if produced.resolve() != dst.resolve():
        if dst.exists():
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
        shutil.move(str(produced), str(dst))
    return dst
