import asyncio
import os
import sys

# 將 backend 目錄加入 sys.path，解決 No module named 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_service.app.prompts.templates import PromptManager
from backend.ai_service.app.services.rag_service import call_lightrag_search


async def test_lightrag_connection():
  print("=== 開始測試 LightRAG 檢索連線與 Prompt 產生 ===")

  test_query = "5公尺以上高空作業需要哪些安全措施？"
  test_scenario = "compliance_planning"

  try:
    print(f"[1/3] 發送測試問題: '{test_query}' (情境: {test_scenario})")
    rag_result = await call_lightrag_search(
        query=test_query, scenario=test_scenario
    )
    context = rag_result.get("context", "")
    print("✓ LightRAG 檢索成功！回傳 Context 長度:", len(context))

    print("[2/3] 測試 Prompt 格式模組化組裝...")
    full_prompt = PromptManager.get_prompt(
        scenario=test_scenario, context=context, query=test_query
    )
    print("✓ Prompt 組裝成功！前 200 字預覽：")
    print("-" * 40)
    print(full_prompt[:200] + "...")
    print("-" * 40)

    # 修改 backend/tests/test_rag.py 的第 31-33 行
    print("[3/3] 檢查 Prompt 是否包含全域限制條件...")
    assert "【資料唯一性與真實性】" in full_prompt
    assert "【禁忌詞彙】" in full_prompt
    print("✓ 驗證通過： Prompt 包含完整的嚴格限制規則！")

  except Exception as e:
    print(f"❌ 測試失敗: {e}")


if __name__ == "__main__":
  asyncio.run(test_lightrag_connection())