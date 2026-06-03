# Agent Workshop — WG-22 拆檔（peas-workshop-advanced-coach）

本檔為 **peas-workshop-advanced-coach** skill 專用教案（**僅含 WG-22**）。**前置**：學生須已完成 **WG-12～21**（單檔合併藍本）；作答為 **`agent_core.py`** + **`main.py`**。拆檔**起點**對照 **`references/starter_main_wg21.py`**（=`W1-W21.py`）；**驗收標準**對照 **`references/reference_agent_core.py`** + **`references/reference_main.py`**（WG-22 拆檔後）。**執行 Agent（WG-19 整併）必備資產**：專案根 **`prompts/memory_merge.md`**、**`templates/memory/MEMORY.md`**；缺檔時教練自 **`references/project_assets/`** 複製至專案根（只補缺、不覆寫）。

- **串流要求（WG-10 起）**：除工具判斷、工具執行、JSONL 載入、長期記憶整併等**內部步驟**可使用 `invoke` 外，凡是「最後要顯示給使用者看的 assistant 文字回覆」都必須使用 `stream` 串流輸出；不得只以 `print(response.content)` 一次印出最終回答。

---

## Challenge WG-22：核心與殼分家——`agent_core.py` 與 `Agent.chat`

### 情境

**WG-12～21** 已把 ReAct、JSONL、預算整併、Skills、附圖等收在**單一**合併藍本（WG-22 前約千行單檔，對照 **`references/starter_main_wg21.py`**）。實務上要接 Web UI、測試或第二種入口時，需要把「**Agent 怎麼想、怎麼記**」與「**終端怎麼問**」分開；本題即將該單檔邏輯遷入 **`agent_core.py`**。

本題要求：在**不改變對外行為**的前提下，將 **WG-12～21 全部執行邏輯**遷入 **`agent_core.py`**，並以 **`class Agent`** 對外提供**單一**入口 **`chat(...)`**；**`main.py`** 為**唯一** CLI（`input`／`print`、離開指令、**WG-21** **`/image`** 解析）。

**本題不在挑戰規格內**：Streamlit／Gradio 等 Web UI（課堂可另作口頭選修專題，用已拆好的 **`Agent`** 做應用；**不**納入本題驗收）。

**驗收基準**：拆檔後 **`uv run main.py`** 之對話、工具、JSONL、整併、附圖行為，與拆前 **`references/starter_main_wg21.py`**（或拆前專案根 **`main.py`** 單檔）等價；拆後結構須對齊 **`references/reference_agent_core.py`** + **`references/reference_main.py`**（允許差異：僅檔案位置、**`Agent`** 封裝、註解）。

---

### 規格

#### 先修與依賴

- 須已完成 **WG-12～21**（拆檔**前**以專案根 **`main.py`** 單檔或 **`references/starter_main_wg21.py`** 為起點；**尚無** **`agent_core.py`** 或尚未完成拆檔；含 **ReAct**、JSONL、**WG-19** 整併、**WG-21** **`image_path`**）。
- 本題為 **AI Coding 實戰／重構題**：規格以**可機讀契約**為主；Coding Agent 實作時**不得**自行增刪檔名、改 **`Agent`** 公開 API、或引入本題未列之框架。

#### 檔案與職責（必守）

| 路徑 | 角色 | 必含 | 不得含 |
| --- | --- | --- | --- |
| **`agent_core.py`** | Agent 核心（**必建**） | **`class Agent`** 及 **WG-12～21 全部執行邏輯**（見下方遷移表） | **`input()`**；**`if __name__ == "__main__"`** 互動主迴圈 |
| **`main.py`** | CLI 進入點（**必改**） | **`Agent.from_env()`**、**`while`** 讀 **`input`**、**`/image`** 解析、呼叫 **`agent.chat(...)`**、離開指令 | **`run_react_turn`**、**`save_session_jsonl`**、**`ensure_budget_before_react`** 等核心邏輯（須在 core） |

- **不得**另建 **`agent.py`**、**`AgentSession`**、**`ChatBot`** 等替代檔名／類名取代 **`Agent`**／**`agent_core.py`**。
- **不得**把 **WG-12～21** 邏輯留一份在 **`main.py`**、一份在 **`agent_core.py`**（**單一真相來源**在 core）。

#### 公開 API 契約（`agent_core.py`）

**類別名**必須為 **`Agent`**（不可改名）。

**1. 工廠方法**


- **必須**在 **`from_env`** 內呼叫 **`load_dotenv()`**。
- **必須**檢查 **`OPENAI_API_KEY`**：若不存在，**必須**抛出 **`RuntimeError`**（訊息須提示檢查 `.env`；**不得**在 core 內用 **`input`**）。CLI 捕捉後 **`print`** 即可。
- **`session_path`**：省略時讀 **`os.getenv("SESSION_JSONL_PATH", "session_wiki_wg.jsonl")`**（與拆前一致）。
- **必須**在 **`from_env`** 內完成拆前 **`main()`** 啟動段之等價初始化：載入 JSONL（**WG-16**）、建立 **`ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)`**、**`bind_tools(TOOLS)`**、還原 **`last_consolidated`** 等 **`Agent`** 實例狀態。

