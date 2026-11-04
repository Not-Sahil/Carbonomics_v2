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
        carbon: {
          bg: "#090D14",
          subtle: "#111827",
          card: "#151D2B",
          cardHover: "#1C273A",
          border: "#1F2D42",
          borderSubtle: "#172334",
          primary: "#16C784",
          primaryHover: "#14B577",
          cyan: "#38BDF8",
          warning: "#F5B942",
          danger: "#F16C6C",
          text: "#F8FAFC",
          muted: "#94A3B8",
          dim: "#64748B",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;

