"""SqlAlchemyRepository persistence tests (SQLite stands in for PostgreSQL).

Proves review decisions and the audit log survive a 'restart' (a fresh
repository instance on the same database), which is the P1 persistence
acceptance without requiring a running Postgres in CI.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from storeguard_contracts import EventStatus, ReviewDecision

from storeguard_api.db.sql_repository import SqlAlchemyRepository
from storeguard_api.seed import build_seed_data


def _repo(db_path: Path) -> SqlAlchemyRepository:
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    seed = build_seed_data()
    repo = SqlAlchemyRepository(engine, seed)
    repo.ensure_schema()
    repo.seed_events_if_empty(seed.events)
    return repo


def test_seed_and_list(tmp_path: Path) -> None:
    repo = _repo(tmp_path / "a.db")
    assert len(repo.list_events()) >= 6


def test_resolve_persists_across_restart(tmp_path: Path) -> None:
    db = tmp_path / "b.db"
    repo = _repo(db)
    eid = repo.list_events()[0].event_id
    repo.resolve_event(
        eid,
        reviewer="qa",
        decision=ReviewDecision.CONFIRMED_OPERATIONAL_ANOMALY,
        note="n",
    )

    # Fresh instance on the same DB == process restart.
    repo2 = _repo(db)
    got = repo2.get_event(eid)
    assert got.status == EventStatus.RESOLVED
    assert got.review is not None and got.review.reviewer == "qa"
    assert any(a["action"].startswith("resolve") for a in repo2.list_audit())


def test_add_event_persists(tmp_path: Path) -> None:
    from storeguard_contracts import AnomalyEvent, EventType

    db = tmp_path / "c.db"
    repo = _repo(db)
    ev = AnomalyEvent(
        store_id="store_demo_01",
        camera_id="cam_shelf_01",
        event_type=EventType.SHELF_ITEM_REMOVED_UNRESOLVED,
    )
    repo.add_event(ev)
    assert _repo(db).get_event(ev.event_id).event_id == ev.event_id
