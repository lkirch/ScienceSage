import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# --- File paths ---
RAW_DATA_DIR = "data/raw"
CHUNKS_FILE = "data/processed/chunks.jsonl"
EMBEDDING_FILE = "data/embeddings/embeddings.parquet"
FEEDBACK_FILE = "data/feedback/feedback.jsonl"
GROUND_TRUTH_FILE = "data/ground_truth/ground_truth_dataset.jsonl"
EVAL_RESULTS_FILE = "data/eval/eval_results.jsonl" # Stores the output of your retrieval system for each query (retrieved chunks, answers, etc.) for retrieval performance evaluation
LLM_EVAL_FILE = "data/eval/llm_eval.jsonl"
METRICS_SUMMARY_FILE = "data/eval/metrics_summary.csv"

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# --- Embeddings ---
EMBEDDING_MODEL = "text-embedding-3-small" # or "text-embedding-3-large"
EMBEDDING_DIM = 1536
DISTANCE_METRIC = "Cosine"

# --- Chunking ---
CHUNK_SIZE = None # No fixed size when chunking by paragraphs
CHUNK_OVERLAP = 0  # No overlap when chunking by paragraphs

# --- Tokens ---
MAX_TOKENS = 8192  # For OpenAI text-embedding-3-small or test-embedding-3-large

# --- Qdrant ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = "scientific_concepts"
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
QDRANT_BATCH_SIZE = 64  # Number of vectors to upload in each batch

# --- Wikipedia settings ---
WIKI_URL = "https://en.wikipedia.org"
WIKI_USER_AGENT = "ScienceSageBot/1.0 (contact: lkonthego@gmail.com)"


# --- Chunk fields ---
CHUNK_FIELDS = [
    "uuid",              # Unique chunk UUID
    "text",              # The chunked text content
    "title",             # Page/article title
    "source_url",        # Source URL
    "categories",        # Wikipedia categories for the page
    "topic",             # Inferred topic based on categories
    "images",            # List of image URLs or metadata   
    "summary",           # Summary (if available)
    "chunk_index",       # Index of the chunk in the original text
    "char_start",        # Character start position in original text
    "char_end",          # Character end position in original text
    "created_at"         # Timestamp of creation or last update    
]

EXCLUDED_CATEGORY_PREFIXES = [
    "Category:Articles",
    "Category:CS1",
    "Category:Wikipedia",
    "Category:Pages",
    "Category:Vague",
    "Category:Use",
    "Category:Short",
    "Category:Webarchive",
    "Category:All",
    "Category:Commons"
]

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
TOP_K = 5   # number of chunks to retrieve

SIMILARITY_THRESHOLD = 0.2  # discard very low-similarity scores

logger.add("logs/sciencesage.log", rotation="10 MB", retention="10 days", level="INFO")
logger.info("Configuration loaded.")
