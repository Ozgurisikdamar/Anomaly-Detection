import { AlertsLive } from "@/components/AlertsLive";
import { loadEvents } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function AlertsPage() {
  // Initial server-side fetch (live/sample); the client then subscribes to SSE.
  const { data: events } = await loadEvents();
  return <AlertsLive initialEvents={events} />;
}
