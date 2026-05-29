import { Github, Zap } from "lucide-react";
import type { Health } from "../api";

export default function Nav({ health }: { health: Health | null }) {
  const live = health?.llm_mode === "live";
  return (
    <nav className="sticky top-0 z-50 border-b border-edge bg-bg/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <a href="#top" className="flex items-center gap-2 font-extrabold">
          <Zap className="h-5 w-5 text-accent" />
          <span>
            Financial <span className="gradient-text">Analyst</span>
          </span>
        </a>
        <div className="flex items-center gap-6 text-sm text-muted">
          <a href="#how" className="hidden transition-colors hover:text-white sm:block">
            How it works
          </a>
          <a href="#architecture" className="hidden transition-colors hover:text-white sm:block">
            Architecture
          </a>
          <span
            className={`rounded-full border px-3 py-1 text-[11px] ${
              live ? "border-emerald-800 bg-emerald-950/40 text-emerald-300" : "border-edge text-muted"
            }`}
          >
            {health ? (live ? `LIVE · ${health.model}` : "MOCK mode") : "…"}
          </span>
          <a
            href="https://github.com/Bargavisivaraman/financial-analyst-agent"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 transition-colors hover:text-white"
          >
            <Github className="h-4 w-4" /> GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}
