import { motion } from "framer-motion";

export default function SentimentMeter({ score }: { score: number }) {
  const s = Math.max(-1, Math.min(1, score));
  const pctFromCenter = (s / 2) * 100; // -50%..+50%
  const color = s > 0.15 ? "#34d399" : s < -0.15 ? "#f87171" : "#fbbf24";
  const label = s > 0.15 ? "Bullish" : s < -0.15 ? "Bearish" : "Neutral";

  return (
    <div className="rounded-xl border border-edge bg-panel2 p-5">
      <div className="mb-2 flex items-center justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-[1.5px] text-muted">
          News Sentiment
        </p>
        <span className="text-sm font-bold" style={{ color }}>
          {label} ({s >= 0 ? "+" : ""}
          {s.toFixed(2)})
        </span>
      </div>
      <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-gradient-to-r from-red-500/40 via-amber-400/30 to-emerald-500/40">
        <div className="absolute left-1/2 top-0 h-full w-px bg-white/30" />
        <motion.div
          className="absolute top-1/2 h-3.5 w-3.5 -translate-y-1/2 rounded-full border-2 border-bg"
          style={{ background: color, left: `calc(50% + ${pctFromCenter}%)` }}
          initial={{ left: "50%" }}
          animate={{ left: `calc(50% + ${pctFromCenter}%)` }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        />
      </div>
      <div className="mt-1 flex justify-between text-[10px] text-faint">
        <span>Bearish</span>
        <span>Neutral</span>
        <span>Bullish</span>
      </div>
    </div>
  );
}
