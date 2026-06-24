# Mermaid → PNG（B3 後備）

## 首選：skill 腳本 + mmdc

在**學生專案根目錄**：

```bash
python "<skill>/scripts/render_project_diagram.py" ^
  --mmd report/project-architecture.mmd ^
  --out report/assets/project-architecture.png
```

需本機 **Node.js** 與 `npx`（腳本會執行 `npx -y @mermaid-js/mermaid-cli`）。

### 常見失敗

| 現象 | 處理 |
|------|------|
| `npx not found` | 安裝 Node.js LTS，重開終端 |
| mmdc 語法錯誤 | 修正 `.mmd` 括號、引號；對照 `example-project-architecture.mmd` |
| 中文乱码 | 確保 `.mmd` UTF-8 存檔 |

## 後備：ChatGPT 或 Gemini 網頁

1. 開啟 `report/project-architecture.mmd` 全文複製
2. 在 ChatGPT／Gemini 貼上並說：「請把以下 Mermaid 渲染成 PNG，白底，不要改節點文字。」
3. 下載 PNG 存為 `report/assets/project-architecture.png`
4. 確認檔案非空、可預覽

**禁止**用 IDE 內建「憑空生圖」代替 Mermaid 渲染（會改變拓撲）。

## Server 圖

`server-topology.png` **不要**讓學生重跑 mmdc；一律複製 skill `assets/` 定稿。
