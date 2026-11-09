# Local RAG prototype

From the project root create a Python environment and run `pip install -r requirements.txt`. Put permitted, text-based technical PDFs in `Task2/prototype/docs/` (the supplied files are intentionally ignored by Git). Then run:

```powershell
python Task2/prototype/rag_prototype.py --question "What can a sudden draft drop indicate?"
```

The first run downloads the free Hugging Face models `sentence-transformers/all-MiniLM-L6-v2` and `google/flan-t5-small`; later runs can use the local cache. It rebuilds `chroma_db` from the input folder by default, so removed or changed files do not leave stale evidence. Add `--reuse-index` for faster subsequent questions, but omit it after any document changes. Each run requires enough disk, memory and CPU for the models. `--docs` selects a different PDF folder, `--db` selects another local index, and `--max-distance` adjusts the uncalibrated cosine distance cutoff. `python -m unittest discover -s Task2/prototype -p "test_*.py"` tests chunking and guardrail behavior without downloading models.

For a fictional test corpus, run `python Task2/prototype/make_demo_docs.py`, then pass `--docs Task2/prototype/demo_docs`. Those PDFs are explicitly fictional and must not be treated as operating guidance. Real files and derived vectors are private and excluded from Git.

Outputs include a generated answer and retrieved filename, page, distance and snippets. Check the cited pages: generated text can be wrong even when citations are present. Scanned pages need OCR; the basic extractor can produce incomplete text or warnings. Sensitive-query blocking and prompt-injection resistance are limited heuristics. Do not use this prototype to make safety-critical decisions without human review.
