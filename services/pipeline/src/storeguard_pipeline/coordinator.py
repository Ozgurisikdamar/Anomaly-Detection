"""PipelineCoordinator: file/RTSP frames -> detector/tracker -> zones -> shelf FSM.

Each camera gets its own YOLO detector/tracker instance (isolated ByteTrack
state). Person interaction comes from the real COCO person class; product
occupancy from the labelled DemoProductDetector. Emitted events are the shared
AnomalyEvent contract and carry an evidence reference from real frames.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from storeguard_contracts import AnomalyEvent, CameraStreamState
from storeguard_shelf.model import ShelfRules, ShelfTick
from storeguard_shelf.monitor import ShelfMonitor
from storeguard_zones.geometry import point_in_polygon

from storeguard_pipeline.demo_product_detector import LABEL as DEMO_DETECTOR_LABEL
from storeguard_pipeline.demo_product_detector import product_present_in_roi
from storeguard_pipeline.evidence_clip import save_evidence_gif

Polygon = list[tuple[float, float]]


@dataclass
class CameraConfig:
    camera_id: str
    store_id: str
    source_dir: str
    shelf_zone_id: str
    shelf_polygon: Polygon
    pickup_polygon: Polygon | None = None
    source_label: str = "FILE DEMO"
    fps: float = 10.0
    weights: str = "yolo26n.pt"
    imgsz: int = 640


@dataclass
class PipelineResult:
    camera_id: str
    source_label: str
    events: list[AnomalyEvent]
    metrics: dict = field(default_factory=dict)


def _roi_bbox(poly: Polygon) -> tuple[float, float, float, float]:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


class PipelineCoordinator:
    """Runs the vertical slice for one or more cameras (per-camera isolation)."""

    def __init__(self, rules: ShelfRules | None = None) -> None:
        # Demo thresholds: short enough that the removal fires within a short clip.
        self.rules = rules or ShelfRules(baseline_min_observations=5, removal_interval_s=1.0)

    def run_camera(self, cfg: CameraConfig, out_dir: str | Path) -> PipelineResult:
        from storeguard_vision.capture.file_source import FileFrameSource
        from storeguard_vision.detect.detector import YoloDetector
        from storeguard_vision.metrics import LatencyStats, ResourceSampler

        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)

        detector = YoloDetector(weights=cfg.weights, imgsz=cfg.imgsz, device="cpu")  # per-camera
        monitor = ShelfMonitor(cfg.store_id, self.rules)
        shelf_roi = _roi_bbox(cfg.shelf_polygon)
        interaction_zone = cfg.pickup_polygon or cfg.shelf_polygon

        latencies: list[float] = []
        frames: list = []
        total_dets = 0
        events: list[AnomalyEvent] = []

        with ResourceSampler() as sampler:
            for frame in FileFrameSource(cfg.source_dir, fps=cfg.fps):
                frames.append(frame.image)
                t0 = time.perf_counter()
                dets = detector.track(frame.image)  # real YOLO + ByteTrack
                latencies.append((time.perf_counter() - t0) * 1000.0)
                total_dets += len(dets)

                h, w = frame.image.shape[:2]
                person_interaction = False
                track_ref = None
                for d in dets:
                    if d.label != "person":
                        continue
                    cx = ((d.xyxy[0] + d.xyxy[2]) / 2) / w
                    cy = ((d.xyxy[1] + d.xyxy[3]) / 2) / h
                    if point_in_polygon((cx, cy), interaction_zone):
                        person_interaction = True
                        track_ref = None if d.track_id is None else f"trk_{d.track_id}"

                product_present = product_present_in_roi(frame.image, shelf_roi)

                tick = ShelfTick(
                    t=frame.timestamp,
                    zone_id=cfg.shelf_zone_id,
                    camera_id=cfg.camera_id,
                    product_present=product_present,
                    camera_state=CameraStreamState.ONLINE,
                    person_interaction=person_interaction,
                    track_ref=track_ref,
                )
                for ev in monitor.process(tick):
                    ev.evidence = [
                        save_evidence_gif(frames, out, f"ev_{ev.event_id}", cfg.shelf_polygon)
                    ]
                    ev.model_version = f"{cfg.weights} (person=COCO) + {DEMO_DETECTOR_LABEL}"
                    events.append(ev)

        stats = LatencyStats.from_samples(latencies)
        metrics = {
            "frames": len(frames),
            "detections_total": total_dets,
            "latency_p50_ms": round(stats.p50_ms, 2),
            "latency_p95_ms": round(stats.p95_ms, 2),
            "latency_mean_ms": round(stats.mean_ms, 2),
            "fps": round(stats.fps, 2),
            "frame_age_p95_ms": round(stats.p95_ms, 2),  # processing-cadence proxy (file batch)
            "cpu_percent": (round(sampler.avg_cpu_percent, 1) if sampler.avg_cpu_percent else None),
            "ram_mb": round(sampler.peak_rss_mb, 1) if sampler.peak_rss_mb else None,
            "detector": cfg.weights,
            "source_label": cfg.source_label,
        }
        return PipelineResult(cfg.camera_id, cfg.source_label, events, metrics)
