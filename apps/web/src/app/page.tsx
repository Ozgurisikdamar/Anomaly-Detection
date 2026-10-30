import Link from "next/link";

import { loadCameras, loadCheckouts, loadEvents } from "@/lib/api";
import { Panel, SeverityBadge, SourcePill, StatCard } from "@/lib/ui";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  const [{ data: events, source }, cameras, checkouts] = await Promise.all([
    loadEvents(),
    loadCameras(),
    loadCheckouts(),
  ]);

  const open = events.filter((e) => e.status === "OPEN");
  // Per-camera health lives on the status endpoint, not the camera list, so the
  // overview shows the registry count here; the Cameras page shows health.
  const cameraCount = cameras.data.length;

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Overview</h1>
          <p className="text-sm text-muted">StoreGuard Demo Market · values below are DEMO/SIMULATED</p>
        </div>
        <SourcePill source={source} />
      </header>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Cameras" value={`${cameraCount}`} hint="see Cameras for health" />
        <StatCard label="Open reviews" value={`${open.length}`} hint="awaiting human review" />
        <StatCard label="Checkout terminals" value={`${checkouts.data.length}`} hint="simulated feeds" />
        <StatCard label="Detection latency" value="— ms" hint="measured in Phase 1" />
      </div>

      <Panel title="Latest review events">
        <ul className="divide-y divide-edge">
          {events.slice(0, 5).map((e) => (
            <li key={e.event_id} className="flex items-center justify-between py-2 text-sm">
              <div className="flex items-center gap-3">
                <SeverityBadge severity={e.severity} />
                <Link href={`/alerts/${e.event_id}`} className="font-medium text-slate-100 hover:underline">
                  {e.event_type}
                </Link>
                <span className="text-muted">{e.camera_id}</span>
              </div>
              <span className="text-xs text-muted">{e.status}</span>
            </li>
          ))}
        </ul>
      </Panel>

      <Panel title="Product principles (enforced by the demo)">
        <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
          <li>Alerts describe observable operational anomalies — never theft, intent, or a person.</li>
          <li>Missing integration data is UNKNOWN, never a violation.</li>
          <li>POS / scanner / scale signals are SIMULATED until real integrations are validated.</li>
          <li>No face recognition, biometrics, or cross-camera re-identification.</li>
        </ul>
      </Panel>
    </div>
  );
}
