import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# --- File paths ---
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
CHUNKS_FILE = "data/chunks/chunks.jsonl"
EMBEDDINGS_FILE = "data/embeddings/embeddings.jsonl"
FEEDBACK_FILE = "data/feedback/feedback.jsonl"

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# --- Embeddings ---
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
DISTANCE_METRIC = "Cosine"

# --- Chunking ---
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- Qdrant ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = "scientific_concepts"
EMBED_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"

# --- Topics ---
TOPICS = [
    "Neuroplasticity",
    "AI",
    "Renewable Energy & Climate Change",
    "Animal Adaptation",
    "Ecosystem Interactions"
]

# --- Education levels ---
LEVELS = [
    "Middle School",
    "College",
    "Advanced",
]

# --- Chat completion model ---
CHAT_MODEL = "gpt-4o-mini"

# --- Retrieval settings ---
TOP_K = 3   # number of chunks to retrieve

logger.add("logs/sciencesage.log", rotation="10 MB", retention="10 days", level="INFO")
logger.info("Configuration loaded.")
