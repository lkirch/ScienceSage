"""
Evaluate RAG retrieval and answer quality using the golden dataset.
Assumes your RAG API is running at http://localhost:8000/rag.
"""

import json
import requests
from pathlib import Path
from tqdm import tqdm

GOLDEN_DATASET = Path("data/eval/golden_dataset.jsonl")
API_URL = "http://localhost:8000/rag"
RESULTS_FILE = Path("data/eval/eval_results.jsonl")

def load_golden_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def evaluate_retrieval(golden_examples, top_k=5):
    results = []
    for example in tqdm(golden_examples, desc="Evaluating"):
        query = example.get("query") or example.get("question")
        expected_sources = set(example.get("expected_sources", []))
        expected_answer = example.get("expected_answer", "").lower()
        payload = {"query": query, "top_k": top_k}
        try:
            resp = requests.post(API_URL, json=payload, timeout=60)
            if resp.status_code != 200:
                result = {"query": query, "error": f"API {resp.status_code}"}
            else:
                data = resp.json()
                retrieved_sources = set([src for src in data.get("sources", [])])
                answer = data.get("answer", "").lower()
                # Simple retrieval recall: did we get any expected source?
                recall = int(bool(expected_sources & retrieved_sources)) if expected_sources else None
                # Simple answer match: does the answer contain the expected answer?
                answer_match = int(expected_answer in answer) if expected_answer else None
                result = {
                    "query": query,
                    "expected_sources": list(expected_sources),
                    "retrieved_sources": list(retrieved_sources),
                    "recall": recall,
                    "expected_answer": expected_answer,
                    "answer": answer,
                    "answer_match": answer_match,
                }
        except Exception as e:
            result = {"query": query, "error": str(e)}
        results.append(result)
        with open(RESULTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")
    return results

def summarize_results(results):
    recall_scores = [r["recall"] for r in results if r.get("recall") is not None]
    answer_scores = [r["answer_match"] for r in results if r.get("answer_match") is not None]
    print(f"Total evaluated: {len(results)}")
    if recall_scores:
        print(f"Retrieval Recall@k: {sum(recall_scores)}/{len(recall_scores)} = {sum(recall_scores)/len(recall_scores):.2f}")
    if answer_scores:
        print(f"Answer Match: {sum(answer_scores)}/{len(answer_scores)} = {sum(answer_scores)/len(answer_scores):.2f}")

def main():
    if not GOLDEN_DATASET.exists():
        print(f"Golden dataset not found at {GOLDEN_DATASET}")
        return
    golden_examples = load_golden_dataset(GOLDEN_DATASET)
    print(f"Loaded {len(golden_examples)} golden examples.")
    results = evaluate_retrieval(golden_examples, top_k=5)
    summarize_results(results)
    print(f"Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()