FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY Task2 /app/Task2
COPY backend /app/backend
ENV PYTHONPATH=/app HF_HOME=/tmp/hf-cache CHROMA_DIR=/tmp/chroma_public_demo
EXPOSE 7860
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "7860"]
