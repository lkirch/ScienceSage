from sciencesage.config import (
    OPENAI_API_KEY, QDRANT_URL, QDRANT_COLLECTION,
    TOPICS, CHAT_MODEL, MAX_TOKENS, EMBEDDING_MODEL
)
from sciencesage.prompts import get_system_prompt, get_user_prompt
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny
from loguru import logger

client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)

def embed_text(text: str):
    """Embed text using OpenAI embedding API."""
    response = client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def retrieve_answer(query: str, topic: str, level: str):
    """
    Retrieve top context from Qdrant and generate answer.
    Returns:
        answer: str
        contexts: List[dict]
        references: List[dict]
    """
    logger.info(f"Retrieving answer for query='{query[:50]}...', topic='{topic}', level='{level}'")
    vector = embed_text(query)

    # Filter by topic
    query_filter = Filter(
        must=[
            FieldCondition(
                key="topics",
                match=MatchAny(any=[topic])
            )
        ]
    )

    results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=5,
        query_filter=query_filter,
    )

    if not results.points:
        logger.warning("No results returned from Qdrant.")
        return "Sorry, I couldn't find an answer for that.", [], []

    # Gather contexts and references
    contexts = []
    references = []
    for point in results.points:
        payload = point.payload
        text = payload.get("text", "")
        url = payload.get("source_url", "")
        contexts.append({
            "text": text,
            "source": payload.get("title", ""),
            "chunk": payload.get("chunk_index", 0),
            "score": point.score
        })
        references.append({
            "url": url,
            "snippet": text[:200],
            "score": point.score
        })

    # Generate answer using LLM and prompts from prompts.py
    context_texts = [c["text"] for c in contexts]
    system_prompt = get_system_prompt(topic, level)
    user_prompt = get_user_prompt(query, "\n".join(context_texts), level)
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=512 if MAX_TOKENS > 512 else MAX_TOKENS
    )
    answer = completion.choices[0].message.content.strip()
    return answer, contexts, references

def rephrase_query(query: str) -> str:
    """Rephrase a user query for clarity."""
    prompt = f"Rephrase the following question for clarity:\n\n{query}"
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=64
    )
    return completion.choices[0].message.content.strip()
