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
