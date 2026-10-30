"""Replay tests for shelf scenarios 1-3 and rule invariants (no ML stack)."""

from __future__ import annotations

from storeguard_contracts import CameraStreamState, EventType

from storeguard_shelf.model import ShelfRules, ShelfTick
from storeguard_shelf.monitor import ShelfMonitor
from storeguard_shelf.scenarios import (
    run_all,
    run_scenario,
    scenario_occlusion,
    scenario_removal,
    scenario_replenishment,
    total_false_alerts,
)

ZONE = "zone_shelf_01_display"
CAM = "cam_shelf_01"


def test_scenario_removal_fires_once_with_association() -> None:
    r = run_scenario("shelf-removal", scenario_removal(), expected_removal=True)
    assert r.removal_count == 1
    assert r.false_alerts == 0
    ev = r.events[0]
    assert ev.event_type == EventType.SHELF_ITEM_REMOVED_UNRESOLVED
    assert "person_interaction_nearby" in ev.reason_codes
    assert ev.human_review_required is True
    assert ev.simulated is True
    # Neutral language: the type never names or accuses a person.
    assert "thief" not in ev.event_type.value.lower()


def test_scenario_occlusion_no_removal_marks_unknown() -> None:
    r = run_scenario("shelf-occlusion", scenario_occlusion(), expected_removal=False)
    assert r.removal_count == 0
    assert r.occlusion_count >= 1
    assert r.false_alerts == 0
    occl = r.events[0]
    assert occl.event_type == EventType.SHELF_OCCLUSION_REVIEW
    assert "shelf_zone_occluded" in occl.missing_data_flags


def test_scenario_replenishment_no_alert() -> None:
    r = run_scenario(
        "shelf-replenishment", scenario_replenishment(), expected_removal=False
    )
    assert r.removal_count == 0
    assert r.occlusion_count == 0
    assert r.false_alerts == 0


def test_total_false_alerts_zero() -> None:
    assert total_false_alerts(run_all()) == 0


def test_removal_does_not_reset_baseline_and_cooldown_dedups() -> None:
    mon = ShelfMonitor(
        "store_demo_01", ShelfRules(baseline_min_observations=3, removal_interval_s=2.0)
    )
    events = []
    for t in range(0, 3):  # baseline
        events += mon.process(
            ShelfTick(t=float(t), zone_id=ZONE, camera_id=CAM, product_present=True)
        )
    for t in range(3, 8):  # long absence: fires once, then cooldown dedups
        events += mon.process(
            ShelfTick(t=float(t), zone_id=ZONE, camera_id=CAM, product_present=False)
        )
    removals = [
        e for e in events if e.event_type == EventType.SHELF_ITEM_REMOVED_UNRESOLVED
    ]
    assert len(removals) == 1  # baseline not reset into a new removal; cooldown holds


def test_offline_absence_is_unknown_not_removal() -> None:
    mon = ShelfMonitor("store_demo_01")
    for t in range(0, 5):
        mon.process(
            ShelfTick(t=float(t), zone_id=ZONE, camera_id=CAM, product_present=True)
        )
    events = []
    for t in range(5, 12):
        events += mon.process(
            ShelfTick(
                t=float(t),
                zone_id=ZONE,
                camera_id=CAM,
                product_present=False,
                camera_state=CameraStreamState.OFFLINE,
            )
        )
    assert all(e.event_type != EventType.SHELF_ITEM_REMOVED_UNRESOLVED for e in events)
    assert any(e.event_type == EventType.SHELF_OCCLUSION_REVIEW for e in events)
