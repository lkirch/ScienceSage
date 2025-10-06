# 📥 ScienceSage Collection Point Data

This document describes the process and structure of data at the collection point where embeddings are generated for each text chunk in ScienceSage.

---

## 🔄 Collection Point Overview

After chunking and before storing embeddings, each chunk is passed through an embedding model (e.g., OpenAI embeddings). The collection point is where the system gathers the chunk data and the resulting embedding vector for storage and later retrieval.

---

## 📝 Example Collection Point Record

```json
{
  "chunk_id": "90a4913a-d951-5c8d-ac1b-ca7ff747285b",
  "text": "Discovery and exploration of the Solar System is observation, visitation, and increase in knowledge and understanding of Earth's \"cosmic neighborhood\". This includes the Sun, Earth and the Moon, the major planets Mercury, Venus, Mars, Jupiter, Saturn, Uranus, and Neptune, their satellites, as well as smaller bodies including comets, asteroids, and dust.",
  "title": "Discovery and exploration of the Solar System",
  "chunk_index": 0
}
```

- **chunk_id**: Unique identifier for the chunk.
- **text**: The actual text content of the chunk.
- **title**: Title of the source article.
- **chunk_index**: Position of the chunk within the article.

---

## 🛠️ Example Collection Code

```python
# Example: Collecting data for embedding
collection_records = []
for chunk in chunks:
    collection_records.append({
        "chunk_id": chunk["chunk_id"],
        "text": chunk["text"],
        "title": chunk["title"],
        "chunk_index": chunk["chunk_index"]
    })
# This data is then passed to the embedding function/model.
```

---

## 📂 Related Files

- [embedding_data.md](embedding_data.md) — Structure and storage of embedding vectors
- [chunks.md](chunks.md) — Structure of text chunks

---