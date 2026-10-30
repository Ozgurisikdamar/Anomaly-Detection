# StoreGuard — Demo Implementation Roadmap
> Product: retail computer-vision loss-prevention and checkout-anomaly demo
> Status: planning baseline, 2026-10-30

## 0. Product definition and non-goals

Build a human-in-the-loop retail vision system with:
1. Aisle/shelf cameras: detect and track visible products and people; associate product interaction with shelf zones; flag unresolved item disappearance or occupancy anomalies.
2. Self-checkout cameras: track items through scan and bagging zones and compare visual observations with scanner/POS/scale signals where integrations exist.
3. Web dashboard and mobile demo: camera tiles, overlays, event timeline, alert details, review/resolve workflow, camera health and metrics.

Alerts describe observable anomalies, not criminal intent. Never label a person a thief, infer guilt, automatically detain or penalize anyone, or trigger law-enforcement action. Every alert requires human review.

A shelf item leaving the camera view is not proof of theft: it may be picked up legitimately, replenished, occluded or moved by staff. A visually observed item without a matching scan is not enough to infer non-payment unless event synchronization and sensor coverage are validated. Missing data must be UNKNOWN, not a violation.

## 1. Research and design references

### Product/company references
- Trigo Loss Prevention: https://www.trigo.tech/loss-prevention/ and https://www.trigoretail.com/loss-prevention/
  - Publicly describes connecting existing CCTV and POS, tracking shopper-product interactions and comparing picked-up items with paid items across aisles, checkout and exit.
  - Design implication: model store-wide item journey and transaction reconciliation, not isolated person classification.
  - Public demo: https://vimeo.com/1118699670
- SeeChange: https://seechange.com/ and https://seechange.com/solutions/ai-self-checkout-software/
  - Publicly describes missed scans, barcode switching, product stacking, walkaways and integration with existing cameras/sensors; edge/cloud/hybrid deployment.
  - Design implication: per-checkout state machines and integration with scan, scale/bagging and transaction events.
- Veesion: https://veesion.io/en/
  - Gesture/behavior-focused retail loss-prevention reference. Treat gesture scores as supplementary evidence, never proof.
- ThirdAI / Turbo AI Vision: https://turboaivision.com/thirdai/
  - Public product positioning describes suspicious behavior, event clips, review priority and pilot false-alert measurement. Claims are vendor statements, not independently verified.
- NVIDIA Retail Loss Prevention workflow: https://www.nvidia.com/en-us/ai-data-science/ai-workflows/retail-loss-prevention/
  - Reference for product recognition, model adaptation and point-of-sale workflow.
- NVIDIA DeepStream docs: https://docs.nvidia.com/metropolis/deepstream/text/DS_Overview.html and https://docs.nvidia.com/metropolis/deepstream/text/DS_plugin_gst-nvstreammux.html
  - Relevant for multi-stream batching and GPU deployment later; not a CPU-only demo dependency.
- NVIDIA TAO: https://developer.nvidia.com/tao-toolkit
  - Candidate for later fine-tuning and deployment of supported models; not required for MVP.
- Ultralytics YOLO26: https://docs.ultralytics.com/models/yolo26 and https://docs.ultralytics.com/modes/track
  - Current tracking docs demonstrate YOLO26 with persistent IDs and selectable TrackTrack, BoT-SORT and ByteTrack. Verify package/model availability at implementation time.

### Medium / employee content
Research did not establish a clearly attributable Medium publication by a named employee of Trigo, SeeChange, Veesion or ThirdAI that materially exceeds their official technical materials. Do not invent employee authorship or assert that no such posts exist. Follow up by inspecting company engineering blogs, verified employee profiles, conference talks and technical publications.

### Demo patterns
- Trigo public Vimeo demo: shelf-to-checkout journey and matching items picked with items paid.
- NVIDIA retail workflow: checkout scanner, item recognition and transaction comparison.
- SeeChange product pages: missed-scan nudge, non-scan, barcode switching, item stacking and walkaway examples.
Build original demo overlays and synthetic scenarios. Do not copy vendor UI or imply partnership/endorsement.

## 2. Model decision

