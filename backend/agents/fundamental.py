"""Fundamental Analyst Agent — reasons over valuation/financial metrics."""
from __future__ import annotations

from typing import Any, Callable, Dict

from .. import llm

NAME = "fundamental"

SYSTEM = (
    "You are a Fundamental Analyst agent. Given a company's market and financial metrics, "
    "write a concise (3-5 sentence) assessment of valuation, growth, margins, and balance-sheet "
    "health. Be specific and reference the numbers. End with a one-word lean: BULLISH/NEUTRAL/BEARISH."
)


def run(state: Dict[str, Any], emit: Callable[[str, str], None]) -> Dict[str, Any]:
    m = state.get("market", {})
    emit(NAME, "Analyzing valuation, growth and margins…")
    user = (
        f"Ticker: {state['ticker']}\n"
        f"Price: {m.get('price')}  P/E: {m.get('pe_ratio')}  MktCap: {m.get('market_cap')}\n"
        f"RevGrowthYoY: {m.get('revenue_growth_yoy')}  ProfitMargin: {m.get('profit_margin')}\n"
        f"1M change %: {m.get('change_pct_1m')}"
    )
    analysis = llm.complete(SYSTEM, user, max_tokens=400)
    emit(NAME, "Fundamental assessment complete.")
    return {"fundamental": analysis}
