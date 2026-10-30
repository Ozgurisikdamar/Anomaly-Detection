"""Evidence upload + authenticated short-lived URL serving."""

from __future__ import annotations

import time
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from storeguard_contracts import (
    AnomalyEvent,
    ConfidenceComponents,
    EventType,
    EvidenceRef,
    Severity,
)

from storeguard_api.evidence import EvidenceStore
from storeguard_api.main import create_app

GIF_BYTES = (  # a tiny valid 1x1 GIF
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def _event_with_evidence(evidence_id: str) -> AnomalyEvent:
    return AnomalyEvent(
        event_type=EventType.SHELF_ITEM_REMOVED_UNRESOLVED,
        severity=Severity.REVIEW,
        store_id="store_demo_01",
        camera_id="cam_shelf_01",
        confidence=ConfidenceComponents(),
        explanation="evidence test",
        evidence=[EvidenceRef(evidence_id=evidence_id, kind="clip", available=True)],
    )


@pytest.fixture
def client(tmp_path):
    app = create_app()
    # Point the evidence store at an isolated temp dir for the test.
    app.state.evidence_store = EvidenceStore(
        tmp_path / "evidence", "test-secret", ttl_s=300
    )
    return TestClient(app)


def test_upload_then_serve_via_signed_url(client: TestClient) -> None:
    ev = _event_with_evidence("ev_test_serve")
    event_id = ev.event_id
    assert (
        client.post("/api/v1/events", json=ev.model_dump(mode="json")).status_code
        == 201
    )

    # Before upload the bytes do not exist: available must be False, no url.
    pre = client.get(f"/api/v1/events/{event_id}").json()
    assert pre["evidence"][0]["available"] is False
    assert pre["evidence"][0]["url"] is None

    up = client.post(
        f"/api/v1/events/{event_id}/evidence",
        files={"file": ("clip.gif", GIF_BYTES, "image/gif")},
    )
    assert up.status_code == 201

    # Now the read mints a short-lived signed URL and reports available.
    got = client.get(f"/api/v1/events/{event_id}").json()
    ref = got["evidence"][0]
    assert ref["available"] is True
    assert ref["url"] and ref["url"].startswith("/api/v1/evidence/")
    assert ref["expires_at"]

    served = client.get(ref["url"])
    assert served.status_code == 200
    assert served.headers["content-type"] == "image/gif"
    assert served.content == GIF_BYTES


def test_bad_signature_is_rejected(client: TestClient) -> None:
    ev = _event_with_evidence("ev_test_badsig")
    client.post("/api/v1/events", json=ev.model_dump(mode="json"))
    client.post(
        f"/api/v1/events/{ev.event_id}/evidence",
        files={"file": ("clip.gif", GIF_BYTES, "image/gif")},
    )
    url = client.get(f"/api/v1/events/{ev.event_id}").json()["evidence"][0]["url"]
    q = parse_qs(urlparse(url).query)
    tampered = f"/api/v1/evidence/ev_test_badsig?exp={q['exp'][0]}&sig=deadbeef"
    assert client.get(tampered).status_code == 403


def test_expired_url_is_rejected(client: TestClient) -> None:
    ev = _event_with_evidence("ev_test_expired")
    client.post("/api/v1/events", json=ev.model_dump(mode="json"))
    client.post(
        f"/api/v1/events/{ev.event_id}/evidence",
        files={"file": ("clip.gif", GIF_BYTES, "image/gif")},
    )
    store: EvidenceStore = client.app.state.evidence_store
    # Mint a token that already expired (now far in the past).
    url, _ = store.sign_url("ev_test_expired", now=time.time() - 10_000)
    assert client.get(url).status_code == 403


def test_upload_requires_known_event(client: TestClient) -> None:
    r = client.post(
        "/api/v1/events/evt_does_not_exist/evidence",
        files={"file": ("clip.gif", GIF_BYTES, "image/gif")},
    )
    assert r.status_code == 404
