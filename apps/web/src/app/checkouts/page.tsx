import { loadCheckouts } from "@/lib/api";
import { Panel, SourcePill } from "@/lib/ui";

export const dynamic = "force-dynamic";

const STATES = [
  "IDLE",
  "SESSION_ACTIVE",
  "ITEM_PRESENTED",
  "SCAN_OBSERVED",
  "BAGGING_OBSERVED",
  "SCALE_STABLE",
  "PAYMENT_PENDING",
  "PAID",
];

export default async function CheckoutsPage() {
  const { data: checkouts, source } = await loadCheckouts();

  return (
    <div className="space-y-5">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Checkout monitor</h1>
          <p className="text-sm text-muted">Per-terminal state machine · SIMULATED POS / scanner / scale feeds.</p>
        </div>
        <SourcePill source={source} />
      </header>

      <div className="rounded-lg border border-edge bg-panel p-3 text-xs text-muted">
        Non-scan review events are produced by correlating camera bagging-zone
        observations with the (SIMULATED) scanner/POS feed by terminal, session and
        synchronized UTC time. A missing <em>or</em> delayed POS feed yields{" "}
        <span className="text-slate-200">TRANSACTION_DATA_MISSING</span> (UNKNOWN) — never a
        non-scan alert. Scale mismatch requires scale telemetry.
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {checkouts.map((c) => (
          <Panel key={c.terminal_id} title={`${c.terminal_id} · ${c.state}`}>
            <div className="mb-3 flex flex-wrap gap-1 text-[10px]">
              {STATES.map((s) => (
                <span
                  key={s}
                  className={`rounded px-1.5 py-0.5 ${
                    s === c.state ? "bg-accent text-white" : "bg-edge text-muted"
                  }`}
                >
                  {s}
                </span>
              ))}
            </div>

            <div className="text-sm">
              <div className="mb-1 text-muted">
                Scans (SIMULATED): {c.scans.length === 0 ? "none" : c.scans.length}
              </div>
              {c.scans.map((s) => (
                <div key={s.scan_id} className="flex justify-between text-xs text-slate-200">
                  <span>{s.sku} ×{s.quantity}</span>
                  <span className="text-amber-200">SIMULATED</span>
                </div>
              ))}
              {c.scans.length === 0 ? (
                <div className="rounded border border-slate-500/30 bg-slate-500/10 px-2 py-1 text-xs text-slate-300">
                  ⚠ No scanner feed — state stays UNKNOWN; no non-scan alert emitted.
                </div>
              ) : null}
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}
