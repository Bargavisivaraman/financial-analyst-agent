const STACK = [
  "Python", "FastAPI", "Server-Sent Events", "React", "TypeScript", "Tailwind",
  "Recharts", "Groq · Llama 3.3", "LLM tool-calling", "TF-IDF RAG", "SEC EDGAR",
  "yfinance", "Docker",
];

export default function Architecture() {
  return (
    <section id="architecture" className="border-t border-edge py-16">
      <div className="mx-auto max-w-6xl px-6">
        <p className="mb-2.5 text-xs font-semibold uppercase tracking-[2px] text-accent">
          Architecture
        </p>
        <h2 className="mb-3 text-3xl font-extrabold tracking-tight">
          Hierarchical multi-agent graph
        </h2>
        <p className="mb-7 max-w-xl text-muted">
          A hand-rolled, LangGraph-style state machine streams every transition to this UI over
          Server-Sent Events.
        </p>
        <img
          src="/architecture.svg"
          alt="architecture diagram"
          className="w-full rounded-2xl border border-edge bg-[#0a0e17]"
          onError={(e) => ((e.target as HTMLImageElement).style.display = "none")}
        />
        <p className="mb-3 mt-9 text-xs font-semibold uppercase tracking-[2px] text-accent">
          Built with
        </p>
        <div className="flex flex-wrap gap-2.5">
          {STACK.map((s) => (
            <span
              key={s}
              className="rounded-lg border border-edge bg-panel px-3.5 py-1.5 text-[13px] text-muted"
            >
              {s}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
