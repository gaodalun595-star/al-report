from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import uuid
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from openai_tts import Settings, stream_tts_play
from openai_tts.settings import MAX_TTS_SPEED, MIN_TTS_SPEED

SHELL_ROOT = Path(__file__).parent
PROJECT_ROOT = SHELL_ROOT.parent
WORKSPACE_DIR = SHELL_ROOT / "workspace"
SESSION_DIR = SHELL_ROOT / "sessions"
SCRIPTS_DIR = SHELL_ROOT / "scripts"
CHAT_IMAGE_DIR = SHELL_ROOT / "uploads" / "chat_images"
AGENT_ACTIVATION_MARKER_PATH = SHELL_ROOT / ".agent_core_activated"
USER_SETTINGS_PATH = WORKSPACE_DIR / "user_settings.json"
MAX_CHAT_IMAGE_BYTES = 5 * 1024 * 1024
TTS_VOICE_OPTIONS = [
    "alloy",
    "ash",
    "ballad",
    "coral",
    "echo",
    "fable",
    "nova",
    "onyx",
    "sage",
    "shimmer",
]
TTS_VOICE_LABELS: dict[str, str] = {
    "alloy": "中性 · 音色均衡",
    "ash": "男聲 · 偏低沉、語速平穩",
    "ballad": "男聲 · 柔和、節奏偏慢",
    "coral": "女聲 · 溫暖、親切",
    "echo": "男聲 · 清晰、標準",
    "fable": "男聲 · 英式口音、適合旁白",
    "nova": "女聲 · 明亮、有活力",
    "onyx": "男聲 · 低沉、穩重",
    "sage": "女聲 · 沉穩、較內斂",
    "shimmer": "女聲 · 輕快、偏年輕",
}

load_dotenv(PROJECT_ROOT / ".env")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _tts_voice_label(voice_id: str) -> str:
    label = TTS_VOICE_LABELS.get(voice_id)
    if label:
        return f"{label}（{voice_id}）"
    return voice_id


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _ensure_workspace_dir() -> None:
    WORKSPACE_DIR.mkdir(exist_ok=True)


def _ensure_session_dir() -> None:
    SESSION_DIR.mkdir(exist_ok=True)


def _ensure_chat_image_dir() -> None:
    CHAT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def _default_tts_preferences() -> dict[str, object]:
    env = Settings()
    return {
        "tts_enabled": False,
        "tts_voice": env.voice,
        "tts_instructions": env.instructions,
        "tts_speed": float(env.speed if env.speed is not None else 1.0),
    }


def _normalize_tts_preferences(
    raw: dict[str, object],
    defaults: dict[str, object],
) -> dict[str, object]:
    voice = str(raw.get("tts_voice", defaults["tts_voice"]))
    if voice not in TTS_VOICE_OPTIONS:
        voice = str(defaults["tts_voice"])

    try:
        speed = float(raw.get("tts_speed", defaults["tts_speed"]))
    except (TypeError, ValueError):
        speed = float(defaults["tts_speed"])
    speed = max(MIN_TTS_SPEED, min(MAX_TTS_SPEED, speed))

    return {
        "tts_enabled": bool(raw.get("tts_enabled", defaults["tts_enabled"])),
        "tts_voice": voice,
        "tts_instructions": str(raw.get("tts_instructions", defaults["tts_instructions"])),
        "tts_speed": speed,
    }


