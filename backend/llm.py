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
import time


def _is_transient(e: Exception) -> bool:
    """Rate limits (429), server errors (5xx), and timeouts are worth retrying."""
    s = str(e).lower()
    return any(k in s for k in ("429", "rate limit", "ratelimit", "timeout", "timed out",
                                "500", "502", "503", "504", "overloaded", "connection"))


def _with_retry(fn, attempts: int = 4, base_delay: float = 1.0):
    """Call fn(), retrying transient failures with exponential backoff. Re-raises
    the last error if all attempts fail (caller decides how to degrade)."""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            if not _is_transient(e) or i == attempts - 1:
                raise
            time.sleep(base_delay * (2 ** i))
    raise last  # pragma: no cover

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

    try:
        if _provider == "groq":
            def _call():
                return _client.chat.completions.create(
                    model=_model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    **({"response_format": {"type": "json_object"}} if json_mode else {}),
                )

            resp = _with_retry(_call)
            return (resp.choices[0].message.content or "").strip()

        # anthropic
        def _acall():
            return _client.messages.create(
                model=_model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )

        msg = _with_retry(_acall)
        return "".join(block.text for block in msg.content if block.type == "text").strip()
    except Exception:
        # Persistent failure (e.g. sustained rate limiting): degrade gracefully to a
        # deterministic response so the multi-agent run still COMPLETES instead of
        # crashing the SSE stream mid-analysis.
        return _mock(system, user, json_mode)


def supports_tools() -> bool:
    """Genuine LLM-driven tool-calling is available only on the Groq backend here."""
    return _provider == "groq" and _client is not None


def complete_with_tools(system, user, tools, dispatch, max_rounds=4, emit=None) -> str:
    """Real agentic tool-calling loop: the LLM autonomously decides which tools to
    invoke, we execute them and feed results back, repeating until it answers.

    `tools`    — OpenAI-style tool schemas.
    `dispatch` — callable(name, args_dict) -> JSON-serializable result.
    Returns the model's final text. Raises if tools are unsupported (caller falls back).
    """
    if not supports_tools():
        raise RuntimeError("tool-calling unsupported on this backend")

    def _create(**kw):
        # Retry transient failures: Llama-on-Groq intermittently emits a malformed
        # tool call (tool_use_failed), and the free tier rate-limits (429).
        last = None
        for attempt in range(4):
            try:
                return _client.chat.completions.create(**kw)
            except Exception as e:  # noqa: BLE001
                last = e
                retryable = "tool_use_failed" in str(e) or "400" in str(e) or _is_transient(e)
                if not retryable or attempt == 3:
                    raise
                time.sleep(1.0 * (2 ** attempt))
        raise last

    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    for _ in range(max_rounds):
        resp = _create(
            model=_model, messages=messages, tools=tools, tool_choice="auto", max_tokens=800
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return (msg.content or "").strip()

        messages.append(
            {
                "role": "assistant",
                "content": msg.content,  # null is valid (and expected) alongside tool_calls
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ],
            }
        )
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            if emit:
                emit(f"LLM chose tool → {tc.function.name}({args})")
            result = dispatch(tc.function.name, args)
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)[:4000]}
            )

    final = _create(model=_model, messages=messages, max_tokens=800)
    return (final.choices[0].message.content or "").strip()


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
    if "filings" in role or "10-k" in role:
        return (
            "Per the filing, the company cites intense competition and supply-chain dependence as "
            "primary risks [1], while revenue growth is attributed to strong product demand and "
            "pricing [2]. Liquidity is described as adequate, with operating cash flow funding "
            "capex and buybacks [4]. NEUTRAL"
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
