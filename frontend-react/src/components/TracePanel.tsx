import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import type { TraceEvent } from "../api";

export default function TracePanel({ trace }: { trace: TraceEvent[] }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    ref.current?.scrollTo({ top: ref.current.scrollHeight, behavior: "smooth" });
  }, [trace.length]);

  return (
    <div
      ref={ref}
      className="scroll-thin h-[300px] overflow-y-auto rounded-xl border border-edge bg-panel p-4"
    >
      <p className="mb-3 text-[11px] font-semibold uppercase tracking-[1.5px] text-muted">
        Live Agent Trace
      </p>
      {trace.length === 0 ? (
        <p className="text-sm text-muted">
          Enter a ticker and hit Analyze to watch the agents collaborate in real time.
        </p>
      ) : (
        <AnimatePresence initial={false}>
          {trace.map((e, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex gap-3 border-b border-dashed border-[#18202e] py-1.5 text-[12.5px]"
            >
              <span
                className={`min-w-[112px] font-mono ${
                  e.agent === "supervisor" ? "text-accent" : "text-accent2"
                }`}
              >
                {e.agent}
              </span>
              <span className="text-slate-300">{e.message}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      )}
    </div>
  );
}
