from sciencesage.config import (
    OPENAI_API_KEY, QDRANT_URL, QDRANT_COLLECTION,
    TOPICS, EMBED_MODEL, CHAT_MODEL
)
from openai import OpenAI
from qdrant_client import QdrantClient
from typing import Union, List, Tuple
from qdrant_client.models import Filter, FieldCondition, MatchAny
from sciencesage.prompts import get_system_prompt, get_user_prompt
import hashlib
from loguru import logger
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------
# Clients
# -------------------------
client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)

# -------------------------
# Precompute Topic Embeddings
# -------------------------
def embed_once(text: str):
    try:
        response = client.embeddings.create(model=EMBED_MODEL, input=text)
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to embed text: {text}, error: {e}")
        raise

logger.info("Precomputing topic embeddings...")
TOPIC_EMBEDDINGS = {topic: embed_once(topic) for topic in TOPICS}

# -------------------------
# Embedding Function
# -------------------------
def embed_text(text: str):
    """Embed text with OpenAI."""
    try:
        response = client.embeddings.create(model=EMBED_MODEL, input=text)
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise

# -------------------------
# Topic-Aware Re-Ranking
# -------------------------
def rerank_results(results, query_vector):
    """Re-rank Qdrant results using topic similarity as secondary score."""
    reranked = []
    query_vec_np = np.array(query_vector).reshape(1, -1)

    for r in results.points:
        payload = r.payload
        chunk_topics = payload.get("topics", [])
        max_topic_score = 0

        for t in chunk_topics:
            topic_vec = TOPIC_EMBEDDINGS.get(t)
            if topic_vec is not None:
                score = cosine_similarity(query_vec_np, np.array(topic_vec).reshape(1, -1))[0][0]
                max_topic_score = max(max_topic_score, score)

        combined_score = 0.8 * r.score + 0.2 * max_topic_score
        reranked.append((combined_score, r))

    reranked.sort(key=lambda x: x[0], reverse=True)
    for score, r in reranked:
        logger.debug(f"Re-ranked: id={r.id}, vec_score={r.score:.3f}, combined={score:.3f}")

    return reranked

# -------------------------
# Deduplicate and merge URLs
# -------------------------
def deduplicate_and_merge(results_with_scores):
    """
    Deduplicate by text content and merge reference URLs for same snippet.
    Returns list of dicts with 'text', 'source', 'chunk', 'score', 'urls'.
    """
    seen = {}
    for score, r in results_with_scores:
        payload = r.payload
        text = payload.get("text", "").strip()
        if not text:
            continue
        key = hashlib.md5(text.encode("utf-8")).hexdigest()
        source = payload.get("source", "unknown")
        chunk = payload.get("chunk_index", "?")
        urls = payload.get("reference_urls", [])

        if key not in seen:
            seen[key] = {
                "text": text,
                "source": source,
                "chunk": chunk,
                "score": score,
                "urls": urls.copy()
            }
        else:
            if score > seen[key]["score"]:
                seen[key]["score"] = score
            seen[key]["urls"] = list(set(seen[key]["urls"] + urls))
    return list(seen.values())

# -------------------------
# Main Retrieval Function
# -------------------------
def retrieve_answer(query: str, topic: Union[str, List[str]], level: str) -> Tuple[str, List[dict], List[dict]]:
    """
    Retrieve top context from Qdrant and generate answer with confidence scores.
    Returns:
        answer: str
        contexts: List[dict] -> {'text','source','chunk','score'}
        references: List[dict] -> {'url','snippet','score'}
    """
    logger.info(f"Retrieving answer for query='{query[:50]}...', topic='{topic}', level='{level}'")

    vector = embed_text(query)

    query_filter = None
    if topic:
        selected_topics = topic if isinstance(topic, list) else [topic]
        query_filter = Filter(must=[FieldCondition(key="topics", match=MatchAny(any=selected_topics))])

    results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=10,
        query_filter=query_filter,
    )

    if not results.points:
        logger.warning("No results returned from Qdrant.")
        return "I don’t know based on the available information.", [], []

    reranked = rerank_results(results, vector)
    deduped = deduplicate_and_merge(reranked)
    top_results = deduped[:5]

    contexts = []
    references = []
    for r in top_results:
        contexts.append({
            "text": r["text"],
            "source": r["source"],
            "chunk": r["chunk"],
            "score": r["score"]
        })
        for url in r["urls"]:
            references.append({
                "url": url,
                "snippet": r["text"][:150] + "...",
                "score": r["score"]
            })

    context_text = "\n\n".join([
        (
            f"[Source: <a href='{r['urls'][0]}' target='_blank'>{get_domain(r['urls'][0])}</a> | chunk {c['chunk']}] {c['text']}"
            if r.get("urls") else
            f"[Source: {c['source']} | chunk {c['chunk']}] {c['text']}"
        )
        for c, r in zip(contexts, top_results)
    ])
    if not context_text:
        context_text = "No additional context found in the database."
        logger.warning("No relevant context found above threshold.")

    system_prompt = get_system_prompt(topic, level)
    user_prompt = get_user_prompt(query, context_text)

    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        answer = completion.choices[0].message.content
        logger.info("Answer generated successfully.")
    except Exception as e:
        logger.error(f"OpenAI completion failed: {e}")
        answer = "I don’t know based on the available information."

    return answer, contexts, references

# -------------------------
# Rephrase Query Function
# -------------------------
def rephrase_query(query: str) -> str:
    """
    Use the LLM to rewrite the user query in a clearer or alternative way
    to improve retrieval results.
    """
    system_prompt = (
        "You are a helpful assistant that rewrites science questions "
        "for better search and retrieval. Keep the meaning intact but make it concise."
    )
    user_prompt = f"Original question: {query}\n\nPlease rewrite it for better search:"

    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        new_query = completion.choices[0].message.content.strip()
        if not new_query:
            logger.warning("Rephrase returned empty, using original query.")
            return query
        logger.info(f"Query rephrased: {new_query}")
        return new_query
    except Exception as e:
        logger.error(f"Rephrase query failed: {e}")
        return query

def get_domain(url):
    from urllib.parse import urlparse
    try:
        netloc = urlparse(url).netloc
        return netloc.replace("www.", "") if netloc else url
    except Exception:
        return url
