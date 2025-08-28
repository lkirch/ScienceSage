import os
from dotenv import load_dotenv 

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