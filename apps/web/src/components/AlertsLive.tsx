"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { AnomalyEvent } from "@storeguard/contracts";

import { SeverityBadge } from "@/lib/ui";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export function AlertsLive({ initialEvents }: { initialEvents: AnomalyEvent[] }) {
  const [events, setEvents] = useState<AnomalyEvent[]>(initialEvents);
  const [live, setLive] = useState(false);

  useEffect(() => {
    let es: EventSource | null = null;
    try {
      es = new EventSource(`${API_BASE}/api/v1/stream/events`);
      es.onopen = () => setLive(true);
      es.onerror = () => setLive(false);
      es.onmessage = (m) => {
        try {
          const { kind, event } = JSON.parse(m.data) as { kind: string; event: AnomalyEvent };
          if (!event?.event_id) return;
          setEvents((prev) => {
            const rest = prev.filter((e) => e.event_id !== event.event_id);
            // new events go to the top; updates replace in place at the top too
            return kind === "event.new" || kind === "event.updated"
              ? [event, ...rest]
              : prev;
          });
        } catch {
          /* ignore malformed */
        }
      };
    } catch {
      setLive(false);
    }
    return () => es?.close();
  }, []);

  return (
    <div className="space-y-5">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Alerts inbox</h1>
          <p className="text-sm text-muted">{events.length} events · all require human review</p>
        </div>
        <span
          className={`rounded-full border px-2 py-0.5 text-xs ${
            live
              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
              : "border-slate-500/40 bg-slate-500/10 text-slate-300"
          }`}
        >
          {live ? "● live (SSE)" : "○ not live"}
        </span>
      </header>

      <div className="overflow-hidden rounded-xl border border-edge">
        <table className="w-full text-left text-sm">
          <thead className="bg-panel text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Event type</th>
              <th className="px-4 py-3">Camera</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Detected</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-edge bg-ink">
            {events.map((e) => (
              <tr key={e.event_id} className="hover:bg-panel/60">
                <td className="px-4 py-3">
                  <SeverityBadge severity={e.severity} />
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/alerts/${e.event_id}`}
                    className="font-medium text-slate-100 hover:underline"
                  >
                    {e.event_type}
                  </Link>
                  {e.missing_data_flags.length > 0 ? (
                    <span className="ml-2 rounded bg-slate-500/15 px-1.5 py-0.5 text-[10px] text-slate-300">
                      missing data
                    </span>
                  ) : null}
                </td>
                <td className="px-4 py-3 text-muted">{e.camera_id}</td>
                <td className="px-4 py-3 text-muted">{e.status}</td>
                <td className="px-4 py-3 text-xs text-muted">
                  {new Date(e.detected_at).toISOString().replace("T", " ").slice(0, 19)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
