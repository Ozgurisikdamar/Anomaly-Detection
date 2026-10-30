import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "StoreGuard Dashboard",
  description: "Retail loss-prevention demo dashboard (Phase 0 scaffold, SIMULATED data).",
};

const nav = [
  { href: "/", label: "Overview" },
  { href: "/alerts", label: "Alerts inbox" },
  { href: "/cameras", label: "Cameras" },
  { href: "/checkouts", label: "Checkout monitor" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink text-slate-100 antialiased">
        {/* Non-negotiable: demo data is always visibly labelled. */}
        <div className="w-full bg-amber-500/15 py-1.5 text-center text-xs font-medium text-amber-200">
          SCAFFOLD · All data is SIMULATED — no real camera, POS, scanner or scale is connected.
          Every alert is a human-review task; nobody is labelled.
        </div>
        <div className="flex min-h-[calc(100vh-28px)]">
          <aside className="hidden w-60 shrink-0 border-r border-edge bg-panel p-5 md:block">
            <div className="mb-6">
              <div className="text-lg font-bold text-white">StoreGuard</div>
              <div className="text-xs text-muted">Loss-prevention demo</div>
            </div>
            <nav className="space-y-1">
              {nav.map((n) => (
                <Link
                  key={n.href}
                  href={n.href}
                  className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-edge hover:text-white"
                >
                  {n.label}
                </Link>
              ))}
            </nav>
            <div className="mt-8 rounded-lg border border-edge p-3 text-xs text-muted">
              Phase 0 scaffold. Vision/ML not implemented yet.
            </div>
          </aside>
          <main className="flex-1 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
