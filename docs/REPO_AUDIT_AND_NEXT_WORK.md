# StoreGuard — Repository Audit & Next Work Package
> Audit date: 2026-10-30
> Audited ref: feat/storeguard-demo-foundation
> Audited HEAD: babfabb0099ad92e9da9ae9645503dbf25e40067
> Purpose: implementation backlog after Phases 0–4; this document supersedes any instruction to restart Phase 0.

## 1. Executive assessment

Phases 0–4 have substantial implementation on the feature branch: backend/API scaffold, web dashboard, Expo mobile scaffold, shared contracts, CPU YOLO benchmark workbench, capture supervision, zone geometry, shelf event state machine, and self-checkout reconciliation state machine. Phase reports document 53 passing backend/service tests by Phase 4 and local lint/typecheck/build evidence.

However, this is **not yet an end-to-end working camera product or demo**. The main missing link is orchestration: real frame observations do not flow through detector -> zones -> shelf/checkout state machines -> persistent API -> web/mobile review surfaces. The API still serves an in-memory SIMULATED seed. POS/scanner/scale are simulated. No real RTSP camera was exercised. The web and mobile clients still have placeholder/local-only review paths and no real-time event delivery.

Do not rebuild the repository or repeat Phases 0–4. Continue from the current feature branch and preserve the existing work.

## 2. Repository state inspected

- Default branch: `main`; the working implementation is on `feat/storeguard-demo-foundation`.
- Audited feature branch HEAD: `babfabb0099ad92e9da9ae9645503dbf25e40067`.
- `main` still points to the earlier documentation-only history; do not merge automatically.
- Feature branch contains apps/api, apps/web, apps/mobile, packages/contracts, services/vision, capture, zones, shelf-analytics, checkout-analytics, integrations, migrations, configs, tests, CI and phase reports.
- Latest README says Phases 0–4 complete and awaits Phase 5.
- Phase 0 report is historical and correctly describes the initial scaffold; later Phase 1–4 reports supersede its status for subsequent work.

## 3. Implemented work — acknowledge, do not rewrite

| Area | Existing implementation | Current limitation |
|---|---|---|
| Backend | FastAPI routers, contracts, review endpoints, SQLAlchemy models, Alembic migration | API currently constructs an in-memory seed; DB path is not wired into request lifecycle |
| Vision | YOLO26n/YOLO11n CPU benchmark, detector wrapper, file/synthetic sources, annotation and tracking CLI | No live multi-camera pipeline; no labelled retail SKU dataset; OpenVINO/ONNX export candidates not benchmarked |
| Capture | supervised reader, latest-frame buffer, reconnect/backoff, health metrics, RTSP adapter | RTSP code path not tested against an actual camera; API/dashboard are not wired to it |
| Zones | normalized polygon geometry and overlays | Zone observations are not yet fed from live detections into analytics |
| Shelf analytics | tested shelf baseline/removal/occlusion/replenishment FSM | Inputs are manually supplied observations; detector-to-zone-to-FSM pipeline is absent; evidence is a montage, not a real synchronized clip |
| Checkout analytics | per-terminal FSM, simulated POS/scanner/scale events, scan/scale reconciliation | Camera-derived item observations are not connected; all transaction feeds are simulated |
| Web | Next.js overview, alerts, event detail, cameras, checkout views | seeded/sample data; review buttons not fully API-wired; no event WebSocket/SSE; no real camera playback/overlay stream |
| Mobile | Expo screens, inbox/detail/camera status | review actions update local state only; API client currently reads events only; no authenticated action API or push/realtime |
| Persistence | SQLAlchemy models and migration | no end-to-end PostgreSQL repository implementation, migrations not exercised against live Postgres in report |

## 4. CI finding — must be investigated first

The latest observed GitHub Actions run for HEAD `babfabb0099ad92e9da9ae9645503dbf25e40067` is marked **failure**. Its three jobs (Backend, Web, Mobile) all failed within roughly 2–3 seconds and the job summaries returned no steps. A subsequent attempt to retrieve job logs returned a GitHub log-blob 404, so the exact cause is **not established**.

Do not assume application tests failed. First inspect the run/check details and workflow configuration, determine whether this is workflow dispatch/runner/permissions/configuration or actual build failure, and produce a reproducible local CI run. Fix the root cause and rerun Actions. Record evidence and URLs in the report.

Observed run: https://github.com/Ozgurisikdamar/Anomaly-Detection/actions/runs/41047025562

## 5. Priority order

