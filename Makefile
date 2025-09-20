# Makefile for ScienceSage

# Paths
APP_DIR=sciencesage
SCRIPTS_DIR=scripts
DATA_DIR=data
ENV_FILE=.env

# Main targets
.PHONY: all ingest run-app test test-qdrant clean logs help download preprocess embed

all: ingest run-app

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

## ------------------------
## Application
## ------------------------

run-app:
	@echo ">>> Starting Streamlit app..."
	streamlit run $(APP_DIR)/main.py --server.port=8501

## ------------------------
## Testing
## ------------------------

test:
	@echo ">>> Running tests..."
	pytest -q --disable-warnings --maxfail=1

test-qdrant:
	@echo ">>> Testing Qdrant connection..."
	python $(SCRIPTS_DIR)/test_qdrant.py

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
	@echo "  make download       - Download raw data"
	@echo "  make preprocess     - Chunk processed text into JSONL for embeddings"
	@echo "  make embed          - Embed chunks into Qdrant"
	@echo "  make ingest         - Run full pipeline: download → preprocess → embed"
	@echo "  make run-app        - Start the Streamlit application"
	@echo "  make test           - Run all tests using pytest"
	@echo "  make test-qdrant    - Run Qdrant sanity check script"
	@echo "  make clean          - Remove processed files and chunks"
	@echo "  make logs           - Show last 50 lines of logs"
	@echo "  make help           - Display this help message"
