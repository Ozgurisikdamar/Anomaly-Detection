"""StoreGuard vision workbench.

Phase 1: offline vision workbench — file/synthetic capture adapters, a YOLO
detector + tracker wrapper, annotated output, and a CPU benchmark that measures
YOLO26n vs YOLO11n on this machine.

Model execution needs the optional ``ml`` extra (ultralytics, opencv-python,
psutil). Importing this package does **not** import those heavy dependencies;
only the capture/detector/benchmark modules pull them in when used, so the
lightweight unit tests and a clean install stay fast.
"""

__version__ = "0.2.0"
# Phase 1: the benchmark is implemented (was a stub in Phase 0).
BENCHMARK_IMPLEMENTED = True
