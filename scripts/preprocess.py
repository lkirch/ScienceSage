from pathlib import Path
import json
import uuid
import datetime
import time
from loguru import logger
from tqdm import tqdm

from sciencesage.config import (
    RAW_DATA_DIR,
    CHUNKS_FILE,
    CHUNK_FIELDS,
    EXCLUDED_CATEGORY_PREFIXES
)

logger.add("logs/preprocess.log", rotation="5 MB", retention="7 days")
logger.info("Started preprocess.py script.")

def chunk_text_by_paragraphs(text, min_length=100, max_length=1200):
    """
    Split text into paragraphs, merge short ones, and split long ones.
    - min_length: minimum number of characters for a chunk
    - max_length: maximum number of characters for a chunk
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

    # Merge short paragraphs with the next one
    merged = []
    buffer = ""
    for para in paragraphs:
        if len(buffer) == 0:
            buffer = para
        else:
            if len(buffer) < min_length:
                buffer += " " + para
            else:
                merged.append(buffer)
                buffer = para
    if buffer:
        merged.append(buffer)

    # Split long paragraphs
    final_chunks = []
    for para in merged:
        if len(para) > max_length:
            # Split by sentences if possible
            sentences = para.split('. ')
            chunk = ""
            for sentence in sentences:
                if len(chunk) + len(sentence) < max_length:
                    chunk += sentence + '. '
                else:
                    final_chunks.append(chunk.strip())
                    chunk = sentence + '. '
            if chunk.strip():
                final_chunks.append(chunk.strip())
        else:
            final_chunks.append(para)
    # Remove empty chunks
    return [c for c in final_chunks if c.strip()]

def filter_categories(categories):
    return [
        c for c in categories
        if not any(c.startswith(prefix) for prefix in EXCLUDED_CATEGORY_PREFIXES)
    ]

def infer_topic(meta):
    """
    Infer topic from article title and categories.
    """
    title = meta.get("title", "").lower()
    categories = [c.lower() for c in meta.get("categories", [])]

    # Example mappings
    if "mars" in title or any("mars" in c for c in categories):
        return "mars"
    if "moon" in title or any("moon" in c for c in categories):
        return "moon"
    if "space exploration" in title or any("space exploration" in c for c in categories):
        return "space exploration"
    if "animals in space" in title or any("animals in space" in c for c in categories):
        return "animals in space"
    if any("planet" in c for c in categories):
        return "planets"
    # Add more mappings as needed

    return "other"

def make_standard_chunk(text, meta, chunk_index, char_start, char_end):
    chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, meta.get("title", "") + text))
    filtered_categories = filter_categories(meta.get("categories", []))
    chunk = {
        "uuid": chunk_uuid,
        "text": text,
        "title": meta.get("title"),
        "source_url": meta.get("fullurl"),
        "categories": filtered_categories,
        "topic": infer_topic(meta),
        "images": meta.get("images", []),
        "summary": meta.get("summary"),
        "chunk_index": chunk_index,
        "char_start": char_start,
        "char_end": char_end,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    return {k: chunk.get(k) for k in CHUNK_FIELDS if k in chunk}

def main():
    start_time = time.time()
    raw_dir = Path(RAW_DATA_DIR)
    txt_files = list(raw_dir.glob("*.txt"))
    all_chunks = []
    for txt_path in tqdm(txt_files, desc="Preprocessing articles"):
        meta_path = txt_path.with_suffix(".meta.json")
        if not meta_path.exists():
            logger.warning(f"Missing meta.json for {txt_path.name}")
            continue
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        paragraphs = chunk_text_by_paragraphs(text)
        char_offset = 0
        for i, para in enumerate(paragraphs):
            char_start = char_offset
            char_end = char_offset + len(para)
            char_offset = char_end
            chunk_dict = make_standard_chunk(para, meta, i, char_start, char_end)
            all_chunks.append(chunk_dict)
        logger.info(f"Processed {len(paragraphs)} paragraph chunks from {txt_path.name}")

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        for entry in all_chunks:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    elapsed = time.time() - start_time
    logger.success(f"Saved {len(all_chunks)} paragraph chunks to {CHUNKS_FILE}")
    logger.info(f"Total elapsed time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()