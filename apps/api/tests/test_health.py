"""Health and root endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "storeguard-api"
    assert body["phase"] == "phase-0"
    assert body["simulated_data"] is True


def test_root(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "storeguard-api"


def test_openapi_available(client: TestClient) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
