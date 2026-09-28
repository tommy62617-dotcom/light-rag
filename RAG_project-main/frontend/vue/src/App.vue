<template>
  <div class="app-viewport">
    <!-- 1. 左側 slim 導覽列 -->
    <aside class="sidebar">
      <div class="brand-icon">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      </div>

      <nav class="nav-menu">
        <button
          v-for="item in menuItems"
          :key="item.id"
          @click="toggleDrawer(item.id)"
          :class="['nav-item', { active: activeDrawer === item.id }]"
          :title="item.title"
        >
          {{ item.icon }}
        </button>
      </nav>
    </aside>

    <!-- 2. 抽屜區塊 -->
    <transition name="drawer">
      <section v-if="activeDrawer" class="drawer">
        <header class="drawer-header">
          <h3>{{ currentDrawerTitle }}</h3>
          <button @click="activeDrawer = null" class="close-btn">✕</button>
        </header>

        <div v-if="activeDrawer === 'search'" class="drawer-body">
          <div class="form-group">
            <label class="form-label">搜尋歷史諮詢</label>
            <input
              type="text"
              placeholder="輸入關鍵字搜尋紀錄..."
              class="form-input"
            />
          </div>
        </div>

        <div v-if="activeDrawer === 'modules'" class="drawer-body">
          <div class="form-group">
            <label class="form-label">標準模組庫</label>
            <p class="form-hint">包含內部 SOP 規範與各項職安標準文件。</p>
          </div>
        </div>
      </section>
    </transition>

    <!-- 3. 主要工作區 -->
    <main class="main-stage">
      <header class="top-nav">
        <div class="header-title">
          <h2>數位職安顧問</h2>
          <span class="sub-title">分流專業諮詢系統</span>
        </div>

        <!-- 頂部四大對話框切換頁籤 -->
        <div class="mode-tabs">
          <button
            v-for="mode in topics"
            :key="mode.id"
            @click="switchTopic(mode.id)"
            :class="['tab-btn', { active: activeTopicId === mode.id }]"
          >
            <span class="tab-icon">{{ mode.icon }}</span>
            <span class="tab-label">{{ mode.title }}</span>
          </button>
        </div>
      </header>

      <div class="workspace">
        <!-- 對話視圖 -->
        <div class="chat-wrapper">
          <div class="chat-feed" ref="chatFeedRef">
            <!-- 無訊息時顯示提示卡片 -->
            <div
              v-if="currentMessages.length === 0 && !isLoading"
              class="welcome-card"
            >
              <div class="welcome-icon-circle">
                {{ currentTopic.icon }}
              </div>
              <div class="welcome-info">
                <h3>{{ currentTopic.title }} 頻道</h3>
                <p>{{ currentTopic.desc }}</p>
              </div>
            </div>

            <!-- 對話紀錄 -->
            <div
              v-for="(msg, idx) in currentMessages"
              :key="idx"
              :class="['chat-item', msg.role]"
            >
              <div class="author-tag">
                {{
                  msg.role === "user" ? "提問者" : currentTopic.title + " 顧問"
                }}
              </div>
              <div class="bubble">
                <div
                  class="text-content"
                  v-html="formatResponse(msg.text)"
                ></div>
              </div>
            </div>

            <div v-if="isLoading" class="loading-indicator">
              資料處理與比對中，請稍候...
            </div>
          </div>

          <!-- 底部輸入區域 -->
          <div class="chat-input-area">
            <!-- 選擇檔案後的預覽卡片 -->
            <div v-if="selectedFile" class="file-preview-tag">
              <span class="file-icon">📎</span>
              <span class="file-name" :title="selectedFile.name">{{
                selectedFile.name
              }}</span>
              <button @click="removeSelectedFile" class="remove-file-btn">
                ✕
              </button>
            </div>

            <div class="input-container">
              <!-- 隱藏的 File Input -->
              <input
                type="file"
                ref="fileInputRef"
                @change="handleFileSelect"
                style="display: none"
                accept=".txt,.pdf,.docx,.doc,.md,.csv,.xlsx,.xls,.json,.html"
              />

              <!-- ➕ 加號上傳按鈕 -->
              <button
                @click="triggerFileInput"
                class="attach-btn"
                title="上傳檔案/文件"
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>

              <input
                ref="queryInputRef"
                type="text"
                v-model="userQuery"
                @keyup.enter="runQuery"
                :placeholder="currentTopic.placeholder"
              />
              <button
                @click="runQuery"
                :disabled="isLoading"
                class="send-action"
              >
                發送
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, reactive, nextTick } from "vue";

const activeDrawer = ref(null);

const menuItems = [
  { id: "search", icon: "🔍", title: "歷史紀錄" },
  { id: "modules", icon: "📁", title: "標準模組" },
];

const currentDrawerTitle = computed(() => {
  const item = menuItems.find((m) => m.id === activeDrawer.value);
  return item ? item.title : "";
});

