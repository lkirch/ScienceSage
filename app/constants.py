"""
Constants for ScienceSage project.
Keep static values here (not secrets).
"""

# --- Topics we support ---
TOPICS = [
    "Neuroplasticity",
    "AI",
    "Renewable Energy & Climate Change",
    "Animal Adaptation & Behavior",
    "Ecosystem Interactions",
]

# --- Education levels ---
LEVELS = [
    "Middle School",
    "College",
    "Advanced",
]

# --- Embedding model ---
EMBEDDING_MODEL = "text-embedding-3-small"

# --- Chat completion model ---
CHAT_MODEL = "gpt-4o-mini"

# --- File paths ---
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/chunks"
CHUNKS_FILE = f"{PROCESSED_DATA_DIR}/chunks.jsonl"
EMBEDDINGS_FILE = "data/embeddings/embeddings.jsonl"

# --- Qdrant ---
QDRANT_COLLECTION = "scientific_concepts"

# --- Feedback ---
FEEDBACK_FILE = "data/feedback/feedback.jsonl"

# --- Retrieval settings ---
TOP_K = 3   # number of chunks to retrieve
