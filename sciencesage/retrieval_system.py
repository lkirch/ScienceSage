from sciencesage.config import OPENAI_API_KEY, QDRANT_URL, QDRANT_COLLECTION, CHAT_MODEL
from openai import OpenAI
from qdrant_client import QdrantClient
from typing import Union, List
from qdrant_client.models import Filter, FieldCondition, MatchAny
from sciencesage.prompts import get_system_prompt, get_user_prompt
from loguru import logger

client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)

def embed_text(text: str):
    """Embed text with OpenAI."""
    logger.debug(f"Embedding text: {text[:50]}...")  # Log first 50 chars
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        logger.debug("Embedding successful")
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise

def retrieve_answer(query: str, topic: Union[str, List[str]], level: str):
    """Retrieve top context from Qdrant and generate answer."""
    logger.info(f"Retrieving answer for query='{query[:50]}...', topic='{topic}', level='{level}'")

    try:
        vector = embed_text(query)
        logger.debug(f"Query vector (len={len(vector)}): {vector}")  # Log the query vector
    except Exception as e:
        logger.error(f"Failed to embed query: {e}")
        raise

    # Normalize topic into a list (MatchAny expects a list)
    if topic:
        selected_topics = topic if isinstance(topic, list) else [topic]
        query_filter = Filter(
            must=[FieldCondition(key="topics", match=MatchAny(any=selected_topics))]
        )
    else:
        # No topic selected, don't filter at all
        query_filter = None

    try:
        results = qdrant.query_points(
            collection_name=QDRANT_COLLECTION,
            query=vector,
            limit=5,
            query_filter=query_filter,
        )
        logger.debug(f"Qdrant returned {len(results.points)} points")
    except Exception as e:
        logger.error(f"Qdrant query failed: {e}")
        raise

    contexts = []
    references = []

    for p in results.points:
        payload = p.payload
        text = payload.get("text", "")
        source = payload.get("source", "unknown")
        chunk = payload.get("chunk_index", "?")
        urls = payload.get("reference_urls", [])

        # Store context with metadata for prompting
        contexts.append(f"[{source}:{chunk}] {text}")

        # Collect URLs for display at bottom
        if urls:
            references.extend(urls)

    context_text = "\n\n".join(contexts) if contexts else "No additional context found in the database."

    system_prompt = get_system_prompt(topic, level)
    user_prompt = get_user_prompt(query, context_text)

    logger.debug(f"Context sent to GPT:\n{context_text}")
    logger.debug(f"Full user prompt:\n{user_prompt}")

    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
        )
        logger.info(f"Answer generated using model={CHAT_MODEL}")
    except Exception as e:
        logger.error(f"OpenAI completion failed: {e}")
        raise

    answer = completion.choices[0].message.content
    return answer, contexts, references
