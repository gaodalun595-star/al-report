from __future__ import annotations

import json
from pathlib import Path

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


def page_slug(page_name: str) -> str:
    return page_name.strip().lower()


def shared_data_path(page_name: str, *, shell_root: Path) -> Path:
    return shell_root / "data" / f"{page_slug(page_name)}.json"


def load_page_data(page_name: str, *, shell_root: Path) -> dict:
    path = shared_data_path(page_name, shell_root=shell_root)
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def save_page_data(page_name: str, data: dict, *, shell_root: Path) -> None:
    path = shared_data_path(page_name, shell_root=shell_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def format_extra_context(page_name: str, **fields: object) -> str:
    """Build a pure data snapshot for user-message 【目前頁面狀態】.

    - First line is always 【目前頁面】
    - Use 左欄* prefixes for form/widget values; 共享資料檔 for absolute JSON path
    - Do not include 【任務】, 【本頁焦點】, or imperative instructions
    """
    lines = [f"【目前頁面】{page_name}"]
    for key, value in fields.items():
        lines.append(f"【{key}】{value}")
    return "\n".join(lines)
