# StoreGuard — Retail Loss Prevention Demo

A human-in-the-loop computer vision demo for shelf/aisle monitoring and
self-checkout transaction anomaly detection.

> **Status: Phase 4 (self-checkout MVP).** Phases 0–3 (baseline, vision
> workbench, camera supervision & zones, shelf event MVP) + a self-checkout
> terminal state machine with scan/scale reconciliation (scenarios 4–8 pass
> replay tests; a missing POS feed yields UNKNOWN, never a non-scan).
> Dashboard/API demo data is still **SIMULATED**. See the
> [Phase 0](docs/reports/PHASE_0_REPORT.md) · [1](docs/reports/PHASE_1_REPORT.md)
> · [2](docs/reports/PHASE_2_REPORT.md) · [3](docs/reports/PHASE_3_REPORT.md)
> · [4](docs/reports/PHASE_4_REPORT.md) reports.

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

## Vision workbench (Phase 1)
```bash
pip install -e "services/vision[ml]"   # ultralytics/opencv/psutil (CPU torch)
python -m storeguard_vision.cli benchmark --models yolo26n yolo11n --clip <imgs> --out runs
python -m storeguard_vision.cli annotate  --model yolo26n --clip <img|dir> --out runs
python -m storeguard_vision.cli track     --model yolo26n --image <img> --out runs
```

## Implementation
Follow the phase gates in the roadmap. Phases 0–4 are complete. The post-audit
work package (`docs/REPO_AUDIT_AND_NEXT_WORK.md`) is underway:
- **P0** (CI root cause + local green baseline — Actions is blocked owner-side on
  runner/billing) and **P1** (a real FILE DEMO vertical slice: video → YOLO26n +
  ByteTrack → zones → shelf FSM → event → API with PostgreSQL persistence → live
  web inbox + review) — see `docs/reports/REPO_AUDIT_AND_PHASE_5_REPORT.md`.
- **P2** (self-checkout visual↔POS correlation: a checkout FILE DEMO camera +
  SIMULATED POS feed correlated by terminal/session/UTC through the checkout FSM
  to an event in the web dashboard; a missing **or** delayed POS feed yields
  UNKNOWN, never a non-scan) — see `docs/reports/REPO_AUDIT_P2_REPORT.md`.
- **P3** (a real bounded, zone-masked evidence clip served via an authenticated
  short-lived URL and played in **web and mobile**; a mobile API client with
  real acknowledge/resolve/dismiss, polling realtime and source labels;
  **server-authoritative** review transitions that are audited and reject
  invalid/duplicate actions with 409) — see `docs/reports/REPO_AUDIT_P3_REPORT.md`.

Awaiting owner review before P4 (real RTSP camera validation + OpenVINO
benchmark). Shelf and checkout events come from a FILE DEMO vision pipeline;
POS/scanner/scale remain SIMULATED and labelled. Try it: `make demo` (shelf) or
`make demo-checkout` (self-checkout).
