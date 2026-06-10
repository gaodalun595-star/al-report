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

PAGE_NAME = "Playground"

st.set_page_config(page_title="Playground", page_icon="🎛️", layout="wide")
inject_style()

MOOD_OPTIONS = ["😀 開心", "😐 普通", "😢 低落"]


def render_main() -> str:
    state = load_page_data(PAGE_NAME, shell_root=SHELL_ROOT)

    st.markdown("#### 練習 1 · 心情儀表板")

    col1, col2 = st.columns(2)
    with col1:
        nickname = st.text_input(
            "暱稱",
            value=state.get("nickname", ""),
            placeholder="例如：小明",
        )
    with col2:
        mood_default = state.get("mood", MOOD_OPTIONS[1])
        mood_index = MOOD_OPTIONS.index(mood_default) if mood_default in MOOD_OPTIONS else 1
        mood = st.radio("今天心情", MOOD_OPTIONS, index=mood_index, horizontal=True)

    energy = st.slider(
        "能量",
        min_value=1,
        max_value=10,
        value=int(state.get("energy", 5)),
    )
    event = st.text_area(
        "今天發生一件事（一句話）",
        value=state.get("event", ""),
        placeholder="例如：段考結束了",
    )

    count = int(state.get("count", 0))

    st.divider()
    st.markdown("#### 計數器（AI coding 小練習）")

    metric_col, btn_col = st.columns([2, 1])
    metric_col.metric("Count", count)
    if btn_col.button("+1", use_container_width=True):
        count += 1

    st.caption("試著請 Agent 在 `pages/2_Playground.py` 加一個「-1」按鈕。")

    save_page_data(
        PAGE_NAME,
        {
            "nickname": nickname,
            "mood": mood,
            "energy": energy,
            "event": event,
            "count": count,
        },
        shell_root=SHELL_ROOT,
    )

    st.divider()
    st.markdown("#### 練習 2 · 請 Agent 透過共享 JSON 改左欄")
    st.info(
        "右欄 Agent 已能讀【目前頁面狀態】，也能寫入 `data/playground.json` 更新左欄。"
        "試著說：「請把心情改成 😀 開心」→ chat 完左欄應自動更新。"
    )

    st.markdown("#### 給 Agent 的摘要")
    extra = format_extra_context(
        PAGE_NAME,
        共享資料檔=str(shared_data_path(PAGE_NAME, shell_root=SHELL_ROOT)),
        左欄暱稱=nickname or "（未填）",
        左欄心情=mood,
        左欄能量=f"{energy}/10",
        左欄今日事件=event or "（未填）",
        左欄計數器=count,
    )
    st.code(extra, language="text")

    st.markdown("#### 右欄可以這樣問")
    st.markdown(
        """
- 「根據我的心情和能量，給我三個今晚可以放鬆的建議。」
- 「請把心情改成 😀 開心。」
- 「用鼓勵的語氣寫一段 50 字給我，不要說教。」

**驗收：** 改心情或能量 → 用同一句話問右欄 → 回答應跟著變；請 Agent 改心情 → 左欄 radio 應更新。
"""
    )
    return extra


page_shell(
    "Playground",
    "已接線 extra context 與共享 JSON；練習讀取快照與 Agent 改左欄。",
    render_main,
    page_name=PAGE_NAME,
)
