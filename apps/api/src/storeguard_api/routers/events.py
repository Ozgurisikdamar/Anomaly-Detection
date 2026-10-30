"""Anomaly event endpoints: ingest, list, detail, and human-review actions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from storeguard_contracts import AnomalyEvent, EventStatus, ReviewDecision

from storeguard_api.deps import get_event_bus, get_evidence_store, get_repository
from storeguard_api.event_bus import EventBus
from storeguard_api.evidence import EvidenceStore
from storeguard_api.repository import InvalidTransitionError, NotFoundError

router = APIRouter()


def _with_evidence_urls(event: AnomalyEvent, store: EvidenceStore) -> AnomalyEvent:
    """Return a copy whose evidence carries a fresh short-lived signed URL.

    Availability is recomputed from what is actually in the store (the pipeline
    uploads the bytes separately), so ``available`` never over-claims. The stored
    event is never mutated — the URL is minted per response and expires.
    """
    decorated = event.model_copy(deep=True)
    for ev in decorated.evidence:
        if store.exists(ev.evidence_id):
            url, exp = store.sign_url(ev.evidence_id)
            ev.available = True
            ev.url = url
            ev.expires_at = datetime.fromtimestamp(exp, tz=UTC)
        else:
            ev.available = False
            ev.url = None
            ev.expires_at = None
    return decorated


class AcknowledgeRequest(BaseModel):
    reviewer: str = "demo-reviewer"


class ResolveRequest(BaseModel):
    reviewer: str = "demo-reviewer"
    decision: ReviewDecision = ReviewDecision.CONFIRMED_OPERATIONAL_ANOMALY
    note: str | None = None


class DismissRequest(BaseModel):
    reviewer: str = "demo-reviewer"
    note: str | None = None


def _publish(bus: EventBus, kind: str, event: AnomalyEvent) -> None:
    bus.publish({"kind": kind, "event": event.model_dump(mode="json")})


@router.post("/events", response_model=AnomalyEvent, status_code=201, tags=["events"])
def ingest_event(
    event: AnomalyEvent,
    repo: Any = Depends(get_repository),
    bus: EventBus = Depends(get_event_bus),
) -> AnomalyEvent:
    """Ingest an event produced by the pipeline (persist + publish realtime)."""
    stored = repo.add_event(event)
    _publish(bus, "event.new", stored)
    return stored


@router.get("/events", response_model=list[AnomalyEvent], tags=["events"])
def list_events(
    status: EventStatus | None = None,
    type: str | None = None,
    camera_id: str | None = None,
    repo: Any = Depends(get_repository),
    store: EvidenceStore = Depends(get_evidence_store),
) -> list[AnomalyEvent]:
    events = repo.list_events(status=status, event_type=type, camera_id=camera_id)
    return [_with_evidence_urls(e, store) for e in events]


@router.get("/events/{event_id}", response_model=AnomalyEvent, tags=["events"])
def get_event(
    event_id: str,
    repo: Any = Depends(get_repository),
    store: EvidenceStore = Depends(get_evidence_store),
) -> AnomalyEvent:
    try:
        return _with_evidence_urls(repo.get_event(event_id), store)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc


def _review_error(exc: Exception) -> HTTPException:
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=404, detail="event not found")
    if isinstance(exc, InvalidTransitionError):
        return HTTPException(status_code=409, detail=str(exc))
    raise exc


@router.post(
    "/events/{event_id}/acknowledge", response_model=AnomalyEvent, tags=["events"]
)
def acknowledge(
    event_id: str,
    body: AcknowledgeRequest | None = None,
    repo: Any = Depends(get_repository),
    bus: EventBus = Depends(get_event_bus),
    store: EvidenceStore = Depends(get_evidence_store),
) -> AnomalyEvent:
    reviewer = (body or AcknowledgeRequest()).reviewer
    try:
        event = repo.acknowledge_event(event_id, reviewer=reviewer)
    except (NotFoundError, InvalidTransitionError) as exc:
        raise _review_error(exc) from exc
    _publish(bus, "event.updated", event)
    return _with_evidence_urls(event, store)


@router.post("/events/{event_id}/resolve", response_model=AnomalyEvent, tags=["events"])
def resolve(
    event_id: str,
    body: ResolveRequest | None = None,
    repo: Any = Depends(get_repository),
    bus: EventBus = Depends(get_event_bus),
    store: EvidenceStore = Depends(get_evidence_store),
) -> AnomalyEvent:
    req = body or ResolveRequest()
    try:
        event = repo.resolve_event(
            event_id, reviewer=req.reviewer, decision=req.decision, note=req.note
        )
    except (NotFoundError, InvalidTransitionError) as exc:
        raise _review_error(exc) from exc
    _publish(bus, "event.updated", event)
    return _with_evidence_urls(event, store)


@router.post("/events/{event_id}/dismiss", response_model=AnomalyEvent, tags=["events"])
def dismiss(
    event_id: str,
    body: DismissRequest | None = None,
    repo: Any = Depends(get_repository),
    bus: EventBus = Depends(get_event_bus),
    store: EvidenceStore = Depends(get_evidence_store),
) -> AnomalyEvent:
    req = body or DismissRequest()
    try:
        event = repo.dismiss_event(event_id, reviewer=req.reviewer, note=req.note)
    except (NotFoundError, InvalidTransitionError) as exc:
        raise _review_error(exc) from exc
    _publish(bus, "event.updated", event)
    return _with_evidence_urls(event, store)
