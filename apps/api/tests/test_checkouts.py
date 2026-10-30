"""Checkout endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_checkouts_simulated(client: TestClient) -> None:
    resp = client.get("/api/v1/checkouts")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 2
    assert all(c["simulated"] is True for c in rows)
    # Any scan/scale signal present must be flagged simulated.
    for c in rows:
        for scan in c["scans"]:
            assert scan["simulated"] is True


def test_checkout_state_and_404(client: TestClient) -> None:
    ok = client.get("/api/v1/checkouts/term_01/state")
    assert ok.status_code == 200
    assert ok.json()["state"] == "BAGGING_OBSERVED"

    # Terminal with unavailable scanner feed has no scans (stays UNKNOWN).
    missing = client.get("/api/v1/checkouts/term_02/state")
    assert missing.status_code == 200
    assert missing.json()["scans"] == []

    assert client.get("/api/v1/checkouts/nope/state").status_code == 404


def test_cameras_and_status(client: TestClient) -> None:
    cams = client.get("/api/v1/cameras").json()
    assert len(cams) == 4
    status = client.get("/api/v1/cameras/cam_sco_02/status").json()
    assert status["state"] == "OFFLINE"
    assert status["simulated"] is True


def test_demo_scenario(client: TestClient) -> None:
    resp = client.post("/api/v1/demo/scenarios/sco-feed-missing/run")
    assert resp.status_code == 200
    body = resp.json()
    assert body["expected_event"] == "TRANSACTION_DATA_MISSING"
    assert body["simulated"] is True
    assert client.post("/api/v1/demo/scenarios/unknown/run").status_code == 404
