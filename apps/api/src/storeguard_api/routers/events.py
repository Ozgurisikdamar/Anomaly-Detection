"""Anomaly event endpoints: ingest, list, detail, and human-review actions."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from storeguard_contracts import AnomalyEvent, EventStatus, ReviewDecision

from storeguard_api.deps import get_event_bus, get_repository
from storeguard_api.event_bus import EventBus
from storeguard_api.repository import NotFoundError

router = APIRouter()


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
) -> list[AnomalyEvent]:
    return repo.list_events(status=status, event_type=type, camera_id=camera_id)


@router.get("/events/{event_id}", response_model=AnomalyEvent, tags=["events"])
def get_event(event_id: str, repo: Any = Depends(get_repository)) -> AnomalyEvent:
    try:
        return repo.get_event(event_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc


@router.post(
    "/events/{event_id}/acknowledge", response_model=AnomalyEvent, tags=["events"]
)
def acknowledge(
    event_id: str,
    body: AcknowledgeRequest | None = None,
    repo: Any = Depends(get_repository),
    bus: EventBus = Depends(get_event_bus),
) -> AnomalyEvent:
    reviewer = (body or AcknowledgeRequest()).reviewer
    try:
        event = repo.acknowledge_event(event_id, reviewer=reviewer)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc
    _publish(bus, "event.updated", event)
    return event


@router.post("/events/{event_id}/resolve", response_model=AnomalyEvent, tags=["events"])
def resolve(
    event_id: str,
    body: ResolveRequest | None = None,
    repo: Any = Depends(get_repository),
    bus: EventBus = Depends(get_event_bus),
) -> AnomalyEvent:
    req = body or ResolveRequest()
    try:
        event = repo.resolve_event(
            event_id, reviewer=req.reviewer, decision=req.decision, note=req.note
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc
    _publish(bus, "event.updated", event)
    return event


@router.post("/events/{event_id}/dismiss", response_model=AnomalyEvent, tags=["events"])
def dismiss(
    event_id: str,
    body: DismissRequest | None = None,
    repo: Any = Depends(get_repository),
    bus: EventBus = Depends(get_event_bus),
) -> AnomalyEvent:
    req = body or DismissRequest()
    try:
        event = repo.dismiss_event(event_id, reviewer=req.reviewer, note=req.note)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc
    _publish(bus, "event.updated", event)
    return event
