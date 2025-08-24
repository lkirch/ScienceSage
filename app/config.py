import os
from dotenv import load_dotenv 

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Qdrant collection name
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