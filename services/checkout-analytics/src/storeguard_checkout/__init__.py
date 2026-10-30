"""StoreGuard self-checkout analytics (Phase 4).

A per-terminal state machine + reconciliation engine that compares simulated
scanner/POS/scale signals with camera observations. Core safety rule: a
non-scan alert requires a HEALTHY scanner/POS feed. If the feed is unavailable
or late, the system emits ``TRANSACTION_DATA_MISSING`` / UNKNOWN — **never**
``ITEM_PLACED_NOT_SCANNED``. Scale mismatch requires actual scale telemetry and a
known tolerance. Nothing here asserts theft; every alert is a human-review task.

All POS/scanner/scale signals are SIMULATED (``storeguard_integrations``).
"""

from storeguard_checkout.model import CheckoutRules
from storeguard_checkout.monitor import CheckoutMonitor

__all__ = ["CheckoutMonitor", "CheckoutRules"]
__version__ = "0.1.0"
