import type { Metadata } from "next";
import Link from "next/link";

import { UI } from "@/lib/tr";

import "./globals.css";

export const metadata: Metadata = {
  title: "StoreGuard — Kayıp Önleme Konsolu",
  description: "Perakende kayıp-önleme demo panosu (SİMÜLASYON veri).",
};

const nav = [
  { href: "/", label: UI.nav.overview },
  { href: "/alerts", label: UI.nav.alerts },
  { href: "/cameras", label: UI.nav.cameras },
  { href: "/checkouts", label: UI.nav.checkouts },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body className="min-h-screen bg-ink text-slate-100 antialiased">
        {/* Değişmez kural: demo verisi her zaman görünür şekilde etiketlenir. */}
        <div className="w-full bg-amber-500/15 py-1.5 text-center text-xs font-medium text-amber-200">
          {UI.banner}
        </div>
        <div className="flex min-h-[calc(100vh-28px)]">
          <aside className="hidden w-60 shrink-0 border-r border-edge bg-panel p-5 md:block">
            <div className="mb-6">
              <div className="text-lg font-bold text-white">{UI.appName}</div>
              <div className="text-xs text-muted">{UI.tagline}</div>
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
              {UI.sidebarNote}
            </div>
          </aside>
          <main className="flex-1 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
