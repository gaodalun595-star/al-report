# Agentic AI Workshop — From Zero to Hero

- **基礎挑戰（手把手建立 Agent）（WG-01～WG-16）**：從 Python 入門到「能與模型對話、能呼叫工具、能把對話寫入／讀回檔案」的**概念與實作題**；請依題號順序完成，每題對照藍本在教師指定檔中實作與驗收。
- **進階挑戰（AI Coding 實戰）（WG-17～WG-21）**：在基礎段之上，練習上下文裁切、送模前整理、長期記憶、Skills 與多模態等**進階 Agent 行為**；題目較複雜，**建議搭配 AI 協作編程**（如 Cursor）完成；建議基礎段通過後再接續。
- **全域串流要求（WG-10 起）**：除工具判斷、工具執行、JSONL 載入、長期記憶整併等**內部步驟**可使用 `invoke` 外，凡是「最後要顯示給使用者看的 assistant 文字回覆」都必須使用 `stream` 串流輸出；不得只以 `print(response.content)` 一次印出最終回答。若特定模型／供應商路徑暫不支援串流（例如部分 vision 驗收環境），須在程式註解或驗收說明中明確標示退回 `invoke` 的原因。

## ITS Python 基礎概念

| 序 | 學習主軸（由簡入繁） | 教材統整頁檔名 |
| --- | --- | --- |
| 1 | 基礎資料與變數 | `Python-基礎資料與變數.md` |
| 2 | 運算與輸入輸出 | `Python-運算與輸入輸出.md` |
| 3 | 條件判斷與迴圈 | `Python-條件判斷與迴圈.md` |
| 4 | 資料結構（串列等） | `Python-資料結構-串列元組字典.md` |
| 5 | 函式與模組 | `Python-函式與模組.md` |
| 6 | 檔案與例外處理 | `Python-檔案與例外處理.md` |
| 7 | 類別與單元測試 | `Python-類別與單元測試.md` |

## WG 挑戰題一覽（速查）

**Python 學習主軸**欄之編號，與上方 **ITS Python 基礎概念** 表之 **「序」**（1～7）一致：**1** 基礎資料與變數、**2** 運算與輸入輸出、**3** 條件與迴圈、**4** 資料結構、**5** 函式與模組、**6** 檔案與例外、**7** 類別與測試（多項以 **、** 分隔；為主軸複選，非課堂時數分配）。

| 層級 | 編號 | 標題 | 大概內容 | Python 學習主軸（序） |
| --- | --- | --- | --- | --- |
| 基礎 | **WG-01** | 按下啟動鍵——最小進入點與第一則輸出 | `if __name__ == "__main__"`、`print()` 字面量；直接執行與被 `import` 的差異。 | 2、7 |
| 基礎 | **WG-02** | 給台詞一個名字——變數與再輸出 | 以變數保存字串，再交給 `print`（不接 API）。 | 1、2 |
| 基礎 | **WG-03** | 把身分縫進一句介紹——兩變數與 f-string | 多個 `str` 變數；`f"…{變數}…"` 組一句話輸出。 | 1、2 |
| 基礎 | **WG-04** | 替 Agent 備料——`uv add` 與頂層匯入 | 安裝套件；檔案頂層 `import`／`from … import`；終端輸出行為對齊 **WG-03**（仍不呼叫 API）。 | 5 |
| 基礎 | **WG-05** | 讀設定、不賣鑰匙——`load_dotenv` 與安全診斷 | `load_dotenv()`、`os.getenv`；印「有／無」金鑰但不洩漏內容；單行 `#` 註解。 | 1、5、6 |
| 基礎 | **WG-06** | 有通行證才開門——`if`／`else` 依金鑰分支 | 有金鑰與無金鑰兩種提示；仍不呼叫 `ChatOpenAI`。 | 3 |
| 基礎 | **WG-07** | 一行進門、其餘進房——`def main()` 與精簡進入點 | 用 `def main()` 封裝流程；進入點僅呼叫 `main()`。 | 5 |
| 基礎 | **WG-08** | 第一通打進大模型——`ChatOpenAI` 與 `invoke` | 建實例、`invoke`、讀回 `content` 並 `print`；無金鑰不呼叫。 | 5 |
| 基礎 | **WG-09** | 櫃台問答不斷線——互動迴圈與多輪 `invoke` | `while`、`input`、關鍵字結束；每輪 `invoke`（非串流）。 | 3、5 |
| 基礎 | **WG-10** | 回答像打字機——串流式 `stream` | 架構同 **WG-09**，改 `stream` + `print(..., end="", flush=True)`。 | 3、5 |
| 基礎 | **WG-11** | 短期記憶只活在當下——RAM 對話脈絡 | `HumanMessage`／`AIMessage` 串列累積；`context_messages` 先組再串流，串流後才 `append`；關閉程式即清空。 | 3、4、5 |
| 基礎 | **WG-12** | 人設寫進系統層——`SystemMessage` 與可變系統字串 | `**get_identity()`**：課堂規則＋顯示名；**【執行環境】**（`platform.system()` 動態偵測）；**【exec 注意】**（依 OS 選 shell、Python 先 **write_file** 再 **uv run**）；`system`／`history` 分離。 | 4、5 |
| 基礎 | **WG-13** | 會查表才算真 Agent——工具與 ReAct（單檔） | `@tool`、`bind_tools`、`tool_calls`、`ToolMessage`、多段 `**stream`**（累積成 `AIMessage`）；實作 `**run_react_turn**` 精神；本題不要求 JSONL／預算裁切。 | 3、4、5 |
| 基礎 | **WG-14** | 讓 Agent 有手有腳——`exec` 與檔案的 **`@tool` 最小組** | 以 LangChain **`@tool`** 暴露五支工具；**exec** 僅單行 shell、**勿 Bash**（`<<`／heredoc）；跑 Python 先 **write_file** 再 **exec `uv run python …`**；檔案操作走專用工具；workspace 路徑限制與 UTF-8 子程序輸出。 | 4、5、6、7 |
| 基礎 | **WG-15** | 對話落盤、人設不留痕——JSONL 先寫檔 | 在 **WG-12** 送模結構下整檔覆寫 JSONL（首行 `metadata`；**對話列** `**user`／`assistant`／`tool`** 對齊 **WG-13**／**WG-14** 之 **ReAct** 鏈）；啟動**不**讀舊檔；**不**寫 `SystemMessage`。 | 5、6 |
| 基礎 | **WG-16** | 冷啟動撿回昨日脈絡——JSONL 載回 | 啟動讀檔還原 `**history`**（`**assistant**` 列可還原含 `**tool_calls**` 之 `**AIMessage**`，`**tool**` 列還原 `**ToolMessage**`，對齊 **WG-15** 完整版）；壞行略過；關閉再開可接續。 | 6 |
| 進階 | **WG-17** | 視窗太窄先裁舊帳——字元預算與整併邊界 | `estimate_message_tokens`、`pick_consolidation_boundary`、`last_consolidated`；超線裁切 `**past`**；成本含 `**ToolMessage**`（與 **WG-13**／**WG-14** 銜接）。 | 3、4、5 |
| 進階 | **WG-18** | 送模前先洗對話簿——transcript 修復與工具輸出預算 | 實作 `messages_for_model` 管線（孤兒 tool 清理、缺洞補齊、tool 截斷、舊 tool 摘要、全對話字元預算）。 | 4、5、6 |
| 進階 | **WG-19** | 舊對話濃縮成長期備忘——整併與每輪讀回組裝 | `memory/MEMORY.md`（精簡備忘，非對話抄寫）、`HISTORY.md`；超線時 **consolidation** `invoke`；`## Long-term Memory` 併入 **system**；送主模型前壓至 **≤ TOKEN_BUDGET//2**。 | 5、6 |
| 進階 | **WG-20** | 技能卡進工具箱——最小 SkillsLoader 與 system prompt 注入 | `skills/<name>/SKILL.md`、frontmatter 摘要、workspace／builtin 合併、同名覆蓋；`**build_system_prompt(loader)`** 依序：**課堂基底**（`**get_identity()`**）→ **長期記憶**（若有）→ `**# Active Skills`**（`always` 正文）→ `**# Skills**`（繁中引導＋摘要）；大段間 `**---**`；並**銜接 WG-13／WG-14**：各 **`BaseTool`** 之輸入 **JSON Schema**（或等價 `parameters`）、`**cast_params`／`validate_params**`、在 **`invoke` 實作前** 的 **`prepare_tool_call`**（或等價流程，**不**要求自訂 `Tool`／`ToolRegistry` 類別）。 | 4、5、6 |
| 進階 | **WG-21** | 眼睛也進對話——多模態附圖、`image_path` 與 JSONL 載回閉環 | JSONL 之 `**user**` 列僅存 **`image_path`**／`**media_type**`（**不**存長 base64）；冷啟動載入 `**history**` 為**純文字占位**；**送模層** `**messages_for_model**`：**僅本輪**可含 data URL 圖區塊、**歷史**舊附圖不得重送；`**open(..., "rb")**`／base64 僅在本輪組圖時使用；須使用支援 **vision** 之模型。 | 4、5、6 |

---


# 第一部分 · 基礎挑戰（手把手建立 Agent）（WG-01～WG-16）

---

## Challenge WG-01：按下啟動鍵——最小進入點與第一則輸出

### 情境

暖身用：讓學生確認專案環境能執行一支極短檔案，並習慣「只有直接跑這個檔時，才執行區塊裡的程式」。**不**在本題要求讀環境變數、迴圈，也不要求把邏輯拆進自訂的 `main()` 函式（留給後續單元）。通過後可銜接 **WG-02**（以變數保存問候語再輸出）。**本題驗收**以下方藍本為準；若教學檔已擴寫，驗 WG-01 時可請學生暫時只保留藍本兩行，或由教師口頭約定「整檔跑通即可，但理解題仍對準藍本兩行」。

### 規格

- 使用 `if __name__ == "__main__":` 作為程式進入點慣例。
- 進入點區塊內呼叫 `print`，引數為字串字面量（藍本為 `"Hello, World!"`；若要本土化可改繁中招呼句，但須仍為單一 `str` 字面量）。
- 作答與驗收以**教師指定檔名**為準（依班級流程擇一即可）。

### 驗收條件

- 在專案根目錄以 `uv run <教師指定檔名>`（或教師指定之檔名）執行，終端機出現預期字樣。
- 能說明：`print(...)` 括號內的資料，在 Python 裡屬於哪一種基本型態？
- 能一句話說明：為什麼要把 `print` 寫在 `if __name__ == "__main__":` **底下**（與「被別的檔 `import` 時不要自動跑」有關即可）。
- 能描述一個**邊界**：若有另一支程式只寫了 `import <你的模組檔名>`（檔名依實際為準），執行那支程式時，你預期終端會不會出現 `Hello, World!`？為什麼？

### 藍本對應程式

```python
if __name__ == "__main__":
    print("Hello, World!")
```


---

## Challenge WG-02：給台詞一個名字——變數與再輸出

### 情境

在 **WG-01** 能跑、能說明進入點之後，在**進入點區塊裡**把「要印的字」存進**變數**再印出。終端機看到的問候句應與先前相同，避免學生以為行為改壞了。通過後可銜接 **WG-03**（名稱獨立成變數，再以 f-string 組句）。

### 規格

- 在 `if __name__ == "__main__":` **底下**（與藍本相同縮排層級）：先以賦值建立一個變數（藍本為 `message`），型別為 `str`，內容為問候字串；再呼叫 `print(message)`。
- 變數與 `print` 皆須落在進入點區塊內（不把問候字串留在「只有被 `import` 時也會執行」的模組頂層賦值）。
- **不**在本題加入 `input()`、迴圈、自訂函式或讀檔。

### 驗收條件

- `uv run <教師指定檔名>` 終端機仍出現預期問候字樣。
- 能說明：`message`（或自訂的同名變數）綁到的是哪一種基本型態？
- 能連結回 **WG-01**：為什麼現在 `print` 的括號裡**不必**再寫字面量 `"Hello, World!"` 也能印出同樣結果？
- **邊界**：若把區塊內的 `message = "Hello, World!"` 改成 `message = "Hi"`，其餘行不變，你預期輸出會變成什麼？為什麼？
- **邊界**：若有另一支程式只寫了 `import <你的模組檔名>`（檔名依實際為準）並執行，你預期此時模組裡是否一定已經有 `message` 這個名稱？為什麼？（與進入點區塊有沒有跑過有關即可。）

### 藍本對應程式

```python
if __name__ == "__main__":
    message = "Hello, World!"
    print(message)
```


---

## Challenge WG-03：把身分縫進一句介紹——兩變數與 f-string 組句

### 情境

在 **WG-02** 已會把整句問候存進 `message` 之後，進一步把「名字／稱呼」獨立成一個變數，再用**字串模板**把名字嵌進句子裡。這樣之後只改名字變數，不必整句重抄。呼應課堂裡常見的「小助手／代理人名稱」設定。

### 規格

- 在 `if __name__ == "__main__":` 區塊內：
  - 先建立一個 `str` 變數表示名稱或稱呼（藍本為 `agent_name`；字串內容可改，但須仍為 `str`）。
  - 再建立 `message`，使用 **f-string**（字串前綴 `f`），並以 `{agent_name}`（或與你變數名一致的大括號嵌入）把名稱嵌進整句問候裡。
  - 最後 `print(message)`。
- **賦值順序**：凡在右側運算式會讀到的變數，必須**先**完成賦值（藍本為 `agent_name` 在 `message` 之上）。
- **不**在本題改用 `+` 硬串、`%` 或 `format()` 取代 f-string（避免與本題主軸混淆）；不加入 `input()`、迴圈、自訂函式。

### 驗收條件

- `uv run <教師指定檔名>` 終端機出現**一整句**問候，且句中可看出你設定的名稱或稱呼（與藍本精神一致即可）。
- 能說明：`message` 這一行裡，大括號 `{...}` 在執行時會被替換成什麼？
- 能說明：為什麼 `agent_name`（或你的對應變數）那一行**必須**寫在組出 `message` 的那一行**上面**？（若反過來寫會發生什麼，用自己的話即可。）
- **邊界**：只把 `agent_name` 的字串改成另一個名字、其餘不變，你預期輸出哪裡會變、哪裡不會變？

### 藍本對應程式

```python
if __name__ == "__main__":
    agent_name = "法鬥超人"
    message = f"Hello, 我是{agent_name}，很開心認識你!"
    print(message)
```


---

## Challenge WG-04：替 Agent 備料——`uv add` 安裝依賴與頂層匯入（終端輸出對齊 WG-03）

### 情境

後續單元會用到 **OpenAI 相關的 LangChain 整合**（套件發佈名為 `langchain-openai`）以及從 `**.env` 讀設定**（常搭配 `python-dotenv`）。本題**一次**完成兩件事，讓「套件進專案」與「程式裡怎麼引用名稱」連在一起：（1）在已用 **uv** 管理的專案**根目錄**用 `**uv add`** 把兩套件寫進 `pyproject.toml`（並由 uv 維護 lock／環境）；（2）在示範檔（藍本見下方）**最上方**寫入兩行 `from … import`，**進入點內**仍只做與 **WG-03** 相同的問候（`agent_name`、f-string `message`、`print`）——**先不要**建立 `ChatOpenAI`、打 API、也不要求建立或提交 `.env` 內容，避免與下一階段混線。通過後可銜接 **WG-05**（在進入點呼叫 `load_dotenv`、用 `os.getenv` 讀 `OPENAI_API_KEY`，並以**不暴露完整金鑰**的方式印出診斷）。

### 規格

**依賴（專案根）**

- 工作目錄須為本專案**根目錄**（與 `pyproject.toml` 同層）。
- 以**一條指令**同時加入兩個套件（套件名以 PyPI 為準）：`uv add langchain-openai python-dotenv`
- 執行後 `pyproject.toml` 的 `[project]` → `dependencies` 中應出現上述兩個套件名（版本約束由 uv 寫入即可，不必手改）。

**示範檔結構**

- 在 `if __name__ == "__main__":` **之上**（模組頂層、無額外縮排）：
  - `from langchain_openai import ChatOpenAI`
  - `from dotenv import load_dotenv`
- `if __name__ == "__main__":` 區塊內與 **WG-03** 相同精神：先 `agent_name`（`str`），再以 **f-string** 組出 `message`，最後 `print(message)`。
- **不要求**在區塊內呼叫 `load_dotenv()`、不要求建立 `ChatOpenAI` 實例或呼叫 `invoke`（留給後續 Challenge）；頂層匯入的 `ChatOpenAI`／`load_dotenv` 執行時**可尚未被使用**。

### 驗收條件

**依賴與環境**

- 能說明：為什麼要在「專案根」執行 `uv add`，而不是在任意資料夾執行？
- 終端機曾成功跑過 `uv add langchain-openai python-dotenv`（或同等效果：兩套件已列於 `dependencies` 且 lock／環境一致）；若專案**已**含兩依賴，能說明「再跑一次 `uv add` 通常會做什麼」（例如解析／同步，而非重複亂裝）。
- 在專案根執行下列**其中一種**並成功（無 `ModuleNotFoundError`）：
  - `uv run python -c "import langchain_openai; import dotenv; print('deps-ok')"`
  - 或：`uv run python -c "import langchain_openai; from dotenv import load_dotenv; print('deps-ok')"`
- **邊界**：若只在某子資料夾執行 `uv add`、該處沒有 `pyproject.toml`，你預期會發生什麼？（用自己的話即可。）

**示範檔行為與理解**

- 在專案根執行 `uv run <教師指定檔名>`（或教師指定之同結構檔名），終端機出現**一整句**問候，且句中可看出 `agent_name` 設定的名稱或稱呼（與 **WG-03** 精神一致即可）。
- 能說明：`from langchain_openai import ChatOpenAI` 這一行裡，`ChatOpenAI` 是從哪一個**已安裝套件**（PyPI 上的發佈名稱）拿出來的名稱？
- 能說明：`from dotenv import load_dotenv` 對應的是哪一個 PyPI 套件？若程式裡**沒有**呼叫 `load_dotenv()`，執行時**環境變數是否會因此自動從 `.env` 載入**？（用自己的話即可。）
- **邊界**：若把兩行頂層 `from … import` 整段刪掉、進入點內容不變，在已安裝兩依賴的專案裡，`uv run <教師指定檔名>` 是否仍可能正常輸出問候？為什麼？（與「有沒有用到那些名稱」有關即可。）

### 藍本對應

**指令與快速驗收（專案根）**

```bash
uv add langchain-openai python-dotenv
```

