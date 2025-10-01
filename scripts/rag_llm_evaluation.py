import os
import sys
import json
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sciencesage.config import (
    GROUND_TRUTH_FILE,
    LLM_EVAL_FILE,
    TOP_K,
)
from sciencesage.retrieval_system import retrieve_context, generate_answer
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

def simple_exact_match(pred, gold):
    if not pred or not gold:
        return 0.0
    return float(pred.strip().lower() == gold.strip().lower())

def generate_llm_eval_for_entry(entry):
    query = entry.get("question")
    expected_answer = entry.get("answer")
    topic = entry.get("topic", None)
    level = entry.get("level", "College")
    relevant_ids = [entry["chunk_id"]] if "chunk_id" in entry else []

    # Ensure query is not None or empty
    if not query or not isinstance(query, str):
        raise ValueError(f"Invalid query in entry: {entry}")

    # Retrieve top-k context chunks
    context_chunks = retrieve_context(query, top_k=TOP_K, topic=topic)
    context_ids = [chunk.get("chunk_id") for chunk in context_chunks]
    retrieved_context = [chunk.get("text") for chunk in context_chunks]

    # Generate answer using the LLM
    llm_answer = generate_answer(query, context_chunks, level, topic)

    # Simple exact match metric (replace with F1, ROUGE, etc. as needed)
    exact_match = simple_exact_match(llm_answer, expected_answer)

    # Retrieval metrics for transparency
    p_at_k = precision_at_k(context_ids, relevant_ids, TOP_K)
    r_at_k = recall_at_k(context_ids, relevant_ids, TOP_K)
    rr = reciprocal_rank(context_ids, relevant_ids)
    ndcg = ndcg_at_k(context_ids, relevant_ids, TOP_K)

    return {
        "query": query,
        "expected_answer": expected_answer,
        "retrieved_answer": llm_answer,
        "exact_match": exact_match,
        "context_ids": context_ids,
        "retrieved_context": retrieved_context,
        "relevant_context_ids": relevant_ids,
        "precision_at_k": p_at_k,
        "recall_at_k": r_at_k,
        "reciprocal_rank": rr,
        "ndcg_at_k": ndcg,
        "topic": topic,
        "level": level,
        "metadata": entry.get("metadata"),
    }

def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    ground_truth_path = os.path.join(project_root, GROUND_TRUTH_FILE)
    llm_eval_path = os.path.join(project_root, LLM_EVAL_FILE)

    ground_truth = load_jsonl(ground_truth_path)
    llm_eval_results = []

    for entry in tqdm(ground_truth, desc="Evaluating RAG LLM"):
        eval_result = generate_llm_eval_for_entry(entry)
        llm_eval_results.append(eval_result)

    save_jsonl(llm_eval_results, llm_eval_path)
    print(f"Saved RAG LLM evaluation results to {llm_eval_path}")

if __name__ == "__main__":
    main()