### Initial detector candidate
Use Ultralytics YOLO26n as the first benchmark candidate, not as an unconditionally proven best model. Compare YOLO26n, YOLO11n and an OpenVINO/ONNX-exported candidate on the actual CPU, camera resolution and clips. Choose using measured precision/recall, latency, stability and resource use.

Generic COCO weights do not recognize arbitrary supermarket SKUs, brands, packages or all shelf products. Add a custom retail product detector and/or product image embedding retrieval after collecting a lawful, representative labelled dataset.

CPU strategy: benchmark inference at resized input, frame sampling, ROI cropping, OpenVINO/ONNX Runtime and bounded latest-frame queues. Keep capture independent of inference to avoid unbounded latency. Do not promise FPS or camera capacity before measurement.

Review current Ultralytics code/model licensing before commercial distribution or deployment.

### Tracking
- ByteTrack: efficient fixed-camera baseline.
- BoT-SORT: compare for occlusion and ID switches; optional ReID increases cost and has privacy implications.
- TrackTrack: currently shown as Ultralytics default in current docs; benchmark rather than assume superiority.
Keep tracker state isolated per camera. Do not reuse persistent state across unrelated streams. Do not implement face recognition or person identity embeddings. Use short-lived camera-local track IDs.

### Product recognition and temporal analysis
1. Generic person/object detector for baseline.
2. Custom retail product classes trained on curated store imagery.
3. Optional SKU/image embedding retrieval for visually similar product variants.
4. Integrate POS catalog/SKU metadata where permitted.
Do not start with a black-box theft classifier. Begin with transparent finite-state machines and observable events. Pose/action models can provide supplementary geometry only, not evidence of theft.

## 3. Target architecture

### CPU-only local demo
- RTSP/file/synthetic capture adapters (one supervised reader per camera).
- Frame sampling and bounded latest-frame queue.
- Vision worker: detector + tracker.
- Store geometry / zone service.
- Shelf interaction and event state machine.
- Optional POS/scale adapter; simulated events for demo.
- Event API and WebSocket/SSE push.
- PostgreSQL for metadata, events and reviews.
- Local evidence clip store with retention controls.
- Web dashboard (Next.js/React).
- Mobile app (React Native/Expo); responsive PWA fallback only with product-owner approval.

### Later production scale
- Per-camera/partition workers; Redis Streams or Kafka only if measured throughput requires it.
- GPU inference nodes; evaluate NVIDIA DeepStream for multi-stream batching.
- Edge-first processing; cloud receives event metadata and only necessary authorized evidence.
- Encrypted object storage with lifecycle retention.
- Metrics, structured logs, traces and deployment orchestration.

Do not begin with Kubernetes, Kafka or microservices for a one-host demo. Keep clear module boundaries for later extraction.

Logical flow: RTSP -> Capture -> Decode -> Sample/ROI -> Detector -> Tracker -> Zones/interactions -> Domain event state machine <- POS/scan/scale events -> Event correlation -> Event API -> Web/mobile review queue.

### Core entities
- Store, Camera, CameraZone, CameraStreamStatus
- FrameObservation, Track (ephemeral, camera-local), ProductObservation
- ShelfInteraction, CheckoutSession, ScanEvent, ScaleEvent, TransactionEvent
- AnomalyEvent, EvidenceClip, ReviewDecision, AuditLog

### Event contract
Each event includes event_id, store_id, camera_id, zone_id, event_type, severity, status, occurred_at/detected_at/created_at UTC timestamps, ephemeral track references, evidence references, model/tracker/rule versions, confidence components, reason codes, missing-data flags and human_review_required=true.
Never store face identity or infer protected attributes.

## 4. Functional requirements and event rules

### A. Shelf/aisle cameras
Configure polygon/ROI zones: SHELF_DISPLAY, PICKUP_INTERACTION, OCCLUSION/UNKNOWN and optional AISLE_EXIT.

Rule A1 — Product presence baseline:
- Maintain occupancy/position estimates per shelf ROI.
- Require stable detections over N observations before establishing baseline.
- Update baseline only through approved replenishment/adjustment or a stable-observation policy.
- Never silently learn a removal as a new baseline.