```bash
uv run python -c "import langchain_openai; import dotenv; print('deps-ok')"
```

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

if __name__ == "__main__":
    agent_name = "法鬥超人"
    message = f"Hello, 我是{agent_name}，很開心認識你!"
    print(message)
```


---

## Challenge WG-05：讀設定、不賣鑰匙——`load_dotenv`、讀環境變數與安全診斷輸出

### 情境

專案裡常把 **API 金鑰**放在 `**.env`**（不進版控），程式執行時要「載入 `.env` 到環境」再「依名稱讀出字串」。**請在專案根目錄**（與 `pyproject.toml` 同層）**新建一個檔案** `**.env`**，用純文字編輯器寫入至少一行 `OPENAI_API_KEY=你的金鑰`（實際金鑰由你或課堂提供；**不要**把含真金鑰的 `.env` 交進版控）。本題只練這一段：**先**在進入點呼叫 `**load_dotenv()`**，再用 `**os.getenv("OPENAI_API_KEY")**` 讀到變數（可能為 `None` 或空字串）。終端機上**只能**用「有／無」或**不會暴露金鑰本體**的短句說明狀態——**禁止**把金鑰整串 `print` 出來（螢幕錄影、截圖外洩風險）。**本題另一重點**：用 **單行註解符號 `#`**（寫在該行最前面）把 **WG-04** 的問候程式「關起來不執行」——執行時 Python 會**略過**這幾行，等於暫時從流程裡拿掉，但程式碼仍留在檔案裡方便日後取消註解再接回。通過後可銜接 **WG-06**（用 `if`／`else` 依有無金鑰印不同提示）。**本題不要求**呼叫 `ChatOpenAI` 或 `invoke`。

### 規格

- **檔案**：在**專案根目錄**建立新檔 `**.env`**（檔名開頭為點號；與示範檔 同層、不在子資料夾），內容至少含 `OPENAI_API_KEY=` 與對應值；若課堂採「僅用系統環境變數、不建檔」可經教師口頭約定略過建檔步驟，但驗收時仍須能說明「有／無 `.env` 時 `getenv` 差異」。
- 在示範檔（藍本見下方）頂層新增 `**import os**`（與既有兩行 `from … import` 並列，順序可為：`ChatOpenAI`、`load_dotenv`、`os`）。
- 在 `if __name__ == "__main__":` 區塊內，**第一行**呼叫 `**load_dotenv()`**（讓後續 `os.getenv` 能讀到 `.env` 寫入的變數）。
- 以變數（例如 `api_key`）保存 `**os.getenv("OPENAI_API_KEY")**` 的結果。
- **診斷輸出**：僅能印出「已設定／未設定」或等價語意，**不得**在 `print`／f-string 中嵌入 `{api_key}` 或任何會印出金鑰本體的寫法。
- **問候與註解**：本題藍本將 **WG-04** 的 `agent_name`／問候／`print(message)` **三行各加上行首 `#`**（**單行註解**），使這段程式**不被執行**；註解僅作用於**該行**（要停用多行就逐行加 `#`，或之後再學區塊註解）。先專心練環境讀取與一行診斷；**WG-06** 起再視藍本決定是否恢復問候（取消 `#` 或改寫）。

### 驗收條件

- 已在**專案根**建立 `**.env`** 新檔並寫入 `OPENAI_API_KEY`（或經教師同意改以系統環境變數測試，但仍能連結回說明「根目錄 `.env`」的用途）。
- 在專案根執行 `uv run <教師指定檔名>`（或教師指定檔名），終端出現**一行**金鑰狀態診斷（有／無或等價），**不**出現完整 `sk-…` 或長密文本體（亦**不**在 f-string 內嵌 `{api_key}`）。
- 能說明：`load_dotenv()` 放在區塊開頭與放在 `print` 之後，對「`os.getenv` 讀不讀得到 `.env`」可能差在哪？
- **邊界**：若專案根**沒有** `.env` 檔、也沒在系統預先匯出 `OPENAI_API_KEY`，你預期 `os.getenv("OPENAI_API_KEY")` 多半是什麼？診斷行應長什麼樣？
- 能說明：藍本裡問候那幾行前面的 `**#`** 有什麼效果？若把其中一行的 `#` 刪掉、其餘仍保留註解，執行時可能發生什麼事？

### 藍本對應

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OPENAI_API_KEY：{'已設定' if api_key else '未設定'}")
    # agent_name = "法鬥超人"
    # message = f"Hello, 我是{agent_name}，很開心認識你!"
    # print(message)
```


---

## Challenge WG-06：有通行證才開門——`if`／`else` 依金鑰有無分支

### 情境

在 **WG-05** 已能讀到金鑰變數的前提下，使用者體驗上常希望：**有金鑰**與**沒金鑰**時，程式用**不同的一句話**提醒下一步（例如可呼叫模型 vs. 請先設定環境）。本題在相同檔案結構上加入 `**if api_key:`** 與 `**else:**`，兩分支各至少 `**print` 一行**且內容**不同**；**仍不**建立 `ChatOpenAI` 或呼叫 `invoke`。通過後可銜接 **WG-07**（收成 `def main()`）。

### 規格

- 延續 **WG-05**：頂層匯入、`load_dotenv()`、`api_key = os.getenv("OPENAI_API_KEY")`。
- 以 `**if api_key:`**／`**else:**` 包住（或緊接其後）**兩組不同的**狀態 `print`（分支內各至少一行；文字由教學約定，但語意須區分「有讀到可用金鑰」與「沒讀到」）。
- **診斷安全**：與 **WG-05** 相同，**任何**分支都**不得**印出完整金鑰字串（**不**在 f-string 內嵌 `{api_key}`）。
- **問候**：藍本將問候維持為**註解**（與 **WG-05** 相同）；若教師希望兩分支後都印問候，可取消註解並自行對齊驗收。

### 驗收條件

- `uv run <教師指定檔名>`：無金鑰時與有金鑰時（或暫時改環境／`.env`），**狀態提示行**文字不同，且皆**不**洩漏完整金鑰。
- 能指出：`if` 的條件式為何能同時涵蓋 `None` 與空字串兩種「沒有可用金鑰」的情況？（用自己的話即可。）
- **邊界**：若誤寫成 `if api_key == True:`，與 `if api_key:` 在本題情境下可能差在哪？（提示：變數型態。）

### 藍本對應

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("OPENAI_API_KEY：已設定")
    else:
        print("未設定 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
    # agent_name = "法鬥超人"
    # message = f"Hello, 我是{agent_name}，很開心認識你!"
    # print(message)
```


---

## Challenge WG-07：一行進門、其餘進房——收成 `def main()` 與精簡進入點

### 情境

當進入點區塊變長，慣例會把主要流程收進 `**def main():**`，讓 `if __name__ == "__main__":` **只負責呼叫** `main()`，方便閱讀與之後擴充（例如加參數、測試）。本題把 **WG-06** 的邏輯移入 `**main()`**，並依藍本在 **無金鑰**時 `**return`**、狀態字樣可與 **WG-06** 台詞不同（**以本題藍本為準**）；頂層僅保留匯入與進入點一行呼叫。

### 規格

- 新增 `**def main() -> None:`**（`-> None` 可選，若教學未教型別註解可省略，但藍本保留示範）。
- `**main` 函式內**含：`load_dotenv()`、`api_key`、依有無金鑰之 `**if`／`else`**；**無金鑰**時在 `else` 印提示後 `**return`** 結束（**不**往下執行）。問候相關程式在藍本中**維持註解**（與 **WG-06** 相同）。
- `if __name__ == "__main__":` 區塊內**僅** `main()`（或等價單一呼叫），**不**再堆疊其他可執行述句。
- **不要求**新增其他檔案或改 `pyproject.toml`。

### 驗收條件

- `uv run <教師指定檔名>` 在「有金鑰／無金鑰」兩種情境下，**分支與早退**（`return`）行為與**本題藍本**一致；狀態字樣以藍本為準（不必與 **WG-06** 逐字相同）。
- 能說明：為什麼「只把程式搬進函式」通常**不會**改變執行結果，但對維護有幫助？
- **邊界**：若誤把 `load_dotenv()` **只**放在 `if __name__` 區塊、卻放在 `main()` 呼叫**之後**，會發生什麼事？

