from typing import List, Optional
from loguru import logger
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

from sciencesage.config import (
    CHAT_MODEL,
    TOP_K,
    EMBEDDING_MODEL,
    QDRANT_URL,
    QDRANT_COLLECTION,
    LEVELS,
    SIMILARITY_THRESHOLD,
)
from sciencesage.prompts import get_system_prompt, get_user_prompt


# -------- Initialization --------
logger.info("Initializing Retrieval System...")
client = OpenAI()
embedder = SentenceTransformer(EMBEDDING_MODEL)
qdrant = QdrantClient(url=QDRANT_URL)


# -------- Retrieval Function --------
def retrieve_context(
    query: str,
    top_k: int = TOP_K,
    topic: Optional[str] = None,
) -> List[dict]:
    """
    Retrieve top_k most relevant chunks from Qdrant for a given query.

    Returns list of dicts with keys: text, source_url, chunk_id, score
    """
    query_embedding = embedder.encode(query).tolist()

    # Build metadata filter (only topic, not level)
    qdrant_filter = None
    #if topic:
    #    qdrant_filter = Filter(
    #        must=[FieldCondition(key="topic", match=MatchValue(value=topic))]
    #    )

    search_result = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_embedding,
        limit=top_k,
        query_filter=qdrant_filter,
        with_payload=True,
        score_threshold=SIMILARITY_THRESHOLD,
    )

    chunks = []
    for i, hit in enumerate(search_result.points):
        chunks.append({
            "text": hit.payload["text"],
            "source_url": hit.payload.get("source_url", "unknown"),
            "chunk_id": hit.payload.get("chunk_id", i),
            "score": hit.score,
        })

    logger.debug(f"Retrieved {len(chunks)} chunks (top_k={top_k}, topic={topic})")
    return chunks


# -------- Generation Function --------
def generate_answer(query: str, context_chunks: List[dict], level: str, topic: str) -> str:
    """
    Generate an answer from the chat model given a query and retrieved context.
    """
    # Format context with citations
    context_text = "\n\n".join(
        f"[{i+1}] {chunk['text']} (Source: {chunk['source_url']}, Chunk: {chunk['chunk_id']})"
        for i, chunk in enumerate(context_chunks)
    )

    system_prompt = get_system_prompt(topic=topic, level=level)
    user_prompt = get_user_prompt(query=query, context_text=context_text, level=level)

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()
    logger.debug(f"Generated answer length: {len(answer)} characters")
    return answer


# -------- High-Level RAG Function --------
def retrieve_answer(
    query: str,
    topic: str,
    level: str = "College",
    top_k: int = TOP_K,
) -> str:
    """
    Full RAG pipeline: retrieve + generate
    """
    logger.info(f"Processing query: '{query}' | topic={topic} | level={level}")
    context_chunks = retrieve_context(query, top_k=top_k, topic=topic)

    if not context_chunks:
        logger.warning("No context retrieved — returning fallback response.")
        return "I don’t know based on the available information."

    return generate_answer(query, context_chunks, level, topic)
