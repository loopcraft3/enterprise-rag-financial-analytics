FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/user/.cache/huggingface

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face runs the container as UID 1000
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY requirements.txt .
# CPU-only torch first (the default Linux wheel is a multi-GB CUDA build), then everything else
RUN pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt

USER user

# Download the embedding model at build time so startup is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

COPY --chown=user . .

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]