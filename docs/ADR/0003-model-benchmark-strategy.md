# ADR 0003 — Model benchmark strategy (YOLO26n vs YOLO11n)

- Status: Accepted
- Date: 2026-10-30

## Context
A detector must be chosen for CPU inference. YOLO26n is a current candidate but
not a proven winner. The choice must be evidence-based.

## Decision
Treat **YOLO26n as the initial candidate, not a pre-approved winner**, and
**benchmark YOLO26n against YOLO11n** (plus an OpenVINO/ONNX export) on the same
representative clips, resolution and the target CPU. Select on measured
precision/recall, latency (p50/p95), frame age, tracking stability and resource
use. Tracking baseline is **ByteTrack**, with **BoT-SORT** and **TrackTrack**
compared; per-camera isolated state and short-lived camera-local pseudonymous
IDs only — no face recognition or person re-identification.

The methodology and result matrix live in `services/vision/benchmark_plan.md`.
Generic COCO weights are not SKU recognition; a custom retail product
detector/embedding path is a separate, later effort on a lawful labelled
dataset. Ultralytics licensing is reviewed before any commercial deployment.

## Consequences
- Phase 1 produces a reproducible benchmark report; the model decision is
  deferred to that measurement.
- Phase 0 only fixes the harness interface and candidate enumeration; no model
  runs.

## Alternatives rejected
- **Hardcoding YOLO26n as the winner**: contradicts the measure-first rule.
- **A black-box theft classifier**: rejected outright; the system uses
  transparent state machines over observable events, not intent inference.
