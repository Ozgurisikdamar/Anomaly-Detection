"""Database layer.

Defined for later phases. Phase 0 serves in-memory SIMULATED data and does
**not** require a running database; nothing in the request path imports a live
session. The models here are mirrored by the initial Alembic migration under
``infra/migrations`` so the schema is reviewable now.
"""