**2. 單輪對話**


| 項目 | 規定 |
| --- | --- |
| **`user_text`** | 本輪使用者文字（可為空字串，但若 **`image_path`** 亦為空則 CLI 不應呼叫） |
| **`image_path`** | 可選；**必須**為**相對 `PROJECT_ROOT`** 之路徑（**WG-21** **`image_path` 路徑契約**）；**絕對路徑**須 **`PermissionError`** 並略過附圖。語意同 **WG-21**（**`resolve_project_image_path`**、**`build_human_message_for_current_turn`**、占位 **`history_human`**） |
| **`on_token`** | 可選；**`None`** 時 assistant 串流 token **必須**與拆前相同以 **`print(..., end="", flush=True)`** 輸出 |
| **`on_token` 非 `None`** | 每收到一段 assistant **文字** token，**必須**呼叫 **`on_token(token_str)`**，**且不得**再對同一段 token **`print`**；**工具／整併／JSONL 等 core `print` 仍可能存在**（見「串流與工具輸出」UI 殼層小節） |
| **回傳值** | 本輪 ReAct 結束後 assistant **最終文字**（**`str`**，同拆前 **`run_react_turn`** 之 **`final_text`**） |
| **單輪內必做** | 與拆前 **`main()`** 一輪等價：**WG-19** **`ensure_budget_before_react(llm, ...)`**（**`llm`** 為同一實例）、**WG-13** **`run_react_turn`**、**WG-15** **`save_session_jsonl`**、**`history.extend(turn_messages)`** |
| **模型** | **全程** **`gpt-5.4-mini`**；**不得**另建第二 model 名或 **`consolidation_llm`** 變數指向不同 model |

**3. 串流與工具輸出**

- **Assistant 可見回覆**：仍須 **`stream`**（**WG-10**）；經 **`_stream_model_response`**（或等價）累積為 **`AIMessage`**。
- **`on_token` 為 `None`**（**`main.py` CLI**）：行為與拆前單檔藍本一致（含 CLI 在 **`chat`** 前 **`print("\n助手：", end="", flush=True)`** 之慣例——此 **`print`** 留在 **`main.py`**，不在 core 強制）；core 內工具／整併／JSONL 等 **`print`** **須**正常出現在**真實終端**。
- **`on_token` 非 `None`**：assistant **文字 token 僅**經 **`on_token`** 輸出（**不**再 **`print`** 同段 token）；**但** core **仍可能** **`print`** 下列內容（與拆前等價，**不**強制改 callback）：
  - ReAct 內 **`print()`** 換行、**`[工具 …]`** 結果
  - **WG-19** 整併規劃／進行中提示
  - **JSONL** 寫入完成提示（含中文）
- **UI 殼層與 core 的 `print`（第二入口必讀）**：Web UI／GUI 等**非終端**入口呼叫 **`Agent.chat(..., on_token=...)`** 時，宿主常**攔截或改寫 stdout**。在 **Windows** 上，core 對該 stdout **`print(..., flush=True)`**（尤其含中文）可能抛出 **`OSError: [Errno 22] Invalid argument`**，導致整輪 **`chat`** 失敗——**不是**模型或附圖路徑錯誤。**殼層責任**（**不**改 **`main.py`**、**不**要求 core 必改）：在 **`agent.chat`** 外層以 **`contextlib.redirect_stdout`／`redirect_stderr`**（或等價）暫時導走 core 的 **`print`**；assistant 串流仍只靠 **`on_token`** 更新 UI。**`main.py`**（**`on_token=None`**）**不得**套用此導向，須保留終端 **`print`** 行為。
- **本節不**展開 Streamlit／Gradio 等 Web UI 實作（**非** WG-22 必交）。

#### 遷移清單（必須位於 `agent_core.py`）

自 **`references/starter_main_wg21.py`**（WG-12～21 單檔藍本）遷入 **`agent_core.py`**（名稱可保留；**邏輯不得缺失**）：

