"""Application settings (environment-driven, no secrets committed)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STOREGUARD_", env_file=".env", extra="ignore"
    )

    service_name: str = "storeguard-api"
    environment: str = "local"

    # Phase 0 serves deterministic in-memory SIMULATED data; no DB is required.
    use_in_memory_seed: bool = True

    # Present for later phases; unused while use_in_memory_seed is True.
    database_url: str = (
        "postgresql+psycopg://storeguard:storeguard@localhost:5432/storeguard"
    )

    # CORS origins for the local web/mobile dev servers.
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:19006",
        "http://localhost:8081",
    ]


settings = Settings()
