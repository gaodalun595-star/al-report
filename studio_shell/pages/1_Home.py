from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SHELL_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import (
    format_extra_context,
    inject_style,
    load_page_data,
    save_page_data,
    shared_data_path,
)

PAGE_NAME = "Home"

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
inject_style()


def render_main() -> str:
    state = load_page_data(PAGE_NAME, shell_root=SHELL_ROOT)

    st.markdown("#### 輸入區")
    nickname = st.text_input(
        "我的暱稱",
        value=state.get("nickname", ""),
        placeholder="例如：小明",
    )
    goal = st.text_area(
        "今天想在左欄做什麼？",
        value=state.get("goal", ""),
        placeholder="例如：做一個心情儀表板、待辦清單、或小遊戲介面",
        height=100,
    )

    save_page_data(
        PAGE_NAME,
        {"nickname": nickname, "goal": goal},
        shell_root=SHELL_ROOT,
    )

    st.divider()
    st.markdown("#### 給 Agent 的摘要")
    extra = format_extra_context(
        PAGE_NAME,
        共享資料檔=str(shared_data_path(PAGE_NAME, shell_root=SHELL_ROOT)),
        左欄暱稱=nickname or "（未填）",
        左欄今日目標=goal or "（未填）",
    )
    st.code(extra, language="text")

    st.markdown("#### 右欄可以這樣問")
    st.markdown(
        """
- 「用暱稱跟我打招呼，兩句話就好。」
- 「根據我的今日目標，建議左欄先做哪三個 widget。」
"""
    )
    return extra


page_shell(
    "Home",
    "練習 0：左欄收集資訊，右欄 Agent 讀摘要回答。",
    render_main,
    page_name=PAGE_NAME,
)
