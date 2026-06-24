# PPT 風格選擇（Step 6）

## 開啟選擇器

路徑（peas-capstone-report skill 根目錄下）：

```text
assets/ppt-style-picker/index.html
```

- **檔案總管雙擊**開啟，或
- Agent 提供 `file:///` 完整路徑

## 三選一（必選其一）

| 選項 | 代號 | 顯示名稱 | 適合 |
|------|------|----------|------|
| **A** | `classic-blue` | 經典藍 | 穩重、口試正式 |
| **B** | `teal-coral` | 青綠珊瑚 | 清新、科技專題 |
| **C** | `sage-terracotta` | 鼠尾草赤陶 | 溫暖、人文／生活類 App |

無「自訂／其他」。Agent **只接受**上表代號或 A/B/C。

## Agent 動作

1. 學生回覆後驗證代號（A→classic-blue、B→teal-coral、C→sage-terracotta）
2. 非法 → 請重選
3. 寫入 `report/ppt-style.json`：

```json
{
  "style": "classic-blue",
  "selected_at": "2026-06-23T10:00:00+08:00"
}
```

4. 進 Step 6b

## 學生可見話術（Step 6 模板用）

```text
步驟 6 · 選擇 PPT 風格

請打開風格選擇頁（我會給你檔案路徑），三選一後告訴我：
- 「我選 A」或「我選 classic-blue」
- 「我選 B」或「我選 teal-coral」
- 「我選 C」或「我選 sage-terracotta」

完成後跟我說：「風格選好了」
```
