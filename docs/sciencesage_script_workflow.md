# ScienceSage Script Workflow

This table summarizes the main scripts in the ScienceSage project, their purposes, inputs, outputs, and required dependencies.

| Order | Script Name                    | Purpose / Description                                                        | Inputs                                      | Outputs                                   | Keys/Apps Required                  |
|-------|------------------------------- |------------------------------------------------------------------------------|---------------------------------------------|-------------------------------------------|-------------------------------------|
| 1     | `download_data.py`             | Download raw Wikipedia data for your topics.                                 | None (topics hardcoded or via config)       | `data/raw/*.html`, `.txt`, `.meta.json`   | None                                |
| 2     | `preprocess.py`                | Clean and chunk the raw data into JSONL format.                              | `data/raw/*.txt`                            | `chunks.jsonl`                            | None                                |
| 3     | `embed.py`                     | Embed the chunks and upload them to Qdrant vector DB.                        | `chunks.jsonl`                              | `embeddings.parquet`                      | Qdrant running, OpenAI API key      |
| 4     | `ck_example_queries.py`        | Checks retrieval for all example queries and logs the results (sanity check).| Qdrant DB, config/example queries           | `logs/ck_example_queries.log`             | Qdrant running, OpenAI API key      |
| 5     | `create_ground_truth_dataset.py`| Helps create a golden dataset for evaluation (manual/interactive step).      | None or user input                          | `ground_truth_dataset.jsonl`               | None                                |
| 6     | `validate_ground_truth_dataset.py`| Validates the format and content of the ground truth dataset.                | `ground_truth_dataset.jsonl`                | Validation report (stdout/log)             | None                                |
| 7     | `rag_llm_evaluation.py`        | Runs retrieval and LLM answer evaluation using the golden dataset.           | `ground_truth_dataset.jsonl`, Qdrant, LLM   | `eval_results.jsonl`, `llm_eval.jsonl`     | Qdrant running, OpenAI API key      |
| 8     | `generate_eval_results.py`     | Generates and saves evaluation results (metrics, logs, etc.).                | `eval_results.jsonl`, `llm_eval.jsonl`      | Summary files (various, e.g., metrics)     | None                                |
| 9     | `summarize_metrics.py`         | Summarizes evaluation metrics for reporting.                                 | `eval_results.jsonl`, `llm_eval.jsonl`      | Printed or saved summary (stdout/file)     | None                                |

---

## Legend for "Keys/Apps Required"

- **Qdrant running:** Qdrant vector DB must be running (usually via Docker).
- **OpenAI API key:** Must be set in your environment (for embedding/LLM calls).