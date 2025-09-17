"""
Grid search for best chunk size and overlap.
Evaluates retrieval quality using a golden dataset and logs results.
"""

import os
import json
import shutil
from pathlib import Path
from subprocess import run
from sciencesage.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHUNKS_FILE,
    RAW_HTML_DIR,
    RAW_PDF_DIR,
    RAW_DATA_DIR,
)
from loguru import logger

GOLDEN_DATASET = Path("data/eval/golden_dataset.jsonl")
RESULTS_FILE = Path("data/eval/chunk_grid_search_results.jsonl")
CHUNK_SIZES = [512, 750, 1000, 1500, 2000]
CHUNK_OVERLAPS = [0, 50, 100, 200, 300]

def run_preprocess(chunk_size, chunk_overlap):
    # Patch config.py with new chunk size/overlap
    config_path = Path("sciencesage/config.py")
    with open(config_path, "r") as f:
        lines = f.readlines()
    with open(config_path, "w") as f:
        for line in lines:
            if line.strip().startswith("CHUNK_SIZE"):
                f.write(f"CHUNK_SIZE = {chunk_size}\n")
            elif line.strip().startswith("CHUNK_OVERLAP"):
                f.write(f"CHUNK_OVERLAP = {chunk_overlap}\n")
            else:
                f.write(line)
    # Remove old chunks file
    if Path(CHUNKS_FILE).exists():
        os.remove(CHUNKS_FILE)
    # Run preprocess
    logger.info(f"Running preprocess.py with CHUNK_SIZE={chunk_size}, CHUNK_OVERLAP={chunk_overlap}")
    result = run(["python3", "scripts/preprocess.py"])
    return result.returncode == 0

def run_embed():
    # Remove old embeddings file if exists
    embeddings_file = Path("data/embeddings/embeddings.jsonl")
    if embeddings_file.exists():
        os.remove(embeddings_file)
    logger.info("Running embed.py")
    result = run(["python3", "scripts/embed.py", "--append"])
    return result.returncode == 0

def evaluate_retrieval():
    """
    Dummy evaluation: counts number of chunks and average chunk length.
    Replace with your own retrieval evaluation using the golden dataset.
    """
    if not Path(CHUNKS_FILE).exists():
        return {"num_chunks": 0, "avg_chunk_len": 0}
    with open(CHUNKS_FILE, "r") as f:
        chunks = [json.loads(line) for line in f]
    if not chunks:
        return {"num_chunks": 0, "avg_chunk_len": 0}
    avg_len = sum(len(c["text"]) for c in chunks) / len(chunks)
    return {"num_chunks": len(chunks), "avg_chunk_len": avg_len}

def main():
    logger.add("logs/chunk_grid_search.log", rotation="5 MB", retention="7 days")
    results = []
    for chunk_size in CHUNK_SIZES:
        for chunk_overlap in CHUNK_OVERLAPS:
            logger.info(f"Testing CHUNK_SIZE={chunk_size}, CHUNK_OVERLAP={chunk_overlap}")
            ok = run_preprocess(chunk_size, chunk_overlap)
            if not ok:
                logger.error("Preprocess failed, skipping.")
                continue
            ok = run_embed()
            if not ok:
                logger.error("Embed failed, skipping.")
                continue
            metrics = evaluate_retrieval()
            result = {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                **metrics
            }
            logger.info(f"Result: {result}")
            results.append(result)
            with open(RESULTS_FILE, "a") as f:
                f.write(json.dumps(result) + "\n")
    logger.success("Grid search complete. Results saved to %s", RESULTS_FILE)

if __name__ == "__main__":
    main()