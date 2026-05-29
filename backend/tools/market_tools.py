"""Market & fundamentals data tools. Uses yfinance when available/online,
and degrades to deterministic synthetic data so the demo always produces output."""
from __future__ import annotations

import hashlib
import math
import os
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


# yfinance is blocked/rate-limited from many datacenter IPs (e.g. Render). After it
# fails once in a given process we stop trying so we don't pay a timeout every request.
_YF_DISABLED = False


def _try_yfinance(ticker: str) -> Dict[str, Any] | None:
    global _YF_DISABLED
    if _YF_DISABLED:
        return None
    try:
        import yfinance as yf

        t = yf.Ticker(ticker)
        info = t.info
        if not info or info.get("regularMarketPrice") is None:
            raise ValueError("empty info")
        hist = t.history(period="1mo")
        change, history = 0.0, []
        if len(hist) > 1:
            change = round((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100, 2)
            history = [{"t": i, "close": round(c, 2)} for i, c in enumerate(hist["Close"].tolist())]
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
        _YF_DISABLED = True
        return None


def _stats_from_closes(closes: List[float]) -> tuple[float, float]:
    change = round((closes[-1] - closes[0]) / closes[0] * 100, 2)
    rets = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
    mean = sum(rets) / len(rets) if rets else 0.0
    vol = round((sum((r - mean) ** 2 for r in rets) / len(rets)) ** 0.5, 4) if rets else None
    return change, vol


def _try_yahoo_chart(ticker: str) -> Dict[str, Any] | None:
    """Real price + 1M history from Yahoo's public v8 chart endpoint (no key). This is a
    different endpoint than the one yfinance uses, so it often works from cloud IPs where
    yfinance is blocked. Fundamentals (P/E, beta) aren't here, so they stay null."""
    import json
    import urllib.request

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1mo&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=8).read())
        res = d["chart"]["result"][0]
        meta = res["meta"]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
        if len(closes) < 5:
            return None
        change, vol = _stats_from_closes(closes)
        return {
            "source": "yahoo",
            "ticker": ticker.upper(),
            "price": round(meta.get("regularMarketPrice", closes[-1]), 2),
            "change_pct_1m": change,
            "pe_ratio": None,
            "market_cap": None,
            "beta": None,
            "volatility_30d": vol,
            "revenue_growth_yoy": None,
            "profit_margin": None,
            "price_history": [{"t": i, "close": round(c, 2)} for i, c in enumerate(closes)],
        }
    except Exception:
        return None


def _fmp_get(url: str):
    import json
    import urllib.request

    return json.loads(urllib.request.urlopen(url, timeout=8).read())


def _try_fmp(ticker: str) -> Dict[str, Any] | None:
    """Full real data (price + fundamentals) from Financial Modeling Prep. Requires a
    free FMP_API_KEY (https://site.financialmodelingprep.com). Works from cloud IPs.

    Tries FMP's current `/stable/` endpoints first, then the legacy `/api/v3/` ones,
    so it works regardless of which API surface the key is provisioned for."""
    key = os.getenv("FMP_API_KEY")
    if not key:
        return None

    # ---- quote (price + P/E + market cap) ----
    info = None
    for url in (
        f"https://financialmodelingprep.com/stable/quote?symbol={ticker}&apikey={key}",
        f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={key}",
    ):
        try:
            data = _fmp_get(url)
            if isinstance(data, list) and data and data[0].get("price") is not None:
                info = data[0]
                break
        except Exception:
            continue
    if info is None:
        return None

    # ---- 1-month price history (best-effort; chart still works without it) ----
    closes: list[float] = []
    for url in (
        f"https://financialmodelingprep.com/stable/historical-price-eod/light?symbol={ticker}&apikey={key}",
        f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&timeseries=30&apikey={key}",
    ):
        try:
            raw = _fmp_get(url)
            rows = raw.get("historical", raw) if isinstance(raw, dict) else raw
            vals = []
            for p in rows:
                c = p.get("close", p.get("price"))
                if c is not None:
                    vals.append(float(c))
            if len(vals) >= 5:
                closes = list(reversed(vals[:30]))  # FMP returns newest-first
                break
        except Exception:
            continue

    if len(closes) >= 5:
        change, vol = _stats_from_closes(closes)
        history = [{"t": i, "close": round(c, 2)} for i, c in enumerate(closes)]
    else:
        change, vol = info.get("changesPercentage"), None
        history = _synthetic(ticker)["price_history"]

    # ---- fundamentals (P/E, profit margin) from the ratios endpoint (best-effort) ----
    pe, margin = info.get("pe"), None
    try:
        r = _fmp_get(f"https://financialmodelingprep.com/stable/ratios-ttm?symbol={ticker}&apikey={key}")
        row = r[0] if isinstance(r, list) and r else r
        if isinstance(row, dict):
            pe = row.get("priceToEarningsRatioTTM", pe)
            margin = row.get("netProfitMarginTTM")
    except Exception:
        pass

    return {
        "source": "fmp",
        "ticker": ticker.upper(),
        "price": info.get("price"),
        "change_pct_1m": change,
        "pe_ratio": round(pe, 2) if isinstance(pe, (int, float)) else pe,
        "market_cap": info.get("marketCap"),
        "beta": None,
        "volatility_30d": vol,
        "revenue_growth_yoy": None,
        "profit_margin": round(margin, 4) if isinstance(margin, (int, float)) else margin,
        "price_history": history,
    }


def get_market_data(ticker: str) -> Dict[str, Any]:
    """Real data with graceful degradation:
    FMP (full, needs free key) -> yfinance (full, local) -> Yahoo chart (real price, no key)
    -> deterministic synthetic (last resort, always works)."""
    return _try_fmp(ticker) or _try_yfinance(ticker) or _try_yahoo_chart(ticker) or _synthetic(ticker)


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