### P0 — Reconcile repository reports and establish a green baseline
1. Verify current branch/head and working tree; do not alter main.
2. Inspect all workflow jobs/check-runs and identify why Actions fails before steps appear.
3. Run the exact CI commands locally: ruff, black --check, mypy, pytest, Alembic offline SQL, web lint/typecheck/build, mobile typecheck/export, compose config.
4. Fix only proven issues. Ensure GitHub Actions runs on feature branch and PRs; pin or cache dependencies only where useful.
5. Update README status and phase report references if stale. Preserve phase reports as historical evidence; add a new audit/implementation report.
Acceptance: all local checks pass and GitHub Actions reports green for the new commit.

### P1 — Complete the real vertical slice: video → event → API → dashboard
1. Introduce a `PipelineCoordinator` / application service that composes `SupervisedCamera`, `YoloDetector`, zone mapping, `ShelfMonitor`, and event publication.
2. Add a deterministic `file` source mode that runs without RTSP and can be demonstrated on a clean machine. RTSP remains optional and uses server-side secrets.
3. Add an observation adapter mapping detector boxes/tracks to normalized zone observations. Explicitly define the product-presence input: generic COCO objects are not SKU detections. For the demo, use a clearly labelled demo product detector/config or synthetic product observations; never misrepresent COCO class detections as SKU recognition.
4. Add per-camera isolated detector/tracker state. Current detector wrapper owns one persistent Ultralytics tracker; do not share one instance across camera streams.
5. Feed shelf FSM with camera health, occlusion, product occupancy, interaction and approved replenishment observations. Persist resulting events and evidence references.
6. Add event publisher (in-process async queue initially) and WebSocket or SSE endpoint; do not introduce Kafka for this demo.
7. Wire web camera tiles to real capture status when configured, file/demo playback when not; display source labels LIVE / FILE DEMO / SIMULATED distinctly.
8. Wire acknowledge/resolve/dismiss buttons to API; require reviewer/reason and show server response/errors.
9. Replace in-memory-only production path with a repository interface backed by PostgreSQL for events, review decisions and audit log. Keep deterministic seed mode explicitly for offline demo.
Acceptance: one command starts API + DB + file-demo pipeline; an offline sample clip produces a shelf review event visible in the web inbox; reviewer action persists after API restart; tests cover pipeline and API integration.

### P2 — Checkout visual/event correlation
1. Create camera observation adapter for scan-area, bagging/scale-area, cart/basket and exit zones.
2. Correlate item observation and scanner/POS/scale messages by terminal_id, session_id and synchronized UTC timestamps.
3. Keep simulated adapter for demo; add adapter interfaces and contract validation for future real POS integration.
4. Enforce feed health and lateness windows: if scanner/POS is unavailable or delayed, event must be UNKNOWN / TRANSACTION_DATA_MISSING, never ITEM_PLACED_NOT_SCANNED.
5. Do not claim scale mismatch without real or explicitly simulated scale telemetry.
6. Add replay tests for normal, non-scan with healthy feed, missing feed, delayed feed, void, attendant override, multiple items and session reset.
Acceptance: one self-checkout demo scenario runs from video/file observations + simulated POS feed through checkout FSM to an event visible in web dashboard; missing POS feed cannot create non-scan alert.

### P3 — Evidence, review, mobile
1. Replace evidence montage placeholder with a real bounded pre/post-event clip buffer from file/RTSP source, timestamped and linked to event; redact/mask outside configured zones where required.
2. Serve evidence via authenticated short-lived API URL; never expose raw filesystem paths or RTSP credentials.
3. Implement mobile API client for list/detail/acknowledge/resolve/dismiss, error handling and source labels.
4. Implement in-app realtime refresh; push notifications are optional after demo. No push is required to pass first mobile milestone.
5. Ensure web and mobile review decisions are server-authoritative and audited; prevent duplicate or invalid state transitions.
Acceptance: event evidence plays in web and mobile; review action from either client is reflected in the other after refresh; audit record is persisted.

### P4 — Actual camera validation and deployment demo
1. Test RTSP against a camera the owner is authorized to access; document codec, resolution, FPS, network, reconnect and decode behavior. If no camera is available, mark this acceptance blocked and retain file-demo as valid fallback.
2. Measure CPU/RAM, detector latency p50/p95, frame age, dropped frames, effective FPS and number of streams on the actual target machine.
3. Benchmark YOLO26n vs YOLO11n on representative retail clips, not only bus/zidane images. Do not select production model without labelled data and quality metrics.
4. Add OpenVINO/ONNX export and benchmark only after baseline is stable; check model runtime compatibility and model licensing.
5. Provide Docker Compose quickstart, seeded sample mode, demo scenario controls and screenshots/screen recording.
6. Document KVKK review, retention, role-based access, TLS, secret management, network segmentation and audit trail before any real store deployment.
Acceptance: clean-clone demo walkthrough with documented prerequisites, one shelf scenario, one checkout scenario, web and mobile review, measured performance and known limitations.

