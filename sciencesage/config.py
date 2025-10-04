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
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "sciencesage.log")
EXAMPLE_QUERY_SUMMARY_FILE = "data/eval/example_query_summary.jsonl"

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
    "chunk_id",
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

EXAMPLE_QUERIES = {
    "Space exploration": [
        "Who was the first human to travel into outer space, and in which spacecraft did they fly?",
        "What are the main rationales for space exploration?",
        "How has international cooperation in space exploration evolved since the Space Race era, and what are the current examples of major cooperative programs?"
    ],
    "Category:Space missions": [
        "What was the objective of the Voyager missions?",
        "How do robotic space missions differ from crewed missions?",
        "Which space missions have explored the outer planets?"
    ],
    "Category:Discovery and exploration of the Solar System": [
        "What was the first artificial satellite launched into space?",
        "What was the significance of Johannes Kepler's work with Mars and how did it advance our understanding of the Solar System?",
        "How have technological developments in astronomy and physics contributed to the redefinition of the Solar System from a geocentric to a heliocentric model?"
    ],
    "Category:Exploration of Mars": [
        "What are the names of the two NASA rovers currently operating on the surface of Mars?",
        "What is the main reason for the high failure rate of missions sent to Mars?",
        "What is NASA's three-phase official plan for human exploration and colonization of Mars?"
    ],
    "Category:Exploration of the Moon": [
        "Who were the first astronauts to land on the Moon, and in which year did this happen?",
        "What significant firsts were achieved by China's Chang'e program on the Moon?",
        "What are NASA's Artemis program goals and the scientific and logistical objectives supporting the return to the Moon?"
    ],
    "Animals in space": [
        "What was the first animal sent into space and in which year?",
        "Which animals were the first to orbit the Moon, and on what mission?",
        "What were some of the biological experiments and species used in space research from the 1970s to the 1990s?"
    ]
}

# --- Retrieval settings ---
TOP_K = 10
SIMILARITY_THRESHOLD = 0.1

# --- LLM Model ---
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Arize ---
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
os.makedirs(LOGS_DIR, exist_ok=True)
logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="10 days",
    level=LOG_LEVEL,
    format="{time} | {level} | {name}:{function}:{line} | {message}",
    enqueue=True,
    backtrace=True,
    diagnose=True
)
logger.info("Configuration loaded.")

# --- Evaluation metric fields ---
RETRIEVAL_METRIC_KEYS = [
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
    "ndcg_at_k"
]
LLM_METRIC_KEYS = [
    "exact_match"
]