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

# --- Tokens ---
MAX_TOKENS = 8192  # For OpenAI text-embedding-3-small

# --- Qdrant ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = "scientific_concepts"
EMBED_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"

# --- NASA URLs ---
NASA_URLS = {
    "nasa_overview": "https://climate.nasa.gov/",
    "nasa_evidence": "https://climate.nasa.gov/evidence/",
    "nasa_causes": "https://climate.nasa.gov/causes/",
    "nasa_effects": "https://climate.nasa.gov/effects/",
    "nasa_scientific_consensus": "https://science.nasa.gov/climate-change/scientific-consensus/",
    "nasa_what_is_climate_change": "https://science.nasa.gov/climate-change/what-is-climate-change/",
    "nasa_extreme_weather": "https://science.nasa.gov/climate-change/extreme-weather/",
    "nasa_wildfires": "https://science.nasa.gov/earth/explore/wildfires-and-climate-change/",
    "nasa_faq": "https://science.nasa.gov/climate-change/faq/",
    "nasa_adaptation_mitigation": "https://science.nasa.gov/climate-change/adaptation-mitigation/",
    "nasa_adaptation_mitigation_resources": "https://science.nasa.gov/climate-change/adaptation-mitigation/resources/",
}

# --- Wikipedia Titles ---
WIKI_TITLES = {
    "neuroplasticity": "Neuroplasticity",
    "transformer_ml": "Transformer (machine learning)",
    "reinforcement_learning": "Reinforcement learning",
    "large_language_model": "Large language model",
    "retrieval_augmented_generation": "Retrieval-augmented generation",
    "animal_migration": "Animal migration",
    "climate_change_adaptation": "Climate change adaptation",
    "climate_change_and_fisheries": "Climate change and fisheries",
    "climate_change_and_birds": "Climate change and birds",
    "decline_in_wild_mammal_populations": "Decline in wild mammal populations",
}

# --- PDF Titles ---
PDF_TITLES = {
    "stanford_llm_lecture1": "Stanford LLM Lecture 1",
}

# --- Topics ---
TOPICS = [
    "Neuroplasticity",
    "AI",
    "Renewable Energy & Climate Change",
    "Animal Adaptation",
    "Ecosystem Interactions"
]

# --- Topic Keywords ---
TOPIC_KEYWORDS = {
    "Neuroplasticity": ["neuroplasticity", "brain", "neurons", "synapse", "cortex", "plasticity"],
    "AI": ["ai", "artificial intelligence", "machine learning", "neural network", "transformer", "deep learning", "reinforcement learning", "large language model"],
    "Renewable Energy & Climate Change": [
        "climate change", "renewable energy", "solar", "wind", "greenhouse", "carbon", "global warming", "mitigation", "adaptation", "fossil fuel", "emissions"
    ],
    "Animal Adaptation": ["animal adaptation", "migration", "mimicry", "camouflage", "hibernation", "adaptation", "evolution"],
    "Ecosystem Interactions": [
        "ecosystem", "biodiversity", "food chain", "predator", "prey", "symbiosis", "deforestation", "habitat", "species interaction"
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
TOP_K = 3   # number of chunks to retrieve

logger.add("logs/sciencesage.log", rotation="10 MB", retention="10 days", level="INFO")
logger.info("Configuration loaded.")
