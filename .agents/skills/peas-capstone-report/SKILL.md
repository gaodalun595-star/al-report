---
name: peas-capstone-report
description: 逐步引導 Agent Studio 專題學生完成可繳交報告（專題介紹、左欄↔右欄互動、成果／創新／技術由學生主筆；Agent 代勞架構 Mermaid、全班相同 server 拓撲圖、MD／PPT／Word、Step 7 VCR 專題海報）。每則回覆前必讀 references/step-scripts.md 當前 step_id；Step 1–3 學生口述、對齊條列後才落檔；Step 6 三選一 PPT 風格 → 6b html2pptx → 6c docx；Step 7 必產 report/assets/專題海報.png。觸發：專題報告、capstone、Agent Studio 架構圖、server 配置圖、專題海報。
version: "1.2.0"
updated: "2026-06-23"
---

# 專題報告陪練（peas-capstone-report）

## 何時使用

- 馬公高中 Agent Studio + peas-agent-core 專題，要產出 **Markdown + PPTX + DOCX + 專題海報**。
- 使用者說「專題報告」「capstone」「架構圖」「server 配置圖」「專題海報」「peas-capstone-report」等。
- **前置**：專案已有 `studio_shell/`；`~/.peas-agent/config.json` 已指向學校 Router（**報告內不寫 Router IP／URL**）。首次觸發會 **CompanionPreflight** 自動安裝 companion skills、Node 套件、**uv add** Python 依賴（見 `references/companion-skills.md`）。

## 核心原則

- **劇本在 `references/step-scripts.md`**：話術、對齊條列、組裝指令都在該檔；本檔只寫執行協定。
- **學生主筆 A 段（Step 1–3）**：專題介紹、左欄↔右欄互動、成果／創新／技術 — 學生用**自己的話**回答；Agent **整理成條列**並請學生確認後才寫入 `report/`。
- **Agent 代勞 B 段（Step 0、4–7）**：preflight、複製 server 圖、撰寫 `project-architecture.mmd`、mmdc 產 PNG、收 demo 截圖、產 MD／PPT／DOCX、VCR 專題海報。
- **禁止**：改 `studio_shell/pages/` 程式、維運 Ollama Router、在報告中貼 api_key 或 Router 位址。

## 執行協定（每則回覆前必做）

0. **CompanionPreflight**（**非 step_id**）：首次觸發 skill 或缺 `.capstone-companion-check.json` 且 step ≥ 5 時，依 `references/companion-skills.md` 檢查／安裝後寫狀態檔；再繼續下列步驟。
1. **確認 `current_step`**：`1` | `2` | `3` | `3c` | `0` | `4` | `4b` | `5` | `6` | `6b` | `6c` | `7`。首次觸發 → 先 CompanionPreflight → `1`。學生回覆匹配當步 `completion_phrases` 後才進下一 `step_id`（順序見 step-scripts 末尾速查表）。
2. **讀取** `references/step-scripts.md` **該 step_id 整段**（含 `學生可見模板`、`if_stuck`、`agent_must_not`）。
3. **Step 1–3**：一次只問一題；學生答完再追問或進下一步；**不得**代寫長篇，只整理條列。
4. **Step 3c**：輸出完整對齊條列，學生說「確認」後才進 Step 0。
5. **Step 4–7**：可動手寫檔、跑腳本；Step 6c 前依 `references/verification.md` § Step 6c；Step 7 完成前依 § Step 7。
6. **禁止**：同一則兩個待辦；未確認對齊條列就產 MD；交付無圖 docx；Step 7 未完成就標記全部完成。

## 產出契約（學生專案）

```text
report/
├── 專題報告.md
├── 專題報告.pptx
├── 專題報告.docx          ← 必須含嵌入 PNG
├── ppt-style.json         ← Step 6 風格選擇
├── poster-prompt.txt      ← Step 7 prompt（可保留）
├── project-architecture.mmd
├── .capstone-progress.md
└── assets/
    ├── server-topology.png
    ├── project-architecture.png
    ├── 專題海報.png         ← Step 7 必產（直式 2:3）
    └── demo-*.png

.capstone-companion-check.json   ← 專案根；preflight 狀態（建議 gitignore）
```

## 參考檔索引

| 檔案 | 用途 |
|------|------|
| `references/step-scripts.md` | **主檔**；每則必讀當步 |
| `references/companion-skills.md` | CompanionPreflight（npx、Node、uv add、VCR key） |
| `references/ppt-style-guide.md` | Step 6 三選一風格 |
| `references/ppt-build-guide.md` | Step 6b html2pptx |
| `references/student-voice-worksheet.md` | Step 1–3 引導問題與條列範例 |
| `references/studio-patterns.md` | 左欄↔右欄組裝規則 + 已核准 Mermaid 範例 |
| `references/server-topology.md` | 全班相同 server 圖說明（無 IP） |
| `references/mermaid-to-png-guide.md` | mmdc 失敗時 ChatGPT／Gemini 後備 |
| `references/screenshot-guide.md` | demo 截圖規範 |
| `references/report-template.md` | `專題報告.md` 章節骨架 |
| `references/ppt-slide-map.md` | html2pptx 投影片編排契約 |
| `references/docx-fallback.md` | docx 腳本失敗後備 |
| `references/poster-prompt-template.md` | Step 7 海報 prompt 與 vcr-imagegen 指令 |
| `references/poster-fallback.md` | Step 7 VCR 失敗時網頁後備 |
| `references/verification.md` | Step 6b／6c／7 交件前檢查 |

## 腳本（B 段 Agent 執行）

| 腳本 | 用途 |
|------|------|
| `scripts/render_project_diagram.py` | `.mmd` → PNG（npx mmdc） |
| `scripts/build_capstone_ppt_html2pptx.js` | **主流程** MD + style → pptx |
| `scripts/build_capstone_ppt.py` | pptx **fallback**（Node 不可用時） |
| `scripts/build_capstone_docx.py` | MD + assets → docx（**須嵌圖**） |

Step 7 海報：**不新增腳本**；跨 skill 呼叫 **vcr-imagegen**（見 `poster-prompt-template.md`）。

路徑：在**學生專案根目錄**執行；Python 用 **`uv run python`**；`--report-dir report` 為預設。

## 圖片四類

| 圖 | 來源 |
|----|------|
| Server | 複製 skill `assets/server-topology.png` → `report/assets/` |
| 個人架構 | 學生專案 `report/project-architecture.mmd` + mmdc |
| Demo | 學生 `Win+Shift+S` 截自訂頁 → `demo-01.png` … |
| 專題海報 | Step 7：vcr-imagegen（reference 含上三類）→ `專題海報.png` |

**個人架構 Mermaid**：節點用平易近人中文（點餐頁、AI 大腦…）；**禁止**以 `format_extra_context`、`pages/4_*.py` 作節點主文字。

## 觸發後第一則

CompanionPreflight → 讀 step-scripts **§ Step 1**，**只**輸出 Step 1 學生可見模板。
