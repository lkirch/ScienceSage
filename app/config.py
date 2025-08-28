import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = "scientific_concepts"

# Topics & levels
TOPICS = [
    "Neuroplasticity",
    "AI",
    "Renewable Energy & Climate Change",
    "Animal Adaptation",
    "Ecosystem Interactions"
]

LEVELS = ["Middle School", "College", "Advanced"]

logger.add("logs/sciencesage.log", rotation="10 MB", retention="10 days", level="INFO")
logger.info("Configuration loaded.")

if not os.getenv("QDRANT_URL"):
    logger.warning("QDRANT_URL not set, using default http://localhost:6333")
logger.info(f"Qdrant URL: {QDRANT_URL}, Collection: {QDRANT_COLLECTION}")