## 6. Critical technical corrections / risks

- **YOLO26n is a candidate, not a retail SKU solution.** The report benchmarked generic public sample images (bus/zidane), so the ~20 FPS result does not establish retail product accuracy or real-camera performance. The official model docs describe COCO-pretrained generic classes; custom retail data is required. See https://docs.ultralytics.com/models/yolo26.
- **YOLO26n vs YOLO11n benchmark:** reported 48-frame single-machine result is preliminary. Expand to longer warm runs, representative clips, repeated trials and labelled evaluation. Record CPU model/core count, Python/PyTorch/OpenCV versions, thread settings, input resolution and power mode.
- **OpenVINO is worth prioritizing on Intel CPU hardware**, but only after measuring on the owner's exact CPU. Export/compile/cache must be part of repeatable benchmark; don't assume a vendor headline applies to this machine.
- **Track IDs are camera-local and ephemeral.** A detector instance with `persist=True` must not be shared across camera sources. No person re-identification.
- **Shelf baseline semantics:** don't automatically decrement stock baseline on disappearance; only approved replenishment/adjustment or explicit state policy may change it. Occlusion/offline => UNKNOWN.
- **Checkout matching:** scan-to-bag timing and scale tolerance must be configurable per terminal/SKU and robust to delayed events, voids, produce lookup, attendant override, multiple quantities and session reset.
- **API security:** current reviewer defaults such as demo reviewer are not production authentication. Implement mock auth only for local demo and document it; never expose unauthenticated internet deployment.
- **CORS and mobile networking:** localhost on a physical phone is the phone itself, not the developer host. Document LAN host configuration and secure API base settings.
- **Next.js version/scripts:** verify installed Next.js version supports the configured lint command; CI is currently failing and must be diagnosed rather than ignored.
- **Data privacy:** no real identifiable CCTV data in repository or screenshots without lawful basis and approval; no face recognition or audio.

## 7. Required test matrix

| Test | Expected result |
|---|---|
| File clip pipeline | frames -> detections -> zone observations -> shelf FSM -> event |
| Camera disconnect during absence | no removal accusation; UNKNOWN/occlusion/integration state |
| Reconnect | frame age resets, reconnect counter increments, pipeline resumes without stale track reuse |
| Two camera sources | tracker IDs/state isolated per camera |
| Shelf removal | one deduplicated unresolved event after threshold |
| Shelf occlusion | no removal event |
| Approved replenishment | baseline updates; no anomaly |
| Checkout scan + bagging + payment | no alert |
| Checkout bagging without scan + healthy POS | review alert |
| Checkout scanner feed unavailable/delayed | UNKNOWN only; zero non-scan alerts |
| Scale feed absent | no scale mismatch alert |
| Void/attendant override | no false non-scan alert |
| API review action | state and audit persist in PostgreSQL |
| Web review | server action succeeds/fails visibly |
| Mobile review | same server-authoritative state as web |
| Evidence access | authenticated, expiring URL; no raw path/RTSP secret |

## 8. Claude execution contract

Work from `feat/storeguard-demo-foundation` at the current remote HEAD. Do not restart Phase 0, do not rewrite history, do not merge to main, and do not create fake integrations.

Implement P0 first, then P1. Stop and report before P2 unless P1 is fully green. The owner wants a working demo, so prioritize a complete file-based vertical slice over additional disconnected abstractions.

At each checkpoint create `docs/reports/REPO_AUDIT_AND_PHASE_5_REPORT.md` (or a clearly versioned follow-up) with changed files, commit SHAs, exact commands and outputs, CI run URL, screenshots, measured performance, limitations and remaining work.

Do not report 'complete' unless acceptance criteria are demonstrated. Clearly distinguish REAL RTSP, FILE DEMO and SIMULATED POS/scale signals.

## 9. Definition of demo-ready

A clean clone can launch the system with one documented command; web dashboard is usable; mobile app can view and review events; a shelf clip generates a real pipeline event; self-checkout scenario reconciles visual observations with explicitly simulated scanner/POS/scale messages; human review persists; camera health and inference metrics are visible; no unsupported theft accusation is produced; CI is green.