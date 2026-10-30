"""Capture adapters: one supervised reader per source (synthetic / file).

Kept deliberately simple for the offline workbench. RTSP capture with
reconnect/health is a Phase 2 concern; these adapters produce frames for
detection, tracking and benchmarking without any network source.
"""

from storeguard_vision.capture.base import Frame, FrameSource
from storeguard_vision.capture.synthetic import SyntheticFrameSource

__all__ = ["Frame", "FrameSource", "SyntheticFrameSource"]
