import os
from dotenv import load_dotenv
load_dotenv()

from loguru import logger

# --- File paths ---
RAW_DATA_DIR = "data/raw"
CHUNKS_FILE = "data/processed/chunks.jsonl"
EMBEDDING_FILE = "data/embeddings/embeddings.parquet"
FEEDBACK_FILE = "data/feedback/feedback.jsonl"
GROUND_TRUTH_FILE = "data/ground_truth/ground_truth_dataset.jsonl"
EVAL_RESULTS_FILE = "data/eval/eval_results.jsonl"
LLM_EVAL_FILE = "data/eval/llm_eval.jsonl"
METRICS_SUMMARY_FILE = "data/eval/metrics_summary.csv"

# --- Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
MAX_TOKENS = 512
DISTANCE_METRIC = "Cosine" # Options: Cosine, Euclidean, Dot
QDRANT_COLLECTION = "scientific_concepts"

# --- Chunking ---
CHUNK_SIZE = None
CHUNK_OVERLAP = 0

# --- Qdrant ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
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

# --- Retrieval settings ---
TOP_K = 5
SIMILARITY_THRESHOLD = 0.2

# --- LLM Model ---
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Arize ---
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger.add("logs/sciencesage.log", rotation="10 MB", retention="10 days", level=LOG_LEVEL)
logger.info("Configuration loaded.")