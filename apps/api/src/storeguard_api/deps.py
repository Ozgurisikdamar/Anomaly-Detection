"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from storeguard_api.event_bus import EventBus


def get_repository(request: Request) -> Any:
    """Return the process-wide repository (in-memory seed or SQL-backed)."""
    return request.app.state.repository


def get_event_bus(request: Request) -> EventBus:
    """Return the process-wide realtime event bus."""
    return request.app.state.event_bus  # type: ignore[no-any-return]
