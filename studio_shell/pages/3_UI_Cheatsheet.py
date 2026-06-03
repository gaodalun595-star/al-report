from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import inject_style


st.set_page_config(page_title="UI 元件詞彙表", page_icon="🧰", layout="wide")
inject_style()


def _prompt(text: str) -> None:
    st.code(text.strip(), language="text")


def _render_widget_vocab() -> None:
    st.markdown("#### 常用元件名稱")
    st.caption("不知道怎麼跟 Agent 說時，先從這張表找元件名稱，再放進 Prompt。")
    st.table(
        [
            {"想做什麼": "輸入一行文字", "元件名稱": "text_input", "常見用途": "暱稱、姓名、標題"},
            {"想做什麼": "輸入多行文字", "元件名稱": "text_area", "常見用途": "備註、心得、故事"},
            {"想做什麼": "多選一", "元件名稱": "radio / selectbox", "常見用途": "心情、主餐、科目"},
            {"想做什麼": "多選", "元件名稱": "multiselect", "常見用途": "加點、興趣、標籤"},
            {"想做什麼": "是 / 否", "元件名稱": "checkbox", "常見用途": "不要香菜、是否完成"},
            {"想做什麼": "拖拉數值", "元件名稱": "slider", "常見用途": "能量、分數、預算"},
            {"想做什麼": "點一下觸發", "元件名稱": "button", "常見用途": "送出、重置、+1"},
            {"想做什麼": "記住狀態", "元件名稱": "st.session_state", "常見用途": "計數器、目前訂單"},
            {"想做什麼": "顯示摘要", "元件名稱": "code / json / markdown", "常見用途": "Extra Context、訂單、說明"},
            {"想做什麼": "安排版面", "元件名稱": "columns / expander / tabs", "常見用途": "左右並排、提示、分頁"},
        ]
    )


def _render_input_widgets() -> None:
    st.markdown("#### 文字與數字輸入")
    col1, col2 = st.columns(2)
    with col1:
        nickname = st.text_input("`text_input`：一行文字", value="小明", key="ui_text_input")
        note = st.text_area("`text_area`：多行文字", value="今天想練習做點餐 App。", key="ui_text_area")
    with col2:
        quantity = st.number_input("`number_input`：數字", min_value=1, max_value=10, value=2, key="ui_number")
        st.json({"text_input": nickname, "text_area": note, "number_input": quantity})

    _prompt(
        """
請在左欄新增一個 `text_input`，讓使用者輸入暱稱，並把暱稱放進 Extra Context。
"""
    )


def _render_choice_widgets() -> None:
    st.markdown("#### 選擇類元件")
    col1, col2 = st.columns(2)
    with col1:
        mood = st.radio("`radio`：少量選項，多選一", ["開心", "普通", "低落"], horizontal=True, key="ui_radio")
        main = st.selectbox("`selectbox`：下拉選單，多選一", ["牛肉麵", "雞腿飯", "滷肉飯"], key="ui_selectbox")
    with col2:
        addons = st.multiselect("`multiselect`：多選", ["蛋", "青菜", "飲料"], default=["蛋"], key="ui_multiselect")
        no_cilantro = st.checkbox("`checkbox`：是 / 否", value=True, key="ui_checkbox")
    st.json({"radio": mood, "selectbox": main, "multiselect": addons, "checkbox": no_cilantro})

    _prompt(
        """
請新增一個 `selectbox` 讓使用者選主餐，選項有牛肉麵、雞腿飯、滷肉飯。
請新增一個 `multiselect` 讓使用者選加點，選項有蛋、青菜、飲料。
請新增一個 `checkbox` 做「不要香菜」選項，並把結果放進 Extra Context。
"""
    )


def _render_value_widgets() -> None:
    st.markdown("#### 數值、日期與時間")
    col1, col2, col3 = st.columns(3)
    with col1:
        energy = st.slider("`slider`：拖拉數值", min_value=1, max_value=10, value=6, key="ui_slider")
    with col2:
        date = st.date_input("`date_input`：日期", key="ui_date")
    with col3:
        time = st.time_input("`time_input`：時間", key="ui_time")
    st.json({"slider": energy, "date_input": str(date), "time_input": str(time)})

    _prompt(
        """
請用 `slider` 做一個能量選擇器，範圍 1 到 10，並把能量放進 Extra Context。
"""
    )


def _render_state_widgets() -> None:
    st.markdown("#### 按鈕與狀態")
    if "ui_cheatsheet_count" not in st.session_state:
        st.session_state.ui_cheatsheet_count = 0

    col1, col2, col3 = st.columns([2, 1, 1])
    col1.metric("`metric`：顯示指標", st.session_state.ui_cheatsheet_count)
    if col2.button("`button` +1", use_container_width=True, key="ui_plus"):
        st.session_state.ui_cheatsheet_count += 1
        st.rerun()
    if col3.button("重置", use_container_width=True, key="ui_reset"):
        st.session_state.ui_cheatsheet_count = 0
        st.rerun()

    st.caption("按鈕點完會 rerun；要讓數字不消失，常用 `st.session_state` 記住狀態。")
    _prompt(
        """
請用 `button` 加一個「送出訂單」按鈕，並用 `st.session_state` 記住目前訂單。
"""
    )


def _render_display_widgets() -> None:
    st.markdown("#### 顯示與版面")
    tabs = st.tabs(["顯示元件", "版面元件"])

    with tabs[0]:
        st.markdown("`markdown`：顯示說明文字、標題或清單。")
        st.code("【目前頁面】點餐助手\n【主餐】牛肉麵\n【加點】蛋", language="text")
        st.json({"page": "點餐助手", "main": "牛肉麵", "addons": ["蛋"], "no_cilantro": True})
        st.success("`success`：成功訊息")
        st.warning("`warning`：提醒訊息")
        st.error("`error`：錯誤訊息")

    with tabs[1]:
        left, right = st.columns(2)
        left.info("`columns`：左右並排")
        right.info("適合把表單和摘要分開")
        with st.expander("`expander`：可展開提示"):
            st.write("適合放 Prompt 範例或進階說明。")
        st.divider()
        st.caption("`divider`：分隔不同區塊。")

    _prompt(
        """
請用 `columns` 把主餐和加點左右並排，並用 `expander` 放 Prompt 提示。
"""
    )


def render_main() -> str:
    st.markdown("#### 跟 Agent 說 UI：元件詞彙表")
    st.info(
        "這頁讓你實際玩 Streamlit UI 元件。"
        "看到想用的元件後，把它的英文名稱放進右欄 Prompt，Agent 會更容易照你的想法修改 App。"
    )

    _render_widget_vocab()
    st.divider()
    _render_input_widgets()
    st.divider()
    _render_choice_widgets()
    st.divider()
    _render_value_widgets()
    st.divider()
    _render_state_widgets()
    st.divider()
    _render_display_widgets()

    return "【目前頁面】UI 元件詞彙表\n【任務】協助學生選擇適合的 Streamlit UI 元件，並把元件名稱寫進 Prompt。"


page_shell(
    "UI 元件詞彙表",
    "先玩看看 Streamlit 元件，再把元件名稱放進 Prompt 請 Agent 修改 App。",
    render_main,
    page_name="UI 元件詞彙表",
)
