# 🎯 ScienceSage Ground Truth Data

The ground truth data in ScienceSage provides reference questions, answers, and the specific Wikipedia text chunks that contain the answer for each evaluation item. This data is essential for objectively measuring retrieval and answer quality.

---

## 📦 Structure

Each ground truth record in `ground_truth_dataset.jsonl` includes:

- **chunk_id**: Unique identifier for the relevant text chunk.
- **topic**: High-level topic label (e.g., "mars", "moon", "other").
- **text**: The full text of the chunk containing the answer.
- **level**: Intended answer complexity or audience (e.g., "Middle School", "College", "Advanced").
- **question**: The evaluation question.
- **answer**: The correct or reference answer for the question.
- **ground_truth_chunks**: List of chunk IDs (usually one) that contain the answer.

---

## 📄 Example Ground Truth Record

```json
{
  "chunk_id": "451501cf-51c2-5954-abab-35ff573a201d",
  "topic": "other",
  "text": "Pioneer Venus\nIn 1978, NASA sent two Pioneer spacecraft to Venus. The Pioneer mission consisted of two components, launched separately: an orbiter and a multiprobe. The Pioneer Venus Multiprobe carried one large and three small atmospheric probes. The large probe was released on November 16, 1978, and the three small probes on November 20. All four probes entered the Venusian atmosphere on December 9, followed by the delivery vehicle. Although not expected to survive the descent through the atmosphere, one probe continued to operate for 45 minutes after reaching the surface. The Pioneer Venus Orbiter was inserted into an elliptical orbit around Venus on December 4, 1978. It carried 17 experiments and operated until the fuel used to maintain its orbit was exhausted and atmospheric entry destroyed the spacecraft in August 1992.",
  "level": "Middle School",
  "question": "What year did NASA send the Pioneer spacecraft to Venus?",
  "answer": "1978",
  "ground_truth_chunks": ["451501cf-51c2-5954-abab-35ff573a201d"]
}
```

---

## 🧩 Usage

- **Retrieval Evaluation:**  
  Used to calculate metrics like Recall@K, Precision@K, MRR, and nDCG@K by comparing retrieved chunks to ground truth chunks.
- **LLM Answer Evaluation:**  
  Used to compare generated answers to the reference answer for accuracy and completeness.

---

## 📂 Location

Ground truth data is stored in  
`data/ground_truth/ground_truth_dataset.jsonl`  
with one JSON object per line.