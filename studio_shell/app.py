from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHELL_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import inject_style


st.set_page_config(page_title="Agent Studio", page_icon="🤖", layout="wide")
inject_style()


def overview() -> None:
    def render_main() -> str:
        st.markdown(
            """
### 左欄 · 你的創意 UI
- 在 `studio_shell/pages/` 設計 Streamlit 介面
- 把使用者選擇整理成 **Agent 摘要**（extra_context）
- 改左欄 → 右欄回答應跟著變

### 右欄 · 我的 Agent
- 連接專案根目錄的 `agent_core.py`
- 讀取左欄傳來的頁面狀態再回答

### 建議流程
1. 完成 `agent_core.py`
2. 在 **Home** 確認接線已通，再到 **Playground** 自己完成 extra context 接線
3. 到 **UI 元件詞彙表** 找元件名稱，練習把元件名稱放進 Prompt
4. 修改或新增 `pages/` 練習自己的 UI
"""
        )
        st.info("詳細練習題見 `docs/exercises.md`（若已安裝在專案中）。")
        return "【目前頁面】總覽\n【任務】向學生說明左欄創意、右欄 Agent 的分工。"

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
        st.Page(str(SHELL_ROOT / "pages" / "4_Food_Order_Kiosk.py"), title="餐點點餐機"),
        st.Page(str(SHELL_ROOT / "pages" / "5_Delivery_Tracking.py"), title="快遞查詢"),
        st.Page(str(SHELL_ROOT / "pages" / "6_Send_Package.py"), title="我要寄件"),
    ],
}

st.navigation(pages).run()
