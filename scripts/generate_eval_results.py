import os
import sys
import json
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sciencesage.config import (
    GROUND_TRUTH_FILE,
    EVAL_RESULTS_FILE,
    TOP_K,
)
from sciencesage.retrieval_system import retrieve_context
from sciencesage.metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)

def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(records, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

def generate_eval_for_entry(entry):
    query = entry.get("question")
    expected_answer = entry.get("answer")
    topic = entry.get("topic", None)
    level = entry.get("level", None)
    relevant_ids = [entry["chunk_id"]] if "chunk_id" in entry else []

    # Retrieve top-k context chunks
    context_chunks = retrieve_context(query, top_k=TOP_K, topic=topic)
    context_ids = [chunk.get("chunk_id") for chunk in context_chunks]
    retrieved_context = [chunk.get("text") for chunk in context_chunks]

    # Compute retrieval metrics
    p_at_k = precision_at_k(context_ids, relevant_ids, TOP_K)
    r_at_k = recall_at_k(context_ids, relevant_ids, TOP_K)
    rr = reciprocal_rank(context_ids, relevant_ids)
    ndcg = ndcg_at_k(context_ids, relevant_ids, TOP_K)

    return {
        "query": query,
        "expected_answer": expected_answer,
        "context_ids": context_ids,
        "retrieved_context": retrieved_context,
        "relevant_context_ids": relevant_ids,
        "precision_at_k": p_at_k,
        "recall_at_k": r_at_k,
        "reciprocal_rank": rr,
        "ndcg_at_k": ndcg,
        "topic": topic,
        "level": level,
        "metadata": {
            "source_text": entry.get("text"),
            "chunk_id": entry.get("chunk_id"),
        },
    }

def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    ground_truth_path = os.path.join(project_root, GROUND_TRUTH_FILE)
    eval_results_path = os.path.join(project_root, EVAL_RESULTS_FILE)

    ground_truth = load_jsonl(ground_truth_path)
    eval_results = []

    for entry in tqdm(ground_truth, desc="Evaluating retrieval"):
        eval_result = generate_eval_for_entry(entry)
        eval_results.append(eval_result)

    save_jsonl(eval_results, eval_results_path)
    print(f"Saved retrieval evaluation results to {eval_results_path}")

if __name__ == "__main__":
    main()