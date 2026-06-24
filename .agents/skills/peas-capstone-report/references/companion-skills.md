# Companion Skills Preflight（CompanionPreflight）

**注意**：本 preflight **不是** step_id `0`（自訂頁清單）。step_id `0` 見 step-scripts § Step 0。

## 時機

| 時機 | 動作 |
|------|------|
| **首次觸發** peas-capstone-report | 完整 preflight → 寫 `.capstone-companion-check.json` → 再輸出 Step 1 |
| Step 0、Step 6b 前 | 讀狀態檔；`install_failed` 可重試一次 |
| `current_step ≥ 5` 且無狀態檔 | 先跑 preflight 再繼續 |

## 前置

- cwd = **學生專題專案根**（有 `studio_shell/`）
- 禁止把 api_key 寫入 repo、`report/`、`.env` commit

## 1 · Companion skills（專案 `.agents`）

檢查：

- `.agents/skills/vcr-imagegen/SKILL.md`
- `.agents/skills/pptx/SKILL.md` 或 `scripts/html2pptx.js`

缺任一 → 專案根執行（**無 `-g`**）：

```bash
npx skills add mz038197/vanscoding-skills/Media/vcr-imagegen -y --all
npx skills add mz038197/vanscoding-skills/Documents/pptx -y --all
```

路徑優先序（Step 7 / Step 6b 共用）：

| skill | 1 | 2 | 3 |
|-------|---|---|---|
| vcr-imagegen | `{project}/.agents/skills/vcr-imagegen/` | `%USERPROFILE%\.agents\skills\vcr-imagegen\` | `%USERPROFILE%\.cursor\skills\vcr-imagegen\` |
| pptx | `{project}/.agents/skills/pptx/` | `%USERPROFILE%\.agents\skills\pptx\` | `{project}/.cursor/skills/pptx/` |

## 2 · VSROUTER_API_KEY

1. 若 `$env:VSROUTER_API_KEY` 已有 → `vcr_key: ok`
2. 否則讀 `%USERPROFILE%\.peas-agent\config.json` 的 `api_key`
3. 若非空 → **僅本次工作階段** `$env:VSROUTER_API_KEY = api_key`
4. 仍缺 → `vcr_key: missing`；Step 1 末尾提醒完成 Agent Studio api_key；Step 7 走 `poster-fallback.md`

## 3 · Node（html2pptx）

| 項目 | 檢查 | 安裝 |
|------|------|------|
| Node.js | `node -v` | `winget install OpenJS.NodeJS.LTS --accept-package-agreements` |
| pptxgenjs | `node -e "require('pptxgenjs')"` | `npm install -g pptxgenjs` |
| playwright | `npx playwright --version` | `npm install -g playwright` 後 `npx playwright install chromium` |
| sharp | `node -e "require('sharp')"` | `npm install -g sharp` |

Windows 全域 `require` 失敗 → retry 一次 → 仍失敗標 `install_failed`（Step 6b fallback，不擋 docx／海報）。

## 4 · Python（`uv add`）

專題專案根須有 `pyproject.toml`；無則 `uv init` 或請老師。

| 項目 | 檢查 | 安裝 |
|------|------|------|
| python-pptx | `uv run python -c "import pptx"` | `uv add python-pptx` |
| python-docx | `uv run python -c "import docx"` | `uv add python-docx` |

**一律 `uv add`**；避免 `uv pip install` / `pip install`。

## 5 · 狀態檔

寫入專案根 `.capstone-companion-check.json`：

```json
{
  "vcr-imagegen": "ok",
  "pptx": "ok",
  "vcr_key": "ok",
  "node": "ok",
  "pptxgenjs": "ok",
  "playwright": "ok",
  "sharp": "ok",
  "python_pptx": "ok",
  "python_docx": "ok",
  "checked_at": "2026-06-23T12:00:00",
  "project_agents_path": ".agents/skills/"
}
```

各欄位值：`ok` | `missing` | `install_failed`

## 6 · Fallback 規則

| 條件 | Step 6b |
|------|---------|
| Node 四項 + `pptx` skill 皆 `ok` | html2pptx 主流程 |
| 任一 `install_failed`（重試後） | `build_capstone_ppt.py` |
| `python_docx` 非 `ok` | **不得** Step 6c |

## 7 · `.gitignore` 建議

```
.capstone-companion-check.json
report/.ppt-build-tmp/
```

`report/ppt-style.json` 為繳交物，**不要** ignore。

## 8 · 學生可見話術

preflight 成功 → **不**向學生展開安裝細節，直接 Step 1。

任一 `install_failed` → Step 1 模板末尾加一句：「後段 PPT／海報可能改用備援流程；請確認網路，或請老師協助。」
