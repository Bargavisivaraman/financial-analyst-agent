import { useState } from "react";
import { ArrowRight } from "lucide-react";
import type { AgentId } from "../api";
import { useAnalysis } from "../api";
import AgentGraph from "./AgentGraph";
import TracePanel from "./TracePanel";
import ResultsPanel from "./ResultsPanel";

const EXAMPLES = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"];

const AGENT_META: { id: AgentId; name: string; role: string }[] = [
  { id: "supervisor", name: "Supervisor", role: "orchestrates & routes" },
  { id: "market_data", name: "Market Data", role: "tool-calling · price" },
  { id: "fundamental", name: "Fundamental", role: "growth & margins" },
  { id: "filings", name: "SEC Filings", role: "RAG over 10-K" },
  { id: "news_sentiment", name: "News & Sentiment", role: "headline scoring" },
  { id: "risk_manager", name: "Risk Manager", role: "risk score · veto" },
  { id: "report_writer", name: "Report Writer", role: "final memo" },
];

export default function Analyzer() {
  const [ticker, setTicker] = useState("");
  const { status, trace, active, done, result, run } = useAnalysis();
  const busy = status === "running";

  const submit = (t?: string) => {
    const tk = (t ?? ticker).trim().toUpperCase() || "AAPL";
    setTicker(tk);
    if (!busy) run(tk);
  };

  return (
    <div className="rounded-2xl border border-edge bg-panel p-5 shadow-2xl shadow-black/40">
      <div className="flex gap-2.5">
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Enter a ticker — e.g. AAPL"
          className="flex-1 rounded-xl border border-edge bg-panel2 px-4 py-3.5 text-base uppercase outline-none focus:border-accent2"
        />
        <button
          onClick={() => submit()}
          disabled={busy}
          className="flex items-center gap-1.5 whitespace-nowrap rounded-xl bg-gradient-to-br from-accent2 to-accent px-6 py-3.5 font-extrabold text-[#06121a] transition-opacity disabled:opacity-50"
        >
          {busy ? "Analyzing…" : "Analyze"} <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-3.5 flex flex-wrap items-center gap-2">
        <span className="text-[12.5px] text-faint">Try:</span>
        {EXAMPLES.map((t) => (
          <button
            key={t}
            onClick={() => submit(t)}
            className="rounded-lg border border-edge bg-panel2 px-3 py-1 text-[13px] text-muted transition-colors hover:border-accent2 hover:text-white"
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[340px_1fr]">
        <div className="space-y-4">
          <div className="rounded-xl border border-edge bg-panel2 p-3">
            <p className="mb-1 px-1 text-[11px] font-semibold uppercase tracking-[1.5px] text-muted">
              Agent Graph
            </p>
            <div className="h-[200px]">
              <AgentGraph active={active} done={done} />
            </div>
          </div>
          <div className="space-y-2">
            {AGENT_META.map((a) => {
              const isActive = active === a.id;
              const isDone = done.has(a.id);
              return (
                <div
                  key={a.id}
                  className={`flex items-center gap-3 rounded-lg border bg-panel2 px-3 py-2.5 transition-all ${
                    isActive ? "glow-accent border-accent" : isDone ? "border-emerald-900" : "border-edge"
                  }`}
                >
                  <span
                    className={`h-2.5 w-2.5 flex-none rounded-full ${
                      isActive ? "animate-pulseDot bg-accent" : isDone ? "bg-emerald-400" : "bg-edge"
                    }`}
                  />
                  <div>
                    <div className="text-[13.5px]">{a.name}</div>
                    <div className="text-[11px] text-muted">{a.role}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <TracePanel trace={trace} />
          {result && <ResultsPanel result={result} />}
        </div>
      </div>
    </div>
  );
}
