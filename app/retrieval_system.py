#!/usr/bin/env python3

import os
from .config import OPENAI_API_KEY, QDRANT_URL, QDRANT_COLLECTION
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from .prompts import get_system_prompt, get_user_prompt

client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)

def embed_text(text: str):
    """Embed text with OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def retrieve_answer(query: str, topic: str, level: str):
    """Retrieve top context from Qdrant and generate GPT answer."""
    vector = embed_text(query)

    results = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=3,
        query_filter=Filter(
            must=[FieldCondition(key="topic", match=MatchValue(value=topic))]
        )
    )

    contexts = [p.payload.get("text") for p in results.points]
    context_text = "\n\n".join(contexts) if contexts else "No additional context found."

    system_prompt = get_system_prompt(topic, level)
    user_prompt = get_user_prompt(query, context_text)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    answer = completion.choices[0].message.content
    return answer, contexts
