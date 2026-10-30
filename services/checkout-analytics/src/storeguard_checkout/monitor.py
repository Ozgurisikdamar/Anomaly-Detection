"""Self-checkout terminal state machine + reconciliation (rules B1–B4)."""

from __future__ import annotations

from datetime import UTC

from storeguard_contracts import (
    AnomalyEvent,
    CheckoutSession,
    CheckoutState,
    ConfidenceComponents,
    EventType,
    ScaleEvent,
    ScanEvent,
    Severity,
    TransactionEvent,
)

from storeguard_checkout.model import CheckoutRules, PendingItem, TerminalState

RULE_VERSION = "phase4-checkout-fsm"


class CheckoutMonitor:
    def __init__(self, store_id: str, rules: CheckoutRules | None = None) -> None:
        self.store_id = store_id
        self.rules = rules or CheckoutRules()
        self._terminals: dict[str, TerminalState] = {}

    def _term(self, terminal_id: str, camera_id: str = "") -> TerminalState:
        ts = self._terminals.get(terminal_id)
        if ts is None:
            ts = TerminalState(
                terminal_id=terminal_id, camera_id=camera_id, store_id=self.store_id
            )
            self._terminals[terminal_id] = ts
        elif camera_id:
            ts.camera_id = camera_id
        return ts

    # --- inputs ----------------------------------------------------------
    def start_session(
        self, terminal_id: str, session_id: str, camera_id: str, t: float
    ) -> None:
        ts = self._term(terminal_id, camera_id)
        ts.session_id = session_id
        ts.state = CheckoutState.SESSION_ACTIVE
        ts.pending.clear()
        ts.unmatched_scans.clear()
        ts.feed_was_unavailable = False
        ts.updated_at = t

    def set_scanner_available(self, terminal_id: str, available: bool) -> None:
        ts = self._term(terminal_id)
        ts.scanner_available = available
        if not available:
            ts.feed_was_unavailable = True

    def observe_scan(self, scan: ScanEvent) -> list[AnomalyEvent]:
        ts = self._term(scan.terminal_id)
        ts.scans.append(scan)
        ts.state = CheckoutState.SCAN_OBSERVED
        # The window clock is driven by the float `t` passed to bagging/advance;
        # scan ordering (not its wall-clock) drives matching here.
        # Match the oldest unmatched pending item (reconciliation is per session).
        for item in ts.pending:
            if not item.matched and not item.voided:
                item.matched = True
                return []
        ts.unmatched_scans.append((scan.sku, 0.0))
        return []

    def observe_bagging_item(
        self,
        terminal_id: str,
        session_id: str,
        item_id: str,
        t: float,
        camera_id: str = "",
        expected_sku: str | None = None,
    ) -> list[AnomalyEvent]:
        ts = self._term(terminal_id, camera_id)
        ts.state = CheckoutState.BAGGING_OBSERVED
        ts.updated_at = t
        # If a scan is already waiting, match immediately.
        if ts.unmatched_scans:
            ts.unmatched_scans.pop(0)
            ts.pending.append(
                PendingItem(
                    item_id=item_id, t=t, expected_sku=expected_sku, matched=True
                )
            )
            return []
        ts.pending.append(PendingItem(item_id=item_id, t=t, expected_sku=expected_sku))
        return self.advance(terminal_id, t)

    def observe_scale(self, scale: ScaleEvent) -> list[AnomalyEvent]:
        ts = self._term(scale.terminal_id)
        ts.scale_events.append(scale)
        ts.state = CheckoutState.SCALE_STABLE
        if scale.stable_weight_g is None or scale.expected_weight_g is None:
            return []  # cannot compare without telemetry -> no mismatch alert
        diff = abs(scale.stable_weight_g - scale.expected_weight_g)
        if diff > self.rules.scale_tolerance_g:
            return [self._scale_mismatch_event(ts, scale, diff)]
        return []

    def observe_item_moved_out(
        self, terminal_id: str, session_id: str, item_id: str, t: float
    ) -> list[AnomalyEvent]:
        ts = self._term(terminal_id)
        for item in ts.pending:
            if item.item_id == item_id:
                item.moved_out = True
                if not item.matched and not item.voided and not item.alerted:
                    item.alerted = True
                    return [self._item_moved_event(ts, item)]
        return []

    def observe_transaction(self, txn: TransactionEvent) -> list[AnomalyEvent]:
        ts = self._term(txn.terminal_id)
        ts.transaction_events.append(txn)
        if txn.kind == "payment_authorized":
            ts.state = CheckoutState.PAYMENT_PENDING
            return []
        if txn.kind == "void":
            # Authorized void resolves the matching item — no alert.
            for item in reversed(ts.pending):
                if not item.voided:
                    item.voided = True
                    item.matched = True
                    break
            return []
        if txn.kind == "completed":
            events = self.advance(terminal_id=txn.terminal_id, t=ts.updated_at)
            events += self._reconcile_close(ts)
            ts.state = CheckoutState.SESSION_CLOSED
            return events
        return []

    # --- window / finalize ----------------------------------------------
    def advance(self, terminal_id: str, t: float) -> list[AnomalyEvent]:
        """Flush non-scan / data-missing decisions for expired bagging windows."""
        ts = self._term(terminal_id)
        out: list[AnomalyEvent] = []
        for item in ts.pending:
            if item.matched or item.voided or item.alerted or item.moved_out:
                continue
            if (t - item.t) < self.rules.scan_match_window_s:
                continue
            item.alerted = True
            if ts.scanner_available and ts.camera_ok:
                out.append(self._non_scan_event(ts, item))
            else:
                # Core rule: missing/late POS feed is UNKNOWN, never a non-scan.
                out.append(self._data_missing_event(ts, item))
        return out

    def finalize(self, terminal_id: str, t: float) -> list[AnomalyEvent]:
        events = self.advance(terminal_id, t)
        events += self._reconcile_close(self._term(terminal_id))
        return events

    def _reconcile_close(self, ts: TerminalState) -> list[AnomalyEvent]:
        unresolved = [
            i for i in ts.pending if not i.matched and not i.voided and not i.alerted
        ]
        if not unresolved:
            return []
        if ts.feed_was_unavailable:
            return [self._unknown_event(ts)]
        return [self._reconciliation_event(ts, len(unresolved))]

    # --- snapshot --------------------------------------------------------
    def session(self, terminal_id: str) -> CheckoutSession:
        ts = self._term(terminal_id)
        from datetime import datetime

        return CheckoutSession(
            terminal_id=ts.terminal_id,
            store_id=ts.store_id,
            session_id=ts.session_id,
            state=ts.state,
            scans=ts.scans,
            scale_events=ts.scale_events,
            transaction_events=ts.transaction_events,
            updated_at=datetime.now(tz=UTC),
            simulated=True,
        )

    # --- event builders --------------------------------------------------
    def _base_kwargs(self, ts: TerminalState) -> dict:
        return {
            "store_id": self.store_id,
            "camera_id": ts.camera_id or ts.terminal_id,
            "rule_version": RULE_VERSION,
            "simulated": True,
        }

    def _non_scan_event(self, ts: TerminalState, item: PendingItem) -> AnomalyEvent:
        return AnomalyEvent(
            event_type=EventType.ITEM_PLACED_NOT_SCANNED,
            severity=Severity.HIGH_REVIEW,
            confidence=ConfidenceComponents(
                zone_certainty=0.85, pos_synchronization=0.9, rule_evidence=0.7
            ),
            reason_codes=["item_in_bagging_zone", "no_matching_scan_in_window"],
            explanation=(
                "An item was observed in the bagging zone with no matching scan within the "
                "window on a HEALTHY simulated POS session. Flagged for review — not an "
                "accusation."
            ),
            **self._base_kwargs(ts),
        )

    def _data_missing_event(self, ts: TerminalState, item: PendingItem) -> AnomalyEvent:
        return AnomalyEvent(
            event_type=EventType.TRANSACTION_DATA_MISSING,
            severity=Severity.INFO,
            confidence=ConfidenceComponents(pos_synchronization=None),
            reason_codes=["scanner_feed_unavailable"],
            missing_data_flags=["scanner_feed_unavailable"],
            explanation=(
                "The scanner/POS feed was unavailable or late, so a scan could not be "
                "confirmed. Per the core rule, this is UNKNOWN — NO non-scan alert is "
                "emitted. Integration warning only."
            ),
            **self._base_kwargs(ts),
        )

    def _scale_mismatch_event(
        self, ts: TerminalState, scale: ScaleEvent, diff: float
    ) -> AnomalyEvent:
        return AnomalyEvent(
            event_type=EventType.SCALE_MISMATCH_REVIEW,
            severity=Severity.REVIEW,
            confidence=ConfidenceComponents(
                pos_synchronization=0.85, rule_evidence=0.6
            ),
            reason_codes=["weight_outside_tolerance"],
            explanation=(
                f"Simulated stable scale weight differs from the expected weight by "
                f"{diff:.0f} g (tolerance {self.rules.scale_tolerance_g:.0f} g). Could be a "
                "produce lookup, stacking, packaging or tare — review required, never theft."
            ),
            **self._base_kwargs(ts),
        )

    def _item_moved_event(self, ts: TerminalState, item: PendingItem) -> AnomalyEvent:
        return AnomalyEvent(
            event_type=EventType.ITEM_MOVED_UNRESOLVED,
            severity=Severity.REVIEW,
            confidence=ConfidenceComponents(zone_certainty=0.8, rule_evidence=0.5),
            reason_codes=["item_moved_without_transaction"],
            explanation=(
                "An item left the bagging zone without a corresponding transaction or "
                "authorized workflow event. Requires review; not an accusation."
            ),
            **self._base_kwargs(ts),
        )

    def _reconciliation_event(self, ts: TerminalState, count: int) -> AnomalyEvent:
        return AnomalyEvent(
            event_type=EventType.TRANSACTION_RECONCILIATION_REQUIRED,
            severity=Severity.REVIEW,
            confidence=ConfidenceComponents(rule_evidence=0.5, pos_synchronization=0.8),
            reason_codes=["unmatched_item_at_transaction_close"],
            explanation=(
                f"At transaction close, {count} observed item(s) did not reconcile with "
                "scans, voids, payment and scale. Requires reconciliation review."
            ),
            **self._base_kwargs(ts),
        )

    def _unknown_event(self, ts: TerminalState) -> AnomalyEvent:
        return AnomalyEvent(
            event_type=EventType.TRANSACTION_UNKNOWN,
            severity=Severity.INFO,
            confidence=ConfidenceComponents(pos_synchronization=None),
            reason_codes=["missing_or_contradictory_signals"],
            missing_data_flags=["scanner_feed_unavailable"],
            explanation=(
                "Transaction closed with missing/contradictory integration signals; the "
                "outcome is UNKNOWN. No violation is alleged."
            ),
            **self._base_kwargs(ts),
        )
