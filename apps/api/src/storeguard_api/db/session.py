"""SQLAlchemy engine/session factory (unused in Phase 0 request path).

Provided for later phases and for Alembic. Importing this module does not open
a connection; the engine is created lazily.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from storeguard_api.settings import settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(settings.database_url, future=True)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
