import { useCallback, useEffect, useRef, useState } from "react";

export type AgentId =
  | "supervisor"
  | "market_data"
  | "fundamental"
  | "filings"
  | "news_sentiment"
  | "risk_manager"
  | "report_writer";

export interface TraceEvent {
  type: "trace";
  agent: AgentId;
  message: string;
  ts: number;
}

export interface PricePoint {
  t: number;
  close: number;
}

export interface MarketData {
  source: string;
  ticker: string;
  price: number | null;
  change_pct_1m: number | null;
  pe_ratio: number | null;
  market_cap: number | null;
  beta: number | null;
  volatility_30d: number | null;
  revenue_growth_yoy: number | null;
  profit_margin: number | null;
  price_history: PricePoint[];
}

export interface RiskData {
  risk_score: number;
  risk_band: "Low" | "Moderate" | "High" | "Severe";
  veto: boolean;
  flags: string[];
  rationale: string;
}

export interface FilingsData {
  source: string;
  url: string | null;
  passages: string[];
  analysis: string;
}

export interface NewsData {
  headlines: string[];
  summary: string;
  score: number;
}

export interface ResultEvent {
  type: "result";
  ticker: string;
  market: MarketData;
  fundamental: string;
  filings: FilingsData;
  news: NewsData;
  risk: RiskData;
  memo: string;
}

export interface Health {
  status: string;
  llm_mode: "live" | "mock";
  provider: string;
  model: string;
}

export type RunStatus = "idle" | "running" | "done" | "error";

export function useHealth(): Health | null {
  const [health, setHealth] = useState<Health | null>(null);
  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => {});
  }, []);
  return health;
}

export function useAnalysis() {
  const [status, setStatus] = useState<RunStatus>("idle");
  const [trace, setTrace] = useState<TraceEvent[]>([]);
  const [active, setActive] = useState<AgentId | null>(null);
  const [done, setDone] = useState<Set<AgentId>>(new Set());
  const [result, setResult] = useState<ResultEvent | null>(null);
  const esRef = useRef<EventSource | null>(null);

  const run = useCallback((ticker: string) => {
    esRef.current?.close();
    setStatus("running");
    setTrace([]);
    setActive(null);
    setDone(new Set());
    setResult(null);

    const es = new EventSource(`/api/analyze?ticker=${encodeURIComponent(ticker)}`);
    esRef.current = es;

    es.onmessage = (e) => {
      const ev = JSON.parse(e.data);
      if (ev.type === "trace") {
        setActive(ev.agent);
        setTrace((t) => [...t, ev]);
        const msg = (ev.message as string).toLowerCase();
        if (
          ev.agent !== "supervisor" &&
          (msg.includes("complete") || msg.includes("got") || msg.includes("ready") || msg.includes("score:"))
        ) {
          setDone((d) => new Set(d).add(ev.agent));
        }
        if (msg.includes("cleared") || msg.includes("veto")) {
          setDone((d) => new Set(d).add("risk_manager"));
        }
      } else if (ev.type === "result") {
        setResult(ev);
        setDone(new Set(["supervisor", "market_data", "fundamental", "filings", "news_sentiment", "risk_manager", "report_writer"]));
        setActive(null);
      } else if (ev.type === "done") {
        es.close();
        setStatus("done");
      }
    };
    es.onerror = () => {
      es.close();
      setStatus((s) => (s === "done" ? s : "error"));
    };
  }, []);

  useEffect(() => () => esRef.current?.close(), []);

  return { status, trace, active, done, result, run };
}
