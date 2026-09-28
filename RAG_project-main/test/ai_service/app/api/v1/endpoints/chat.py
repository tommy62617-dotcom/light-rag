# backend/app/api/v1/endpoints/chat.py
import time
from fastapi import APIRouter, HTTPException
from backend.ai_service.app.schemas.chat import ChatRequest, ChatResponse, SourceNode
from backend.ai_service.app.prompts.templates import PromptManager
from backend.ai_service.app.services.rag_service import call_lightrag_search, call_ollama_llm

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    
    try:
        # 1. 檢索 LightRAG[cite: 3]
        rag_data = await call_lightrag_search(query=request.query, scenario=request.scenario)
        context = rag_data.get("context", "")
        sources_raw = rag_data.get("sources", [])
        
        # 2. 套用專屬情境 Prompt[cite: 3]
        full_prompt = PromptManager.get_prompt(
            scenario=request.scenario,
            context=context,
            query=request.query
        )
        
        # 3. 生成回答[cite: 3]
        llm_answer = await call_ollama_llm(prompt=full_prompt)
        
        # 4. 整理引用來源與警示
        sources = [SourceNode(**s) for s in sources_raw]
        
        return ChatResponse(
            conversation_id=request.conversation_id or "session_default",
            answer=full_prompt,  # 開發階段可回傳 full_prompt 檢視組出的完整 Prompt
            scenario_used=request.scenario,
            warning_message="提示：請注意部分項目不符合規定" if request.scenario in ["sop_check", "prework_check"] else None,
            sources=sources,
            execution_time=round(time.time() - start_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系統處理失敗: {str(e)}")