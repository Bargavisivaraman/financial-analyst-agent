import { Zap } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-edge py-9 text-[13px] text-faint">
      <div className="mx-auto flex max-w-6xl flex-wrap justify-between gap-4 px-6">
        <div className="max-w-md">
          <div className="mb-2 flex items-center gap-2 font-extrabold text-slate-200">
            <Zap className="h-4 w-4 text-accent" /> Financial <span className="gradient-text">Analyst</span>
          </div>
          <p className="m-0">
            Educational research tool — <b>not financial advice</b>. Built by Bargavi Sivaraman.
          </p>
        </div>
        <div className="flex gap-5">
          <a
            href="https://github.com/Bargavisivaraman/financial-analyst-agent"
            target="_blank"
            rel="noreferrer"
            className="text-muted hover:text-white"
          >
            GitHub ↗
          </a>
          <a href="#top" className="text-muted hover:text-white">
            Back to top ↑
          </a>
        </div>
      </div>
    </footer>
  );
}
