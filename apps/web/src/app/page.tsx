import Link from "next/link";

import { loadCameras, loadCheckouts, loadEvents } from "@/lib/api";
import { EVENT_TYPE_TR, STATUS_TR, trLabel } from "@/lib/tr";
import { Panel, SeverityBadge, SourcePill, StatCard } from "@/lib/ui";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  const [{ data: events, source }, cameras, checkouts] = await Promise.all([
    loadEvents(),
    loadCameras(),
    loadCheckouts(),
  ]);

  const open = events.filter((e) => e.status === "OPEN");
  const cameraCount = cameras.data.length;

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-fg">Genel Bakış</h1>
          <p className="text-sm text-muted">
            StoreGuard Demo Market · aşağıdaki değerler DEMO/SİMÜLASYON'dur
          </p>
        </div>
        <SourcePill source={source} />
      </header>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Kameralar" value={`${cameraCount}`} hint="sağlık için Kameralar'a bakın" />
        <StatCard label="Açık incelemeler" value={`${open.length}`} hint="insan incelemesi bekliyor" />
        <StatCard
          label="Self-checkout terminalleri"
          value={`${checkouts.data.length}`}
          hint="simüle akışlar"
        />
        <StatCard label="Algılama gecikmesi" value="— ms" hint="kıyaslamada ölçüldü" />
      </div>

      <Panel title="Son inceleme olayları">
        <ul className="divide-y divide-edge">
          {events.slice(0, 5).map((e) => (
            <li key={e.event_id} className="flex items-center justify-between py-2 text-sm">
              <div className="flex items-center gap-3">
                <SeverityBadge severity={e.severity} />
                <Link
                  href={`/alerts/${e.event_id}`}
                  className="font-medium text-fg hover:underline"
                >
                  {trLabel(EVENT_TYPE_TR, e.event_type)}
                </Link>
                <span className="text-muted">{e.camera_id}</span>
              </div>
              <span className="text-xs text-muted">{trLabel(STATUS_TR, e.status)}</span>
            </li>
          ))}
        </ul>
      </Panel>

      <Panel title="Ürün ilkeleri (demo tarafından uygulanır)">
        <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
          <li>Alarmlar gözlemlenebilir operasyonel anomalileri tanımlar — hırsızlık, niyet veya kişi değil.</li>
          <li>Eksik entegrasyon verisi BİLİNMİYOR'dur, asla bir ihlal değildir.</li>
          <li>POS / tarayıcı / tartı sinyalleri, gerçek entegrasyonlar doğrulanana dek SİMÜLASYON'dur.</li>
          <li>Yüz tanıma, biyometri veya kameralar arası yeniden-kimliklendirme yoktur.</li>
        </ul>
      </Panel>
    </div>
  );
}
