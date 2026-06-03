from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import inject_style


st.set_page_config(page_title="餐點點餐機", page_icon="🍱", layout="wide")
inject_style()


def render_main() -> str:
    st.markdown("#### 餐點點餐機")
    st.caption("這是新頁面，目前先保留空白，之後再加入點餐元件。")
    return "【目前頁面】餐點點餐機"


page_shell(
    "餐點點餐機",
    "空白頁面，之後可加入點餐 UI。",
    render_main,
    page_name="餐點點餐機",
)
