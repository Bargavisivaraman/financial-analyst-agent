import { motion } from "framer-motion";
import type { RiskData } from "../api";

const BAND_COLOR: Record<string, string> = {
  Low: "#34d399",
  Moderate: "#fbbf24",
  High: "#fb923c",
  Severe: "#f87171",
};

export default function RiskGauge({ risk }: { risk: RiskData }) {
  const c = BAND_COLOR[risk.risk_band] || "#fbbf24";
  const R = 52;
  const CIRC = Math.PI * R; // half circle
  const pct = Math.min(100, Math.max(0, risk.risk_score)) / 100;

  return (
    <div className="rounded-xl border border-edge bg-panel2 p-5">
      <p className="mb-1 text-[11px] font-semibold uppercase tracking-[1.5px] text-muted">
        Risk Score
      </p>
      <div className="flex items-center gap-5">
        <div className="relative h-[72px] w-[130px]">
          <svg viewBox="0 0 130 72" className="h-full w-full">
            <path
              d="M 9 66 A 56 56 0 0 1 121 66"
              fill="none"
              stroke="#1f2937"
              strokeWidth="10"
              strokeLinecap="round"
            />
            <motion.path
              d="M 9 66 A 56 56 0 0 1 121 66"
              fill="none"
              stroke={c}
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={CIRC}
              initial={{ strokeDashoffset: CIRC }}
              animate={{ strokeDashoffset: CIRC * (1 - pct) }}
              transition={{ duration: 0.9, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
            <span className="text-2xl font-extrabold" style={{ color: c }}>
              {risk.risk_score}
            </span>
            <span className="text-[10px] text-faint">/ 100</span>
          </div>
        </div>
        <div>
          <span
            className="rounded-full px-3 py-1 text-xs font-bold"
            style={{ background: `${c}22`, color: c, border: `1px solid ${c}` }}
          >
            {risk.risk_band}
          </span>
          {risk.veto && (
            <div className="mt-2 text-sm font-bold text-red-400">⛔ RISK VETO ISSUED</div>
          )}
        </div>
      </div>
      {risk.flags?.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {risk.flags.map((f, i) => (
            <span
              key={i}
              className="rounded-md border border-[#2a3346] bg-[#1a2230] px-2 py-1 text-[11px] text-amber-300"
            >
              {f}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
