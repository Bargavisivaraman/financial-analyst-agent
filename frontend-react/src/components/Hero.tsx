import Analyzer from "./Analyzer";

export default function Hero() {
  return (
    <header id="top" className="hero-glow relative overflow-hidden pb-12 pt-16">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-emerald-900 bg-emerald-950/30 px-3 py-1.5 text-[12.5px] text-accent">
          <span className="h-1.5 w-1.5 rounded-full bg-accent shadow-[0_0_8px_#5eead4]" />
          6 AI agents · real SEC filings · live reasoning
        </div>
        <h1 className="mb-4 max-w-3xl text-4xl font-extrabold leading-[1.08] tracking-tight sm:text-5xl">
          Autonomous equity research, run by a{" "}
          <span className="gradient-text">team of AI agents</span>.
        </h1>
        <p className="mb-8 max-w-xl text-lg text-muted">
          Enter a ticker. A supervisor dispatches six specialized agents — they pull live market
          data, read the company's real 10-K, score risk, and write you an investment memo. Watch
          every step stream in real time.
        </p>
        <Analyzer />
      </div>
    </header>
  );
}
