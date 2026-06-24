# VCR 生圖 Skill 安裝

## 安裝 skill

```bash
# 全域（裝一次、所有專案可用）
npx skills add mz038197/vanscoding-skills/Media/vcr-imagegen -g -y --all

# 專案內（隨 repo / AGENTS.md）
npx skills add mz038197/vanscoding-skills/Media/vcr-imagegen -y --all
```

## 環境變數

| 變數 | 說明 |
|------|------|
| `VSROUTER_API_KEY` | Portal 取得的 `vcr_sk_...`（**唯一**接受的 key 環境變數） |
| `VCR_BASE_URL` | 預設 `https://ai.vanscoding.com/v1` |
| `OPENAI_BASE_URL` | 同上 fallback |
| `VCR_IMAGE_MODEL` | 覆寫預設生圖 model（少見） |

Windows 可寫入使用者環境變數，或在專案 `.env` 由你的工具載入（勿 commit key）。

## 專案設定

複製 skill 內 `assets/image.config.example.json` → 專案根 `.vans/image.json`。

## 403 image_generation_disabled

老師在 Portal 課次列表關閉「生圖」時，學生 session key 會收到 403。請老師開啟該課堂生圖開關；老師 long-lived key 不受限。

## 腳本路徑

Agent 依序尋找：

1. `%USERPROFILE%\.cursor\skills\vcr-imagegen\scripts\generate-image.ps1`
2. `%USERPROFILE%\.copilot\skills\vcr-imagegen\scripts\generate-image.ps1`
3. 專案 `.cursor/skills/vcr-imagegen/` 或 `.agents/skills/vcr-imagegen/`

## 需求

- Python 3.10+（stdlib only，腳本內建 HTTP）
- 可連線 VCR（預設 production `https://ai.vanscoding.com`）
