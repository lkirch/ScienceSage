#!/usr/bin/env python3

import os
import json
import hashlib

from pathlib import Path
from typing import List, Dict

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
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


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
    return chunks


def get_topic_from_filename(filename: str) -> str:
    """Infer topic from filename (e.g., 'climate_nasa.txt' → 'climate')."""
    return filename.split("_")[0] if "_" in filename else filename.replace(".txt", "")


def generate_id(text: str, prefix: str) -> str:
    """Generate a stable unique ID from hash of text."""
    hash_id = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{hash_id}"


# -------------------------
# Main Processing
# -------------------------
def process_file(filepath: Path) -> List[Dict]:
    """Convert a text file into JSONL chunks with metadata."""
    text = read_text_file(filepath)
    filename = filepath.stem
    topic = get_topic_from_filename(filename)

    chunks = chunk_text(text)
    results = []

    for i, chunk in enumerate(chunks):
        chunk_id = generate_id(chunk, filename)
        results.append({
            "id": chunk_id,
            "topic": topic,
            "source": filename,
            "chunk_index": i,
            "text": chunk
        })
    return results


def main():
    all_chunks = []
    for filepath in PROCESSED_DIR.glob("*.txt"):
        print(f"Processing {filepath.name}...")
        file_chunks = process_file(filepath)
        all_chunks.extend(file_chunks)

    output_path = CHUNKS_DIR / "chunks.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in all_chunks:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Saved {len(all_chunks)} chunks to {output_path}")


if __name__ == "__main__":
    main()
