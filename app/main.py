from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, HttpUrl

from .config import settings
from .pipeline import Analyzer, AnalysisError

analyzer = Analyzer(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Libera o cliente HTTP persistente do Ollama ao encerrar o servidor.
    analyzer.client.close()


app = FastAPI(
    title="Repository Intelligence MVP",
    version="0.2.0",
    description="Local/open-source GitHub repository analyzer using Ollama.",
    lifespan=lifespan,
)


class AnalyzeRequest(BaseModel):
    url: HttpUrl


STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", response_class=HTMLResponse)
def home():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.ollama_model}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    try:
        run_id = analyzer.start(str(request.url))
        return {"run_id": run_id, "status": "started"}
    except AnalysisError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/runs")
def list_runs():
    return analyzer.list_runs()


@app.get("/api/runs/{run_id}")
def run_status(run_id: str):
    try:
        return analyzer.status(run_id)
    except AnalysisError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/runs/{run_id}/report", response_class=PlainTextResponse)
def report(run_id: str):
    try:
        return analyzer.report(run_id)
    except AnalysisError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
