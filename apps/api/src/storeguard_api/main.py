"""StoreGuard API application factory.

Two repository modes:
- ``use_in_memory_seed=True`` (default): deterministic SIMULATED seed, no DB —
  for offline demo and tests.
- ``use_in_memory_seed=False`` + ``database_url``: PostgreSQL-backed repository
  so events, review decisions and the audit log persist across restarts.

A small in-process event bus powers the SSE realtime stream.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from storeguard_api import __version__
from storeguard_api.event_bus import EventBus
from storeguard_api.logging_config import configure_logging
from storeguard_api.routers import checkouts, demo, events, health, stores, stream
from storeguard_api.seed import build_repository, build_seed_data
from storeguard_api.settings import settings

API_PREFIX = "/api/v1"
logger = logging.getLogger("storeguard_api")

DESCRIPTION = (
    "StoreGuard — retail loss-prevention demo API.\n\n"
    "Non-vision camera/POS/scanner/scale data is SIMULATED and labelled. Events "
    "describe observable operational anomalies and always require human review; "
    "missing integration data is UNKNOWN, never a violation."
)


def build_repository_from_settings() -> Any:
    """Pick the repository implementation from settings."""
    if settings.use_in_memory_seed:
        logger.info("repository: in-memory SIMULATED seed")
        return build_repository()

    from sqlalchemy import create_engine

    from storeguard_api.db.sql_repository import SqlAlchemyRepository

    logger.info("repository: SQLAlchemy (%s)", settings.database_url.split("@")[-1])
    seed = build_seed_data()
    engine = create_engine(settings.database_url, future=True)
    repo = SqlAlchemyRepository(engine, seed)
    repo.ensure_schema()
    repo.seed_events_if_empty(seed.events)
    return repo


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="StoreGuard API", version=__version__, description=DESCRIPTION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.repository = build_repository_from_settings()
    app.state.event_bus = EventBus()

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(stores.router, prefix=API_PREFIX)
    app.include_router(events.router, prefix=API_PREFIX)
    app.include_router(checkouts.router, prefix=API_PREFIX)
    app.include_router(demo.router, prefix=API_PREFIX)
    app.include_router(stream.router, prefix=API_PREFIX)

    @app.get("/", tags=["health"])
    def root() -> dict[str, str]:
        if settings.use_in_memory_seed:
            persistence = "memory"
        else:
            persistence = settings.database_url.split("://", 1)[0].split("+")[0]
        return {
            "service": "storeguard-api",
            "persistence": persistence,
            "docs": "/docs",
            "health": f"{API_PREFIX}/health",
            "stream": f"{API_PREFIX}/stream/events",
        }

    return app


app = create_app()
