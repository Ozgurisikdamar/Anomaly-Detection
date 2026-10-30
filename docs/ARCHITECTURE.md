# StoreGuard architecture

> Phase 0 scaffold. This describes the intended architecture and what exists
> today. Vision/ML and real integrations are later phases.

## Overview
StoreGuard is a human-in-the-loop retail loss-prevention demo: shelf/aisle
monitoring and self-checkout transaction-anomaly review. It is a **CPU-first,
single-host modular monolith** (see ADR 0001, 0002).

Alerts describe **observable operational anomalies** — never theft, intent, or a
person. Every alert is a human-review task. Missing integration data is
**UNKNOWN**, never a violation.

## Logical flow (target)
```
RTSP/file/synthetic → Capture → Decode → Sample/ROI → Detector → Tracker
    → Zones/interactions → Domain event state machine ← POS/scan/scale (SIMULATED)
    → Event correlation → Event API → Web/mobile review queue
```

## Components (and Phase 0 status)
| Component | Path | Phase 0 status |
|---|---|---|
| Shared contracts | `packages/contracts` | ✅ Pydantic (source of truth) + TS mirror |
| API (FastAPI) | `apps/api` | ✅ health + seeded SIMULATED read/review endpoints |
| Web dashboard | `apps/web` | ✅ Next.js scaffold (Overview/Alerts/Cameras/Checkouts) |
| Mobile app | `apps/mobile` | ✅ Expo scaffold (login/inbox/detail/cameras) |
| Integrations | `services/integrations` | ✅ SIMULATED POS/scanner/scale generators |
| Vision | `services/vision` | ✅ Phase 1 workbench — capture adapters, YOLO detector/tracker, annotated output, measured YOLO26n vs YOLO11n CPU benchmark (`ml` extra) |
| Capture (supervision) | `services/capture` | ✅ Phase 2 — RTSP-capable supervised reader, reconnect/health/frame-age, bounded latest-frame buffer |
| Zones | `services/zones` | ✅ Phase 2 — polygon geometry, point-in-polygon, YAML loader, overlay |
| Shelf analytics | `services/shelf-analytics` | ✅ Phase 3 — occupancy baseline + unresolved-removal FSM, occlusion/offline suppression, person association, evidence + review |
| Checkout analytics | (later) | ⏳ Phase 4 |
| Persistence | `apps/api/src/.../db`, `infra/migrations` | ✅ models + initial Alembic migration (inert) |

## Data / persistence
Core entities: Store, Camera, CameraZone, CameraStreamStatus; FrameObservation,
Track (ephemeral, camera-local), ProductObservation; ShelfInteraction,
CheckoutSession, ScanEvent, ScaleEvent, TransactionEvent; AnomalyEvent,
EvidenceClip, ReviewDecision, AuditLog.

Phase 0 serves a deterministic in-memory **SIMULATED** seed so a clean clone
runs and tests pass without PostgreSQL. SQLAlchemy models and the initial
Alembic migration exist and mirror the core entities for later phases.

## Event contract
See `packages/contracts`. Every `AnomalyEvent` carries ids, UTC timestamps,
ephemeral track refs, evidence refs, model/tracker/rule versions, multidimensional
confidence, reason codes, missing-data flags, an explanation, and
`human_review_required=true`. No face identity or protected attributes are
stored.

## Privacy & safety
No face recognition, biometric identification, demographic inference, or
cross-camera re-identification. Short-lived camera-local pseudonymous track IDs.
No raw RTSP credentials exposed to clients. KVKK legal review required before any
real deployment in Türkiye. See roadmap section 13.

## Later production scale (not built now)
Per-camera/partition workers; Redis Streams/Kafka only if measured; GPU nodes and
NVIDIA DeepStream for multi-stream batching; encrypted object storage with
lifecycle retention; metrics/logs/traces and orchestration. See ADR 0001.
