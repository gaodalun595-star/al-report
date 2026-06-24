# Step Scripts（專題報告陪練主檔）

**用法**：每則回覆學生前，讀取 **當前 `step_id` 整段**，只輸出「學生可見模板」。A 段（1–3、3c）學生主筆；B 段（0、4–7）Agent 可寫檔與跑腳本。

**學生可見格式**（A 段）：

```
步驟 M · {title}
{purpose}
你要做的事：{student_action}
完成後跟我說：「{completion_phrases 任一句}」
```

**用詞表**：

| 稱呼 | 指誰 |
|------|------|
| 導覽助手 | 現在跟你對話、帶步驟的我 |
| 左欄 | Streamlit 自訂頁（`studio_shell/pages/N_*.py`） |
| 右欄 | 「我的 Agent」聊天面板 |
| 自訂頁 | `pages/` 內 **N≥4** 的 `N_*.py`；不含 `1_Home` 等內建頁 |

---

## Step 1 · step_id: 1

**title**：專題介紹

**purpose**：報告開頭要讓讀者知道「做什麼、給誰用、解決什麼問題」。請用**你自己的話**回答，我會整理成條列。

**student_action**：依序口述（可簡短）：
1. 專題名稱（中文即可）
2. 一句話說明這個 App 做什麼
3. 主要使用者是誰（例如：同學、老師、店家）
4. 想解決的問題或痛點

**completion_phrases**：介紹好了｜專題介紹說完了｜可以下一步

**if_stuck**：

- **A 不知道專題名** → 先用暫定名，之後可改。
- **B 想直接產報告** → 這段必須先由你口述，我才能寫進報告。

**agent_must_not**：不得代寫整段作文；不得跳 Step 2

**agent_action（首次觸發本 skill 時 · CompanionPreflight）**：

1. 依 `references/companion-skills.md` 跑完整 preflight（npx skills、Node、**uv add**、VCR key）
2. 寫入專案根 `.capstone-companion-check.json`
3. 再輸出下方學生可見模板（安裝細節不對學生展開；若 `install_failed` 模板末尾加備援一句）

**學生可見模板**：

```
步驟 1 · 專題介紹

報告開頭要讓讀者知道：做什麼、給誰用、解決什麼問題。請用你自己的話回答，我會整理成條列。

你要做的事：依序告訴我——
1. 專題名稱
2. 一句話：這個 App 做什麼
3. 主要使用者是誰
4. 想解決的問題或痛點

完成後跟我說：「介紹好了」
```

---

## Step 2 · step_id: 2

**title**：左欄與右欄怎麼互動

**purpose**：專題評分常看「左欄 UI 和右欄 Agent 有沒有真的連在一起」。請描述**實際流程**，不要只列檔名。

**student_action**：依 `references/studio-patterns.md` 思考後口述：
1. 左欄有哪些**自訂頁**（頁面用途，白話）
2. 左欄什麼資料會傳給右欄 Agent（例如：訂單、心情分數）
3. 右欄 Agent 回覆或工具會寫回哪裡（例如：JSON 訂單檔）
4. 舉一個「使用者按鈕 → Agent 回應 → 左欄更新」的完整例子

**completion_phrases**：互動說完了｜左欄右欄好了｜可以下一步

**if_stuck**：

- **A 只有聊天沒有左欄** → 說明右欄單獨做什麼；若完全沒連左欄，Step 3c 會標註限制。
- **B 想講 format_extra_context** → 報告用白話（「整理成 Agent 摘要」）；技術名詞放 §5。

**agent_must_not**：不得要求改程式；不得跳 Step 3

**學生可見模板**：

```
步驟 2 · 左欄與右欄怎麼互動

請描述實際流程：左欄 UI 和右欄 Agent 怎麼連在一起。

你要做的事：告訴我——
1. 左欄有哪些自訂頁（各做什麼）
2. 左欄什麼資料會傳給 Agent
3. Agent 會寫回哪裡
4. 舉一個完整例子（按鈕 → Agent → 左欄更新）

完成後跟我說：「互動說完了」
```

---

## Step 3 · step_id: 3

**title**：成果、創新與技術

**purpose**：說明你**完成了什麼**、**和別人不一樣在哪**、**用了哪些技術**（可含 Agent Studio、Streamlit、JSON、LLM 等）。

**student_action**：口述三塊（每塊 2–4 句即可）：
1. **成果**：目前能 demo 的功能清單
2. **創新／亮點**：和範例模板或同學作品不同的設計
3. **技術含量**：用到的框架、資料格式、Agent 工具等（不必背程式碼）

**completion_phrases**：成果技術說完了｜第三步好了｜可以對齊

**if_stuck**：

