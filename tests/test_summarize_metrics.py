import os
import csv
import json

from scripts import summarize_metrics

def test_summarize_metrics_basic():
    # Prepare dummy records
    records = [
        {"precision_at_k": 0.8, "recall_at_k": 0.7, "reciprocal_rank": 1.0, "ndcg_at_k": 0.9},
        {"precision_at_k": 0.6, "recall_at_k": 0.5, "reciprocal_rank": 0.5, "ndcg_at_k": 0.7},
    ]
    metric_keys = ["precision_at_k", "recall_at_k", "reciprocal_rank", "ndcg_at_k"]
    summary = summarize_metrics.summarize_metrics(records, metric_keys)
    assert summary["precision_at_k_mean"] == 0.7
    assert summary["recall_at_k_min"] == 0.5
    assert summary["reciprocal_rank_max"] == 1.0
    assert summary["ndcg_at_k_stdev"] > 0

def test_main_creates_csv(tmp_path, monkeypatch):
    # Create dummy eval and llm eval files
    eval_records = [
        {"precision_at_k": 0.8, "recall_at_k": 0.7, "reciprocal_rank": 1.0, "ndcg_at_k": 0.9}
    ]
    llm_records = [
        {"precision_at_k": 0.6, "recall_at_k": 0.5, "reciprocal_rank": 0.5, "ndcg_at_k": 0.7, "exact_match": 1.0}
    ]
    eval_path = tmp_path / "eval_results.jsonl"
    llm_path = tmp_path / "llm_eval.jsonl"
    summary_path = tmp_path / "metrics_summary.csv"

    for rec, path in [(eval_records, eval_path), (llm_records, llm_path)]:
        with open(path, "w") as f:
            for r in rec:
                f.write(json.dumps(r) + "\n")

    # Patch config paths
    monkeypatch.setattr(summarize_metrics, "EVAL_RESULTS_FILE", str(eval_path))
    monkeypatch.setattr(summarize_metrics, "LLM_EVAL_FILE", str(llm_path))
    monkeypatch.setattr(summarize_metrics, "METRICS_SUMMARY_FILE", str(summary_path))

    # Patch __file__ to simulate script location
    monkeypatch.setattr(summarize_metrics, "__file__", str(tmp_path / "summarize_metrics.py"))

    summarize_metrics.main()

    # Check that the CSV was created and contains expected metrics
    assert summary_path.exists()
    with open(summary_path) as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert any("retrieval_precision_at_k_mean" in row for row in rows)
        assert any("llm_exact_match_mean" in row for row in rows)