"""SEC Filings Agent — RAG over the latest 10-K.

Fetches the real 10-K from EDGAR, chunks it, retrieves the most relevant passages
for a set of analyst queries via TF-IDF, and asks the LLM to produce a grounded
assessment. The retrieved passages are returned so the memo can cite primary source.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

from .. import llm
from ..rag import TfidfRetriever, chunk_text
from ..tools import get_10k_text

NAME = "filings"

QUERIES = [
    "key risk factors and uncertainties",
    "revenue growth drivers and segments",
    "competition and competitive pressures",
    "liquidity, cash flow and capital expenditures",
]

SYSTEM = (
    "You are an SEC Filings analyst agent. You are given verbatim passages retrieved from a "
    "company's latest 10-K. Using ONLY these passages, write a 3-5 sentence grounded assessment "
    "covering material risks and business drivers. Do not invent facts not in the passages. "
    "Refer to passages as [1], [2], etc. End with a one-word lean: BULLISH/NEUTRAL/BEARISH."
)


def run(state: Dict[str, Any], emit: Callable[[str, str], None]) -> Dict[str, Any]:
    ticker = state["ticker"]
    emit(NAME, f"Fetching latest 10-K for {ticker} from SEC EDGAR…")
    filing = get_10k_text(ticker)
    emit(NAME, f"Source: {filing['source']}. Chunking & building TF-IDF index…")

    chunks = chunk_text(filing["text"])
    retriever = TfidfRetriever(chunks)

    seen, passages = set(), []
    for q in QUERIES:
        for idx, score, text in retriever.query(q, k=2):
            if idx not in seen and score > 0:
                seen.add(idx)
                passages.append(text)
    passages = passages[:6]
    emit(NAME, f"Retrieved {len(passages)} relevant passages from {len(chunks)} chunks.")

    numbered = "\n\n".join(f"[{i+1}] {p}" for i, p in enumerate(passages))
    analysis = llm.complete(SYSTEM, f"Ticker: {ticker}\n\nPassages:\n{numbered}", max_tokens=500)
    emit(NAME, "10-K grounded assessment complete.")

    return {
        "filings": {
            "source": filing["source"],
            "url": filing["url"],
            "passages": passages,
            "analysis": analysis,
        }
    }
