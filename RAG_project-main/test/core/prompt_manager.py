# -*- coding: utf-8 -*-
from app.core.templates import PROMPT_TEMPLATES, GLOBAL_RULES

class PromptManager:
    @staticmethod
    def build_prompt(scenario: str, context: str, query: str) -> str:
        template = PROMPT_TEMPLATES.get(scenario, PROMPT_TEMPLATES["general"])
        
        full_prompt = f"{template}\n\n{GLOBAL_RULES}\n\n【檢索知識庫內容】：\n{context}\n\n【使用者提問】：\n{query}"
        return full_prompt
