---
description: "Use when the user asks to generate or edit images via Vans Coding Router (VCR), OpenRouter image models, Portal session keys, or needs PNG/JPEG under assets/generated with input_references for reference-based editing."
---
# Vans Coding Router 生圖

## 定位

| 層 | 路徑 | 角色 |
|----|------|------|
| **VCR API** | `https://ai.vanscoding.com/v1/images` | OpenRouter 生圖路由；Portal `vcr_sk_...` 認證 |
| **本 skill** | `~/.cursor/skills/vcr-imagegen/` | Agent 薄包裝：只呼叫同捆腳本 |

**不是** OpenAI DALL·E Platform API，也**不是** Codex／Gemini CLI 內建生圖。走 VCR `POST /v1/images`，回傳 `data[0].b64_json` 寫入專案路徑。

## 核心原則

需要產出**專案內實際 PNG／JPEG**時，agent **只呼叫**：

`$env:USERPROFILE\.cursor\skills\vcr-imagegen\scripts\generate-image.ps1`

Copilot 全域：`$env:USERPROFILE\.copilot\skills\vcr-imagegen\scripts\generate-image.ps1`

不要手動組 curl／fetch base64；不要讓 agent 在 chat 貼整段 reference base64。

## 何時使用

- 使用者要落地圖檔，且環境有 **VCR Portal key**（`VSROUTER_API_KEY` = `vcr_sk_...`）
- 固定輸出如 `assets/generated/...`
- 參考圖再改（`-ReferencePath` → `input_references`）
- 課堂 preset：icon／ui_mockup／photo

**不要用**：只要構想；使用者指定 Codex／Gemini CLI 生圖且堅持不用 VCR；沒有 API key。

## 前置條件

1. 安裝 skill（見 `references/setup.md`）
2. 環境變數：`VSROUTER_API_KEY`（必填）；可選 `VCR_BASE_URL`（預設 production）
3. Python 3.10+（腳本 stdlib only）
4. 可選：專案 `.vans/image.json`（複製 `assets/image.config.example.json`）

Portal 課堂若關閉「生圖」，學生 key 會 **403**；請老師開啟開關。

## 標準流程

1. 決定 `-OutputPath`（預設 `assets/generated/image.png`，相對專案根）
2. 中文或長 prompt → UTF-8 檔 + `-PromptFile`
3. 選 preset 或讓腳本依 `.vans/image.json` 解析 model
4. 執行腳本；結束碼 0；stdout 為 JSON `{ path, model, total_tokens, reference_paths }`
5. 回報路徑與 model；失敗說明 401／403／timeout

```powershell
$gen = Join-Path $env:USERPROFILE '.cursor/skills/vcr-imagegen/scripts/generate-image.ps1'

# Icon（flux klein，便宜快）
& $gen `
  -PromptFile ".cursor/tmp/vcr-prompt.txt" `
  -Preset icon `
  -OutputPath "assets/generated/app-icon.png" `
  -AspectRatio "1:1" `
  -Resolution "512" `
  -Cwd (Get-Location).Path
```

改圖（自動 `edit_model` = GPT-5.4 Image 2）：

```powershell
& $gen `
  -PromptFile ".cursor/tmp/vcr-edit.txt" `
  -ReferencePath "assets/generated/app-icon.png" `
  -OutputPath "assets/generated/app-icon-v2.png"
```

驗參數用 `-DryRun`（不呼叫 API，stdout 印計畫請求摘要）。

## 參數速查

| 參數 | 說明 |
|------|------|
| `-ImagePrompt` | 與 `-PromptFile` 二擇一 |
| `-PromptFile` | UTF-8 prompt；中文優先 |
| `-OutputPath` | 預設 `assets/generated/image.png` |
| `-Cwd` | 專案根；預設目前目錄 |
| `-Preset` | `icon` \| `ui_mockup` \| `photo` |
| `-Model` | 完整 `openrouter@...`（覆寫 preset） |
| `-ReferencePath` | 本機參考圖（可重複） |
| `-ReferencePaths` | 逗號分隔多路徑 |
| `-AspectRatio` | 如 `1:1`、`16:9` |
| `-Resolution` | 如 `512`、`1K` |
| `-DryRun` | 只印 JSON 摘要 |
| `-TimeoutSec` | 預設 120（有 reference 時 180） |

## Model presets（GPT 高品質包）

詳見 `references/model-presets.md`：

| Preset | Model |
|--------|-------|
| icon | `openrouter@black-forest-labs/flux.2-klein-4b` |
| ui_mockup | `openrouter@openai/gpt-5.4-image-2` |
| photo | `openrouter@bytedance-seed/seedream-4.5` |
| 有 `-ReferencePath` | `edit_model` → GPT-5.4 Image 2 |

**不要**讓學生從 OpenRouter 長列表自選 model；一律用 preset 即可。

## 常見問題

| 狀況 | 處理 |
|------|------|
| Missing API key | 設 `VSROUTER_API_KEY`（不接受 `OPENAI_API_KEY` 等其他變數） |
| HTTP 403 | Portal 課堂生圖開關；見 setup.md |
| HTTP 401 | key 無效或過期 |
| Reference 找不到 | 路徑相對 `-Cwd` |
| 與 codex-imagegen 選哪個 | 有 VCR key → 本 skill；Codex 訂閱額度 → codex-imagegen |

## 參考

- `references/setup.md` — 安裝與環境變數
- `references/model-presets.md` — preset 與解析順序
- `references/image-editing.md` — `input_references` 改圖
- VCR 生圖 API：`POST /v1/images`（OpenRouter 相容 body）
