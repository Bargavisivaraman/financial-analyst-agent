"""Market & fundamentals data tools. Uses yfinance when available/online,
and degrades to deterministic synthetic data so the demo always produces output."""
from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List


def _seed(ticker: str) -> float:
    h = int(hashlib.sha256(ticker.upper().encode()).hexdigest(), 16)
    return (h % 1000) / 10.0  # stable pseudo-value per ticker


def _synthetic_series(ticker: str, base: float, points: int = 30) -> List[Dict[str, Any]]:
    """Deterministic but realistic-looking price walk for charting."""
    series, price = [], base * 0.9
    for i in range(points):
        wiggle = math.sin((i + _seed(ticker)) / 3.0) * base * 0.02
        drift = (i / points) * base * 0.1
        price = round(base * 0.9 + drift + wiggle, 2)
        series.append({"t": i, "close": price})
    return series


def _synthetic(ticker: str) -> Dict[str, Any]:
    base = 50 + _seed(ticker)
    return {
        "source": "synthetic",
        "ticker": ticker.upper(),
        "price": round(base, 2),
        "change_pct_1m": round((_seed(ticker) % 20) - 10, 2),
        "pe_ratio": round(15 + (_seed(ticker) % 25), 1),
        "market_cap": int(base * 1e9),
        "beta": round(0.7 + (_seed(ticker) % 80) / 100, 2),
        "volatility_30d": round(0.15 + (_seed(ticker) % 30) / 100, 3),
        "revenue_growth_yoy": round((_seed(ticker) % 30) - 5, 2),
        "profit_margin": round((_seed(ticker) % 25) / 100, 3),
        "price_history": _synthetic_series(ticker, base),
    }


def get_market_data(ticker: str) -> Dict[str, Any]:
    try:
        import yfinance as yf

        t = yf.Ticker(ticker)
        info = t.info
        if not info or info.get("regularMarketPrice") is None:
            raise ValueError("empty info")
        hist = t.history(period="1mo")
        change = 0.0
        history: List[Dict[str, Any]] = []
        if len(hist) > 1:
            change = round(
                (hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100, 2
            )
            closes = hist["Close"].tolist()
            history = [{"t": i, "close": round(c, 2)} for i, c in enumerate(closes)]
        return {
            "source": "yfinance",
            "ticker": ticker.upper(),
            "price": info.get("regularMarketPrice"),
            "change_pct_1m": change,
            "pe_ratio": info.get("trailingPE"),
            "market_cap": info.get("marketCap"),
            "beta": info.get("beta"),
            "volatility_30d": round(hist["Close"].pct_change().std(), 4) if len(hist) > 1 else None,
            "revenue_growth_yoy": info.get("revenueGrowth"),
            "profit_margin": info.get("profitMargins"),
            "price_history": history or _synthetic(ticker)["price_history"],
        }
    except Exception:
        return _synthetic(ticker)


def get_news(ticker: str, limit: int = 5) -> Dict[str, Any]:
    """Lightweight news fetch via yfinance; synthetic fallback otherwise."""
    try:
        import yfinance as yf

        items = yf.Ticker(ticker).news or []
        headlines = [n.get("title") for n in items[:limit] if n.get("title")]
        if headlines:
            return {"source": "yfinance", "ticker": ticker.upper(), "headlines": headlines}
        raise ValueError("no news")
    except Exception:
        return {
            "source": "synthetic",
            "ticker": ticker.upper(),
            "headlines": [
                f"{ticker.upper()} unveils next-gen product line ahead of earnings",
                f"Analysts raise {ticker.upper()} price target on margin expansion",
                f"{ticker.upper()} faces modest supply-chain headwinds in latest quarter",
            ],
        }
