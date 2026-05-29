import { motion } from "framer-motion";
import type { ResultEvent } from "../api";
import Filings from "./Filings";
import Memo from "./Memo";
import PriceChart from "./PriceChart";
import RiskGauge from "./RiskGauge";
import SentimentMeter from "./SentimentMeter";

export default function ResultsPanel({ result }: { result: ResultEvent }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mt-5 grid gap-4 md:grid-cols-2"
    >
      <div className="md:col-span-2">
        <PriceChart market={result.market} />
      </div>
      <RiskGauge risk={result.risk} />
      <SentimentMeter score={result.news?.score ?? 0} />
      <div className="md:col-span-2">
        <Filings filings={result.filings} />
      </div>
      <div className="md:col-span-2">
        <Memo memo={result.memo} />
      </div>
    </motion.div>
  );
}
