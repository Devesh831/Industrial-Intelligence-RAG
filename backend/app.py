"""Public demo API. Only aggregate results and generated demo PDFs are loaded."""
import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from Task2.prototype.rag_prototype import answer, build_index, EMBEDDING_MODEL, GENERATION_MODEL

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "Task2" / "prototype" / "demo_docs"
DB = Path(os.getenv("CHROMA_DIR", "/tmp/chroma_public_demo"))


def initialize_rag(app):
    """Load models and build the small demo index outside the server startup path."""
    try:
        from sentence_transformers import SentenceTransformer
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        from Task2.prototype.make_demo_docs import make_docs
        if not DOCS.exists() or not list(DOCS.glob("*.pdf")):
            make_docs()
        embedder = SentenceTransformer(EMBEDDING_MODEL)
        tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(GENERATION_MODEL).eval()
        app.state.models_ready = True
        collection = build_index(DOCS, DB, embedder)
        app.state.index_ready = collection.count() > 0
        def generate(prompt: str) -> str:
            tokens = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            return tokenizer.decode(model.generate(**tokens, max_new_tokens=120, do_sample=False)[0], skip_special_tokens=True)
        app.state.rag = (collection, embedder, generate)
    except Exception as exc:
        app.state.startup_error = type(exc).__name__


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models_ready = False
    app.state.index_ready = False
    app.state.startup_error = None
    # Yield immediately so Render can connect to the injected PORT. The model
    # download and Chroma build run in a worker thread after the socket opens.
    app.state.initializer_task = asyncio.create_task(asyncio.to_thread(initialize_rag, app))
    yield


app = FastAPI(title="Industrial Intelligence Public Demo API", lifespan=lifespan)
origins = [value.strip() for value in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",") if value.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=300)


@app.get("/health")
def health():
    models_ready = bool(getattr(app.state, "models_ready", False))
    index_ready = bool(getattr(app.state, "index_ready", False))
    payload = {"status": "ready" if models_ready and index_ready else "starting", "demo_only": True,
               "models_ready": models_ready, "index_ready": index_ready,
               "startup_error": getattr(app.state, "startup_error", None)}
    return JSONResponse(status_code=200 if models_ready and index_ready else 503, content=payload)


@app.get("/analytics")
def analytics():
    # Verified aggregates from Task1/results.json; no row-level telemetry is shipped.
    return {"rows": 377719, "missing_timestamps": 861, "shutdown_events": 68,
            "shutdown_hours": 5402, "anomaly_events": 1765, "test_origins": 6268,
            "persistence_mae": 11.4244, "persistence_rmse": 20.1097,
            "forest_mae": 9.3149, "forest_rmse": 16.9377,
            "coverage": "2017-01-01 to 2020-08-07", "shutdown_note": "Unverified threshold proxy"}


@app.post("/ask")
def ask(query: Question):
    if not getattr(app.state, "models_ready", False) or not getattr(app.state, "index_ready", False):
        raise HTTPException(status_code=503, detail="The demo models and document index are still starting")
    collection, embedder, generate = app.state.rag
    try:
        response, sources = answer(query.question, collection, embedder, generate)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The demo model is temporarily unavailable") from exc
    return {"answer": response, "sources": sources, "corpus": "Fictional public demo documents"}
