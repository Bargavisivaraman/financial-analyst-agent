"""Market Data Agent — fetches live price/valuation metrics via tools."""
from __future__ import annotations

from typing import Any, Callable, Dict

from ..tools import get_market_data

NAME = "market_data"


def run(state: Dict[str, Any], emit: Callable[[str, str], None]) -> Dict[str, Any]:
    ticker = state["ticker"]
    emit(NAME, f"Calling get_market_data({ticker})…")
    data = get_market_data(ticker)
    emit(NAME, f"Got {data['source']} data: price={data.get('price')}, P/E={data.get('pe_ratio')}")
    return {"market": data}
