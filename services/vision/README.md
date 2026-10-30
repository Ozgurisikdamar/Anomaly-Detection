# services/vision — detector + tracker (Phase 1 workbench)

Offline vision workbench: file/synthetic capture adapters, a YOLO detector +
tracker wrapper, annotated output, and a **CPU benchmark** comparing
**YOLO26n vs YOLO11n** on the real machine.

Phase 1 runs real models. Measured results for this environment are in
[`docs/reports/PHASE_1_REPORT.md`](../../docs/reports/PHASE_1_REPORT.md).

## Install (ML extra)
Model execution needs the optional `ml` extra (ultralytics, opencv-python,
psutil). It is kept out of the default dev/CI install so a clean clone and
baseline tests stay fast.

```bash
. .venv/bin/activate
pip install -e "services/vision[ml]"
```

## CLI
```bash
# CPU benchmark over an image dir / video (omit --clip for synthetic frames)
python -m storeguard_vision.cli benchmark --models yolo26n yolo11n --clip <path> --frames 48 --out runs

# Annotated detections for a source
python -m storeguard_vision.cli annotate --model yolo26n --clip <img|dir> --out runs

# Tracking demo (persistent IDs; a sample image is slid across a canvas)
python -m storeguard_vision.cli track --model yolo26n --image <img> --out runs
```
Weights (`yolo26n.pt`, `yolo11n.pt`) download on first use; outputs and weights
are git-ignored (`runs/`, `.cache/`, `*.pt`).

## CPU-first strategy (preserved)
CPU-only inference: capture independent of inference, bounded latest-frame
queue (Phase 2), resized input / frame sampling, OpenVINO/ONNX export candidates
to evaluate. FPS/latency are **measured**, never promised — see the report.

## Model benchmark (preserved)
YOLO26n is the initial candidate, **measured** against YOLO11n (ByteTrack
baseline; BoT-SORT/TrackTrack to compare). Per-camera isolated tracker state,
short-lived camera-local pseudonymous IDs only — no face recognition or person
re-identification. Generic COCO weights are not supermarket SKU recognition; a
custom retail detector/embedding path remains a separate effort. Review
Ultralytics licensing before commercial deployment. See `benchmark_plan.md`.

## Benchmark result shape
`run_benchmark(BenchmarkConfig) -> BenchmarkResult` returns measured latency
(p50/p95/mean), single-stream FPS, process CPU% and peak RSS. Precision/recall
and tracking ID-switch counts stay `None` until a labelled eval set exists
(never invented). Export candidates (`onnx-export`, `openvino-export`) raise
`NotImplementedError` pending a follow-up.
