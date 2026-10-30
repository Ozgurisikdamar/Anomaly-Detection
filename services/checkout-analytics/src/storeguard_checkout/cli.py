"""Checkout-analytics CLI.

    python -m storeguard_checkout.cli checkout-demo

Runs scenarios 4-8 and prints each one's emitted events, highlighting the core
safety rule: a missing POS feed yields TRANSACTION_DATA_MISSING, never a
non-scan alert.
"""

from __future__ import annotations

import argparse

from storeguard_checkout.scenarios import non_scan_when_feed_unavailable, run_all


def cmd_checkout_demo(_args: argparse.Namespace) -> int:
    results = run_all()
    print("=== Self-checkout scenarios (replay, SIMULATED signals) ===")
    for r in results:
        print(f"- {r.name:22} -> {r.types if r.types else '[] (no alert — correct)'}")
        for e in r.events:
            print(
                f"      {e.event_type.value:34} sev={e.severity.value:11} {e.reason_codes}"
            )
    n = non_scan_when_feed_unavailable(results)
    print(f"\nCRITICAL: non-scan alerts while POS feed unavailable = {n} (must be 0)")
    print("OK" if n == 0 else "FAIL: emitted a non-scan without a healthy feed")
    return 0 if n == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="storeguard-checkout")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("checkout-demo", help="run self-checkout scenarios 4-8")
    d.set_defaults(func=cmd_checkout_demo)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
