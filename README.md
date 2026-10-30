# StoreGuard — Retail Loss Prevention Demo

A human-in-the-loop computer vision demo for shelf/aisle monitoring and
self-checkout transaction anomaly detection.

> **Status: Phase 0 (engineering baseline) scaffold.** No vision/ML runs yet and
> all data is **SIMULATED**. See the [Phase 0 report](docs/reports/PHASE_0_REPORT.md).

## Start here
- [Demo implementation roadmap](docs/STOREGUARD_DEMO_ROADMAP.md) — source of truth
- [Architecture](docs/ARCHITECTURE.md) and [ADRs](docs/ADR/)
- [Phase 0 report](docs/reports/PHASE_0_REPORT.md)

## Product principles
- Detect observable operational anomalies; do not infer criminal intent or label people.
- Shelf disappearance is unresolved until corroborated; occlusion and replenishment must be handled.
- Self-checkout non-scan detection requires synchronized camera + scanner/POS data. Scale mismatch requires scale telemetry.
- Missing integration data means UNKNOWN, never a violation.
- Every event requires human review.
- Privacy by design: no face recognition, no biometric identification, pseudonymous camera-local tracks, controlled retention.

## Planned demo
- CPU-first local inference with RTSP and offline file/synthetic sources.
- YOLO26n benchmark baseline vs YOLO11n, tracking benchmark and measured selection.
- Web dashboard and React Native mobile client.
- Simulated scanner/POS/scale feed clearly labelled as simulated until real integrations are provided.

## Repository layout
```
apps/api/                 FastAPI backend (health + SIMULATED read endpoints)
apps/web/                 Next.js dashboard
apps/mobile/              Expo / React Native app
packages/contracts/       shared contracts — Pydantic (source of truth) + TS mirror
services/vision/          CPU benchmark methodology + harness stub (no model run)
services/integrations/    SIMULATED POS/scanner/scale generators
infra/docker/             Dockerfiles
infra/migrations/         Alembic env + initial migration
configs/                  cameras / zones / rules example YAML
docs/                     roadmap, architecture, ADRs, reports
```

## Quickstart (Phase 0)
Requirements: Python 3.11+, Node 22+.

```bash
make setup          # venv + install contracts/integrations/vision/api (editable)
make test           # backend tests (no database required)
make lint typecheck # ruff/next-lint + mypy/tsc
make dev-api        # API at http://localhost:8000 (docs at /docs)
```

```bash
make setup-web && make dev-web        # dashboard at http://localhost:3000
make setup-mobile && make dev-mobile  # Expo dev server (or `make export-mobile-web`)
```

Docker: `docker compose up --build` (api + web + postgres). The API runs from the
in-memory SIMULATED seed in Phase 0; PostgreSQL is included for later phases.

## Implementation
Follow the phase gates in the roadmap. Claude Code implemented **Phase 0 only**
and is awaiting product-owner review before Phase 1. No models were run; all
camera/POS/scale data is clearly labelled SIMULATED.
