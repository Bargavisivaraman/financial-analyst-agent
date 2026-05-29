"""Tiny, dependency-free TF-IDF retriever for RAG over filing text.

Implemented from scratch (no scikit-learn / no embedding API) so it runs anywhere
with zero credentials and installs nothing extra. Sparse TF-IDF + cosine similarity
is a legitimate retrieval method and is plenty for grounding an LLM in a 10-K.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import List, Tuple

_WORD = re.compile(r"[a-z0-9]+")
_STOP = set(
    "the a an and or of to in for on with is are was were be been being this that these those "
    "as at by from it its their our we us you your they them he she his her which who whom whose "
    "will would shall should may might can could not no nor so than then there here".split()
)


def _tokens(text: str) -> List[str]:
    return [t for t in _WORD.findall(text.lower()) if t not in _STOP and len(t) > 1]


def chunk_text(text: str, size: int = 1200, overlap: int = 200) -> List[str]:
    """Split into overlapping character windows on whitespace boundaries."""
    text = re.sub(r"\s+", " ", text).strip()
    chunks, i = [], 0
    while i < len(text):
        end = min(i + size, len(text))
        # extend to the next space so we don't cut mid-word
        if end < len(text):
            nxt = text.find(" ", end)
            end = nxt if nxt != -1 else end
        chunks.append(text[i:end].strip())
        if end >= len(text):
            break
        i = end - overlap
    return [c for c in chunks if len(c) > 80]


class TfidfRetriever:
    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self.docs = [Counter(_tokens(c)) for c in chunks]
        df: Counter = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = max(1, len(self.docs))
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}
        self.vecs = [self._vec(d) for d in self.docs]
        self.norms = [math.sqrt(sum(v * v for v in vec.values())) or 1.0 for vec in self.vecs]

    def _vec(self, counter: Counter) -> dict:
        total = sum(counter.values()) or 1
        return {t: (c / total) * self.idf.get(t, 0.0) for t, c in counter.items()}

    def query(self, q: str, k: int = 4) -> List[Tuple[int, float, str]]:
        qc = Counter(_tokens(q))
        qv = self._vec(qc)
        qn = math.sqrt(sum(v * v for v in qv.values())) or 1.0
        scored = []
        for i, (vec, norm) in enumerate(zip(self.vecs, self.norms)):
            dot = sum(qv.get(t, 0.0) * w for t, w in vec.items())
            scored.append((i, dot / (qn * norm), self.chunks[i]))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
