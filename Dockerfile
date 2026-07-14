# Contract Risk Highlighter — Hugging Face Spaces (Docker SDK)
FROM python:3.12-slim

# System deps: build tools for a few wheels; curl for healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces run as non-root UID 1000. Create that user and give it a home so
# model/tokenizer caches (HF, sentence-transformers, NLTK) are writable.
RUN useradd -m -u 1000 appuser
ENV HOME=/home/appuser \
    HF_HOME=/home/appuser/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/home/appuser/.cache/sentence_transformers \
    NLTK_DATA=/home/appuser/nltk_data \
    TOKENIZERS_PARALLELISM=false \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python deps first (better layer caching).
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code.
COPY --chown=appuser:appuser . .

USER appuser

# Pre-download NLTK data and the CrossEncoder reranker at BUILD time so the
# first request isn't blocked on a ~400MB model download.
RUN python -c "import nltk; nltk.download('punkt', download_dir='$NLTK_DATA'); nltk.download('stopwords', download_dir='$NLTK_DATA')" && \
    python -c "from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-base')"

EXPOSE 7860

# HF Spaces expects the app on 0.0.0.0:7860.
CMD ["uvicorn", "api_wrapper:app", "--host", "0.0.0.0", "--port", "7860"]