def _read_user_settings() -> tuple[dict[str, object], bool]:
    defaults = _default_tts_preferences()
    if not USER_SETTINGS_PATH.exists():
        return defaults, True

    try:
        with USER_SETTINGS_PATH.open(encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return defaults, True

    if not isinstance(raw, dict):
        return defaults, True

    normalized = _normalize_tts_preferences(raw, defaults)
    return normalized, raw != normalized


def _load_user_settings() -> dict[str, object]:
    prefs, _needs_repair = _read_user_settings()
    return prefs


def _save_user_settings(settings: dict[str, object]) -> str | None:
    payload = _normalize_tts_preferences(settings, _default_tts_preferences())
    try:
        _ensure_workspace_dir()
        USER_SETTINGS_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        return f"無法寫入語音設定檔：{exc}"
    return None


def _ensure_user_settings_file() -> str | None:
    prefs, needs_repair = _read_user_settings()
    if not needs_repair:
        return None
    return _save_user_settings(prefs)


def _should_reload_tts_for_page(last_page: str | None, page_name: str) -> bool:
    return last_page != page_name


def _sync_tts_preferences_for_page(page_name: str) -> str | None:
    settings_error = _ensure_user_settings_file()
    if settings_error is not None:
        return settings_error

    persist_error = _persist_tts_preferences_if_changed()
    if persist_error is not None:
        return persist_error

    _reload_tts_preferences_from_file()
    st.session_state["_studio_tts_page_name"] = page_name
    return None


def _reload_tts_preferences_from_file() -> None:
    prefs = _load_user_settings()
    st.session_state["studio_tts_enabled"] = prefs["tts_enabled"]
    st.session_state["studio_tts_voice"] = prefs["tts_voice"]
    st.session_state["studio_tts_instructions"] = prefs["tts_instructions"]
    st.session_state["studio_tts_speed"] = prefs["tts_speed"]
    st.session_state["_studio_user_settings_snapshot"] = dict(prefs)


def _persist_tts_preferences_if_changed() -> str | None:
    required_keys = {
        "studio_tts_enabled",
        "studio_tts_voice",
        "studio_tts_instructions",
        "studio_tts_speed",
    }
    if not required_keys.issubset(st.session_state):
        return None

    current = {
        "tts_enabled": bool(st.session_state.get("studio_tts_enabled", False)),
        "tts_voice": str(st.session_state.get("studio_tts_voice", "")),
        "tts_instructions": str(st.session_state.get("studio_tts_instructions", "")),
        "tts_speed": float(st.session_state.get("studio_tts_speed", 1.0)),
    }
    normalized = _normalize_tts_preferences(current, _default_tts_preferences())
    previous = st.session_state.get("_studio_user_settings_snapshot")
    if previous is None:
        return None
    if previous == normalized:
        return None

    error = _save_user_settings(normalized)
    if error is not None:
        return error
    st.session_state["_studio_user_settings_snapshot"] = dict(normalized)
    return None


def _prepare_tts_preferences(page_name: str) -> str | None:
    return _sync_tts_preferences_for_page(page_name)


def _render_tts_settings_ui(*, settings_error: str | None = None) -> None:
    if settings_error:
        st.warning(settings_error)

    voice_options = list(TTS_VOICE_OPTIONS)
    current_voice = str(st.session_state.get("studio_tts_voice", Settings().voice))
    if current_voice not in voice_options:
        voice_options.insert(0, current_voice)

    with st.expander("語音播放", expanded=False):
        st.checkbox(
            "語音播放",
            key="studio_tts_enabled",
            help="開啟後，Agent 文字回答完成後會播放語音。",
        )
        st.selectbox(
            "聲音",
            voice_options,
            format_func=_tts_voice_label,
            key="studio_tts_voice",
            disabled=not st.session_state.get("studio_tts_enabled", False),
        )
        st.text_area(
            "語氣指示 (TTS_INSTRUCTIONS)",
            key="studio_tts_instructions",
            height=100,
            disabled=not st.session_state.get("studio_tts_enabled", False),
        )
        st.number_input(
            "語速 (TTS_SPEED)",
            min_value=MIN_TTS_SPEED,
            max_value=MAX_TTS_SPEED,
            step=0.05,
            format="%.2f",
            key="studio_tts_speed",
            disabled=not st.session_state.get("studio_tts_enabled", False),
        )
        st.caption("文字回答完成後才開始 TTS；語音錯誤不會影響文字顯示。")
        persist_error = _persist_tts_preferences_if_changed()
        if persist_error:
            st.warning(persist_error)


def studio_base_context(page_name: str = "") -> str:
    parts = [
        "這是學生的 Agent Studio Streamlit 專案。",
        f"Shell 目錄：{_display_path(SHELL_ROOT)}。",
        f"工作區：{_display_path(WORKSPACE_DIR)}（學生資料與輸出）。",
        f"腳本目錄：{_display_path(SCRIPTS_DIR)}（Agent 如需寫 Python 請放這裡）。",
        "不要修改 studio_shell/agent_panel.py 或 page_shell.py，除非學生明確要求。",
    ]
    if page_name:
        parts.append(f"目前 Streamlit 頁面：{page_name}。")
    return " ".join(parts)


def load_agent_class(project_root: Path = PROJECT_ROOT) -> tuple[type[Any] | None, str | None]:
    agent_core_path = project_root / "agent_core.py"
    if not agent_core_path.exists():
        return None, "請確認 agent_core.py 已放在專案根目錄。"

    module_name = f"_studio_shell_agent_core_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, agent_core_path)
    if spec is None or spec.loader is None:
        return None, "已找到 agent_core.py，但無法載入這個檔案。"

    inserted_path = False
    project_root_text = str(project_root)
    if project_root_text not in sys.path:
        sys.path.insert(0, project_root_text)
        inserted_path = True

    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as exc:
        return None, f"已找到 agent_core.py，但無法匯入 Agent：{exc}"
    finally:
        sys.modules.pop(module_name, None)
        if inserted_path:
            with contextlib.suppress(ValueError):
                sys.path.remove(project_root_text)

    agent_class = getattr(module, "Agent", None)
    if agent_class is None:
        return None, "已找到 agent_core.py，但檔案內沒有 Agent 類別。"
    return agent_class, None


def _clear_agent_cache() -> None:
    st.session_state.pop("studio_agent", None)
    st.session_state.pop("studio_agent_session_path", None)
    st.session_state["studio_agent_core_connected"] = False


def _write_activation_marker() -> None:
    AGENT_ACTIVATION_MARKER_PATH.write_text(
        datetime.now().isoformat(timespec="seconds"),
        encoding="utf-8",
    )


def _remove_activation_marker() -> None:
    if AGENT_ACTIVATION_MARKER_PATH.exists():
        AGENT_ACTIVATION_MARKER_PATH.unlink()


def _save_uploaded_chat_image(uploaded_file) -> tuple[str | None, str | None]:
    if uploaded_file is None:
        return None, None

    data = uploaded_file.getvalue()
    if len(data) > MAX_CHAT_IMAGE_BYTES:
        return None, "圖片超過 5 MB，請先壓縮後再上傳。"

    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        return None, "只支援 PNG、JPG、JPEG、WEBP 圖片。"

    _ensure_chat_image_dir()
    filename = f"chat_image_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}{suffix}"
    target = CHAT_IMAGE_DIR / filename
    target.write_bytes(data)
    return target.relative_to(PROJECT_ROOT).as_posix(), None


def _new_session_path() -> Path:
    _ensure_session_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shortid = uuid.uuid4().hex[:6]
    path = SESSION_DIR / f"session_{stamp}_{shortid}.jsonl"
    path.touch(exist_ok=False)
    return path


def _session_sort_time(path: Path) -> datetime:
    created_at: str | None = None
    try:
        with path.open(encoding="utf-8") as f:
            first = f.readline().strip()
        if first:
            obj = json.loads(first)
            if isinstance(obj, dict):
                created_at = obj.get("created_at")
    except (OSError, json.JSONDecodeError):
        created_at = None

    if created_at:
        try:
            return datetime.fromisoformat(created_at)
        except ValueError:
            pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def _session_label(path: Path) -> str:
    ts = _session_sort_time(path)
    shortid = path.stem.split("_")[-1]
    return f"{ts:%H:%M:%S} · 本機 · {shortid}"


def _session_relpath(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _is_valid_session_relpath(value: str) -> bool:
    if not value or not value.endswith(".jsonl"):
        return False
    if "sessions" not in Path(value).parts:
        return False
    return (PROJECT_ROOT / value).is_file()


def _resolve_session_relpath(value: str, labels: dict[str, str]) -> str | None:
    if _is_valid_session_relpath(value):
        return value
    for relpath, label in labels.items():
        if value == label:
            return relpath
    return None


def _build_session_picker_options(
    sessions: list[Path],
) -> tuple[list[str], dict[str, str]]:
    labels = {_session_relpath(path): _session_label(path) for path in sessions}
    return list(labels), labels


def _list_sessions() -> list[Path]:
    _ensure_session_dir()
    return sorted(
        SESSION_DIR.glob("session_*.jsonl"),
        key=_session_sort_time,
        reverse=True,
    )


def _extract_display_user_text(text: str) -> str:
    marker = "\n\n學生問題："
    if marker in text:
        return text.rsplit(marker, 1)[-1].strip()
    return text


def _load_session_history(path: Path) -> list[tuple[str, str]]:
    history: list[tuple[str, str]] = []
    if not path.exists():
        return history

    try:
        with path.open(encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(obj, dict) or obj.get("_type") == "metadata":
                    continue

                role = obj.get("role")
                content = str(obj.get("content", "") or "").strip()
                if role == "user" and content:
                    history.append(("user", _extract_display_user_text(content)))
                elif role == "assistant" and content:
                    history.append(("assistant", content))
    except OSError:
        return history
    return history


def _set_current_session(path: Path) -> None:
    session_path = _session_relpath(path)
    st.session_state["session_path"] = session_path
    st.session_state["studio_chat_history"] = _load_session_history(path)
    st.session_state.pop("studio_agent", None)
    st.session_state.pop("studio_agent_session_path", None)


def _ensure_valid_current_session(sessions: list[Path]) -> str | None:
    current_session = st.session_state.get("session_path")
    if current_session and _is_valid_session_relpath(current_session):
        return current_session

    st.session_state.pop("session_path", None)
    st.session_state.pop("studio_agent", None)
    st.session_state.pop("studio_agent_session_path", None)
    if sessions:
        _set_current_session(sessions[0])
        return st.session_state["session_path"]
    return None


def _reset_session_picker_widget() -> None:
    st.session_state["session_picker_version"] = (
        st.session_state.get("session_picker_version", 0) + 1
    )


def _create_agent_for_session(session_path: str) -> Any:
    agent_class, error = load_agent_class()
    if error is not None or agent_class is None:
        raise RuntimeError(error or "無法載入 Agent Core。")
    if not _is_valid_session_relpath(session_path):
        raise RuntimeError(f"對話紀錄路徑無效：{session_path!r}")
    return agent_class.from_env(session_path=session_path)


def _get_agent_for_session(session_path: str) -> Any:
    if (
        "studio_agent" not in st.session_state
        or st.session_state.get("studio_agent_session_path") != session_path
    ):
        st.session_state["studio_agent"] = _create_agent_for_session(session_path)
        st.session_state["studio_agent_session_path"] = session_path
        st.session_state["studio_agent_core_connected"] = True
    return st.session_state["studio_agent"]


def _activate_agent_core(session_path: str) -> tuple[bool, str]:
    _clear_agent_cache()
    try:
        agent = _create_agent_for_session(session_path)
    except RuntimeError as exc:
        _remove_activation_marker()
        return False, str(exc)
    except Exception as exc:
        _remove_activation_marker()
        return False, f"Agent Core 啟用失敗：{exc}"

    st.session_state["studio_agent"] = agent
    st.session_state["studio_agent_session_path"] = session_path
    st.session_state["studio_agent_core_connected"] = True
    _write_activation_marker()
    return True, "Agent Core 已連接。"


def _restore_agent_core_if_possible(session_path: str) -> tuple[bool, str | None]:
    if st.session_state.get("studio_agent_core_connected"):
        return True, None
    if not AGENT_ACTIVATION_MARKER_PATH.exists():
        return False, None
    ok, message = _activate_agent_core(session_path)
    if ok:
        return True, None
    return False, message


def render_chat_panel(*, extra_context: str = "", page_name: str = "") -> None:
    st.markdown('<div class="studio-agent-title-spacer"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="studio-agent-title-text">我的 Agent</div>',
        unsafe_allow_html=True,
    )

    sessions = _list_sessions()
    if "session_path" not in st.session_state and sessions:
        _set_current_session(sessions[0])
    current_session = _ensure_valid_current_session(sessions)

    if "studio_chat_history" not in st.session_state:
        st.session_state["studio_chat_history"] = [
            (
                "assistant",
                "請先按「啟用 Agent」。啟用後，我會讀取左欄傳來的頁面狀態，再回答你的問題。",
            )
        ]

    ids, labels = _build_session_picker_options(sessions)
    if current_session and current_session not in labels and _is_valid_session_relpath(current_session):
        ids.insert(0, current_session)
        labels[current_session] = "剛剛 · 目前對話"

    picker_key = f"session_picker_{st.session_state.get('session_picker_version', 0)}"
    selected_index = ids.index(current_session) if current_session in ids else 0

    pick_col, new_col, del_col = st.columns([6, 1, 1])
    picked_id = pick_col.selectbox(
        "對話紀錄",
        ids,
        index=selected_index,
        format_func=lambda value: labels.get(value, value),
        disabled=not ids,
        label_visibility="collapsed",
        key=picker_key,
    )
    resolved_pick = _resolve_session_relpath(picked_id, labels)
    if resolved_pick and resolved_pick != current_session:
        _set_current_session(PROJECT_ROOT / resolved_pick)
        st.rerun()
    if new_col.button("", icon=":material/add:", help="新增對話", use_container_width=True):
        _set_current_session(_new_session_path())
        _reset_session_picker_widget()
        st.rerun()
    if del_col.button(
        "",
        icon=":material/delete:",
        help="刪除對話",
        use_container_width=True,
        disabled=not current_session,
    ):
        if current_session:
            target = PROJECT_ROOT / current_session
            if target.exists():
                target.unlink()
            st.session_state.pop("session_path", None)
            st.session_state.pop("studio_chat_history", None)
            st.session_state.pop("studio_agent", None)
            st.session_state.pop("studio_agent_session_path", None)
            remaining = _list_sessions()
            if remaining:
                _set_current_session(remaining[0])
            _reset_session_picker_widget()
            st.rerun()

    settings_error = _prepare_tts_preferences(page_name)

    current_session = st.session_state.get("session_path")
    if not current_session:
        st.caption("尚無對話紀錄，請按 **+** 新增對話。")
        _render_tts_settings_ui(settings_error=settings_error)
        st.chat_input("詢問...", disabled=True, key="studio_chat_no_session")
        return

    restored, restore_error = _restore_agent_core_if_possible(current_session)
    connected = bool(st.session_state.get("studio_agent_core_connected")) or restored
    status_text = ":green[●] Agent Core：已連接" if connected else ":red[●] Agent Core：未啟用"
    st.markdown(f"**{status_text}**")
    if not connected:
        if restore_error:
            st.warning(restore_error)
        if st.button("啟用 Agent", type="primary", use_container_width=True):
            ok, message = _activate_agent_core(current_session)
            if ok:
                st.success("Agent Core 已連接。你可以開始詢問。")
                st.rerun()
            else:
                st.error(message)
        _render_tts_settings_ui(settings_error=settings_error)
        st.chat_input("請先啟用 Agent...", disabled=True, key="studio_chat_not_activated")
        return

    with st.expander("技術資訊", expanded=False):
        st.caption(f"對話紀錄檔：`{current_session}`")
        st.caption(f"語音設定檔：`{_display_path(USER_SETTINGS_PATH)}`")
        if page_name:
            st.caption(f"目前頁面：{page_name}")

    _render_tts_settings_ui(settings_error=settings_error)

    uploaded_image = st.file_uploader(
        "附加圖片（選填）",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"studio_chat_image_{current_session}",
        help="圖片只會送給下一則訊息；支援 PNG/JPG/WEBP，大小上限 5 MB。",
    )
    if uploaded_image is not None:
        st.image(uploaded_image, caption="下一則訊息會附上這張圖片", use_container_width=True)

    try:
        agent = _get_agent_for_session(current_session)
    except RuntimeError as exc:
        st.error(str(exc))
        _clear_agent_cache()
        _remove_activation_marker()
        st.chat_input("詢問 Agent...", disabled=True, key="studio_chat_no_key")
        return
    except Exception as exc:
        st.error(f"Agent Core 連線失敗：`{exc}`")
        _clear_agent_cache()
        _remove_activation_marker()
        st.chat_input("詢問 Agent...", disabled=True, key="studio_chat_connect_failed")
        return

    chat = st.container(height=460, border=False)
    with chat:
        for role, text in st.session_state["studio_chat_history"]:
            with st.chat_message(role):
                st.markdown(text)

    if user_text := st.chat_input("詢問 Agent...", key="studio_chat"):
        image_path, image_error = _save_uploaded_chat_image(uploaded_image)
        display_user_text = user_text
        if image_error:
            st.warning(image_error)
        elif image_path:
            display_user_text = f"{user_text}\n\n（已附圖：{image_path}）"

        st.session_state["studio_chat_history"].append(("user", display_user_text))
        context = studio_base_context(page_name)
        if extra_context.strip():
            context = f"{context}\n\n【目前頁面狀態】\n{extra_context.strip()}"
        prompt = f"{context}\n\n學生問題：{user_text}"

        with chat:
            with st.chat_message("user"):
                st.markdown(user_text)
                if uploaded_image is not None and image_path:
                    st.image(uploaded_image, caption="已附圖", use_container_width=True)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                answer_parts: list[str] = []
                tts_settings = (
                    replace(
                        Settings.from_env(),
                        voice=str(st.session_state["studio_tts_voice"]),
                        instructions=str(st.session_state["studio_tts_instructions"]).strip(),
                        speed=float(st.session_state["studio_tts_speed"]),
                    )
                    if st.session_state["studio_tts_enabled"]
                    else None
                )

                def on_token(token: str) -> None:
                    answer_parts.append(token)
                    placeholder.markdown("".join(answer_parts))

                try:
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                        io.StringIO()
                    ):
                        final_text = agent.chat(
                            prompt,
                            image_path=image_path,
                            on_token=on_token,
                        )
                except Exception as exc:
                    final_text = f"Agent 執行時發生錯誤：`{exc}`"
                    answer = final_text
                    placeholder.error(final_text)
                else:
                    answer = "".join(answer_parts).strip() or final_text.strip()

                st.session_state["studio_chat_history"].append(("assistant", answer))
                if st.session_state["studio_tts_enabled"] and tts_settings is not None and answer:
                    try:
                        stream_tts_play(answer, tts_settings)
                    except Exception as exc:
                        st.warning(f"語音播放發生錯誤，文字回答已保留：`{exc}`")
