"""API ingest + SSE + DB persistence integration test.

Builds the app with a SQLite-backed SqlAlchemyRepository (stands in for
PostgreSQL), ingests a pipeline-style event, lists it, resolves it via the API,
and verifies the decision persisted in the database.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from storeguard_contracts import AnomalyEvent, EventType

from storeguard_api.db.sql_repository import SqlAlchemyRepository
from storeguard_api.main import create_app
from storeguard_api.seed import build_seed_data


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    return tmp_path / "api.db"


@pytest.fixture()
def db_client(db: Path) -> TestClient:
    app = create_app()  # default in-memory
    engine = create_engine(f"sqlite:///{db}", future=True)
    seed = build_seed_data()
    repo = SqlAlchemyRepository(engine, seed)
    repo.ensure_schema()
    repo.seed_events_if_empty(seed.events)
    app.state.repository = repo  # swap to DB-backed repo for this test
    return TestClient(app)


def _pipeline_event() -> dict:
    return AnomalyEvent(
        event_id="evt_pipeline_test_01",
        store_id="store_demo_01",
        camera_id="cam_shelf_01",
        event_type=EventType.SHELF_ITEM_REMOVED_UNRESOLVED,
    ).model_dump(mode="json")


def test_ingest_list_resolve_persist(db_client: TestClient, db: Path) -> None:
    # Ingest (pipeline -> API).
    resp = db_client.post("/api/v1/events", json=_pipeline_event())
    assert resp.status_code == 201

    listed = db_client.get("/api/v1/events").json()
    assert any(e["event_id"] == "evt_pipeline_test_01" for e in listed)

    # Review via API, with reviewer + reason.
    res = db_client.post(
        "/api/v1/events/evt_pipeline_test_01/resolve",
        json={
            "reviewer": "web",
            "decision": "CONFIRMED_OPERATIONAL_ANOMALY",
            "note": "ok",
        },
    )
    assert res.status_code == 200 and res.json()["status"] == "RESOLVED"

    # Persisted independently of the app instance (restart proof).
    engine = create_engine(f"sqlite:///{db}", future=True)
    repo2 = SqlAlchemyRepository(engine, build_seed_data())
    got = repo2.get_event("evt_pipeline_test_01")
    assert got.status.value == "RESOLVED"
    assert got.review is not None and got.review.reviewer == "web"


def test_stream_endpoint_exists(db_client: TestClient) -> None:
    # The SSE route is registered (HEAD-ish check without consuming the stream).
    # A GET would block on the stream, so just confirm the OpenAPI lists it.
    spec = db_client.get("/openapi.json").json()
    assert "/api/v1/stream/events" in spec["paths"]
