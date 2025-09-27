import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# --- File paths ---
RAW_DATA_DIR = "data/raw"
CHUNKS_FILE = "data/processed/chunks.jsonl"

# Embedding files for each backend
OPENAI_EMBEDDING_FILE = "data/embeddings/openai_embeddings.parquet"
SENTENCE_TRANSFORMER_EMBEDDING_FILE = "data/embeddings/sbert_embeddings.parquet"

EMBEDDING_FILES = {
    "openai": OPENAI_EMBEDDING_FILE,
    "sentence-transformers": SENTENCE_TRANSFORMER_EMBEDDING_FILE,
}

FEEDBACK_FILE = "data/feedback/feedback.jsonl"
GROUND_TRUTH_FILE = "data/ground_truth/ground_truth_dataset.jsonl"
EVAL_RESULTS_FILE = "data/eval/eval_results.jsonl"
LLM_EVAL_FILE = "data/eval/llm_eval.jsonl"
METRICS_SUMMARY_FILE = "data/eval/metrics_summary.csv"

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# --- Embeddings ---
EMBEDDING_MODELS = {
    "openai": {
        "model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        "dim": 1536,
        "max_tokens": 8192,
        "distance_metric": "Cosine",
        "collection": "scientific_concepts_openai",
    },
    "sentence-transformers": {
        "model": os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2"),
        "dim": 384,
        "max_tokens": 512,
        "distance_metric": "Cosine",
        "collection": "scientific_concepts_sbert",
    },
}

# Select backend
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "sentence-transformers")  # "openai" or "sentence-transformers"

# --- Chunking ---
CHUNK_SIZE = None
CHUNK_OVERLAP = 0

# --- Tokens ---
MAX_TOKENS = EMBEDDING_MODELS[EMBEDDING_BACKEND]["max_tokens"]

# --- Qdrant ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = EMBEDDING_MODELS[EMBEDDING_BACKEND]["collection"]
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
QDRANT_BATCH_SIZE = 64

# --- Wikipedia settings ---
WIKI_URL = "https://en.wikipedia.org"
WIKI_USER_AGENT = "ScienceSageBot/1.0 (contact: lkonthego@gmail.com)"

# --- Chunk fields ---
CHUNK_FIELDS = [
    "uuid",
    "text",
    "title",
    "source_url",
    "categories",
    "topic",
    "images",
    "summary",
    "chunk_index",
    "char_start",
    "char_end",
    "created_at"
]

EXCLUDED_CATEGORY_PREFIXES = sorted([
    "Category:Accuracy",
    "Category:All",
    "Category:Articles",
    "Category:CS1",
    "Category:Commons",
    "Category:Disambiguation",
    "Category:Hidden",
    "Category:Lists",
    "Category:Lists of",
    "Category:Maintenance",
    "Category:Monitoring",
    "Category:Non-article",
    "Category:Pages",
    "Category:Pages using",
    "Category:Pages with",
    "Category:Project",
    "Category:Redirects",
    "Category:Short",
    "Category:Stub",
    "Category:Template",
    "Category:Tracking",
    "Category:Unprintworthy",
    "Category:Use",
    "Category:Vague",
    "Category:Webarchive",
    "Category:Wikipedia",
    "Category:WikiProject",
    "Category:Articles containing",
    "Category:Articles lacking",
    "Category:Articles missing",
    "Category:Articles needing",
    "Category:Articles using",
    "Category:Articles with",
])

# --- Topics ---
TOPICS = [
    "Space exploration",
    "Category:Space missions",
    "Category:Discovery and exploration of the Solar System",
    "Category:Exploration of Mars",
    "Category:Exploration of the Moon",
    "Animals in space",
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
TOP_K = 5
SIMILARITY_THRESHOLD = 0.2

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger.add("logs/sciencesage.log", rotation="10 MB", retention="10 days", level=LOG_LEVEL)
logger.info("Configuration loaded for backend: %s", EMBEDDING_BACKEND)
