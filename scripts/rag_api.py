from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchRequest
from sciencesage.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_COLLECTION,
    EMBED_MODEL,
    OPENAI_API_KEY,
)
import os

app = FastAPI(title="ScienceSage RAG API")

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", OPENAI_API_KEY))
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

class RAGRequest(BaseModel):
    query: str
    top_k: int = 5
    filter_topic: Optional[str] = None

class RAGResponse(BaseModel):
    answer: str
    context_chunks: List[dict]
    sources: List[str]

def get_query_embedding(query: str) -> List[float]:
    response = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    )
    return response.data[0].embedding

def search_qdrant(embedding: List[float], top_k: int = 5, filter_topic: Optional[str] = None):
    if filter_topic:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="topic",
                    match=MatchValue(value=filter_topic)
                )
            ]
        )
    else:
        search_filter = None
    hits = qdrant.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=embedding,
        limit=top_k,
        search_filter=search_filter,
        with_payload=True
    )
    return hits

def build_prompt(query: str, context_chunks: List[dict]) -> str:
    context = "\n\n".join(
        f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(context_chunks)
    )
    prompt = (
        f"Answer the following question using only the provided context. "
        f"List sources as [number] if used.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        f"Answer:"
    )
    return prompt

def generate_answer(prompt: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()

@app.post("/rag", response_model=RAGResponse)
def rag_endpoint(request: RAGRequest):
    embedding = get_query_embedding(request.query)
    hits = search_qdrant(embedding, top_k=request.top_k, filter_topic=request.filter_topic)
    context_chunks = [hit.payload for hit in hits]
    sources = []
    for i, chunk in enumerate(context_chunks):
        src = chunk.get("url") or chunk.get("doc_id") or f"chunk_{chunk.get('id')}"
        sources.append(f"[{i+1}] {src}")
    prompt = build_prompt(request.query, context_chunks)
    answer = generate_answer(prompt)
    return RAGResponse(
        answer=answer,
        context_chunks=context_chunks,
        sources=sources
    )

@app.get("/")
def root():
    return {"message": "ScienceSage RAG API. POST /rag with your query."}