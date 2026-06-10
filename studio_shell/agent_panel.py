from __future__ import annotations

import contextlib
import io
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from openai_tts import Settings, stream_tts_play
from openai_tts.settings import MAX_TTS_SPEED, MIN_TTS_SPEED

SHELL_ROOT = Path(__file__).parent
PROJECT_ROOT = SHELL_ROOT.parent
PEAS_AGENT_HOME = Path.home() / ".peas-agent"
PEAS_WORKSPACE = PEAS_AGENT_HOME / "workspace"
SESSION_DIR = PEAS_WORKSPACE / "sessions"
SCRIPTS_DIR = SHELL_ROOT / "scripts"
CHAT_IMAGE_DIR = PEAS_WORKSPACE / "uploads" / "chat_images"
TTS_CONFIG_PATH = PEAS_AGENT_HOME / "tts.json"
MIGRATION_MARKER_PATH = PEAS_AGENT_HOME / ".studio_migration_done"
LEGACY_USER_SETTINGS_PATH = SHELL_ROOT / "workspace" / "user_settings.json"
LEGACY_SESSION_DIR = SHELL_ROOT / "sessions"
AGENT_ACTIVATION_MARKER_PATH = SHELL_ROOT / ".agent_core_activated"
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


def _tts_voice_label(voice_id: str) -> str:
    label = TTS_VOICE_LABELS.get(voice_id)
    if label:
        return f"{label}（{voice_id}）"
    return voice_id


def _display_path(path: Path) -> str:
    return path.resolve().as_posix()


def _ensure_peas_dirs() -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    CHAT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def _default_tts_config() -> dict[str, object]:
    return {
        "api_key": "",
        "base_url": "",
        "enabled": False,
        "voice": "nova",
        "instructions": "用台灣繁體中文說話。",
        "speed": 1.0,
    }


def _normalize_tts_config(
    raw: dict[str, object],
    defaults: dict[str, object],
) -> dict[str, object]:
    voice = str(raw.get("voice", raw.get("tts_voice", defaults["voice"])))
    if voice not in TTS_VOICE_OPTIONS:
        voice = str(defaults["voice"])

    try:
        speed = float(raw.get("speed", raw.get("tts_speed", defaults["speed"])))
    except (TypeError, ValueError):
        speed = float(defaults["speed"])
    speed = max(MIN_TTS_SPEED, min(MAX_TTS_SPEED, speed))

    enabled = raw.get("enabled", raw.get("tts_enabled", defaults["enabled"]))
    instructions = raw.get("instructions", raw.get("tts_instructions", defaults["instructions"]))

    return {
        "api_key": str(raw.get("api_key", defaults["api_key"])),
        "base_url": str(raw.get("base_url", defaults["base_url"])),
        "enabled": bool(enabled),
        "voice": voice,
        "instructions": str(instructions),
        "speed": speed,
    }


