# peas-capstone-report

Agent Studio 專題報告陪練 skill — 引導學生產出 `report/專題報告.{md,pptx,docx}`、`report/ppt-style.json` 與 `report/assets/專題海報.png`。

## 老師端（vanscoding-skills 維護者）

在 repo 根目錄：

```powershell
.\scripts\sync-skill-to-agents.ps1 -SourcePath Teacher/peas-capstone-report
```

## 學生端（課堂安裝）

### 方式 A：Git 子路徑

1. Clone 或 sparse checkout `Teacher/peas-capstone-report/` 資料夾。
2. 整份複製到：

```text
%USERPROFILE%\.cursor\skills\peas-capstone-report\
```

3. 重開 Cursor 或新開 Agent 對話，說「用 peas-capstone-report 帶我寫專題報告」。

### 方式 B：Zip

1. 老師 zip `peas-capstone-report` 資料夾內容（含 `SKILL.md`、`references/`、`assets/`、`scripts/`）。
2. 解壓到 `%USERPROFILE%\.cursor\skills\peas-capstone-report\`。
3. 同上觸發 skill。

## 學生專案前置

- 已安裝 Agent Studio（專案根有 `studio_shell/`）。
- `~/.peas-agent/config.json` 已設定學校發放的 `api_key`（報告內**不要**寫 key 或 Router 位址）。
- **首次觸發 skill** 會自動 CompanionPreflight：專案 `.agents` 安裝 vcr-imagegen + pptx、Node 全域套件、**uv add** python-pptx／python-docx（見 `references/companion-skills.md`）。

## PPT 流程（v1.2.0）

| Step | 內容 |
|------|------|
| 6 | 學生三選一風格（`assets/ppt-style-picker/index.html`）→ `report/ppt-style.json` |
| 6b | **html2pptx** 主流程 → `專題報告.pptx`；Node 不可用時 fallback `build_capstone_ppt.py` |
| 6c | `build_capstone_docx.py` → 三份報告驗收 |

## 產出位置

在**專題專案根目錄**建立 `report/`，完成後應有：

- `專題報告.md`、`專題報告.pptx`、`專題報告.docx`
- `ppt-style.json`
- `project-architecture.mmd`
- `assets/server-topology.png`、`project-architecture.png`、`demo-*.png`
- `assets/專題海報.png`（Step 7，直式 2:3 展覽海報）

## 腳本依賴（Agent 代跑時）

```bash
# mmdc（Node）
npx -y @mermaid-js/mermaid-cli ...

# PPT 主流程（Node + 全域 npm）
npm install -g pptxgenjs playwright sharp
npx playwright install chromium
node "<skill>/scripts/build_capstone_ppt_html2pptx.js" --report-dir report --skill-root "<skill>"

# Python（專題專案根 · uv add）
uv add python-pptx python-docx
uv run python "<skill>/scripts/build_capstone_docx.py" --report-dir report
```

Step 7 海報：vcr-imagegen `generate-image.ps1`（見 `references/poster-prompt-template.md`）。

## 維護：重新產生 PPT 風格 HTML 模板

```bash
node scripts/_generate_ppt_templates.js
```
