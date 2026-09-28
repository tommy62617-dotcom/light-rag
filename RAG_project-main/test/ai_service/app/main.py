from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.ai_service.app.api.v1.endpoints import chat

app = FastAPI(
    title="職安智腦 API 服務",
    description="提供建置合規規劃、SOP合規檢查、事故原因分析、作業前安全檢核等四大情境介面",
    version="1.0.0"
)

# 跨域 CORS 設定 (允許 Vue 3 前端連線)[cite: 1]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開發階段允許所有來源，部署時可再縮小範圍
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 Chat 路由
app.include_router(chat.router, prefix="/api/v1", tags=["職安智腦對話服務"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)