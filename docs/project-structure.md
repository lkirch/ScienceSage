## 📂 Project Structure

```
ScienceSage/
│
├── sciencesage/            # Application (Streamlit + backend logic)
│ ├── rag_api.py            # FastAPI backend for RAG
│ ├── app.py                # Streamlit UI
│ ├── config.py             # API keys & settings
│ ├── prompts.py            # Prompts
│ ├── metrics.py            # For evaluating retrieval and answer quality
│ ├── retrieval_system.py   # Core RAG logic: Query → retrieve → GPT pipeline
│ ├── feedback_manager.py   # Save thumbs up/down
│ └── analyze_feedback.py   # Summarize user feedback
│
├── data/                   # Data sources & outputs (Raw data → Processed chunks → Embeddings → Evaluation → Feedback)
│ ├── raw/                  # Raw Wikipedia data & metadata (.html, .txt, .meta.json per articl)
│ ├── processed/            # Cleaned, chunked text (chunks.jsonl)
│ ├── embeddings/           # Vector embeddings for retrieval (embeddings.parquet)
│ ├── ground_truth/         # Ground truth dataset for evaluation (ground_truth_dataset.jsonl)
│ ├── eval/                 # Evaluation results and metrics (eval_results.jsonl, llm_eval.jsonl)
│ └── feedback/             # User feedback for analysis (feedback.jsonl)
|
├── images/                 # Images
|
├── logs/                   # Logs
|
├── notebooks/              # Jupyter exploration
│ ├── eda.ipynb             # EDA of raw and processed Wikipedia data
│ ├── ck_chunks.ipynb       # Inspect and validate the chunking process and chunk metadata
│ ├── qdrant_eda.ipynb.     # Analyze Qdrant vector DB contents and embedding distributions
│ ├── research_wikipedia_topics.ipynb # Research and select relevant Wikipedia articles for project topics
│ ├── sanity_check.ipynb    # End-to-end pipeline sanity check with sample queries
│ └── sciencesage_rag_llm_evaluation.ipynb # Evaluate retrieval and LLM answer quality and compute metrics
│
├── scripts/                # Utilities
│ ├── download_and_clean.py # Download Wikipedia → text
│ ├── preprocess.py         # Chunk text → JSONL
│ ├── embed.py              # Embed chunks → Qdrant
│ ├── rag_api.py            # FastAPI RAG backend (retrieval + answer)
│ ├── streamlit_app.py      # Streamlit UI (calls RAG API)
│ └── evaluate_rag.py       # Evaluate retrieval/answer quality
│
├── docker/                 # Docker setup
│ └── Dockerfile
│
├── tests/                  # Unit/integration tests
│ ├── conftest.py           # Setup/teardown for the test suite
│ ├── test_app_pipeline.py. # Tests the end-to-end application pipeline
│ ├── test_embed.py.        # Tests the embedding process
│ ├── test_integration.py.  # Tests across the retrieval system, LLM, and database
│ ├── test_missing.py.      # Testing missing/invalid data 
│ ├── test_pipeline.py.     # Tests RAG pipeline logic
│ ├── test_prompts.py.      # Test prompt generation logic
│ ├── test_qdrant.py        # Tests interactions with Qdrant
│ ├── test_retrieval_system.py # Tests the retrieval system
│ ├── test_session_state.py # Tests Streamlit session state logic
│ └── test_ui.py            # Tests Streamlit UI components
│
├── requirements.txt        # Python dependencies
├── README.md               # Project description & usage (this file)
├── Makefile                # Common workflows
├── pyproject.toml          # Python packaging + deps
├── .env.example            # Example API keys (not committed)
└── .gitignore


