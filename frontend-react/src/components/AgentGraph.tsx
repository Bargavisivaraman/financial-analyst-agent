import { motion } from "framer-motion";
import type { AgentId } from "../api";

const NODES: { id: AgentId; label: string; x: number; y: number }[] = [
  { id: "supervisor", label: "Supervisor", x: 50, y: 8 },
  { id: "market_data", label: "Market", x: 10, y: 50 },
  { id: "fundamental", label: "Fundamental", x: 30, y: 50 },
  { id: "filings", label: "Filings·RAG", x: 50, y: 50 },
  { id: "news_sentiment", label: "News", x: 70, y: 50 },
  { id: "risk_manager", label: "Risk·Veto", x: 90, y: 50 },
  { id: "report_writer", label: "Report", x: 50, y: 92 },
];

export default function AgentGraph({
  active,
  done,
}: {
  active: AgentId | null;
  done: Set<AgentId>;
}) {
  const sup = NODES[0];
  const report = NODES[6];
  const middle = NODES.slice(1, 6);

  const stroke = (id: AgentId) =>
    done.has(id) ? "#34d399" : active === id ? "#5eead4" : "#243044";

  return (
    <svg viewBox="0 0 100 100" className="h-full w-full" preserveAspectRatio="xMidYMid meet">
      {/* edges supervisor -> middle */}
      {middle.map((n) => (
        <line
          key={`e-${n.id}`}
          x1={sup.x}
          y1={sup.y + 5}
          x2={n.x}
          y2={n.y - 5}
          stroke={stroke(n.id)}
          strokeWidth={0.5}
          opacity={0.7}
        />
      ))}
      {/* edges middle -> report */}
      {middle.map((n) => (
        <line
          key={`r-${n.id}`}
          x1={n.x}
          y1={n.y + 5}
          x2={report.x}
          y2={report.y - 5}
          stroke={done.has("report_writer") ? "#34d399" : "#243044"}
          strokeWidth={0.4}
          opacity={0.5}
        />
      ))}

      {NODES.map((n) => {
        const isActive = active === n.id;
        const isDone = done.has(n.id);
        const fill = isDone ? "#0e1b17" : isActive ? "#0c1b17" : "#0d1320";
        const ring = isDone ? "#34d399" : isActive ? "#5eead4" : "#1f2937";
        return (
          <g key={n.id}>
            <motion.circle
              cx={n.x}
              cy={n.y}
              r={isActive ? 6.5 : 5.5}
              fill={fill}
              stroke={ring}
              strokeWidth={isActive ? 0.9 : 0.5}
              animate={
                isActive
                  ? { opacity: [1, 0.45, 1] }
                  : { opacity: 1 }
              }
              transition={isActive ? { duration: 1, repeat: Infinity } : {}}
            />
            <text
              x={n.x}
              y={n.y + (n.id === "report_writer" || n.y > 60 ? 0 : 0) + 0.9}
              textAnchor="middle"
              fontSize={2.0}
              fill={isDone || isActive ? "#e8edf5" : "#8b95a7"}
              fontFamily="SF Mono, monospace"
            >
              {n.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
