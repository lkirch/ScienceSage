🛠️ Using the Makefile

This project includes a Makefile to simplify common setup and run tasks.

**Notes:**
- You still need to start Qdrant before running any commands that interact with the vector database.
- See the Makefile for current available targets and details.

--- 

List available commands
```bash
make help
```

Typical usage:

- Set up the environment and install dependencies:
```bash
make setup
```

or
```bash
make install
```

- Download, preprocess, and embed data (full pipeline):
```bash
make data
```
or
```bash
make ingest
```

- Download only:
```bash
make download
```

- Preprocess only:
```bash
make preprocess
```

- Embed only:
```bash
make embed
```

- Run the Streamlit app:
```bash
make run-app
```
or
```bash
make run
```

- Run the FastAPI RAG API:
```bash
make run-api
```

- Create ground truth dataset:
```bash
make create-ground-truth
```

- Validate ground truth dataset:
```bash
make validate-ground-truth
```

- Generate retrieval evaluation results:
```bash
make generate-eval-results
```

- Run RAG LLM evaluation:
```bash
make rag-llm-eval
```

- Summarize evaluation metrics:
```bash
make summarize-metrics
```

- Check to see if example queries run:
```bash
make ck-example-queries
```

- Run all evaluation steps:
```bash
make eval-all
```

- Run all tests:
```bash
make test
```

- Test Qdrant connection:
```bash
make test-qdrant
```

- Show last 50 lines of logs:
```bash
make logs
```

- Remove all log files:
```bash
make clean-logs
```

- Clean up generated data outputs:
```bash
make clean
```