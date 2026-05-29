"""SEC EDGAR tools: resolve a ticker to its latest 10-K and return the filing text.

Uses only the stdlib (urllib) + EDGAR's free JSON/HTML endpoints — no API key.
Filings are cached on disk. If EDGAR is unreachable, falls back to a small bundled
excerpt so the RAG path always produces output.
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from typing import Optional

_UA = {"User-Agent": "financial-analyst-agent contact@example.com"}
_CACHE = Path(__file__).resolve().parent.parent.parent / ".cache" / "filings"
_CACHE.mkdir(parents=True, exist_ok=True)

_FALLBACK = (
    "Item 1A. Risk Factors. Our business is subject to numerous risks including intense "
    "competition, rapid technological change, dependence on key suppliers, and demand volatility. "
    "Item 7. Management's Discussion and Analysis. Revenue grew year over year driven by strong "
    "product demand and pricing, while operating margins were pressured by elevated input costs. "
    "We expect continued investment in research and development. Liquidity remains adequate with "
    "cash flows from operations funding capital expenditures and shareholder returns. Foreign "
    "currency fluctuations and supply-chain constraints could materially affect future results."
)


def _get(url: str, timeout: int = 12) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=timeout).read()


# The ticker->CIK map (~1MB) is identical for every request, so fetch it once per
# process and keep it in memory instead of re-downloading it on every analysis.
_CIK_MAP: dict | None = None


def _cik_for(ticker: str) -> Optional[str]:
    global _CIK_MAP
    if _CIK_MAP is None:
        data = json.loads(_get("https://www.sec.gov/files/company_tickers.json"))
        _CIK_MAP = {row["ticker"].upper(): str(row["cik_str"]).zfill(10) for row in data.values()}
    return _CIK_MAP.get(ticker.upper())


def _latest_10k_url(cik: str) -> Optional[str]:
    sub = json.loads(_get(f"https://data.sec.gov/submissions/CIK{cik}.json"))
    recent = sub["filings"]["recent"]
    for form, acc, doc in zip(recent["form"], recent["accessionNumber"], recent["primaryDocument"]):
        if form == "10-K":
            acc_nodash = acc.replace("-", "")
            return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{doc}"
    return None


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = (
        text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#160;", " ")
        .replace("&#39;", "'").replace("&rsquo;", "'").replace("&ldquo;", '"').replace("&rdquo;", '"')
    )
    return re.sub(r"\s+", " ", text).strip()


def get_10k_text(ticker: str, max_chars: int = 120_000) -> dict:
    """Return {'source','ticker','url','text'} for the latest 10-K (cached)."""
    cache = _CACHE / f"{ticker.upper()}_10k.json"
    if cache.exists():
        return json.loads(cache.read_text())

    try:
        cik = _cik_for(ticker)
        if not cik:
            raise ValueError("ticker not found in EDGAR")
        url = _latest_10k_url(cik)
        if not url:
            raise ValueError("no 10-K found")
        text = _strip_html(_get(url).decode("utf-8", errors="ignore"))[:max_chars]
        if len(text) < 500:
            raise ValueError("filing text too short")
        result = {"source": "sec_edgar", "ticker": ticker.upper(), "url": url, "text": text}
    except Exception as e:
        result = {
            "source": f"fallback ({type(e).__name__})",
            "ticker": ticker.upper(),
            "url": None,
            "text": _FALLBACK,
        }

    cache.write_text(json.dumps(result))
    return result