- **A 創新想不出** → 可寫「整合左欄情境到 Agent 對話」等實際有做的。
- **B 技術太多** → 挑 3–5 個最重要的。

**agent_must_not**：不得虛構學生沒說的功能

**學生可見模板**：

```
步驟 3 · 成果、創新與技術

你要做的事：口述三塊——
1. 成果：目前能 demo 的功能
2. 創新／亮點：和範例或他人作品哪裡不同
3. 技術含量：用到的框架、資料、Agent 能力（各 2–4 句）

完成後跟我說：「成果技術說完了」
```

---

## Step 3c · step_id: 3c

**title**：對齊條列確認

**purpose**：把 Step 1–3 整理成報告用的條列，學生確認無誤後才進入組裝（寫檔、做圖）。

**student_action**：閱讀 Agent 輸出的**完整對齊條列**（見 `student-voice-worksheet.md` 格式）；若要改，直接指出；無誤則回「確認」。

**completion_phrases**：確認｜條列 OK｜可以組裝

**if_stuck**：

- **A 要改某一條** → 指出編號與新 wording，更新條列後再請確認。
- **B 想跳過確認** → 必須確認後才能產 `report/` 檔案。

**agent_must_not**：不得在未確認前建立 `report/專題報告.md`；不得開始 Step 4

**agent_action**（對內，不整段貼給學生）：將 Step 1–3 整理為：

```markdown
## 對齊條列（待確認）
### §1 專題介紹
- ...
### §2 左欄↔右欄互動
- ...
### §3 成果
- ...
### §4 創新
- ...
### §5 技術含量
- ...
```

**學生可見模板**：

```
步驟 3c · 對齊條列確認

我把你剛才說的整理成下面條列。請逐條看，有錯告訴我編號；都對就回「確認」。

（此處貼完整對齊條列）

完成後跟我說：「確認」
```

---

## Step 0 · step_id: 0

**title**：Preflight 檢查

**purpose**：確認專案與自訂頁清單，決定 demo 截圖最低張數。

**student_action**：（通常 Agent 已自動檢查）確認專案根有 `studio_shell/`；看 Agent 列出的**自訂頁清單**是否正確。

**agent_action**：

1. 確認 `studio_shell/pages/` 存在
2. 列出 `N_*.py` 且 **N 的數字 ≥ 4**（或課堂約定之自訂頁前綴）→ 計數 **demo 最低張數**
3. 建立 `report/assets/`（若尚無）
4. 複製 skill `assets/server-topology.png` → `report/assets/server-topology.png`
5. 寫入 `report/.capstone-progress.md`（step、自訂頁清單、demo 需求張數）
6. 讀 `.capstone-companion-check.json`；companion／Node 若 `install_failed` → 依 `companion-skills.md` 重試一次

**`.capstone-progress.md` 建議格式**（含自訂頁 ↔ demo 對照）：

```markdown
step_id: 0
demo_required: 2

## 自訂頁
| demo | 檔名 | 頁名 |
|------|------|------|
| 01 | 4_order.py | 點餐頁 |
| 02 | 5_stats.py | 統計頁 |
```

**completion_phrases**：preflight 好了｜清單對｜可以畫架構圖

**if_stuck**：

- **A 沒有自訂頁** → 提醒至少一頁自訂功能才能符合專題 demo 要求。
- **B 找不到 studio_shell** → 請先安裝 Agent Studio。

**學生可見模板**：

```
步驟 0 · 開工前檢查

我已確認你的專案與自訂頁如下：
（列出 pages/ 內自訂頁 → demo 至少需要 N 張截圖）

全班相同的 server 拓撲圖已複製到 report/assets/。

你要做的事：看清單是否正確；有漏掉的頁面跟我說。

完成後跟我說：「preflight 好了」
```

---

## Step 4 · step_id: 4

**title**：個人架構圖（Mermaid + PNG）

**purpose**：依 Step 2 互動描述，產生**平易近人**的 `project-architecture.mmd` 並轉 PNG。

**agent_action**：

1. 依 `references/studio-patterns.md` 撰寫 `report/project-architecture.mmd`
2. 執行 `scripts/render_project_diagram.py --mmd report/project-architecture.mmd --out report/assets/project-architecture.png`
3. 若 mmdc 失敗 → `references/mermaid-to-png-guide.md`

**student_action**：看 PNG 是否反映你的 App；節點用詞不對就指出。

**completion_phrases**：架構圖好了｜圖 OK｜可以截圖

**if_stuck**：

- **A mmdc 失敗** → 依 mermaid-to-png-guide 用 ChatGPT／Gemini 匯出 PNG 到 `report/assets/project-architecture.png`
- **B 節點太技術** → Agent 改為白話標籤

