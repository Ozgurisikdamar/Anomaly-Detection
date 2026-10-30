# Claude Code — StoreGuard Implementation Assignment

You are the implementation engineer for StoreGuard in this repository:
https://github.com/Ozgurisikdamar/Anomaly-Detection

Read first:
- README.md
- docs/STOREGUARD_DEMO_ROADMAP.md

## Mission
Build a presentable demo for retail shelf/aisle anomaly monitoring and self-checkout transaction anomaly detection. The demo must include a web dashboard and a mobile application (React Native + Expo preferred). The roadmap is the source of truth.

## Non-negotiable product rules
- Report observable operational anomalies, not theft or criminal intent.
- Never label, identify, profile, or score a person as a thief.
- Every alert is a human-review task.
- Shelf item disappearance is not proof of theft; use UNKNOWN when occlusion, camera degradation or replenishment could explain it.
- Self-checkout non-scan requires synchronized camera observation AND healthy scanner/POS session data. If POS data is missing or late, emit UNKNOWN/integration warning, never ITEM_PLACED_NOT_SCANNED.
- Scale mismatch requires actual scale telemetry and known calibration/tolerance.
- Demo POS/scanner/scale events must be visibly labelled SIMULATED.
- No face recognition, biometric identification, demographic inference or cross-camera person re-identification.
- Do not commit private CCTV, credentials, API keys or .env files.

## Model direction
YOLO26n is the initial candidate, not a pre-approved winner. Benchmark YOLO26n and YOLO11n on the same representative clips and CPU environment. Compare detector quality, track stability, latency, frame age, CPU and RAM. ByteTrack is baseline; compare BoT-SORT where useful. Generic COCO weights are not supermarket SKU recognition. Document the custom product dataset/model path. Check current Ultralytics licensing before commercial deployment.

## Required implementation protocol
1. Inspect the complete repository, git status, branch, README and license. Do not overwrite or force-push.
2. Create branch feat/storeguard-demo-foundation.
3. Implement Phase 0 only from the roadmap: project structure, backend/web/mobile scaffolds, configuration examples, shared contracts, developer setup, lint/format/type/test commands and CI.
4. Add an architecture decision record explaining modular-monolith-first, CPU-first inference, model benchmark strategy and simulated POS boundary.
5. Add a runnable health endpoint and minimal web/mobile launch screens, clearly marked as scaffold/demo placeholders where applicable.
6. Run all available checks. Report actual command outputs; do not claim tests passed if not run.
7. Commit Phase 0 on the feature branch and report the SHA. Do not merge into main.
8. Stop and wait for product-owner review before Phase 1.

## Required report
Create docs/reports/PHASE_0_REPORT.md with repository inspection summary, architecture decisions and rejected alternatives, files changed, setup/run commands, actual test/lint/type-check results, known gaps and risks, exact branch and commit SHA, and screenshots of web/mobile scaffold if possible.

Then provide a concise final summary referencing the report and commit. Do not start Phase 1 without approval.