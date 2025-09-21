from pathlib import Path
import json
import hashlib
import uuid
import datetime
import time
from loguru import logger
from tqdm import tqdm

from sciencesage.config import (
    RAW_DATA_DIR,
    CHUNKS_FILE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    STANDARD_CHUNK_FIELDS,
)

logger.add("logs/preprocess.log", rotation="5 MB", retention="7 days")
logger.info("Started preprocess.py script.")

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

def make_standard_chunk(text, meta, chunk_index, char_start, char_end):
    chunk_id = hashlib.md5((meta["title"] + text).encode("utf-8")).hexdigest()[:12]
    chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
    chunk = {
        "id": chunk_id,
        "uuid": chunk_uuid,
        "text": text,
        "title": meta.get("title"),
        "source_url": meta.get("fullurl"),
        "categories": meta.get("categories", []),
        "images": meta.get("images", []),
        "summary": meta.get("summary"),
        "chunk_index": chunk_index,
        "char_start": char_start,
        "char_end": char_end,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    # Only keep fields in STANDARD_CHUNK_FIELDS
    return {k: chunk.get(k) for k in STANDARD_CHUNK_FIELDS if k in chunk}

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
        chunks = chunk_text(text)
        char_offset = 0
        for i, chunk in enumerate(chunks):
            char_start = char_offset
            char_end = char_offset + len(chunk)
            char_offset = char_end
            chunk_dict = make_standard_chunk(chunk, meta, i, char_start, char_end)
            all_chunks.append(chunk_dict)
        logger.info(f"Processed {len(chunks)} chunks from {txt_path.name}")

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        for entry in all_chunks:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    elapsed = time.time() - start_time
    logger.success(f"Saved {len(all_chunks)} chunks to {CHUNKS_FILE}")
    logger.info(f"Total elapsed time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()