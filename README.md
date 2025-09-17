![ScienceSage Logo](images/nano-banana-generated-logo.jpeg)

#  🧠 ScienceSage
Smart Science, Made Simple

An end-to-end **Retrieval-Augmented Generation (RAG)** project built for the [LLM Zoomcamp Capstone](https://github.com/DataTalksClub/llm-zoomcamp).  
This system helps users **explore complex scientific topics** (like neuroplasticity, AI concepts, renewable energy, animal behavior, and ecosystem interactions) at **different levels of explanation**:

- 🏫 **Middle School** (simple, intuitive)  
- 🎓 **College** (intermediate, with more depth)  
- 🧪 **Advanced** (detailed, technical)

Powered by **GPT-4**, **Qdrant**, and **Streamlit**, and developed in **Codespaces (Python 3.12)**.

---

## ✨ Features
- **End-to-end RAG pipeline** (OpenAI GPT + Qdrant vector DB).  
- **Multi-level answers** (simple → advanced).  
- **Public domain data sources** (NASA, Wikipedia, Stanford).  
- **Feedback system** (👍 / 👎 per answer, stored for analysis).  
- **Streamlit interface** with example queries and sidebar controls.  

---

## 🔹 Topics
- **Space**
- **AI Concepts** (transformers, RAG, embeddings, etc.)
- **Climate**

---

## 📂 Project Structure
```
ScienceSage/
│
├── sciencesage/            # Application (Streamlit + backend logic)
│ ├── main.py               # Streamlit UI
│ ├── retrieval_system.py   # Query → retrieve → GPT pipeline
│ ├── feedback_manager.py   # Save thumbs up/down
│ ├── analyze_feedback.py   # Summarize user feedback
│ ├── config.py             # API keys & settings
│ └── prompts.py            # Prompts
│
├── data/                   # Data sources & outputs
│ ├── raw/                  # Original files (html, pdf, etc.)
│ ├── processed/            # Clean text files
│ ├── chunks/               # JSONL with chunked docs (JSONL)
│ └── feedback/             # Feedback file for analysis
│ └── eval/                 # Golden dataset + evaluation outputs
|
├── images/                 # Images
|
├── logs/                   # Logs
|
├── notebooks/              # Jupyter exploration
│ └── sanity_check.ipynb
│
├── scripts/                # Utilities
│ ├── download_and_clean.py # Download NASA/Wikipedia/PDF → text
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

## 📊 Data Sources (Public Domain)

- [Wikipedia](https://www.wikipedia.org/)
- [arXiv](https://arxiv.org/)
- [NASA Astronomy Picture of the Day](https://apod.nasa.gov/apod/astropix.html) 

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
python scripts/download_data.py        # fetch NASA/Wikipedia/PDF
python scripts/preprocess.py           # clean & chunk into JSONL
python scripts/embed.py                # embed & store in Qdrant
```

### 6. Run the Streamlit app
```bash
streamlit run sciencesage/main.py
```

### 7. Run the FastAPI RAG API

This backend serves retrieval-augmented answers via HTTP.

```bash
uvicorn scripts.rag_api:app --reload
```

The API will be available at http://localhost:8000.  You can test it with:

```bash
curl -X POST "http://localhost:8000/rag" -H "Content-Type: application/json" -d '{"query": "What is the Hubble constant?"}'
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
python [evaluate_rag.py]
```

- Results are saved to data/eval/eval_results.jsonl.
- The script reports retrieval recall and answer match metrics.


## 🛠️ Using the Makefile

This project includes a `Makefile` to simplify common setup and run tasks.

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
  make run
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

- Select a topic in the sidebar (AI, Neuroplasticity, Climate, etc.).
- Ask a question (e.g., "Explain transformers like I’m 12").
- Choose answer complexity (Middle School / College / Advanced).
- Get a generated answer with citations to sources.
- Provide feedback via 👍 / 👎.

---

## 💡 Example Queries

Here are some example questions to try for each topic:


🤖 AI Concepts

- Middle School: "What is a transformer in AI, explained simply?"
- College: "How do attention mechanisms work in transformers?"
- Advanced: "Compare RAG with fine-tuning for knowledge integration."

🌍 Climate

- Middle School: "Why is Earth getting hotter?"
- College: "What are the main human causes of climate change?"
- Advanced: "Explain how feedback loops (like melting ice) accelerate climate change."

---

## 📦 Requirements

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
    "query": "What is the Hubble constant?",
    "top_k": 5
  }
  ```

- **Output:**  
  ```json
  {
    "answer": "...",
    "context_chunks": [...],
    "sources": ["[1] https://en.wikipedia.org/wiki/Hubble_constant", ...]
  }
  ```

---

## 🏅 Golden Dataset Format

Each line in `data/eval/golden_dataset.jsonl` should be a JSON object like:

```json
{
  "query": "What is the Hubble constant?",
  "expected_sources": ["https://en.wikipedia.org/wiki/Hubble_constant"],
  "expected_answer": "about 70 kilometers per second per megaparsec"
}
```

---

## 📝 Notes

- The **Streamlit app** in `sciencesage/main.py` is the original UI.  
  The **newer frontend** for the RAG API is in `scripts/streamlit_app.py`.  
  Try the new frontend for the best RAG experience.
- Make sure to set up your `.env` file with `OPENAI_API_KEY` (and `NASA_API_KEY` if using NASA data).
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
- [arXiv API](https://info.arxiv.org/help/api/index.html)
- [NASA APOD API](https://github.com/nasa/apod-api)
- [Qdrant](https://qdrant.tech/)
- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [Claude](http://claude.ai) and [ChatGPT](http://chatgpt.com) for brainstorming, code debugging and improvements
- [Google's Nano Banana](https://aistudio.google.com/prompts/new_chat?model=gemini-2.5-flash-image-preview) for designing the logo

---

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue or PR if you have suggestions or improvements.

---