Rule A2 — Possible removal:
- Detect product disappearance from shelf ROI over a configurable interval.
- Verify the zone is not occluded and camera health is good.
- Check for person/product interaction near shelf.
- Emit SHELF_ITEM_REMOVED_UNRESOLVED or SHELF_OCCLUSION_REVIEW, not theft.
- Merge duplicates using incident correlation and cooldown.

Rule A3 — Product-person association:
- Associate by spatial overlap, hand/object proximity if reliable, temporal proximity and camera geometry.
- Store association score components; it is not identity.
- In crowded/occluded scenes return UNKNOWN.

Rule A4 — Cross-camera journey:
- Optional only where cameras are calibrated and overlap.
- No face recognition. Use time/location continuity and object/product cues; if uncertain, do not force linkage.
- Do not claim reliable cross-camera re-identification without evaluation and legal review.

### B. Self-checkout
Model each checkout terminal as an independent state machine:
IDLE -> SESSION_ACTIVE -> ITEM_PRESENTED -> SCAN_OBSERVED -> BAGGING_OBSERVED -> SCALE_STABLE -> PAYMENT_PENDING -> PAID/SESSION_CLOSED.
Support retries, item removal, produce lookup, attendant override, void/cancel and payment failure.

Required adapters:
- Camera zones: scan-area, bagging/scale-area, basket/cart-area and exit-side.
- Scanner/POS: SKU, timestamp, quantity, terminal/session ID, void/refund.
- Scale: stable weight, placement/removal, expected/actual weight when available, calibration status.
- Terminal state: active, suspended, attendant approval, payment authorized/declined, completed.
Demo uses deterministic simulated POS/scanner/scale events and labels them SIMULATED. Video alone cannot know that an item was scanned or weighed.

Rule B1 — Possible non-scan:
- Detect item in bagging zone.
- Look for scanner event within configurable window tied to same terminal session.
- If scanner event absent and video + POS adapter healthy, emit ITEM_PLACED_NOT_SCANNED.
- If scanner integration is unavailable/delayed, emit TRANSACTION_DATA_MISSING or UNKNOWN, never a non-scan alert.

Rule B2 — Scale mismatch:
- Compare expected product weight with stable measured weight if available.
- Account for tolerance, produce lookup, multiple-item stacking, packaging, tare and approved overrides.
- Emit SCALE_MISMATCH_REVIEW, never assert theft.

Rule B3 — Item moved outside bagging zone:
- Detect movement to cart/basket/hand/other region without corresponding transaction or authorized workflow event.
- Limit to calibrated field of view and observed terminal session.
- Emit ITEM_MOVED_UNRESOLVED.

Rule B4 — Transaction completed with unresolved item:
- Reconcile visual item events, scans, voids, payment and scale at transaction close.
- Unmatched item -> TRANSACTION_RECONCILIATION_REQUIRED.
- Missing/contradictory signals -> TRANSACTION_UNKNOWN.

Rule B5 — Barcode substitution: out of MVP unless package/SKU recognition and scanner SKU are validated. If built, emit PRODUCT_SCAN_MISMATCH_REVIEW.
Rule B6 — Product stacking/multiple-item scan: out of MVP unless segmentation/counting and checkout geometry are validated.

### C. Shared alert logic
- Confidence is multidimensional: detector confidence, track quality, zone certainty, POS synchronization and rule evidence.
- Add temporal smoothing, minimum evidence requirements and cooldown.
- Deduplicate by store + terminal/zone + event type + time bucket + ephemeral track ref.
- Every alert includes explanation and missing-data status.
- Severity: INFO, REVIEW, HIGH_REVIEW. Never label a person a suspect/thief.
- Review outcomes: CONFIRMED_OPERATIONAL_ANOMALY, FALSE_POSITIVE, INSUFFICIENT_EVIDENCE, RESOLVED_BY_STAFF. These describe event review, not legal guilt.

## 5. Required demo scenarios
1. Shelf: product visible -> person interacts -> product disappears beyond threshold -> event timeline and zone overlay.
2. Shelf occlusion: another shopper blocks shelf -> no removal allegation; optionally mark zone unknown.
3. Shelf replenishment: staff replenishment/authorized adjustment simulated -> controlled baseline update.
4. Self-checkout normal: item detected -> simulated scan -> bagging/scale -> paid -> no alert.
5. Self-checkout non-scan: item detected in bagging zone -> no scan in time window -> neutral alert.
6. Self-checkout delayed feed: scanner adapter unavailable -> UNKNOWN/integration warning, not non-scan.
7. Weight mismatch: item scanned, simulated scale reading outside tolerance -> review alert.
8. Transaction void/removal: legitimate void and item removal -> resolved with audit event.

