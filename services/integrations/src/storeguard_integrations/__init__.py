"""StoreGuard integration adapters.

Phase 0 contains **only simulators**. There is no real POS, scanner or scale
connection. Every event these functions produce carries ``simulated=True`` and
``SIMULATED_LABEL`` so the demo can never be mistaken for a live integration.

Real adapters (replacing these simulators behind the same contract types) are a
later-phase task and must be clearly separated from this module.
"""

SIMULATED_LABEL = "SIMULATED"
__version__ = "0.1.0"
