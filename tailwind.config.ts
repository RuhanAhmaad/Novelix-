import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        novelix: {
          950: "#060608",
          900: "#0b0b10",
          850: "#101018",
          800: "#161622",
          750: "#1e1e2f",
          700: "#27273d",
          600: "#3d3d5c",
          500: "#6366f1",
          400: "#818cf8",
          purple: "#9333ea",
          violet: "#a855f7",
          electric: "#8b5cf6",
          neon: "#c084fc",
          gold: "#f59e0b",
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "hero-glow": "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139, 92, 246, 0.25), transparent)",
        "card-glass": "linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)",
      },
      boxShadow: {
        "glow-sm": "0 0 15px -3px rgba(139, 92, 246, 0.3)",
        "glow-md": "0 0 25px -5px rgba(139, 92, 246, 0.4)",
        "glow-lg": "0 0 40px -8px rgba(168, 85, 247, 0.5)",
      },
      keyframes: {
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        pulseSlow: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },
      animation: {
        shimmer: "shimmer 2s infinite",
        "pulse-slow": "pulseSlow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
export default config;
