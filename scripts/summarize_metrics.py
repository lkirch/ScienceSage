import os
import sys
import json
import csv
from statistics import mean, stdev

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sciencesage.config import (
    EVAL_RESULTS_FILE,
    LLM_EVAL_FILE,
    METRICS_SUMMARY_FILE,
)

def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f if line.strip()]

def summarize_metrics(records, metric_keys):
    summary = {}
    for key in metric_keys:
        values = [rec.get(key) for rec in records if rec.get(key) is not None]
        if values:
            summary[key + "_mean"] = mean(values)
            summary[key + "_stdev"] = stdev(values) if len(values) > 1 else 0.0
            summary[key + "_min"] = min(values)
            summary[key + "_max"] = max(values)
        else:
            summary[key + "_mean"] = summary[key + "_stdev"] = summary[key + "_min"] = summary[key + "_max"] = None
    summary["count"] = len(records)
    return summary

def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    eval_results_path = os.path.join(project_root, EVAL_RESULTS_FILE)
    llm_eval_path = os.path.join(project_root, LLM_EVAL_FILE)
    metrics_summary_path = os.path.join(project_root, METRICS_SUMMARY_FILE)

    # Load records
    eval_records = load_jsonl(eval_results_path) if os.path.exists(eval_results_path) else []
    llm_records = load_jsonl(llm_eval_path) if os.path.exists(llm_eval_path) else []

    # Define metric keys to summarize
    retrieval_metric_keys = ["precision_at_k", "recall_at_k", "reciprocal_rank", "ndcg_at_k"]
    llm_metric_keys = ["exact_match"]

    # Summarize
    retrieval_summary = summarize_metrics(eval_records, retrieval_metric_keys)
    llm_summary = summarize_metrics(llm_records, retrieval_metric_keys + llm_metric_keys)

    # Write summary CSV
    os.makedirs(os.path.dirname(metrics_summary_path), exist_ok=True)
    with open(metrics_summary_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["metric", "value"])
        for key, value in retrieval_summary.items():
            writer.writerow([f"retrieval_{key}", value])
        for key, value in llm_summary.items():
            writer.writerow([f"llm_{key}", value])

    print(f"Metrics summary written to {metrics_summary_path}")

if __name__ == "__main__":
    main()