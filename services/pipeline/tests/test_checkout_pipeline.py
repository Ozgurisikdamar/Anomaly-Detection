"""Checkout correlation pipeline test (guarded by the `ml` extra).

Runs the real FILE DEMO checkout slice (clip -> YOLO+ByteTrack -> bagging
observation -> POS correlation -> checkout FSM -> event). Skips when the ml
stack is absent so CI stays light.
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

BAG_POLY = [(0.50, 0.30), (0.85, 0.30), (0.85, 0.75), (0.50, 0.75)]
SCAN_POLY = [(0.15, 0.30), (0.45, 0.30), (0.45, 0.65), (0.15, 0.65)]


def _cfg(clip: Path, session_id: str = "sess_demo_01"):  # noqa: ANN202
    from storeguard_pipeline.checkout_coordinator import CheckoutCameraConfig

    return CheckoutCameraConfig(
        camera_id="cam_sco_01",
        store_id="store_demo_01",
        terminal_id="term_01",
        session_id=session_id,
        source_dir=str(clip),
        bagging_polygon=BAG_POLY,
        scan_polygon=SCAN_POLY,
    )


def _clip(tmp_path: Path) -> Path:
    from storeguard_pipeline.demo_clip import make_checkout_demo_clip

    return make_checkout_demo_clip(tmp_path / "clip", frames=24, place_at=8)


def test_healthy_feed_unscanned_item_is_non_scan(tmp_path: Path) -> None:
    from storeguard_integrations.pos_feed import SimulatedPosFeed

    from storeguard_pipeline.checkout_coordinator import CheckoutPipelineCoordinator

    feed = SimulatedPosFeed("term_01", "sess_demo_01")  # item placed, never scanned
    result = CheckoutPipelineCoordinator().run(_cfg(_clip(tmp_path)), feed, tmp_path / "out")

    non_scan = [e for e in result.events if e.event_type.value == "ITEM_PLACED_NOT_SCANNED"]
    assert len(non_scan) == 1
    ev = non_scan[0]
    assert ev.human_review_required is True
    assert ev.evidence and ev.evidence[0].available is True
    assert "DEMO-PRODUCT-DETECTOR" in (ev.model_version or "")


def test_missing_feed_never_produces_non_scan(tmp_path: Path) -> None:
    from storeguard_integrations.pos_feed import SimulatedPosFeed

    from storeguard_pipeline.checkout_coordinator import CheckoutPipelineCoordinator

    feed = SimulatedPosFeed("term_01", "sess_demo_01", available=False)
    result = CheckoutPipelineCoordinator().run(_cfg(_clip(tmp_path)), feed, tmp_path / "out")
    types = [e.event_type.value for e in result.events]
    assert "ITEM_PLACED_NOT_SCANNED" not in types
    assert "TRANSACTION_DATA_MISSING" in types


def test_delayed_feed_never_produces_non_scan(tmp_path: Path) -> None:
    from storeguard_integrations.pos_feed import SimulatedPosFeed

    from storeguard_pipeline.checkout_coordinator import CheckoutPipelineCoordinator

    feed = SimulatedPosFeed("term_01", "sess_demo_01", degraded_window=(0.3, 5.0)).add_scan(
        "SKU-DEMO", occurred_at_s=0.8, delivery_delay_s=10.0
    )
    result = CheckoutPipelineCoordinator().run(_cfg(_clip(tmp_path)), feed, tmp_path / "out")
    types = [e.event_type.value for e in result.events]
    assert "ITEM_PLACED_NOT_SCANNED" not in types
    assert "TRANSACTION_DATA_MISSING" in types


def test_mismatched_session_scan_does_not_correlate(tmp_path: Path) -> None:
    # A scan for a different session_id must never match the observed item.
    from storeguard_integrations.pos_feed import SimulatedPosFeed

    from storeguard_pipeline.checkout_coordinator import CheckoutPipelineCoordinator

    feed = SimulatedPosFeed("term_01", "other_session").add_scan("SKU-1", 0.5)
    result = CheckoutPipelineCoordinator().run(
        _cfg(_clip(tmp_path), session_id="sess_demo_01"), feed, tmp_path / "out"
    )
    non_scan = [e for e in result.events if e.event_type.value == "ITEM_PLACED_NOT_SCANNED"]
    assert len(non_scan) == 1  # the mismatched scan did not resolve the item
