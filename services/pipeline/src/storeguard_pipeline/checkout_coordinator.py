"""CheckoutPipelineCoordinator: file/RTSP frames + a POS feed -> correlation.

Ties a self-checkout camera to a (simulated or, later, real) POS feed:

- The camera, per frame, yields **real COCO person** detections (proving the
  detector/tracker run) and a **bagging-zone product-presence** signal from the
  labelled DemoProductDetector — never an SKU claim. A rising edge "product now
  present in the bagging ROI" is one item placed in the bagging area.
- The ``PosFeed`` is drained on the same session clock. Messages are correlated
  to the terminal/session; a down feed or a late/degraded feed marks the FSM so
  an unmatched item resolves to TRANSACTION_DATA_MISSING, **never** a non-scan.
- The ``CheckoutMonitor`` (phase-4 FSM) turns correlated observations + messages
  into the shared ``AnomalyEvent`` contract, with real-frame evidence attached.

Each camera gets its own isolated YOLO detector/tracker instance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from storeguard_checkout.model import CheckoutRules
from storeguard_checkout.monitor import CheckoutMonitor
from storeguard_contracts import AnomalyEvent, ScaleEvent, ScanEvent, TransactionEvent
from storeguard_integrations.pos_feed import PosFeed
from storeguard_zones.geometry import point_in_polygon

from storeguard_pipeline.coordinator import PipelineResult
from storeguard_pipeline.demo_product_detector import LABEL as DEMO_DETECTOR_LABEL
from storeguard_pipeline.demo_product_detector import product_present_in_roi
from storeguard_pipeline.evidence_clip import save_evidence_gif

Polygon = list[tuple[float, float]]

# Demo thresholds: short enough that the scan window expires within a short clip.
DEMO_RULES = CheckoutRules(scan_match_window_s=1.0, feed_lateness_window_s=0.5)


@dataclass
class CheckoutCameraConfig:
    camera_id: str
    store_id: str
    terminal_id: str
    session_id: str
    source_dir: str
    bagging_polygon: Polygon
    scan_polygon: Polygon | None = None
    source_label: str = "FILE DEMO"
    fps: float = 10.0
    weights: str = "yolo26n.pt"
    imgsz: int = 640


def _roi_bbox(poly: Polygon) -> tuple[float, float, float, float]:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


class CheckoutPipelineCoordinator:
    """Runs a self-checkout camera + POS feed through the checkout FSM."""

    def __init__(self, rules: CheckoutRules | None = None) -> None:
        self.rules = rules or DEMO_RULES

    def run(
        self, cfg: CheckoutCameraConfig, feed: PosFeed, out_dir: str | Path
    ) -> PipelineResult:
        from storeguard_vision.capture.file_source import FileFrameSource
        from storeguard_vision.detect.detector import YoloDetector
        from storeguard_vision.metrics import LatencyStats, ResourceSampler

        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)

        detector = YoloDetector(
            weights=cfg.weights, imgsz=cfg.imgsz, device="cpu"
        )  # per-camera, isolated ByteTrack state
        monitor = CheckoutMonitor(cfg.store_id, self.rules)
        monitor.start_session(cfg.terminal_id, cfg.session_id, cfg.camera_id, t=0.0)

        bagging_roi = _roi_bbox(cfg.bagging_polygon)
        interaction_zone = cfg.scan_polygon or cfg.bagging_polygon

        latencies: list[float] = []
        frames: list = []
        total_dets = 0
        events: list[AnomalyEvent] = []
        prev_present = False
        item_seq = 0
        last_t = 0.0

        with ResourceSampler() as sampler:
            for frame in FileFrameSource(cfg.source_dir, fps=cfg.fps):
                frames.append(frame.image)
                t = frame.timestamp
                last_t = t

                t0 = time.perf_counter()
                dets = detector.track(frame.image)  # real YOLO + ByteTrack
                latencies.append((time.perf_counter() - t0) * 1000.0)
                total_dets += len(dets)

                h, w = frame.image.shape[:2]
                for d in dets:  # real COCO person interaction (not an SKU)
                    if d.label != "person":
                        continue
                    cx = ((d.xyxy[0] + d.xyxy[2]) / 2) / w
                    cy = ((d.xyxy[1] + d.xyxy[3]) / 2) / h
                    point_in_polygon((cx, cy), interaction_zone)

                # --- feed health first: a down or late feed is UNKNOWN ----
                if not feed.available(t):
                    monitor.set_scanner_available(cfg.terminal_id, False)
                elif feed.degraded(t):
                    monitor.set_feed_degraded(cfg.terminal_id)

                # --- correlate delivered POS messages by terminal/session --
                for dm in feed.drain(t):
                    msg = dm.message
                    if (
                        msg.terminal_id != cfg.terminal_id
                        or msg.session_id != cfg.session_id
                    ):
                        continue  # mismatched session never correlates
                    if dm.lateness_s > self.rules.feed_lateness_window_s:
                        monitor.set_feed_degraded(cfg.terminal_id)
                    events += self._route(monitor, msg)

                # --- bagging-zone item observation (rising edge) ----------
                present = product_present_in_roi(frame.image, bagging_roi)
                if present and not prev_present:
                    item_seq += 1
                    events += monitor.observe_bagging_item(
                        cfg.terminal_id,
                        cfg.session_id,
                        f"item{item_seq}",
                        t=t,
                        camera_id=cfg.camera_id,
                    )
                prev_present = present

                events += monitor.advance(cfg.terminal_id, t)

        # Flush any window still open at clip end.
        events += monitor.finalize(
            cfg.terminal_id, last_t + self.rules.scan_match_window_s + 1.0
        )

        for ev in events:
            ev.evidence = [
                save_evidence_gif(frames, out, f"ev_{ev.event_id}", cfg.bagging_polygon)
            ]
            ev.model_version = f"{cfg.weights} (person=COCO) + {DEMO_DETECTOR_LABEL}"

        stats = LatencyStats.from_samples(latencies)
        metrics = {
            "frames": len(frames),
            "detections_total": total_dets,
            "latency_p50_ms": round(stats.p50_ms, 2),
            "latency_p95_ms": round(stats.p95_ms, 2),
            "latency_mean_ms": round(stats.mean_ms, 2),
            "fps": round(stats.fps, 2),
            "frame_age_p95_ms": round(stats.p95_ms, 2),
            "cpu_percent": (
                round(sampler.avg_cpu_percent, 1) if sampler.avg_cpu_percent else None
            ),
            "ram_mb": round(sampler.peak_rss_mb, 1) if sampler.peak_rss_mb else None,
            "detector": cfg.weights,
            "source_label": cfg.source_label,
        }
        return PipelineResult(cfg.camera_id, cfg.source_label, events, metrics)

    @staticmethod
    def _route(monitor: CheckoutMonitor, msg: object) -> list[AnomalyEvent]:
        if isinstance(msg, ScanEvent):
            return monitor.observe_scan(msg)
        if isinstance(msg, ScaleEvent):
            return monitor.observe_scale(msg)
        if isinstance(msg, TransactionEvent):
            return monitor.observe_transaction(msg)
        return []