| 區塊 | 代表符號（非 exhaustive） |
| --- | --- |
| WG-13～14 | **`get_identity`**、**`TOOLS`**、**`@tool`** 五支＋**`add_numbers`**、**`_run_bound_tool`**、**`resolve_workspace_path`**、**`WORKSPACE`** |
| WG-15～16 | **`save_session_jsonl`**、**`load_session_jsonl`**、**`_message_to_jsonl_line`**、**`_row_to_message`**、**`_serialize_tool_calls`**、**`_default_metadata`** |
| WG-21 | **`history_human_placeholder`**、**`build_human_message_for_current_turn`**、**`human_fields_for_jsonl`**、**`load_user_row_to_history_human`**、**`PROJECT_ROOT`**／**`resolve_project_image_path`** 等 |
| WG-17 | **`get_token_budget`**、**`estimate_message_tokens`**、**`message_cost`**、**`pick_consolidation_boundary`** |
| WG-18＋21 送模 | **`messages_for_model`**（含歷史剝圖；合併示範以 **`_keep_image_only_on_current_human`** 或等價邏輯） |
| WG-13 ReAct | **`run_react_turn`**、**`_stream_model_response`**（**須**支援 **`on_token`** 參數或等價 hook） |
| WG-19 | **`memory/*` helpers**、**`ensure_budget_before_react`**、**`_consolidate_pack`** 等 |
| WG-20 | **`SkillsLoader`**、**`SKILLS_LOADER`**、**`build_system_prompt`** |

**留在 `main.py` 者**：**`main()`** 迴圈、**`input`**、離開指令（**`quit`／`exit`／`q`**）、**WG-21** **`/image`**／**`pending_image`** 解析、啟動橫幅與金鑰錯誤 **`print`**、每輪 **`print("\n助手：", ...)`** 後呼叫 **`agent.chat(...)`**。

#### 禁止項（Coding Agent 必讀）

- **`agent_core.py` 內不得 `input()`**。
- **不得**引入 **Streamlit**／**Gradio** 或本題未要求之 Web 框架於必交檔。
- **不得**使用 **`AgentSession`**、**`Chat`**、**`Bot`** 等類名取代 **`Agent`**。
- **不得**為整併另建不同 **`model=`**（須與 **`chat`** 共用 **`gpt-5.4-mini`** 之 **`llm`**）。
- **不得**在 **`main.py`** 複製 **ReAct**／JSONL／整併迴圈；**單輪**只能經 **`agent.chat`**。
- **不得**刪改 **WG-21** 三層語義（JSONL 只存路徑、**`history`** 占位、本輪送模多模態）及 **`image_path` 路徑契約**（相對專案根、拒絕絕對路徑）。

#### 模型

- 與 **WG-12～21** 相同：**全程 `ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)`**；**不**另設環境變數分流。

---

### 驗收條件

- 專案根存在 **`agent_core.py`**，可 **`from agent_core import Agent`**；存在 **`main.py`** 作 **`uv run main.py`** 進入點。
- **`Agent.from_env()`** 在無 **`OPENAI_API_KEY`** 時抛出 **`RuntimeError`**；**`main.py`** 捕捉後印提示並結束（**不**崩潰 trace 即可）。
- **有金鑰**時：CLI 行為與拆前 **`references/starter_main_wg21.py`** 一致——多輪對話、**`quit`** 離開、工具呼叫、JSONL 寫入／冷啟動載回、**WG-19** 整併提示、**`/image`** 附圖與 JSONL **`image_path`**（**WG-21**）。
- **`agent.chat("…")`** 回傳本輪 assistant 最終文字；**`history`**／JSONL 在 core 內累積；關閉再開可接續。
- **`on_token`**：傳入 **`on_token=lambda s: ...`** 時，assistant 串流文字**只**進 callback、**不**再 **`print`** 同段 token（可寫最小腳本或測試說明驗證）。
- **（選修／第二入口）** 能說明：UI 殼層若遇 **`[Errno 22] Invalid argument`**，常為 core **`print`** 與宿主 stdout 衝突；**`main.py` CLI 不受影響**。
- **無** **`input()`** 出現在 **`agent_core.py`**（`grep` 或檢視）。
- 能指出：**`run_react_turn`**／**`save_session_jsonl`** 等僅在 **`agent_core.py`**，**`main.py`** 僅呼叫 **`Agent.chat`**。

---

### 藍本對應（拆前／拆後）

- **拆前起點**：**`references/starter_main_wg21.py`**（~1223 行單檔；教練僅在 **`main.py` 空白且尚未拆檔** 時可複製至專案根）。
- **拆後標準**：**`references/reference_agent_core.py`** + **`references/reference_main.py`**（本 skill 內 WG-22 驗收對照；**不**當起點覆寫）。

拆後目標結構：

```text
專案根/
  agent_core.py      # Agent + WG-12～21 全部邏輯
  main.py            # 唯一 CLI 進入點（uv run main.py）
  memory/ …          # 與 WG-19 相同
  prompts/ …
  templates/memory/MEMORY.md
  session_wiki_wg.jsonl
```

**WG-19 必備資產**（整併時讀檔；缺則 runtime 失敗）：**`prompts/memory_merge.md`**、**`templates/memory/MEMORY.md`**。教練自 **`references/project_assets/`** 部署至專案根。

**`Agent` 公開 API 與 `_stream_model_response` 簽名**：對照 **`references/reference_agent_core.py`**（含 **`on_token`** hook）；CLI 殼層對照 **`references/reference_main.py`**。
