![ScienceSage Logo](images/nano-banana-generated-logo.jpeg)

## 🤔💭 Problem: Why ScienceSage?

🚀 Space exploration is fascinating, but often hard to understand — especially for younger learners or those new to the field. Reliable information is scattered across the web, and most resources aren’t tailored to different backgrounds.

**ScienceSage** bridges this gap by:
- Delivering accurate, up-to-date answers sourced from Wikipedia.
- Adapting explanations for middle schoolers, college students, or advanced users.
- Providing clear citations for every answer.
- Enabling feedback to improve explanations over time.

Space exploration inspires curiosity and innovation, but understanding it shouldn’t be limited by age or background.

This system helps users **explore complex scientific topics—focused on space exploration—at different levels of explanation**:
- 🏫 **Middle School** (simple, intuitive)
- 🎓 **College** (intermediate, with more depth)
- 🧪 **Advanced** (detailed, technical)

---

## 💡 Approach

**ScienceSage** is an end-to-end **Retrieval-Augmented Generation (RAG)** project built for the [LLM Zoomcamp Capstone](https://github.com/DataTalksClub/llm-zoomcamp), powered by **GPT-4**, **Qdrant**, and **Streamlit**, and developed in Codespaces (Python 3.12).

✨ **Features**:
- **End-to-end RAG pipeline** (OpenAI GPT + Qdrant vector DB).  
- **Multi-level answers** (simple → advanced).  
- **Wikipedia as the primary data source** (focused on space exploration).  
- **Feedback system** (👍 / 👎 per answer, stored for analysis).  
- **Streamlit interface** with example queries and sidebar controls.  

📊 **Data Source** : [Wikipedia](https://www.wikipedia.org/) (focused on space exploration topics)

🔹 **Topics**
- **Space Exploration**
- **Space missions**
- **Discovery and exploration of the Solar System**
- **Exploration of Mars**
- **Exploration of the Moon**
- **Animals in space**

---

## 📊 Results

---

## 🔜 Future Work

---

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

```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/lkirch/ScienceSage.git
cd ScienceSage
```

### 2. Create a virtual environment
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the environment variables
Copy `.env.example` → `.env` and fill in:
```ini
OPENAI_API_KEY=sk-xxxx
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. Start Qdrant

You need a running Qdrant vector database for embedding and retrieval.  
You can start Qdrant using Docker:

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

- This will start Qdrant on `localhost:6333` (REST API) and `localhost:6334` (gRPC).
- Make sure Qdrant is running **before** running any scripts that load collections or query the database.

Alternatively, see [Qdrant documentation](https://qdrant.tech/documentation/quick-start/) for other install options.

### 5. Prepare the data
```bash
python scripts/download_and_clean.py        # fetch Wikipedia (space exploration)
python scripts/preprocess.py                # clean & chunk into JSONL
python scripts/embed.py                     # embed & store in Qdrant
```

### 6. Run the Streamlit app
```bash
streamlit run sciencesage/app.py
```

### 7. Run the FastAPI RAG API

This backend serves retrieval-augmented answers via HTTP.

```bash
uvicorn scripts.rag_api:app --reload
```

The API will be available at http://localhost:8000.  You can test it with:

```bash
curl -X POST "http://localhost:8000/rag" -H "Content-Type: application/json" -d '{"query": "What is the Hubble Space Telescope?"}'
```

### 8. Run the Streamlit Frontend

This web app lets you interact with the RAG system visually.

```bash
streamlit run scripts/streamlit_app.py
```

- The app will open in your browser (or use $BROWSER http://localhost:8501).
- Make sure the FastAPI RAG API is running before using the Streamlit app.

### 9. Evaluate Retrieval and Answer Quality

You can evaluate your RAG pipeline using a golden dataset:

```bash
python scripts/evaluate_rag.py
```

- Results are saved to data/eval/eval_results.jsonl.
- The script reports retrieval recall and answer match metrics.

---

## 🛠️ Using the Makefile

This project includes a `Makefile` to simplify common setup and run tasks.
See [docs/using-the-makefile.md](docs/using-the-makefile.md) for more details.

### List available commands
```bash
make help
```

### Typical usage

- **Set up the environment and install dependencies:**
  ```bash
  make install
  ```
- **Prepare the data (download, preprocess, embed):**
  ```bash
  make data
  ```
- **Run the Streamlit app:**
  ```bash
  make run-app
  ```
- **Clean up generated files:**
  ```bash
  make clean
  ```

> **Note:**  
> You still need to [start Qdrant](#4-start-qdrant) before running any commands that interact with the vector database.

See the `Makefile` for more available targets and details.

---

## 🧪 Running Tests

Unit and integration tests are located in the `tests/` directory and use [pytest](https://docs.pytest.org/).

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run a specific test file
```bash
pytest tests/test_pipeline.py
```

> **Tip:**  
> Make sure your virtual environment is activated and all dependencies are installed before running tests.

Some integration tests require a running Qdrant instance and a valid OpenAI API key.  
You can skip these by default, or set the required environment variables to enable

---

## 🖥️ Usage

- Select a topic in the sidebar (Space Exploration)
- Choose answer complexity (Middle School / College / Advanced)
- Use an example question or ask a question of your own
- Get a generated answer with citations to Wikipedia sources
- Click the Show retrieved context to view the context returned
- Provide feedback via 👍 / 👎
- Click the Debug Options expander to show debug info

---

## 💡 Example Queries

Here are some example questions to try for space exploration:


🚀 Space Exploration

- Middle School: "What is the International Space Station?"
- College: "How do Mars rovers navigate on the surface?"
- Advanced: "Describe NASA's three-phase official plan for human exploration and colonization of Mars."

---

## ✅ Requirements

All Python dependencies are listed in `requirements.txt`.  
Install with:
```bash
pip install -r requirements.txt
```

---

## 🛠️ API Reference

**POST /rag**

- **Input:**  
  ```json
  {
    "query": "What is the Hubble Space Telescope?",
    "top_k": 5
  }
  ```

- **Output:**  
  ```json
  {
    "answer": "...",
    "context_chunks": [...],
    "sources": ["[1] https://en.wikipedia.org/wiki/Hubble_Space_Telescope", ...]
  }
  ```

---

## 🏅 Ground Truth Dataset Format

Each line in `data/ground_truth/ground_truth_dataset.jsonl` should be a JSON object like:

```json
{"chunk_id": "cd61606a-b53b-5385-b764-1b82a8d660ec", 
  "topic": "moon", 
  "text": "Commercial Lunar Payload Services (CLPS) is a NASA program to hire companies to send small robotic landers and rovers to the Moon. Most landing sites are near the lunar south pole where they will scout for lunar resources, test in situ resource utilization (ISRU) concepts, and perform lunar science to support the Artemis lunar program. CLPS is intended to buy end-to-end payload services between Earth and the lunar surface using fixed-price contracts. The program achieved the first landing on the Moon by a commercial company in history with the IM-1 mission in 2024. The program was extended to add support for large payloads starting after 2025.\nThe CLPS program is run by NASA's Science Mission Directorate along with the Human Exploration and Operations and Space Technology Mission directorates.", 
  "level": "Middle School", 
  "question": "What is the purpose of the Commercial Lunar Payload Services (CLPS) program?", 
  "answer": "The purpose of the CLPS program is to hire companies to send small robotic landers and rovers to the Moon."
}
```

---

## 📝 Notes

- The **Streamlit app** in `sciencesage/app.py` is the UI.  
- Make sure to set up your `.env` file with `OPENAI_API_KEY`.
- To open the Streamlit app in your browser from the dev container, use:
  ```bash
  $BROWSER http://localhost:8501
  ```
- All dependencies are managed in `requirements.txt`.

---

## 🙌 Acknowledgements

- [DataTalksClub LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp)
- [GitHub Codespaces](https://github.com/features/codespaces)
- [Wikipedia API](https://pypi.org/project/Wikipedia-API/)
- [Qdrant](https://qdrant.tech/)
- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [Claude](http://claude.ai) and [ChatGPT](http://chatgpt.com) for brainstorming, code debugging and improvements
- [Google's Nano Banana](https://aistudio.google.com/prompts/new_chat?model=gemini-2.5-flash-image-preview) for designing the logo

---

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue or PR if you have suggestions or improvements.

---