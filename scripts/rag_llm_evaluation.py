import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sciencesage"))
from sciencesage.config import GROUND_TRUTH_FILE, EVAL_RESULTS_FILE, TOP_K, METRICS_SUMMARY_FILE, LLM_EVAL_FILE


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def precision_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)
    return len([chunk for chunk in retrieved_k if chunk in relevant_set]) / k

def recall_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)
    return len([chunk for chunk in retrieved_k if chunk in relevant_set]) / len(relevant_set) if relevant_set else 0.0

def reciprocal_rank(retrieved, relevant):
    for idx, chunk in enumerate(retrieved, 1):
        if chunk in relevant:
            return 1.0 / idx
    return 0.0

def dcg(retrieved, relevant, k):
    dcg_val = 0.0
    for i, chunk in enumerate(retrieved[:k]):
        rel = 1 if chunk in relevant else 0
        dcg_val += rel / np.log2(i + 2)
    return dcg_val

def ndcg_at_k(retrieved, relevant, k):
    ideal_rels = [1] * min(len(relevant), k)
    ideal_dcg = sum([rel / np.log2(i + 2) for i, rel in enumerate(ideal_rels)])
    if ideal_dcg == 0:
        return 0.0
    return dcg(retrieved, relevant, k) / ideal_dcg

def contextual_recall_and_sufficiency(retrieved, relevant, k):
    # Placeholder: in practice, this may require human or LLM judgment
    return recall_at_k(retrieved, relevant, k)


def evaluate_entry(entry):
    """
    Evaluate a single entry using LLM logic.
    Returns a dict with expected fields.
    """
    # Dummy implementation for testing
    return {
        "query": entry.get("query"),
        "expected_answer": entry.get("expected_answer"),
        "retrieved_answer": entry.get("retrieved_answer"),
        "llm_score": 1.0,  # Replace with actual LLM scoring logic
        "context_ids": entry.get("context_ids"),
        "metadata": entry.get("metadata"),
    }

def save_jsonl(records, path):
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

def main():
    # All paths are relative to the project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    ground_truth_path = os.path.join(project_root, GROUND_TRUTH_FILE)
    results_path = os.path.join(project_root, EVAL_RESULTS_FILE)
    metrics_path = os.path.join(project_root, METRICS_SUMMARY_FILE)
    llm_eval_path = os.path.join(project_root, LLM_EVAL_FILE)

    ground_truth = load_jsonl(ground_truth_path)
    results = load_jsonl(results_path)

    # --- Existing metrics code ---
    metrics = []
    for g, r in zip(golden, results):
        retrieved = r.get("retrieved_chunks", [])
        relevant = [int(cid) for cid in g.get("context_ids", [])]
        metrics.append({
            "query": g.get("query", ""),
            f"precision@{TOP_K}": precision_at_k(retrieved, relevant, TOP_K),
            f"recall@{TOP_K}": recall_at_k(retrieved, relevant, TOP_K),
            "MRR": reciprocal_rank(retrieved, relevant),
            "nDCG": ndcg_at_k(retrieved, relevant, TOP_K),
            "contextual_recall_sufficiency": contextual_recall_and_sufficiency(retrieved, relevant, TOP_K)
        })

    metrics_df = pd.DataFrame(metrics)
    print("Average Metrics:")
    print(metrics_df.mean(numeric_only=True))
    metrics_df.to_csv(metrics_path, index=False)
    print(f"Saved metrics summary to {metrics_path}")

    # --- NEW: LLM evaluation and save ---
    llm_eval_results = []
    for r in results:
        llm_eval_results.append(evaluate_entry(r))
    save_jsonl(llm_eval_results, llm_eval_path)
    print(f"Saved LLM eval results to {llm_eval_path}")

if __name__ == "__main__":
    main()