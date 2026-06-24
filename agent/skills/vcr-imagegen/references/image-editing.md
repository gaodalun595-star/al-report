# 參考圖再改（input_references）

## 何時用

- 使用者要「改這張圖」「換背景」「保留角色只改…」
- 專案內已有 PNG/JPEG（例如上一輪 `assets/generated/icon.png`）

## Agent 規則

1. **必須** `-ReferencePath` 指向 workspace 內已存在檔案
2. **不要** 在 chat 貼整段 base64
3. 編輯 prompt 只寫「要改什麼」
4. **輸出新檔名**（如 `icon-v2.png`），不要覆蓋原圖

## 範例

```powershell
$gen = Join-Path $SkillRoot 'scripts/generate-image.ps1'

# 先產圖
& $gen -PromptFile .cursor/tmp/prompt.txt -Preset icon -OutputPath assets/generated/icon.png

# 再改圖（自動用 edit_model = gpt-5.4-image-2）
& $gen -PromptFile .cursor/tmp/edit.txt `
  -ReferencePath assets/generated/icon.png `
  -OutputPath assets/generated/icon-v2.png
```

## API body 形狀（腳本自動組）

```json
{
  "model": "openrouter@openai/gpt-5.4-image-2",
  "prompt": "dark blue background, keep the robot head unchanged",
  "input_references": [
    {
      "type": "image_url",
      "image_url": { "url": "data:image/png;base64,..." }
    }
  ]
}
```

## 參考圖上限

依 model 不同（腳本會截斷並 warning）：

| Model | 約略上限 |
|-------|----------|
| gpt-5.4-image-2 | 16 |
| seedream-4.5 | 14 |
| flux.2-klein-4b | 4 |

v1 只支援**本機檔案**路徑，不支援 HTTP URL 參考。

## 常見錯誤

| 狀況 | 處理 |
|------|------|
| Reference 檔不存在 | 確認路徑相對專案根 |
| 403 | Portal 課堂生圖開關 |
| 401 | 檢查 `VSROUTER_API_KEY` |
