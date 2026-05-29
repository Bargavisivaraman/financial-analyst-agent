"""FastAPI server. Streams the multi-agent run as Server-Sent Events so the
React frontend can render a live agent trace, and serves the built SPA."""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import graph, llm

app = FastAPI(title="Autonomous Financial Analyst", version="2.0.0")

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "frontend-react" / "dist"


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "llm_mode": "live" if llm.live_mode() else "mock",
        "provider": llm.PROVIDER,
        "model": llm.MODEL,
    }


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


# Serve the built React SPA (index.html + hashed assets + public files like
# /architecture.svg). Mounted last so /api routes take precedence. html=True
# serves index.html at "/" and falls back to it for client-side routes.
if DIST.exists():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="spa")
else:
    @app.get("/")
    def _missing():
        return JSONResponse(
            {"error": "frontend not built", "hint": "run `npm run build` in frontend-react/"},
            status_code=503,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.server:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
