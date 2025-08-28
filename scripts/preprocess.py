#!/usr/bin/env python3

import os
import json
import hashlib
import uuid
import datetime

from pathlib import Path
from typing import List, Dict

from loguru import logger

# -------------------------
# Logging
# -------------------------
logger.add("logs/preprocess.log", rotation="5 MB", retention="7 days")
logger.info("Started preprocess.py script.")

# -------------------------
# Config
# -------------------------
PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR = Path("data/chunks")
CHUNK_SIZE = 500  # approx. words per chunk
OVERLAP = 50      # overlap between chunks for context

CHUNKS_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# Helpers
# -------------------------
def read_text_file(filepath: Path) -> str:
    """Read text from file."""
    logger.debug(f"Reading text file: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {filepath}: {e}")
        raise


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    """Split text into overlapping chunks (by words)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    logger.debug(f"Chunked text into {len(chunks)} chunks (chunk_size={chunk_size}, overlap={overlap})")
    return chunks


def get_topic_from_filename(filename: str) -> str:
    """Infer topic from filename (e.g., 'climate_nasa.txt' → 'climate')."""
    topic = filename.split("_")[0] if "_" in filename else filename.replace(".txt", "")
    logger.debug(f"Inferred topic '{topic}' from filename '{filename}'")
    return topic


def generate_id(text: str, prefix: str) -> str:
    """Generate a stable unique ID from hash of text."""
    hash_id = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{hash_id}"


# -------------------------
# Main Processing
# -------------------------
def process_file(filepath: Path) -> List[Dict]:
    """Convert a text file into JSONL chunks with metadata."""
    logger.info(f"Processing file: {filepath}")
    text = read_text_file(filepath)
    filename = filepath.stem
    topic = get_topic_from_filename(filename)
    # Use timezone-aware UTC datetime
    loadtime = datetime.datetime.now(datetime.UTC).isoformat()

    chunks = chunk_text(text)
    results = []

    for i, chunk in enumerate(chunks):
        chunk_id = generate_id(chunk, filename)
        chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
        results.append({
            "id": chunk_id,
            "uuid": chunk_uuid,
            "topic": topic,
            "source": filename,
            "chunk_index": i,
            "text": chunk,
            "loadtime": loadtime
        })
    logger.info(f"Processed {len(results)} chunks from {filepath.name}")
    return results


def main():
    all_chunks = []
    files = list(PROCESSED_DIR.glob("*.txt"))
    if not files:
        logger.warning(f"No .txt files found in {PROCESSED_DIR}")
    for filepath in files:
        logger.info(f"Processing {filepath.name}...")
        try:
            file_chunks = process_file(filepath)
            all_chunks.extend(file_chunks)
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")

    output_path = CHUNKS_DIR / "chunks.jsonl"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in all_chunks:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.success(f"Saved {len(all_chunks)} chunks to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save chunks to {output_path}: {e}")

    print(f"✅ Saved {len(all_chunks)} chunks to {output_path}")


if __name__ == "__main__":
    main()
