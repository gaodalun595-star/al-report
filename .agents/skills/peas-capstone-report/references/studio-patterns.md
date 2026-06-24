# Agent Studio 左欄↔右欄組裝規則

## 典型資料流（報告用白話）

1. **左欄自訂頁**收集使用者輸入（表單、按鈕、slider…）
2. 部分頁面把狀態整理成**一段文字摘要**（報告稱「整理成 Agent 摘要」；技術上常見 `format_extra_context` 或 session 組字串）
3. **右欄聊天**每則使用者問題會**附上**這段左欄狀態
4. **Agent**（peas-agent-core）推理，必要時呼叫 **tool** 寫入 JSON／CSV 等
5. **左欄**再讀取同一檔案或 session，更新 UI

## Mermaid 撰寫規則（個人架構圖）

### 必須

- 三個子圖方向感：**左欄網頁**、**右欄 AI 助手**、**資料存放**（若專題無持久檔可省略或改「暫存設定」）
- 節點用**功能名**（點餐頁、聊天面板、AI 大腦、訂單檔…）
- 箭頭標**白話**（「每則問題附上左欄狀態」「Agent 寫入訂單」）

### 禁止

- 節點主文字用 `format_extra_context`、`pages/4_Order.py` 等原始碼名稱
- 在圖上寫 Router IP、api_key

### 技術名詞放哪

- 檔名、函式名 → `專題報告.md` **§5 技術含量** 正文
- 全班 server → **§2 學校 Server 環境** + `server-topology.png`

## 已核准範例

skill 內 `assets/example-project-architecture.mmd`（點餐＋心情儀表板範例）。學生專題不同時，**替換節點與箭頭文字**，保留結構與白話風格。

## 自訂頁認定（demo 截圖）

- 路徑：`studio_shell/pages/N_*.py`
- **計入 demo**：檔名前綴數字 **≥ 4**（例如 `4_`、`5_`）
- **不計入**：`1_Home`、`2_Playground`、`3_UI_Cheatsheet` 等 installer 內建頁

Preflight 以實際檔名為準；若課堂統一從 `4_` 開始自訂，與上規則一致。
