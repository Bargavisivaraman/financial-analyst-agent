import { motion } from "framer-motion";
import { BarChart3, FileText, Newspaper, PenLine, Shield, Satellite } from "lucide-react";

const FEATURES = [
  { n: "01", icon: Satellite, title: "Market Data", desc: "Real LLM tool-calling — the model autonomously decides to fetch live price, P/E, beta and news via function calls." },
  { n: "02", icon: BarChart3, title: "Fundamental Analyst", desc: "Reasons over valuation, growth and margins to form a bullish / neutral / bearish lean." },
  { n: "03", icon: FileText, title: "SEC Filings (RAG)", desc: "Fetches the latest 10-K from EDGAR, retrieves the most relevant passages, and grounds its analysis in primary source with citations." },
  { n: "04", icon: Newspaper, title: "News & Sentiment", desc: "Scores recent headlines from -1 to +1 and flags material legal or regulatory risks." },
  { n: "05", icon: Shield, title: "Risk Manager", desc: "Blends a deterministic quant score with LLM judgment — and can veto a recommendation outright." },
  { n: "06", icon: PenLine, title: "Report Writer", desc: "Synthesizes every signal into a concise, risk-aware memo with a clear BUY / HOLD / SELL call." },
];

export default function HowItWorks() {
  return (
    <section id="how" className="border-t border-edge py-16">
      <div className="mx-auto max-w-6xl px-6">
        <p className="mb-2.5 text-xs font-semibold uppercase tracking-[2px] text-accent">
          How it works
        </p>
        <h2 className="mb-3 text-3xl font-extrabold tracking-tight">
          A supervisor orchestrating six specialists
        </h2>
        <p className="mb-9 max-w-xl text-muted">
          This isn't a single prompt. A supervisor agent plans the work, dispatches each specialist,
          runs a reflection loop on weak output, and lets the Risk Manager veto the final call.
        </p>
        <div className="grid gap-4 md:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.n}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="group rounded-2xl border border-edge bg-panel p-6 transition-all hover:-translate-y-1 hover:border-accent2"
            >
              <div className="mb-3.5 flex items-center justify-between">
                <div className="grid h-10 w-10 place-items-center rounded-xl border border-edge bg-gradient-to-br from-[#1a2236] to-[#141b2b]">
                  <f.icon className="h-5 w-5 text-accent" />
                </div>
                <span className="font-mono text-xs text-faint">{f.n}</span>
              </div>
              <h3 className="mb-2 text-base font-semibold">{f.title}</h3>
              <p className="text-[13.5px] text-muted">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
