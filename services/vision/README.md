# services/vision — detector + tracker (scaffold)

**Phase 0 status: scaffold only. No model runs here and no weights are
downloaded.** This package fixes the benchmark interface (`benchmark.py`) and
documents the methodology (`benchmark_plan.md`). The real benchmark and
inference are Phase 1.

## CPU-first strategy (preserved from the roadmap)
The demo targets **CPU-only local inference**. The plan is to measure, never to
promise FPS or camera capacity before measurement:
- resized input, frame sampling, ROI cropping;
- OpenVINO / ONNX Runtime export candidates;
- bounded latest-frame queues with capture kept independent of inference.

## Model benchmark (preserved)
YOLO26n is the **initial candidate, not a pre-approved winner**. Phase 1
benchmarks **YOLO26n vs YOLO11n** (plus an OpenVINO/ONNX export) on the real
target CPU, camera resolution and clips, and selects on measured
precision/recall, latency (p50/p95), stability and resource use.

Tracking baseline is **ByteTrack**; **BoT-SORT** and **TrackTrack** are compared
rather than assumed superior. Trackers keep per-camera isolated state and use
short-lived, camera-local pseudonymous IDs. No face recognition, no person
re-identification.

Review current Ultralytics code/model licensing before any commercial
distribution or deployment.

See `benchmark_plan.md` for the full methodology and result matrix.
