"""Contract invariant tests (Python source of truth)."""

from __future__ import annotations

from storeguard_contracts import (
    AnomalyEvent,
    EventType,
    ScanEvent,
)


def test_event_defaults_require_human_review() -> None:
    ev = AnomalyEvent(
        store_id="s", camera_id="c", event_type=EventType.SHELF_ITEM_REMOVED_UNRESOLVED
    )
    assert ev.human_review_required is True
    assert ev.simulated is True
    assert ev.event_id.startswith("evt_")


def test_event_timestamps_are_utc() -> None:
    ev = AnomalyEvent(
        store_id="s", camera_id="c", event_type=EventType.TRANSACTION_UNKNOWN
    )
    assert ev.occurred_at.tzinfo is not None
    assert ev.detected_at.utcoffset() is not None


def test_scan_event_is_simulated_by_default() -> None:
    scan = ScanEvent(scan_id="x", terminal_id="t", session_id="s", sku="SKU-1")
    assert scan.simulated is True


def test_no_event_type_names_a_person() -> None:
    banned = ("thief", "suspect", "criminal", "person_guilty")
    for et in EventType:
        assert not any(b in et.value.lower() for b in banned)
