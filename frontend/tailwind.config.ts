import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        surface: {
          DEFAULT: "var(--surface)",
          muted: "var(--surface-muted)",
          border: "var(--surface-border)",
        },
        peexh: {
          brand: "#2563eb",
          "brand-hover": "#1d4ed8",
          listening: "#dc2626",
          confidence: {
            high: "#16a34a",
            medium: "#d97706",
            low: "#dc2626",
          },
        },
      },
    },
  },
  plugins: [],
};

export default config;
