# DOCX 後備（腳本失敗時）

## 硬性要求

**不可**交付純文字 Word。`專題報告.docx` 必須嵌入：

- `server-topology.png`
- `project-architecture.png`
- 全部 `demo-*.png`

## 首選：build_capstone_docx.py

```bash
uv run python "<skill>/scripts/build_capstone_docx.py" --report-dir report
```

需 `python-docx`：`uv add python-docx`

腳本結束時會檢查 docx 內嵌圖片數；不足則 exit 1。

## 後備 A：Pandoc

```bash
cd report
pandoc 專題報告.md -o 專題報告.docx --resource-path=.
```

開啟 Word **確認圖片存在**。若無圖 → 改後備 B 或重跑腳本。

## 後備 B：Word 手動

1. 開啟 `專題報告.md` 或已產 docx
2. 在 §2、§3、附錄各 **插入圖片** → 選 `report/assets/` 對應 PNG
3. 寬度約 15 cm、置中
4. 存檔覆蓋 `專題報告.docx`

## 驗收

用 Word 捲動全文，必須看見 server、架構、每張 demo。**無圖 = 不可交件**。
