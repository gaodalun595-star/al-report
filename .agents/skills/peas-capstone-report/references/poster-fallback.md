# 專題海報後備（Step 7）

## 首選：vcr-imagegen

見 `references/poster-prompt-template.md`。需 `VSROUTER_API_KEY`（VCR Portal `vcr_sk_...`）且課堂已開啟生圖開關。

### 常見失敗

| 現象 | 處理 |
|------|------|
| Missing API key | 設 `VSROUTER_API_KEY`；或改走下方網頁後備 |
| HTTP 403 | Portal 課堂生圖開關未開；請老師開啟或改走網頁後備 |
| HTTP 401 | key 無效或過期 |
| 中文錯字 | 學生指出區塊 → edit 模式迭代，或網頁後備重產 |

## 後備：ChatGPT 或 Gemini 網頁

1. 上傳 reference 圖（依序）：
   - `report/assets/server-topology.png`
   - `report/assets/project-architecture.png`
   - 全部 `demo-*.png`（若網頁有張數限制，至少 server + 架構 + 前幾張 demo）
2. 貼上 `report/poster-prompt.txt` 全文
3. 補充：「請依 prompt 製作直式 2:3 繁體中文展覽海報，保留參考圖中的拓撲與架構關係，不要改節點文字。」
4. 下載 PNG 存為 **`report/assets/專題海報.png`**
5. 確認檔案非空、可預覽；學生審核文字是否與報告一致

**禁止**：

- 無 reference 的純生圖（架構會失真）
- 跳過 Step 7 直接標記完成
- 在海報中寫入 api_key 或 Router IP／URL

## 與 Step 6 的關係

Step 6 三份報告驗收通過後才進 Step 7。海報後備**不影響**已完成的 md／pptx／docx。
