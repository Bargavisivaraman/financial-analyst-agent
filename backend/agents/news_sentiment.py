"""News & Sentiment Agent — pulls headlines and scores sentiment with the LLM."""
from __future__ import annotations

from typing import Any, Callable, Dict

from .. import llm
from ..tools import get_news

NAME = "news_sentiment"

SYSTEM = (
    "You are a News & Sentiment analyst agent. Given recent headlines for a stock, summarize the "
    "narrative in 2-4 sentences and assign a net sentiment score from -1.0 (very bearish) to +1.0 "
    "(very bullish). Flag any material legal, regulatory, or accounting risks. End with: "
    "'Net sentiment: <score>'."
)


def run(state: Dict[str, Any], emit: Callable[[str, str], None]) -> Dict[str, Any]:
    ticker = state["ticker"]
    if state.get("news_prefetched"):
        emit(NAME, "Reusing headlines already fetched via tool-calling…")
        news = state["news_prefetched"]
    else:
        emit(NAME, f"Fetching recent headlines for {ticker}…")
        news = get_news(ticker)
    emit(NAME, f"Scoring sentiment over {len(news['headlines'])} headlines…")
    user = "Headlines:\n" + "\n".join(f"- {h}" for h in news["headlines"])
    summary = llm.complete(SYSTEM, user, max_tokens=400)
    return {"news": {"headlines": news["headlines"], "summary": summary}}
