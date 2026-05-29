# ⚡ Autonomous Financial Analyst — a Hierarchical Multi-Agent System

A **supervisor agent** orchestrates a team of five specialized agents to research any
publicly traded stock and produce a **risk-scored investment memo** — autonomously, with
a live, streamed view of every agent's reasoning and tool calls.

> _Educational research tool — not financial advice._

![architecture](docs/architecture.svg)

## Why this is interesting (engineering highlights)

- **Hierarchical multi-agent orchestration.** A supervisor routes work across Market Data,
  Fundamental, News/Sentiment, Risk, and Report-Writer agents over a shared typed state.
- **Reflection loop.** The supervisor re-dispatches the Fundamental agent if its output is
  low-confidence before proceeding — agentic self-correction, not a fixed pipeline.
- **Risk agent with veto authority.** The Risk Manager blends a *deterministic* quant score
  (beta, volatility, valuation) with LLM judgment and can **veto** a recommendation, which the
  Report Writer is forced to honor. This is real cross-agent decision-making.
- **Live agent-trace UI.** Server-Sent Events stream every step to a single-file frontend so you
  can watch the agents collaborate in real time.
- **Eval harness.** `evals/run_eval.py` runs the system over a basket of tickers and reports
  coverage, latency, and veto rate — a production-mindset signal.
- **Runs with zero credentials.** No API key? The system degrades to deterministic **MOCK mode**
  (mock LLM + synthetic market data) so it always demos end-to-end. Add a key for **LIVE mode**.

## Architecture

```
                    ┌─────────────────┐
   "AAPL"  ───────► │   Supervisor    │  routes • reflects • aggregates • forces veto
                    └────────┬────────┘
        ┌──────────┬─────────┼─────────┬──────────────┐
        ▼          ▼         ▼         ▼              ▼
   Market Data  Fundamental  News &   Risk Manager   Report
     Agent       Analyst    Sentiment  (veto power)   Writer
   (yfinance)   (LLM)       (LLM)      (quant+LLM)    (LLM)
```

The graph is a **hand-rolled, LangGraph-style state machine** (`backend/graph.py`). Implementing
it directly keeps dependencies tiny and the control flow fully inspectable; it's trivial to swap
in `langgraph` since the node/edge model is identical.

## Tech stack

Python · FastAPI · Server-Sent Events · Anthropic Claude (tool-use ready) · yfinance · vanilla JS UI

## Quickstart

```bash
cd financial-analyst-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# (optional) enable LIVE mode
cp .env.example .env   # then add ANTHROPIC_API_KEY
export $(grep -v '^#' .env | xargs)   # or use your own env loader

# run the server
python -m backend.server
# open http://localhost:8000
```

Run the eval harness:

```bash
python -m evals.run_eval
```

## Project layout

```
backend/
  agents/        market_data, fundamental, news_sentiment, risk_manager, report_writer
  tools/         market_tools (yfinance + synthetic fallback)
  graph.py       supervisor / orchestrator (state graph + reflection loop)
  llm.py         Claude wrapper with deterministic mock fallback
  server.py      FastAPI + SSE streaming
frontend/
  index.html     live agent-trace UI (single file, no build step)
evals/
  run_eval.py    multi-ticker coverage / latency / veto-rate report
```

## Resume bullet

> Built a hierarchical multi-agent system (supervisor + 5 specialized agents with a risk-veto
> mechanism and reflection loop) that autonomously researches equities via live market/news data
> and streams risk-scored investment memos to a real-time UI; included an eval harness measuring
> coverage, latency, and veto rate across a ticker basket.
