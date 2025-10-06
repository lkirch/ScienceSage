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
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure the environment variables
Copy `.env.example` → `.env` and fill in your OpenAI key:
```ini
OPENAI_API_KEY=sk-xxxx
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. Start Qdrant locally

You need a running Qdrant vector database for embedding and retrieval.  
You can start Qdrant using Docker:

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

- This will start Qdrant on `localhost:6333` (REST API) and `localhost:6334` (gRPC).
- Make sure Qdrant is running **before** running any scripts that load collections or query the database.

Alternatively, see [Qdrant documentation](https://qdrant.tech/documentation/quick-start/) for other install options.

### 5. Prepare the data

You can either run the scripts individually (steps 5a–5c) or use the Makefile commands (recommended for convenience).

```bash
python scripts/download_and_clean.py        # fetch Wikipedia (space exploration)
python scripts/preprocess.py                # clean & chunk into JSONL
python scripts/embed.py                     # embed & store in Qdrant
```

Or if you prefer to use the **Makefile** to prepare and run evaluation:
   ```bash
   make install
   make data
   make eval-all
   ```

### 6. Run the Streamlit app
```bash
streamlit run sciencesage/app.py
```

Or if you prefer to use the **Makefile** to prepare and run evaluation:
   ```bash
   make run-app
   ```

### 7. Open the app in your browser:
   ```bash
   $BROWSER http://localhost:8501
   ```
---

### FastAPI RAG API

This backend serves retrieval-augmented answers via HTTP.

**To run the FastAPI API:**
```bash
uvicorn sciencesage.rag_api:app --reload
```
- The API will be available at [http://localhost:8000](http://localhost:8000).
- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

**Example request:**
```bash
curl -X POST "http://localhost:8000/rag" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Hubble Space Telescope?"}'
```

---

### 🧪 Testing

To run the test suite:
```bash
make test
# or
pytest
```

---

### 📓 Jupyter Notebooks

To launch Jupyter Notebook for exploration and visualization:
```bash
jupyter notebook
# or
make notebook
```
Notebooks are located in the `notebooks/` directory.

---

**Notes:**  
- Make sure Qdrant is running and your `.env` is configured before starting the API.
- The FastAPI app is located at `sciencesage/rag_api.py`.
- The Streamlit app does not require the FastAPI API to be running, but the API is available for programmatic access.