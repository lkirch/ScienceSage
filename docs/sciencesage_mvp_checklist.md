# ScienceSage MVP Completion Checklist

## 1. Core Functionality (MVP for RAG)
- [x] **Data Acquisition**
  - [x] Fetch and store Wikipedia data on space exploration, missions, planets, astronauts, space tech.
  - [x] Save raw data to `data/raw/`.
- [x] **Preprocessing**
  - [x] Clean and chunk documents (e.g., 1000 tokens with overlap).
  - [x] Save processed chunks to `data/processed/` and `chunks.jsonl`.
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
- [ ] Streamlit Smoke Tests
  - [x] App loads.
  - [ ] Sample queries don’t crash.
  - [x] Show that example queries all run ok.

## 3. Evaluation & Metrics
- [X] **Ground Truth Dataset**
  - [X] 20–30 Q&A pairs covering multiple topics & levels.
  - [X] Save as `data/ground_truth/ground_truth.jsonl`.
- [x] **Evaluation Script**
  - [x] Measure precision@k, recall@k.
  - [x] Optionally LLM-grade answers (0–5).
- [ ] **Metrics Tracking**
  - [ ] Results and metrics
  - [ ] Retrieval hit rate (%).
  - [ ] Average answer quality (manual/LLM-graded).
  - [ ] Save results to CSV/Markdown.

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
- [ ] **README.md**
  - [x] Description & purpose.
  - [x] Run instructions.
  - [x] Example queries & screenshots
  - [ ] About/Help section & screen shots
  - [ ] Create sciencesage_ui.png <- missing or rename link in README
  - [ ] Update results/metrics summary table to the README.
  - [ ] Double-check that all required README sections are present and up to date.
- [ ] **Architecture Diagram**
  - [ ] Update architecture diagram
  - [ ] Data flow diagram: Wikipedia → Preprocessing → Qdrant → Retrieval → GPT-4 → Streamlit.
- [ ] **Demo Script**
  - [ ] 3–5 representative queries, one per difficulty level.
- [x] **Short Summary**
  - [x] Problem → Approach → Results → Future Work.

## 6. Nice-to-Have (Optional)
- [x] Feedback button for user responses.
- [x] Provide citations with hyperlinks.
- [ ] Re-rank retrieved chunks.
- [ ] Add caching (embeddings/LLM responses).
- [ ] Configure Arize

## 7. Known Issues to Fix Later
- [ ] Notebooks still logging in notebooks, not in logs

