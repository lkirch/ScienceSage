import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# --- File paths ---
RAW_DATA_DIR = "data/raw"
RAW_HTML_DIR = os.path.join(RAW_DATA_DIR, "html")
RAW_IMAGES_DIR = os.path.join(RAW_DATA_DIR, "images")
CHUNKS_FILE = "data/chunks/chunks.jsonl"
EMBEDDINGS_FILE = "data/embeddings/embeddings.jsonl"
FEEDBACK_FILE = "data/feedback/feedback.jsonl"
GOLDEN_DATA_FILE = "data/eval/golden_dataset.jsonl"

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# --- Embeddings ---
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
DISTANCE_METRIC = "Cosine"

# --- Chunking ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# --- Tokens ---
MAX_TOKENS = 8192  # For OpenAI text-embedding-3-small

# --- Qdrant ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = "scientific_concepts"
EMBED_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
QDRANT_BATCH_SIZE = 64  # Number of vectors to upload in each batch

# --- Wikipedia settings ---
WIKI_URL = "https://en.wikipedia.org"
WIKI_USER_AGENT = "ScienceSageBot/1.0 (contact: lkonthego@gmail.com)"
WIKI_CRAWL_DEPTH = 1   # Set to desired depth (1 = just topics, 2 = topics + linked pages, etc.)
WIKI_MAX_PAGES = 100    # Limit the number of pages to crawl


# --- Standard chunk fields ---
STANDARD_CHUNK_FIELDS = [
    "id",                # Unique chunk ID
    "text",              # The chunked text content
    "title",             # Page/article title
    "source_url",        # Source URL
    "section",           # Section/subsection title   
    "categories",        # Wikipedia categories for the page
    "images",            # List of image URLs or metadata   
    "embedding",         # The vector embedding (for Qdrant)
    "summary",           # Summary (if available)
    "timestamp"          # Timestamp of creation or last update    
]

# --- Topics ---
TOPICS = [
    "Space exploration",
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

MIN_SCORE_THRESHOLD = 0.2  # discard very low-similarity scores

logger.add("logs/sciencesage.log", rotation="10 MB", retention="10 days", level="INFO")
logger.info("Configuration loaded.")
