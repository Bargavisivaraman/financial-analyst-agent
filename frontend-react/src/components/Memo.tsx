import { motion } from "framer-motion";
import { mdToHtml } from "../format";

function callFromMemo(memo: string): { call: string; color: string } {
  const m = memo.toUpperCase();
  if (m.includes("SELL") || m.includes("AVOID")) return { call: "SELL", color: "#f87171" };
  if (m.includes("BUY")) return { call: "BUY", color: "#34d399" };
  return { call: "HOLD", color: "#fbbf24" };
}

export default function Memo({ memo }: { memo: string }) {
  const { call, color } = callFromMemo(memo);
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-edge bg-panel2 p-5"
    >
      <div className="mb-3 flex items-center justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-[1.5px] text-muted">
          Investment Memo
        </p>
        <span
          className="rounded-md px-3 py-1 text-sm font-extrabold"
          style={{ background: `${color}22`, color, border: `1px solid ${color}` }}
        >
          {call}
        </span>
      </div>
      <div
        className="memo-prose text-[14.5px] leading-relaxed text-slate-200"
        dangerouslySetInnerHTML={{ __html: `<p>${mdToHtml(memo)}</p>` }}
      />
    </motion.div>
  );
}
