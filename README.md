# Industrial Intelligence — Machine Analytics & Cited RAG

[![Backend and RAG tests](https://img.shields.io/badge/backend%20%2B%20RAG-14%20passed-16a34a.svg)](backend/test_app.py)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.29-black.svg)](frontend/package.json)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab.svg)](requirements.txt)
[![Render](https://img.shields.io/badge/API-Render%20Free-0f766e.svg)](render.yaml)

**A reproducible cyclone sensor analysis paired with a public document question-answering demo.** Built by Devesh Gautam as a data science internship portfolio project. The analysis studies operating patterns, proxy shutdowns, state-specific anomalies and one-hour temperature forecasts. The app presents aggregate findings and a RAG assistant backed by fictional public sample PDFs.

## Live demo

**Live Website:** [industrial-intelligence-rag.vercel.app](https://industrial-intelligence-rag.vercel.app)  
**GitHub Repository:** [Devesh831/Industrial-Intelligence-RAG](https://github.com/Devesh831/Industrial-Intelligence-RAG)  
**Backend API:** [industrial-intelligence-rag.onrender.com](https://industrial-intelligence-rag.onrender.com)

The frontend is deployed on Vercel and communicates with the FastAPI backend hosted on Render. The public backend uses the documented lightweight RAG mode on the free tier.

## Table of contents

- [Application showcase](#application-showcase)
- [Why this project](#why-this-project)
- [What it does](#what-it-does)
- [Measured Task 1 results](#measured-task-1-results)
- [Architecture](#architecture)
- [Stack](#stack)
- [Run locally](#run-locally)
- [Deploy in this order](#deploy-in-this-order)
- [Repository map](#repository-map)
- [Limits and next steps](#limits-and-next-steps)

## Application Showcase

### 1. Project Overview & Landing Page

The landing page introduces Industrial Intelligence and the path from machine telemetry to practical insight. It highlights the two capabilities: machine analytics and document-based question answering, alongside the telemetry preview.

![Industrial Intelligence project overview and landing page](docs/screenshots/project-overview.png)

---

### 2. Machine Analytics Dashboard

This view presents the actual sensor-analysis summary: 377,719 records, detected idle events, anomalous events and forecasting MAE. It also communicates the workflow from cleaning and behavior detection through one-hour forecasting.

![Machine analytics dashboard with dataset metrics and workflow](docs/screenshots/machine-analytics.png)

---

### 3. RAG Assistant — Document-Based Question Answering

The assistant demonstrates natural-language technical questions, retrieved answers, source snippets and page-level citations. The displayed public demo uses fictional sample PDFs; citations make evidence inspectable but do not guarantee every generated sentence is correct.

![RAG assistant showing a cited answer from fictional sample PDFs](docs/screenshots/rag-assistant.png)

---

### 4. System Architecture & Retrieval Pipeline

This section shows the retrieval workflow from PDF pages to word chunks, isolated HashEmbedder or MiniLM indexes, Chroma search, extractive evidence selection and cited snippets. The standalone CLI's optional FLAN-T5 path is local-only and is not used by the current API or public deployment.

![System architecture and document retrieval pipeline](docs/screenshots/system-architecture.png)

## Why this project

Industrial sensor histories are irregular and lack reliable event labels. Operators also need to search long manuals without losing the source of an answer. This project demonstrates an end-to-end approach: make the time series usable, measure model performance on later data, and return retrieved document evidence with page references. The public demo avoids exposing the supplied workbook or restricted manuals.

## What it does

| Machine analytics | RAG assistant |
| --- | --- |
| Builds a strict five-minute timeline and audits missing values | Extracts text page by page from PDFs |
| Finds low-temperature/low-draft periods with an explicit proxy rule | Splits pages into overlapping chunks and embeds them with MiniLM |
| Clusters active sensor readings with K-means | Searches a local Chroma vector index |
| Detects anomalies separately within each cluster | Full local mode uses FLAN-T5-small; Render Free uses a labeled lightweight extractive mode, with filename, page and snippet |
| Compares persistence and a 12-step random forest on later data | Falls back when retrieval is weak and filters selected sensitive queries |

## Measured Task 1 results

The supplied workbook contains **377,719 readings** from **1 January 2017 to 7 August 2020**, with **861 missing five-minute timestamps**. The analysis detected **68 proxy shutdown events / 5,402 hours** across the full available period and **1,765 anomaly events**. Restricting shutdown overlap to the three full calendar years 2017–2019 yields **65 events / 4,487 hours**. These are threshold-based findings, not confirmed plant logs.

The one-hour forecast uses **6,268 later, fully observed hourly origins**. Across all 12 horizons, persistence scored **MAE 11.42 / RMSE 20.11**; the random forest scored **MAE 9.31 / RMSE 16.94**. The dataset does not specify physical measurement units.

![Measured held-out forecast error by horizon](frontend/public/forecast-error.svg)

The public chart reports only aggregate error. Local analysis outputs include the one-week and one-year time-series views, highlighted shutdown periods and four anomaly context plots. See [Task 1 methods](Task1/README.md) and `Task1/findings.md` in the private submission for event hypotheses and caveats.

## Architecture

```mermaid
flowchart LR
  A[Permitted demo PDFs] --> B[Page extraction]
  B --> C[Overlapping chunks]
  C --> D[MiniLM embeddings]
  D --> E[Local Chroma index]
  Q[Question] --> E
  E --> F[Distance filter]
  F --> G[FLAN-T5-small]
  G --> H[Answer + page snippets]
  M[Private workbook] --> N[Offline Python analysis]
  N --> O[Approved aggregate metrics]
  O --> P[FastAPI]
  H --> P
  P --> V[Next.js on Vercel]
```

The same flow is provided as an editable [PowerPoint architecture diagram](Task2/architecture_diagram.pptx). The public corpus is generated by `Task2/prototype/make_demo_docs.py`; those documents are explicitly fictional. **No RAG answer or screenshot is presented as validated operational advice.** A real assistant response must be checked against its cited page.

## Stack

Python, Pandas, NumPy, Scikit-learn, Matplotlib, FastAPI, Pydantic, pypdf, Sentence Transformers, Chroma, Hugging Face Transformers, PyTorch, Next.js, React and TypeScript. The frontend is prepared for Vercel; the Dockerized API is prepared for Render.

## Run locally

1. Install Python 3.11+ and Node.js 20+. Create a Python environment and run `pip install -r requirements.txt` for analysis or `pip install -r backend/requirements.txt` for the web API.
2. For the private machine analysis, run `python Task1/task1_analysis.py path/to/data.xlsx` and `python Task1/validate_outputs.py`. The raw workbook is not included in Git.
3. Start the public API with `uvicorn backend.app:app --port 7860`. The first start downloads the free models and creates fictional demo PDFs. Check `http://localhost:7860/health`.
4. In `frontend`, copy `.env.example` to `.env.local`, run `npm install`, then `npm run dev`. Open `http://localhost:3000`.
5. Run `python -m pytest backend/test_app.py Task2/prototype/test_rag.py -q` and `npm run build` before deployment.

## Deploy in this order

### 1. Render backend

1. In Render, choose **New → Web Service**, connect GitHub and select `Devesh831/Industrial-Intelligence-RAG`.
2. Use the checked-in `render.yaml` as the Blueprint, or configure the service manually with Docker runtime, root directory `.`, root `Dockerfile`, and Free plan. The root Dockerfile installs `backend/requirements.txt`, copies only `Task2` and `backend`, and listens on Render's injected `PORT` (falling back to 7860 locally). `.dockerignore` excludes `frontend`, `Task1`, private PDFs, spreadsheets, generated plots and local caches.
3. Set `FRONTEND_ORIGINS` to the exact Vercel origin you will use later. Before the frontend exists, use `http://localhost:3000`; update it and redeploy after Vercel is created.
4. Set the Render health check path to `/health`. The FastAPI lifespan yields immediately so the process binds Render's port before a background worker builds Chroma. Free-tier deployments keep `ENABLE_LOCAL_MODELS=false`, using lightweight hash retrieval and extractive cited answers; set it to `true` only on a larger host. Render should route traffic only when this endpoint returns 200 with `status: "ready"`, `models_ready: true` and `index_ready: true`.
5. Verify `GET https://YOUR-SERVICE.onrender.com/analytics`. Verify `POST /ask` with JSON such as `{"question":"What does the public demo document say about a draft drop?"}`. A 503 while health is `starting` is expected; inspect Render logs if it remains 503 after model loading.

### 2. Vercel frontend

1. Import the same GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`. Vercel will use `frontend/vercel.json`, `npm install --no-audit --no-fund` and `npm run build`.
3. Add the Production environment variable `NEXT_PUBLIC_API_BASE_URL=https://industrial-intelligence-rag.onrender.com`. Redeploy after changing it; the browser needs the value at build time. For local development, copy `frontend/.env.example` to `frontend/.env.local` and use `http://localhost:7860` only when running the backend locally.
4. Open the Vercel preview first and verify the analytics section loads, the assistant returns citations, and browser requests do not show CORS errors. Then promote the tested deployment.
5. Replace the `Live app` placeholder near the top of this README only after the Vercel URL and its API calls have been tested. Do not publish a placeholder as if it were live.

If a local browser shows `__webpack_modules__[moduleId] is not a function` or the server reports missing files under `.next`, stop all dev/build processes, remove the generated `frontend/.next` directory, and run `npm run dev` again. Do not run `next build` concurrently with `next dev`, because both mutate `.next`. The development script uses Next's Turbopack path to avoid stale Webpack HMR module tables. This is a generated-cache issue; the production build is independently verified.

If the Render service sleeps, allow roughly a minute for a cold start before retrying. Render Free web services spin down after inactivity and use an ephemeral filesystem, so the Hugging Face model cache and Chroma index may be downloaded or rebuilt after restarts. Render persistent disks are not available on Free web services; this demo intentionally rebuilds its small fictional index at startup. The free instance's memory and CPU may be insufficient for larger models or a large corpus. Render describes these constraints in its [free service documentation](https://render.com/docs/free), [filesystem documentation](https://render.com/docs/disks), and [health check documentation](https://render.com/docs/health-checks).

`FRONTEND_ORIGINS` is an exact CORS allowlist. The browser-facing API URL is public by design and must not contain credentials. Keep service tokens only in server-side secrets if a future feature needs them. See [backend instructions](backend/README.md) and [RAG instructions](Task2/prototype/README.md).

## Repository map

```text
frontend/             Next.js portfolio UI and public aggregate chart
backend/              FastAPI public demo and Docker requirements
Task1/                Reproducible private-data analysis and validators
Task2/prototype/      Reusable local PDF RAG logic and fictional demo generator
Task2/notes.md        Retrieval, guardrail and scaling trade-offs
Dockerfile            Render Docker deployment entry point
```

## Limits and next steps

## Deployment Architecture & Limitations

The current FastAPI `/ask` implementation returns extractive, evidence-based
answers in both lightweight and semantic retrieval modes. The standalone local
CLI retains an optional FLAN-T5 generation path for a suitably provisioned
machine; FLAN-T5 is not used by the public Render deployment.

The project has two execution environments. The public frontend is deployed on
Vercel and the public FastAPI backend is hosted on Render. Render Free provides
approximately 512 MB RAM, which was not sufficient for reliably loading and
indexing the complete 11-PDF technical corpus with the heavier local embedding
and model stack. The public service therefore runs a lightweight demonstration
configuration over fictional sample PDFs. It demonstrates the workflow and
citation contract, but it does not provide the same full-corpus functionality
as the local implementation.

The complete local implementation processes all 11 supplied technical PDFs:
195 pages become 403 page-aware ChromaDB chunks. It supports the lightweight
`HashEmbedder` mode and an opt-in Sentence Transformers
`all-MiniLM-L6-v2` semantic mode, each using a separate ChromaDB index. Local
execution provides technical-document retrieval, filename/page citations and
evidence-based abstention when the corpus lacks sufficient support. The current
API answer path is extractive evidence selection; it does not claim that
FLAN-T5 or another generative LLM is running.

For the complete local API, keep the authorized PDFs in
`Task2/prototype/docs/` and run:

```powershell
$env:RAG_DOCS_DIR = (Resolve-Path "Task2/prototype/docs").Path
$env:CHROMA_DIR = "C:\path\to\local_test_chroma_full"
$env:RAG_REUSE_INDEX = "true"
$env:RAG_EMBEDDING_MODE = "hash"
$env:ENABLE_LOCAL_MODELS = "false"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 7860
```

For optional local MiniLM retrieval, use a separate existing semantic index,
set `RAG_EMBEDDING_MODE=semantic`, `ENABLE_LOCAL_MODELS=true`, and point
`CHROMA_DIR` to that semantic index. See the detailed setup in
[`Task2/prototype/README.md`](Task2/prototype/README.md).

### RAG modes and local evaluation

The RAG workflow extracts PDF text page by page, creates overlapping
page-aware chunks, stores embeddings in ChromaDB, retrieves candidates and
returns complete evidence snippets with filename/page citations. The public
Render service uses deterministic `HashEmbedder` retrieval over fictional demo
documents. The full local corpus contains 11 authorized PDFs and 403 chunks.

Local semantic retrieval is opt-in with Sentence Transformers
`all-MiniLM-L6-v2` through `RAG_EMBEDDING_MODE=semantic`. It uses a separate
Chroma index from the hash-based index so embedding spaces cannot be mixed.
Sentence-level selection, duplicate avoidance and abstention are implemented,
but citations remain evidence pointers rather than proof that every generated
claim is correct. The API modes currently return lightweight extractive
evidence; do not describe the deployed demo as using an LLM.

Locally measured observations for the semantic index were approximately 6
seconds to load MiniLM, 34 seconds to index 403 chunks, and 12-71 ms query
latency after model loading. These measurements depend on hardware. The
`RAG_MAX_DISTANCE` environment variable controls the semantic cutoff and needs
calibration with labeled questions; weak semantic matches can still require
human review. Semantic mode is not enabled on Render Free because PyTorch and
model memory exceed the intended lightweight deployment budget.

For local semantic setup, see
[`Task2/prototype/README.md`](Task2/prototype/README.md). Keep the supplied
PDFs and local Chroma indexes outside GitHub and public deployment images.

Shutdown events are proxy labels; the model needs operator logs to measure detection accuracy. The RAG distance threshold is uncalibrated, and the small local generator can repeat snippets or make unsupported claims. Some PDFs need OCR, and the supplied corpus mixes industrial and weather-cyclone documents. Before operational use, curate the corpus, add labeled retrieval questions, measure faithfulness and abstention, verify citations sentence by sentence, and test capacity with concurrent users. The portfolio demonstrates methods and transparent limitations; it is not a plant control system.
