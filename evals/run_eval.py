"""Eval harness: runs the multi-agent pipeline over a basket of tickers and reports
coverage + latency + veto rate. Run from project root:  python -m evals.run_eval
This is the 'production mindset' signal — measuring agent behavior, not just shipping it."""
from __future__ import annotations

import time

from backend import graph

TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "JPM", "XOM", "PFE", "AMZN", "GOOGL", "META"]


def consume(ticker: str) -> dict:
    result = {}
    for ev in graph.run_analysis(ticker):
        if ev["type"] == "result":
            result = ev
    return result


def main() -> None:
    print(f"Running eval over {len(TICKERS)} tickers…\n")
    rows, vetoes, total_t = [], 0, 0.0
    for tk in TICKERS:
        t0 = time.time()
        r = consume(tk)
        dt = time.time() - t0
        total_t += dt
        risk = r.get("risk", {})
        ok = all(r.get(k) for k in ("market", "fundamental", "news", "risk", "memo"))
        vetoes += 1 if risk.get("veto") else 0
        rows.append((tk, "PASS" if ok else "FAIL", risk.get("risk_score"), risk.get("risk_band"), round(dt, 2)))

    print(f"{'TICKER':<8}{'STATUS':<8}{'RISK':<6}{'BAND':<10}{'SECS':<6}")
    print("-" * 40)
    for tk, st, rs, band, dt in rows:
        print(f"{tk:<8}{st:<8}{str(rs):<6}{str(band):<10}{dt:<6}")
    passed = sum(1 for r in rows if r[1] == "PASS")
    print("-" * 40)
    print(f"Coverage: {passed}/{len(TICKERS)} complete | Veto rate: {vetoes}/{len(TICKERS)} | "
          f"Avg latency: {total_t/len(TICKERS):.2f}s")


if __name__ == "__main__":
    main()
