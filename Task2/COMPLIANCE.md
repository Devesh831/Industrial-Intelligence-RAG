# Task 2 Compliance Report

This report maps the original ExactSpace assignment requirements to the checked-in implementation.

| Requirement | Status | Evidence or limitation |
|---|---|---|
| Architecture covering ingestion, chunking, embeddings, vector store, retrieval, LLM and guardrails | Implemented | `architecture_diagram.pptx`, `notes.md` |
| PDF ingestion and page-aware chunking | Implemented locally | `prototype/rag_prototype.py` uses pypdf and 160-word/40-word-overlap page chunks |
| Open-source embeddings | Implemented locally and in full API mode | `sentence-transformers/all-MiniLM-L6-v2`; Render default uses a deterministic lightweight fallback |
| ChromaDB vector index | Implemented | Persistent local Chroma index with filename/page metadata |
| Retrieval with source citations/snippets | Implemented | `/ask` and CLI return citation, file, page, distance and snippet |
| Free/open-source LLM answer generation | Implemented locally and optionally in API mode | `google/flan-t5-small` is loaded only with `ENABLE_LOCAL_MODELS=true` |
| Graceful no-answer fallback | Implemented | Distance threshold and fallback response |
| Sensitive-query guardrail | Implemented | Credential/sensitive-identifier heuristic filter |
| Prompt-injection and hallucination mitigations | Partially implemented | Evidence-only prompt and citations; not a security boundary, no claim of verified faithfulness |
| Retrieval evaluation | Partially implemented | Evaluation approach and metrics are documented; no broad labeled benchmark is included |
| 10x corpus, 100+ users and cost scalability plan | Implemented as design notes only | Proposed in `notes.md`; not load-tested |
| Public deployment using the full LLM | Not implemented | Render Free intentionally serves lightweight mode because the full PyTorch stack may exceed 512 MB |

The lightweight public mode must not be described as an LLM. The full mode is runnable locally with the documented Hugging Face downloads and performs dense embedding retrieval plus FLAN-T5 generation.
