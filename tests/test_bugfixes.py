"""Unit tests for bug fixes. No extra deps — run from the repo root:

    python -m unittest discover tests
"""
from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import llm  # noqa: E402
from backend.agents import risk_manager  # noqa: E402
from backend.agents.news_sentiment import _extract_score  # noqa: E402
from backend.rag import chunk_text  # noqa: E402
from backend.tools import market_tools, sec_tools  # noqa: E402


class ExtractScoreTests(unittest.TestCase):
    def test_capitalized_sentiment_label(self):
        # "Net Sentiment" (capital S) must scope the search like "net sentiment"
        text = "Shares slid 0.5 this week on mixed coverage. Net Sentiment: -0.6"
        self.assertEqual(_extract_score(text), -0.6)

    def test_lowercase_sentiment_label(self):
        text = "Positive momentum into earnings. Net sentiment: +0.35"
        self.assertEqual(_extract_score(text), 0.35)

    def test_no_sentiment_word(self):
        self.assertEqual(_extract_score("nothing to see, 0.9 irrelevant"), 0.0)


class RiskManagerTests(unittest.TestCase):
    def _run_with(self, raw: str) -> dict:
        with mock.patch.object(risk_manager.llm, "complete", return_value=raw):
            out = risk_manager.run({"ticker": "AAPL", "market": {}}, lambda a, m: None)
        return out["risk"]

    def test_string_risk_score_does_not_crash(self):
        raw = json.dumps({"risk_score": "42", "risk_band": "Moderate", "veto": False,
                          "flags": [], "rationale": "x"})
        risk = self._run_with(raw)
        self.assertIsInstance(risk["risk_score"], int)

    def test_non_dict_json_does_not_crash(self):
        risk = self._run_with(json.dumps([{"risk_score": 42}]))
        self.assertIsInstance(risk["risk_score"], int)
        self.assertEqual(risk["veto"], False)

    def test_string_flags_coerced_to_list(self):
        raw = json.dumps({"risk_score": 50, "risk_band": "High", "veto": False,
                          "flags": "high beta", "rationale": "x"})
        risk = self._run_with(raw)
        self.assertEqual(risk["flags"], ["high beta"])

    def test_high_score_forces_veto(self):
        raw = json.dumps({"risk_score": 95, "risk_band": "Severe", "veto": False,
                          "flags": [], "rationale": "x"})
        with mock.patch.object(risk_manager, "_quant_risk", return_value=90):
            with mock.patch.object(risk_manager.llm, "complete", return_value=raw):
                out = risk_manager.run({"ticker": "AAPL", "market": {}}, lambda a, m: None)
        self.assertTrue(out["risk"]["veto"])


class SecToolsTests(unittest.TestCase):
    def test_strip_html_decodes_numeric_entities(self):
        html = "<p>The Company&#8217;s risks include &#8220;competition&#8221; &amp; costs.</p>"
        self.assertEqual(sec_tools._strip_html(html),
                         "The Company’s risks include “competition” & costs.")

    def test_fallback_is_not_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(sec_tools, "_CACHE", Path(tmp)):
                with mock.patch.object(sec_tools, "_cik_for", side_effect=OSError("edgar down")):
                    result = sec_tools.get_10k_text("FAKETICK")
                self.assertTrue(result["source"].startswith("fallback"))
                self.assertEqual(list(Path(tmp).iterdir()), [])


class ChunkTextTests(unittest.TestCase):
    def test_chunks_start_on_word_boundaries(self):
        text = " ".join(f"word{i}" for i in range(2000))
        for c in chunk_text(text):
            self.assertTrue(c.startswith("word"), f"chunk starts mid-word: {c[:20]!r}")


class GetNewsTests(unittest.TestCase):
    def test_parses_nested_content_schema(self):
        items = [{"id": "a", "content": {"title": "AAPL beats estimates"}},
                 {"id": "b", "content": {"title": "AAPL raises guidance"}}]
        fake_yf = types.SimpleNamespace(Ticker=lambda t: types.SimpleNamespace(news=items))
        with mock.patch.dict(sys.modules, {"yfinance": fake_yf}):
            news = market_tools.get_news("AAPL")
        self.assertEqual(news["source"], "yfinance")
        self.assertEqual(news["headlines"],
                         ["AAPL beats estimates", "AAPL raises guidance"])

    def test_parses_flat_legacy_schema(self):
        items = [{"title": "AAPL ships new product"}]
        fake_yf = types.SimpleNamespace(Ticker=lambda t: types.SimpleNamespace(news=items))
        with mock.patch.dict(sys.modules, {"yfinance": fake_yf}):
            news = market_tools.get_news("AAPL")
        self.assertEqual(news["headlines"], ["AAPL ships new product"])


class _FakeGroqClient:
    """chat.completions.create 404s on the dead model, succeeds on the live one."""

    def __init__(self, dead: str, alive: str):
        self.dead, self.alive = dead, alive
        outer = self

        class _Completions:
            def create(self, **kw):
                if kw["model"] == outer.dead:
                    raise RuntimeError(
                        "Error code: 404 - {'error': {'code': 'model_not_found', "
                        f"'message': 'The model `{outer.dead}` does not exist'}}}}")
                msg = types.SimpleNamespace(content="live answer", tool_calls=None)
                return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])

        class _Models:
            def list(self):
                data = [types.SimpleNamespace(id=i) for i in
                        ("whisper-large-v3", outer.alive, "playai-tts")]
                return types.SimpleNamespace(data=data)

        self.chat = types.SimpleNamespace(completions=_Completions())
        self.models = _Models()


class DecommissionedModelTests(unittest.TestCase):
    def test_complete_recovers_from_model_not_found(self):
        fake = _FakeGroqClient(dead="llama-old-retired", alive="llama-3.1-8b-instant")
        with mock.patch.object(llm, "_client", fake), \
             mock.patch.object(llm, "_provider", "groq"), \
             mock.patch.object(llm, "_model", "llama-old-retired"), \
             mock.patch.object(llm, "MODEL", "llama-old-retired"):
            out = llm.complete("system", "user")
            self.assertEqual(out, "live answer")
            self.assertEqual(llm.MODEL, "llama-3.1-8b-instant")  # health reflects the switch

    def test_is_model_gone_detection(self):
        self.assertTrue(llm._is_model_gone(RuntimeError("'code': 'model_not_found'")))
        self.assertTrue(llm._is_model_gone(RuntimeError("model X has been decommissioned")))
        self.assertFalse(llm._is_model_gone(RuntimeError("Error code: 429 rate limit")))


if __name__ == "__main__":
    unittest.main()
