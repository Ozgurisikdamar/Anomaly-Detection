import Link from "next/link";

import { loadEvent } from "@/lib/api";
import { Panel, SeverityBadge, SourcePill } from "@/lib/ui";

export const dynamic = "force-dynamic";

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 py-1 text-sm">
      <span className="text-muted">{label}</span>
      <span className="text-right text-slate-100">{value}</span>
    </div>
  );
}

export default async function EventDetailPage({ params }: { params: { id: string } }) {
  const { data: event, source } = await loadEvent(params.id);

  if (!event) {
    return (
      <div className="space-y-4">
        <Link href="/alerts" className="text-sm text-accent hover:underline">
          ← Back to alerts
        </Link>
        <p className="text-slate-300">Event not found.</p>
      </div>
    );
  }

  const conf = event.confidence;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <Link href="/alerts" className="text-sm text-accent hover:underline">
          ← Back to alerts
        </Link>
        <SourcePill source={source} />
      </div>

      <header className="flex flex-wrap items-center gap-3">
        <SeverityBadge severity={event.severity} />
        <h1 className="text-2xl font-bold text-white">{event.event_type}</h1>
        {event.simulated ? (
          <span className="rounded bg-amber-500/15 px-2 py-0.5 text-xs text-amber-200">SIMULATED</span>
        ) : null}
      </header>

      <p className="max-w-3xl text-sm leading-relaxed text-slate-300">{event.explanation}</p>

      <div className="grid gap-4 md:grid-cols-2">
        <Panel title="Event">
          <Row label="Event ID" value={event.event_id} />
          <Row label="Status" value={event.status} />
          <Row label="Camera" value={event.camera_id} />
          <Row label="Zone" value={event.zone_id ?? "—"} />
          <Row label="Detected" value={new Date(event.detected_at).toISOString()} />
          <Row label="Human review required" value={event.human_review_required ? "YES" : "no"} />
        </Panel>

        <Panel title="Confidence components">
          <Row label="Detector" value={conf.detector ?? "— (n/a)"} />
          <Row label="Track quality" value={conf.track_quality ?? "— (n/a)"} />
          <Row label="Zone certainty" value={conf.zone_certainty ?? "— (n/a)"} />
          <Row label="POS synchronization" value={conf.pos_synchronization ?? "— (n/a)"} />
          <Row label="Rule evidence" value={conf.rule_evidence ?? "— (n/a)"} />
        </Panel>

        <Panel title="Reason codes & missing signals">
          <div className="mb-2 flex flex-wrap gap-2">
            {event.reason_codes.map((r) => (
              <span key={r} className="rounded bg-edge px-2 py-0.5 text-xs text-slate-200">
                {r}
              </span>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            {event.missing_data_flags.length === 0 ? (
              <span className="text-xs text-muted">no missing-data flags</span>
            ) : (
              event.missing_data_flags.map((m) => (
                <span key={m} className="rounded bg-slate-500/20 px-2 py-0.5 text-xs text-slate-300">
                  ⚠ {m}
                </span>
              ))
            )}
          </div>
        </Panel>

        <Panel title="Versions & review actions">
          <Row label="Model version" value={event.model_version ?? "—"} />
          <Row label="Tracker version" value={event.tracker_version ?? "—"} />
          <Row label="Rule version" value={event.rule_version ?? "—"} />
          <div className="mt-3 flex gap-2">
            <button className="rounded-lg border border-edge bg-edge px-3 py-1.5 text-xs text-slate-200" disabled>
              Acknowledge
            </button>
            <button className="rounded-lg border border-edge bg-edge px-3 py-1.5 text-xs text-slate-200" disabled>
              Resolve
            </button>
            <button className="rounded-lg border border-edge bg-edge px-3 py-1.5 text-xs text-slate-200" disabled>
              Dismiss
            </button>
          </div>
          <p className="mt-2 text-[11px] text-muted">
            Buttons are scaffold placeholders; the API exposes these actions (Phase 5 wires them up).
          </p>
        </Panel>
      </div>
    </div>
  );
}
