"""LLM layer with pluggable backends.

Backend priority (first one with a key wins):
  1. Groq        — free, fast, OpenAI-compatible   (GROQ_API_KEY)
  2. Anthropic   — Claude                            (ANTHROPIC_API_KEY)
  3. Mock        — deterministic, no key needed       (always available)

The rest of the app is provider-agnostic; it only calls `complete()`.
"""
from __future__ import annotations

import json
import os

# ---- backend selection -----------------------------------------------------
_provider = "mock"
_model = "deterministic-mock"
_client = None

_GROQ_KEY = os.getenv("GROQ_API_KEY")
_ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

if _GROQ_KEY:
    try:
        from openai import OpenAI  # OpenAI SDK speaks to Groq's compatible endpoint

        _client = OpenAI(api_key=_GROQ_KEY, base_url="https://api.groq.com/openai/v1")
        _model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        _provider = "groq"
    except Exception:
        _client = None

elif _ANTHROPIC_KEY:
    try:
        from anthropic import Anthropic

        _client = Anthropic()
        _model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        _provider = "anthropic"
    except Exception:
        _client = None

# public, read by server /api/health
MODEL = _model
PROVIDER = _provider


def live_mode() -> bool:
    return _client is not None


def complete(system: str, user: str, max_tokens: int = 1024, json_mode: bool = False) -> str:
    """Single-shot completion. Returns plain text (or a JSON string if json_mode)."""
    if _client is None:
        return _mock(system, user, json_mode)

    if _provider == "groq":
        resp = _client.chat.completions.create(
            model=_model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **({"response_format": {"type": "json_object"}} if json_mode else {}),
        )
        return (resp.choices[0].message.content or "").strip()

    # anthropic
    msg = _client.messages.create(
        model=_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in msg.content if block.type == "text").strip()


def _mock(system: str, user: str, json_mode: bool) -> str:
    """Deterministic, plausible output keyed off the agent's role in the system
    prompt. Lets the multi-agent flow run with zero credentials."""
    role = system.lower()
    if json_mode or "risk manager" in role:
        return json.dumps(
            {
                "risk_score": 42,
                "risk_band": "Moderate",
                "veto": False,
                "flags": ["Elevated valuation vs. sector median", "Earnings call in <14 days"],
                "rationale": "Volatility and beta are within normal range; no hard veto triggered.",
            }
        )
    if "fundamental" in role:
        return (
            "Fundamentals look solid: revenue growth is positive YoY, margins are stable, "
            "and the balance sheet carries manageable leverage. P/E sits modestly above the "
            "sector median, suggesting the market prices in continued growth. Free cash flow "
            "comfortably covers capex and buybacks."
        )
    if "news" in role or "sentiment" in role:
        return (
            "Recent coverage skews mildly positive. Headlines emphasize product momentum and "
            "an upcoming earnings catalyst. No material legal/regulatory red flags surfaced. "
            "Net sentiment: +0.35 (mildly bullish)."
        )
    if "report" in role or "writer" in role:
        return (
            "## Investment Memo\n\n**Recommendation: HOLD (lean Buy)**\n\n"
            "The company shows healthy fundamentals and constructive news flow, balanced by a "
            "premium valuation. Suitable as a core holding; add on pullbacks below fair value.\n"
        )
    return (
        "Plan: gather market data, analyze fundamentals, assess news sentiment, run a risk "
        "check, then synthesize a memo. All sub-agents report sufficient confidence."
    )
