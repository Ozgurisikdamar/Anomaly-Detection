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

    # CORS origins for the local web/mobile dev servers (localhost + 127.0.0.1).
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:19006",
        "http://127.0.0.1:19006",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ]
    # Extra production origins, comma-separated, via STOREGUARD_CORS_ORIGINS
    # (e.g. a deployed dashboard: "https://storeguard.netlify.app"). Merged with
    # the local defaults above by `allowed_origins`.
    cors_origins_extra: str = ""

    @property
    def allowed_origins(self) -> list[str]:
        """Local defaults + any comma-separated production origins from the env."""
        extra = [o.strip() for o in self.cors_origins_extra.split(",") if o.strip()]
        # De-dupe while preserving order.
        return list(dict.fromkeys([*self.cors_origins, *extra]))

    # Evidence media: where uploaded clips are stored on the API host, the HMAC
    # secret that signs short-lived evidence URLs, and the URL lifetime (seconds).
    # evidence_secret is a DEMO default — a real deployment MUST set
    # STOREGUARD_EVIDENCE_SECRET via the environment.
    evidence_dir: str = "runs/evidence"
    evidence_secret: str = "storeguard-demo-evidence-secret-change-me"
    evidence_url_ttl_s: int = 300


settings = Settings()
