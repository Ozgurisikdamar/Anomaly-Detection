# ADR 0002 — CPU-first local inference

- Status: Accepted
- Date: 2026-10-30

## Context
The demo must run on CPU-only local hardware. GPU/DeepStream is a later,
production-scale concern. Frame rates and camera capacity must not be promised
before measurement.

## Decision
Target **CPU-only** inference for the demo:
- capture kept independent of inference, with a bounded latest-frame queue (no
  unbounded backlog / latency);
- resized input, frame sampling and ROI cropping to control cost;
- OpenVINO / ONNX Runtime export candidates evaluated as CPU optimizations.

No FPS or camera-count guarantees are made until measured on the target machine
(Phase 1).

## Consequences
- Phase 0 ships **no** model execution and downloads **no** weights; heavy ML
  dependencies are intentionally absent from `services/vision` for now.
- The benchmark harness interface is fixed (`services/vision/benchmark.py`) so
  Phase 1 can measure without changing callers.

## Alternatives rejected
- **GPU-first / DeepStream now**: out of scope for a CPU demo; added later if
  throughput requires it.
- **Assuming a frame rate**: violates the roadmap's "measure, don't promise"
  rule.
