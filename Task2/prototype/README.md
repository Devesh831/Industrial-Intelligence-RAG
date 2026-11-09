# Local RAG prototype

The public portfolio API reuses the same retrieval and citation contracts through `backend/app.py`. Render Free runs a clearly labeled lightweight mode by default: deterministic hash embeddings plus extractive cited answers. It does not claim to be an LLM. The full assignment prototype remains available locally with Sentence Transformers, ChromaDB and FLAN-T5. Private or restricted manuals never enter the public Docker image.

From the project root create a Python environment and run `pip install -r requirements.txt`. Put permitted, text-based technical PDFs in `Task2/prototype/docs/` (the supplied files are intentionally ignored by Git). Then run:

```powershell
python Task2/prototype/rag_prototype.py --question "What can a sudden draft drop indicate?"
```

The first full-prototype run downloads the free Hugging Face models `sentence-transformers/all-MiniLM-L6-v2` and `google/flan-t5-small`; later runs can use the local cache. It rebuilds `chroma_db` from the input folder by default, so removed or changed files do not leave stale evidence. Add `--reuse-index` for faster subsequent questions, but omit it after document changes. Each full run requires substantially more memory and CPU than Render Free. `--docs` selects a different PDF folder, `--db` selects another local index, and `--max-distance` adjusts the uncalibrated cosine distance cutoff. `python -m unittest discover -s Task2/prototype -p "test_*.py"` tests chunking and guardrails without downloading models.

## API mode switch

`ENABLE_LOCAL_MODELS=false` is the safe Render default. Set `ENABLE_LOCAL_MODELS=true` before starting `uvicorn` on a sufficiently provisioned local machine to use Sentence Transformer embeddings and FLAN-T5 generation through the API. `/health` reports `model_mode` as `lightweight-extractive` or `local-models`; `/ask` always returns retrieved file, page, distance and snippet citations.

For a fictional test corpus, run `python Task2/prototype/make_demo_docs.py`, then pass `--docs Task2/prototype/demo_docs`. Those PDFs are explicitly fictional and must not be treated as operating guidance. Real files and derived vectors are private and excluded from Git.

Retrieval uses normalized page text, dense Chroma candidates and a lexical-overlap reranker. Weak candidates are rejected unless they have meaningful query-term overlap or a very strong dense score. Outputs include a generated answer and retrieved filename, page, distance, relevance score and focused snippets. Check the cited pages: generated text can be wrong even when citations are present. Scanned pages need OCR; the basic extractor can produce incomplete text or warnings. Sensitive-query blocking and prompt-injection resistance are limited heuristics. Do not use this prototype to make safety-critical decisions without human review.
