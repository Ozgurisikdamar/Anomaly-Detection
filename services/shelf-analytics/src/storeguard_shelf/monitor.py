"""Shelf occupancy / unresolved-removal state machine (rules A1–A3)."""

from __future__ import annotations

from storeguard_contracts import (
    AnomalyEvent,
    CameraStreamState,
    ConfidenceComponents,
    EventType,
    Severity,
)

from storeguard_shelf.model import ShelfRules, ShelfTick, ZoneState

RULE_VERSION = "phase3-shelf-fsm"
_ASSOCIATION_WINDOW_S = 2.0


class ShelfMonitor:
    def __init__(self, store_id: str, rules: ShelfRules | None = None) -> None:
        self.store_id = store_id
        self.rules = rules or ShelfRules()
        self._zones: dict[str, ZoneState] = {}
        self._last_interaction_t: dict[str, float] = {}

    def _zone(self, zone_id: str) -> ZoneState:
        return self._zones.setdefault(zone_id, ZoneState())

    def _cooldown_ok(self, last_t: float | None, now: float) -> bool:
        return last_t is None or (now - last_t) >= self.rules.cooldown_s

    def process(self, tick: ShelfTick) -> list[AnomalyEvent]:
        z = self._zone(tick.zone_id)
        events: list[AnomalyEvent] = []
        trustworthy = (
            tick.camera_state == CameraStreamState.ONLINE and not tick.occluded
        )

        if tick.person_interaction:
            self._last_interaction_t[tick.zone_id] = tick.t

        # A1 — approved replenishment: controlled baseline update, never an alert,
        # and never confused with a removal.
        if tick.approved_replenishment and tick.product_present:
            z.baseline_established = True
            z.stable_present_count = self.rules.baseline_min_observations
            z.present = True
            z.absence_start_t = None
            z.interaction_during_absence = False
            z.crowded_during_absence = False
            return events

        # A2 — occlusion / offline suppression: an untrustworthy frame can never
        # allege a removal. Surface an occlusion review instead and keep UNKNOWN.
        if not trustworthy:
            if z.baseline_established and not tick.product_present:
                if z.absence_start_t is None:
                    z.absence_start_t = tick.t
                z.crowded_during_absence = z.crowded_during_absence or tick.crowded
                if self._cooldown_ok(z.last_occlusion_event_t, tick.t):
                    z.last_occlusion_event_t = tick.t
                    events.append(self._occlusion_event(tick))
            return events

        # Trustworthy frame.
        if tick.product_present:
            if z.present is False and z.absence_start_t is not None:
                z.absence_start_t = None  # item returned; clear pending absence
                z.interaction_during_absence = False
                z.crowded_during_absence = False
            z.present = True
            if not z.baseline_established:
                z.stable_present_count += 1
                if z.stable_present_count >= self.rules.baseline_min_observations:
                    z.baseline_established = True
            return events

        # Absent and trustworthy.
        z.present = False
        if not z.baseline_established:
            return events  # no baseline yet -> nothing to allege

        if z.absence_start_t is None:
            z.absence_start_t = tick.t
            z.interaction_during_absence = False
            z.crowded_during_absence = False
        if tick.person_interaction:
            z.interaction_during_absence = True
        if tick.crowded:
            z.crowded_during_absence = True

        elapsed = tick.t - z.absence_start_t
        if elapsed >= self.rules.removal_interval_s and self._cooldown_ok(
            z.last_removal_event_t, tick.t
        ):
            z.last_removal_event_t = tick.t
            events.append(self._removal_event(tick, z))
            # A1 invariant: do NOT learn the removal as a new baseline. Baseline
            # stays established; cooldown prevents duplicate candidates.
        return events

    # --- event builders --------------------------------------------------
    def _interacted(self, tick: ShelfTick, z: ZoneState) -> bool:
        if z.interaction_during_absence:
            return True
        last = self._last_interaction_t.get(tick.zone_id)
        if last is not None and z.absence_start_t is not None:
            return (z.absence_start_t - last) <= _ASSOCIATION_WINDOW_S
        return False

    def _removal_event(self, tick: ShelfTick, z: ZoneState) -> AnomalyEvent:
        interacted = self._interacted(tick, z)
        crowded = z.crowded_during_absence
        reason_codes = ["item_absent_over_threshold"]
        if interacted:
            reason_codes.append("person_interaction_nearby")
        missing = ["association_unknown_crowded"] if crowded else []
        return AnomalyEvent(
            store_id=self.store_id,
            camera_id=tick.camera_id,
            zone_id=tick.zone_id,
            event_type=EventType.SHELF_ITEM_REMOVED_UNRESOLVED,
            severity=Severity.REVIEW,
            track_refs=[tick.track_ref] if (interacted and tick.track_ref) else [],
            confidence=ConfidenceComponents(
                zone_certainty=0.85,
                rule_evidence=0.6,
                track_quality=0.6 if interacted and not crowded else None,
            ),
            reason_codes=reason_codes,
            missing_data_flags=missing,
            explanation=(
                "A product left the shelf ROI and did not reappear within the configured "
                "interval. This is NOT proof of theft — it may be a legitimate pickup, "
                "replenishment or occlusion. "
                + (
                    "A nearby person interaction was observed (association evidence only, not "
                    "identity). "
                    if interacted
                    else ""
                )
                + ("Association is UNKNOWN (crowded/occluded). " if crowded else "")
                + "Requires human review."
            ),
            rule_version=RULE_VERSION,
            simulated=True,
        )

    def _occlusion_event(self, tick: ShelfTick) -> AnomalyEvent:
        occluded = tick.occluded
        reason = "zone_occluded" if occluded else "camera_unhealthy"
        flag = (
            "shelf_zone_occluded"
            if occluded
            else f"camera_{tick.camera_state.value.lower()}"
        )
        return AnomalyEvent(
            store_id=self.store_id,
            camera_id=tick.camera_id,
            zone_id=tick.zone_id,
            event_type=EventType.SHELF_OCCLUSION_REVIEW,
            severity=Severity.INFO,
            confidence=ConfidenceComponents(zone_certainty=0.3),
            reason_codes=[reason],
            missing_data_flags=[flag],
            explanation=(
                "The shelf ROI could not be trusted (occluded or camera unhealthy) while the "
                "product appeared absent. No removal is alleged; the zone is marked UNKNOWN "
                "for this window."
            ),
            rule_version=RULE_VERSION,
            simulated=True,
        )
