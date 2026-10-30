"""Shelf-analytics CLI.

    python -m storeguard_shelf.cli shelf-demo --out runs

Runs scenarios 1-3, prints the event timeline and false-alert count, renders an
evidence montage for the removal candidate, and walks it through a mock review
(acknowledge -> resolve) to show the detect -> evidence -> review loop.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from storeguard_contracts import EventStatus, ReviewDecision, ReviewOutcome

from storeguard_shelf.scenarios import run_all, total_false_alerts


def cmd_shelf_demo(args: argparse.Namespace) -> int:
    results = run_all()
    print("=== Shelf scenarios (replay) ===")
    for r in results:
        verdict = "removal expected" if r.expected_removal else "NO removal expected"
        print(
            f"- {r.name:22} {verdict:18} removals={r.removal_count} "
            f"occlusion={r.occlusion_count} false_alerts={r.false_alerts}"
        )
        for e in r.events:
            print(
                f"      {e.event_type.value:30} sev={e.severity.value:11} {e.reason_codes}"
            )
    print(f"TOTAL false alerts across scenarios: {total_false_alerts(results)}")

    # Evidence + review workflow for the removal candidate.
    removal = next(
        (
            e
            for r in results
            for e in r.events
            if e.event_type.value == "SHELF_ITEM_REMOVED_UNRESOLVED"
        ),
        None,
    )
    if removal is None:
        print("no removal candidate to review")
        return 0

    try:
        from storeguard_shelf.evidence import render_evidence_montage

        ref = render_evidence_montage(Path(args.out) / "shelf_evidence.png")
        removal.evidence = [ref]
        print(
            f"\nEvidence montage: {Path(args.out) / 'shelf_evidence.png'} (ref={ref.evidence_id})"
        )
    except Exception as exc:  # noqa: BLE001 - optional ml extra may be absent
        print(f"\n(evidence montage skipped: {exc})")

    # Mock human review (the API exposes the same acknowledge/resolve/dismiss).
    print("\n=== Review workflow (mock) ===")
    removal.status = EventStatus.ACKNOWLEDGED
    print(f"acknowledge: {removal.event_id} -> {removal.status.value}")
    removal.status = EventStatus.RESOLVED
    removal.review = ReviewOutcome(
        decision=ReviewDecision.CONFIRMED_OPERATIONAL_ANOMALY,
        reviewer="demo-reviewer",
        note="Reviewed evidence montage; operational anomaly confirmed (not an accusation).",
        decided_at=datetime.now(tz=UTC),
    )
    decision = removal.review.decision.value
    print(f"resolve:     {removal.event_id} -> {removal.status.value} ({decision})")
    print(f"human_review_required stays: {removal.human_review_required}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="storeguard-shelf")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("shelf-demo", help="run scenarios + evidence + mock review")
    d.add_argument("--out", default="runs")
    d.set_defaults(func=cmd_shelf_demo)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
