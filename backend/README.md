# Public demo API

The verified `/ask` API path is extractive and evidence-based. Render Free uses
the lightweight hash mode over fictional demo PDFs. FLAN-T5 remains an optional
standalone local CLI capability only; it is not loaded by the public deployment.

Run from the repository root: `pip install -r backend/requirements.txt` then `uvicorn backend.app:app --reload --port 7860`. The first start downloads MiniLM and FLAN-T5-small. Set `FRONTEND_ORIGINS=http://localhost:3000` for local CORS. `GET /analytics` returns approved aggregate results; `POST /ask` accepts `{"question":"..."}` and indexes only generated fictional PDFs. `/health` reports API availability.

For Render, create a Docker Web Service from this repository or apply `render.yaml`. The root `Dockerfile` is the entry point and uses `${PORT:-7860}` so it works with Render's injected port and locally. `ENABLE_LOCAL_MODELS=false` is intentional on the 512 MB Free tier: the service uses deterministic hash retrieval plus extractive cited answers, while the optional PyTorch/FLAN-T5 path remains available for larger hosts. FastAPI yields from its lifespan immediately; index initialization runs in a background worker after the port is available. Set `FRONTEND_ORIGINS` to the exact Vercel origin, configure `/health` as the HTTP health check, and wait for `status: ready`, `models_ready: true` and `index_ready: true` before testing `/analytics` or `/ask`. Render Free services sleep after inactivity and have an ephemeral filesystem, so the model cache and Chroma index are rebuilt after restarts. No secret keys are needed for the public sample.
