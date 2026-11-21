# Hisaab backend (FastAPI). Build:  docker build -t hisaab-backend .
# Run:   docker run --env-file .env -p 8000:8000 hisaab-backend
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FASTEMBED_CACHE_PATH=/opt/models \
    PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first so Docker can reuse this layer when only the code changes.
# requirements-deploy.txt uses fastembed (ONNX), not PyTorch, so the image stays small.
COPY requirements-deploy.txt .
RUN pip install -r requirements-deploy.txt

# Download the embedding model at build time, so the container starts fast.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

# Run as a normal user, not root.
RUN useradd -m -u 1000 appuser && chown -R appuser /app /opt/models
USER appuser

COPY --chown=appuser . .

EXPOSE 8000
# Platforms like Render set PORT; locally it defaults to 8000.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
