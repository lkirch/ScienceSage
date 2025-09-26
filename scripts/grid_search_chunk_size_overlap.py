import os
import sys
import json
import shutil
import subprocess
from itertools import product
from tqdm import tqdm

# Paths and config
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CHUNK_CONFIG_FILE = os.path.join(PROJECT_ROOT, "sciencesage", "config_chunking.json")
METRICS_SUMMARY_FILE = os.path.join(PROJECT_ROOT, "data", "eval", "metrics_summary.csv")

# Define your grid based on using text-embedding-3-small
# (max 8191 tokens per chunk, but we want to stay well below that)
CHUNK_SIZES = [256, 384, 512, 768]
OVERLAPS = [0, 64, 128, 192]

# Helper to update chunking config
def update_chunking_config(chunk_size, overlap):
    config = {"chunk_size": chunk_size, "chunk_overlap": overlap}
    with open(CHUNK_CONFIG_FILE, "w") as f:
        json.dump(config, f)

# Helper to run a script and check for errors
def run_script(script_name):
    result = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, "scripts", script_name)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error running {script_name}:\n{result.stderr}")
        sys.exit(1)

# Main grid search loop
results = []
for chunk_size, overlap in tqdm(list(product(CHUNK_SIZES, OVERLAPS)), desc="Grid Search"):
    print(f"\n=== Chunk size: {chunk_size}, Overlap: {overlap} ===")
    # 1. Update chunking config
    update_chunking_config(chunk_size, overlap)

    # 2. Re-chunk, embed, and index (assume embed.py reads config_chunking.json)
    run_script("embed.py")

    # 3. Generate eval results
    run_script("generate_eval_results.py")

    # 4. Evaluate metrics
    run_script("rag_llm_evaluation.py")

    # 5. Read metrics summary
    if not os.path.exists(METRICS_SUMMARY_FILE):
        print("Metrics summary file not found!")
        continue
    with open(METRICS_SUMMARY_FILE) as f:
        lines = f.readlines()
        if len(lines) < 2:
            print("Metrics summary file is empty!")
            continue
        header = lines[0].strip().split(",")
        values = lines[1].strip().split(",")
        metrics = dict(zip(header, values))
        metrics["chunk_size"] = chunk_size
        metrics["overlap"] = overlap
        results.append(metrics)

# Save grid search results
grid_results_file = os.path.join(DATA_DIR, "eval", "grid_search_results.csv")
with open(grid_results_file, "w") as f:
    if results:
        header = list(results[0].keys())
        f.write(",".join(header) + "\n")
        for row in results:
            f.write(",".join(str(row[h]) for h in header) + "\n")

print(f"\nGrid search complete. Results saved to {grid_results_file}")