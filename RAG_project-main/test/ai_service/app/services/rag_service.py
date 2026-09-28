# -*- coding: utf-8 -*-
import httpx
from typing import Dict, Any
from app.core.prompt_manager import PromptManager

LIGHTRAG_API_URL = "http://localhost:9621/query"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def call_lightrag_search(query: str, scenario: str = "general") -> Dict[str, Any]:
    payload = {
        "query": query,
        "mode": "hybrid"
    }
    print(" -> [Step 1] 正發送 LightRAG 檢索請求...", flush=True)
    timeout_config = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        response = await client.post(LIGHTRAG_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        context_text = data.get("response", "") or data.get("context", "")
        print(f" -> [Step 1 完成] 取得 Context 長度: {len(context_text)} 字", flush=True)
        return {"context": context_text}

async def call_ollama_generate(prompt: str, model: str = "llama3") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    print(f" -> [Step 2] 正發送 Ollama ({model}) 生成請求...", flush=True)
    timeout_config = httpx.Timeout(180.0, connect=10.0)
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        print(" -> [Step 2 完成] Ollama 回應生成完畢！", flush=True)
        return data.get("response", "")

async def generate_rag_response(query: str, scenario: str = "general", model: str = "llama3") -> Dict[str, Any]:
    search_res = await call_lightrag_search(query, scenario)
    context = search_res.get("context", "")
    
    full_prompt = PromptManager.build_prompt(
        scenario=scenario,
        context=context,
        query=query
    )
    
    llm_response = await call_ollama_generate(full_prompt, model=model)
    
    return {
        "query": query,
        "scenario": scenario,
        "context_length": len(context),
        "response": llm_response
    }
