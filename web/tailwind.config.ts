import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#F7F7F8",
        void: "#08090D",
        panel: "#111318",
        panel2: "#171A21",
        line: "rgba(255,255,255,0.10)",
        teal: "#2DD4BF",
        blue: "#60A5FA",
        coral: "#FB7185",
        gold: "#FBBF24"
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans TC", "system-ui", "sans-serif"],
        mono: ["SFMono-Regular", "ui-monospace", "Menlo", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
