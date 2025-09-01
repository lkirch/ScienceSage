import os
import sys
from pathlib import Path
import json
import hashlib
import uuid
import datetime
import re
from typing import List, Dict
from loguru import logger
import tiktoken 

# Ensure project root is in sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import PROCESSED_DATA_DIR, CHUNKS_FILE, CHUNK_SIZE, CHUNK_OVERLAP, TOPIC_KEYWORDS, MAX_TOKENS

# -------------------------
# Logging
# -------------------------
logger.add("logs/preprocess.log", rotation="5 MB", retention="7 days")
logger.info("Started preprocess.py script.")

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


def extract_urls(text: str) -> List[str]:
    """Extract reference URLs from text."""
    url_pattern = r"https?://[^\s)]+"
    return re.findall(url_pattern, text)


def chunk_text_by_paragraphs(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into overlapping chunks, keeping paragraphs together.
    Paragraphs are joined until reaching chunk_size (word-based).
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = []

    word_count = 0
    for para in paragraphs:
        para_words = para.split()
        if word_count + len(para_words) > chunk_size and current_chunk:
            # save chunk
            chunks.append(" ".join(current_chunk))

            # overlap: keep last `overlap` words from previous chunk
            overlap_words = current_chunk[-overlap:] if overlap > 0 else []
            current_chunk = overlap_words + para_words
            word_count = len(current_chunk)
        else:
            current_chunk.extend(para_words)
            word_count += len(para_words)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    logger.debug(
        f"Chunked text into {len(chunks)} chunks (chunk_size={chunk_size}, overlap={overlap})"
    )
    return chunks


def generate_id(text: str, prefix: str) -> str:
    """Generate a stable unique ID from hash of text."""
    hash_id = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{hash_id}"


def auto_tag_chunk(text: str) -> list:
    tags = []
    lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            tags.append(topic)
    return tags or ["Other"]


def num_tokens(text: str, model: str = "text-embedding-3-small") -> int:
    """Estimate the number of tokens in a string for the given model."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def split_chunk_by_tokens(text: str, max_tokens: int = MAX_TOKENS, model: str = "text-embedding-3-small") -> list:
    """Split a chunk into smaller chunks if it exceeds max_tokens."""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return [text]
    # Split tokens into segments
    sub_chunks = []
    for i in range(0, len(tokens), max_tokens):
        sub = tokens[i:i+max_tokens]
        sub_chunks.append(enc.decode(sub))
    return sub_chunks


def get_topic_from_keywords(text: str) -> str:
    """
    Infer the most relevant topic from the text using TOPIC_KEYWORDS.
    Returns the first matching topic, or 'Other' if none found.
    """
    lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return topic
    return "Other"


# -------------------------
# Main Processing
# -------------------------
def process_file(filepath: Path) -> List[Dict]:
    """Convert a text file into JSONL chunks with metadata."""
    logger.info(f"Processing file: {filepath}")
    text = read_text_file(filepath)
    filename = filepath.stem
    loadtime = datetime.datetime.now(datetime.UTC).isoformat()
    reference_urls = extract_urls(text)
    chunks = chunk_text_by_paragraphs(text)
    results = []

    for i, chunk in enumerate(chunks):
        # Split chunk if too large
        sub_chunks = split_chunk_by_tokens(chunk, MAX_TOKENS)
        for j, sub_chunk in enumerate(sub_chunks):
            chunk_id = generate_id(sub_chunk, filename + f"_{i}_{j}")
            chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
            chunk_topics = auto_tag_chunk(sub_chunk)
            # Get the primary topic for this chunk using keywords
            topic = get_topic_from_keywords(sub_chunk)
            results.append(
                {
                    "id": chunk_id,
                    "uuid": chunk_uuid,
                    "topics": chunk_topics,
                    "topic": topic,  # <-- primary topic inferred here
                    "source": filename,
                    "chunk_index": f"{i}_{j}" if len(sub_chunks) > 1 else i,
                    "text": sub_chunk,
                    "reference_urls": reference_urls,
                    "loadtime": loadtime,
                }
            )
    logger.info(f"Processed {len(results)} chunks from {filepath.name}")
    return results


def main():
    all_chunks = []
    processed_dir = Path(PROCESSED_DATA_DIR)  # Convert to Path object
    files = list(processed_dir.glob("*.txt"))
    if not files:
        logger.warning(f"No .txt files found in {processed_dir}")
    for filepath in files:
        logger.info(f"Processing {filepath.name}...")
        try:
            file_chunks = process_file(filepath)
            all_chunks.extend(file_chunks)
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")

    try:
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            for entry in all_chunks:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.success(f"Saved {len(all_chunks)} chunks to {CHUNKS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save chunks to {CHUNKS_FILE}: {e}")

    print(f"✅ Saved {len(all_chunks)} chunks to {CHUNKS_FILE}")


if __name__ == "__main__":
    main()