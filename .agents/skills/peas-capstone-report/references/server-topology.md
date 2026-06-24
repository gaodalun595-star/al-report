# 學校 Server 環境（全班相同拓撲圖）

## 用途

- 報告 **§2 學校 Server 環境** 使用 skill 預製 `server-topology.png`
- **全班相同**：由老師自 `assets/server-topology.mmd` 定稿，學生**複製**到 `report/assets/`，勿各自改拓撲

## 圖上呈現（平易近人）

| 區塊 | 含義 |
|------|------|
| 學生端 | Agent Studio 網頁 App、本機 Agent 設定檔 |
| 學校 AI 閘道 | Ollama Router 負載平衡、課堂 Portal 與 API Key 管理 |
| AI 運算節點 | 多台 Ollama（分散請求） |

## 報告正文怎麼寫

- 說明：專題 App 透過學校提供的 **API Key** 呼叫 **Ollama Router**，由 Router 分配至後端 Ollama 節點執行 LLM。
- Portal 負責課堂發放 Key、班級與紀錄（細節依老師課堂說明）。
- **不要寫** Router IP、URL、完整 api_key。

## 依據

架構概念來自 [`ollama_router`](https://github.com/) README：OpenAI 相容 API、多後端負載平衡、API Key 驗證、Portal。skill 圖為教學簡化版，非完整維運手冊。

## Agent 動作（Step 0）

```text
複製：<skill>/assets/server-topology.png
  →  <專案>/report/assets/server-topology.png
```

MD 引用：`![](assets/server-topology.png)`
