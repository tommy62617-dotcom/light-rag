from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

# 啟用 CORS 跨來源資源共用，允許前端（如 Vite Port 5173）存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LightRAG 伺服器的查詢端點
LIGHTRAG_QUERY_URL = "http://localhost:9621/query"

# 定義前端傳進來的資料格式（支援 prompt 或 query 欄位）
class PromptPayload(BaseModel):
    prompt: str = ""
    query: str = ""

@app.post("/api/forward-to-lightrag")
async def forward_to_lightrag(payload: PromptPayload):
    # 兼容前端傳送 query 或 prompt 的欄位
    user_query = payload.query or payload.prompt
    
    # 按照 LightRAG 規定的 JSON 格式打包
    rag_body = {
        "query": user_query,
        "mode": "hybrid"  # 可選用 hybrid, local, global 等模式
    }
    
    # 使用 httpx 轉發 POST 請求給 LightRAG
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(LIGHTRAG_QUERY_URL, json=rag_body)
            response.raise_for_status()
            
            # 將 LightRAG 回傳的結果回傳給前端
            return response.json()
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"與 LightRAG 溝通失敗: {str(e)}")