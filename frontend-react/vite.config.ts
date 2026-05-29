import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: proxy API + SSE to the FastAPI backend on :8000.
// Build: emits static assets into dist/, served by FastAPI in production.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
  build: { outDir: "dist", emptyOutDir: true },
});
