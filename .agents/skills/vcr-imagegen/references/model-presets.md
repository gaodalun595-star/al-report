# 課堂 Model Presets（GPT 高品質包）

Skill 只教以下四種用途；**不要**讓學生從 OpenRouter 長列表自選。

| Preset / 用途 | Config 鍵 | Model | 何時用 |
|---------------|-----------|-------|--------|
| Icon／簡單插圖 | `models.icon` / `-Preset icon` | `openrouter@black-forest-labs/flux.2-klein-4b` | App icon、flat 插圖 |
| UI mockup／海報 | `models.ui_mockup` / `-Preset ui_mockup` | `openrouter@openai/gpt-5.4-image-2` | 介面稿、含文字版面 |
| 寫實照片 | `models.photo` / `-Preset photo` | `openrouter@bytedance-seed/seedream-4.5` | 場景、人物、產品照風格 |
| 有參考圖的改圖 | `edit_model`（自動） | `openrouter@openai/gpt-5.4-image-2` | 傳 `-ReferencePath` 時 |

## 解析順序（腳本內建）

**有 `-ReferencePath` 且未指定 `-Model`：**

1. `.vans/image.json` → `edit_model`
2. Fallback → `openrouter@openai/gpt-5.4-image-2`

**純生圖：**

1. CLI `--Model`
2. `--Preset` → `models.*`
3. `VCR_IMAGE_MODEL`
4. `default_model`
5. Fallback → `flux.2-klein-4b`

## 成本提示

GPT-5.4 Image 2 與 Seedream 比 flux klein 貴。Icon 作業盡量 `-Preset icon`。

## 進階

老師可自行改 `.vans/image.json` 的 model 字串；Skill 不列出其他 OpenRouter 生圖 model。