def _read_tts_config() -> tuple[dict[str, object], bool]:
    defaults = _default_tts_config()
    if not TTS_CONFIG_PATH.exists():
        return defaults, True

    try:
        with TTS_CONFIG_PATH.open(encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return defaults, True

    if not isinstance(raw, dict):
        return defaults, True

    normalized = _normalize_tts_config(raw, defaults)
    return normalized, raw != normalized


def _load_tts_config() -> dict[str, object]:
    prefs, _needs_repair = _read_tts_config()
    return prefs


def _save_tts_config(settings: dict[str, object]) -> str | None:
    payload = _normalize_tts_config(settings, _default_tts_config())
    try:
        TTS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        TTS_CONFIG_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        return f"無法寫入語音設定檔：{exc}"
    return None


def _ensure_tts_config_file() -> str | None:
    prefs, needs_repair = _read_tts_config()
    if not needs_repair:
        return None
    return _save_tts_config(prefs)


def _tts_widgets_from_config(config: dict[str, object]) -> dict[str, object]:
    return {
        "studio_tts_enabled": config["enabled"],
        "studio_tts_voice": config["voice"],
        "studio_tts_instructions": config["instructions"],
        "studio_tts_speed": config["speed"],
    }


def _config_from_tts_widgets() -> dict[str, object]:
    current = _load_tts_config()
    return {
        "api_key": current.get("api_key", ""),
        "base_url": current.get("base_url", ""),
        "enabled": bool(st.session_state.get("studio_tts_enabled", False)),
        "voice": str(st.session_state.get("studio_tts_voice", "")),
        "instructions": str(st.session_state.get("studio_tts_instructions", "")),
        "speed": float(st.session_state.get("studio_tts_speed", 1.0)),
    }


def _should_reload_tts_for_page(last_page: str | None, page_name: str) -> bool:
    return last_page != page_name


def _sync_tts_preferences_for_page(page_name: str) -> str | None:
    settings_error = _ensure_tts_config_file()
    if settings_error is not None:
        return settings_error

    persist_error = _persist_tts_preferences_if_changed()
    if persist_error is not None:
        return persist_error

    _reload_tts_preferences_from_file()
    st.session_state["_studio_tts_page_name"] = page_name
    return None


def _reload_tts_preferences_from_file() -> None:
    prefs = _load_tts_config()
    widgets = _tts_widgets_from_config(prefs)
    for key, value in widgets.items():
        st.session_state[key] = value
    st.session_state["_studio_tts_snapshot"] = dict(prefs)


def _persist_tts_preferences_if_changed() -> str | None:
    required_keys = {
        "studio_tts_enabled",
        "studio_tts_voice",
        "studio_tts_instructions",
        "studio_tts_speed",
    }
    if not required_keys.issubset(st.session_state):
        return None

    normalized = _normalize_tts_config(
        _config_from_tts_widgets(),
        _default_tts_config(),
    )
    previous = st.session_state.get("_studio_tts_snapshot")
    if previous is None:
        return None
    if previous == normalized:
        return None

    error = _save_tts_config(normalized)
    if error is not None:
        return error
    st.session_state["_studio_tts_snapshot"] = dict(normalized)
    return None


def _prepare_tts_preferences(page_name: str) -> str | None:
    return _sync_tts_preferences_for_page(page_name)


def _build_tts_settings_for_playback() -> Settings | None:
    if not st.session_state.get("studio_tts_enabled", False):
        return None
    cfg = _load_tts_config()
    api_key = str(cfg.get("api_key", "")).strip()
    if not api_key:
        return None
    return Settings(
        api_key=api_key,
        voice=str(st.session_state["studio_tts_voice"]),
        instructions=str(st.session_state["studio_tts_instructions"]).strip(),
        speed=float(st.session_state["studio_tts_speed"]),
    )


def _render_tts_settings_ui(*, settings_error: str | None = None) -> None:
    if settings_error:
        st.warning(settings_error)

    voice_options = list(TTS_VOICE_OPTIONS)
    current_voice = str(st.session_state.get("studio_tts_voice", "nova"))
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
            "語氣指示",
            key="studio_tts_instructions",
            height=100,
            disabled=not st.session_state.get("studio_tts_enabled", False),
        )
        st.number_input(
            "語速",
            min_value=MIN_TTS_SPEED,
            max_value=MAX_TTS_SPEED,
            step=0.05,
            format="%.2f",
            key="studio_tts_speed",
            disabled=not st.session_state.get("studio_tts_enabled", False),
        )
        st.caption(
            f"TTS 設定檔：`{TTS_CONFIG_PATH}`（含 api_key）。"
            "文字回答完成後才開始 TTS；語音錯誤不會影響文字顯示。"
        )
        persist_error = _persist_tts_preferences_if_changed()
        if persist_error:
            st.warning(persist_error)


