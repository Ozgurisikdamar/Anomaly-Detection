"use client";

import { useEffect, useState } from "react";

type Theme = "dark" | "light";
const STORAGE_KEY = "sg-theme";

function currentTheme(): Theme {
  if (typeof document === "undefined") return "dark";
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

/**
 * Aydınlık/Karanlık tema anahtarı.
 * Seçim localStorage("sg-theme") içinde saklanır; ilk boyama layout.tsx'teki
 * satır-içi script tarafından uygulanır (FOUC yok). Varsayılan: karanlık.
 */
export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("dark");

  // İlk mount'ta DOM'daki gerçek değerle senkronla (hydration güvenli).
  useEffect(() => {
    setTheme(currentTheme());
  }, []);

  function toggle() {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* özel pencere / depolama kapalı — yok say */
    }
  }

  const isDark = theme === "dark";
  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={isDark ? "Gündüz moduna geç" : "Gece moduna geç"}
      title={isDark ? "Gündüz modu" : "Gece modu"}
      className="flex w-full items-center justify-between rounded-lg border border-edge px-3 py-2 text-sm text-muted hover:bg-edge hover:text-fg"
    >
      <span>{isDark ? "Gündüz modu" : "Gece modu"}</span>
      <span aria-hidden className="text-base leading-none">
        {isDark ? "☀" : "☾"}
      </span>
    </button>
  );
}
