# 🗃️ ScienceSage Metadata

This document describes the metadata structure associated with each Wikipedia article and chunk in ScienceSage. Metadata provides context and enables efficient retrieval, filtering, and analysis.

---

## 📄 Example Metadata Record

```json
{
  "article_id": "b8c1e1a2-3f6d-4e2b-9c2e-1a2b3c4d5e6f",
  "title": "Mars Exploration",
  "source_url": "https://en.wikipedia.org/wiki/Mars_exploration",
  "categories": [
    "Category:Mars",
    "Category:Space missions"
  ],
  "topics": ["mars", "missions"],
  "summary": "Mars exploration refers to the study of Mars by spacecraft. Probes, landers, and rovers have been sent to Mars since the 1960s.",
  "num_chunks": 12,
  "images": [
    "https://upload.wikimedia.org/wikipedia/commons/0/02/Spirit_Rover_on_Mars.jpg"
  ],
  "created_at": "2025-10-04T21:29:53.997985+00:00"
}
```

---

## 🏷️ Field Descriptions

- **article_id**: Unique identifier for the article (UUID).
- **title**: Title of the Wikipedia article.
- **source_url**: URL to the original Wikipedia article.
- **categories**: List of Wikipedia categories associated with the article.
- **topics**: List of high-level topics (e.g., "mars", "missions").
- **summary**: Short summary of the article.
- **num_chunks**: Number of text chunks derived from this article.
- **images**: List of image URLs relevant to the article.
- **created_at**: Timestamp when the metadata record was created.

---

## 📂 Location

Metadata records are typically stored in `data/processed/meta_data.jsonl`, one JSON object per line.

---