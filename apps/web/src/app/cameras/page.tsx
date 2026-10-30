import { loadCameras } from "@/lib/api";
import { SourcePill, StateDot } from "@/lib/ui";

export const dynamic = "force-dynamic";

export default async function CamerasPage() {
  const { data: cameras, source } = await loadCameras();

  return (
    <div className="space-y-5">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Cameras</h1>
          <p className="text-sm text-muted">Health is SIMULATED; real FPS / frame-age arrive in Phase 2.</p>
        </div>
        <SourcePill source={source} />
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cameras.map((c: { camera_id: string; name: string; kind: string; state: string; fps: number | null }) => (
          <div key={c.camera_id} className="rounded-xl border border-edge bg-panel p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-semibold text-white">{c.name}</div>
                <div className="text-xs text-muted">{c.camera_id} · {c.kind}</div>
              </div>
              <StateDot state={c.state} />
            </div>
            {/* Placeholder preview tile; live overlays/zone polygons come later. */}
            <div className="mt-3 flex h-28 items-center justify-center rounded-lg border border-dashed border-edge text-xs text-muted">
              preview placeholder
            </div>
            <div className="mt-3 flex justify-between text-xs text-muted">
              <span>FPS: {c.fps ?? "—"}</span>
              <span>SIMULATED</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
