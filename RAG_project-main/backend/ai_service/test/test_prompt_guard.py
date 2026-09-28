import asyncio
import unittest

from app.services import rag_service


class PromptGuardTests(unittest.TestCase):
    def test_empty_context_returns_refusal_without_llm(self):
        async def run_test():
            async def fake_search(*args, **kwargs):
                return {"context": ""}

            async def fake_llm(*args, **kwargs):
                raise AssertionError("LLM should not be called when context is empty")

            original_search = rag_service.call_lightrag_search
            original_llm = rag_service.call_ollama_generate
            rag_service.call_lightrag_search = fake_search
            rag_service.call_ollama_generate = fake_llm
            try:
                result = await rag_service.generate_rag_response(
                    "發生事故了，請分析原因",
                    "incident_analysis",
                    "llama3",
                )
                self.assertIn("無法依據現有知識庫", result["response"])
            finally:
                rag_service.call_lightrag_search = original_search
                rag_service.call_ollama_generate = original_llm

        asyncio.run(run_test())

    def test_lightrag_default_no_context_message_returns_refusal(self):
        """測試 LightRAG 返回預設「無法回答」訊息時的拒答行為"""
        async def run_test():
            async def fake_search(*args, **kwargs):
                # 模擬 LightRAG 返回的預設無法回答訊息
                return {"context": "Sorry, I'm not able to provide an answer to that question.[no-context]"}

            async def fake_llm(*args, **kwargs):
                raise AssertionError("LLM should not be called when LightRAG returns no-context marker")

            original_search = rag_service.call_lightrag_search
            original_llm = rag_service.call_ollama_generate
            rag_service.call_lightrag_search = fake_search
            rag_service.call_ollama_generate = fake_llm
            try:
                result = await rag_service.generate_rag_response(
                    "測試查詢",
                    "compliance_planning",
                    "llama3",
                )
                # 應該返回中文拒答訊息，而不是模板內容
                self.assertIn("無法依據現有知識庫", result["response"])
                self.assertNotIn("I'm a digital", result["response"])
            finally:
                rag_service.call_lightrag_search = original_search
                rag_service.call_ollama_generate = original_llm

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
