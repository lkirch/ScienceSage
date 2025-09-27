# Makefile for ScienceSage

# Paths
APP_DIR=sciencesage
SCRIPTS_DIR=scripts
DATA_DIR=data
ENV_FILE=.env

.PHONY: all setup ingest preprocess embed create-golden validate-golden generate-eval-results rag-llm-eval eval-all run-app run-api test test-qdrant clean logs help install data run

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
## Golden Dataset & Evaluation
## ------------------------

create-golden:
	@echo ">>> Creating golden dataset..."
	python $(SCRIPTS_DIR)/create_golden_dataset.py

validate-golden:
	@echo ">>> Validating golden dataset..."
	python $(SCRIPTS_DIR)/validate_golden_dataset.py

generate-eval-results:
	@echo ">>> Generating evaluation results..."
	python $(SCRIPTS_DIR)/generate_eval_results.py

rag-llm-eval:
	@echo ">>> Running RAG LLM evaluation..."
	python $(SCRIPTS_DIR)/rag_llm_evaluation.py

eval-all: create-golden validate-golden generate-eval-results rag-llm-eval
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
	rm -rf $(DATA_DIR)/processed/* $(DATA_DIR)/chunks/*

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
	@echo "  make create-golden        - Create golden evaluation dataset"
	@echo "  make validate-golden      - Validate golden dataset"
	@echo "  make generate-eval-results- Generate evaluation results"
	@echo "  make rag-llm-eval         - Run RAG LLM evaluation"
	@echo "  make eval-all             - Run all evaluation steps (create-golden, validate-golden, generate-eval-results, rag-llm-eval)"
	@echo "  make run-app              - Start the Streamlit application"
	@echo "  make run-api              - Start the FastAPI RAG API"
	@echo "  make run                  - Start the Streamlit application (alias)"
	@echo "  make test                 - Run all tests using pytest"
	@echo "  make test-qdrant          - Run Qdrant sanity check script"
	@echo "  make clean                - Remove processed files and chunks"
	@echo "  make logs                 - Show last 50 lines of logs"
	@echo "  make help                 - Display this help message"
