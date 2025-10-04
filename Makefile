# Makefile for ScienceSage

# Paths
APP_DIR=sciencesage
SCRIPTS_DIR=scripts
DATA_DIR=data
ENV_FILE=.env

.PHONY: all setup ingest preprocess embed create-ground-truth validate-ground-truth generate-eval-results rag-llm-eval summarize-metrics eval-all run-app run-api test test-qdrant clean logs help install data run clean-logs

## ------------------------
## Setup & Installation
## ------------------------

install:
	@echo ">>> Installing dependencies..."
	pip install --upgrade pip && pip install -r requirements.txt

setup: install
	@echo ">>> Setup complete!"

## ------------------------
## Data Ingestion Pipeline
## ------------------------

download:
	@echo ">>> Downloading and cleaning data..."
	python $(SCRIPTS_DIR)/download_data.py

preprocess:
	@echo ">>> Preprocessing data into chunks..."
	python $(SCRIPTS_DIR)/preprocess.py

embed:
	@echo ">>> Embedding chunks into Qdrant..."
	python $(SCRIPTS_DIR)/embed.py

ingest: download preprocess embed
	@echo ">>> Ingestion pipeline complete!"

data: ingest
	@echo ">>> Data pipeline complete!"

## ------------------------
## Ground Truth Dataset & Evaluation
## ------------------------

create-ground-truth:
	@echo ">>> Creating ground truth dataset..."
	python $(SCRIPTS_DIR)/create_ground_truth_dataset.py

validate-ground-truth:
	@echo ">>> Validating ground truth dataset..."
	python $(SCRIPTS_DIR)/validate_ground_truth_dataset.py

generate-eval-results:
	@echo ">>> Generating retrieval evaluation results..."
	python $(SCRIPTS_DIR)/generate_eval_results.py

rag-llm-eval:
	@echo ">>> Running RAG LLM evaluation..."
	python $(SCRIPTS_DIR)/rag_llm_evaluation.py

summarize-metrics:
	@echo ">>> Summarizing evaluation metrics..."
	python $(SCRIPTS_DIR)/summarize_metrics.py

ck-example-queries:
	@echo ">>> Running example queries check..."
	python $(SCRIPTS_DIR)/ck_example_queries.py

eval-all: create-ground-truth validate-ground-truth generate-eval-results rag-llm-eval summarize-metrics ck-example-queries
	@echo ">>> Full evaluation pipeline complete!"

## ------------------------
## Application
## ------------------------

run-app:
	@echo ">>> Starting Streamlit app..."
	streamlit run $(APP_DIR)/app.py --server.port=8501

run-api:
	@echo ">>> Starting FastAPI RAG API..."
	uvicorn sciencesage.rag_api:app --host 0.0.0.0 --port 8000

run: run-app
	@echo ">>> App started!"

## ------------------------
## Testing
## ------------------------

test:
	@echo ">>> Running tests..."
	pytest -q --disable-warnings --maxfail=1

test-qdrant:
	@echo ">>> Testing Qdrant connection..."
	python tests/test_qdrant.py

## ------------------------
## Utilities
## ------------------------

clean:
	@echo ">>> Cleaning data outputs..."
	rm -rf $(DATA_DIR)/processed/* $(DATA_DIR)/chunks/* $(DATA_DIR)/ground_truth/* $(DATA_DIR)/eval/* $(DATA_DIR)/embeddings/*

clean-logs:
	@echo ">>> Removing all log files..."
	rm -rf logs/*.log

logs:
	@echo ">>> Showing latest logs..."
	tail -n 50 logs/*.log || echo "No logs yet."

## ------------------------
## Help
## ------------------------

help:
	@echo ""
	@echo "ScienceSage Makefile Commands:"
	@echo "  make setup                - Install dependencies"
	@echo "  make install              - Install dependencies (alias)"
	@echo "  make download             - Download raw data"
	@echo "  make preprocess           - Chunk processed text into JSONL for embeddings"
	@echo "  make embed                - Embed chunks into Qdrant"
	@echo "  make ingest               - Run full pipeline: download → preprocess → embed"
	@echo "  make data                 - Run full data pipeline (alias for ingest)"
	@echo "  make create-ground-truth  - Create ground truth dataset"
	@echo "  make validate-ground-truth - Validate ground truth dataset"
	@echo "  make generate-eval-results - Generate retrieval evaluation results"
	@echo "  make rag-llm-eval         - Run RAG LLM evaluation"
	@echo "  make summarize-metrics    - Summarize evaluation metrics"
	@echo "  make eval-all             - Run all evaluation steps (create-ground-truth, validate-ground-truth, generate-eval-results, rag-llm-eval, summarize-metrics, ck-example-queries)"
	@echo "  make ck-example-queries   - Run example queries check"
	@echo "  make run-app              - Start the Streamlit application"
	@echo "  make run-api              - Start the FastAPI RAG API"
	@echo "  make run                  - Start the Streamlit application (alias)"
	@echo "  make test                 - Run all tests using pytest"
	@echo "  make test-qdrant          - Run Qdrant sanity check script"
	@echo "  make clean                - Remove processed files and chunks"
	@echo "  make logs                 - Show last 50 lines of logs"
	@echo "  make clean-logs           - Remove all log files"
	@echo "  make help                 - Display this help message"
	@echo ""
	@echo "Tip: To measure execution time for any pipeline step, prefix with 'time', e.g.:"
	@echo "       time make ingest"
	@echo "       time make data"
	@echo "       time make eval-all"
