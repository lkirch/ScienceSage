# ScienceSage MVP Completion Checklist

## 1. Core Functionality (MVP for RAG)
- [x] **Data Acquisition**
  - [x] Fetch and store Wikipedia data on space exploration, missions, planets, astronauts, space tech.
  - [x] Save raw data to `data/raw/`.
- [x] **Preprocessing**
  - [x] Clean and chunk documents (e.g., 1000 tokens with overlap).
  - [x] Save processed chunks to `data/processed/chunks.jsonl`.
  - [x] Auto-tag chunks with topic (space_missions, planets, etc.).
- [x] **Vector Store Setup**
  - [x] Embed chunks (sentence-transformers).
  - [x] Store vectors + metadata in Qdrant.
  - [x] Verify Qdrant collection is populated.
- [x] **Retriever**
  - [x] Query Qdrant for top-k relevant chunks.
  - [x] Return retrieved context and metadata.
- [x] **LLM Response**
  - [x] Pass retrieved chunks into GPT-4o-mini.
  - [x] Generate level-appropriate answer.
  - [x] Return answer + source references.

## 2. Streamlit App (User Experience)
- [x] Clean, working UI in `sciencesage/app.py`.
- [x] Components:
  - [x] Input box for user question.
  - [x] Radio buttons for difficulty level.
  - [x] Drop down for topic filter.
  - [x] Display answer text, retrieved context (expandable), debug info (toggle).
- [x] Error handling (friendly message if Qdrant/LLM fails).
- [x] Streamlit Smoke Tests
  - [x] App loads.
  - [x] Sample queries don’t crash.
  - [x] Show that example queries all run ok.

## 3. Evaluation & Metrics
- [X] **Ground Truth Dataset**
  - [X] 20–30 Q&A pairs covering multiple topics & levels.
  - [X] Save as `data/ground_truth/ground_truth.jsonl`.
- [x] **Evaluation Script**
  - [x] Measure precision@k, recall@k.
  - [x] Optionally LLM-grade answers (0–5).
- [x] **Metrics Tracking**
  - [x] Results and metrics
  - [x] Retrieval hit rate (%).
  - [x] Average answer quality (manual/LLM-graded).
  - [x] Save results to CSV/Markdown.

## 4. Testing & Logging
- [x] **Unit Tests**
  - [x] Chunking function.
  - [x] Qdrant insert & retrieval.
  - [x] Retriever returns relevant context.
- [ ] **Streamlit Smoke Tests**
  - [x] App loads.
  - [x] Sample queries don’t crash.
- [x] **Logging**
  - [x] Loguru setup: logs go to `logs/`.
  - [x] Log query, retrieved docs, LLM output.

## 5. Project Presentation (Capstone Deliverable)
- [x] **README.md**
  - [x] Description & purpose.
  - [x] Run instructions.
  - [x] Example queries & screenshots
  - [x] About/Help section & screen shots
  - [x] Update results/metrics summary table to the README.
- [x] **Architecture Diagram** Wikipedia → Preprocessing → Qdrant → Retrieval → GPT-4 → Streamlit.
- [ ] **Demo Script**
  - [x] 3–5 representative queries, one per difficulty level.
- [x] **Short Summary**
  - [x] Problem → Approach → Results → Future Work.

## 6. Nice-to-Have (Optional)
- [x] Feedback button for user responses.
- [x] Provide citations with hyperlinks.
- [ ] Data flow diagram
- [ ] Re-rank retrieved chunks.
- [ ] Add caching (embeddings/LLM responses).
- [ ] Configure Arize in qdrant_eda.ipynb

## 7. Known Issues to Fix Later
- [ ] Try to get the thumbs up/down icons on the same line as Feedback on this answer:
- [ ] Notebooks still logging in notebooks, not in logs

