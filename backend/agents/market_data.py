"""Market Data Agent — acquires price/valuation + headlines.

When the backend supports it (Groq), this agent uses *real LLM tool-calling*: the
model is given tool schemas and autonomously decides to invoke get_market_data and
get_news, we execute them and feed results back. On other backends it falls back to
calling the tools directly. Either way the structured data lands in shared state.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

from .. import llm
from ..tools import get_market_data, get_news

NAME = "market_data"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_market_data",
            "description": "Get current price, P/E, market cap, beta, volatility and growth for a ticker.",
            "parameters": {
                "type": "object",
                "properties": {"ticker": {"type": "string", "description": "Stock ticker symbol"}},
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get recent news headlines for a ticker.",
            "parameters": {
                "type": "object",
                "properties": {"ticker": {"type": "string"}},
                "required": ["ticker"],
            },
        },
    },
]

SYSTEM = (
    "You are a data-acquisition agent. Use the available tools to gather current market data and "
    "recent headlines for the requested ticker, then reply with one short sentence confirming what "
    "you retrieved. Always call get_market_data before answering."
)


def run(state: Dict[str, Any], emit: Callable[[str, str], None]) -> Dict[str, Any]:
    ticker = state["ticker"]
    captured: Dict[str, Any] = {}

    def dispatch(name: str, args: Dict[str, Any]) -> Any:
        tk = args.get("ticker", ticker)
        if name == "get_market_data":
            captured["market"] = get_market_data(tk)
            return captured["market"]
        if name == "get_news":
            captured["news_raw"] = get_news(tk)
            return captured["news_raw"]
        return {"error": f"unknown tool {name}"}

    if llm.supports_tools():
        emit(NAME, "Reasoning about which tools to call (LLM tool-calling)…")
        try:
            llm.complete_with_tools(
                SYSTEM, f"Gather data for {ticker}.", TOOLS, dispatch,
                emit=lambda m: emit(NAME, m),
            )
        except Exception as e:
            emit(NAME, f"Tool-calling failed ({type(e).__name__}); using direct fetch.")
        if "market" not in captured:  # ensure we always have market data
            captured["market"] = get_market_data(ticker)
    else:
        emit(NAME, f"Calling get_market_data({ticker})…")
        captured["market"] = get_market_data(ticker)

    m = captured["market"]
    emit(NAME, f"Got {m['source']} data: price={m.get('price')}, P/E={m.get('pe_ratio')}")
    out: Dict[str, Any] = {"market": m}
    if "news_raw" in captured:
        out["news_prefetched"] = captured["news_raw"]
    return out