Use synthetic/sample clips or user-provided authorized videos. Do not commit scraped identifiable CCTV footage. Include offline file mode and synthetic camera adapter. Document data provenance and clip license.

## 6. Web dashboard
- Overview: active cameras, online streams, open review events, detection latency; demo values visibly tagged.
- Live camera grid with health, stream latency, FPS, detection overlays and zone polygons.
- Camera detail: timeline, tracks, zone configuration and event history.
- Alerts inbox with filters by store/camera/event/status/date/severity.
- Event detail: synchronized clip, timeline of vision/POS/scale signals, reason codes, missing signals, model/rule version and review actions.
- Checkout monitor: per-terminal state machine and scanner/scale feed.
- Configuration: camera registry, zones, thresholds and demo controls.
- Audit page for reviewer decisions/config changes.
No face thumbnails, identity search, demographic inference or person profiling.

## 7. Mobile application
Use React Native + Expo + TypeScript if native app is required. Screens: mock login for local demo, alert inbox, event detail/evidence, acknowledge/assign/resolve/dismiss with reason, camera health, offline/error state.
Do not expose raw RTSP credentials or direct camera URLs to mobile. Deliver authorized evidence through authenticated API with short-lived access.

## 8. API contract (suggested)
- GET /api/v1/health
- GET /api/v1/stores
- GET /api/v1/cameras
- GET /api/v1/cameras/{camera_id}/status
- GET /api/v1/cameras/{camera_id}/observations
- GET /api/v1/events?status=&type=&camera_id=
- GET /api/v1/events/{event_id}
- POST /api/v1/events/{event_id}/acknowledge
- POST /api/v1/events/{event_id}/resolve
- POST /api/v1/events/{event_id}/dismiss
- GET /api/v1/checkouts
- GET /api/v1/checkouts/{terminal_id}/state
- POST /api/v1/demo/scenarios/{scenario_id}/run (demo only)
- WS /api/v1/stream/events or SSE
- Authenticated short-lived evidence endpoint; never return raw storage paths.

## 9. Suggested repository structure
```text
apps/api/                 # FastAPI
apps/web/                 # Next.js dashboard
apps/mobile/              # React Native / Expo
services/capture/         # RTSP/file/synthetic adapters
services/vision/          # detector, tracker, product recognition
services/zones/           # polygon geometry and calibration
services/shelf-analytics/ # shelf occupancy/removal candidates
services/checkout-analytics/ # checkout state machine/reconciliation
services/integrations/    # POS/scanner/scale adapters
services/events/          # contracts, correlation, evidence
packages/contracts/       # shared event/API schemas
infra/docker/
infra/migrations/
configs/cameras.example.yaml
configs/zones.example.yaml
configs/rules.example.yaml
data/README.md            # no private footage committed
docs/STOREGUARD_DEMO_ROADMAP.md
docs/ARCHITECTURE.md
docs/ADR/
docs/research/
tests/unit/
tests/integration/
tests/replay/
tests/e2e/
.env.example
docker-compose.yml
README.md
```

## 10. Technology stack
- Backend: Python 3.11/3.12, FastAPI, Pydantic.
- Video: OpenCV + FFmpeg/GStreamer RTSP/file ingest.
- Detection: YOLO26n benchmark baseline plus YOLO11n comparison.
- Tracking: ByteTrack baseline, compare BoT-SORT and current Ultralytics TrackTrack.
- CPU optimization: OpenVINO or ONNX Runtime benchmarks.
- Persistence: PostgreSQL + Alembic.
- Redis only if event fanout/job queue warrants it.
- Real-time: WebSocket/SSE.
- Web: Next.js + TypeScript + Tailwind.
- Mobile: React Native + Expo + TypeScript.
- Packaging: Docker Compose. No Kubernetes/Kafka in MVP.

