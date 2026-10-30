"""Anomaly event endpoints: list, detail, and human-review actions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from storeguard_contracts import AnomalyEvent, EventStatus, ReviewDecision

from storeguard_api.deps import get_repository
from storeguard_api.repository import InMemoryRepository, NotFoundError

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


@router.get("/events", response_model=list[AnomalyEvent], tags=["events"])
def list_events(
    status: EventStatus | None = None,
    type: str | None = None,
    camera_id: str | None = None,
    repo: InMemoryRepository = Depends(get_repository),
) -> list[AnomalyEvent]:
    return repo.list_events(status=status, event_type=type, camera_id=camera_id)


@router.get("/events/{event_id}", response_model=AnomalyEvent, tags=["events"])
def get_event(
    event_id: str,
    repo: InMemoryRepository = Depends(get_repository),
) -> AnomalyEvent:
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
    repo: InMemoryRepository = Depends(get_repository),
) -> AnomalyEvent:
    reviewer = (body or AcknowledgeRequest()).reviewer
    try:
        return repo.acknowledge_event(event_id, reviewer=reviewer)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc


@router.post("/events/{event_id}/resolve", response_model=AnomalyEvent, tags=["events"])
def resolve(
    event_id: str,
    body: ResolveRequest | None = None,
    repo: InMemoryRepository = Depends(get_repository),
) -> AnomalyEvent:
    req = body or ResolveRequest()
    try:
        return repo.resolve_event(
            event_id, reviewer=req.reviewer, decision=req.decision, note=req.note
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc


@router.post("/events/{event_id}/dismiss", response_model=AnomalyEvent, tags=["events"])
def dismiss(
    event_id: str,
    body: DismissRequest | None = None,
    repo: InMemoryRepository = Depends(get_repository),
) -> AnomalyEvent:
    req = body or DismissRequest()
    try:
        return repo.dismiss_event(event_id, reviewer=req.reviewer, note=req.note)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc
