from __future__ import annotations

import streamlit as st


def inject_style() -> None:
    st.markdown(
        """
<style>
    .block-container { padding-top: 2rem; }
    .studio-card {
        border: 1px solid rgba(250, 250, 250, 0.12);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        background: rgba(255, 255, 255, 0.035);
    }
    .studio-muted { color: rgba(250, 250, 250, 0.65); }
    .studio-agent-title-spacer {
        height: 0.75rem;
    }
    .studio-agent-title-text {
        font-size: 1.25rem;
        font-weight: 800;
        line-height: 1.5;
        margin-bottom: 0.55rem;
    }
</style>
""",
        unsafe_allow_html=True,
    )


def format_extra_context(page_name: str, **fields: object) -> str:
    lines = [f"【目前頁面】{page_name}"]
    for key, value in fields.items():
        lines.append(f"【{key}】{value}")
    return "\n".join(lines)
