"""
Config package initializer.
Provides easy access to environment-based config and project constants.
"""

from .config import *      # QDRANT_URL, OPENAI_API_KEY, COLLECTION_NAME, etc.
from .constants import *   # EMBEDDING_DIM, DISTANCE_METRIC, CHUNK_SIZE, etc.