def _maybe_migrate_legacy_data() -> str | None:
    if MIGRATION_MARKER_PATH.exists():
        return None

    messages: list[str] = []
    _ensure_peas_dirs()

    if not TTS_CONFIG_PATH.exists() and LEGACY_USER_SETTINGS_PATH.is_file():
        try:
            raw = json.loads(LEGACY_USER_SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                migrated = _normalize_tts_config(raw, _default_tts_config())
                _save_tts_config(migrated)
                messages.append("已將舊語音設定遷移至 ~/.peas-agent/tts.json。")
        except (OSError, json.JSONDecodeError):
            pass

    if LEGACY_SESSION_DIR.is_dir():
        legacy_sessions = sorted(LEGACY_SESSION_DIR.glob("session_*.jsonl"))
        moved = 0
        for src in legacy_sessions:
            dest = SESSION_DIR / src.name
            if dest.exists():
                continue
            try:
                shutil.copy2(src, dest)
                moved += 1
            except OSError:
                continue
        if moved:
            messages.append(
                f"已將 {moved} 個舊對話紀錄遷移至 ~/.peas-agent/workspace/sessions/。"
            )

    try:
        MIGRATION_MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
        MIGRATION_MARKER_PATH.write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")
    except OSError:
        return None

    return " ".join(messages) if messages else None


def studio_base_context() -> str:
    return "\n".join([
        "使用者身份、名稱、角色、偏好以 system prompt 中的 USER.md 為準；【目前頁面狀態】與【左欄暱稱】只代表左欄表單快照，不得取代 USER.md 身份。",
        f"Streamlit 專案根目錄：{_display_path(PROJECT_ROOT)}",
        f"左欄 UI 程式：{_display_path(SHELL_ROOT / 'pages')}（每頁一個檔案）",
        "左欄各頁以 `render_main()` 收集 widget 狀態，用 `format_extra_context()` 組成 extra context 並 return；"
        "`page_shell` 會在使用者送訊息時附上【目前頁面狀態】。",
        "extra context 以本次 render 的 widget 值為準，不可假設讀檔一定等同目前畫面；禁止在 extra context 寫【任務】或指令語氣。",
        f"共享狀態檔目錄：{_display_path(SHELL_ROOT / 'data')}（與 pages 同層）。",
        "檔名慣例：`{page_slug}.json`（page_slug = 頁面名稱小寫，Playground → playground.json）。",
        "讀寫 Studio 共享 JSON 時，`read_file`/`write_file`/`edit_file` 必須使用【共享資料檔】或上述目錄的完整絕對路徑。",
        "勿用 `studio_shell/data/...` 相對路徑（相對路徑會解析到 ~/.peas-agent/workspace，找不到專案檔）。",
        "左欄 `render_main()` 從該檔讀取初始值餵 widget。",
        "左欄程式讀寫 JSON 用 `load_page_data()` / `save_page_data()`（`shell_ui.py`）；Agent 不可呼叫這兩個 helper。",
        "Agent 要改左欄狀態時：先 `read_file`【共享資料檔】，再用 `edit_file`/`write_file` 更新同一 JSON；勿直接改 Streamlit widget。",
        "有共享檔的頁面，extra context 應含【共享資料檔】完整路徑（可用 `shared_data_path()`）。",
        f"內建 JSON 模板目錄：{_display_path(SHELL_ROOT / 'data')}。",
        "內建欄位：home.json → nickname(str), goal(str)；playground.json → nickname, mood(str), energy(int 1-10), event(str), count(int)。",
        "Agent 寫入時須保留既有鍵名與型別，只改目標欄位；新頁面建立 JSON 時，鍵名須與該頁 `save_page_data({...})` 一致，可複製同目錄既有模板再改。",
        "使用者新增 page 時：建立 `pages/N_xxx.py` + `data/{page_slug}.json` 模板（含初始鍵值），左欄 load/save 與 extra context 欄位對齊。",
        "參考範例：`pages/1_Home.py`、`data/home.json`；`pages/2_Playground.py`、`data/playground.json`。",
    ])


def _clear_agent_cache() -> None:
    st.session_state.pop("studio_agent", None)
    st.session_state.pop("studio_agent_session_name", None)
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

    _ensure_peas_dirs()
    filename = f"chat_image_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}{suffix}"
    target = CHAT_IMAGE_DIR / filename
    target.write_bytes(data)
    return target.relative_to(PEAS_WORKSPACE).as_posix(), None


def _new_session_path() -> Path:
    _ensure_peas_dirs()
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


def _session_name(path: Path) -> str:
    return path.name


def _is_valid_session_name(value: str) -> bool:
    if not value or not value.endswith(".jsonl"):
        return False
    if value != Path(value).name or ".." in value:
        return False
    return (SESSION_DIR / value).is_file()


def _coerce_session_name(value: str) -> str | None:
    if _is_valid_session_name(value):
        return value
    candidate = Path(value).name
    if _is_valid_session_name(candidate):
        return candidate
    return None


def _resolve_session_picker_value(value: str, labels: dict[str, str]) -> str | None:
    coerced = _coerce_session_name(value)
    if coerced:
        return coerced
    for session_name, label in labels.items():
        if value == label:
            return session_name
    return None


def _build_session_picker_options(
    sessions: list[Path],
) -> tuple[list[str], dict[str, str]]:
    labels = {_session_name(path): _session_label(path) for path in sessions}
    return list(labels), labels


def _list_sessions() -> list[Path]:
    _ensure_peas_dirs()
    return sorted(
        SESSION_DIR.glob("session_*.jsonl"),
        key=_session_sort_time,
        reverse=True,
    )


def _extract_display_user_text(text: str) -> str:
    marker = "\n\n使用者問題："
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
    session_name = _session_name(path)
    st.session_state["session_name"] = session_name
    st.session_state.pop("session_path", None)
    st.session_state["studio_chat_history"] = _load_session_history(path)
    st.session_state.pop("studio_agent", None)
    st.session_state.pop("studio_agent_session_name", None)


def _ensure_valid_current_session(sessions: list[Path]) -> str | None:
    current = st.session_state.get("session_name")
    if not current:
        legacy = st.session_state.get("session_path")
        if legacy:
            current = _coerce_session_name(str(legacy))
            if current:
                st.session_state["session_name"] = current
                st.session_state.pop("session_path", None)

    if current and _is_valid_session_name(current):
        return current

    st.session_state.pop("session_name", None)
    st.session_state.pop("session_path", None)
    st.session_state.pop("studio_agent", None)
    st.session_state.pop("studio_agent_session_name", None)
    if sessions:
        _set_current_session(sessions[0])
        return st.session_state["session_name"]
    return None


def _reset_session_picker_widget() -> None:
    st.session_state["session_picker_version"] = (
        st.session_state.get("session_picker_version", 0) + 1
    )


def _create_agent_for_session(session_name: str) -> Any:
    if not _is_valid_session_name(session_name):
        raise RuntimeError(f"對話紀錄無效：{session_name!r}")
    try:
        from peas_agent import Agent
    except ImportError as exc:
        raise RuntimeError(
            "找不到 peas-agent-core。請執行 add-studio-shell 安裝依賴，"
            "或手動 uv add peas-agent-core。"
        ) from exc
    return Agent.create(
        session_name=session_name,
        host_context=studio_base_context(),
    )


def _get_agent_for_session(session_name: str) -> Any:
    if (
        "studio_agent" not in st.session_state
        or st.session_state.get("studio_agent_session_name") != session_name
    ):
        st.session_state["studio_agent"] = _create_agent_for_session(session_name)
        st.session_state["studio_agent_session_name"] = session_name
        st.session_state["studio_agent_core_connected"] = True
    return st.session_state["studio_agent"]


def _activate_agent_core(session_name: str) -> tuple[bool, str]:
    _clear_agent_cache()
    try:
        agent = _create_agent_for_session(session_name)
    except RuntimeError as exc:
        _remove_activation_marker()
        return False, str(exc)
    except Exception as exc:
        _remove_activation_marker()
        return False, f"Agent Core 啟用失敗：{exc}"

    st.session_state["studio_agent"] = agent
    st.session_state["studio_agent_session_name"] = session_name
    st.session_state["studio_agent_core_connected"] = True
    _write_activation_marker()
    return True, "Agent Core 已連接。"


def _restore_agent_core_if_possible(session_name: str) -> tuple[bool, str | None]:
    if st.session_state.get("studio_agent_core_connected"):
        return True, None
    if not AGENT_ACTIVATION_MARKER_PATH.exists():
        return False, None
    ok, message = _activate_agent_core(session_name)
    if ok:
        return True, None
    return False, message


def render_chat_panel(*, extra_context: str = "", page_name: str = "") -> None:
    migration_message = _maybe_migrate_legacy_data()
    if migration_message:
        st.info(migration_message)

    st.markdown('<div class="studio-agent-title-spacer"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="studio-agent-title-text">我的 Agent</div>',
        unsafe_allow_html=True,
    )

    sessions = _list_sessions()
    if "session_name" not in st.session_state and "session_path" not in st.session_state and sessions:
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
    if current_session and current_session not in labels and _is_valid_session_name(current_session):
        ids.insert(0, current_session)
        labels[current_session] = "剛剛 · 目前對話"

    pick_col, new_col, del_col = st.columns([6, 1, 1])
    if ids:
        picker_key = f"session_picker_{st.session_state.get('session_picker_version', 0)}"
        selected_index = ids.index(current_session) if current_session in ids else 0
        picked_id = pick_col.selectbox(
            "對話紀錄",
            ids,
            index=selected_index,
            format_func=lambda value: labels.get(value, value),
            label_visibility="collapsed",
            key=picker_key,
        )
        resolved_pick = _resolve_session_picker_value(picked_id, labels)
        if resolved_pick and resolved_pick != current_session:
            _set_current_session(SESSION_DIR / resolved_pick)
            st.rerun()
    else:
        pick_col.caption("尚無對話紀錄")
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
            target = SESSION_DIR / current_session
            if target.exists():
                target.unlink()
            st.session_state.pop("session_name", None)
            st.session_state.pop("session_path", None)
            st.session_state.pop("studio_chat_history", None)
            st.session_state.pop("studio_agent", None)
            st.session_state.pop("studio_agent_session_name", None)
            remaining = _list_sessions()
            if remaining:
                _set_current_session(remaining[0])
            else:
                _clear_agent_cache()
                _remove_activation_marker()
            _reset_session_picker_widget()
            st.rerun()

    settings_error = _prepare_tts_preferences(page_name)

    current_session = st.session_state.get("session_name")
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
        st.caption(f"對話紀錄檔：{SESSION_DIR / current_session}")
        st.caption(f"語音設定檔：{TTS_CONFIG_PATH}")
        st.caption(f"LLM 設定檔：{PEAS_AGENT_HOME / 'config.json'}")
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
        if extra_context.strip():
            prompt = f"【目前頁面狀態】\n{extra_context.strip()}\n\n使用者問題：{user_text}"
        else:
            prompt = f"使用者問題：{user_text}"

        with chat:
            with st.chat_message("user"):
                st.markdown(user_text)
                if uploaded_image is not None and image_path:
                    st.image(uploaded_image, caption="已附圖", use_container_width=True)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                answer_parts: list[str] = []
                tts_settings = _build_tts_settings_for_playback()
                if st.session_state.get("studio_tts_enabled") and tts_settings is None:
                    cfg = _load_tts_config()
                    if not str(cfg.get("api_key", "")).strip():
                        st.warning("語音已開啟，但 ~/.peas-agent/tts.json 尚未設定 api_key。")

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
                if tts_settings is not None and answer:
                    try:
                        stream_tts_play(answer, tts_settings)
                    except Exception as exc:
                        st.warning(f"語音播放發生錯誤，文字回答已保留：`{exc}`")
                st.rerun()
