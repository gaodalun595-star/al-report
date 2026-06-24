# 專題報告 Markdown 模板

Agent 在 Step 5 依對齊條列產出 `report/專題報告.md`。占位 `{…}` 由 Step 3c 條列替換。

```markdown
# {專題名稱}

**組別／組員**：{組別}  
**日期**：{YYYY-MM-DD}

---

## 1. 專題介紹

{§1 條列展開為段落或 bullet}

---

## 2. 學校 Server 環境

本專題透過學校提供的 API Key 呼叫 Ollama Router，由 Router 分配至後端 Ollama 節點執行 LLM。下圖為全班相同之 server 拓撲（報告不標示 Router 位址）。

![學校 Server 拓撲](assets/server-topology.png)

---

## 3. 系統概覽

左欄 Streamlit 自訂頁與右欄 Agent 的互動如下。

![專案架構](assets/project-architecture.png)

{§2 條列：自訂頁、資料流、完整例子}

---

## 4. 成果與創新

### 4.1 成果

{§3 條列}

### 4.2 創新／亮點

{§4 條列}

---

## 5. 技術含量

{§5 條列；可含檔名、框架、資料格式}

---

## 附錄：Demo 截圖

{依 demo-01 … demo-NN 各一段，嵌入圖片}

### {自訂頁名稱 1}

![Demo 1](assets/demo-01.png)

### {自訂頁名稱 2}

![Demo 2](assets/demo-02.png)

```

展覽用綜整海報（Step 7 另產）：`assets/專題海報.png`

## 撰寫注意

- 全文繁體中文
- 圖片路徑一律 `assets/...`（相對 `report/` 目錄）
- 勿貼 api_key、Router IP
