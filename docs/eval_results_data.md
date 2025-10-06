# 🧪 ScienceSage Evaluation Results

This document describes the structure of evaluation results generated during retrieval and answer quality assessment in ScienceSage. Evaluation results are stored in `data/eval/eval_results.jsonl`, with one JSON object per line.

---

## 📄 Example Evaluation Record

```json
{
  "query": "What year did NASA send the Pioneer spacecraft to Venus?",
  "expected_answer": "1978",
  "retrieved_chunks": [
    "5c2ed7e7-af71-5401-8ae1-59b0b1af0b9a",
    "f85242a8-b3d5-50d9-a3ad-4ca26ff918cf",
    "... (more chunk IDs) ..."
  ],
  "retrieved_context": [
    "Pioneer Venus\nIn 1978, NASA sent two Pioneer spacecraft to Venus. The Pioneer mission consisted of two components, launched separately: an orbiter and a multiprobe. ...",
    "... (more context passages) ..."
  ],
  "ground_truth_chunks": [
    "451501cf-51c2-5954-abab-35ff573a201d"
  ],
  "ground_truth_texts": [
    "Pioneer Venus\nIn 1978, NASA sent two Pioneer spacecraft to Venus. The Pioneer mission consisted of two components, launched separately: an orbiter and a multiprobe. ..."
  ],
  "precision_at_k": 0.1,
  "recall_at_k": 1.0,
  "reciprocal_rank": 1.0,
  "ndcg_at_k": 1.0,
  "topic": "other",
  "level": "Middle School",
  "metadata": {
    "source_text": "Pioneer Venus\nIn 1978, NASA sent two Pioneer spacecraft to Venus. ...",
    "chunk_id": "451501cf-51c2-5954-abab-35ff573a201d"
  }
}
```

---

## 🏷️ Field Descriptions

- **query**: The user or test question being evaluated.
- **expected_answer**: The correct or reference answer for the query.
- **retrieved_chunks**: List of chunk IDs retrieved by the system for this query.
- **retrieved_context**: Text passages corresponding to the retrieved chunks.
- **ground_truth_chunks**: List of chunk IDs considered as ground truth for the query.
- **ground_truth_texts**: Text passages considered as ground truth.
- **precision_at_k**: Precision at top K retrieved chunks.
- **recall_at_k**: Recall at top K retrieved chunks.
- **reciprocal_rank**: Reciprocal rank of the first relevant chunk.
- **ndcg_at_k**: Normalized Discounted Cumulative Gain at K.
- **topic**: High-level topic label (e.g., "mars", "moon", "other").
- **level**: Intended answer complexity or audience (e.g., "Middle School", "College").
- **metadata**: Additional metadata, such as the source text and chunk ID.

---

## 📂 Location

All evaluation records are stored in [data/eval/eval_results.jsonl](../data/eval/eval_results.jsonl), one JSON object per line.

---