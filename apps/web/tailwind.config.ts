import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  // Koyu varsayılan: html[data-theme="dark"] iken `dark:` yardımcıları devreye girer.
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        ink: "var(--ink)",
        panel: "var(--panel)",
        edge: "var(--edge)",
        muted: "var(--muted)",
        accent: "var(--accent)",
        fg: "var(--fg)",
      },
    },
  },
  plugins: [],
};

export default config;