**agent_must_not**：節點主文字不得用 `format_extra_context` 或 `pages/4_*.py`

**學生可見模板**：

```
步驟 4 · 個人架構圖

我已依你的左欄↔右欄描述寫好 Mermaid 並產生 PNG：
- report/project-architecture.mmd
- report/assets/project-architecture.png

你要做的事：打開 PNG 看流程是否正確；不對就告訴我哪個框或箭頭要改。

完成後跟我說：「架構圖好了」
```

---

## Step 4b · step_id: 4b

**title**：Demo 截圖

**purpose**：每個**自訂頁**至少 1 張 Streamlit 畫面截圖，供報告附錄與 Word 嵌入。

**student_action**：

1. 執行 `uv run streamlit run studio_shell/app.py`
2. 逐頁進入自訂頁，用 **Win+Shift+S** 截圖
3. 存成 `report/assets/demo-01.png`、`demo-02.png` …（順序對應 preflight 清單）
4. 詳見 `references/screenshot-guide.md`

**completion_phrases**：截圖好了｜demo 圖齊了｜N 張都好了

**if_stuck**：

- **A 張數不夠** → 對照 preflight 清單補齊；**不得**進 Step 6
- **B 畫面有 api_key** → 裁切或遮罩後再存

**agent_must_not**：不得用 placeholder 假圖交件

**學生可見模板**：

```
步驟 4b · Demo 截圖

每個自訂頁至少 1 張截圖，共需 N 張：
（列出頁面 ↔ demo-XX.png 對照）

你要做的事：
1. 開 App，逐頁截圖
2. 存到 report/assets/demo-01.png …

完成後跟我說：「截圖好了」
```

---

## Step 5 · step_id: 5

**title**：產生 Markdown 報告

**purpose**：依對齊條列與 `references/report-template.md` 產出 `report/專題報告.md`（含三類圖的 `![](assets/...)`）。

**agent_action**：撰寫 MD；§2 嵌入 server 圖；§3 嵌入個人架構圖；附錄嵌入全部 demo。

**student_action**：快速掃描 MD；要改 wording 指出章節。

**completion_phrases**：MD 好了｜報告 md OK｜可以轉 PPT

**if_stuck**：

- **A 缺圖** → 回到 Step 4／4b

**學生可見模板**：

```
步驟 5 · Markdown 報告

我已產生 report/專題報告.md（含 server、架構、demo 圖片連結）。

你要做的事：打開 MD 看章節與條列是否要改 wording。

完成後跟我說：「MD 好了」
```

---

## Step 6 · step_id: 6

**title**：PPT 風格三選一

**purpose**：學生選定 html2pptx 風格；Agent 寫入 `report/ppt-style.json` 後進 Step 6b。

**student_action**：開啟 skill 內 `assets/ppt-style-picker/index.html`（見 `references/ppt-style-guide.md`）；三選一回覆 A/B/C 或代號。

**agent_action**：

1. 提供 picker 的 `file:///` 或檔案總管路徑
2. 學生回覆後驗證 style ∈ `classic-blue` | `teal-coral` | `sage-terracotta`
3. 寫入 `report/ppt-style.json`（含 `selected_at`）

**completion_phrases**：風格選好了｜我選 A｜我選 B｜我選 C｜我選 classic-blue｜我選 teal-coral｜我選 sage-terracotta

**if_stuck**：

- **A 代號不明** → 請重選 A/B/C
- **B 從 v1.1.0 續做、缺 ppt-style.json** → 插入本步再 6b/6c

**agent_must_not**：不得跳過風格選擇（除非學生已選且 json 有效）

**學生可見模板**：

```
步驟 6 · 選擇 PPT 風格

請打開風格選擇頁（路徑如下），三選一後告訴我 A、B、C 或代號：
（Agent 貼 index.html 路徑）

完成後跟我說：「風格選好了」
```

---

## Step 6b · step_id: 6b

**title**：產生 PowerPoint

**purpose**：依 `ppt-style.json` 與 `專題報告.md` 產出 `report/專題報告.pptx`。

**agent_action**：

1. 讀 `.capstone-companion-check.json`
2. Node + pptx skill 皆 `ok` → 依 `references/ppt-build-guide.md`：

```bash
node "<skill>/scripts/build_capstone_ppt_html2pptx.js" --report-dir report --skill-root "<skill>"
```

3. 否則 fallback：

```bash
uv run python "<skill>/scripts/build_capstone_ppt.py" --report-dir report
```

4. 依 `references/verification.md` § Step 6b 檢查

**student_action**：（通常 Agent 代跑）確認 `專題報告.pptx` 可開啟。

