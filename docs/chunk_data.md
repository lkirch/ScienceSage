# 📝 ScienceSage Data Chunks

This document describes the structure of individual data records ("chunks") used in ScienceSage, with an example from `data/processed/chunks.jsonl`.

---

## 📄 Example Chunk Record

```json
{
  "chunk_id": "90a4913a-d951-5c8d-ac1b-ca7ff747285b",
  "text": "Discovery and exploration of the Solar System is observation, visitation, and increase in knowledge and understanding of Earth's \"cosmic neighborhood\". This includes the Sun, Earth and the Moon, the major planets Mercury, Venus, Mars, Jupiter, Saturn, Uranus, and Neptune, their satellites, as well as smaller bodies including comets, asteroids, and dust.\nIn ancient and medieval times, only objects visible to the naked eye—the Sun, the Moon, the five classical planets, and comets, along with phenomena now known to take place in Earth's atmosphere, like meteors and aurorae—were known. Ancient astronomers were able to make geometric observations with various instruments. The collection of precise observations in the early modern period and the invention of the telescope helped determine the overall structure of the Solar System.",
  "title": "Discovery and exploration of the Solar System",
  "source_url": "https://en.wikipedia.org/wiki/Discovery_and_exploration_of_the_Solar_System",
  "categories": [
    "Category:Discovery and exploration of the Solar System",
    "Category:Solar System"
  ],
  "topic": "other",
  "images": [
    "https://upload.wikimedia.org/wikipedia/commons/a/aa/%28253%29_mathilde_crop.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/c6/17pHolmes_071104_eder_vga.jpg",
    "... (more image URLs) ..."
  ],
  "summary": "Discovery and exploration of the Solar System is observation, visitation, and increase in knowledge and understanding of Earth's \"cosmic neighborhood\". ...",
  "chunk_index": 0,
  "char_start": 0,
  "char_end": 836,
  "created_at": "2025-10-04T21:29:53.997985+00:00"
}
```

---

## 🏷️ Field Descriptions

- **chunk_id**: Unique identifier for the chunk (UUID).
- **text**: The main content of the chunk (a passage from a Wikipedia article).
- **title**: Title of the source article.
- **source_url**: URL to the original Wikipedia article.
- **categories**: List of Wikipedia categories associated with the article.
- **topic**: High-level topic label (e.g., "mars", "moon", "other").
- **images**: List of image URLs relevant to the chunk.
- **summary**: A summary of the chunk or its source article.
- **chunk_index**: The position of this chunk within the source article.
- **char_start** / **char_end**: Character offsets of the chunk within the source article.
- **created_at**: Timestamp when the chunk was created.

---

## 📂 Location

All chunk records are stored in [data/processed/chunks.jsonl](../data/processed/chunks.jsonl), one JSON object per line.

---