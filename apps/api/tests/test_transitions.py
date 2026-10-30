"""Server-authoritative review transitions: invalid/duplicate actions -> 409."""

from __future__ import annotations

from fastapi.testclient import TestClient
from storeguard_contracts import (
    AnomalyEvent,
    ConfidenceComponents,
    EventType,
    Severity,
)

from storeguard_api.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def _open_event() -> AnomalyEvent:
    return AnomalyEvent(
        event_type=EventType.SHELF_ITEM_REMOVED_UNRESOLVED,
        severity=Severity.REVIEW,
        store_id="store_demo_01",
        camera_id="cam_shelf_01",
        confidence=ConfidenceComponents(),
        explanation="transition test",
    )


def test_happy_path_acknowledge_then_resolve() -> None:
    c = _client()
    ev = _open_event()
    c.post("/api/v1/events", json=ev.model_dump(mode="json"))
    assert c.post(f"/api/v1/events/{ev.event_id}/acknowledge").status_code == 200
    r = c.post(f"/api/v1/events/{ev.event_id}/resolve")
    assert r.status_code == 200
    assert r.json()["status"] == "RESOLVED"


def test_resolve_twice_is_conflict() -> None:
    c = _client()
    ev = _open_event()
    c.post("/api/v1/events", json=ev.model_dump(mode="json"))
    assert c.post(f"/api/v1/events/{ev.event_id}/resolve").status_code == 200
    again = c.post(f"/api/v1/events/{ev.event_id}/resolve")
    assert again.status_code == 409


def test_acknowledge_after_resolve_is_conflict() -> None:
    c = _client()
    ev = _open_event()
    c.post("/api/v1/events", json=ev.model_dump(mode="json"))
    c.post(f"/api/v1/events/{ev.event_id}/resolve")
    assert c.post(f"/api/v1/events/{ev.event_id}/acknowledge").status_code == 409


def test_dismiss_after_dismiss_is_conflict() -> None:
    c = _client()
    ev = _open_event()
    c.post("/api/v1/events", json=ev.model_dump(mode="json"))
    assert c.post(f"/api/v1/events/{ev.event_id}/dismiss").status_code == 200
    assert c.post(f"/api/v1/events/{ev.event_id}/dismiss").status_code == 409
