# Local RAG prototype

The public portfolio API reuses the same retrieval and citation contracts through `backend/app.py`. Render Free runs a clearly labeled lightweight mode by default: deterministic hash embeddings plus extractive cited answers. It does not claim to be an LLM. The full assignment prototype remains available locally with Sentence Transformers, ChromaDB and FLAN-T5. Private or restricted manuals never enter the public Docker image.

From the project root create a Python environment and run `pip install -r requirements.txt`. Put permitted, text-based technical PDFs in `Task2/prototype/docs/` (the supplied files are intentionally ignored by Git). Then run:

```powershell
python Task2/prototype/rag_prototype.py --question "What can a sudden draft drop indicate?"
```

The first full-prototype run downloads the free Hugging Face models `sentence-transformers/all-MiniLM-L6-v2` and `google/flan-t5-small`; later runs can use the local cache. It rebuilds `chroma_db` from the input folder by default, so removed or changed files do not leave stale evidence. Add `--reuse-index` for faster subsequent questions, but omit it after document changes. Each full run requires substantially more memory and CPU than Render Free. `--docs` selects a different PDF folder, `--db` selects another local index, and `--max-distance` adjusts the uncalibrated cosine distance cutoff. `python -m unittest discover -s Task2/prototype -p "test_*.py"` tests chunking and guardrails without downloading models.

## API mode switch

The API returns extractive evidence-based answers in both lightweight and
semantic retrieval modes. FLAN-T5 is retained only as an optional standalone
local CLI path and is not used by Render or the verified API semantic mode.

`ENABLE_LOCAL_MODELS=false` is the safe Render default. Set `ENABLE_LOCAL_MODELS=true` before starting `uvicorn` on a sufficiently provisioned local machine to use Sentence Transformer embeddings and FLAN-T5 generation through the API. `/health` reports `model_mode` as `lightweight-extractive` or `local-models`; `/ask` always returns retrieved file, page, distance and snippet citations.

The FastAPI app uses the fictional `demo_docs` corpus by default so the public
Render service never loads restricted manuals. To run the full supplied corpus
through the local frontend/API, set both variables from the project root:

```powershell
$env:RAG_DOCS_DIR = (Resolve-Path "Task2/prototype/docs").Path
$env:CHROMA_DIR = (Resolve-Path "Task2/prototype/chroma_full_api").Path
$env:ENABLE_LOCAL_MODELS = "true"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 7860
```

Then set `NEXT_PUBLIC_API_BASE_URL=http://localhost:7860` in
`frontend/.env.local` and restart Next.js. This keeps the existing API and UI
contracts unchanged while indexing all authorized PDFs in `Task2/prototype/docs`.
Do not set `RAG_DOCS_DIR` to the private corpus in a public deployment.

For a fictional test corpus, run `python Task2/prototype/make_demo_docs.py`, then pass `--docs Task2/prototype/demo_docs`. Those PDFs are explicitly fictional and must not be treated as operating guidance. Real files and derived vectors are private and excluded from Git.

## Optional semantic retrieval mode

The local API also supports an explicit MiniLM mode. It uses the locally cached
`sentence-transformers/all-MiniLM-L6-v2` model for both document and query
embeddings and must use a separate Chroma directory; it never mixes vectors
with the hash index. The measured local build for 403 chunks took about 34
seconds after a roughly 6-second model load, with observed query latency of
about 12-71 ms after loading. These are local observations, not guarantees.

```powershell
$env:RAG_DOCS_DIR = (Resolve-Path "Task2/prototype/docs").Path
$env:CHROMA_DIR = "C:\path\to\local_test_chroma_semantic"
$env:RAG_REUSE_INDEX = "true"
$env:RAG_EMBEDDING_MODE = "semantic"
$env:ENABLE_LOCAL_MODELS = "true"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 7860
```

Create the semantic index once with the local prototype using the same docs and
`--db` path, then reuse it. `RAG_MAX_DISTANCE` controls the cosine-distance
cutoff (default `0.65`); calibrate it with labeled questions because a close
semantic match can still be weak evidence. If semantic initialization fails,
the API reports the startup error and does not silently switch to hash vectors.
This mode performs retrieval and extractive evidence responses; FLAN-T5 is not
loaded by the API semantic path.

### Deployment Architecture & Limitations

The public Vercel frontend calls a FastAPI service on Render Free. That
instance has approximately 512 MB RAM, so the complete 11-PDF technical corpus
and heavier local embedding/model stack are not loaded there reliably. The
public service is therefore a resource-constrained demonstration over the
fictional `demo_docs` PDFs; it is functional for that corpus but does not offer
the full technical-document coverage available locally.

Locally, all 11 supplied PDFs (195 pages) are processed into 403 page-aware
chunks. Hash and MiniLM semantic retrieval use separate ChromaDB indexes, and
the local API returns source filename/page citations and abstains when evidence
is insufficient. The current answer path is extractive and evidence-grounded;
the API does not claim to run FLAN-T5.

For the complete local hash-mode API:

```powershell
$env:RAG_DOCS_DIR = (Resolve-Path "Task2/prototype/docs").Path
$env:CHROMA_DIR = "C:\path\to\local_test_chroma_full"
$env:RAG_REUSE_INDEX = "true"
$env:RAG_EMBEDDING_MODE = "hash"
$env:ENABLE_LOCAL_MODELS = "false"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 7860
```

For MiniLM, use `RAG_EMBEDDING_MODE=semantic`,
`ENABLE_LOCAL_MODELS=true`, and a separate semantic `CHROMA_DIR`; never point
semantic queries at the hash index. Set
`NEXT_PUBLIC_API_BASE_URL=http://localhost:7860` in `frontend/.env.local` and
start the frontend with `npm run dev`.

Retrieval uses normalized page text, dense Chroma candidates and a lexical-overlap reranker. Weak candidates are rejected unless they have meaningful query-term overlap or a very strong dense score. Outputs include a generated answer and retrieved filename, page, distance, relevance score and focused snippets. Check the cited pages: generated text can be wrong even when citations are present. Scanned pages need OCR; the basic extractor can produce incomplete text or warnings. Sensitive-query blocking and prompt-injection resistance are limited heuristics. Do not use this prototype to make safety-critical decisions without human review.
