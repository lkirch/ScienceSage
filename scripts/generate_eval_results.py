import os
import sys
import json
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sciencesage"))
from sciencesage.config import GOLDEN_DATA_FILE, EVAL_RESULTS_FILE, TOP_K

from sciencesage.retrieval_system import embed_text
from qdrant_client import QdrantClient
from sciencesage.config import QDRANT_URL, QDRANT_COLLECTION

qdrant = QdrantClient(url=QDRANT_URL)

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(records, path):
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

def retrieve_top_k_chunks(query, k):
    # Embed the query
    vector = embed_text(query)
    # Query Qdrant for top-k chunks (no topic filter)
    results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=k,
    )
    # Return chunk IDs or indexes of the top-k results
    return [
        point.payload.get("chunk_index", point.id)
        for point in results.points
    ]

def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    golden_path = os.path.join(project_root, GOLDEN_DATA_FILE)
    eval_results_path = os.path.join(project_root, EVAL_RESULTS_FILE)

    golden = load_jsonl(golden_path)
    eval_results = []

    for entry in tqdm(golden, desc="Generating eval results"):
        query = entry.get("query", "")
        retrieved_chunks = retrieve_top_k_chunks(query, TOP_K)
        eval_results.append({
            "query": query,
            "retrieved_chunks": retrieved_chunks
        })

    save_jsonl(eval_results, eval_results_path)
    print(f"Saved eval results to {eval_results_path}")

if __name__ == "__main__":
    main()