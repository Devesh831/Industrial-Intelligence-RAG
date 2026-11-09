# Public demo API

Run from the repository root: `pip install -r backend/requirements.txt` then `uvicorn backend.app:app --reload --port 7860`. The first start downloads MiniLM and FLAN-T5-small. Set `FRONTEND_ORIGINS=http://localhost:3000` for local CORS. `GET /analytics` returns approved aggregate results; `POST /ask` accepts `{"question":"..."}` and indexes only generated fictional PDFs. `/health` reports API availability.

For Hugging Face Spaces, create a **Docker** Space. Copy this repository into the Space and use `backend/Dockerfile` as the Dockerfile (or set the Space README YAML to `sdk: docker`, `app_file: backend/Dockerfile`). Set `FRONTEND_ORIGINS` to the exact Vercel origin. Free CPU startup can take several minutes; ephemeral `/tmp` storage causes reindexing on restart. For production, use persistent storage and health monitoring. No secret keys are needed for the public sample.
