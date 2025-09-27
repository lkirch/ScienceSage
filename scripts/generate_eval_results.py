import os
import sys
import json
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sciencesage"))
from sciencesage.config import GROUND_TRUTH_FILE, EVAL_RESULTS_FILE, TOP_K

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

def generate_eval_for_entry(entry):
    """
    Generate evaluation results for a single entry.
    Returns a dict with expected fields.
    """
    # Dummy implementation for testing
    return {
        "query": entry.get("query"),
        "expected_answer": entry.get("expected_answer"),
        "retrieved_answer": "A planet.",  # Replace with actual retrieval logic
        "score": 1.0,  # Replace with actual scoring logic
        "context_ids": entry.get("context_ids"),
        "metadata": entry.get("metadata"),
    }

def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    ground_truth_path = os.path.join(project_root, GROUND_TRUTH_FILE)
    eval_results_path = os.path.join(project_root, EVAL_RESULTS_FILE)

    ground_truth = load_jsonl(ground_truth_path)
    eval_results = []

    for entry in tqdm(ground_truth, desc="Generating eval results"):
        eval_result = generate_eval_for_entry(entry)
        eval_results.append(eval_result)

    save_jsonl(eval_results, eval_results_path)
    print(f"Saved eval results to {eval_results_path}")

if __name__ == "__main__":
    main()