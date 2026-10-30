import Link from "next/link";

import { loadEvents } from "@/lib/api";
import { SeverityBadge, SourcePill } from "@/lib/ui";

export const dynamic = "force-dynamic";

export default async function AlertsPage() {
  const { data: events, source } = await loadEvents();

  return (
    <div className="space-y-5">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Alerts inbox</h1>
          <p className="text-sm text-muted">{events.length} events · all require human review</p>
        </div>
        <SourcePill source={source} />
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
                  <Link href={`/alerts/${e.event_id}`} className="font-medium text-slate-100 hover:underline">
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
