"""Hierarchical multi-agent orchestrator (a hand-rolled, LangGraph-style state graph).

A Supervisor routes work through specialized agent nodes over a shared typed state.
It includes a *reflection loop*: if the Fundamental agent's confidence is low, the
supervisor re-dispatches it once before proceeding. Implementing the graph by hand
(rather than importing langgraph) keeps the dependency surface tiny and makes the
control flow fully inspectable — every transition is a streamed trace event.
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, Iterator

from . import llm
from .agents import fundamental, market_data, news_sentiment, report_writer, risk_manager

Emit = Callable[[str, str], None]

SUPERVISOR = "supervisor"


def _low_confidence(text: str) -> bool:
    return len(text.strip()) < 40 or "insufficient" in text.lower()


def run_analysis(ticker: str) -> Iterator[Dict[str, Any]]:
    """Generator that yields trace events as (dict) and finally the result.

    Each yielded event: {"type": "trace"|"result"|"done", "agent":..., "message":...}
    """
    events: list[Dict[str, Any]] = []

    def emit(agent: str, message: str) -> None:
        events.append({"type": "trace", "agent": agent, "message": message, "ts": time.time()})

    state: Dict[str, Any] = {"ticker": ticker.upper()}

    mode = "LIVE (Claude)" if llm.live_mode() else "MOCK (no API key)"
    emit(SUPERVISOR, f"Received request for {state['ticker']}. LLM mode: {mode}.")
    emit(SUPERVISOR, "Planning: market → fundamental → news → risk → report.")
    yield from _flush(events)

    # Node 1: Market data (parallel-capable, sequential here for clear tracing)
    emit(SUPERVISOR, "Dispatching → Market Data Agent")
    yield from _flush(events)
    state.update(market_data.run(state, emit))
    yield from _flush(events)

    # Node 2: Fundamental, with one reflection retry
    emit(SUPERVISOR, "Dispatching → Fundamental Analyst Agent")
    yield from _flush(events)
    state.update(fundamental.run(state, emit))
    if _low_confidence(state.get("fundamental", "")):
        emit(SUPERVISOR, "Fundamental output low-confidence → re-dispatching (reflection loop).")
        yield from _flush(events)
        state.update(fundamental.run(state, emit))
    yield from _flush(events)

    # Node 3: News & sentiment
    emit(SUPERVISOR, "Dispatching → News & Sentiment Agent")
    yield from _flush(events)
    state.update(news_sentiment.run(state, emit))
    yield from _flush(events)

    # Node 4: Risk manager (can veto)
    emit(SUPERVISOR, "Dispatching → Risk Manager Agent")
    yield from _flush(events)
    state.update(risk_manager.run(state, emit))
    yield from _flush(events)

    if state.get("risk", {}).get("veto"):
        emit(SUPERVISOR, "Risk Manager issued a VETO — forcing defensive memo.")
    yield from _flush(events)

    # Node 5: Report writer
    emit(SUPERVISOR, "Dispatching → Report Writer Agent")
    yield from _flush(events)
    state.update(report_writer.run(state, emit))
    yield from _flush(events)

    emit(SUPERVISOR, "All agents reported. Analysis complete.")
    yield from _flush(events)

    yield {
        "type": "result",
        "ticker": state["ticker"],
        "market": state.get("market"),
        "fundamental": state.get("fundamental"),
        "news": state.get("news"),
        "risk": state.get("risk"),
        "memo": state.get("memo"),
    }
    yield {"type": "done"}


def _flush(events: list[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    while events:
        yield events.pop(0)
