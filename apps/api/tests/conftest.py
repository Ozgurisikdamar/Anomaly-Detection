"""Pytest fixtures for the StoreGuard API tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from storeguard_api.main import create_app


@pytest.fixture()
def client() -> TestClient:
    # Fresh app (fresh in-memory seed) per test so review mutations are isolated.
    return TestClient(create_app())
