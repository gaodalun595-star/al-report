# 專題海報 Prompt 模板（Step 7）

Agent 在 Step 7 依本檔組裝 **`report/poster-prompt.txt`**（UTF-8），再交 vcr-imagegen 生圖。**文字只能來自** Step 3c 對齊條列或 `專題報告.md`，不得虛構功能。

## Reference 圖順序（`-ReferencePaths` 逗號分隔）

| 順序 | 檔案 | 海報用途 |
|------|------|----------|
| 1 | `report/assets/server-topology.png` | § Server 環境區塊 |
| 2 | `report/assets/project-architecture.png` | § 系統概覽區塊 |
| 3+ | `report/assets/demo-01.png` … | Demo 縮圖列（依 preflight 清單） |

GPT-5.4 Image 2 參考圖上限約 **16 張**。若 demo 過多：必保留 1、2，其餘 demo 依序加入至上限；未放入 reference 的頁面在 prompt **文字**列出頁名。

## Prompt 骨架

將 `{占位}` 替換為報告內容後寫入 `report/poster-prompt.txt`：

```text
請製作一張繁體中文專題展覽海報（直式 2:3），風格清晰、教學展示用，白底或淺色底，分區標題大字、內文可讀。

【重要】
- 下列條列文字請逐字使用，不要改寫或新增未列出的功能。
- 參考圖 1 為學校 Server 拓撲，請嵌入「Server 環境」區塊，不要改變節點關係。
- 參考圖 2 為本專案架構流程，請嵌入「系統概覽」區塊，不要改變箭頭與節點文字。
- 參考圖 3 起為 App 各頁 demo 截圖，請以縮圖列呈現於「Demo 展示」區。
- 報告內不要出現 api_key 或 Router 位址。

【海報標題】
{專題名稱}

【副標】
組別／組員：{組別}　日期：{YYYY-MM-DD}

【區塊 1 · 專題介紹】
{§1 條列，每行一 bullet}

【區塊 2 · 左欄與右欄互動】
{§2 條列}

【區塊 3 · 成果】
{§3 條列}

【區塊 4 · 創新／亮點】
{§4 條列}

【區塊 5 · 技術含量】
{§5 條列}

【版面配置建議】
由上而下：標題 → 專題介紹 → Server 拓撲圖（大）→ 系統架構圖（大）→ 成果／創新／技術（三欄或三區）→ Demo 縮圖列。
```

## vcr-imagegen 指令

在**學生專案根目錄**執行。Agent 先讀 vcr-imagegen skill；腳本路徑依序：

1. `{project}/.agents/skills/vcr-imagegen/scripts/generate-image.ps1`
2. `%USERPROFILE%\.agents\skills\vcr-imagegen\scripts\generate-image.ps1`
3. `%USERPROFILE%\.cursor\skills\vcr-imagegen\scripts\generate-image.ps1`

```powershell
$gen = "<上述第一個存在的 generate-image.ps1>"
& $gen `
  -PromptFile "report/poster-prompt.txt" `
  -Preset ui_mockup `
  -AspectRatio "2:3" `
  -Resolution "2K" `
  -ReferencePaths "report/assets/server-topology.png,report/assets/project-architecture.png,..." `
  -OutputPath "report/assets/專題海報.png" `
  -Cwd (Get-Location).Path
```

## 修正迭代

學生指出文字或區塊錯誤時，用 edit 模式：

```powershell
& $gen `
  -PromptFile "report/poster-edit-prompt.txt" `
  -ReferencePath "report/assets/專題海報.png" `
  -OutputPath "report/assets/專題海報-v2.png"
```

確認後將最終版存為 `report/assets/專題海報.png`。

## 失敗時

見 `references/poster-fallback.md`（403／無 key）。
