from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHELL_ROOT = Path(__file__).resolve().parent
PAGES_ROOT = SHELL_ROOT / "pages"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import format_extra_context, inject_style


st.set_page_config(page_title="Agent Studio", page_icon="🤖", layout="wide")
inject_style()

with st.sidebar:
    st.markdown("### 頁面檔案")
    page_files = sorted(p.name for p in PAGES_ROOT.glob("*.py"))
    for file_name in page_files:
        st.text(file_name)


def overview() -> None:
    def render_main() -> str:
        st.markdown(
            """
### 左欄 · 你的創意 UI
- 在 `studio_shell/pages/` 設計 Streamlit 介面
- 把使用者選擇整理成 **Agent 摘要**（extra_context）
- 改左欄 → 右欄回答應跟著變

### 右欄 · 我的 Agent
- 連接 `peas-agent-core`（設定在 `~/.peas-agent/config.json`）
- 讀取左欄傳來的頁面狀態再回答

### 建議流程
1. 設定 `~/.peas-agent/config.json`（LLM api_key）與 `tts.json`（語音，選填）
2. 在 **Home** 與 **Playground** 體驗 extra context 與共享 JSON 雙向互動
3. 到 **UI 元件詞彙表** 找元件名稱，練習把元件名稱放進 Prompt
4. 修改或新增 `pages/` 練習自己的 UI
"""
        )
        st.info("詳細練習題見 `docs/exercises.md`（若已安裝在專案中）。")
        return format_extra_context("總覽")

    page_shell(
        "Agent Studio",
        "左欄發揮創意，右欄連接你的 Agent。",
        render_main,
        page_name="總覽",
    )


pages = {
    "Studio": [
        st.Page(overview, title="總覽", default=True),
        st.Page(str(SHELL_ROOT / "pages" / "1_Home.py"), title="Home"),
        st.Page(str(SHELL_ROOT / "pages" / "2_Playground.py"), title="Playground"),
        st.Page(str(SHELL_ROOT / "pages" / "3_UI_Cheatsheet.py"), title="UI 元件詞彙表"),
        st.Page(str(SHELL_ROOT / "pages" / "4_Food_Order_Kiosk.py"), title="點餐機"),
        st.Page(str(SHELL_ROOT / "pages" / "5_Delivery_Tracking.py"), title="配送追蹤"),
        st.Page(str(SHELL_ROOT / "pages" / "6_Send_Package.py"), title="我要寄件"),
        st.Page(str(SHELL_ROOT / "pages" / "7_來寄件吧.py"), title="來寄件吧"),
    ],
}

st.navigation(pages).run()
