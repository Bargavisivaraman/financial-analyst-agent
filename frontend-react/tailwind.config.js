/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#070b12",
        panel: "#111726",
        panel2: "#0d1320",
        edge: "#1f2937",
        accent: "#5eead4",
        accent2: "#818cf8",
        accent3: "#c084fc",
        muted: "#8b95a7",
        faint: "#5b6678",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["SF Mono", "ui-monospace", "Menlo", "monospace"],
      },
      keyframes: {
        pulseDot: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.3" } },
        shimmer: { "100%": { transform: "translateX(100%)" } },
      },
      animation: {
        pulseDot: "pulseDot 1s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
