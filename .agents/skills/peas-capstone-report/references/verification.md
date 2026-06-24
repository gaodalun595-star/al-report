# 交件驗收（Step 6b / 6c / Step 7）

Agent 在標記完成前**逐項檢查**（可腳本 + 人工）。任一失敗 → 回到對應步驟。

---

## Step 6 · 風格（6b 前）

學生選完風格、進 6b 前：

- [ ] `report/ppt-style.json` 存在
- [ ] `style` 為 `classic-blue` | `teal-coral` | `sage-terracotta` 之一

---

## Step 6b · PowerPoint

Step 6b 完成後：

| 路徑 | 必要 |
|------|------|
| `report/專題報告.pptx` | ✓ 非空、可開啟 |

---

## Step 6c · Word 與三份報告

Step 6c 通過後才可進 Step 7。

### 檔案存在

| 路徑 | 必要 |
|------|------|
| `report/專題報告.md` | ✓ |
| `report/專題報告.pptx` | ✓ |
| `report/專題報告.docx` | ✓ |
| `report/ppt-style.json` | ✓ |
| `report/project-architecture.mmd` | ✓ |
| `report/assets/server-topology.png` | ✓ |
| `report/assets/project-architecture.png` | ✓ |
| `report/assets/demo-*.png` | ✓ 張數 ≥ 自訂頁數 |

### 內容對齊

- [ ] MD §1–5 與 Step 3c 對齊條列一致（無擅自新增功能）
- [ ] 報告**無** api_key、Router IP／URL
- [ ] 個人架構 Mermaid 節點為白話中文（非 `format_extra_context` 作主標）

### DOCX 圖片（硬性）

執行：

```bash
uv run python "<skill>/scripts/build_capstone_docx.py" --report-dir report --verify-only
```

或 Agent 用 python-docx 讀取 `專題報告.docx` 統計 `inline_shapes` / 圖片關係：

- **至少** 2 + demo 張數（server + 架構 + 各 demo）
- 若只有文字 → **失敗**，依 `docx-fallback.md` 處理，**不得**進 Step 7

### 學生可見驗收問句（一次一條）

1. 三份檔 `md / pptx / docx` 都打開了嗎？
2. Word 裡看得到 server 圖、架構圖嗎？
3. 每個自訂頁的 demo 圖都在 Word 附錄嗎？

全部 OK → 進 Step 7。

---

## Step 7 · 專題海報

標記「全部完成」前逐項檢查。

### 檔案存在

| 路徑 | 必要 |
|------|------|
| `report/assets/專題海報.png` | ✓ 非空、可預覽 |

### 內容（人工）

- [ ] 海報可見**專題名稱**
- [ ] 可辨識 server 拓撲與個人架構圖元素（非純文字重畫失真）
- [ ] 海報文字與 Step 3c／MD 一致，**無**虛構功能
- [ ] 海報**無** api_key、Router IP／URL

### 學生可見驗收問句

1. `專題海報.png` 打開了嗎？
2. 標題與各區文字是否正確？
3. Server 圖、架構圖、Demo 縮圖是否看得清楚？

全部 OK → 「專題報告與海報已完成，可以繳交 `report/` 資料夾。」

---

## Preflight 紀錄

`report/.capstone-progress.md` 應含：

- 自訂頁清單（demo ↔ 頁名表）
- demo 需求張數
- 已完成 step_id（完成時應為 `7`）

專案根 `.capstone-companion-check.json` 記錄 companion／Node／Python 環境（見 `companion-skills.md`）。
