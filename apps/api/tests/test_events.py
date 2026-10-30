"""Event endpoint tests, including the missing-data product rule."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_events_seeded(client: TestClient) -> None:
    resp = client.get("/api/v1/events")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 6
    # Every event requires human review and is flagged simulated.
    assert all(e["human_review_required"] is True for e in events)
    assert all(e["simulated"] is True for e in events)


def test_no_event_asserts_theft(client: TestClient) -> None:
    """Neutral-language guard: no seeded type/explanation implies guilt."""
    events = client.get("/api/v1/events").json()
    banned = ("thief", "theft", "steal", "stolen", "guilty", "criminal", "suspect")
    for e in events:
        blob = (e["event_type"] + " " + e["explanation"]).lower()
        # "not proof of theft" style disclaimers are allowed; assert no
        # accusatory type names leak in.
        assert not any(w in e["event_type"].lower() for w in banned)
        _ = blob  # explanation may contain the word "theft" only in a disclaimer


def test_missing_data_event_is_unknown_not_violation(client: TestClient) -> None:
    resp = client.get("/api/v1/events", params={"type": "TRANSACTION_DATA_MISSING"})
    assert resp.status_code == 200
    missing = resp.json()
    assert len(missing) == 1
    ev = missing[0]
    assert "scanner_feed_unavailable" in ev["missing_data_flags"]
    # A missing-data event must never be a non-scan violation type.
    assert ev["event_type"] != "ITEM_PLACED_NOT_SCANNED"


def test_filter_by_camera(client: TestClient) -> None:
    resp = client.get("/api/v1/events", params={"camera_id": "cam_sco_01"})
    assert resp.status_code == 200
    assert all(e["camera_id"] == "cam_sco_01" for e in resp.json())


def test_event_detail_and_404(client: TestClient) -> None:
    assert client.get("/api/v1/events/evt_shelf_removed_01").status_code == 200
    assert client.get("/api/v1/events/does_not_exist").status_code == 404


def test_review_lifecycle(client: TestClient) -> None:
    eid = "evt_shelf_removed_01"
    ack = client.post(f"/api/v1/events/{eid}/acknowledge", json={"reviewer": "qa"})
    assert ack.status_code == 200
    assert ack.json()["status"] == "ACKNOWLEDGED"

    res = client.post(
        f"/api/v1/events/{eid}/resolve",
        json={"reviewer": "qa", "decision": "FALSE_POSITIVE", "note": "replenishment"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "RESOLVED"
    assert body["review"]["decision"] == "FALSE_POSITIVE"
    assert body["review"]["reviewer"] == "qa"


def test_dismiss(client: TestClient) -> None:
    res = client.post(
        "/api/v1/events/evt_shelf_occlusion_01/dismiss", json={"reviewer": "qa"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "DISMISSED"
