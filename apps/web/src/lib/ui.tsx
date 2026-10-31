/** Small presentational helpers shared across pages. */
import type { DataSource } from "./api";
import { SEVERITY_TR, SOURCE_TR, STATE_TR, trLabel } from "./tr";

const severityStyles: Record<string, string> = {
  INFO: "bg-sky-500/15 text-sky-700 dark:text-sky-300 border-sky-500/30",
  REVIEW: "bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30",
  HIGH_REVIEW: "bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30",
};

export function SeverityBadge({ severity }: { severity: string }) {
  const cls = severityStyles[severity] ?? "bg-slate-500/15 text-muted border-slate-500/30";
  return (
    <span className={`inline-block rounded border px-2 py-0.5 text-xs font-medium ${cls}`}>
      {trLabel(SEVERITY_TR, severity)}
    </span>
  );
}

const stateStyles: Record<string, string> = {
  ONLINE: "text-emerald-700 dark:text-emerald-300",
  DEGRADED: "text-amber-700 dark:text-amber-300",
  OFFLINE: "text-rose-700 dark:text-rose-300",
  UNKNOWN: "text-muted",
};

export function StateDot({ state }: { state: string }) {
  return (
    <span className={`font-medium ${stateStyles[state] ?? "text-muted"}`}>
      ● {trLabel(STATE_TR, state)}
    </span>
  );
}

export function SourcePill({ source }: { source: DataSource }) {
  const live = source === "live";
  return (
    <span
      className={`rounded-full border px-2 py-0.5 text-xs ${
        live
          ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
          : "border-slate-500/40 bg-slate-500/10 text-muted"
      }`}
    >
      {live ? trLabel(SOURCE_TR, "live") : trLabel(SOURCE_TR, "sample")}
    </span>
  );
}

export function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-edge bg-panel p-4">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-fg">{value}</div>
      {hint ? <div className="mt-1 text-xs text-muted">{hint}</div> : null}
    </div>
  );
}

export function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-edge bg-panel p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted">{title}</h2>
      {children}
    </section>
  );
}
