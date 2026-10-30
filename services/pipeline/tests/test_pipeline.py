"""Pipeline vertical-slice test (guarded by the `ml` extra).

Skips when ultralytics/opencv are not installed so CI stays light; runs the real
FILE DEMO slice (clip -> YOLO+ByteTrack -> zones -> shelf FSM -> event) where the
ml stack is present.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_HAS_ML = (
    importlib.util.find_spec("ultralytics") is not None
    and importlib.util.find_spec("cv2") is not None
)

pytestmark = pytest.mark.skipif(not _HAS_ML, reason="ml extra (ultralytics/opencv) not installed")

SHELF_POLY = [(0.10, 0.20), (0.55, 0.20), (0.55, 0.70), (0.10, 0.70)]
PICKUP_POLY = [(0.55, 0.20), (0.90, 0.20), (0.90, 0.80), (0.55, 0.80)]


def test_file_demo_produces_shelf_event(tmp_path: Path) -> None:
    from storeguard_pipeline.coordinator import CameraConfig, PipelineCoordinator
    from storeguard_pipeline.demo_clip import make_demo_clip

    clip = make_demo_clip(tmp_path / "clip", frames=24, remove_at=12)
    cfg = CameraConfig(
        camera_id="cam_shelf_01",
        store_id="store_demo_01",
        source_dir=str(clip),
        shelf_zone_id="zone_shelf_01_display",
        shelf_polygon=SHELF_POLY,
        pickup_polygon=PICKUP_POLY,
    )
    result = PipelineCoordinator().run_camera(cfg, tmp_path / "out")

    removals = [e for e in result.events if e.event_type.value == "SHELF_ITEM_REMOVED_UNRESOLVED"]
    assert len(removals) == 1
    ev = removals[0]
    assert ev.human_review_required is True
    assert ev.evidence and ev.evidence[0].available is True
    # A real bounded GIF clip is written, keyed by evidence_id (ready to upload).
    gif = tmp_path / "out" / f"{ev.evidence[0].evidence_id}.gif"
    assert gif.is_file() and gif.read_bytes()[:6] in (b"GIF87a", b"GIF89a")
    assert result.metrics["frames"] == 24
    assert result.metrics["latency_p50_ms"] > 0
    # Product occupancy comes from the labelled demo detector, not SKU recognition.
    assert "DEMO-PRODUCT-DETECTOR" in (ev.model_version or "")


def test_per_camera_detectors_are_isolated(tmp_path: Path) -> None:
    # Two cameras must not share a detector/tracker instance.
    from storeguard_vision.detect.detector import YoloDetector

    d1 = YoloDetector(weights="yolo26n.pt", device="cpu")
    d2 = YoloDetector(weights="yolo26n.pt", device="cpu")
    assert d1 is not d2
    assert d1._model is not d2._model
