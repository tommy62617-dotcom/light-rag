# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.rag_service import generate_rag_response

app = FastAPI(title="RAG AI Microservice", version="1.0.0")

class ChatRequest(BaseModel):
    query: str
    scenario: Optional[str] = "general"
    model: Optional[str] = "llama3"

class ChatResponse(BaseModel):
    query: str
    scenario: str
    context_length: int
    response: str

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fastapi-rag-service"}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        result = await generate_rag_response(
            query=req.query,
            scenario=req.scenario,
            model=req.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)