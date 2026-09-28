# -*- coding: utf-8 -*-
import httpx
from typing import Dict, Any
from app.core.templates import PromptManager

# 外部微服務連線位址設定
LIGHTRAG_API_URL = "http://localhost:9621/query"
OLLAMA_API_URL = "http://localhost:11434/api/generate"


async def call_lightrag_search(query: str, scenario: str = "compliance_planning") -> Dict[str, Any]:
    """
    呼叫 LightRAG API 進行知識庫向量與知識圖譜檢索
    """
    payload = {
        "query": query,
        "mode": "hybrid"  # 使用混合檢索模式以涵蓋實體與全文資訊
    }
    timeout_config = httpx.Timeout(60.0, connect=10.0)
    
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        response = await client.post(LIGHTRAG_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # 提取檢索到的 Context 內容
        context_text = data.get("response", "") or data.get("context", "")
        return {"context": context_text}


async def call_ollama_generate(prompt: str, model: str = "llama3") -> str:
    """
    呼叫 Ollama API 進行 LLM 文字生成
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2  # 低 Temperature 以保持回答穩定與嚴謹
        }
    }
    timeout_config = httpx.Timeout(180.0, connect=10.0)
    
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        response = await client.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


async def generate_rag_response(query: str, scenario: str = "compliance_planning", model: str = "llama3") -> Dict[str, Any]:
    """
    RAG 主流程控制：檢索 -> 組裝 Prompt -> LLM 推理生成
    """
    # 1. 執行 LightRAG 檢索
    search_res = await call_lightrag_search(query, scenario)
    context = search_res.get("context", "")
    
    # 2. 依據情境使用 PromptManager 組裝 Prompt
    full_prompt = PromptManager.get_prompt(
        scenario=scenario,
        context=context,
        query=query
    )
    
    # 3. 呼叫 LLM 進行推理
    llm_response = await call_ollama_generate(full_prompt, model=model)
    
    # 4. 回傳格式化結果
    return {
        "query": query,
        "scenario": scenario,
        "context_length": len(context),
        "response": llm_response
    }