## 11. Implementation phases and acceptance criteria

### Phase 0 — Repository and engineering baseline
- Inspect repository tree, README, license, git status and branch.
- Add roadmap, architecture ADR and README.
- Scaffold backend, web and mobile apps.
- Configure lint, format, type checks, tests and CI.
Acceptance: clean clone installs; health endpoints and baseline tests pass.

### Phase 1 — Offline vision workbench
- File/synthetic camera adapter.
- YOLO26n detection + tracking.
- Annotated output with labels, boxes, IDs, FPS and latency.
- CPU benchmark YOLO26n vs YOLO11n.
Acceptance: reproducible benchmark report on target machine; model choice supported by measurements.

### Phase 2 — Camera and zones
- RTSP reconnect and health state.
- Per-camera latest-frame buffer; no unbounded queue.
- Polygon zone configuration/overlay.
Acceptance: disconnect/reconnect test, frame-age metric, camera status and zones visible.

### Phase 3 — Shelf event MVP
- Shelf occupancy baseline and unresolved disappearance candidate.
- Occlusion/offline suppression.
- Optional person/product spatial-temporal association.
- Evidence clip and review workflow.
Acceptance: scenarios 1–3 pass replay tests; false-alert count recorded.

### Phase 4 — Self-checkout MVP
- Checkout terminal state machine.
- Simulated scanner/POS/scale adapters.
- Item detection + scan reconciliation window.
- Weight mismatch and unavailable integration behavior.
Acceptance: scenarios 4–8 pass deterministic integration/replay tests; never emit non-scan when POS feed is unavailable.

### Phase 5 — Web dashboard
- Camera grid, event inbox/details, checkout monitor and review actions.
- Real-time updates.
Acceptance: complete browser-operated end-to-end demo.

### Phase 6 — Mobile
- Alert inbox, event detail, evidence and review actions.
- Authenticated API and short-lived media access.
Acceptance: mobile receives test alerts and acknowledges/resolves with audit trail.

### Phase 7 — Demo packaging and hardening
- Docker Compose, seeded demo data and scenario runner.
- Observability, structured logs, metrics and graceful shutdown.
- Security/privacy review checklist.
Acceptance: single-command offline demo; RTSP optional; known limitations documented.

## 12. Evaluation plan
Measure and report, never invent:
- Detection precision/recall per class and camera angle.
- Tracking ID switches, fragmentation and continuity.
- Shelf candidate precision/recall.
- Self-checkout event precision/recall by rule.
- False alerts per camera-hour and checkout-hour.
- End-to-end alert latency p50/p95.
- Frame age, dropped frames and reconnect count.
- CPU/RAM/disk/network utilization.
- Evidence clip completeness and timestamp alignment.
Split train/validation/test by store/camera and time, not adjacent random frames. Run shadow mode; alerts are review-only.

## 13. Privacy, safety and security
- Before deployment in Türkiye, obtain legal review of KVKK basis, notices, purpose limitation, retention, access, processor contracts and cross-border transfers.
- No facial recognition, biometric identification or identity matching; use short-lived camera-local pseudonymous track IDs.
- No audio unless separately justified and legally reviewed.
- Mask areas outside operational zones; never capture sensitive/private areas.
- Encrypt transport/evidence; role-based access, audit logs, key rotation and secrets management.
- Minimize evidence retention and implement automated deletion.
- Never expose RTSP publicly; isolate cameras on trusted network.
- Every alert is explainable and human-reviewed; no automated accusation or enforcement.

## 14. Claude Code execution instructions

Work in small, reviewable increments. Do not build all phases in one pass.
1. Inspect repository tree, README, license, git status and current branch.
2. Report existing state and proposed changes.
3. Create branch feat/storeguard-demo-foundation; do not force-push or rewrite history.
4. Implement Phase 0 only; run tests, lint and type checks; report results.

For every phase report summary/changed files, decisions and alternatives, commands and actual outputs, tests passed/failed, measured CPU/RAM/FPS/latency, gaps/risks, screenshots or screen recording where relevant, commit SHA and branch.
Do not claim completion when code is stubbed or tests were not run. Clearly label simulated camera/POS/scale data.
Stop after Phase 0 and await owner review before Phase 1.