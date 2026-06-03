from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import inject_style

CURRENT_STATUS_INDEX = 2
DELIVERY_STEPS = ["已成立訂單", "理貨中心", "配送中", "已送達"]


st.set_page_config(page_title="快遞查詢", page_icon="📦", layout="wide")
inject_style()
st.markdown(
    """
    <style>
    .delivery-line-step {
        text-align: center;
        padding: 0.25rem 0;
    }
    .delivery-line-icon-done {
        font-size: 1.25rem;
        color: #33c481;
        font-weight: 700;
    }
    .delivery-line-icon-current {
        font-size: 1.35rem;
        color: #2f80ed;
        font-weight: 800;
    }
    .delivery-line-icon-pending {
        font-size: 1.2rem;
        color: #8a8f98;
    }
    .delivery-line-label-done {
        color: #d7dbe2;
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }
    .delivery-line-label-current {
        color: #2f80ed;
        font-size: 1rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }
    .delivery-line-label-pending {
        color: #8a8f98;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    .delivery-line-time {
        color: #9aa3af;
        font-size: 0.82rem;
        margin-top: 0.2rem;
        line-height: 1.35;
    }
    .delivery-line-location {
        color: #cbd5e1;
        font-size: 0.82rem;
        margin-top: 0.15rem;
        line-height: 1.35;
    }
    .delivery-line-connector-done {
        text-align: center;
        color: #33c481;
        font-size: 1.4rem;
        padding-top: 0.15rem;
    }
    .delivery-line-connector-pending {
        text-align: center;
        color: #6b7280;
        font-size: 1.4rem;
        padding-top: 0.15rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

COMPANY_OPTIONS = ["黑貓宅急便", "7-ELEVEN 交貨便", "新竹物流"]
STATUS_ROWS = [
    {"時間": "2026-06-03 09:10", "狀態": "已成立訂單", "地點": "台北"},
    {"時間": "2026-06-03 12:40", "狀態": "理貨中心", "地點": "桃園理貨中心"},
    {"時間": "2026-06-03 16:20", "狀態": "配送中", "地點": "新北配送站"},
]
STEP_TIMES = [
    "2026-06-03 09:10",
    "2026-06-03 12:40",
    "2026-06-03 16:20",
    "待更新",
]
STEP_LOCATIONS = [
    "台北",
    "桃園理貨中心",
    "新北配送站",
    "待更新",
]


def render_main() -> str:
    st.markdown("#### 快遞查詢")

    order_no = st.text_input("快遞單號", placeholder="例如：TW123456789", key="delivery_order_no")
    company = st.selectbox("快遞公司", COMPANY_OPTIONS, key="delivery_company")

    if "delivery_queried" not in st.session_state:
        st.session_state.delivery_queried = False

    if st.button("查詢", use_container_width=True, key="delivery_query"):
        st.session_state.delivery_queried = True

    st.divider()
    st.markdown("#### 物流狀態")

    if st.session_state.delivery_queried:
        st.markdown("#### 配送流程")
        line_cols = st.columns([2, 1, 2, 1, 2, 1, 2])

        for index, step in enumerate(DELIVERY_STEPS):
            step_col = line_cols[index * 2]
            with step_col:
                step_time = STEP_TIMES[index]
                step_location = STEP_LOCATIONS[index]
                if index < CURRENT_STATUS_INDEX:
                    st.markdown(
                        "<div class='delivery-line-step'>"
                        "<div class='delivery-line-icon-done'>●</div>"
                        f"<div class='delivery-line-label-done'>{step}</div>"
                        f"<div class='delivery-line-time'>{step_time}</div>"
                        f"<div class='delivery-line-location'>{step_location}</div>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                elif index == CURRENT_STATUS_INDEX:
                    st.markdown(
                        "<div class='delivery-line-step'>"
                        "<div class='delivery-line-icon-current'>◉</div>"
                        f"<div class='delivery-line-label-current'>{step}</div>"
                        f"<div class='delivery-line-time'>{step_time}</div>"
                        f"<div class='delivery-line-location'>{step_location}</div>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='delivery-line-step'>"
                        "<div class='delivery-line-icon-pending'>○</div>"
                        f"<div class='delivery-line-label-pending'>{step}</div>"
                        f"<div class='delivery-line-time'>{step_time}</div>"
                        f"<div class='delivery-line-location'>{step_location}</div>"
                        "</div>",
                        unsafe_allow_html=True,
                    )

            if index < len(DELIVERY_STEPS) - 1:
                connector_col = line_cols[index * 2 + 1]
                with connector_col:
                    connector_class = (
                        "delivery-line-connector-done" if index < CURRENT_STATUS_INDEX else "delivery-line-connector-pending"
                    )
                    st.markdown(
                        f"<div class='{connector_class}'>━━</div>",
                        unsafe_allow_html=True,
                    )

        st.caption("目前狀態：配送中")
        st.markdown("#### 詳細紀錄")
        st.table(STATUS_ROWS)
    else:
        st.caption("請先輸入單號並按下查詢。")

    return (
        "【目前頁面】快遞查詢\n"
        f"【快遞單號】{order_no or '（未填）'}\n"
        f"【快遞公司】{company}\n"
        f"【是否已查詢】{'是' if st.session_state.delivery_queried else '否'}"
    )


page_shell(
    "快遞查詢",
    "用假資料展示物流狀態流程。",
    render_main,
    page_name="快遞查詢",
)
