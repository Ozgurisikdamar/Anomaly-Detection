"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type { AnomalyEvent } from "@storeguard/contracts";

import {
  EVENT_TYPE_TR,
  eventSourceLabel,
  relativeTimeTr,
  STATUS_TR,
  trLabel,
} from "@/lib/tr";
import { SeverityBadge } from "@/lib/ui";

import { CctvScene, sceneKind } from "./CctvScene";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const STATUS_FILTERS = ["ALL", "OPEN", "ACKNOWLEDGED", "RESOLVED", "DISMISSED"] as const;

export function AlertsLive({ initialEvents }: { initialEvents: AnomalyEvent[] }) {
  const [events, setEvents] = useState<AnomalyEvent[]>(initialEvents);
  const [live, setLive] = useState(false);
  const [filter, setFilter] = useState<(typeof STATUS_FILTERS)[number]>("ALL");

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
            return kind === "event.new" || kind === "event.updated" ? [event, ...rest] : prev;
          });
        } catch {
          /* bozuk mesajı yok say */
        }
      };
    } catch {
      setLive(false);
    }
    return () => es?.close();
  }, []);

  const shown = useMemo(
    () => (filter === "ALL" ? events : events.filter((e) => e.status === filter)),
    [events, filter],
  );

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Alarmlar</h1>
          <p className="text-sm text-muted">
            {shown.length} olay · tümü insan incelemesi gerektirir
          </p>
        </div>
        <span
          className={`rounded-full border px-2 py-0.5 text-xs ${
            live
              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
              : "border-slate-500/40 bg-slate-500/10 text-slate-300"
          }`}
        >
          {live ? "● canlı (SSE)" : "○ bağlı değil"}
        </span>
      </header>

      {/* durum filtreleri */}
      <div className="flex flex-wrap gap-2">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-full border px-3 py-1 text-xs ${
              filter === f
                ? "border-accent bg-accent/15 text-accent"
                : "border-edge bg-panel text-muted hover:text-slate-200"
            }`}
          >
            {f === "ALL" ? "Tümü" : trLabel(STATUS_TR, f)}
          </button>
        ))}
      </div>

      {/* alarm kartları ızgarası */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {shown.map((e) => {
          const url = e.evidence?.[0]?.available && e.evidence[0].url ? `${API_BASE}${e.evidence[0].url}` : null;
          return (
            <Link
              key={e.event_id}
              href={`/alerts/${e.event_id}`}
              className="group rounded-xl border border-edge bg-panel p-3 transition hover:border-accent/50"
            >
              <CctvScene
                kind={sceneKind(e.camera_id)}
                seed={e.event_id}
                evidenceUrl={url}
                timestamp={new Date(e.detected_at).toLocaleString("tr-TR", { hour12: false }).replace(",", "")}
              />
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <SeverityBadge severity={e.severity} />
                <span className="rounded border border-slate-500/40 bg-slate-500/10 px-1.5 py-0.5 text-[10px] text-slate-300">
                  {eventSourceLabel(e.model_version)}
                </span>
                {e.missing_data_flags.length > 0 ? (
                  <span className="rounded bg-slate-500/15 px-1.5 py-0.5 text-[10px] text-slate-300">
                    veri eksik
                  </span>
                ) : null}
              </div>
              <div className="mt-2 font-semibold text-slate-100 group-hover:text-white">
                {trLabel(EVENT_TYPE_TR, e.event_type)}
              </div>
              <div className="mt-1 flex items-center justify-between text-xs text-muted">
                <span>
                  {e.camera_id} · {relativeTimeTr(e.detected_at)}
                </span>
                <span className="rounded-full border border-edge px-2 py-0.5">
                  {trLabel(STATUS_TR, e.status)}
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
