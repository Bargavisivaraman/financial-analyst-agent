import { Area, AreaChart, ResponsiveContainer, Tooltip, YAxis } from "recharts";
import type { MarketData } from "../api";
import { fmtCap, fmtNum, fmtPct } from "../format";

export default function PriceChart({ market }: { market: MarketData }) {
  const data = market.price_history || [];
  const up = (market.change_pct_1m ?? 0) >= 0;
  const color = up ? "#34d399" : "#f87171";

  const stats = [
    { k: "Price", v: market.price ? `$${market.price}` : "—" },
    { k: "1M", v: fmtPct(market.change_pct_1m) },
    { k: "P/E", v: fmtNum(market.pe_ratio ? Number(market.pe_ratio.toFixed?.(1) ?? market.pe_ratio) : null) },
    { k: "Mkt Cap", v: fmtCap(market.market_cap) },
    { k: "Beta", v: fmtNum(market.beta) },
  ];

  return (
    <div className="rounded-xl border border-edge bg-panel2 p-5">
      <div className="mb-2 flex items-center justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-[1.5px] text-muted">
          {market.ticker} · 1M Price
        </p>
        <span className="rounded-md border border-edge px-2 py-0.5 text-[10px] text-faint">
          {market.source}
        </span>
      </div>
      <div className="h-[120px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <YAxis domain={["dataMin", "dataMax"]} hide />
            <Tooltip
              contentStyle={{
                background: "#0d1320",
                border: "1px solid #1f2937",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelStyle={{ display: "none" }}
              formatter={(v: number) => [`$${v}`, "Close"]}
            />
            <Area type="monotone" dataKey="close" stroke={color} strokeWidth={2} fill="url(#pg)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 grid grid-cols-5 gap-2">
        {stats.map((s) => (
          <div key={s.k} className="rounded-lg border border-edge bg-panel px-2 py-2 text-center">
            <div className="text-[10px] uppercase tracking-wide text-faint">{s.k}</div>
            <div className="mt-0.5 text-[13px] font-semibold text-slate-200">{s.v}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
