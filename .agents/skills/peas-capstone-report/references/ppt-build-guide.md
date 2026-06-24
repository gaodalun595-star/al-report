# PPT 建置（Step 6b · html2pptx）

Agent 執行 Step 6b 前必讀本檔 + **pptx skill** 的 `html2pptx.md` + `references/ppt-slide-map.md`。

## 主流程

在**學生專案根**：

```bash
node "<peas-capstone-report>/scripts/build_capstone_ppt_html2pptx.js" \
  --report-dir report \
  --skill-root "<peas-capstone-report 絕對路徑>"
```

前置：

- `report/ppt-style.json` 存在且 style ∈ 三選一
- `report/專題報告.md` 存在
- `.capstone-companion-check.json` 中 Node 四項 + `pptx` skill 皆 `ok`

## pptx skill 路徑

腳本自動解析（見 `companion-skills.md`）。找不到 → 專案根：

```bash
npx skills add mz038197/vanscoding-skills/Documents/pptx -y --all
```

## 模板

`assets/ppt-styles/{style}/`：

| 檔案 | 用途 |
|------|------|
| `cover.html` | 封面 |
| `bullets.html` | 條列頁 |
| `image-full.html` | Server 全幅圖 |
| `image-caption.html` | 架構圖 + 精簡條列 |
| `demo.html` | Demo 截圖 |

占位：`{{TITLE}}`、`{{META_HTML}}`、`{{HEADING}}`、`{{BULLETS_HTML}}`、`{{IMAGE_PATH}}`、`{{CAPTION_HTML}}`

## 編排

依 `ppt-slide-map.md` 硬編排程（非 MD 章節順序碰運氣）。

## Fallback

Node／pptx skill `install_failed` 時：

```bash
uv run python "<skill>/scripts/build_capstone_ppt.py" --report-dir report
```

`ppt-style.json` 保留；環境修好可重跑 html2pptx。

## 驗收（可選）

pptx skill 的 `scripts/thumbnail.py` 產縮圖目視檢查 overflow。

## 暫存

`report/.ppt-build-tmp/` 可刪；建議 gitignore。
