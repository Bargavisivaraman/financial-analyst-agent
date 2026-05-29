"""Risk Manager Agent — computes a risk score and can VETO a recommendation.
This veto authority is the core 'agentic decision-making' signal of the system."""
from __future__ import annotations

import json
from typing import Any, Callable, Dict

from .. import llm

NAME = "risk_manager"

SYSTEM = (
    "You are a Risk Manager agent with veto authority. Given market metrics and analyst notes, "
    "return STRICT JSON with keys: risk_score (0-100, higher=riskier), risk_band "
    "(Low/Moderate/High/Severe), veto (bool), flags (list of short strings), rationale (string). "
    "Set veto=true only if risk is Severe (e.g. extreme volatility, solvency or fraud red flags)."
)


def _quant_risk(m: Dict[str, Any]) -> int:
    """Deterministic quantitative floor for the risk score, independent of the LLM."""
    score = 30
    beta = m.get("beta") or 1.0
    vol = m.get("volatility_30d") or 0.2
    pe = m.get("pe_ratio") or 20
    score += int((beta - 1) * 20)
    score += int(vol * 100)
    if pe and pe > 40:
        score += 10
    return max(0, min(100, score))


def run(state: Dict[str, Any], emit: Callable[[str, str], None]) -> Dict[str, Any]:
    m = state.get("market", {})
    emit(NAME, "Computing quantitative risk (beta, volatility, valuation)…")
    quant = _quant_risk(m)
    user = (
        f"Quant risk floor: {quant}\n"
        f"Metrics: beta={m.get('beta')} vol30d={m.get('volatility_30d')} pe={m.get('pe_ratio')}\n"
        f"Fundamental note: {state.get('fundamental','')}\n"
        f"News note: {state.get('news',{}).get('summary','')}"
    )
    raw = llm.complete(SYSTEM, user, max_tokens=400, json_mode=True)
    try:
        risk = json.loads(raw)
    except Exception:
        risk = {"risk_score": quant, "risk_band": "Moderate", "veto": False, "flags": [], "rationale": raw}
    # Blend LLM judgment with the deterministic floor.
    risk["risk_score"] = int((risk.get("risk_score", quant) + quant) / 2)
    if risk["risk_score"] >= 80:
        risk["veto"] = True
    verdict = "VETO" if risk.get("veto") else "cleared"
    emit(NAME, f"Risk score {risk['risk_score']}/100 ({risk.get('risk_band')}) — {verdict}.")
    return {"risk": risk}
