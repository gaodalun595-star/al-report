from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from studio_shell.agent_panel import render_chat_panel


def page_shell(
    title: str,
    caption: str,
    render_main: Callable[[], str | None],
    *,
    page_name: str = "",
) -> None:
    """Left column UI + right column Agent. render_main returns extra_context for Agent."""

    main, side = st.columns([5, 3], gap="large")

    with main:
        st.title(title)
        st.caption(caption)
        extra_context = render_main() or ""

    with side:
        render_chat_panel(extra_context=extra_context, page_name=page_name or title)
