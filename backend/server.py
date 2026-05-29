"""FastAPI server. Streams the multi-agent run as Server-Sent Events so the
frontend can render a live agent trace, and serves the single-file UI."""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse

from . import graph, llm

app = FastAPI(title="Autonomous Financial Analyst", version="1.0.0")

FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "llm_mode": "live" if llm.live_mode() else "mock", "model": llm.MODEL}


@app.get("/api/analyze")
def analyze(ticker: str):
    def stream():
        for event in graph.run_analysis(ticker):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/")
def index():
    return FileResponse(FRONTEND)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.server:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
