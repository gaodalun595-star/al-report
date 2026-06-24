# Demo 截圖指南（Step 4b）

## 範圍

- **只截自訂頁**：`studio_shell/pages/N_*.py`，且 **N ≥ 4**
- **不截**內建 `1_Home`、`2_Playground`、`3_UI_Cheatsheet`（除非老師另行要求）

Preflight 列出的自訂頁數 = **最低截圖張數**。

## 檔名規則

| 檔案 | 對應 |
|------|------|
| `report/assets/demo-01.png` | 清單第 1 個自訂頁 |
| `report/assets/demo-02.png` | 第 2 個 |
| … | … |

清單寫入 `report/.capstone-progress.md` 供對照。

## 操作步驟

1. 專案根：`uv run streamlit run studio_shell/app.py`
2. 左側選單進入自訂頁
3. **Win+Shift+S** 選取 App 主內容區（可含側欄）
4. 存 PNG 到 `report/assets/`
5. 重複直到每自訂頁至少 1 張

## 品質與安全

- 畫面清晰、可讀 UI 標題
- **不要**露出 api_key、完整 Router URL、個資
- 若右欄有測試對話，避免不雅或私密內容

## 交件

Step 6 verification 會檢查：

- `demo-*.png` 數量 ≥ 自訂頁數
- MD／docx 內引用全部 demo 圖

缺圖 → **阻擋**交件，回到 Step 4b。
