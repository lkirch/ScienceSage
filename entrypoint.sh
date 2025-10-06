#!/bin/sh
set -e

echo ">>> Starting Qdrant in the background..."
if [ -f ./qdrant_config.yaml ]; then
  qdrant --config-path ./qdrant_config.yaml &
else
  qdrant &
fi

echo ">>> Waiting for Qdrant to be ready on port 6333..."
until nc -z localhost 6333; do
  echo "Waiting for Qdrant to start..."
  sleep 1
done

echo ">>> Installing Python dependencies via Makefile..."
make install

echo ">>> Running data pipeline via Makefile..."
make data

echo ">>> Running evaluation pipeline via Makefile..."
make eval-all

echo ">>> Launching Streamlit app..."
exec streamlit run sciencesage/app.py --server.port=8501