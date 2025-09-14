import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# --- File paths ---
RAW_DATA_DIR = "data/raw"
RAW_HTML_DIR = os.path.join(RAW_DATA_DIR, "html")
RAW_IMAGES_DIR = os.path.join(RAW_DATA_DIR, "images")
RAW_PDF_DIR = os.path.join(RAW_DATA_DIR, "pdf")
PROCESSED_DATA_DIR = "data/processed"
CHUNKS_FILE = "data/chunks/chunks.jsonl"
EMBEDDINGS_FILE = "data/embeddings/embeddings.jsonl"
FEEDBACK_FILE = "data/feedback/feedback.jsonl"

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

NASA_API_KEY = os.getenv("NASA_API_KEY")
if not NASA_API_KEY:
    raise RuntimeError("NASA_API_KEY environment variable not set")

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

# --- NASA APOD settings ---
NASA_APOD_API_URL = "https://api.nasa.gov/planetary/apod"
NASA_APOD_DAYS = 30                      # Number of days of APOD to fetch
NASA_APOD_START_DATE = None  # e.g., "2023-01-01", or None to fetch latest

# --- Wikipedia settings ---
WIKI_USER_AGENT = "ScienceSageBot/1.0 (contact: lkonthego@gmail.com)"
WIKI_CRAWL_DEPTH = 1   # Set to desired depth (1 = just topics, 2 = topics + linked pages, etc.)
WIKI_MAX_PAGES = 100    # Limit the number of pages to crawl

# --- arXiv Categories ---
ARXIV_CATEGORIES = [
    "cs.AI",             # Artificial Intelligence
    "cs.CV",             # Computer Vision
    "cs.ET",             # Emerging Technologies
    "cs.LG",             # Machine Learning
    "cs.MA",             # Multiagent Systems
    "astro-ph",          # Astrophysics
    "physics.space-ph",  # Space Physics
    "physics.ao-ph",     # Atmospheric and Oceanic Physics
    "physics.geo-ph",    # Geophysics
    "climate-change",    # Climate Change
]
ARXIV_MAX_RESULTS = 10  # Number of papers to fetch per category

# --- Topics ---
TOPICS = [
    "Space",
    "AI",
    "Climate"
]

# --- Topic Keywords ---
TOPIC_KEYWORDS = {
    "Space": [
        "space", "astronomy", "cosmos", "universe", "galaxy", "star", "planet", "satellite",
        "black hole", "nebula", "telescope", "astronaut", "spacecraft", "NASA", "cosmology",
        "solar system", "exoplanet", "comet", "asteroid", "orbit", "rocket", "super nova",
        # Recent missions:
        "Artemis", "Artemis I", "Artemis II", "Mars Sample Return", "JUICE", "Psyche",
        "OSIRIS-REx", "Chandrayaan-3", "Tianwen-1", "Euclid", "XRISM", "SLIM", "Starship",
        "Perseverance rover", "James Webb Space Telescope", "JWST", "DART mission", "Lucy mission",
        "Hayabusa2", "BepiColombo", "Rosalind Franklin rover", "Lunar Gateway", "CLPS",
        "Voyage 1", "Voyage 2", "Hubble Space Telescope", "Spitzer Space Telescope",
        "Cassini-Huygens", "New Horizons", "InSight", "Curiosity rover"
    ],
    "AI": [
        "ai", "artificial intelligence", "machine learning", "neural network", "deep learning",
        "transformer", "reinforcement learning", "large language model", "natural language processing",
        "computer vision", "robotics", "algorithm", "supervised learning", "unsupervised learning",
        "generative ai", "chatbot", "data science", "pattern recognition"
    ],
    "Climate": [
        "climate", "climate change", "global warming", "greenhouse gas", "carbon dioxide",
        "emissions", "renewable energy", "solar power", "wind energy", "fossil fuel",
        "mitigation", "adaptation", "sea level rise", "extreme weather", "carbon footprint",
        "sustainability", "environment", "biodiversity", "ecosystem", "deforestation"
    ],
}

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
