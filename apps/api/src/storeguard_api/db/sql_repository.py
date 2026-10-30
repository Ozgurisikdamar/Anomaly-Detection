"""PostgreSQL-backed repository for events, review decisions and audit log.

Events and audit rows persist in the database so review outcomes survive an API
restart. Store/camera/checkout *configuration* is read from the seed config
(it is static demo config, not mutable review state). The full ``AnomalyEvent``
is stored as JSON (authoritative on read); indexed columns stay in sync for
filtering/sorting. Works against PostgreSQL (demo) and SQLite (tests).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, sessionmaker
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

from storeguard_api.db import models
from storeguard_api.repository import NotFoundError
from storeguard_api.seed import SeedData


def _event_to_row(e: AnomalyEvent) -> models.AnomalyEvent:
    return models.AnomalyEvent(
        event_id=e.event_id,
        store_id=e.store_id,
        camera_id=e.camera_id,
        zone_id=e.zone_id,
        event_type=e.event_type.value,
        severity=e.severity.value,
        status=e.status.value,
        occurred_at=e.occurred_at,
        detected_at=e.detected_at,
        created_at=e.created_at,
        model_version=e.model_version,
        tracker_version=e.tracker_version,
        rule_version=e.rule_version,
        explanation=e.explanation,
        reason_codes_json=json.dumps(e.reason_codes),
        missing_data_flags_json=json.dumps(e.missing_data_flags),
        confidence_json=e.confidence.model_dump_json(),
        track_refs_json=json.dumps(e.track_refs),
        human_review_required=e.human_review_required,
        simulated=e.simulated,
        payload_json=e.model_dump_json(),
    )


def _row_to_event(row: models.AnomalyEvent) -> AnomalyEvent:
    # payload_json is authoritative (carries review, evidence, tz-aware times).
    return AnomalyEvent.model_validate_json(row.payload_json)


class SqlAlchemyRepository:
    """Same method surface as InMemoryRepository, backed by a SQL database."""

    def __init__(self, engine: Engine, seed: SeedData) -> None:
        self._engine = engine
        self._session_factory: sessionmaker[Session] = sessionmaker(
            bind=engine, expire_on_commit=False, future=True
        )
        self._stores = {s.store_id: s for s in seed.stores}
        self._cameras = {c.camera_id: c for c in seed.cameras}
        self._statuses = {s.camera_id: s for s in seed.statuses}
        self._checkouts = {c.terminal_id: c for c in seed.checkouts}

    # --- schema / seeding ------------------------------------------------
    def ensure_schema(self) -> None:
        models.Base.metadata.create_all(self._engine)

    def seed_events_if_empty(self, events: list[AnomalyEvent]) -> None:
        with self._session_factory() as s:
            existing = s.scalar(select(models.AnomalyEvent).limit(1))
            if existing is not None:
                return
            for e in events:
                s.add(_event_to_row(e))
            s.commit()

    # --- config (static, from seed) --------------------------------------
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

    def list_checkouts(self) -> list[CheckoutSession]:
        return list(self._checkouts.values())

    def get_checkout(self, terminal_id: str) -> CheckoutSession:
        if terminal_id not in self._checkouts:
            raise NotFoundError(terminal_id)
        return self._checkouts[terminal_id]

    # --- events (DB) -----------------------------------------------------
    def list_events(
        self,
        status: EventStatus | None = None,
        event_type: str | None = None,
        camera_id: str | None = None,
    ) -> list[AnomalyEvent]:
        stmt = select(models.AnomalyEvent)
        if status:
            stmt = stmt.where(models.AnomalyEvent.status == status.value)
        if event_type:
            stmt = stmt.where(models.AnomalyEvent.event_type == event_type)
        if camera_id:
            stmt = stmt.where(models.AnomalyEvent.camera_id == camera_id)
        stmt = stmt.order_by(models.AnomalyEvent.detected_at.desc())
        with self._session_factory() as s:
            rows: list[models.AnomalyEvent] = list(s.scalars(stmt).all())
            return [_row_to_event(r) for r in rows]

    def _get_row(self, s: Session, event_id: str) -> models.AnomalyEvent:
        row = s.get(models.AnomalyEvent, event_id)
        if row is None:
            raise NotFoundError(event_id)
        return row

    def get_event(self, event_id: str) -> AnomalyEvent:
        with self._session_factory() as s:
            return _row_to_event(self._get_row(s, event_id))

    def add_event(self, event: AnomalyEvent) -> AnomalyEvent:
        with self._session_factory() as s:
            existing = s.get(models.AnomalyEvent, event.event_id)
            if existing is not None:
                return event
            s.add(_event_to_row(event))
            s.commit()
        return event

    def _apply(
        self, event_id: str, mutate, audit_action: str, reviewer: str, note: str | None
    ) -> AnomalyEvent:
        with self._session_factory() as s:
            row = self._get_row(s, event_id)
            event = _row_to_event(row)
            mutate(event)
            row.status = event.status.value
            row.payload_json = event.model_dump_json()
            s.add(
                models.AuditLog(
                    actor=reviewer,
                    action=audit_action,
                    target=event_id,
                    note=note,
                    created_at=datetime.now(tz=UTC),
                )
            )
            s.commit()
            return event

    def acknowledge_event(self, event_id: str, reviewer: str) -> AnomalyEvent:
        def mutate(e: AnomalyEvent) -> None:
            e.status = EventStatus.ACKNOWLEDGED

        return self._apply(event_id, mutate, "acknowledge", reviewer, None)

    def resolve_event(
        self, event_id: str, reviewer: str, decision: ReviewDecision, note: str | None
    ) -> AnomalyEvent:
        def mutate(e: AnomalyEvent) -> None:
            e.status = EventStatus.RESOLVED
            e.review = ReviewOutcome(
                decision=decision,
                reviewer=reviewer,
                note=note,
                decided_at=datetime.now(tz=UTC),
            )

        return self._apply(
            event_id, mutate, f"resolve:{decision.value}", reviewer, note
        )

    def dismiss_event(
        self, event_id: str, reviewer: str, note: str | None
    ) -> AnomalyEvent:
        def mutate(e: AnomalyEvent) -> None:
            e.status = EventStatus.DISMISSED
            e.review = ReviewOutcome(
                decision=ReviewDecision.FALSE_POSITIVE,
                reviewer=reviewer,
                note=note,
                decided_at=datetime.now(tz=UTC),
            )

        return self._apply(event_id, mutate, "dismiss", reviewer, note)

    # --- audit (DB) ------------------------------------------------------
    def append_audit(
        self, actor: str, action: str, target: str, note: str | None
    ) -> None:
        with self._session_factory() as s:
            s.add(
                models.AuditLog(
                    actor=actor,
                    action=action,
                    target=target,
                    note=note,
                    created_at=datetime.now(tz=UTC),
                )
            )
            s.commit()

    def list_audit(self) -> list[dict[str, str | None]]:
        with self._session_factory() as s:
            audit_rows: list[models.AuditLog] = list(
                s.scalars(select(models.AuditLog).order_by(models.AuditLog.id)).all()
            )
            return [
                {
                    "actor": r.actor,
                    "action": r.action,
                    "target": r.target,
                    "note": r.note,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in audit_rows
            ]
