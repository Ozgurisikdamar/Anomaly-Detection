"""Deterministic SIMULATED seed data for the Phase 0 demo.

Everything here is fabricated for the scaffold. There is **no** real camera,
POS, scanner or scale behind this data. Checkout feeds are produced by the
``storeguard_integrations`` simulators and carry ``simulated=True``.

The seed deliberately includes a ``TRANSACTION_DATA_MISSING`` event and a
terminal whose scanner feed is unavailable, to demonstrate the core product
rule: missing integration data is UNKNOWN, never a violation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from storeguard_contracts import (
    AnomalyEvent,
    Camera,
    CameraStreamState,
    CameraStreamStatus,
    CameraZone,
    CheckoutSession,
    CheckoutState,
    ConfidenceComponents,
    EventType,
    Severity,
    Store,
    ZoneType,
)
from storeguard_integrations.simulated import (
    simulate_scale_event,
    simulate_scan_event,
)

from storeguard_api.repository import InMemoryRepository

STORE_ID = "store_demo_01"
_T0 = datetime(2026, 10, 30, 9, 0, 0, tzinfo=UTC)


def _store() -> Store:
    return Store(
        store_id=STORE_ID, name="StoreGuard Demo Market", timezone="Europe/Istanbul"
    )


def _cameras() -> list[Camera]:
    shelf_zones = [
        CameraZone(
            zone_id="zone_shelf_01_display",
            camera_id="cam_shelf_01",
            zone_type=ZoneType.SHELF_DISPLAY,
            label="Shelf A — display",
            polygon=[(0.10, 0.20), (0.55, 0.20), (0.55, 0.70), (0.10, 0.70)],
        ),
        CameraZone(
            zone_id="zone_shelf_01_pickup",
            camera_id="cam_shelf_01",
            zone_type=ZoneType.PICKUP_INTERACTION,
            label="Shelf A — pickup",
            polygon=[(0.55, 0.20), (0.90, 0.20), (0.90, 0.80), (0.55, 0.80)],
        ),
    ]
    sco_zones = [
        CameraZone(
            zone_id="zone_sco_01_scan",
            camera_id="cam_sco_01",
            zone_type=ZoneType.SCAN_AREA,
            label="SCO 1 — scan area",
            polygon=[(0.15, 0.30), (0.45, 0.30), (0.45, 0.65), (0.15, 0.65)],
        ),
        CameraZone(
            zone_id="zone_sco_01_bag",
            camera_id="cam_sco_01",
            zone_type=ZoneType.BAGGING_SCALE_AREA,
            label="SCO 1 — bagging/scale",
            polygon=[(0.50, 0.30), (0.85, 0.30), (0.85, 0.75), (0.50, 0.75)],
        ),
    ]
    return [
        Camera(
            camera_id="cam_shelf_01",
            store_id=STORE_ID,
            name="Aisle 3 — Shelf A",
            kind="shelf",
            zones=shelf_zones,
        ),
        Camera(
            camera_id="cam_shelf_02",
            store_id=STORE_ID,
            name="Aisle 5 — Shelf C",
            kind="shelf",
        ),
        Camera(
            camera_id="cam_sco_01",
            store_id=STORE_ID,
            name="Self-checkout 1",
            kind="checkout",
            zones=sco_zones,
        ),
        Camera(
            camera_id="cam_sco_02",
            store_id=STORE_ID,
            name="Self-checkout 2",
            kind="checkout",
        ),
    ]


def _statuses() -> list[CameraStreamStatus]:
    # Placeholder health values, all flagged simulated. Real metrics are Phase 2.
    return [
        CameraStreamStatus(
            camera_id="cam_shelf_01",
            state=CameraStreamState.ONLINE,
            fps=11.8,
            frame_age_ms=90.0,
            last_frame_at=_T0,
            reconnect_count=0,
        ),
        CameraStreamStatus(
            camera_id="cam_shelf_02",
            state=CameraStreamState.DEGRADED,
            fps=4.1,
            frame_age_ms=820.0,
            last_frame_at=_T0,
            reconnect_count=3,
        ),
        CameraStreamStatus(
            camera_id="cam_sco_01",
            state=CameraStreamState.ONLINE,
            fps=14.2,
            frame_age_ms=70.0,
            last_frame_at=_T0,
            reconnect_count=0,
        ),
        CameraStreamStatus(
            camera_id="cam_sco_02",
            state=CameraStreamState.OFFLINE,
            fps=None,
            frame_age_ms=None,
            last_frame_at=None,
            reconnect_count=7,
        ),
    ]


def _apply_versions(events: list[AnomalyEvent]) -> list[AnomalyEvent]:
    """Stamp the scaffold model/tracker/rule versions on every seeded event.

    Phase 0 runs no model, so these are explicit "scaffold" placeholders.
    """
    for event in events:
        event.model_version = "scaffold-0 (no model run)"
        event.tracker_version = "scaffold-0"
        event.rule_version = "phase0-demo"
    return events


def _events() -> list[AnomalyEvent]:
    events = [
        AnomalyEvent(
            event_id="evt_shelf_removed_01",
            store_id=STORE_ID,
            camera_id="cam_shelf_01",
            zone_id="zone_shelf_01_display",
            event_type=EventType.SHELF_ITEM_REMOVED_UNRESOLVED,
            severity=Severity.REVIEW,
            detected_at=_T0 + timedelta(minutes=2),
            track_refs=["trk_a3f9"],
            confidence=ConfidenceComponents(
                detector=0.71,
                track_quality=0.63,
                zone_certainty=0.80,
                rule_evidence=0.55,
            ),
            reason_codes=["item_absent_over_threshold", "person_interaction_nearby"],
            explanation=(
                "An item left Shelf A display zone and did not reappear within the "
                "configured interval. This is NOT proof of theft — it may be a legitimate "
                "pickup, replenishment or occlusion. Requires human review."
            ),
        ),
        AnomalyEvent(
            event_id="evt_shelf_occlusion_01",
            store_id=STORE_ID,
            camera_id="cam_shelf_02",
            event_type=EventType.SHELF_OCCLUSION_REVIEW,
            severity=Severity.INFO,
            detected_at=_T0 + timedelta(minutes=5),
            confidence=ConfidenceComponents(zone_certainty=0.30),
            reason_codes=["zone_occluded"],
            missing_data_flags=["shelf_zone_occluded"],
            explanation=(
                "Shelf C zone was occluded by another shopper. No removal is alleged; "
                "zone marked UNKNOWN for the occlusion window."
            ),
        ),
        AnomalyEvent(
            event_id="evt_sco_not_scanned_01",
            store_id=STORE_ID,
            camera_id="cam_sco_01",
            zone_id="zone_sco_01_bag",
            event_type=EventType.ITEM_PLACED_NOT_SCANNED,
            severity=Severity.HIGH_REVIEW,
            detected_at=_T0 + timedelta(minutes=8),
            track_refs=["trk_b1c2"],
            confidence=ConfidenceComponents(
                detector=0.82,
                track_quality=0.74,
                zone_certainty=0.88,
                pos_synchronization=0.90,
                rule_evidence=0.70,
            ),
            reason_codes=["item_in_bagging_zone", "no_matching_scan_in_window"],
            explanation=(
                "An item was observed in the bagging zone with no matching scan within the "
                "window on a HEALTHY simulated POS session. Flagged for review — not an "
                "accusation."
            ),
        ),
        AnomalyEvent(
            event_id="evt_sco_scale_mismatch_01",
            store_id=STORE_ID,
            camera_id="cam_sco_01",
            zone_id="zone_sco_01_bag",
            event_type=EventType.SCALE_MISMATCH_REVIEW,
            severity=Severity.REVIEW,
            detected_at=_T0 + timedelta(minutes=11),
            confidence=ConfidenceComponents(
                pos_synchronization=0.85, rule_evidence=0.60, zone_certainty=0.80
            ),
            reason_codes=["weight_outside_tolerance"],
            explanation=(
                "Simulated stable scale weight fell outside tolerance for the scanned SKU. "
                "Could be produce lookup, stacking, packaging or tare — review required."
            ),
        ),
        AnomalyEvent(
            event_id="evt_sco_data_missing_01",
            store_id=STORE_ID,
            camera_id="cam_sco_02",
            event_type=EventType.TRANSACTION_DATA_MISSING,
            severity=Severity.INFO,
            detected_at=_T0 + timedelta(minutes=13),
            confidence=ConfidenceComponents(pos_synchronization=None),
            reason_codes=["scanner_feed_unavailable"],
            missing_data_flags=["scanner_feed_unavailable", "camera_offline"],
            explanation=(
                "Scanner/POS feed was unavailable for SCO 2 (camera also OFFLINE). Per the "
                "core rule, missing integration data is UNKNOWN — NO non-scan alert is "
                "emitted. Integration warning only."
            ),
        ),
        AnomalyEvent(
            event_id="evt_sco_reconcile_01",
            store_id=STORE_ID,
            camera_id="cam_sco_01",
            event_type=EventType.TRANSACTION_RECONCILIATION_REQUIRED,
            severity=Severity.REVIEW,
            detected_at=_T0 + timedelta(minutes=15),
            confidence=ConfidenceComponents(rule_evidence=0.5, pos_synchronization=0.8),
            reason_codes=["unmatched_item_at_transaction_close"],
            explanation=(
                "At transaction close, one observed item did not reconcile with scans, "
                "voids, payment and scale. Requires reconciliation review."
            ),
        ),
    ]
    return _apply_versions(events)


def _checkouts() -> list[CheckoutSession]:
    # term_01: a healthy simulated session with scan + scale feeds.
    scan = simulate_scan_event(
        terminal_id="term_01", session_id="sess_01", sku="SKU-1001"
    )
    scale = simulate_scale_event(
        terminal_id="term_01",
        session_id="sess_01",
        stable_weight_g=330.0,
        expected_weight_g=325.0,
    )
    term_01 = CheckoutSession(
        terminal_id="term_01",
        store_id=STORE_ID,
        session_id="sess_01",
        state=CheckoutState.BAGGING_OBSERVED,
        scans=[scan],
        scale_events=[scale],
        updated_at=_T0 + timedelta(minutes=8),
    )
    # term_02: scanner feed unavailable -> no scans; stays UNKNOWN, not a violation.
    term_02 = CheckoutSession(
        terminal_id="term_02",
        store_id=STORE_ID,
        session_id="sess_02",
        state=CheckoutState.SESSION_ACTIVE,
        scans=[],
        updated_at=_T0 + timedelta(minutes=13),
    )
    return [term_01, term_02]


def build_repository() -> InMemoryRepository:
    """Construct a fresh repository populated with the SIMULATED seed."""
    return InMemoryRepository(
        stores=[_store()],
        cameras=_cameras(),
        statuses=_statuses(),
        events=_events(),
        checkouts=_checkouts(),
    )
