FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    netcat \
    libpoppler-cpp-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY sciencesage/ sciencesage/
COPY scripts/ scripts/
COPY Makefile .
COPY requirements.txt .
COPY data/ data/     
COPY notebooks/ notebooks/
COPY docs/ docs/
COPY images/ images/
COPY tests/ tests/

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Install Qdrant (standalone binary)
RUN wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz \
    && tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz \
    && mv qdrant /usr/local/bin/ \
    && rm qdrant-x86_64-unknown-linux-gnu.tar.gz

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["./entrypoint.sh"]