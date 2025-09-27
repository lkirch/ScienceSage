from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sciencesage.retrieval_system import retrieve_answer
from sciencesage.config import TOP_K

app = FastAPI(title="ScienceSage RAG API")

class RAGRequest(BaseModel):
    query: str
    topic: str = "Space Exploration"
    level: str = "middle_school"
    top_k: int = TOP_K

class RAGResponse(BaseModel):
    answer: str
    context_chunks: list
    sources: list

@app.post("/rag", response_model=RAGResponse)
def rag_endpoint(request: RAGRequest):
    try:
        result = retrieve_answer(
            query=request.query,
            topic=request.topic,
            level=request.level,
            top_k=request.top_k
        )
        return RAGResponse(
            answer=result.get("answer", ""),
            context_chunks=result.get("context_chunks", []),
            sources=result.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))