"""CPU benchmark harness (Phase 1 — implemented).

Measures, on the real machine, a detector candidate over a frame source:
per-frame inference latency (p50/p95), single-stream FPS, process CPU% and peak
RSS. Precision/recall and tracking ID-switch counts require a labelled eval set
and are left as ``None`` with an explanatory note (never invented).

Model execution requires the optional ``ml`` extra (ultralytics/opencv/psutil).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum


class ModelCandidate(StrEnum):
    YOLO26N = "yolo26n"
    YOLO11N = "yolo11n"


class Backend(StrEnum):
    """Inference runtime the model is benchmarked on (P4)."""

    PYTORCH = "pytorch"  # the .pt weights via ultralytics/torch
    ONNX = "onnx"  # ultralytics ONNX export + onnxruntime
    OPENVINO = "openvino"  # ultralytics OpenVINO export (Intel CPU)


class Tracker(StrEnum):
    BYTETRACK = "bytetrack"  # efficient fixed-camera baseline
    BOTSORT = "botsort"
    TRACKTRACK = "tracktrack"


# Candidate -> base ultralytics weights file (downloaded on first use / on disk).
_WEIGHTS = {
    ModelCandidate.YOLO26N: "yolo26n.pt",
    ModelCandidate.YOLO11N: "yolo11n.pt",
}


@dataclass(frozen=True)
class BenchmarkConfig:
    """Inputs for a single benchmark run."""

    model: ModelCandidate
    backend: Backend = Backend.PYTORCH
    tracker: Tracker = Tracker.BYTETRACK
    input_size: int = 640
    clip_path: str | None = None
    frame_sample_stride: int = 1
    device: str = "cpu"
    frames: int = 60
    warmup: int = 5
    trials: int = 1
    conf: float = 0.25
    export_dir: str = "runs/exports"


@dataclass
class BenchmarkResult:
    """Measured outputs. Quality fields stay None without a labelled eval set."""

    model: ModelCandidate
    tracker: Tracker
    backend: Backend = Backend.PYTORCH
    device: str = "cpu"
    input_size: int = 640
    frames: int = 0
    trials: int = 1
    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    latency_mean_ms: float | None = None
    fps: float | None = None
    frame_age_p95_ms: float | None = None
    precision: float | None = None
    recall: float | None = None
    id_switches: int | None = None
    total_detections: int | None = None
    cpu_percent: float | None = None
    ram_mb: float | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["model"] = self.model.value
        d["tracker"] = self.tracker.value
        d["backend"] = self.backend.value
        return d


def benchmark_env() -> dict:
    """Capture the machine/runtime so results are interpretable and reproducible.

    Honest provenance: these numbers describe THIS machine, not the owner's
    target hardware. Versions are read best-effort (None if a package is absent).
    """
    import platform

    def _ver(mod: str) -> str | None:
        import importlib

        try:
            return getattr(importlib.import_module(mod), "__version__", None)
        except Exception:  # noqa: BLE001 - absent/optional package
            return None

    env: dict = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or None,
        "cpu_count": __import__("os").cpu_count(),
        "torch": _ver("torch"),
        "opencv": _ver("cv2"),
        "ultralytics": _ver("ultralytics"),
        "onnxruntime": _ver("onnxruntime"),
        "openvino": _ver("openvino"),
    }
    try:
        import torch

        env["torch_num_threads"] = torch.get_num_threads()
    except Exception:  # noqa: BLE001 - torch optional
        env["torch_num_threads"] = None
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name"):
                    env["cpu_model"] = line.split(":", 1)[1].strip()
                    break
    except OSError:
        env["cpu_model"] = None
    return env


def _load_frames(config: BenchmarkConfig) -> list:
    """Materialize frames from the configured source (file or synthetic)."""
    from storeguard_vision.capture.base import FrameSource
    from storeguard_vision.capture.file_source import FileFrameSource
    from storeguard_vision.capture.synthetic import SyntheticFrameSource

    src: FrameSource
    if config.clip_path:
        src = FileFrameSource(config.clip_path, max_frames=config.frames)
    else:
        src = SyntheticFrameSource(
            frames=config.frames, width=config.input_size, height=384
        )
    frames = list(src)
    src.close()
    if config.frame_sample_stride > 1:
        frames = frames[:: config.frame_sample_stride]
    # If a small image set is given, repeat it up to `frames` for a stable sample.
    if frames and len(frames) < config.frames:
        reps = (config.frames // len(frames)) + 1
        frames = (frames * reps)[: config.frames]
    return frames


def run_streams(
    model: ModelCandidate,
    n_streams: int,
    frames: int = 30,
    input_size: int = 640,
    device: str = "cpu",
    clip_path: str | None = None,
) -> dict:
    """Run N isolated detectors in parallel threads; report aggregate load.

    One `YoloDetector` per stream (never a shared tracker). Torch/ultralytics
    release the GIL during native inference, so CPU threads genuinely contend —
    this measures how latency/FPS/CPU scale with concurrent cameras on THIS
    machine (not the owner's target hardware).
    """
    import time as _t
    from concurrent.futures import ThreadPoolExecutor

    from storeguard_vision.detect.detector import YoloDetector
    from storeguard_vision.metrics import LatencyStats, ResourceSampler

    imgs = [
        f.image
        for f in _load_frames(
            BenchmarkConfig(
                model=model, frames=frames, input_size=input_size, clip_path=clip_path
            )
        )
    ]
    if not imgs:
        raise RuntimeError("no frames to benchmark")
    detectors = [
        YoloDetector(weights=_WEIGHTS[model], imgsz=input_size, device=device)
        for _ in range(n_streams)
    ]
    for d in detectors:  # warmup each
        d.infer(imgs[0])

    per_stream: list[list[float]] = [[] for _ in range(n_streams)]

    def work(idx: int) -> None:
        det = detectors[idx]
        for img in imgs:
            t0 = _t.perf_counter()
            det.infer(img)
            per_stream[idx].append((_t.perf_counter() - t0) * 1000.0)

    with ResourceSampler() as sampler:
        wall0 = _t.perf_counter()
        with ThreadPoolExecutor(max_workers=n_streams) as ex:
            list(ex.map(work, range(n_streams)))
        wall_s = _t.perf_counter() - wall0

    pooled = [x for s in per_stream for x in s]
    stats = LatencyStats.from_samples(pooled)
    total_frames = n_streams * len(imgs)
    return {
        "model": model.value,
        "n_streams": n_streams,
        "frames_per_stream": len(imgs),
        "latency_p50_ms": round(stats.p50_ms, 2),
        "latency_p95_ms": round(stats.p95_ms, 2),
        "aggregate_fps": round(total_frames / wall_s, 2) if wall_s else None,
        "wall_s": round(wall_s, 2),
        "cpu_percent": (
            round(sampler.avg_cpu_percent, 1) if sampler.avg_cpu_percent else None
        ),
        "ram_mb": round(sampler.peak_rss_mb, 1) if sampler.peak_rss_mb else None,
    }


def _resolve_weights(config: BenchmarkConfig) -> str:
    """Return the weights path for the chosen backend (exporting on demand)."""
    if config.model not in _WEIGHTS:
        raise NotImplementedError(f"unknown model candidate: {config.model.value!r}")
    base = _WEIGHTS[config.model]
    if config.backend is Backend.PYTORCH:
        return base
    from storeguard_vision.export import export_model

    return str(export_model(base, config.backend, config.input_size, config.export_dir))


def run_benchmark(config: BenchmarkConfig) -> BenchmarkResult:
    """Run the benchmark and return measured metrics (pooled over ``trials``)."""
    from storeguard_vision.detect.detector import YoloDetector
    from storeguard_vision.metrics import LatencyStats, ResourceSampler

    weights = _resolve_weights(config)
    detector = YoloDetector(
        weights=weights,
        imgsz=config.input_size,
        device=config.device,
        conf=config.conf,
    )
    frames = _load_frames(config)
    if not frames:
        raise RuntimeError("no frames to benchmark")

    # Warmup (not measured) to exclude first-call graph/alloc costs.
    for i in range(min(config.warmup, len(frames))):
        detector.infer(frames[i].image)

    latencies: list[float] = []  # pooled across all trials
    total_dets = 0
    trials = max(1, config.trials)
    with ResourceSampler() as sampler:
        for _ in range(trials):
            for frame in frames:
                t0 = time.perf_counter()
                dets = detector.infer(frame.image)
                latencies.append((time.perf_counter() - t0) * 1000.0)
                total_dets += len(dets)

    stats = LatencyStats.from_samples(latencies)
    return BenchmarkResult(
        model=config.model,
        tracker=config.tracker,
        backend=config.backend,
        device=config.device,
        input_size=config.input_size,
        frames=len(frames),
        trials=trials,
        latency_p50_ms=round(stats.p50_ms, 2),
        latency_p95_ms=round(stats.p95_ms, 2),
        latency_mean_ms=round(stats.mean_ms, 2),
        fps=round(stats.fps, 2),
        total_detections=total_dets,
        cpu_percent=(
            round(sampler.avg_cpu_percent, 1) if sampler.avg_cpu_percent else None
        ),
        ram_mb=round(sampler.peak_rss_mb, 1) if sampler.peak_rss_mb else None,
        notes=[
            f"CPU single-stream latency on this machine; backend={config.backend.value}; "
            f"{trials} trial(s) x {len(frames)} frames pooled.",
            "THROUGHPUT only. precision/recall/id_switches need a labelled eval set "
            "(not run); no accuracy or model-selection claim.",
            f"source={'file:' + config.clip_path if config.clip_path else 'synthetic'}",
        ],
    )