**completion_phrases**：PPT 好了｜ppt 好了｜簡報好了

**if_stuck**：

- **A html2pptx 失敗** → fallback `build_capstone_ppt.py`；告知可能為簡易版式
- **B 缺 Node** → 依 `companion-skills.md` 重試安裝一次

**agent_must_not**：不得跳過 pptx 產出

**學生可見模板**：

```
步驟 6b · 產生 PowerPoint

我已產生 report/專題報告.pptx（依你選的風格）。

你要做的事：打開 PPT 快速看一下版面。

完成後跟我說：「PPT 好了」（下一步會產 Word）
```

---

## Step 6c · step_id: 6c

**title**：Word 與交件驗收

**purpose**：產 `專題報告.docx`（**須嵌入全部 PNG**）；依 verification § Step 6c；通過後進 Step 7。

**agent_action**：

```bash
uv run python "<skill>/scripts/build_capstone_docx.py" --report-dir report
```

依 `references/verification.md` § Step 6c；失敗則 `docx-fallback.md`。

**student_action**：確認 md / pptx / docx 可開啟；Word 內看得到圖。

**completion_phrases**：三份報告好了｜交件完成｜md ppt docx 都有了

**if_stuck**：

- **A docx 沒圖** → 重跑 docx 或 fallback；**不得**進 Step 7
- **B 缺 python-docx** → `uv add python-docx`

**agent_must_not**：Step 6c 驗收未通過不得進 Step 7

**學生可見模板**：

```
步驟 6c · Word 與交件

我已產生 report/專題報告.docx（已嵌入 server、架構、全部 demo 圖）。

你要做的事：打開 Word，確認看得到圖；並確認 md / pptx / docx 三份都在。

完成後跟我說：「三份報告好了」（下一步會做專題海報）
```

---

## Step 7 · step_id: 7

**title**：專題海報（VCR 生圖）

**purpose**：將報告全文與三類架構／demo 圖合成一張**直式 2:3**展覽海報 `report/assets/專題海報.png`，供繳交與展示。

**agent_action**：

1. 確認 Step 6c 依 `references/verification.md` § Step 6c 全數通過
2. 讀 `report/專題報告.md`（或 Step 3c 對齊條列）
3. 依 `references/poster-prompt-template.md` 寫入 `report/poster-prompt.txt`
4. 組 `-ReferencePaths`：server-topology、project-architecture、全部 demo-*.png（超 16 張時依 template 截斷）
5. 讀 **vcr-imagegen** skill，執行生圖 → `report/assets/專題海報.png`
6. 若 403／缺 key → `references/poster-fallback.md`
7. 更新 `report/.capstone-progress.md` 的 `step_id: 7`
8. Step 7 依 `references/verification.md` § Step 7 檢查後才算完成

**student_action**：開啟 `專題海報.png`；確認專題名、各區文字、server／架構／demo 可辨識；有錯指出區塊。

**completion_phrases**：海報好了｜poster OK｜全部完成

**if_stuck**：

- **A 中文錯字** → edit 模式（`-ReferencePath` 現有海報 + 修正 prompt）→ `專題海報-v2.png`，確認後覆寫最終版
- **B VCR 403** → `poster-fallback.md` 網頁後備；**不得**跳過
- **C 架構圖失真** → 檢查 reference 順序與 prompt「不要改變拓撲」指示；必要時 fallback 重產

**agent_must_not**：不得虛構海報文字；不得無 reference 純生圖；不得在未產海報前標記「全部完成」

**學生可見模板**：

```
步驟 7 · 專題海報

我已依你的報告內容，用 VCR 生圖合成展覽海報：
- report/assets/專題海報.png

海報包含：專題介紹、Server 拓撲、系統架構、成果／創新／技術、Demo 縮圖。

你要做的事：打開 PNG，看文字與圖是否正確；有錯告訴我哪個區塊要改。

完成後跟我說：「海報好了」
```

---

## 步驟速查表

| 順序 | step_id | 誰主導 | 下一 step_id |
|------|---------|--------|--------------|
| 1 | 1 | 學生 | 2 |
| 2 | 2 | 學生 | 3 |
| 3 | 3 | 學生 | 3c |
| 4 | 3c | 確認 | 0 |
| 5 | 0 | Agent | 4 |
| 6 | 4 | Agent | 4b |
| 7 | 4b | 學生 | 5 |
| 8 | 5 | Agent | 6 |
| 9 | 6 | 學生 | 6b |
| 10 | 6b | Agent | 6c |
| 11 | 6c | Agent+學生 | 7 |
| 12 | 7 | Agent | （完成） |

CompanionPreflight 在 Step 1 首次觸發前執行（不佔 step_id）。
