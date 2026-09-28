# -*- coding: utf-8 -*-
import asyncio
from app.services.rag_service import generate_rag_response

async def main():
    print("=== [開始執行 RAG 端到端測試] ===", flush=True)
    test_query = "雇主對於高空作業有哪些安全防護規定？"
    test_scenario = "general"
    
    try:
        result = await generate_rag_response(
            query=test_query,
            scenario=test_scenario,
            model="llama3"
        )
        q = result["query"]
        s = result["scenario"]
        c_len = result["context_length"]
        resp = result["response"]
        
        print("\n=== [測試結果] ===", flush=True)
        print(f"使用者提問: {q}")
        print(f"情境模組: {s}")
        print(f"Context 長度: {c_len} 字")
        print("\nLLM 生成回應:")
        print(resp)
    except Exception as e:
        print(f"\n[測試失敗] 發生錯誤: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())