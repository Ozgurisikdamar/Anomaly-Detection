"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Request

from storeguard_api.repository import InMemoryRepository


def get_repository(request: Request) -> InMemoryRepository:
    """Return the process-wide in-memory repository held on app state."""
    return request.app.state.repository  # type: ignore[no-any-return]