/* === 四大專業主題對話框配置 === */
const topics = [
  {
    id: "compliance",
    icon: "🏗️",
    title: "建置合規規劃",
    desc: "請在此輸入建置階段的規劃需求或欲比對之法規項目。",
    placeholder: "請輸入建置合規規劃相關問題...",
  },
  {
    id: "sop",
    icon: "📋",
    title: "SOP 合規檢查",
    desc: "請在此貼上或透過加號按鈕上傳需檢查之 SOP 檔案。",
    placeholder: "請輸入文字或點擊 ＋ 號上傳 SOP 檔案...",
  },
  {
    id: "accident",
    icon: "🔍",
    title: "事故原因分析",
    desc: "請在此輸入現場事故經過或情境資訊。",
    placeholder: "請輸入事故發生的詳細經過與現場狀況...",
  },
  {
    id: "precheck",
    icon: "✅",
    title: "作業前安全檢核",
    desc: "請在此輸入作業類型以產出對應之現場檢核項目。",
    placeholder: "請輸入預計執行的作業名稱（如：動火、吊掛、高架）...",
  },
];

const activeTopicId = ref("compliance");
const currentTopic = computed(() =>
  topics.find((t) => t.id === activeTopicId.value)
);

const chatHistories = reactive({
  compliance: [],
  sop: [],
  accident: [],
  precheck: [],
});

const currentMessages = computed(() => chatHistories[activeTopicId.value]);

const userQuery = ref("");
const isLoading = ref(false);
const chatFeedRef = ref(null);
const queryInputRef = ref(null);

/* === 檔案選擇邏輯 === */
const fileInputRef = ref(null);
const selectedFile = ref(null);

const triggerFileInput = () => {
  if (fileInputRef.value) fileInputRef.value.click();
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
  }
};

const removeSelectedFile = () => {
  selectedFile.value = null;
  if (fileInputRef.value) fileInputRef.value.value = "";
};

const toggleDrawer = (id) => {
  activeDrawer.value = activeDrawer.value === id ? null : id;
};

const switchTopic = (topicId) => {
  activeTopicId.value = topicId;
  userQuery.value = "";
  nextTick(() => {
    if (queryInputRef.value) queryInputRef.value.focus();
  });
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatFeedRef.value) {
      chatFeedRef.value.scrollTop = chatFeedRef.value.scrollHeight;
    }
  });
};

const formatResponse = (text) => {
  if (!text) return "";
  return text.replace(/\n/g, "<br>");
};

/* === 本地端防錯引導邏輯 === */
const generateGuideResponse = (topicId, query) => {
  switch (topicId) {
    case "compliance":
      return `【建置合規規劃 - 輸入引導】\n您輸入的內容「${query}」資訊較少。\n\n請提供您預計建置的「場域類型或設備」（例如：高架作業區、化學品儲槽），我將為您整理對應的法定防護設施清單與合規要求。`;
    case "sop":
      return `【SOP 合規檢查 - 輸入引導】\n您輸入的內容「${query}」資訊較少。\n\n您可以點擊對話框旁的「＋」號上傳檔案，或直接「貼上您的 SOP 內文」，我將為您比對最新職業安全衛生法規。`;
    case "accident":
      return `【事故原因分析 - 輸入引導】\n您輸入的內容「${query}」資訊較少。\n\n請簡述「現場事故經過」（如：人員自施工架跌落），我將為您進行 RCA 根本原因分析並提供改善對策。`;
    case "precheck":
      return `【作業前安全檢核 - 輸入引導】\n您輸入的內容「${query}」資訊較少。\n\n請輸入「今日預計執行的作業種類」（如：電焊切割、局限空間作業），我將為您生成開工前標準 Checklist。`;
  }
};

/* === 發送諮詢對話 === */
const runQuery = async () => {
  if ((!userQuery.value.trim() && !selectedFile.value) || isLoading.value)
    return;

  const queryText = userQuery.value.trim();
  const currentTopicId = activeTopicId.value;
  const attachedFile = selectedFile.value;

  // 1. 將使用者輸入寫入對話，如果有夾帶檔案一併顯示
  let userDisplayMsg = queryText;
  if (attachedFile) {
    userDisplayMsg =
      `[已夾帶檔案：${attachedFile.name}]\n` +
      (queryText || "請協助分析此檔案。");
  }

  chatHistories[currentTopicId].push({ role: "user", text: userDisplayMsg });

  // 清空輸入框與夾帶檔案
  userQuery.value = "";
  selectedFile.value = null;
  if (fileInputRef.value) fileInputRef.value.value = "";

  isLoading.value = true;
  scrollToBottom();

  // 2. 本地無意義字串引導（如果沒傳檔案且字數過少）
  if (!attachedFile) {
    const isInvalid =
      queryText.length < 3 ||
      /^\d+$/.test(queryText) ||
      /^[a-zA-Z]+$/.test(queryText);
    if (isInvalid) {
      setTimeout(() => {
        isLoading.value = false;
        const guideMsg = generateGuideResponse(currentTopicId, queryText);
        chatHistories[currentTopicId].push({
          role: "assistant",
          text: guideMsg,
        });
        scrollToBottom();
      }, 400);
      return;
    }
  }

  // 3. 正式傳送至 FastAPI 後端 API
  try {
    const response = await fetch("http://localhost:8000/api/forward-to-lightrag", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: queryText || (attachedFile ? `請分析檔案：${attachedFile.name}` : "請協助分析")
      })
    });

    if (!response.ok) {
      throw new Error(`伺服器回應錯誤，狀態碼: ${response.status}`);
    }

    const data = await response.json();

    // 取得後端回傳的解答內容
    const aiReply = data.response || "（系統未回傳有效內容）";

    chatHistories[currentTopicId].push({
      role: "assistant",
      text: aiReply,
    });

    isLoading.value = false;
    scrollToBottom();

  } catch (error) {
    console.error("Chat API Error:", error);
    chatHistories[currentTopicId].push({
      role: "assistant",
      text: "⚠️ 系統連線異常，請確認 FastAPI 後端與 LightRAG 是否已正常啟動。",
    });
    isLoading.value = false;
    scrollToBottom();
  }
};
</script>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  background-color: #f8fafc !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #1e293b;
}

