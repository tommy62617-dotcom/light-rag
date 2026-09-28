# backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    query: str = Field(..., description="使用者輸入的問題", example="我們要新增一處高於5公尺的鋼構施工作業區，需要哪些安全措施？")
    scenario: str = Field(..., description="情境標籤: compliance_planning / sop_check / incident_analysis / prework_check", example="compliance_planning")
    conversation_id: Optional[str] = Field(None, description="對話 Session ID")

class SourceNode(BaseModel):
    source_title: str = Field(..., description="引用法規或內部文件名稱", example="高架作業勞工保護措施標準 第3條")
    file_id: Optional[str] = Field(None, description="對應文件編號", example="公司SOP-5-2")

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str = Field(..., description="LLM 生成的 Markdown 排版結果")
    scenario_used: str
    warning_message: Optional[str] = Field(None, description="開工警示或主要缺口提示")
    sources: List[SourceNode] = Field(default=[], description="引用來源標籤清單")
    execution_time: float = Field(..., description="後端處理耗時（秒）")