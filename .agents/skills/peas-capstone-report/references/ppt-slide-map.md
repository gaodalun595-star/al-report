# PPT 投影片編排契約（html2pptx）

主流程：`scripts/build_capstone_ppt_html2pptx.js` + `assets/ppt-styles/{style}/`  
Fallback：`scripts/build_capstone_ppt.py`（簡易版式、Demo 標題可能為 `Demo N`）

## MD 章節 → 投影片

| # | 標題 | 模板 | 內容來源（`專題報告.md`） |
|---|------|------|---------------------------|
| 1 | 封面 | `cover.html` | `# 標題` + `**組別**` / `**日期**` |
| 2 | 專題介紹 | `bullets.html` | `## 1. 專題介紹` bullet |
| 3 | 學校 Server 環境 | `image-full.html` | `## 2. …` 首段 + `server-topology.png` |
| 4 | 系統概覽 | `image-caption.html` | `project-architecture.png` + `## 3. …` bullet（≤4 條） |
| 5 | 成果 | `bullets.html` | `### 4.1 成果` bullet |
| 6 | 創新／亮點 | `bullets.html` | `### 4.2 創新／亮點` bullet |
| 7 | 技術含量 | `bullets.html` | `## 5. 技術含量` bullet |
| 8+ | {自訂頁名} | `demo.html` | `## 附錄` 各 `### {頁名}` + `demo-XX.png` |

Demo 標題：主流程從附錄 `###` 解析；可 cross-check `report/.capstone-progress.md` 自訂頁表。

## 字數限制

- 每頁 bullet ≤ **6** 條
- 每條 ≤ **80** 字（overflow 時截斷）

## 版式

- 16:9 · 720×405pt（html2pptx 規格）
- 字體：Arial / Helvetica（web-safe）
- 無校徽

## 指令

**主流程（Step 6b）**：

```bash
node "<skill>/scripts/build_capstone_ppt_html2pptx.js" --report-dir report --skill-root "<skill>"
```

**Fallback**：

```bash
uv run python "<skill>/scripts/build_capstone_ppt.py" --report-dir report
```

需 `python-pptx`：`uv add python-pptx`
