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
- **Neuroplasticity** (psych/neuro)
- **AI Concepts** (transformers, RAG, embeddings, etc.)
- **Renewable Energy & Climate Change**
- **Animal Adaptation/Behavior**
- **Ecosystem Interactions**

---

## 📂 Project Structure
```
ScienceSage/
│
├── app/ # Application (Streamlit + backend logic)
│ ├── app.py # Streamlit UI
│ ├── retrieval_system.py # Query → retrieve → GPT pipeline
│ ├── feedback_manager.py # Save thumbs up/down
│ ├── analyze_feedback.py # Summarize user feedback
│ ├── config.py # API keys & settings
│ └── prompts.py # Prompts
│
├── data/ # Data sources & outputs
│ ├── raw/ # Original files (html, pdf, etc.)
│ ├── processed/ # Clean text files
│ ├── chunks/ # JSONL with chunked docs
│ └── feedback/ # Feedback file for analysis
│
├── notebooks/ # Jupyter exploration
│ └── sanity_check.ipynb
│
├── scripts/ # Utilities
│ ├── download_and_clean.py # Download NASA/Wikipedia/PDF → text
│ ├── preprocess.py # Chunk text → JSONL
│ ├── embed.py # Embed chunks → Qdrant
│ └── test_qdrant.py # Sanity check retrieval
│
├── docker/ # Docker setup
│ └── Dockerfile
│
├── tests/ # Unit/integration tests
│ └── test_pipeline.py
│
├── requirements.txt # Python dependencies
├── README.md # This file
├── .env.example # Example API keys (not committed)
└── .gitignore
```

---

## 📊 Data Sources (Public Domain)

- **Neuroplasticity**: [Wikipedia](https://en.wikipedia.org/wiki/Neuroplasticity)  
- **AI Concepts**:  
  - [Wikipedia – Transformer (ML)](https://en.wikipedia.org/wiki/Transformer_(machine_learning))  
  - [Stanford CS324 LLM Lectures (CC BY-SA)](https://web.stanford.edu/class/cs324/)  
- **Climate Change & Renewable Energy**: [NASA Climate Change](https://climate.nasa.gov/)  
- **Animal Behavior & Ecosystems**:  
  - [Smithsonian Open Access](https://www.si.edu/openaccess)  
  - [Wikipedia – Animal Migration](https://en.wikipedia.org/wiki/Animal_migration)  

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
python scripts/download_and_clean.py   # fetch & clean NASA/Wikipedia/PDF
python scripts/preprocess.py           # chunk into JSONL
python scripts/embed.py                # embed & store in Qdrant
```

### 6. Run the Streamlit app
```bash
streamlit run app/app.py
```

---

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