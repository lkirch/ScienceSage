# 🧬 ScienceSage Embedding Data

This document describes the structure and storage of embedding data used in ScienceSage. Embeddings are vector representations of text chunks, enabling efficient similarity search and retrieval.

---

## 📦 Storage Format

Embeddings are stored in a columnar format (Parquet) for efficient access and compatibility with vector databases like Qdrant.

- **File location:**  
  `data/processed/chunks_embeddings.parquet`

---

## 📄 Example Embedding Record

Below is an example row from the Parquet file:

```json
{
  "chunk_id": "90a4913a-d951-5c8d-ac1b-ca7ff747285b",
  "embedding": [
    0.0123, -0.0456, 0.0789, ..., 0.0345
  ],
  "title": "Discovery and exploration of the Solar System",
  "chunk_index": 0
}
```

- **chunk_id**: Unique identifier for the text chunk (matches the chunk in `chunks.jsonl`).
- **embedding**: List of floating-point numbers (vector) representing the chunk.
- **title**: Title of the source article.
- **chunk_index**: Position of the chunk within the article.

---

## 🧠 About Embeddings

Embeddings are high-dimensional vectors generated from text using a machine learning model (e.g., OpenAI embeddings). They capture the semantic meaning of the text, allowing the system to retrieve relevant passages based on similarity to a user’s query.

---

## 📂 Related Files

- [chunks.md](chunks.md) — Structure of text chunks
- [meta_data.md](meta_data.md) — Metadata for articles and chunks

---