### 藍本對應

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("已讀到 API 金鑰設定（內容不顯示）；後續可呼叫模型。")
    else:
        print("尚未讀到 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
        return
    # agent_name = "法鬥超人"
    # message = f"Hello, 我是{agent_name}，很開心認識你!"
    # print(message)

if __name__ == "__main__":
    main()
```


---

## Challenge WG-08：第一通打進大模型——`ChatOpenAI` 與 `invoke` 最小呼叫

### 情境

依賴已在 **WG-04** 安裝、環境讀取與分支在 **WG-05～07** 演練過；本題在**有金鑰**時實際建立 `**ChatOpenAI`**、送一句**繁體中文**提示給 `**invoke`**，並把模型回覆的**文字內容**印到終端。**無金鑰**時**不得**呼叫 API：先印提示再 `**return`**（與 **WG-07** 早退寫法一致）。呼叫 API 需要**網路**，且可能**計費**；驗收前請確認課堂約定。通過後可銜接 **WG-09**（`**while`** 互動迴圈 + `**input()**`，每輪 `**invoke**`），再銜接 **WG-10**（同一迴圈骨架下改 `**stream`** 串流輸出）。

### 規格

- 延續 **WG-07** 結構：`def main()`、`load_dotenv`、`api_key`。
- **流程（藍本採「先判斷、再主流程」）**：
  - `**if api_key:`** 僅印**一行**狀態（表示讀到金鑰、可進入後續；**不**在此巢狀寫入 `ChatOpenAI`／`invoke`）。
  - `**else:`** 印「尚未讀到…」類訊息後 `**return**`，確保不會執行到 API 相關程式。
  - 上述 `if`／`else` **之後**（與 `if api_key` **同層**、且在 `return` 之後自然只會在有金鑰時執行）：建立 `**ChatOpenAI(model="gpt-4o-mini", temperature=0.2)`**，`**invoke**` 繁中提示，`**print(response.content)**`。
- **問候**：本題藍本**不含** **WG-03** 問候（前幾題若已註解問候，本題延續「最小呼叫」主軸即可）。
- **安全**：任何分支仍**不得** `print` 完整 `OPENAI_API_KEY`。

### 驗收條件

- 有設定有效 `OPENAI_API_KEY` 時，`uv run <教師指定檔名>` 會印出**至少一行**模型產生的繁中文本（非空），且**不**含完整金鑰字串。
- 未設定金鑰時，程式**不**拋出未捕捉的 API 認證錯誤（應走 `else` 並 `**return`** 早退，**不**執行 `ChatOpenAI`／`invoke`），且終端仍友善提示。
- 能說明：`invoke` 的回傳值型別為何通常**不是**純 `str`，卻仍可用 `.content` 取出要給使用者看的文字？
- **邊界**：若金鑰錯誤或網路中斷，你預期程式可能在哪一行附近失敗？（不要求本題寫完整 `try`／`except`，能說出觀察點即可。）

### 藍本對應

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print("已讀到 API 金鑰設定（內容不顯示）；後續可呼叫模型。")
    else:
        print("尚未讀到 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
        return

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    response = llm.invoke(
        "用一句繁體中文自我介紹，並說你準備好回答使用者的問題了。"
    )
    print(response.content)

if __name__ == "__main__":
    main()
```


---

## Challenge WG-09：櫃台問答不斷線——互動迴圈與多輪 `invoke`

### 情境

**WG-08** 只呼叫模型**一次**就結束。實務上常希望終端機像「聊天程式」：**重複**讀使用者打字、送進模型、印回覆，直到使用者輸入離開指令。本題在 **WG-08** 的早退與 `**ChatOpenAI` 實例**之後，加上 `**while True`** 與 `**input()**`；每輪用 `**invoke**` 傳入使用者這一行字串，再 `**print**` 助手回覆的 `**content**`。這樣 **「條件判斷與迴圈」** 單元的 `**while`** 與 **「運算與輸入輸出」** 單元的 `**input()`** 會在同一份小程式裡**一次串起來**。通過後可銜接 **WG-10**（同一迴圈，改為 `**stream`** 串流印出）。

### 規格

- 延續 **WG-08**：`def main()`、`load_dotenv`、無金鑰則印提示後 `**return`**（**不**呼叫 API）。
- 有金鑰時建立 `**ChatOpenAI(model="gpt-4o-mini", temperature=0.2)`**（模型名可依課程替換，驗收以藍本為準）。
- `**while True:**` 迴圈內：
  - 用 `**input()**` 讀一行使用者輸入（藍本提示字可自訂，須讓學生知道輪到誰打字）。
  - 若使用者輸入為**結束指令**（藍本：`quit`／`exit`／`q`，**不分大小寫**可比對），印一句告別並 `**break`** 離開迴圈。
  - 可選：若使用者只送**空白**，**不**呼叫 API，`**continue`** 進下一輪（藍本採此行為）。
  - 否則 `**response = llm.invoke(使用者字串)**`，再印 `**response.content**`（建議加前綴如「助手：」方便對齊終端閱讀）。
- **本題不要求** `stream`／`astream`（留給 **WG-10**）；**不要求**對話歷史串列（留給 **WG-11**）、**不要求**寫入檔案。

### 驗收條件

- 有金鑰時，`uv run <教師指定檔名>` 可進入迴圈：至少手動輸入**兩輪**一般問題，助手回覆皆為可讀繁中（或課堂約定語言），且**不**洩漏金鑰。
- 輸入結束指令後程式**正常結束**（無未捕捉錯誤），且**不**再呼叫下一輪 API。
- 能說明：為什麼用 `**while True`** 搭配 `**break**`，而不是只寫一個「條件式 `while`」？
- **邊界**：若使用者第一輪就直接輸入結束指令，你預期會印幾次模型回覆？為什麼？

### 藍本對應

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print("已讀到 API 金鑰設定（內容不顯示）；進入對話（輸入 quit / exit / q 結束）。")
    else:
        print("尚未讀到 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
        return

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    while True:
        user_text = input("你：").strip()
        if user_text.lower() in ("quit", "exit", "q"):
            print("再見！")
            break
        if not user_text:
            continue

        response = llm.invoke(user_text)
        print("助手：", response.content)

if __name__ == "__main__":
    main()
```


---

## Challenge WG-10：回答像打字機——串流式回答（`stream`）

### 情境

**WG-09** 每輪要等模型**整段**生成完才一次印出；使用者體感上，改成**邊生成邊出字**會更像常見的聊天介面。本題**保留 WG-09 的迴圈與 `input`／離開指令邏輯**，只把「一輪助手回覆」從 `**invoke` + `print(整段)`** 改成對同一使用者字串呼叫 `**llm.stream(...)**`，並在 **Python 層**用 `**for chunk in ...:`** 逐塊取出文字，以 `**print(..., end="", flush=True)**` 接續印在**同一行或連續輸出**（藍本於串流結束後 `**print()` 換行**）。需**網路**，且可能**計費**。通過後可銜接 **WG-11**：在**記憶體**裡用訊息**串列**保留多輪脈絡，並維持 `**llm.stream(context_messages)`**（`**context_messages = [*messages, human_message]**`）的串流輸出（**關閉程式即消失**，仍**不**寫入檔案）。

### 規格

- 架構與 **WG-09** 相同：早退、`llm` 建立、`while True`、`input`、結束指令、`continue` 空輸入。
- **差異**：將 `llm.invoke(user_text)` 改為 `**for chunk in llm.stream(user_text):`**（或課程約定之等價寫法），僅印出有內容的 `**chunk.content**`（若某版為 `None` 則略過），並以 `**end=""**`、`**flush=True**` 串接；該輪結束後 `**print()**` 補一行換行。
- **不要求**改為 async／`astream`（除非教師另行升級）；**不要求** WebSocket 或前端。
- **不要求**跨輪 `**messages`** 脈絡串列（留給 **WG-11**）。

### 驗收條件

- 有金鑰時，連續輸入至少一輪一般問題，終端可觀察到助手回覆**分段出現**（與 **WG-09** 一次跳整段不同），且結尾換行合理。
- 結束指令行為與 **WG-09** 一致（離開迴圈、不再呼叫下一輪）。
- 能說明：`**invoke`** 與 `**stream**` 在「你什麼時候拿到完整文字」這點有什麼不同？
- **邊界**：若某一輪網路中斷，你預期錯誤比較可能發生在 `**for` 迴圈內**還是**外**？（不要求本題完整 `try`／`except`，能指認即可。）

### 藍本對應

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print("已讀到 API 金鑰設定（內容不顯示）；進入對話（串流輸出；輸入 quit / exit / q 結束）。")
    else:
        print("尚未讀到 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
        return

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    while True:
        user_text = input("你：").strip()
        if user_text.lower() in ("quit", "exit", "q"):
            print("再見！")
            break
        if not user_text:
            continue

        print("助手：", end="", flush=True)
        for chunk in llm.stream(user_text):
            if chunk.content:
                print(chunk.content, end="", flush=True)
        print()

if __name__ == "__main__":
    main()
```


---

## Challenge WG-11：短期記憶只活在當下——對話脈絡（記憶只在 RAM）

### 情境

**WG-09～10** 每輪只把「當下這一句使用者輸入」送進模型，模型**看不到**先前幾輪說過什麼，因此無法延續暱稱、前情提要或指代詞。實務上會在程式裡用一個**存在記憶體中的串列**（本題稱 `**messages`**）依序放入 `**HumanMessage**`（使用者）與 `**AIMessage**`（助手），**持續累積**「到目前為止」的對話時間軸。

本題**延續 WG-10 的終端體感**：仍以 `**stream`** 邊生成邊 `**print(..., end="", flush=True)**`；差別是 `**stream` 的參數改為「本輪要給模型看的那份訊息串列」**。課堂建議另用變數名 `**context_messages`** 專指**送進 `llm.stream(...)` 的那一個引數**：在 **WG-11** 裡，先把本輪字句建成 `**human_message = HumanMessage(...)`**，再 `**context_messages = [*messages, human_message]**`（**新開一份串列**：前半是**已結束回合**的累積 `**messages`**，最後一則是本輪使用者；**此時尚未**把 `**human_message`** `**append` 進 `messages**`）。串流結束後，再依序 `**messages.append(human_message)**`、`**messages.append(AIMessage(...))**`，下一輪脈絡才不會缺字。**WG-12** 起會改以 `**history`** 累積對話訊息，並加上 `**system_message**`，送模 `**[system_message, *history, human_message]**`（**WG-15** 起 `**history`** 可含 **WG-13** 之 `**ToolMessage`** 鏈）；到 **WG-17** 再把其中的「過去段」換成裁切後的 `**past`**，即 `**context_messages = [system_message, *past, human_message]**`，與**完整**累積的 `**history`** **脫鉤**，以練習預算裁切。

本題**刻意不做**寫檔／讀檔：關掉程式或當機後，脈絡**立刻消失**——用來參考「RAM 內短期記憶」與「寫進檔、下次載回」的差異。通過後可銜接 **WG-12**（`**SystemMessage`** 與 `**get_identity()**`，送模 `**[system_message, *history, human_message]**`，可先仍**不**寫 JSONL）、再 **WG-13**（工具 **ReAct**）、再 **WG-14**（檔案／`exec` 工具組，選修併專案）、再 **WG-15**（對話**寫入** JSONL）、再 **WG-16**（開機**讀回**接續）。

### 規格

- 延續 **WG-07～10**：`def main()`、`load_dotenv`、無金鑰則印提示後 `**return`**；有金鑰時建立 `**ChatOpenAI**`；`**while True**`、`input()`、結束指令（`quit`／`exit`／`q`，不分大小寫）、空白行 `**continue**`。
- 在進入迴圈前（或 `llm` 建立後）宣告 `**messages**` 為**空串列**，型別上可視為「依序儲存多則 `**langchain_core.messages`** 中的 `**HumanMessage`／`AIMessage**`」。
- 每一輪有效使用者輸入：
  1. `**human_message = HumanMessage(content=...)**` — 先把本輪使用者句建成物件（**尚未**寫入累積串列）。
  2. `**context_messages = [*messages, human_message]`**：**本輪送進 `llm.stream` 的引數**；為**新串列**，內容等於「**已結束的 `**messages`**」加上本則 `**human_message**`」，用來參考後續題組「累積一份、送模另一份」的拆法。
  3. `**print("助手：", end="", flush=True)**`（與 **WG-10** 對齊前綴習慣）。
  4. `**for chunk in llm.stream(context_messages):`**：將**本輪 `context_messages` 所代表的脈絡**送進模型；對有內容的 `**chunk.content`** 以 `**print(..., end="", flush=True)**` 串接；同時把片段累積到一字串變數（例如 `**reply_parts**` 再 `**"".join(...)**`）。
  5. `**print()**` 補換行。
  6. `**assistant_message = AIMessage(content=完整助手字串)**` 後，依序 `**messages.append(human_message)**`、`**messages.append(assistant_message)**` — 助手內容必須與終端印出的全文一致，否則下一輪模型讀到的歷史會與你實際看到的不符。
- **禁止**：把 `messages` 寫入磁碟、或從檔案載入歷史（留給 **WG-15**／**WG-16**）。
- **不要求**：自訂 **SystemMessage**／人設（留給 **WG-12**；本題可選加，非驗收重點）。

### 驗收條件

- 有金鑰時，至少一輪助手回覆在終端為**分段／逐塊出現**（與 **WG-10** 類似的串流體感），且換行合理。
- 有金鑰時，連續兩輪以上對話，**第二輪起**模型回覆能合理承接**第一輪**給過的資訊（例如先請助手記住一個自訂代號或數字，下一輪再問「剛才那個是多少」— 由教師或學生自訂台詞，**不**在教案背誦標準答案）。
- 能說明：為什麼 `**messages`** 要同時放**使用者**與**助手**的訊息，而不是只放使用者的句子？
- **邊界**：若使用者**直接關閉終端**而不輸入結束指令，重開程式後，你預期上一輪的對話還在不在？為什麼？
- **邊界**：若某一輪在 `**llm.stream(context_messages)`** 進行中程式就當掉（**尚未**執行到 `**messages.append(human_message)`**），你預期 `**messages**` 裡會不會出現本輪使用者那句？為什麼？（能描述即可，不要求 `try`／`finally`。）

### 藍本對應

**示範檔全檔**

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from dotenv import load_dotenv
import os

def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print(
            "已讀到 API 金鑰設定（內容不顯示）；進入對話（脈絡僅存於記憶體；關閉程式即消失；輸入 quit / exit / q 結束）。"
        )
    else:
        print("尚未讀到 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
        return

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    messages: list[BaseMessage] = []

    while True:
        user_text = input("你：").strip()
        if user_text.lower() in ("quit", "exit", "q"):
            print("再見！")
            break
        if not user_text:
            continue

        human_message = HumanMessage(content=user_text)
        # 本輪送模：舊回合在 messages，本則使用者僅先進 context_messages；WG-17 起改為 [system_message, *past, human_message]
        context_messages = [*messages, human_message]
        print("助手：", end="", flush=True)
        reply_parts: list[str] = []
        for chunk in llm.stream(context_messages):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                reply_parts.append(chunk.content)
        print()
        assistant_text = "".join(reply_parts)
        assistant_message = AIMessage(content=assistant_text)

        messages.append(human_message)
        messages.append(assistant_message)

if __name__ == "__main__":
    main()
```


---

## Challenge WG-12：人設寫進系統層——SystemMessage 與可變系統字串

### 情境

**WG-11** 已能以 `**HumanMessage`／`AIMessage`** 串列維持多輪脈絡，但尚未在送模串列**最前**固定放入「課堂規則、人設、安全邊界」等**系統層**文字。實務上常把這些收斂成 `**get_identity()`** 回傳的一整段字串，再包成 `**SystemMessage**`，且**不**跟著 `**user`／`assistant`** 逐句寫進對話檔（若日後有 **JSONL**，仍只存人機回合）。

本題在**延續 WG-11 的串流節奏**、且**仍可不寫入磁碟**的前提下，練習 `**system_message` 與 `history` 分離**：累積側建議 `**history: list[BaseMessage]`**（僅 **Human／AI**），每輪 `**context_messages = [system_message, *history, human_message]`** 再 `**llm.stream**`。若在同一作答檔合併多題，會再加上 `**load_session_jsonl`／`save_session_jsonl**`（見 **WG-15～16**）；本題獨立作答時**不要求** JSONL，以免與「先釐清 system／history 分工」混淆。

通過後可銜接 **WG-13**：在單檔內練習 `**bind_tools`**、`**ToolMessage**` 與 **ReAct** 式多段 `**stream`**（每次模型呼叫都累積成 `AIMessage`）。再銜接 **WG-14**（檔案／`exec` 工具組，選修併專案）。再銜接 **WG-15**／**WG-16** 將 `**history`**（可含 `**ToolMessage**`）寫入／讀回 **JSONL**（送模仍維持 `**[system_message, *history, human_message]`**），之後再接 **WG-17** 預算裁切、**WG-18**（**transcript**）與 **WG-19**（長期記憶）。

### 規格

- 延續 **WG-07～11**：`def main()`、`load_dotenv`、無金鑰則印提示後 `**return`**；有金鑰時 `**ChatOpenAI**`、`**while True**`、`input()`、結束指令、空白行 `**continue**`。
- 在進入 `**while**` 之前：實作 `**def get_identity() -> str**`，並建立 `**system_message = SystemMessage(content=get_identity())**`；`**history: list[BaseMessage] = []**`（啟動時**不**從檔案載入）。
- `**get_identity()` 回傳字串**須含（1）**一段課堂規則**（`**system_text`**，須含「**繁體中文**」等可驗收關鍵字）；（2）**一段顯示名稱**（`**nick`**，如 `**法鬥超人**`）；（3）**【執行環境】**：以 `**platform.system()`**（與 `**os.name**`）在**程式啟動時**寫入實際 OS（如 Windows／Darwin／Linux），並附一句**與該 OS 相容的 exec 提示**（藍本：`os.name == "nt"` 時註明 PowerShell、勿 `<<`／heredoc；其餘系統可簡化）；（4）**【exec 注意】**：請依【執行環境】選擇 shell 寫法、勿假設 Linux Bash；執行 Python 先 **write_file** 再 **exec** `uv run python 相對路徑`（與 **WG-14** 一致）。**本函式不要求**併入 **WG-13** 工具細則。
- **合併進階題（WG-20 起）**：`**build_system_prompt(loader)**` 直接呼叫本題 `**get_identity()`** 作為課堂基底，**勿**再包一層 `build_classroom_base_prompt` 等別名函式。WG-13 工具約束可不寫進 `get_identity()`，改由 tool **docstring** 或 ReAct 前組裝補足。
- 每一輪有效使用者輸入：送進模型處與 **WG-11** 同一精神——**先組本輪 `context_messages`、串流成功後才把本輪 Human／AI 寫回累積**。建議命名：`**human_message = HumanMessage(...)`** → `**context_messages = [system_message, *history, human_message]**` → `**llm.stream(context_messages)**` → `**history.append(human_message)**`、`**history.append(AIMessage(...))**`。**不要**把 `**system`** 與 `**history**` 硬併成「迴圈內一路 `**append**` 的單一串列」。
- **禁止**：把 `**SystemMessage`** 當成一般對話列 `**append` 進 `history**`；**本題不要求**實作 `**save_session_jsonl`**／讀檔（留給 **WG-15**／**WG-16**）。
- **不要求**：改 **metadata** 或 **JSONL** 欄位（尚無檔案格式）。

### 驗收條件

- 有金鑰時，`**llm.stream(context_messages)`**（`**context_messages = [system_message, *history, human_message]**` 或語意等價）能跑通，且終端串流行為與 **WG-11** 一致（前綴 `**助手：`** 等可保留）。
- 能指出：程式**哪一段**建立 `**system_message`**、**哪一段**初始化 `**history`**，以及迴圈內**哪一行**把兩者與 `**human_message`** 組進 `**context_messages**`。
- 能說明：`**get_identity()**` 回傳字串裡，**課堂規則**、**顯示名稱**、**【執行環境】**與**【exec 注意】**各對應哪一段；**【執行環境】**須為啟動時偵測結果，不可手寫固定成錯誤 OS。
- 修改 `**nick`** 或換一台電腦（不同 OS）後重開程式，模型收到的 system 區塊應反映新字串／新【執行環境】。
- 能一句話說明：為何 **system** 不放在 `**history`** 裡與人機回合混在同一串列（並參考「**JSONL** 對話列通常存 **user／assistant**；併 **WG-13**／**WG-14** 時另含 `**tool`** 列，見 **WG-15**」）。
- **邊界**：`**context_messages[0]`** 是哪一種訊息？本輪 `**human_message` 在送模串列中的位置**為何（相對於 `**history`**）？

### 藍本對應

以下節錄對齊 `**get_identity**` 與 `**system_message`／`history` 分離**（**本題可不寫 JSONL**）。完成 **WG-15～16** 後，合併進階題時會再接 `**load_session_jsonl`／`save_session_jsonl`**（**WG-15～16**）。

```python
import os
import platform

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

def _runtime_env_note() -> str:
    sys_name = platform.system()
    shell_hint = (
        "exec 在 PowerShell 下執行；勿用 <<、heredoc、bash -c。"
        if os.name == "nt"
        else "exec 在系統 shell 下執行；多行腳本仍請 write_file 後 uv run。"
    )
    return (
        f"\n\n【執行環境】{sys_name}（os.name={os.name}）；專案根目錄為目前工作目錄。"
        f"{shell_hint}"
    )

def get_identity() -> str:
    """課堂人設：規則、顯示名、執行環境、exec 注意。"""
    system_text = "你是課堂程式助教，並請使用繁體中文。"
    nick = "法鬥超人"
    exec_note = (
        "\n\n【exec 注意】"
        "\n- 請依上方【執行環境】選擇相容的 shell 指令，勿假設為 Linux Bash。"
        "\n- 若要執行 Python：先用 write_file 寫入 .py，再 exec「uv run python 相對路徑」。"
    )
    return (
        f"{system_text}\n\n【本場次顯示名稱】{nick}"
        f"{_runtime_env_note()}{exec_note}"
    )

def main() -> None:
    # load_dotenv()、api_key 檢查、建立 llm
    system_message = SystemMessage(content=get_identity())
    history: list[BaseMessage] = []

    # while 內：human_message →
    # context_messages = [system_message, *history, human_message] → llm.stream →
    # history.append(human_message); history.append(AIMessage(...))
```


---

## Challenge WG-13：會查表才算真 Agent——工具呼叫與 ReAct 迴圈（單檔）

### 情境

**WG-12** 讓模型以 **system + history + 本輪使用者** 往來，回覆皆為**純文字**。實務上常讓模型**決定何時呼叫工具**（計算、查詢、對外 API 等），再依**工具回傳**續寫下一則模型訊息，直到不再需要工具——這種「**Reason + Act**」迴圈常稱 **ReAct**。本題在**單一 `.py` 檔**內練習 `**@tool`**、`**bind_tools**`、`**tool_calls**` 與 `**ToolMessage**`，與本課 **ReAct** 藍本（`**run_react_turn**`）精神對齊；**不要求**本題接 **JSONL**／持久化／字元預算，以免與後續 **WG-17** 混淆。

通過後可銜接 **WG-14**（workspace 檔案／`exec` 五支 **`@tool`**，仍可不接 **JSONL**），再 **WG-15**：在 **WG-12** 送模結構下將 `**history`**（含 **ReAct** 鏈之 `**ToolMessage`**）寫入 **JSONL**（仍不寫 **system**），再 **WG-16** 載回；之後 **WG-17** 以 `**pick_consolidation_boundary`** 做短期送模裁切（成本與 `**history**` 一併納入 `**ToolMessage**`；邊界仍以 **Human 回合開頭**為主，與 **WG-13** ReAct 整輪語意可參考）。

### 規格

- **延續 WG-12** 之 `**get_identity()`／`SystemMessage`** 概念：送進模型的 **system** 須含**至少一段「何時必須用工具」**的規則（範例：算術須用工具、不可純心算）。**合併藍本（WG-15～）** 可不寫進 `**get_identity()`** 回傳字串，改由 `**@tool**` 的 **docstring**（如 `**add_two**` docstring：「凡涉及兩個整數相加必須呼叫此工具…」）或**選修**常數 `**tool_rule**` 於 `**main**` 組裝 **SystemMessage** 前併入；教師驗收須能指出工具約束出現在送模 **system** 的哪一處。
- 以 `**langchain_core.tools.tool`** 之 `**@tool**` 定義至少**一支**可呼叫函式（課堂可四則運算擇一或全套）；集中於 `**TOOLS`** 列表，並以 `**llm.bind_tools(TOOLS)**` 取得 `**llm_with_tools**`。
- **單輪使用者輸入**的處理流程（與 `**run_react_turn`** 同構）：
  1. 組初始 `**messages = [SystemMessage(...), *past, HumanMessage(user_text)]**`（`**past**` 為本輪之前之訊息；僅 **Human／AI** 亦可，若本題已含工具鏈則可含 **ToolMessage**）。
  2. 以 `**llm_with_tools.stream(messages)`** 串流取得回應片段，累積後轉回 `**AIMessage**`（供檢查 `tool_calls` 與寫入 `history`）。
  3. 若 `**response.tool_calls**` 非空：`**messages.append(response)**`，逐筆執行工具、建立 `**ToolMessage(content=..., tool_call_id=...)**` 並 `**append**`，回到步驟 2。
  3-1. ReAct 會有多次模型呼叫；本教案藍本以多段 `**stream**` 執行，每段串流後都累積成 `**AIMessage**` 再檢查 `tool_calls`。
  4. 若無 `**tool_calls**`：將最後一則 **AI** 文字作為本輪結論；該文字已由 `stream` 串流輸出，不再一次 `**print(response.content)**`。
- **邊界**：工具名稱不在參考表時**不得**崩潰；可將錯誤說明字串放入 `**ToolMessage.content`**。
- **選修**：將本輪新訊息（含 **Tool**）**append** 進 `**history`**，供下一輪 `**past**`；**選修**：`**_normalize_tool_args`** 類相容層（因應部分後端非標準 **args** 形狀）。

### 驗收條件

- 能跑通：使用者提出須依工具才能完成的任務時，終端可觀察到程式**實際呼叫工具**（非僅模型口頭心算）。
- 能指出：**哪一行／哪一段** `**bind_tools`**，以及**哪一層迴圈**在處理 `**tool_calls`** 與 `**ToolMessage**`。
- 能說明：`**AIMessage`（含 tool_calls）** 與 `**ToolMessage`**、最終 `**AIMessage`（純文字）** 在串列中的順序與角色。
- **邊界**：口頭描述若**只做一次 `invoke`、不處理 tool_calls**，可能錯在哪裡。

### 藍本對應

以下為**結構示意**（**非**完整可執行檔）；完整邏輯見下方藍本之 `**run_react_turn**` 與 `**main**` 呼叫方式。

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b

TOOLS = [add_numbers]
# TOOL_MAP = {t.name: t for t in TOOLS}
# llm_with_tools = ChatOpenAI(...).bind_tools(TOOLS)
# messages = [SystemMessage(...), *past, HumanMessage(...)]
# while True:
#     r = stream_to_ai_message(llm_with_tools.stream(messages))
#     if r.tool_calls:
#         messages.append(r)
#         for tc in r.tool_calls:
#             # 執行工具 → ToolMessage(..., tool_call_id=tc["id"])
#             ...
#     else:
#         messages.append(r)
#         break
```


---

## Challenge WG-14：讓 Agent 有手有腳——`exec` 與檔案的 LangChain **`@tool` 最小組**

### 情境

緊接 **WG-13**，你已用 **`@tool`**、`**bind_tools**`、多段 **`invoke`** 與 **`ToolMessage`** 跑通 **ReAct**。本題在同一條技術線上，把工具組擴充為 workspace 內**讀／寫／列目錄／局部替換**，以及必要時的 **`exec`**（shell）；仍**不要求** **JSONL**、持久化或字元預算——那些從 **WG-15** 起再接上。

核心觀念只有一句：**檔案操作走檔案工具，shell 指令才走 `exec`**。也就是說，讀檔不用 `cat`、寫檔不用 `echo >`、改檔不用 `sed -i`；`exec` 留給 `python --version`、`uv run pytest`、執行示範檔這類外部指令。

**Agent 使用 `exec` 時**：先讀 **WG-12** 送模字串中的 **【執行環境】**（`platform.system()` 動態產生），再下**單行**相容指令；多行 Python 須 **write_file → `uv run python …`**。**【exec 注意】** 與 **【執行環境】** 皆在 `get_identity()`（**WG-20** 起經 `build_system_prompt(loader)` 併入送模字串），讓模型每輪都看得到。

本題**不要求**自訂 `Tool` dataclass 或 `ToolRegistry` 類別；**選讀**：可將 **`TOOLS`** 傳入 **`llm.bind_tools(TOOLS)`** 做端到端驗收；若課堂拆步，亦可先用 **`BaseTool.invoke`**（或等價）做**手動**流程驗收。

### 規格

- 在教師指定作答檔中實作，依賴 **`langchain_core`**（與 **WG-13** 一致）。
- 以 **`@tool`**（必要時 **`@tool("exec")`** 等）裝飾五個實作函式，對外工具名稱須為 **`read_file`**、**`write_file`**、**`edit_file`**、**`list_dir`**、**`exec`**（與模型 function calling 對齊）。
- 定義 **`TOOLS: list`**，內含上述五個 **`BaseTool`** 實例，順序自訂但須固定、可重現。
- 設定 **`WORKSPACE = Path.cwd().resolve()`**；**`resolve_workspace_path`**：僅允許**相對路徑**解析到 workspace 底下（**建議**拒絕絕對路徑）；像 **`../outside.txt`** 須拒絕或回傳清楚錯誤，不可寫到 workspace 外。
- **`read_file(path, …)`**：讀 UTF-8 文字檔，回傳含行號的內容；找不到檔案或目標不是檔案時回傳錯誤。**語意上為唯讀**（不改磁碟）。
- **`write_file(path, content)`**：寫入 UTF-8，必要時建立父資料夾；若檔案已存在就是整檔覆寫。
- **`edit_file(path, old_text, new_text, replace_all=False)`**：用 `old_text` 做局部替換；找不到就報錯；出現多次時，預設要求更多上下文，不直接全改。
- **`list_dir(path, …)`**：列出資料夾內容；目標不是資料夾時回傳錯誤。**語意上為唯讀**。
- **`exec`（實作函式名可自訂，例如 `exec_workspace`）**：以 **`subprocess.run`** 在 **`WORKSPACE`** 下執行 shell 指令，回傳 exit code 與輸出摘要；至少阻擋 **`rm -rf`**、**`del /f`**、**`rmdir /s`**、**`format`**、**`shutdown`** 等危險片段。
- **`exec` 與子程序輸出編碼（跨平台必讀）**：在 **`capture_output=True`** 且 **`text=True`** 時，若未指定 **`encoding`**，**Python 會用系統預設編碼**去解 stdout／stderr。在 **繁中 Windows** 上常為 **cp950**；子程序若輸出 **UTF-8**（許多 CLI、日誌、**`uv`**／**`python`** 的訊息），背景讀取執行緒可能拋出 **`UnicodeDecodeError`**（終端機出現 **`Thread-* (_readerthread)`** 之類 traceback，主流程甚至仍回傳空輸出）。實作時應在 **`subprocess.run`** 明確加上 **`encoding="utf-8"`** 與 **`errors="replace"`**（或改讀 **bytes** 再以 **`errors="replace"`** 解碼），並對 **`stdout`／`stderr` 可能為 `None`** 做串接防護。教練／coding agent 檢閱 **`exec`** 時應主動核對這一段，避免只在 macOS／Linux 上測過就以為沒問題。
- **`exec` 的 `@tool` docstring**：說明用途即可（單行 shell、回傳 exit code／輸出）；**勿重複**寫 Bash／write_file 規則——改由 **WG-12** 的 **【執行環境】**與**【exec 注意】** 在 system 層統一約束。

### 驗收條件

- 由 **`TOOLS`**（或等價對照表）可列出 **`read_file`**、**`write_file`**、**`edit_file`**、**`list_dir`**、**`exec`** 五個工具名稱（例如 **`sorted(t.name for t in TOOLS)`**）。
- 手動流程能跑通：`write_file` 建立 `sandbox/hello.txt` → `list_dir` 看見它 → `read_file` 讀回含行號內容 → `edit_file` 改其中一段 → 再 `read_file` 確認 → `exec("python --version")` 回傳 exit code 與版本輸出（以 **`BaseTool.invoke({...})`** 或課堂約定之呼叫方式執行即可）。
- 能說明或示範：自寫 Python 的正確流程為 **write_file** 寫 `.py` → **exec** `uv run python 相對路徑`（勿用 `python << EOF` 等 Bash 寫法）。
- 能說明：為什麼 `write_file` 是整檔覆寫，而 `edit_file` 是局部替換；兩者各自適合什麼情境？
- 能說明：為什麼 **`read_file`／`list_dir` 在設計上屬「只讀磁碟」**，而 **`write_file`／`edit_file`／`exec` 會改檔或啟動子程序**，語意上與唯讀分工如何對應（**不必**再以自訂 `read_only` 欄位表達）。
- 能說明：為什麼不建議用 `exec("cat 檔案")`、`exec("echo ... > 檔案")` 或 `exec("sed -i ...")` 取代專用檔案工具。
- **邊界**：嘗試讀取或寫入 `../outside.txt` 時，工具應拒絕或回傳清楚錯誤，不應真的改到 workspace 外。
- **邊界**：`edit_file` 的 `old_text` 若在檔案中出現兩次，預設不得兩處都改；需要求更多上下文或明確 `replace_all=True`。
- **邊界**：`exec` 收到危險命令片段時應拒絕執行，並說明是安全限制。
- **邊界（Windows）**：在會觸發大量子程序輸出的指令下，**`exec`** 不得因預設 **cp950** 解碼失敗而在背景執行緒崩潰；應採上節規格之 **UTF-8 + replace**（或等價作法）。
- **邊界（Windows／Agent）**：在 PowerShell 下使用 `<<` 等 Bash 語法常導致 **exit_code=1**；應改 **write_file + uv run**。

### 藍本對應

以下為**可執行骨架**，重點是 **`@tool`**、**`TOOLS`** 與 workspace 安全邊界，不要求與任何參考實作逐字一致。

```python
import os
import subprocess
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

WORKSPACE = Path.cwd().resolve()


def resolve_workspace_path(path: str) -> Path:
    raw = Path(path)
    if raw.is_absolute():
        raise PermissionError("absolute paths are not allowed")
    target = (WORKSPACE / path).resolve()
    try:
        target.relative_to(WORKSPACE)
    except ValueError as e:
        raise PermissionError(f"path is outside workspace: {path}") from e
    return target


@tool("read_file")
def read_file(path: str, offset: int = 1, limit: int = 200) -> str:
    """讀取 workspace 內 UTF-8 文字檔，回傳帶行號內容。"""
    try:
        target = resolve_workspace_path(path)
        if not target.is_file():
            return f"Error: not a file: {path}"
        lines = target.read_text(encoding="utf-8").splitlines()
        start = max(offset - 1, 0)
        end = min(start + limit, len(lines))
        return "\n".join(f"{i + 1}| {line}" for i, line in enumerate(lines[start:end], start))
    except Exception as e:
        return f"Error: {e}"


@tool("write_file")
def write_file(path: str, content: str) -> str:
    """整檔覆寫寫入 UTF-8 文字檔（必要時建立父資料夾）。"""
    try:
        target = resolve_workspace_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error: {e}"


@tool("edit_file")
def edit_file(path: str, old_text: str, new_text: str, replace_all: bool = False) -> str:
    """在既有檔案中把 old_text 換成 new_text（預設僅單次替換）。"""
    try:
        target = resolve_workspace_path(path)
        text = target.read_text(encoding="utf-8")
        count = text.count(old_text)
        if count == 0:
            return "Error: old_text not found"
        if count > 1 and not replace_all:
            return "Error: old_text appears multiple times"
        target.write_text(
            text.replace(old_text, new_text, -1 if replace_all else 1),
            encoding="utf-8",
        )
        return f"edited {path}"
    except Exception as e:
        return f"Error: {e}"


@tool("list_dir")
def list_dir(path: str, recursive: bool = False, max_entries: int = 200) -> str:
    """列出 workspace 內資料夾內容。"""
    try:
        root = resolve_workspace_path(path)
        if not root.is_dir():
            return f"Error: not a directory: {path}"
        iterator = root.rglob("*") if recursive else root.iterdir()
        entries = [str(item.relative_to(WORKSPACE)) for item in iterator][:max_entries]
        return "\n".join(entries) if entries else "(empty)"
    except Exception as e:
        return f"Error: {e}"


@tool("exec")
def exec_workspace(command: str, timeout: int = 30) -> str:
    """在專案根目錄（workspace）執行單行 shell 指令，回傳 exit code 與輸出摘要。"""
    blocked = ("rm -rf", "del /f", "rmdir /s", "format", "shutdown")
    lowered = command.lower()
    if any(part in lowered for part in blocked):
        return "Error: blocked dangerous command (safety limit)"

    child_env = os.environ.copy()
    child_env.setdefault("PYTHONUTF8", "1")
    child_env.setdefault("PYTHONIOENCODING", "utf-8")

    run_kw: dict[str, Any] = {
        "cwd": str(WORKSPACE),
        "shell": True,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
        "env": child_env,
    }
    if os.name == "nt":
        run_kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        result = subprocess.run(command, **run_kw)
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        cap = 4000
        if len(output) > cap:
            output = output[:cap] + "\n\n[truncated]"
        if not output:
            output = "(no stdout or stderr; command finished with no captured output)"
        return f"exit_code={result.returncode}\n{output}"
    except Exception as e:
        return f"Error: {e}"


TOOLS: list[Any] = [
    read_file,
    write_file,
    edit_file,
    list_dir,
    exec_workspace,
]

_TOOL_BY_NAME: dict[str, Any] = {t.name: t for t in TOOLS}
```


---

## Challenge WG-15：對話落盤、人設不留痕——對話脈絡寫入 JSONL（先寫檔）

### 情境

**WG-12** 已讓 `**system_message`** 與 `**history**` 分離，且送模 `**context_messages = [system_message, *history, human_message]**`；關程式後 **RAM** 仍清空。**WG-13** 起（課堂若已併 **WG-14** 之檔案／`exec` 工具組亦同）`**history`** 亦可含 **ReAct** 鏈上的 `**AIMessage`（含 `tool_calls`）** 與 `**ToolMessage`**。實務上把這些**可序列化**的對話訊息**寫進檔案**，留下可查紀錄，並讓下一題能**讀回**接續。

本題在**沿用 WG-12 的送模與累積節奏**的前提下，**只做寫檔**：在本輪使用者回合與助手／工具鏈**已依序 `append` 進 `history`**（串流或 `**invoke**` 流程結束後）呼叫寫檔，把 `**session_meta**` 與 `**history` 內可持久化的訊息** **整檔覆寫**到 JSONL（**第一行**為 `**metadata`**）。語法對齊 **第 6 單元（檔案與例外處理）**：`**with open(..., "w", encoding="utf-8")`**、`**json.dumps**`、`**os.getenv**` 指定路徑。檔案長相可參考 `**session.jsonl.example**`，並**擴充** `**role: "tool"`** 等列以還原 `**ToolMessage**`（至少 `**content**`、`**tool_call_id**`）。若要做到「關閉再開仍保留完整 **ReAct** 語意」，`**assistant` 列**必須能還原**帶 `tool_calls` 的 `AIMessage`**（見下方 **規格** 之**完整版**定義）。

**刻意不做**：程式一啟動就**讀舊檔**還原 `**history`**（一律從**空串列**開始，體感仍像 **WG-12** 首次執行——再開程式不會自動接續）。讀檔接續留給 **WG-16**。

### 規格

- 延續 **WG-07～12**：`def main()`、`load_dotenv`、無金鑰則印提示後 `**return`**；有金鑰時 `**ChatOpenAI**`、`**while True**`、`input()`、結束指令、空白行 `**continue**`；`**get_identity()**`、`**system_message**` 與 `**history**` 分離（同 **WG-12**）。`**get_identity()`** 示範僅回傳課堂規則＋【本場次顯示名稱】（見下方藍本）；併 **WG-13** 之工具約束**不強制**寫在此函式內。
- **存檔路徑**：`**os.getenv("SESSION_JSONL_PATH", "session.jsonl")`**；預設 `**session.jsonl**`（`**session.jsonl.example**` 僅供參考，勿當預設寫入目標）。
- **啟動**：`**history`** 固定為**空串列**；`**session_meta`** 初值為 `**None**`。**禁止**在 `**while`** 之前呼叫任何「讀 JSONL 還原 `**history**`」的函式或等價邏輯。
- **送模（併 WG-13 之完整版）**：每輪在 `**[system_message, *history, HumanMessage(本輪)]`** 上做多段 `**llm_with_tools.stream(...)**`（**ReAct**）以判斷與執行工具；每段串流後累積成 `**AIMessage**`，迴圈內依 `**tool_calls`** `**append**` `**AIMessage`／`ToolMessage**`，最終無 `tool_calls` 的 assistant 文字已在串流中顯示，並以同一則 `AIMessage` 寫回 `history`。再將**自本輪 `HumanMessage` 起**之片段整段 `**extend` 進 `history`** 並寫檔。若課堂另做「僅 `**stream`**、無工具」之簡化版，送模仍為 `**[system_message, *history, human_message]**` 再 `**llm.stream**`，但**不**涵蓋 **JSONL** 之 `**tool`／`tool_calls`** 欄位演練。
- **寫檔時機**：本輪對話回合（含 **ReAct** 鏈若實作）**寫回 `history` 後**，呼叫寫檔邏輯；**整檔覆寫** `**"w"`** ＋ `**encoding="utf-8"**`。
- **檔案內容**：**第一行** `**metadata`**（`**_type`／`key`／`created_at`／`updated_at`／`metadata`／`last_consolidated**` 與 `**session.jsonl.example**` 對齊）；之後每行一則對話列，**至少**支援 `**role` 為 `user`／`assistant`／`tool`**，順序與 `**history**` 一致。
  - `**role: "tool"**` 列：須能還原 `**ToolMessage**`（至少 `**content**`、`**tool_call_id**`、`**timestamp**` 等），與 **WG-16** 載回閉環。
  - `**role: "assistant"` 列與 `tool_calls`（本教案採用之「完整版」）**：若該則 `**AIMessage` 帶有非空 `tool_calls`**（**ReAct** 中模型決定呼叫工具的那一則），JSONL **必須**在**同一列**多存一個鍵 `**tool_calls`**，其值為**可被 `json.dumps` 序列化**的陣列，且 `**WG-16` 載回時**能直接餵給建構式 `**AIMessage(content=..., tool_calls=...)`**，使還原後的物件與寫入前**語意一致**（含 `**id`／`name`／`args`** 等欄位，與你執行 **WG-13** 時 `**AIMessage.tool_calls`** 的結構對齊；不同 **LangChain** 版本若欄位名略異，以「能重建同一則 `**invoke`** 上下文」為驗收標準）。**純文字**、無工具呼叫的 `**AIMessage`**：**不**寫 `**tool_calls`** 鍵，或寫 `**"tool_calls": []**`／省略皆可，但**載回規則**須與 **WG-16** 一致。
  - **簡化版（僅純串流、無 ReAct）**：可僅有 `**user`／`assistant`**（無 `**tool_calls**`、無 `**tool**` 列）；一旦併 **WG-13** 並要持久化鏈條，即採上列**完整版**。
- **禁止**：把 `**SystemMessage`** 寫入檔案；從磁碟**載入**歷史到 `**history`**（留給 **WG-16**）。
- **不要求**：讀檔時 `**try`／`except json.JSONDecodeError`**（本題無讀檔）；合併／摘要歷史。

### 驗收條件

- 啟動後行為與 **WG-12**（無檔時）相同可對話（**不**因磁碟上已有舊檔而自動載入）。
- 至少完成一輪後，指定路徑出現 **JSONL**，**第一行**為 `**metadata`**，其後可見 `**user`／`assistant**` 列；若實作 **ReAct** 持久化，可再看到 `**tool`** 列，且**含 `tool_calls` 的 `assistant` 列**須帶 `**tool_calls`** 欄位（與上節**完整版**一致）。
- 能說明：**什麼時機**把 `**history`** 寫入檔案？為什麼在 **本輪助手也寫回 `history` 之後**，而不是 `**human_message` 一建好就寫**？
- **邊界**：若該路徑**已存在**一份舊 JSONL，新開程式後**第一輪**對話結束並存檔，你預期檔案內容與「若程式會讀舊檔」有什麼關鍵差別？（能說出「整檔覆寫、不先載入」即可。）

### 藍本對應

主迴圈與 **WG-13** 之 `**run_react_turn**` 同構（`**bind_tools`、多段 `stream` 累積 `AIMessage`、`ToolMessage**`）；與該檔差異僅在 **WG-15** **不**於啟動讀檔、`**history`** 恆自空開始。

**示範檔 — 僅含寫入時請對齊以下結構**（完整合併版含讀檔見 **WG-16** 藍本）

```python
"""課堂示範：WG-15 對話脈絡 JSONL 僅寫檔。

本藍本主線採 **WG-13** 風格：**`bind_tools` + 多段 `stream` + `ToolMessage`** 處理工具鏈，
每段模型回應都由串流 chunk 累積成 **AIMessage**；每輪結束後把 **`history`** 內 **Human／含 tool_calls 之 AIMessage／ToolMessage／最終 AIMessage** 整檔寫入 JSONL。
"""

import json
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    message_chunk_to_message,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def add_two(a: int, b: int) -> int:
    """兩個整數相加並回傳和。凡涉及兩個整數相加必須呼叫此工具，不要只在文字裡心算。"""
    return a + b

TOOLS = [add_two]
_TOOL_BY_NAME = {t.name: t for t in TOOLS}

def _default_metadata(created_at: str | None = None) -> dict[str, Any]:
    """建立第一行 metadata 物件（與 session.jsonl.example 欄位對齊）。"""
    now = datetime.now().isoformat()
    return {
        "_type": "metadata",
        "key": "session",
        "created_at": created_at or now,
        "updated_at": now,
        "metadata": {},
        "last_consolidated": 0,
    }

def save_session_jsonl(
    path: str,
    messages: list[BaseMessage],
    existing_meta: dict[str, Any] | None,
) -> dict[str, Any]:
    """整檔覆寫：第一行 metadata（更新 updated_at），其餘每行一則 user／assistant／tool。"""
    now = datetime.now().isoformat()
    if existing_meta is None:
        meta = _default_metadata(created_at=now)
    else:
        meta = dict(existing_meta)
        meta["_type"] = "metadata"
        meta["key"] = meta.get("key", "session")
        if "created_at" not in meta:
            meta["created_at"] = now
        meta["updated_at"] = now

    lines: list[str] = [json.dumps(meta, ensure_ascii=False)]

    for m in messages:
        ts = datetime.now().isoformat()
        if isinstance(m, HumanMessage):
            row = {"role": "user", "content": m.content, "timestamp": ts}
        elif isinstance(m, AIMessage):
            row = {"role": "assistant", "content": m.content, "timestamp": ts}
            # 完整 ReAct 鏈：有 tool_calls 時必須寫入同列，WG-16 才能還原 AIMessage(..., tool_calls=...)
            tc = getattr(m, "tool_calls", None)
            if tc:
                row["tool_calls"] = tc
        elif isinstance(m, ToolMessage):
            row = {
                "role": "tool",
                "content": m.content,
                "tool_call_id": m.tool_call_id,
                "timestamp": ts,
            }
        else:
            continue
        lines.append(json.dumps(row, ensure_ascii=False))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")

    return meta

def get_identity() -> str:
    # 同 WG-12：含 _runtime_env_note() 與【exec 注意】（見該題藍本）
    ...

def run_react_turn(
    llm_tools: ChatOpenAI,
    system_message: SystemMessage,
    history: list[BaseMessage],
    user_text: str,
    *,
    stream_stdout: bool = True,
) -> tuple[str, list[BaseMessage]]:
    """本輪自 HumanMessage 起至最終 AIMessage（可含 tool_calls／ToolMessage 鏈）。模型呼叫以 stream 累積成 AIMessage。"""
    human_message = HumanMessage(content=user_text)
    messages: list[BaseMessage] = [system_message, *history, human_message]
    idx_turn_start = 1 + len(history)  # 本輪第一則為 human_message

    while True:
        acc: AIMessageChunk | None = None
        for chunk in llm_tools.stream(messages):
            acc = chunk if acc is None else acc + chunk
            if stream_stdout and chunk.content:
                print(chunk.content, end="", flush=True)
        if acc is None:
            raise RuntimeError("模型串流未回傳任何 chunk")
        response = message_chunk_to_message(acc)

        if response.tool_calls:
            if stream_stdout:
                print()
            messages.append(response)
            for tc in response.tool_calls:
                name = tc["name"]
                raw_args = dict(tc.get("args") or {})
                tool_obj = _TOOL_BY_NAME.get(name)
                if tool_obj is None:
                    result: str | int = f"未知工具: {name}"
                else:
                    try:
                        result = tool_obj.invoke(raw_args)
                    except Exception as e:
                        result = str(e)  # 課堂示範：錯誤字串化寫入 ToolMessage
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tc["id"])
                )
        else:
            messages.append(response)
            break

    turn_messages = messages[idx_turn_start:]
    final_ai = next(
        (m for m in reversed(turn_messages) if isinstance(m, AIMessage)),
        None,
    )
    final_text = ((final_ai.content if final_ai else None) or "").strip()
    return final_text, turn_messages

def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    session_path = os.getenv("SESSION_JSONL_PATH", "session.jsonl")

    system_message = SystemMessage(content=get_identity())
    history: list[BaseMessage] = []
    session_meta: dict[str, Any] | None = None

    if api_key:
        print(
            "已讀到 API 金鑰設定（內容不顯示）；進入對話（ReAct + JSONL 寫檔；每次重開仍從空脈絡開始；輸入 quit / exit / q 結束）。"
        )
    else:
        print("尚未讀到 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
        return

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    llm_tools = llm.bind_tools(TOOLS)

    while True:
        user_text = input("你：").strip()
        if user_text.lower() in ("quit", "exit", "q"):
            print("再見！")
            break
        if not user_text:
            continue

        print("助手：", end="", flush=True)
        reply_text, turn_messages = run_react_turn(
            llm_tools, system_message, history, user_text
        )
        print()

        history.extend(turn_messages)
        session_meta = save_session_jsonl(session_path, history, session_meta)

if __name__ == "__main__":
    main()
```


---

## Challenge WG-16：冷啟動撿回昨日脈絡——從 JSONL 載回對話脈絡

### 情境

**WG-15** 已會把每輪完整 `**history`**（含 **WG-13** **ReAct** 鏈上的 `**AIMessage`（可含 `tool_calls`）／`ToolMessage`**，與一般 `**HumanMessage`／`AIMessage**`）寫成 JSONL，但每次開程式仍從空脈絡開始。本題在**不改寫檔格式與寫檔時機**的前提下，加上**啟動時讀檔**：若路徑上已有檔案，就把 `**metadata`** 與對話列還原成 `**langchain_core.messages**` 物件串列（`**user`／`assistant`（含 `tool_calls` 還原）／`tool**` 與 **WG-15**「完整版」對齊），讓**關閉程式再開**仍能延續同一場對話。

讀取時對齊 **第 6 單元（檔案與例外處理）**：`**with open(..., encoding="utf-8")`** 逐行讀、`**json.loads**` 包在 `**try`／`except json.JSONDecodeError**` 內，壞行略過不中斷。通過後可銜接 **WG-17**：在 **WG-12** 的 `**system_message`** 與 **WG-15** 寫檔格式之上，用 `**pick_consolidation_boundary`** 做短期送模裁切（見該題）。

### 規格

- 延續 **WG-15** 之 JSONL 格式、`**SESSION_JSONL_PATH`**、每輪結束後**整檔覆寫**、**不**寫 `**SystemMessage`**；`**tool**` 列須能還原 `**ToolMessage**`（至少 `**content**`、`**tool_call_id**`，與 **WG-15** 一致）。
- `**assistant` 列與 `tool_calls`（與 WG-15「完整版」同一套）**：讀到 `**role: "assistant"`** 時，若該列含 `**tool_calls**` 鍵且為非空陣列，必須還原為 `**AIMessage(content=..., tool_calls=...)**`（參數值與檔案內 `**tool_calls**` 一致），以保留 **ReAct** 鏈上「模型發出工具呼叫」那一則的語意；若無 `**tool_calls`** 或為空陣列，則 `**AIMessage(content=...)**` 即可。
- **啟動**：若路徑**無檔**，`**history`** 為空、`**session_meta**` 為 `**None**`（與 **WG-15** 相同）。若**有檔**，以 `**"r"`** 模式逐行讀取：
  - 空行略過；`**json.loads**` 使用 `**try`／`except json.JSONDecodeError**`，壞行略過。
  - `**"_type": "metadata"**` 列：保留為 `**session_meta**`，供之後寫回時沿用 `**created_at**`、更新 `**updated_at**`。
  - `**role**` 為 `**"user"**`：轉成 `**HumanMessage**`；為 `**"assistant"**`：依上節還原 `**AIMessage**`（**含／不含 `tool_calls`**）；為 `**"tool"**`：轉成 `**ToolMessage(content=..., tool_call_id=...)**`（欄位與 **WG-15** 寫入一致）；未知 `**role`** 略過（或依教師約定記錄警告）。
- `**main()**` 開頭改為呼叫載入函式（或等價邏輯）取得 `**history**` 與 `**session_meta**`；並與 **WG-12** 相同在進入 `**while`** 前建立 `**system_message = SystemMessage(content=get_identity())**`。其餘每輪與 **WG-15** 閉環：併 **WG-13** 時，以 `**bind_tools` + 多段 `stream`** 產生本輪 `**turn_messages**`（自 `**HumanMessage**` 起，可含 `**AIMessage.tool_calls`／`ToolMessage`／最終 `AIMessage**`），`**history.extend(turn_messages)**` 後 `**save_session_jsonl**`；**本檔藍本**與 **WG-15** 藍本同採 `**run_react_turn`** 寫法（**非**單輪純文字直印）。
- **不要求**：變更 **WG-15** 訂好的 JSON 欄位名稱或檔案編碼。

### 驗收條件

- **關閉程式再開**（仍具金鑰）：先前對話中給過的關鍵資訊可被模型承接（自訂台詞即可），且與磁碟上 JSONL 內容一致。
- 能指出程式裡**哪一段**在啟動時讀檔，以及**哪一段**用 `**try`／`except json.JSONDecodeError`** 處理壞行。
- 能說明：`**session_meta**`（或你專案中等價變數）在「第一次寫檔」與「讀檔後再寫檔」時，`**created_at**` 與 `**updated_at**` 各自扮演什麼角色？
- **邊界**：若手動刪掉 JSONL **第一行 `metadata`** 只留下對話列，下次啟動載入後再完成一輪並存檔，你預期**第一行**會如何變化？（能描述「是否補上新的 metadata」即可。）
- （併 **WG-13** 時）**關閉再開**後，磁碟上 `**assistant` 列**若含 `**tool_calls`**，載入後 `**history**` 中對應 `**AIMessage**` 須仍帶 `**tool_calls**`（可 `**print**` 或除錯器檢查），且後續 `**ToolMessage**` 仍接在正確的 `**tool_call_id**` 之後。

### 藍本對應

與 **WG-15** 藍本同一套 `**run_react_turn`**；另在 `**main()**` 開頭呼叫 `**load_session_jsonl**`，其餘寫檔時機與 **WG-15** 相同。

**示範檔全檔 — 寫入＋載回合併版（對齊 WG-16）**

```python
"""課堂示範：WG-15～WG-16 對話脈絡 JSONL 寫入與載回。

啟動時 **`load_session_jsonl`** 還原含 **`tool_calls`** 之 **`AIMessage`** 與 **`ToolMessage`**；
每輪仍以 **ReAct + `invoke`** 延伸 **`history`**，再 **`save_session_jsonl`** 整檔覆寫。
"""

import json
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    message_chunk_to_message,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def add_two(a: int, b: int) -> int:
    """兩個整數相加並回傳和。凡涉及兩個整數相加必須呼叫此工具，不要只在文字裡心算。"""
    return a + b

TOOLS = [add_two]
_TOOL_BY_NAME = {t.name: t for t in TOOLS}

def _default_metadata(created_at: str | None = None) -> dict[str, Any]:
    """建立第一行 metadata 物件（與 session.jsonl.example 欄位對齊）。"""
    now = datetime.now().isoformat()
    return {
        "_type": "metadata",
        "key": "session",
        "created_at": created_at or now,
        "updated_at": now,
        "metadata": {},
        "last_consolidated": 0,
    }

def load_session_jsonl(path: str) -> tuple[list[BaseMessage], dict[str, Any] | None]:
    """從 JSONL 載入對話訊息串列（assistant 含 tool_calls 時還原完整 AIMessage）與 metadata；檔不存在則回傳空串列與 None。"""
    if not os.path.exists(path):
        return [], None

    messages: list[BaseMessage] = []
    meta: dict[str, Any] | None = None

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                obj: Any = json.loads(line)
            except json.JSONDecodeError:
                continue

            if isinstance(obj, dict) and obj.get("_type") == "metadata":
                meta = obj
                continue

            if not isinstance(obj, dict):
                continue

            role = obj.get("role")
            if role == "user":
                messages.append(HumanMessage(content=str(obj.get("content", ""))))
            elif role == "assistant":
                content = str(obj.get("content", ""))
                tc = obj.get("tool_calls")
                if tc:
                    messages.append(AIMessage(content=content, tool_calls=tc))
                else:
                    messages.append(AIMessage(content=content))
            elif role == "tool":
                tid = obj.get("tool_call_id") or ""
                messages.append(
                    ToolMessage(
                        content=str(obj.get("content", "")),
                        tool_call_id=str(tid),
                    )
                )

    return messages, meta

def save_session_jsonl(
    path: str,
    messages: list[BaseMessage],
    existing_meta: dict[str, Any] | None,
) -> dict[str, Any]:
    """整檔覆寫：第一行 metadata（更新 updated_at），其餘每行一則 user／assistant／tool。"""
    now = datetime.now().isoformat()
    if existing_meta is None:
        meta = _default_metadata(created_at=now)
    else:
        meta = dict(existing_meta)
        meta["_type"] = "metadata"
        meta["key"] = meta.get("key", "session")
        if "created_at" not in meta:
            meta["created_at"] = now
        meta["updated_at"] = now

    lines: list[str] = [json.dumps(meta, ensure_ascii=False)]

    for m in messages:
        ts = datetime.now().isoformat()
        if isinstance(m, HumanMessage):
            row = {"role": "user", "content": m.content, "timestamp": ts}
        elif isinstance(m, AIMessage):
            row = {"role": "assistant", "content": m.content, "timestamp": ts}
            tc = getattr(m, "tool_calls", None)
            if tc:
                row["tool_calls"] = tc
        elif isinstance(m, ToolMessage):
            row = {
                "role": "tool",
                "content": m.content,
                "tool_call_id": m.tool_call_id,
                "timestamp": ts,
            }
        else:
            continue
        lines.append(json.dumps(row, ensure_ascii=False))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")

    return meta

def get_identity() -> str:
    # 同 WG-12：含 _runtime_env_note() 與【exec 注意】（見該題藍本）
    ...

def run_react_turn(
    llm_tools: ChatOpenAI,
    system_message: SystemMessage,
    history: list[BaseMessage],
    user_text: str,
    *,
    stream_stdout: bool = True,
) -> tuple[str, list[BaseMessage]]:
    human_message = HumanMessage(content=user_text)
    messages: list[BaseMessage] = [system_message, *history, human_message]
    idx_turn_start = 1 + len(history)

    while True:
        acc: AIMessageChunk | None = None
        for chunk in llm_tools.stream(messages):
            acc = chunk if acc is None else acc + chunk
            if stream_stdout and chunk.content:
                print(chunk.content, end="", flush=True)
        if acc is None:
            raise RuntimeError("模型串流未回傳任何 chunk")
        response = message_chunk_to_message(acc)

        if response.tool_calls:
            if stream_stdout:
                print()
            messages.append(response)
            for tc in response.tool_calls:
                name = tc["name"]
                raw_args = dict(tc.get("args") or {})
                tool_obj = _TOOL_BY_NAME.get(name)
                if tool_obj is None:
                    result: str | int = f"未知工具: {name}"
                else:
                    try:
                        result = tool_obj.invoke(raw_args)
                    except Exception as e:
                        result = str(e)  # 課堂示範：錯誤字串化寫入 ToolMessage
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tc["id"])
                )
        else:
            messages.append(response)
            break

    turn_messages = messages[idx_turn_start:]
    final_ai = next(
        (m for m in reversed(turn_messages) if isinstance(m, AIMessage)),
        None,
    )
    final_text = ((final_ai.content if final_ai else None) or "").strip()
    return final_text, turn_messages

def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    session_path = os.getenv("SESSION_JSONL_PATH", "session.jsonl")

    loaded, session_meta = load_session_jsonl(session_path)
    history: list[BaseMessage] = list(loaded)
    system_message = SystemMessage(content=get_identity())

    if api_key:
        print(
            "已讀到 API 金鑰設定（內容不顯示）；進入對話（ReAct + JSONL 寫入／載回可接續；輸入 quit / exit / q 結束）。"
        )
    else:
        print("尚未讀到 OPENAI_API_KEY；請檢查 .env 或系統環境變數。")
        return

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    llm_tools = llm.bind_tools(TOOLS)

    while True:
        user_text = input("你：").strip()
        if user_text.lower() in ("quit", "exit", "q"):
            print("再見！")
            break
        if not user_text:
            continue

        print("助手：", end="", flush=True)
        reply_text, turn_messages = run_react_turn(
            llm_tools, system_message, history, user_text
        )
        print()

        history.extend(turn_messages)
        session_meta = save_session_jsonl(session_path, history, session_meta)

if __name__ == "__main__":
    main()
```


---

# 第二部分 · 進階挑戰（AI Coding 實戰）（WG-17～WG-21）

---

## Challenge WG-17：視窗太窄先裁舊帳——字元長度模擬 token 預算與整併邊界（`pick_consolidation_boundary`）

### 情境

**WG-12～15** 已讓模型讀到 **system** 加上自 **JSONL** 載回、並在記憶體中**完整累積**的對話（**WG-13** 起 `**history`** 可含 `**ToolMessage**` 與含 `**tool_calls**` 之 `**AIMessage**`，與磁碟 **JSONL** 一致）；但真實 **API** 有**上下文長度上限**，過長時必須**丟掉最舊**的一部分，只把「塞得進預算」的內容送進模型。本題用**字元數**刻意簡化模擬 **token 成本**（不呼叫 **tiktoken** 等），練習「**先判斷是否超線 → 再裁切 → 再送模（串流或 ReAct 多段 `stream`）**」的節奏；概念上銜接 **WG-13～16** 之字元成本累加與送模裁切思路。**成本**須把 `**past`** 內每一則 `**BaseMessage**`（含 `**ToolMessage**`）一併納入 `**estimate_message_tokens**`；**裁切邊界**仍以「**下一則使用者訊息**」開頭為準（`**pick_consolidation_boundary`** 對 `**HumanMessage**` 的判定），不因中間夾了 `**ToolMessage**` 而改變「從哪一則 **user** 往後保留」的語意。

> **與 WG-11～15 的用語對齊**：**WG-11** 以 `**messages`** 累積**已結束回合**（當時僅 **Human／AI**）；**WG-12** 起 `**history`** 與 **JSONL** 對齊，**WG-13** 起可含 **ReAct** 鏈；每輪無裁切時 `**context_messages = [system_message, *history, human_message]`**。**WG-17** 再把「過去段」換成裁切後的 `**past`**（`**past**` 內仍保留 **tool** 訊息之時間順序）。`**history` 的長度**與 `**context_messages` 裡「過去段」的長度**不必相同——這是本題要學生分辨的核心。

### 規格

- **延續 WG-16**：`**get_identity`**、`**SystemMessage**`、**JSONL** 格式、`**load_session_jsonl`／`save_session_jsonl`**、每輪結束後整檔覆寫等**維持不變**（與 **WG-12～14** 之前題之語意銜接）。
- **資料分工**：
  - `**history`**：依時間順序完整保存**已發生**之 `**BaseMessage`**（`**HumanMessage`／`AIMessage`／`ToolMessage**` 等，與 **WG-15** **JSONL** 與 **WG-13** **ReAct** 一致；`**AIMessage`** 若含 `**tool_calls**` 仍屬同則物件）。啟動載入後 `**history**` 即為 `**load_session_jsonl` 回傳的串列**（**不**含 **system**）。
  - `**last_consolidated`**：**非負整數**，語意對齊長程式 `**Session.last_consolidated`**：從 `**history` 的該索引起**向後掃描，計算「若從某個**之後的使用者回合開頭**開始保留，已略過多少權重」。課堂可自 `**0`** 起；**選修**：每輪整併成功後把 `**last_consolidated`** 更新為本次回傳的 `**idx**`，減少重掃（須與實作一致）。
  - **本輪**使用者新輸入先建成 `**HumanMessage`**（記為 `**human_message**`），**在 append 進 `history` 之前**先參與成本計算與裁切。
  - `**past`**：由整併邊界決定。若 `**pick_consolidation_boundary**`（或等價實作）回傳 `**(idx, _)**`，則 `**past = history[idx:]**`；若回傳 `**None**`（含 `**tokens_to_remove <= 0**` 或 `**start >= len(history)**`），則 `**past = history[last_consolidated:]**`。
- **簡化成本**（本題自訂，**不**代表真實 **token**）：
  - 先定義 `**estimate_message_tokens(message: BaseMessage) -> int`**（本題即 `**len(message.content)**` 當 `**content` 為 `str**`；否則課堂自訂規則），`**cost` 與 `pick_consolidation_boundary` 必須共用**此定義。
  - `**cost = len(system_str) + sum(estimate_message_tokens(m) for m in msgs)`**。
  其中 `**system_str**` 與本輪 `**SystemMessage.content**` 一致（**WG-12～18** 可為 `**get_identity()`**；**WG-19** 起併入長期記憶；**WG-20** 起改 `**build_system_prompt(loader)**`）；`**msgs**` 為 `***past0`（或裁切後的 `past`）與本輪 `human_message**` 之**所有**訊息（**含** `**ToolMessage`**；本題 `**estimate_message_tokens**` 以 `**content` 字串長度**為主，**選修**：對 `**tool_calls`** 另加權）。
- **常數 `TOKEN_BUDGET`**：正整數（檔案頂部常數即可；**選修**改為 `**int(os.getenv("TOKEN_BUDGET", "8000"))`** 等，無效時需有預設）。
- **先判斷再裁切**：
  - 先令 `**past0 = history[last_consolidated:]`**，再算 `**cost**`（`**System` 字串** + `**past0`** + **本輪 `human_message`**），公式同前 `**len` 加總**。
  - 若 `**cost <= TOKEN_BUDGET`**：令 `**tokens_to_remove = 0**`（或不呼叫整併），`**past = past0**`，直接組 `**context_messages**`（見下「送模串列」）。
  - 若 `**cost > TOKEN_BUDGET**`：令 `**tokens_to_remove = max(0, cost - TOKEN_BUDGET // 2)**`（**整數**；目標是把「送模側」壓到約 `**TOKEN_BUDGET // 2`** 留給助手輸出概念）。再呼叫 `**pick_consolidation_boundary(history, last_consolidated, tokens_to_remove)**`（或等價自由函式）決定 `**past**`。
- **裁切流程**（`**pick_consolidation_boundary`**，僅在 `**cost > TOKEN_BUDGET**` 且 `**tokens_to_remove > 0**` 時必須執行；邏輯須與下列一致）：
  - `**start = last_consolidated**`。若 `**start >= len(history)**` 或 `**tokens_to_remove <= 0**`，回傳 `**None**`。
  - 自 `**start**` 以 `**for idx in range(start, len(history)):**` 走訪；維護 `**removed_tokens**` 與 `**last_boundary: tuple[int, int] | None**`。每一則迭代須與你貼的程式**同序**：先依 `**idx > start`** 且該則為**使用者**更新 `**last_boundary`** 並視情況 `**return**`，再執行 `**removed_tokens += estimate_message_tokens(message)**`（定義見上）。
  - **邊界判定**：當 `**idx > start`** 且 `**history[idx]**` 為**使用者訊息**（課堂即 `**isinstance(..., HumanMessage)`**，對齊 `**message.get("role") == "user"**`），令 `**last_boundary = (idx, removed_tokens)**`；若此時 `**removed_tokens >= tokens_to_remove**`，**立即** `**return last_boundary`**。
  - 迴圈結束若從未達標，**回傳最後一次**的 `**last_boundary`**（可為 `**None**`，表示無可用邊界）。
  - `**TOKEN_BUDGET**`：判斷「是否超線、要不要整併」；`**TOKEN_BUDGET // 2**`：換算成本輪要試著削掉的 `**tokens_to_remove**` 目標。**JSONL** 與 `**history`** 仍保存**完整**紀錄；僅送模用的 `**past`** 依 `**idx**` 切片。
- **本輪 `human_message` 必留**：送進 `**llm.stream(context_messages)`** 的 `**context_messages**` 串列**必須**含本則使用者訊息，**不可**因裁切被移除。
- **送模串列**：每輪組 `**context_messages = [system_message, *past, human_message]`**（`**past**` 依上一節），再呼叫 `**llm.stream(context_messages)**`。若本題併 **WG-13**，工具判斷與工具執行使用 **ReAct** 多段 `**stream`**，每段串流後累積成 `**AIMessage**`，且 `**history**` 於該輪 `**append**` 之順序須符合工具協議。回合結束後將本輪產生之訊息依序 `**append` 進 `history**`（純串流時為 **Human＋AI**；**ReAct** 時另含 `**ToolMessage`** 等），並呼叫 `**save_session_jsonl(session_path, history, ...)**`（`**system**` 不在 `**history**`，**不**寫進檔）。

### 驗收條件

- **預算夠**（`**cost <= TOKEN_BUDGET`**）：不進入整併、或 `**pick_consolidation_boundary**` 因 `**tokens_to_remove <= 0**` 回 `**None**` 時，`**past**` 須與 `**history[last_consolidated:]**` 一致，模型讀到的舊對話範圍與「未整併」相同。
- **預算不夠**：`**past`** 的起點索引必須落在 `**HumanMessage**`（與 `**idx > start` 且為 user** 之邊界語意一致），**不可**從 `**AIMessage`** 中間切開當作起點。
- `**removed_tokens**` 的累加順序與 `**estimate_message_tokens**` 定義，須與 `**pick_consolidation_boundary**` 行為一致；能接受「掃完仍 `**removed_tokens < tokens_to_remove**`」時回傳**最後一個** `**last_boundary`** 的設計。
- 本輪 `**HumanMessage**` 始終出現在 `**context_messages**`（`**llm.stream**` 的引數）中。
- 能說明：`**last_consolidated**`、回傳的 `**idx**`、與 `**past = history[idx:]**` 的對應；`**history` 全長**與「實際送入 `**context_messages`** 的過去段」差在哪裡（口頭、註解或白板擇一）。
- 能說明：為什麼邊界要選在「**下一則使用者訊息**」的開頭，而不是任意索引切開。

### 藍本對應

以下為**結構示意**（**非**完整可執行檔）；請在 **WG-12** 藍本上分離 `**history`** 與 `**last_consolidated**`，實作 `**estimate_message_tokens**` 與 `**pick_consolidation_boundary**`，並在 `**while**` 內每輪於 `**append` 進 `history` 之前**完成裁切與 `**stream`**。

```python
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

TOKEN_BUDGET = 8000  # 或 int(os.getenv("TOKEN_BUDGET", "8000")), ...

def estimate_message_tokens(message: BaseMessage) -> int:
    c = message.content
    return len(c) if isinstance(c, str) else 0

def pick_consolidation_boundary(
    messages: list[BaseMessage],
    last_consolidated: int,
    tokens_to_remove: int,
) -> tuple[int, int] | None:
    """自 last_consolidated 掃描，挑「使用者回合開頭」idx，使略過的權重足夠。"""
    start = last_consolidated
    if start >= len(messages) or tokens_to_remove <= 0:
        return None

    removed_tokens = 0
    last_boundary: tuple[int, int] | None = None
    for idx in range(start, len(messages)):
        message = messages[idx]
        if idx > start and isinstance(message, HumanMessage):
            last_boundary = (idx, removed_tokens)
            if removed_tokens >= tokens_to_remove:
                return last_boundary
        removed_tokens += estimate_message_tokens(message)

    return last_boundary

# main 啟動：loaded, session_meta = load_session_jsonl(session_path)
history: list[BaseMessage] = list(loaded)
last_consolidated = 0
system_message = SystemMessage(content=get_identity())
system_str = get_identity()

# while True: 讀 user_text → human_message = HumanMessage(...)
def message_cost(msgs: list[BaseMessage]) -> int:
    return sum(estimate_message_tokens(m) for m in msgs)

past0 = history[last_consolidated:]
cost = len(system_str) + message_cost([*past0, human_message])
if cost <= TOKEN_BUDGET:
    past = past0
else:
    tokens_to_remove = max(0, cost - TOKEN_BUDGET // 2)
    boundary = pick_consolidation_boundary(history, last_consolidated, tokens_to_remove)
    past = history[boundary[0] :] if boundary is not None else past0

context_messages = [system_message, *past, human_message]
# for chunk in llm.stream(context_messages): ...
# history.append(human_message); history.append(AIMessage(...));
# save_session_jsonl(session_path, history, session_meta)
```


---

## Challenge WG-18：送模前先洗對話簿——transcript 修復與工具輸出預算

### 情境

**WG-17** 教你用 `pick_consolidation_boundary` 做「短期送模視窗」裁切；但真實 agent 還會遇到另一類問題：**對話串本身壞掉或太肥**，導致下一輪模型讀到不合法上下文、或直接被超長 `tool` 輸出塞爆。

常見做法是維持一份「完整累積」的 `messages`（之後要寫 JSONL／存檔），但在每一輪呼叫模型前，另組一份 `**messages_for_model`**，允許做**修復／截斷／小型壓縮**，而且註解明確要求「**不要污染**之後要保存的新回合邊界」。

### 規格（本題用「純 dict transcript」教，避免綁死 LangChain 型別）

- 訊息格式使用 OpenAI chat 風格 `list[dict]`，至少支援：
  - `{"role": "system", "content": str}`
  - `{"role": "user" | "assistant", "content": str}`
  - `{"role": "assistant", "content": str, "tool_calls": [...]}`（每個 tool call 至少含 `id` 與 `function.name`）
  - `{"role": "tool", "tool_call_id": str, "name": str, "content": str}`
- 實作 `build_messages_for_model(messages, *, max_chars: int, max_tool_chars: int, keep_recent_tools: int) -> list[dict]`，輸入為「完整累積」的 transcript，輸出為「本輪要送進模型」的版本。
- **禁止**直接就地修改輸入 list 裡的 dict（避免不小心改到要持久化的那份）；需要改動時請複製（shallow copy dict 即可，本題不要求深拷貝整段 content）。

#### A. 孤兒 tool 清理

- 若出現 `role == "tool"`，但它的 `tool_call_id` 在更早的訊息中找不到對應的 assistant `tool_calls[].id`，則在 `messages_for_model` **移除**該 tool 訊息。

#### B. 缺 tool 回覆補洞

- 若 assistant 訊息含 `tool_calls`，但後面沒有對應的 `tool` 訊息（依 `tool_call_id` 對齊），則在 assistant 之後插入一則合成 tool 訊息：
  - `content` 可用固定字串：`"[Tool result unavailable — call was interrupted or lost]"`（本題允許自訂，但須全檔一致）。

#### C. tool 輸出單則上限

- 對 `role == "tool"` 且 `content` 為字串者：若 `len(content) > max_tool_chars`，截斷到 `max_tool_chars`，並在結尾加上提示（例如 `"\n\n[truncated]"`）。

#### D. 小型壓縮

- 針對 `name` 屬於集合 `{"read_file","exec","grep","glob","web_search","web_fetch","list_dir"}` 的 tool 訊息：
  - 若這類 tool 訊息總數 `> keep_recent_tools`，將「最舊的」幾則中、且 `len(content) >= 500` 的長輸出，替換成單行摘要：`"[{name} result omitted from context]"`。
  - **永遠保留**最後 `keep_recent_tools` 則此類 tool 訊息的原文（不做摘要）。

#### E. 全對話字元預算

- 用極簡成本：`cost(msg) = len(str(msg.get("content","")))`（`tool_calls` 可先不算進成本，本題不考精度）。
- 若總成本 `> max_chars`：從**最舊的完整 user 回合**開始**整段刪除**，直到 `<= max_chars`。
  - **user 回合定義**：由一則 `role == "user"` 起算，到**下一則** `user` 之前（不含下一則 user）的所有 `assistant`／`tool` 訊息；邊界語意與 **WG-17** 之「切在 user-turn 前、不拆 ReAct 鏈」一致。
  - **禁止**在 `assistant` ↔ `tool` 之間逐則刪除。E 跑在 A～D **之後**；若逐則刪最舊非 system 訊息，會再次製造孤兒 tool 或缺 tool 回覆，而 A/B **不會**重跑。
  - **保留尾端回合**：含「最後一則 `user`」的那一 whole turn **不得**刪除（該 `user` 之後的 `assistant`／`tool` 亦須完整保留）。
- **與 WG-17 的差別**：WG-17 裁切 `history` 的 `past`（可能觸發長期記憶）；E 只裁**送模副本**，不改持久化的完整 transcript。
- **尾端規則（分情境）**：
  - **新使用者回合**：送模副本最後一則應是本輪 `user`；若做不到，允許插入一則極短 user：`"(conversation continued)"` 作為安全網，並在註解說明。
  - **ReAct 工具續呼叫**：若前一則 assistant 已發出 `tool_calls` 且後面接了對應 `tool` 結果，送模副本最後一則可以是 `tool`；此時**不得**為了滿足「最後 user」而硬插假 user，否則會破壞工具協議。
  - 不論哪種情境，第一則（若存在）仍應是 `system`。

### 驗收條件

- 給定含孤兒 tool 的輸入，`build_messages_for_model` 會移除孤兒，且不修改輸入 list 內容（可用 `id(old[i]) != id(out[i])` 或比對副本驗收）。
- 給定缺 tool 回覆的輸入，輸出會補上合成 tool 訊息，使每個 `tool_call_id` 都有對應 tool。
- 給定超長 tool content，輸出會被截斷到 `max_tool_chars`。
- 給定大量可壓縮 tool 輸出，最舊且夠長的會變成單行摘要，但最後 `keep_recent_tools` 則保留原文。
- 給定總成本超線輸入，輸出會**以 user 回合為單位**刪除夠多的舊訊息使成本下降（不要求最優，但要可重現、可解釋刪到哪一輪 user）。
- 給定含多輪 ReAct 的輸入，E 刪除後 `assistant`／`tool` 協議仍完整（不會在中間拆出孤兒 tool 或未回覆的 `tool_calls`）。
- 能一句話說明：為什麼這題要分「完整累積」與「送模用副本」兩份 transcript？

### 藍本對應

以下為**可讀性優先**的示意骨架（不要求與專案逐字一致）：

```python
from typing import Any

COMPACTABLE = {"read_file", "exec", "grep", "glob", "web_search", "web_fetch", "list_dir"}

def build_messages_for_model(
    messages: list[dict[str, Any]],
    *,
    max_chars: int,
    max_tool_chars: int,
    keep_recent_tools: int,
) -> list[dict[str, Any]]:
    out = [dict(m) for m in messages]  # shallow copy rows; replace content strings as needed

    # A drop orphans, B backfill, C truncate tool, D microcompact
    # E snip oldest whole user-turn blocks until cost <= max_chars (same boundary idea as WG-17;
    #    never pop single rows inside assistant/tool chains — A/B already ran and won't re-run)
    # （請依上方規格完成；此處略）

    return out
```


---

## Challenge WG-19：舊對話濃縮成長期備忘——超預算觸發長期記憶整併與每輪讀回組裝

### 情境

**WG-17** 用 `**past`** 裁切，讓「送進主模型的字」不爆線，但舊對話仍完整留在 `**history**` 與 **JSONL**——模型**看不到**被裁掉的那段細節。實務上常把「已離開短期視窗的內容」**壓縮成可重用的長文**，下次開機或下一輪再從檔案**讀回**，塞進 **system**，讓主模型仍握有**高層次脈絡**。

本題規格對齊課堂 **Challenge A（長期記憶整併）**；以下為**與本課 JSONL session 銜接**的節錄。細節與驗收以本題「規格／驗收條件」為準。

### 規格

#### 與 **WG-12～16** 的關係（**不**推翻既有行為）

- **延續**：`**load_session_jsonl`／`save_session_jsonl`**、`**SESSION_JSONL_PATH**`、`**history**` 仍保存**完整**對話（`**user`／`assistant`／`tool`** 與 **WG-15** 一致）與 **metadata**；`**last_consolidated`** 仍寫入 **JSONL** 第一行 **metadata**（與 **WG-17** 語意一致）。
- **新增儲層**（建議目錄結構如下）：專案根下 `**memory/**` 目錄內 `**MEMORY.md**`（**覆寫**式長期正文）、`**HISTORY.md`**（**追加**式、一行一筆摘要或失敗列）。

#### MEMORY.md 記什麼（內容範圍）

`**MEMORY.md**` 是「**下次開對話仍需要的決策與狀態**」，**不是**對話逐字稿、tool 輸出備份，也**不是** `**session.jsonl**` 的替代品。完整對話真相仍只在 `**history**`／**JSONL**；整併 LLM 的任務是**濃縮**，不是**抄寫**。

| 應寫入 MEMORY | 不應寫入 MEMORY |
|---|---|
| 使用者**穩定**偏好（精簡，建議 ≤3 條） | 每輪問答原文、問候、測試算術等一次性互動 |
| **當前任務**目標一句、**進行中**狀態（做到第幾步、還缺什麼） | `**tool**` 成功／失敗過程、路徑錯誤後的 retry 細節 |
| **已確認**的規格或決策（衝突時只保留**目前有效**一條） | 「使用者曾要求 A，後來又改 B」這類**版本史**逐條堆疊 |
| 必要時的專案錨點（例如檔名、攤位名，建議 ≤2 條） | 已寫入 `**skills/<name>/SKILL.md**` 的完整流程正文（MEMORY 只寫「見 skill: xxx」，需要時 `**read_file**`） |
| | 圖表除錯、指令語法錯誤、一次性統計結果等**過程紀錄** |

- **與 Skills 分工**：程序性步驟（例如心得 8 步流程）放在 **Skill**；MEMORY 只保留「正在做哪個任務、關鍵約束、進度」。
- **與 HISTORY 分工**：`**HISTORY.md**` 記「何時整併了哪段主題」的**一行 log**；**不要把** HISTORY 內容再抄進 MEMORY。
- **整併原則**：`**memory_update**` 須在覆寫 `**MEMORY.md**` 時**刪除過期、合併重複**；禁止把待整併 chunk 逐句貼進 MEMORY。若資訊對下一輪無幫助，**不要寫**。

#### 整併與預算（與 Challenge A 同一套語意）

- **觸發與成本**：常數 `**TOKEN_BUDGET`** 名稱與語意同 **WG-17**（**字元長度**近似 token）。成本為：**system 字串**（含下節讀回之長期記憶區塊）**+** 短期 `**past`**（或與 `**history[last_consolidated:]**` 語意相同之未整併段）**+** 本輪 `**human_message`**；演算法須與 **WG-17** 之 `**request_cost_chars**` **同一語意**——若改寫，請在作答檔以**註解**說明對應欄位。
- **嚴格大於** `**TOKEN_BUDGET`** 時才啟動「整併流程」並**得**呼叫 **consolidation 專用** LLM（`**invoke`／`ainvoke`** 等實際呼叫，**不可**略過）；**未超線時不得**為整併而呼叫該 LLM。
- **整併後目標**：整併與 `**last_consolidated`**（游標）更新後、**呼叫主對話 `llm.stream` 之前**，以**同一套**成本公式重算，總成本**必須 ≤ `TOKEN_BUDGET // 2`**（與 template 之 `**target = budget // 2**` 語意一致）。仍高於此值**不得**送主模型，須**繼續**整併／切塊直至達成，或觸發題目已定義之**停止條件**（例如無可用 **user** 邊界——須在程式**註解**說明）。
- **分輪與邊界（整併切塊）**：以 `**last_consolidated`** 為起點，**每輪整併流程只處理一段 chunk**；切分邊界**僅能落在 user-turn 前**（**不可**拆散同一 **user** 回合後之 **assistant／`ToolMessage`** 鏈，亦**不可**把 **user** 與其後第一則 **assistant** 切半）。邊界選擇須能推進整併並朝「整併後目標」收斂；與 **WG-17** 之 `**pick_consolidation_boundary`** 可並用或等價改寫，須**自洽**。游標後若**無任何** `**HumanMessage`** 則該輪**不整併**，等下一 **user** turn。
- **整併單輪內步驟**（成功路徑摘要）：
  1. 讀取目前 `**MEMORY.md`**（不存在視為空）。
  2. 將「待整併之舊 chunk + 現有 **memory** 脈絡」送給 **consolidation 專用** LLM（可與主模型同型號或不同；須為實際 `**invoke`**）。
  3. 期望回傳**可解析的結構化結果**（擇一）：**首選**單一 **JSON** 物件字串，且**僅兩鍵**：`**history_entry`**（字串）、`**memory_update**`（字串，**完整取代** `**MEMORY.md`** 內文之 markdown，且須符合上節「**MEMORY.md 記什麼**」）；**或** **tool call** 兩參數語意同上。解析失敗計入「重試」；若 **provider** 不支援強制 **tool**，需有 **fallback**（例如改要求純 **JSON**），仍須滿足「兩欄可從回應抽出」。
  4. 成功時：`**append_history`** 之**語意**與本課 `**append_history**` 藍本一致——`**HISTORY.md**` 一行 `**[YYYY-MM-DD HH:MM] <內文>**`；`**history_entry**` 應為**單行**（內部換行改空白或截斷）。並**覆寫** `**MEMORY.md`** 為 `**memory_update**`。
  5. 更新 `**last_consolidated**` 並 `**save_session_jsonl**`（寫回 **metadata** 與完整 `**history`**）。
- **失敗策略**：同一 chunk 之 consolidation 最多重試 `**CONSOLIDATION_MAX_RETRIES`** 次（建議 **3**；**0** 表示不重試、直接 **fallback**，須**註解**）。若仍失敗：`**HISTORY.md`** 寫入**一行**，格式 `**[YYYY-MM-DD HH:MM] [CONSOLIDATION-FAILED]`**  後接**單行**（與 Challenge A 一致）；成功列**不得**使用該前綴。失敗後仍須更新 `**last_consolidated`** 使該 chunk 離開短期送入範圍；`**MEMORY.md**` 維持不變或僅註記擇一、**全專案一致**並**註解**。

#### 讀回與每輪送模組裝

- **每次**送主模型前，用於估算與實際 `**SystemMessage.content`** 的**系統字串**（**僅含 WG-12～WG-19**、尚未併 **Skills** 時）至少包含：（1）**WG-12** 之 `**get_identity()`**（課堂規則／顯示名／【執行環境】／【exec 注意】）；（2）自 `**MEMORY.md`** 讀出、以固定標題 `**## Long-term Memory**` 包起來的區塊（標題字串固定；可經 `**memory_block_for_system()`** 組裝）。**長期記憶須緊接在課堂人設之後**，且仍只出現在 `**SystemMessage.content`** 內（**不得**改放成 **user／assistant／tool** 對話列），與 **Challenge A** 語意一致。
- **併入 WG-20（Skills）時**：建議以 `**build_system_prompt(loader)`**（或等價函式）一次組裝，**大段順序**為：**課堂基底**（等同 **WG-12**，可為 `**get_identity()`**）→ **長期記憶**（若有內文；同 `**## Long-term Memory`** 與空檔不注入規則）→ `**# Active Skills**`（僅 `**always: true**` 之正文；多則之間可插 `**---**`；小標建議 `**### Skill: {name}**`）→ `**# Skills**`（僅非 `**always**` 之摘要＋**繁中**說明須以 `**read_file`** 讀清單中路徑之 `**SKILL.md**`，並一句帶過依賴安裝）。**課堂基底與長期記憶之間不得插入 Active／Skills**（維持 **WG-19** 與 **Challenge A** 之「規則先、記憶次之」）。各 **大段** 之間建議以 `**\n\n---\n\n`** 串接。若沒有任何非 `**always**` 技能，**不得**出現空 `**# Skills`** 標題。
- `**history`（或裁切後之 `past`）** 僅含 `**last_consolidated` 之後**、**尚未經整併移出視窗**之短期內容；**不得**把已整併走之舊段再當「新訊息」重送一遍。
- `**MEMORY.md` 為空或僅空白**：不得出現**孤立**之 `**## Long-term Memory`** 標題；與「完全不注入記憶區塊」擇一、**全專案一致**。
- **長度保護**：若 `**MEMORY.md` 純內文**（不含標題）超過 `**MEMORY_MAX_CHARS`**（建議 **6000**），先**由尾端截斷**至該長度再組進 **system**（截斷後再套區塊標題亦可）。**選修**：截斷前對 **memory** 本體再做二次摘要 **LLM**——須**註解**觸發條件；課堂**允許只做截斷**即通過長度保護項。

### 驗收條件

（與 **Challenge A** 之「整併與預算」「讀回與組裝」兩段**逐條對齊勾選**；以下為**轉寫**以利本檔自洽。）

**整併與預算**

- 觸發／不觸發與 **consolidation** 呼叫行為符合上節；送主模型前成本 **≤ `TOKEN_BUDGET // 2`**。
- 成功路徑：短期送入範圍不再含已整併內容，且 `**MEMORY.md`／`HISTORY.md**` 符合上節；失敗路徑：`**HISTORY.md**` 有 `**[CONSOLIDATION-FAILED]**` 列且短期已不含該 chunk。
- **可觀察**：整併當輪有一次 **consolidation** 用 **LLM** 呼叫（非僅調游標）；成功列與失敗列前綴區分正確。
- 能說明：為何整併邊界取在 **user-turn**，而非任意索引切訊息。

**讀回與組裝**

- 每輪讀取約定路徑之 `**memory/MEMORY.md`**；`**history`／`past**` 僅自 `**last_consolidated**` 之後，不重複送入已整併內容。
- **可觀察**：`**MEMORY.md`** 非空時，`**SystemMessage.content**` 含完整子字串 `**## Long-term Memory**`。
- 能說明：長期記憶放 **system** 與放一般對話訊息之差異。
- `**MEMORY.md**` 符合「記什麼／不記什麼」：無對話逐句抄寫、無 tool 輸出全文、無與 **Skill** 重複的長流程；能舉例說明為何某類內容應留在 JSONL 而非 MEMORY。

### 藍本對應

藍本示意涵蓋 **WG-12～WG-19**：含 `**memory/MEMORY.md`／`memory/HISTORY.md**`、`**system_content_for_model()**`（`**## Long-term Memory**`）、`**request_cost_chars**`、超 `**TOKEN_BUDGET**` 時 consolidation 整併與 `**CONSOLIDATION_MAX_RETRIES**`／`**[CONSOLIDATION-FAILED]**` 失敗列，以及送主模型前壓至 **≤ `TOKEN_BUDGET // 2`** 之迴圈。請在**教師指定作答檔**中依藍本分段實作與驗收。

```text
專案根/
  memory/
    MEMORY.md      # 覆寫：精簡備忘（決策／狀態；非對話抄寫）
    HISTORY.md     # 追加：每行 [時間] 摘要 或 [CONSOLIDATION-FAILED] ...
  session.jsonl    # 仍：metadata + user/assistant/tool；metadata 內 last_consolidated
```

---

## Challenge WG-20：技能卡進工具箱——最小 SkillsLoader 與 system prompt 注入

### 情境

前面 **WG-12～WG-19** 已涵蓋 session、JSONL、`past` 裁切與長期記憶整併；**WG-13** 與 **WG-14** 已涵蓋 **ReAct** 與 workspace 檔案／shell 工具；本題補上如何把「程序知識」以 **skill** 形式寫成 `SKILL.md`，並在啟動時穩定注入 **system prompt**（摘要＋必要時全文）。

下列做法很適合拆給學生理解：**skill 不是 Python tool，也不是模型直接可呼叫的函式**；它是一份 markdown 程序知識。runtime 先掃描 `skills/<name>/SKILL.md`，讀 frontmatter 的 `description` 做摘要；若該 skill 標成 `always`，才把正文去掉 frontmatter 後完整注入 system prompt。其他 skill 只出現在摘要清單中，提醒模型：「需要時請讀這個 `SKILL.md`。」

本題只做「最小可理解架構」：掃目錄、讀檔、取 frontmatter、合併 workspace／builtin、組出 system prompt。**不要求**真的讓 LLM 自動選 skill，也不要求實作 MCP、自訂 **`Tool`／`ToolRegistry` 類別**、sandbox 權限或背景 Dream agent。

### 規格

#### 檔案結構

- 在專案根建立兩個 skill 根目錄（可依教師指定簡化為只做一個）：
  - `**skills/`**：使用者或學生自訂 skill。
  - `**builtin_skills/`**：教師提供的內建 skill 範例。
- 每個 skill 是一個資料夾，底下必須有 `**SKILL.md**`：

```text
專案根/
  作答檔.py
  skills/
    class-helper/
      SKILL.md
  builtin_skills/
    summarize/
      SKILL.md
```

- `**SKILL.md**` 最小格式須含 YAML-like frontmatter 與正文：

```markdown
---
name: class-helper
description: 協助學生把問題拆成步驟，適合卡關時使用。
always: false
---

# Class Helper
先問學生目前做到哪一步，再給一個最小提示，不直接給完整答案。
```

#### `SkillEntry` 與讀取函式

- 建議定義一個小資料結構（`dataclass` 或 dict 皆可）保存：
  - `name`
  - `path`
  - `source`（`"workspace"` 或 `"builtin"`）
  - `description`
  - `always`
  - `body`
- 實作 `**split_frontmatter(text: str) -> tuple[dict[str, str], str]**` 或等價函式：
  - 若檔案開頭是 `---`，讀到下一個單獨一行 `---` 為止。
  - 至少能解析 `name: ...`、`description: ...`、`always: true/false` 三種簡單鍵值。
  - 回傳 metadata 與去掉 frontmatter 後的 markdown body。
  - 不要求支援巢狀 YAML、陣列、多行字串；本題以課堂簡化格式為準。
- skill 的識別名稱以**資料夾名稱**為準（對齊本課 **SkillsLoader** 規格）；frontmatter 內的 `name` 可要求與資料夾同名，或只當作顯示資訊。若 `description` 不存在，使用資料夾名稱作為 fallback。

#### `SkillsLoader`

- 實作一個 `**SkillsLoader`** 類別或同等函式群：
  - 初始化接收 `workspace: Path` 與 `builtin_skills_dir: Path`。
  - `workspace_skills = workspace / "skills"`。
  - `list_skills()` 掃描兩個根目錄底下的第一層資料夾，只收有 `**SKILL.md`** 的項目。
  - 先列 workspace skills，再列 builtin skills。
  - 若 workspace 與 builtin 有同名 skill，**workspace 版本優先**，builtin 同名版本不列入。
  - 略過一般檔案、沒有 `SKILL.md` 的資料夾、空目錄。
- 實作 `**load_skill(name: str)`**：
  - 先找 `skills/<name>/SKILL.md`，再找 `builtin_skills/<name>/SKILL.md`。
  - 找不到則回傳 `None` 或拋出清楚錯誤（擇一，但驗收時須能說明）。

#### system prompt 組裝

- 實作 `**build_skills_summary(entries)`**：
  - 對每個非 `always` skill 產生一行摘要，格式可自訂，但須含 **skill 名稱、description、SKILL.md 路徑**。
  - 範例（一行）：`**class-helper`**、description、以及反引號內 `**skills/class-helper/SKILL.md**` 路徑皆須可從該行讀出。
- 實作 `**build_system_prompt(loader: SkillsLoader) -> str**`（或等價名稱），將 **WG-12** 課堂基底、**WG-19** 長期記憶（若有）、與本題 **Skills** 併成**單一**送模用字串（亦供 **WG-17** 成本估算與 `**SystemMessage.content`** 使用）。**建議大段順序**：
  1. **課堂基底**：直接呼叫 **WG-12** 之 `**get_identity()`**（含【執行環境】與【exec 注意】）。
  2. **長期記憶**：同 **WG-19** `**memory_block_for_system()`** 語意（有內文才 append）。
  3. **Active Skills**：`always: true` 的 skill，放入 **去掉 frontmatter 後的正文**；區塊標題 `**# Active Skills`**。
  4. **Skills**：`build_skills_summary` 產生之清單；區塊標題 `**# Skills`**；其前附**繁體中文**短引導（須明示以 `**read_file`** 讀取清單中路徑之 `**SKILL.md**`，並一句帶過「若需套件／環境請先依該檔或專案說明安裝」）。
- **大段之間**建議以 `**\n\n---\n\n`** 串接（可讀性）；**不得**在「課堂基底」與「`**## Long-term Memory`**」之間插入 **Active／Skills**（與 **WG-19** 讀回小節一致）。
- 若沒有任何非 `**always`** skill，**不得**出現空的 `**# Skills`** 標題；若完全沒有 skill，亦**不**出現空 **Active** 標題。

#### Tool schema 驗證與參數 cast（銜接 **WG-13**／**WG-14**）

延續 **WG-14** 以 **`@tool`** 暴露的 **`BaseTool`**（並列於 **`TOOLS`**）：模型經 **function calling** 回傳的 **`tool_calls` 參數**常是**字串或寬鬆 JSON**，在呼叫 **`BaseTool.invoke`**（或進入檔案／`exec` 的實作邏輯）前，須先**依輸入 schema 做安全 cast**，再**驗證型別與必填欄位**，避免把髒資料餵進檔案工具或 **`exec`**。

- **JSON Schema 來源（擇一即可）**：
  - 由 **`TOOLS`** 內各 **`BaseTool`** 取得輸入 schema（例如從 **`tool.args_schema`** 取得 **Pydantic** 模型並呼叫 **`model_json_schema()`**，或 LangChain 版本提供的等價 API）；**或**
  - 為 **WG-14** 五支工具手寫簡化版 **`parameters: dict`**，至少支援 `**{"type": "object", "properties": {...}, "required": [...]}**`。
  - `**properties**` 內各欄的 `**type**` 至少支援 **`string`**／**`integer`**／**`number`**／**`boolean`**。
  - **選修**：`**array`**（僅一層元素）、`**object**`（巢狀一層）。
- `**cast_params(params: dict) -> dict**`：在驗證**之前**呼叫；語意對齊 **`cast_params`** 藍本——例如 `**"42"**` 在 `**type: "integer"**` 時轉成 `**int**`；`**"true"`／`"false"**`（大小寫不敏感）在 `**boolean**` 轉成 `**bool**`；已符合目標型別則保留；無法轉換時可保留原值交給驗證階段報錯（**全班實作一致**即可）。
- `**validate_params(params: dict) -> list[str]`**：回傳**錯誤訊息串列**（**空**表示通過）；須檢查 `**required`** 缺欄、各欄 `**type**` 與 `**properties**` 鍵是否多出未定義欄位（擇一策略，**註解**說明）。**課堂可自寫檢查器**，不必實作完整 **JSON Schema** 草案。
- `**prepare_tool_call(name: str, raw: Any) -> tuple[BaseTool | None, dict[str, Any], str | None]`**（函式名可自訂）或**等價流程**：工具名在 **`TOOLS`** 對照表中不存在、或 **`raw`** 無法視為 **dict**（**JSON object**）時，第三個回傳值為**單一錯誤字串**（前兩者為 **`None`／空 dict**）；否則依序 **`cast_params` → `validate_params`**，若有錯誤則組成單一 **`error`**（例如分號串接多條訊息），**不**呼叫 **`BaseTool.invoke`**。

#### 設計參考重點

- **Skills 掃描與載入**（對應 `SkillsLoader` 概念）：
  - `skills/<name>/SKILL.md` 是被發現的最小單位。
  - workspace skill 會覆蓋同名 builtin skill。
  - `build_skills_summary` 只把摘要放進 prompt，避免一次塞入所有 skill 正文。
- **system prompt 組裝**（對應 `ContextBuilder` 概念）：
  - `always` skill 的正文可直接進 system prompt。
  - 一般 skill 只進摘要，等模型需要時再讀全文。
- 本題不實作進階依賴檢查、`disabled_skills`、額外 metadata、sandbox 擴充目錄等；這些可列為選修或下一題。
- **工具參數**須依 **`cast_params`／`validate_params`** 流程，並在 **`invoke` 實作前** 完成驗證（對應 `prepare_call` 流程順序）（先 cast、再驗證、最後才執行工具）：本題改以 **`prepare_tool_call`** + **`BaseTool.invoke`** 對齊同一順序即可，**不**要求自訂 **`Tool`／`ToolRegistry` 類別**，亦不要求 **async** 或與執行緒並發細節逐字相同。

### 驗收條件

- 建立至少兩個 skill：一個在 `skills/`、一個在 `builtin_skills/`，且皆有 `SKILL.md`。
- `list_skills()` 只列出有 `SKILL.md` 的資料夾，並略過一般檔案與缺少 `SKILL.md` 的資料夾。
- 當 `skills/demo/SKILL.md` 與 `builtin_skills/demo/SKILL.md` 同名時，清單與載入結果使用 workspace 版本。
- `split_frontmatter` 能取出 `description`，且組出的摘要列含 skill 名稱、description、路徑。
- `always: true` 的 skill 正文會出現在 **Active Skills** 區塊，且不再重複出現在一般摘要清單。
- 一般 skill 不把全文塞進 system prompt，只出現在摘要清單。
- 能說明：為什麼 skill 不等於 tool？若模型需要使用某個一般 skill，為什麼應該先讀 `SKILL.md`？
- **邊界**：若 `SKILL.md` 沒有 frontmatter，程式仍不崩潰，且至少能用資料夾名稱作為 skill 名稱。
- `**prepare_tool_call`**：對 `**read_file**`（或自訂一個 `**integer**` 參數的示範 **`@tool`**）傳入**字串形式的數字**，`**cast_params`** 後 `**validate_params**` 為空；缺 `**required**` 欄位時 `**validate_params**` 非空且 `**prepare_tool_call**` 不呼叫 **`BaseTool.invoke`**。
- 能一句話說明：為什麼要先 `**cast_params**` 再 `**validate_params**`（而不是只驗證原始字串）？

### 藍本對應

以下為**結構示意**（可直接放入教師指定作答檔擴寫）；重點是函式邊界與資料流，不要求與任何參考實作逐字一致。

```python
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SkillEntry:
    name: str
    path: Path
    source: str
    description: str
    always: bool
    body: str

def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, text

    meta: dict[str, str] = {}
    for raw in lines[1:end]:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        meta[key.strip()] = value.strip()

    body = "\n".join(lines[end + 1 :]).strip()
    return meta, body

class SkillsLoader:
    def __init__(self, workspace: Path, builtin_skills_dir: Path) -> None:
        self.workspace_skills = workspace / "skills"
        self.builtin_skills = builtin_skills_dir

    def _entries_from_dir(self, root: Path, source: str, skip: set[str]) -> list[SkillEntry]:
        if not root.exists():
            return []

        entries: list[SkillEntry] = []
        for skill_dir in root.iterdir():
            skill_file = skill_dir / "SKILL.md"
            if not skill_dir.is_dir() or not skill_file.exists():
                continue
            if skill_dir.name in skip:
                continue

            text = skill_file.read_text(encoding="utf-8")
            meta, body = split_frontmatter(text)
            name = skill_dir.name
            description = meta.get("description") or name
            always = meta.get("always", "false").lower() == "true"
            entries.append(SkillEntry(name, skill_file, source, description, always, body))
        return entries

    def list_skills(self) -> list[SkillEntry]:
        workspace_entries = self._entries_from_dir(self.workspace_skills, "workspace", set())
        workspace_names = {entry.name for entry in workspace_entries}
        builtin_entries = self._entries_from_dir(self.builtin_skills, "builtin", workspace_names)
        return workspace_entries + builtin_entries

    def load_skill(self, name: str) -> str | None:
        for root in (self.workspace_skills, self.builtin_skills):
            path = root / name / "SKILL.md"
            if path.exists():
                return path.read_text(encoding="utf-8")
        return None

def build_skills_summary(entries: list[SkillEntry]) -> str:
    summarized = [e for e in entries if not e.always]
    if not summarized:
        return ""
    lines = [f"- **{e.name}** — {e.description} `{e.path}`" for e in summarized]
    return "\n".join(lines)


# get_identity() 沿用 WG-12 藍本，此處不重複定義。

def memory_block_for_system() -> str:
    """WG-19：有 MEMORY.md 內文才回傳 ## Long-term Memory 區塊；此藍本略讀檔，實作請接真檔案。"""
    return ""


def build_system_prompt(loader: SkillsLoader) -> str:
    """課堂基底 → 長期記憶（若有）→ Active Skills → Skills 摘要（若有）。"""
    parts: list[str] = [get_identity()]
    mem = memory_block_for_system()
    if mem:
        parts.append(mem)

    entries = loader.list_skills()
    active = [e for e in entries if e.always]
    if active:
        body = "\n\n---\n\n".join(f"### Skill: {e.name}\n\n{e.body}" for e in active)
        parts.append(f"# Active Skills\n\n{body}")

    summary = build_skills_summary(entries)
    if summary:
        intro = (
            "下列技能可擴充你的能力。若要使用某技能，請用 read_file 讀取清單中該技能路徑下的 SKILL.md。\n"
            "若該技能需額外套件或環境，請先依 SKILL.md 或專案說明安裝相依項目後再操作。\n\n"
        )
        parts.append("# Skills\n\n" + intro + summary)
    return "\n\n---\n\n".join(parts)
```


---

## Challenge WG-21：眼睛也進對話——多模態附圖、`image_path` 與 JSONL 載回閉環

### 情境

**WG-08～12** 已讓每則使用者訊息以**純文字**送進模型；**WG-15～16** 則把 `**user`／`assistant**`（與可選 `**tool**`）寫入／讀回 JSONL。實務上常需要「**這一輪使用者順便附上一張圖**」（例如活動現場照片、螢幕截圖），讓支援**視覺（vision）**的模型一併理解。

本題為**完整版（磁碟層）**規格：**不在 JSONL 裡持久化圖檔位元組或長串 base64**（避免存檔暴肥、版本控制與除錯困難）；改在 `**user**` 列上增加**可選**的 **`image_path`**（與可選 **`media_type`**），關閉程式後再開仍能還原「**哪一輪曾附圖、圖檔在哪**」之語意。

**送模層**另依**實務**處理（見下方「送模層（實務／本題必做）」）：**不要**在每一次 `**invoke**`／`**stream**` 都把歷史裡每一張舊圖再以 base64 重送進模型，以免請求體與成本失控；改為「**僅本輪**若附圖才組多模態；舊附圖回合在送模訊息中改為純文字占位」。

### 規格

#### 先修與依賴

- 須已能組出 **WG-12** 送模結構：`**[system_message, *history, human_message]**`（或課堂合併版之等價結構），並具備 **WG-15**（寫入）與 **WG-16**（載回）之 JSONL 行為。
- 本題**不要求**在驗收場景中實作 **WG-13** **ReAct**／`**tool_calls**`／`**ToolMessage**` 鏈（若學生專案已併入工具，只要 `**user**` 列擴充與載回邏輯仍正確即可）。

#### 模型與套件

- 須使用支援**多模態輸入**的聊天模型（例如 **`gpt-4o`** 或課程指定之等價模型）；`**ChatOpenAI**` 之 `**model**` 須可在環境變數或常數中設定，並在 README／註解註明「本題需 vision」。
- 以 **`langchain_core.messages.HumanMessage`** 建立使用者訊息；當本輪含圖時，`**HumanMessage.content**` 為**串列**，元素為供應商要求之**內容區塊**（dict）。與 **OpenAI Chat Completions 相容**之常見形狀如下（教師可依實際 **LangChain** 版本微調鍵名，以「能成功 `**invoke**`／`**stream**`」為準）：
  - 一則 **`{"type": "text", "text": "<使用者文字>"}`**。
  - 一則 **`{"type": "image_url", "image_url": {"url": "<data URL 或 https URL>"}}`**；本題驗收採 **data URL**：`**data:{media_type};base64,{base64_string}**`。

#### 讀圖與編碼

- 以 **`Path`** 或字串路徑解析 **`image_path`**；相對路徑之**根目錄**由教師約定（建議為**專案根目錄**）。**選修（安全）**：`**Path.resolve()**` 後須仍落在約定根目錄之下（防止 `**..**` 或絕對路徑逃出專案）；否則拒絕附圖並提示。
- 以 **`with open(path, "rb") as f: data = f.read()`** 讀取影像；使用 **`base64.b64encode(data).decode("ascii")`** 取得 base64 字串。
- **`media_type`**：若使用者未提供，可由副檔名推斷（例如 `.png` → `**image/png**`、`.jpg`／`.jpeg` → `**image/jpeg**`），推斷失敗時須有合理預設或明確錯誤訊息（二擇一寫進驗收）。

#### JSONL 之 `user` 列（擴充 **WG-15**）

- 無圖之回合：維持 **WG-15** 既有格式（例如 **`role`／`content`／`timestamp`**），**不**出現 **`image_path`**，或 **`image_path`** 為 **`null`**／空字串（與載入端約定一致即可）。
- 有圖之回合：除原有文字欄外，新增：
  - **`image_path`**：`str`，相對於約定根之路徑（**不得**寫入 base64 或二進位）。
  - **`media_type`**（可選）：`**image/png**`、`**image/jpeg**` 等；省略時由載入端推斷。
- **仍不得**將 **`SystemMessage**` 寫入 JSONL（與 **WG-15** 相同）。

#### 載回（擴充 **WG-16**）— 記憶體中的 `history`

- 讀到 **`role: "user"`** 列時：若僅有文字（無 **`image_path`**），組**純字串** `**HumanMessage(content=...)**`（與 **WG-16** 一致）。
- 若含有效 **`image_path`**：**建議預設（本題驗收以此為準）**還原為**純字串** `**HumanMessage**`，內文為**原 `content` 文字**加上可讀占位（例如單獨一行 **`[此回合曾附圖，路徑：{image_path}]`**；若亦存了 **`media_type`** 可一併寫進占位）。**冷啟動載入時不必**為了還原 `history` 而讀取影像位元組。
- **選修（進階）**：載入時仍組**多模態** `**HumanMessage**`（讀檔＋ data URL）亦可，但**必須**搭配下方「送模層」在送進模型前剝除**非本輪**之 `**image_url**` 區塊，驗收仍以下方送模規則為準。
- 若 **`image_path`** 有值但檔案**不存在**或**無法讀取**（僅在「本輪真的要送圖」讀檔時才會發生；占位還原不依賴檔案存在）：行為須**明確實作並記錄於程式註解或終端**（擇一即可寫進驗收）：
  - **略過圖**：改為僅文字之 `**HumanMessage**`，並 `**print**` 一則警告；或  
  - **明確失敗**：拋出例外或印錯誤並略過該列（與 **WG-16**「壞行略過」精神相容時，須能說明取捨）。

#### 送模層（實務／本題必做）

在每次呼叫 `**llm.invoke(...)**` 或 `**llm.stream(...)**` 之前，須以函式（建議名 **`messages_for_model`**，與 **WG-18** 精神對齊）從 `**[system_message, *history, human_message]**`（或課堂等價結構）產出**實際送進模型**的訊息串列副本，**不得**直接改壞 JSONL 來源資料（可 deep copy 或建新串列）。

- **本輪** `**human_message**`：若使用者本輪有附圖，**可以**（也應）為**多模態**（文字區塊＋`**image_url**`／data URL），並在此時才依「讀圖與編碼」一節執行二進位讀檔、base64、組圖區塊（**不要**在僅還原 `history` 占位時讀圖）。
- **歷史** `**history**` 內之舊 `**user**` 回合：送模副本中**一律不得**含有 `**image_url**` 區塊（含 data URL）。若 `history` 內誤留多模態舊訊息，必須在 `**messages_for_model**` 內轉成**純字串** `**HumanMessage**`，且字串內仍須保留**原使用者文字**與 **`image_path` 占位**（與載回規格一致），讓模型知道「曾有圖」但**不要求**模型在無新圖輸入時重新「看見」像素。
- **單次請求中**，含 `**image_url**`（非 `https` 小圖示範外的一般情境即 data URL）之 `**HumanMessage**` **至多一則**（即本輪那一則；若本輪無圖則為零則）。
- **後續多輪若要延續圖中細節**：實務上依賴當時 **assistant** 回覆裡的**文字描述**（本題**建議**在驗收示範中要求：附圖輪之助手回覆須包含對圖片內容的一句以上具體描述，供之後純文字輪使用）。**不**把「模型仍看得到舊圖像素」當作必驗條件。

#### 互動（建議最小形狀）

- 課堂可約定單一指令，例如使用者輸入 **`/image 相對路徑`** 後再輸入**同一輪**之文字問題；或兩行式 `**input**`（先路徑、後文字）。重點是：**程式能區分「本輪是否附圖」**並正確寫入 JSONL。

### 驗收條件

- 在**有金鑰**且模型支援 vision 的前提下，**同一輪**送進 `**stream**` 的 `**HumanMessage**` 於附圖時為**含文字區塊與 image 區塊**之結構，且模型回覆能合理呼應圖片內容（教師可用專案內一張**固定示範圖**驗收）。若課堂使用的 vision 模型或供應商路徑暫不支援串流，才可退回 `**invoke**`，但須在程式註解或驗收說明中明確標示原因。
- **寫檔後**以文字編輯器或 `**print**` 檢查 JSONL：**不得**出現長度明顯為整檔圖片之 base64 欄位塞在單一 `**user**` 列內；**應**能看到精簡的 **`image_path`**（與可選 **`media_type`**）。
- **關閉程式再開**：載入 JSONL 後，含 **`image_path`** 之舊 `**user**` 回合在 `**history**` 中應還原為**純文字**（含 **`[此回合曾附圖，路徑：…]`** 類占位），且 JSONL 檔內仍**只**有精簡路徑、**無**長 base64。重開後使用者**新的一輪**若再附圖，送進模型之該輪 `**HumanMessage**` 仍須為多模態且能合理呼應該張新圖。
- **送模層**：在「已有一則以上含 `**image_path**` 占位之歷史」且「本輪又附一張新圖」之情境下，實際送入 `**invoke**`／`**stream**` 的訊息列中，**至多一則** `**HumanMessage**` 含 `**image_url**`／data URL（即本輪）；其餘舊附圖回合僅能是純文字占位。能於程式碼或註解指出 **`messages_for_model`**（或等價函式）何處完成此轉換。
- 將示範圖**暫時改名或移走**後再開程式：於**本輪再次**以該路徑附圖送模時，行為符合**規格**中「檔案不存在」之約定（略過圖＋警告，或明確錯誤處理）。
- （建議）附圖那一輪之 **assistant** 回覆至少包含**一句以上**對圖像內容的具體描述，以利後續純文字輪延續討論（呼應送模層「舊圖不重送像素」之實務）。
- 能口頭或書面說明：**為何 JSONL 只存路徑、不存整張圖的 base64？**（檔案大小、可維護性、單一真相來源等任舉兩項合理理由即可。）

### 藍本對應程式（結構示意）

以下示意三層：**JSONL 一列**（只存路徑）、**載入 `history` 之純文字占位**、**本輪送模才組多模態**；並示意 **`messages_for_model`** 保險剝除歷史中的圖區塊。**不**與 **WG-15** 整檔寫入、`**metadata**` 首行等強綁——學生應併入自己已通過之 session 流程。

```python
import base64
import copy
from pathlib import Path

from langchain_core.messages import BaseMessage, HumanMessage

def image_bytes_to_data_url(data: bytes, media_type: str) -> str:
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{media_type};base64,{b64}"


def guess_media_type(path: Path, fallback: str = "image/png") -> str:
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return fallback


def user_row_dict(text: str, image_rel: str | None, media_type: str | None) -> dict:
    """寫入 JSONL 的 user 列：沿用 WG-15 時請補上 timestamp 等欄位。"""
    row: dict = {"role": "user", "content": text}
    if image_rel:
        row["image_path"] = image_rel
        if media_type:
            row["media_type"] = media_type
    return row


def load_user_row_to_history_human(row: dict) -> HumanMessage:
    """冷啟動載入 history：有 image_path 亦只還原為純文字占位，不讀圖。"""
    text = row.get("content", "")
    rel = row.get("image_path")
    if not rel:
        return HumanMessage(content=text)
    mt = row.get("media_type")
    extra = f"[此回合曾附圖，路徑：{rel}]"
    if mt:
        extra += f"（media_type={mt}）"
    return HumanMessage(content=f"{text}\n\n{extra}")


def build_human_message_for_current_turn(
    text: str, image_rel: Path | None, project_root: Path
) -> HumanMessage:
    """僅「本輪」可組多模態；此時才 open(rb)。"""
    if image_rel is None:
        return HumanMessage(content=text)

    full = (project_root / image_rel).resolve()
    if not full.is_file():
        print(f"[warn] missing image for current turn: {image_rel}")
        return HumanMessage(content=text)

    media_type = guess_media_type(full)
    url = image_bytes_to_data_url(full.read_bytes(), media_type)
    return HumanMessage(
        content=[
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": url}},
        ]
    )


def _human_to_text_only_placeholder(m: HumanMessage) -> HumanMessage:
    """若 history 內誤留多模態 user，送模前轉成純字串（保守剝除 image_url）。"""
    c = m.content
    if isinstance(c, str):
        return m
    if isinstance(c, list):
        parts: list[str] = []
        for block in c:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            # image_url 區塊不帶入新字串；改由占位提醒（實作可再加「曾有圖」）
        body = "\n".join(p for p in parts if p).strip() or "[（無文字）此則曾含圖，已於送模層剝除圖區塊]"
        return HumanMessage(content=body + "\n\n[送模層已剝除歷史圖區塊]")
    return HumanMessage(content=str(c))


def messages_for_model(
    system_message: BaseMessage,
    history: list[BaseMessage],
    human_message: HumanMessage,
) -> list[BaseMessage]:
    """送模副本：歷史內 HumanMessage 一律不得含 image_url；本輪 human_message 保留多模態。"""
    out: list[BaseMessage] = [copy.deepcopy(system_message)]
    for m in history:
        mm = copy.deepcopy(m)
        if isinstance(mm, HumanMessage) and not isinstance(mm.content, str):
            mm = _human_to_text_only_placeholder(mm)
        out.append(mm)
    out.append(copy.deepcopy(human_message))
    return out
```

---

## 附錄：七份 Python 教材內可參考的「學習順序」標題（教師速查）

以下僅供**編輯教案**時參考用，不必整段給學生；學生端以各 Challenge 的情境與驗收為主。

- **1 基礎資料與變數**：資料有型態 → 型態轉換 → 變數與賦值 → 命名與註解 → 作用範圍。
- **2 運算與輸入輸出**：運算式與運算子 → 型態下的運算效果 → `print()` → `input()` 與轉型 → 字串格式化。
- **3 條件與迴圈**：布林邏輯 → `if` → `if-else`／`elif` → `while` → `for`／`range()` → 條件與迴圈組合。
- **4 資料結構**：串列基礎 → 批次操作 → 迴圈讀串列 → 切片與串接 → 元組 → 字典與 `get()`／`in`。
- **5 函式與模組**：為何要有函式 → `def`／參數／`return` → 預設參數 → 作用範圍 → 內建與字串函式 → `import` 三型 → `random`／`time`。
- **6 檔案與例外**：`open()` 模式 → `with open` → 指標與寫入 → `os`／`os.path` → `try`／`except` → 檔案＋例外整合。
- **7 類別與測試**：類別作模組化 → 基本結構 → 類別與物件 → 屬性與方法 → `unittest` 最小結構 → `if __name__ == '__main__'`。

---
