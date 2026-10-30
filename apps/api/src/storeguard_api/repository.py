"""In-memory repository backing the Phase 0 API.

Phase 0 intentionally serves deterministic SIMULATED data from memory so a
clean clone runs and tests pass without a running PostgreSQL. The same
interface will later be implemented against SQLAlchemy/PostgreSQL (the models
and the initial Alembic migration already exist under ``infra/migrations``).
"""

from __future__ import annotations

from datetime import UTC, datetime

from storeguard_contracts import (
    AnomalyEvent,
    Camera,
    CameraStreamStatus,
    CheckoutSession,
    EventStatus,
    ReviewDecision,
    ReviewOutcome,
    Store,
)


class NotFoundError(KeyError):
    """Raised when an entity id does not exist."""


class InMemoryRepository:
    def __init__(
        self,
        stores: list[Store],
        cameras: list[Camera],
        statuses: list[CameraStreamStatus],
        events: list[AnomalyEvent],
        checkouts: list[CheckoutSession],
    ) -> None:
        self._stores = {s.store_id: s for s in stores}
        self._cameras = {c.camera_id: c for c in cameras}
        self._statuses = {s.camera_id: s for s in statuses}
        self._events = {e.event_id: e for e in events}
        self._checkouts = {c.terminal_id: c for c in checkouts}
        self._audit: list[dict[str, str | None]] = []

    # --- stores / cameras ------------------------------------------------
    def list_stores(self) -> list[Store]:
        return list(self._stores.values())

    def list_cameras(self, store_id: str | None = None) -> list[Camera]:
        cams = list(self._cameras.values())
        if store_id:
            cams = [c for c in cams if c.store_id == store_id]
        return cams

    def get_camera_status(self, camera_id: str) -> CameraStreamStatus:
        if camera_id not in self._statuses:
            raise NotFoundError(camera_id)
        return self._statuses[camera_id]

    # --- events ----------------------------------------------------------
    def list_events(
        self,
        status: EventStatus | None = None,
        event_type: str | None = None,
        camera_id: str | None = None,
    ) -> list[AnomalyEvent]:
        items = list(self._events.values())
        if status:
            items = [e for e in items if e.status == status]
        if event_type:
            items = [e for e in items if e.event_type.value == event_type]
        if camera_id:
            items = [e for e in items if e.camera_id == camera_id]
        return sorted(items, key=lambda e: e.detected_at, reverse=True)

    def get_event(self, event_id: str) -> AnomalyEvent:
        if event_id not in self._events:
            raise NotFoundError(event_id)
        return self._events[event_id]

    def add_event(self, event: AnomalyEvent) -> AnomalyEvent:
        self._events[event.event_id] = event
        return event

    def _touch(self, event: AnomalyEvent) -> AnomalyEvent:
        self._events[event.event_id] = event
        return event

    def acknowledge_event(self, event_id: str, reviewer: str) -> AnomalyEvent:
        event = self.get_event(event_id)
        event.status = EventStatus.ACKNOWLEDGED
        self.append_audit(reviewer, "acknowledge", event_id, None)
        return self._touch(event)

    def resolve_event(
        self, event_id: str, reviewer: str, decision: ReviewDecision, note: str | None
    ) -> AnomalyEvent:
        event = self.get_event(event_id)
        event.status = EventStatus.RESOLVED
        event.review = ReviewOutcome(
            decision=decision,
            reviewer=reviewer,
            note=note,
            decided_at=datetime.now(tz=UTC),
        )
        self.append_audit(reviewer, f"resolve:{decision.value}", event_id, note)
        return self._touch(event)

    def dismiss_event(
        self, event_id: str, reviewer: str, note: str | None
    ) -> AnomalyEvent:
        event = self.get_event(event_id)
        event.status = EventStatus.DISMISSED
        event.review = ReviewOutcome(
            decision=ReviewDecision.FALSE_POSITIVE,
            reviewer=reviewer,
            note=note,
            decided_at=datetime.now(tz=UTC),
        )
        self.append_audit(reviewer, "dismiss", event_id, note)
        return self._touch(event)

    # --- audit -----------------------------------------------------------
    def append_audit(
        self, actor: str, action: str, target: str, note: str | None
    ) -> None:
        self._audit.append(
            {
                "actor": actor,
                "action": action,
                "target": target,
                "note": note,
                "created_at": datetime.now(tz=UTC).isoformat(),
            }
        )

    def list_audit(self) -> list[dict[str, str | None]]:
        return list(self._audit)

    # --- checkouts -------------------------------------------------------
    def list_checkouts(self) -> list[CheckoutSession]:
        return list(self._checkouts.values())

    def get_checkout(self, terminal_id: str) -> CheckoutSession:
        if terminal_id not in self._checkouts:
            raise NotFoundError(terminal_id)
        return self._checkouts[terminal_id]
