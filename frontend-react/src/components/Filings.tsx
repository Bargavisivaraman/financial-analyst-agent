import { FileText } from "lucide-react";
import type { FilingsData } from "../api";
import { mdToHtml } from "../format";

export default function Filings({ filings }: { filings: FilingsData }) {
  return (
    <div className="rounded-xl border border-edge bg-panel2 p-5">
      <div className="mb-2 flex items-center gap-2 text-xs text-muted">
        <FileText className="h-4 w-4 text-accent2" />
        Grounded in 10-K · source:{" "}
        {filings.url ? (
          <a href={filings.url} target="_blank" rel="noreferrer" className="text-accent2 underline">
            {filings.source}
          </a>
        ) : (
          filings.source
        )}
      </div>
      <div
        className="memo-prose text-[14px] leading-relaxed text-slate-200"
        dangerouslySetInnerHTML={{ __html: `<p>${mdToHtml(filings.analysis)}</p>` }}
      />
      <div className="mt-3 space-y-1.5">
        {filings.passages?.map((p, i) => (
          <details key={i} className="rounded-lg border border-edge bg-[#0c111b]">
            <summary className="cursor-pointer px-3 py-2 text-xs text-accent2">
              [{i + 1}] 10-K passage
            </summary>
            <div className="border-t border-edge px-3 py-2 text-[12px] leading-relaxed text-muted">
              {p.slice(0, 600)}…
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}
