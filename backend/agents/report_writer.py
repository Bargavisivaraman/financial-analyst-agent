"""Report Writer Agent — synthesizes all agent outputs into an investment memo."""
from __future__ import annotations

from typing import Any, Callable, Dict

from .. import llm

NAME = "report_writer"

SYSTEM = (
    "You are an investment Report Writer agent. Synthesize the analyst notes into a crisp Markdown "
    "investment memo with: a one-line **Recommendation** (BUY / HOLD / SELL), a 'Why' section, a "
    "'Risks' section, and a 'Bottom line'. If a risk veto is present, the recommendation MUST be "
    "SELL or AVOID and you must say so explicitly. Keep it under ~200 words. End with the "
    "disclaimer: '_Educational research only — not financial advice._'"
)


def run(state: Dict[str, Any], emit: Callable[[str, str], None]) -> Dict[str, Any]:
    risk = state.get("risk", {})
    emit(NAME, "Synthesizing final investment memo…")
    user = (
        f"Ticker: {state['ticker']}\n\n"
        f"FUNDAMENTALS:\n{state.get('fundamental','')}\n\n"
        f"NEWS/SENTIMENT:\n{state.get('news',{}).get('summary','')}\n\n"
        f"RISK: score={risk.get('risk_score')} band={risk.get('risk_band')} "
        f"veto={risk.get('veto')} flags={risk.get('flags')}"
    )
    memo = llm.complete(SYSTEM, user, max_tokens=600)
    emit(NAME, "Memo ready.")
    return {"memo": memo}
