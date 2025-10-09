FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    netcat-openbsd \
    libpoppler-cpp-dev \
    tesseract-ocr \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY sciencesage/ sciencesage/
COPY scripts/ scripts/
COPY Makefile .
RUN mkdir -p data
COPY notebooks/ notebooks/
COPY docs/ docs/
COPY images/ images/
COPY tests/ tests/

# Install Qdrant (standalone binary)
RUN wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz \
    && tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz \
    && mv qdrant /usr/local/bin/ \
    && rm qdrant-x86_64-unknown-linux-gnu.tar.gz

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8501 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