.app-viewport {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  background-color: #f8fafc;
  overflow: hidden;
}

/* 1. Sidebar */
.sidebar {
  width: 48px;
  height: 100vh;
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  z-index: 20;
  box-sizing: border-box;
}
.brand-icon {
  color: #2563eb;
  margin-bottom: 20px;
}
.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  align-items: center;
}
.nav-item {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s ease;
}
.nav-item:hover {
  background: #f1f5f9;
  color: #0f172a;
}
.nav-item.active {
  background: #eff6ff;
  color: #2563eb;
}

/* 2. Drawer */
.drawer {
  width: 280px;
  height: 100vh;
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 18px;
  box-sizing: border-box;
  z-index: 10;
}
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.drawer-header h3 {
  font-size: 13px;
  font-weight: 600;
  margin: 0;
  color: #0f172a;
}
.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}
.form-label {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}
.form-hint {
  font-size: 11px;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.form-input {
  width: 100%;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #0f172a;
  padding: 8px 10px;
  font-size: 12px;
  box-sizing: border-box;
  outline: none;
}
.form-input:focus {
  border-color: #2563eb;
  background: #ffffff;
}

/* 3. Main Stage */
.main-stage {
  flex: 1;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
  overflow: hidden;
}
.top-nav {
  height: 52px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: #ffffff;
  flex-shrink: 0;
}
.header-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.header-title h2 {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  color: #0f172a;
}
.sub-title {
  font-size: 11px;
  color: #64748b;
}

.mode-tabs {
  display: flex;
  gap: 6px;
  background: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: transparent;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}
.tab-btn:hover {
  color: #0f172a;
}
.tab-btn.active {
  background: #ffffff;
  color: #2563eb;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 4. Chat Workspace */
.workspace {
  flex: 1;
  height: calc(100vh - 52px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-wrapper {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  max-width: 860px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  overflow: hidden;
}

.chat-feed {
  flex: 1;
  overflow-y: auto !important;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-right: 8px;
  scroll-behavior: smooth;
  justify-content: flex-start;
}

.welcome-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  margin: auto;
  max-width: 480px;
  width: 100%;
  box-sizing: border-box;
}
.welcome-icon-circle {
  width: 44px;
  height: 44px;
  background: #eff6ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.welcome-card h3 {
  font-size: 14px;
  margin: 0;
  color: #0f172a;
  font-weight: 600;
}
.welcome-card p {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.chat-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}
.author-tag {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
}
.chat-item.user .author-tag {
  color: #2563eb;
  text-align: right;
}

.bubble {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 16px;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
.chat-item.user .bubble {
  background: #1e293b;
  color: #f8fafc;
  border-color: #1e293b;
  text-align: left;
}

.loading-indicator {
  font-size: 12px;
  color: #64748b;
  text-align: center;
  padding: 10px;
}

/* 5. Input Area */
.chat-input-area {
  padding-top: 10px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 夾帶檔案的預覽卡片 */
.file-preview-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 4px 10px;
  border-radius: 6px;
  width: fit-content;
  font-size: 12px;
  color: #1e40af;
}
.file-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}
.remove-file-btn {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 12px;
  padding: 0 2px;
}
.remove-file-btn:hover {
  color: #1d4ed8;
}

.input-container {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 6px 8px 6px 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* ➕ 加號上傳按鈕樣式 */
.attach-btn {
  background: transparent;
  border: none;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.attach-btn:hover {
  background: #f1f5f9;
  color: #2563eb;
}

.input-container input[type="text"] {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #0f172a;
  font-size: 13px;
}
.input-container input::placeholder {
  color: #94a3b8;
}

.send-action {
  background: #0f172a;
  color: #ffffff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease;
}
.send-action:hover {
  background: #1e293b;
}

/* Custom Scrollbar */
.chat-feed::-webkit-scrollbar,
.drawer-body::-webkit-scrollbar {
  width: 6px;
}
.chat-feed::-webkit-scrollbar-thumb,
.drawer-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
.chat-feed::-webkit-scrollbar-track,
.drawer-body::-webkit-scrollbar-track {
  background: transparent;
}
</style>