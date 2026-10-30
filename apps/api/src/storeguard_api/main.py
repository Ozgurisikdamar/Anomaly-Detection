"""StoreGuard API application factory (Phase 0)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from storeguard_api import __version__
from storeguard_api.logging_config import configure_logging
from storeguard_api.routers import checkouts, demo, events, health, stores
from storeguard_api.seed import build_repository
from storeguard_api.settings import settings

API_PREFIX = "/api/v1"

DESCRIPTION = (
    "StoreGuard — retail loss-prevention demo API (Phase 0 scaffold).\n\n"
    "All data served here is SIMULATED. No camera, POS, scanner or scale is "
    "connected. Events describe observable operational anomalies and always "
    "require human review; missing integration data is UNKNOWN, never a "
    "violation."
)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="StoreGuard API",
        version=__version__,
        description=DESCRIPTION,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Phase 0: process-wide in-memory SIMULATED repository.
    app.state.repository = build_repository()

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(stores.router, prefix=API_PREFIX)
    app.include_router(events.router, prefix=API_PREFIX)
    app.include_router(checkouts.router, prefix=API_PREFIX)
    app.include_router(demo.router, prefix=API_PREFIX)

    @app.get("/", tags=["health"])
    def root() -> dict[str, str]:
        return {
            "service": "storeguard-api",
            "phase": "phase-0",
            "docs": "/docs",
            "health": f"{API_PREFIX}/health",
        }

    return app


app = create_app()
