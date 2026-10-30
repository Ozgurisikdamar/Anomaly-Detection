"""Server-authoritative review state machine.

Both repositories route every review action through ``ensure_transition`` before
mutating, so the web and mobile clients are equally constrained and cannot drive
an event into an invalid or duplicate state (e.g. resolving an already-resolved
event). Terminal states (RESOLVED / DISMISSED) accept no further action.
"""

from __future__ import annotations

from storeguard_contracts import EventStatus

# action name -> statuses it may be applied from
ALLOWED: dict[str, set[EventStatus]] = {
    "acknowledge": {EventStatus.OPEN},
    "resolve": {EventStatus.OPEN, EventStatus.ACKNOWLEDGED},
    "dismiss": {EventStatus.OPEN, EventStatus.ACKNOWLEDGED},
}


class InvalidTransitionError(Exception):
    """A review action was requested from a status that does not allow it."""


def ensure_transition(current: EventStatus, action: str) -> None:
    """Raise ``InvalidTransitionError`` if ``action`` is not allowed from ``current``."""
    allowed_from = ALLOWED.get(action)
    if allowed_from is None:
        raise InvalidTransitionError(f"unknown review action: {action}")
    if current not in allowed_from:
        raise InvalidTransitionError(
            f"cannot {action} an event in status {current.value}"
        )
