import base64
import copy
import json
import os
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    message_chunk_to_message,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


WORKSPACE = Path.cwd().resolve()
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_PATH = MEMORY_DIR / "MEMORY.md"
MEMORY_HISTORY_PATH = MEMORY_DIR / "HISTORY.md"
MEMORY_MAX_CHARS = int(os.getenv("MEMORY_MAX_CHARS", "6000"))
TOKEN_BUDGET = int(os.getenv("TOKEN_BUDGET", "200000"))
CONSOLIDATION_MAX_RETRIES = int(os.getenv("CONSOLIDATION_MAX_RETRIES", "3"))
COMPACTABLE_TOOLS = {
    "read_file",
    "exec",
    "grep",
    "glob",
    "web_search",
    "web_fetch",
    "list_dir",
}


def _runtime_env_note() -> str:
    system = platform.system()
    if system == "Windows":
        shell = "PowerShell"
        python_cmd = "uv run python path\\to\\script.py"
    else:
        shell = "system shell"
        python_cmd = "uv run python path/to/script.py"
    return (
        "【執行環境】\n"
        f"- OS: {system}\n"
        f"- Shell: {shell}\n"
        "- 下 shell 指令時只使用單行相容指令。\n\n"
        "請用uv add方式安裝模組。"
        "【exec 注意】\n"
        "- 檔案讀寫請用 read_file / write_file / edit_file / list_dir，不要用 exec 模擬 cat、echo > 或 sed -i。\n"
        f"- 多行 Python 請先用 write_file 寫成 .py，再用 exec 執行 `{python_cmd}`。\n"
        "- 不要使用 Bash heredoc（例如 <<EOF），Windows PowerShell 通常不支援。"
    )


def get_identity() -> str:
    return (
        "你是課堂練習用的 Agent。請使用繁體中文，保持簡潔、具體、可驗收。\n"
        "凡涉及計算、讀寫檔案、列目錄、修改檔案或執行指令，都必須優先使用工具，不要只用文字猜測。\n"
        "【本場次顯示名稱】Workshop Agent\n\n"
        + _runtime_env_note()
    )


def resolve_workspace_path(path: str | Path) -> Path:
    raw = Path(path)
    if raw.is_absolute():
        raise PermissionError("absolute paths are not allowed")
    target = (WORKSPACE / raw).resolve()
    try:
        target.relative_to(WORKSPACE)
    except ValueError as exc:
        raise PermissionError(f"path is outside workspace: {path}") from exc
    return target


@tool("read_file")
def read_file(path: str, offset: int = 1, limit: int = 200) -> str:
    """讀取 workspace 內 UTF-8 文字檔，回傳帶行號內容。"""
    try:
        target = resolve_workspace_path(path)
        if not target.is_file():
            return f"Error: not a file: {path}"
        lines = target.read_text(encoding="utf-8").splitlines()
        start = max(int(offset) - 1, 0)
        end = min(start + max(int(limit), 1), len(lines))
        return "\n".join(
            f"{line_no}| {line}"
            for line_no, line in enumerate(lines[start:end], start=start + 1)
        )
    except Exception as exc:
        return f"Error: {exc}"


@tool("write_file")
def write_file(path: str, content: str) -> str:
    """整檔覆寫寫入 UTF-8 文字檔（必要時建立父資料夾）。"""
    try:
        target = resolve_workspace_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"wrote {len(content)} characters to {path}"
    except Exception as exc:
        return f"Error: {exc}"


@tool("edit_file")
def edit_file(path: str, old_text: str, new_text: str, replace_all: bool = False) -> str:
    """在既有檔案中把 old_text 換成 new_text（預設僅單次替換）。"""
    try:
        target = resolve_workspace_path(path)
        if not target.is_file():
            return f"Error: not a file: {path}"
        text = target.read_text(encoding="utf-8")
        count = text.count(old_text)
        if count == 0:
            return "Error: old_text not found"
        if count > 1 and not replace_all:
            return "Error: old_text appears multiple times; add more context or set replace_all=True"
        target.write_text(
            text.replace(old_text, new_text, -1 if replace_all else 1),
            encoding="utf-8",
        )
        return f"edited {path}"
    except Exception as exc:
        return f"Error: {exc}"


@tool("list_dir")
def list_dir(path: str = ".", recursive: bool = False, max_entries: int = 200) -> str:
    """列出 workspace 內資料夾內容。"""
    try:
        root = resolve_workspace_path(path)
        if not root.is_dir():
            return f"Error: not a directory: {path}"
        iterator = root.rglob("*") if recursive else root.iterdir()
        entries = []
        for item in iterator:
            marker = "/" if item.is_dir() else ""
            entries.append(str(item.relative_to(WORKSPACE)) + marker)
            if len(entries) >= max_entries:
                entries.append("[truncated]")
                break
        return "\n".join(entries) if entries else "(empty)"
    except Exception as exc:
        return f"Error: {exc}"


@tool("exec")
def exec_workspace(command: str, timeout: int = 30) -> str:
    """在專案根目錄執行單行 shell 指令，回傳 exit code 與輸出摘要。"""
    lowered = command.lower()
    blocked = ("rm -rf", "del /f", "rmdir /s", "format", "shutdown")
    if "\n" in command or "\r" in command:
        return "Error: exec only accepts a single-line shell command"
    if any(part in lowered for part in blocked):
        return "Error: blocked dangerous command (safety limit)"

    child_env = os.environ.copy()
    child_env.setdefault("PYTHONUTF8", "1")
    child_env.setdefault("PYTHONIOENCODING", "utf-8")
    run_kw: dict[str, Any] = {
        "cwd": str(WORKSPACE),
        "shell": True,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
        "env": child_env,
    }
    if os.name == "nt":
        run_kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        result = subprocess.run(command, **run_kw)
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        if len(output) > 4000:
            output = output[:4000] + "\n\n[truncated]"
        if not output:
            output = "(no stdout or stderr; command finished with no captured output)"
        return f"exit_code={result.returncode}\n{output}"
    except Exception as exc:
        return f"Error: {exc}"


@tool("add_two")
def add_two(a: int, b: int) -> int:
    """兩個整數相加並回傳和。凡涉及兩個整數相加必須呼叫此工具，不要只在文字裡心算。"""
    return a + b


TOOLS: list[Any] = [read_file, write_file, edit_file, list_dir, exec_workspace, add_two]
_TOOL_BY_NAME: dict[str, Any] = {t.name: t for t in TOOLS}

TOOL_PARAMETERS: dict[str, dict[str, Any]] = {
    "read_file": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "offset": {"type": "integer"},
            "limit": {"type": "integer"},
        },
        "required": ["path"],
    },
    "write_file": {
        "type": "object",
        "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
        "required": ["path", "content"],
    },
    "edit_file": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"},
            "replace_all": {"type": "boolean"},
        },
        "required": ["path", "old_text", "new_text"],
    },
    "list_dir": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "recursive": {"type": "boolean"},
            "max_entries": {"type": "integer"},
        },
        "required": [],
    },
    "exec": {
        "type": "object",
        "properties": {"command": {"type": "string"}, "timeout": {"type": "integer"}},
        "required": ["command"],
    },
    "add_two": {
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
    },
}


def cast_params(params: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    out = dict(params)
    properties = schema.get("properties", {})
    for key, spec in properties.items():
        if key not in out:
            continue
        value = out[key]
        typ = spec.get("type")
        try:
            if typ == "integer" and not isinstance(value, int):
                out[key] = int(value)
            elif typ == "number" and not isinstance(value, (int, float)):
                out[key] = float(value)
            elif typ == "boolean" and not isinstance(value, bool):
                if isinstance(value, str) and value.lower() in ("true", "false"):
                    out[key] = value.lower() == "true"
            elif typ == "string" and not isinstance(value, str):
                out[key] = str(value)
        except (TypeError, ValueError):
            pass
    return out


def validate_params(params: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    properties = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in params:
            errors.append(f"missing required field: {key}")
    for key, value in params.items():
        if key not in properties:
            errors.append(f"unexpected field: {key}")
            continue
        typ = properties[key].get("type")
        if typ == "string" and not isinstance(value, str):
            errors.append(f"{key} must be string")
        elif typ == "integer" and not isinstance(value, int):
            errors.append(f"{key} must be integer")
        elif typ == "number" and not isinstance(value, (int, float)):
            errors.append(f"{key} must be number")
        elif typ == "boolean" and not isinstance(value, bool):
            errors.append(f"{key} must be boolean")
    return errors


def prepare_tool_call(name: str, raw: Any) -> tuple[Any | None, dict[str, Any], str | None]:
    tool_obj = _TOOL_BY_NAME.get(name)
    if tool_obj is None:
        return None, {}, f"unknown tool: {name}"
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None, {}, "tool arguments must be a JSON object"
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        return None, {}, "tool arguments must be a dict"
    schema = TOOL_PARAMETERS.get(name, {"type": "object", "properties": {}, "required": []})
    params = cast_params(raw, schema)
    errors = validate_params(params, schema)
    if errors:
        return None, params, "; ".join(errors)
    return tool_obj, params, None


def _default_metadata(created_at: str | None = None) -> dict[str, Any]:
    now = datetime.now().isoformat()
    return {
        "_type": "metadata",
        "key": "session",
        "created_at": created_at or now,
        "updated_at": now,
        "metadata": {},
        "last_consolidated": 0,
    }


def load_user_row_to_history_human(row: dict[str, Any]) -> HumanMessage:
    text = str(row.get("content", ""))
    image_path = row.get("image_path")
    if not image_path:
        return HumanMessage(content=text)
    media_type = row.get("media_type")
    extra = f"[此回合曾附圖，路徑：{image_path}]"
    if media_type:
        extra += f"（media_type={media_type}）"
    return HumanMessage(content=f"{text}\n\n{extra}")


def load_session_jsonl(path: str) -> tuple[list[BaseMessage], dict[str, Any] | None]:
    if not os.path.exists(path):
        return [], None

    messages: list[BaseMessage] = []
    meta: dict[str, Any] | None = None
    with open(path, encoding="utf-8") as file:
        for raw in file:
            line = raw.strip()
            if not line:
                continue
            try:
                obj: Any = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            if obj.get("_type") == "metadata":
                meta = obj
                continue
            role = obj.get("role")
            if role == "user":
                messages.append(load_user_row_to_history_human(obj))
            elif role == "assistant":
                tool_calls = obj.get("tool_calls")
                if tool_calls:
                    messages.append(AIMessage(content=str(obj.get("content", "")), tool_calls=tool_calls))
                else:
                    messages.append(AIMessage(content=str(obj.get("content", ""))))
            elif role == "tool":
                messages.append(
                    ToolMessage(
                        content=str(obj.get("content", "")),
                        tool_call_id=str(obj.get("tool_call_id") or ""),
                    )
                )
    return messages, meta


def _user_row_from_message(message: HumanMessage) -> dict[str, Any]:
    row: dict[str, Any] = {
        "role": "user",
        "content": message.content if isinstance(message.content, str) else str(message.content),
        "timestamp": datetime.now().isoformat(),
    }
    image_path = message.additional_kwargs.get("image_path")
    media_type = message.additional_kwargs.get("media_type")
    if image_path:
        row["image_path"] = image_path
        if media_type:
            row["media_type"] = media_type
    return row


def save_session_jsonl(
    path: str,
    messages: list[BaseMessage],
    existing_meta: dict[str, Any] | None,
    last_consolidated: int,
) -> dict[str, Any]:
    now = datetime.now().isoformat()
    meta = _default_metadata(created_at=now) if existing_meta is None else dict(existing_meta)
    meta["_type"] = "metadata"
    meta["key"] = meta.get("key", "session")
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["last_consolidated"] = max(0, last_consolidated)

    lines = [json.dumps(meta, ensure_ascii=False)]
    for message in messages:
        ts = datetime.now().isoformat()
        if isinstance(message, HumanMessage):
            row = _user_row_from_message(message)
        elif isinstance(message, AIMessage):
            row = {"role": "assistant", "content": message.content, "timestamp": ts}
            if getattr(message, "tool_calls", None):
                row["tool_calls"] = message.tool_calls
        elif isinstance(message, ToolMessage):
            row = {
                "role": "tool",
                "content": message.content,
                "tool_call_id": message.tool_call_id,
                "timestamp": ts,
            }
        else:
            continue
        lines.append(json.dumps(row, ensure_ascii=False))

    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    return meta


def estimate_message_tokens(message: BaseMessage) -> int:
    content = message.content
    if isinstance(content, str):
        base = len(content)
    else:
        base = len(str(content))
    tool_calls = getattr(message, "tool_calls", None)
    return base + (len(str(tool_calls)) if tool_calls else 0)


def pick_consolidation_boundary(
    messages: list[BaseMessage],
    last_consolidated: int,
    tokens_to_remove: int,
) -> tuple[int, int] | None:
    start = last_consolidated
    if start >= len(messages) or tokens_to_remove <= 0:
        return None

    removed_tokens = 0
    last_boundary: tuple[int, int] | None = None
    for idx in range(start, len(messages)):
        message = messages[idx]
        if idx > start and isinstance(message, HumanMessage):
            last_boundary = (idx, removed_tokens)
            if removed_tokens >= tokens_to_remove:
                return last_boundary
        removed_tokens += estimate_message_tokens(message)
    return last_boundary


def message_cost(messages: list[BaseMessage]) -> int:
    return sum(estimate_message_tokens(message) for message in messages)


def image_bytes_to_data_url(data: bytes, media_type: str) -> str:
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def guess_media_type(path: Path, fallback: str = "image/png") -> str:
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return fallback


def parse_user_text(raw: str) -> tuple[str, str | None, str | None]:
    if not raw.startswith("/image "):
        return raw, None, None
    parts = raw.split(maxsplit=2)
    if len(parts) < 2:
        return "", None, None
    text = parts[2] if len(parts) >= 3 else input("請輸入這張圖的問題：").strip()
    media_type = guess_media_type(Path(parts[1]))
    return text, parts[1], media_type


def build_current_human_messages(
    text: str,
    image_rel: str | None,
    media_type: str | None,
) -> tuple[HumanMessage, HumanMessage]:
    history_message = HumanMessage(content=text)
    if not image_rel:
        return history_message, history_message

    history_message = HumanMessage(
        content=text,
        additional_kwargs={"image_path": image_rel, "media_type": media_type},
    )
    try:
        full = resolve_workspace_path(image_rel)
    except Exception as exc:
        print(f"[warn] invalid image path for current turn: {exc}")
        return history_message, HumanMessage(content=text)
    if not full.is_file():
        print(f"[warn] missing image for current turn: {image_rel}")
        return history_message, HumanMessage(content=text)

    final_media_type = media_type or guess_media_type(full)
    data_url = image_bytes_to_data_url(full.read_bytes(), final_media_type)
    model_message = HumanMessage(
        content=[
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": data_url}},
        ],
        additional_kwargs={"image_path": image_rel, "media_type": final_media_type},
    )
    return history_message, model_message


def _human_to_text_only_placeholder(message: HumanMessage) -> HumanMessage:
    content = message.content
    if isinstance(content, str):
        return copy.deepcopy(message)
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        body = "\n".join(part for part in parts if part).strip() or "[此則曾含圖但無文字]"
        return HumanMessage(content=body + "\n\n[送模層已剝除歷史圖區塊]")
    return HumanMessage(content=str(content))


def messages_for_model(
    system_message: SystemMessage,
    history: list[BaseMessage],
    human_message: HumanMessage,
) -> list[BaseMessage]:
    out: list[BaseMessage] = [copy.deepcopy(system_message)]
    for message in history:
        cloned = copy.deepcopy(message)
        if isinstance(cloned, HumanMessage) and not isinstance(cloned.content, str):
            cloned = _human_to_text_only_placeholder(cloned)
        out.append(cloned)
    out.append(copy.deepcopy(human_message))
    return out


def build_messages_for_model(
    messages: list[dict[str, Any]],
    *,
    max_chars: int,
    max_tool_chars: int,
    keep_recent_tools: int,
) -> list[dict[str, Any]]:
    out = [dict(message) for message in messages]
    known_call_ids: set[str] = set()
    for message in out:
        if message.get("role") == "assistant":
            for call in message.get("tool_calls") or []:
                call_id = call.get("id")
                if call_id:
                    known_call_ids.add(str(call_id))

    out = [
        message
        for message in out
        if message.get("role") != "tool" or str(message.get("tool_call_id")) in known_call_ids
    ]

    repaired: list[dict[str, Any]] = []
    for idx, message in enumerate(out):
        repaired.append(message)
        if message.get("role") != "assistant":
            continue
        for call in message.get("tool_calls") or []:
            call_id = call.get("id")
            if not call_id:
                continue
            has_tool = any(
                later.get("role") == "tool" and later.get("tool_call_id") == call_id
                for later in out[idx + 1 :]
            )
            if not has_tool:
                name = ((call.get("function") or {}).get("name")) or call.get("name") or ""
                repaired.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": name,
                        "content": "[Tool result unavailable - call was interrupted or lost]",
                    }
                )
    out = repaired

    for message in out:
        if message.get("role") == "tool" and isinstance(message.get("content"), str):
            content = message["content"]
            if len(content) > max_tool_chars:
                message["content"] = content[:max_tool_chars] + "\n\n[truncated]"

    compactable_indexes = [
        idx
        for idx, message in enumerate(out)
        if message.get("role") == "tool" and message.get("name") in COMPACTABLE_TOOLS
    ]
    keep = set(compactable_indexes[-max(keep_recent_tools, 0) :])
    for idx in compactable_indexes:
        if idx in keep:
            continue
        content = str(out[idx].get("content", ""))
        if len(content) >= 500:
            out[idx]["content"] = f"[{out[idx].get('name')} result omitted from context]"

    def cost(rows: list[dict[str, Any]]) -> int:
        return sum(len(str(row.get("content", ""))) for row in rows)

    while cost(out) > max_chars:
        user_indexes = [idx for idx, row in enumerate(out) if row.get("role") == "user"]
        if len(user_indexes) <= 1:
            break
        start = user_indexes[0]
        end = user_indexes[1]
        del out[start:end]

    if out and out[0].get("role") != "system":
        first_system = next((idx for idx, row in enumerate(out) if row.get("role") == "system"), None)
        if first_system is not None:
            system_row = out.pop(first_system)
            out.insert(0, system_row)
    return out


def read_memory_text() -> str:
    if not MEMORY_PATH.exists():
        return ""
    text = MEMORY_PATH.read_text(encoding="utf-8").strip()
    if len(text) > MEMORY_MAX_CHARS:
        text = text[-MEMORY_MAX_CHARS:]
    return text


def memory_block_for_system() -> str:
    text = read_memory_text()
    return f"## Long-term Memory\n\n{text}" if text else ""


def append_memory_history(entry: str, failed: bool = False) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    one_line = " ".join(entry.split())
    prefix = "[CONSOLIDATION-FAILED] " if failed else ""
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {prefix}{one_line}\n"
    with open(MEMORY_HISTORY_PATH, "a", encoding="utf-8") as file:
        file.write(line)


def message_to_plain_text(message: BaseMessage) -> str:
    role = "message"
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, ToolMessage):
        role = "tool"
    return f"{role}: {message.content}"


def parse_consolidation_response(text: str) -> tuple[str, str] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    history_entry = obj.get("history_entry")
    memory_update = obj.get("memory_update")
    if not isinstance(history_entry, str) or not isinstance(memory_update, str):
        return None
    return history_entry, memory_update


def consolidate_chunk(
    llm: ChatOpenAI,
    chunk: list[BaseMessage],
    existing_memory: str,
) -> tuple[str, str] | None:
    transcript = "\n".join(message_to_plain_text(message) for message in chunk)
    prompt = (
        "請把舊對話濃縮為長期記憶更新。只回傳 JSON 物件，且只包含兩個字串鍵："
        "history_entry 與 memory_update。memory_update 必須是完整取代 MEMORY.md 的 Markdown，"
        "只保留未來仍需要的偏好、目標、決策與進度，不要抄寫逐字稿或 tool 輸出。\n\n"
        f"現有 MEMORY.md：\n{existing_memory or '(empty)'}\n\n"
        f"待整併 chunk：\n{transcript}"
    )
    for _ in range(max(CONSOLIDATION_MAX_RETRIES, 1)):
        response = llm.invoke([HumanMessage(content=prompt)])
        content = str(response.content)
        parsed = parse_consolidation_response(content)
        if parsed is not None:
            return parsed
    return None


def request_cost_chars(system_str: str, past: list[BaseMessage], human_message: HumanMessage) -> int:
    return len(system_str) + message_cost([*past, human_message])


def maybe_consolidate_memory(
    llm: ChatOpenAI,
    system_str: str,
    history: list[BaseMessage],
    human_message: HumanMessage,
    session_path: str,
    session_meta: dict[str, Any] | None,
    last_consolidated: int,
) -> tuple[dict[str, Any] | None, int]:
    target = TOKEN_BUDGET // 2
    while request_cost_chars(system_str, history[last_consolidated:], human_message) > target:
        past = history[last_consolidated:]
        if not past:
            break
        tokens_to_remove = max(0, request_cost_chars(system_str, past, human_message) - target)
        boundary = pick_consolidation_boundary(history, last_consolidated, tokens_to_remove)
        if boundary is None or boundary[0] <= last_consolidated:
            break
        chunk = history[last_consolidated : boundary[0]]
        existing_memory = read_memory_text()
        parsed = consolidate_chunk(llm, chunk, existing_memory)
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        if parsed is None:
            append_memory_history(
                f"failed to consolidate messages {last_consolidated}:{boundary[0]}",
                failed=True,
            )
        else:
            history_entry, memory_update = parsed
            append_memory_history(history_entry, failed=False)
            MEMORY_PATH.write_text(memory_update.strip() + "\n", encoding="utf-8")
        last_consolidated = boundary[0]
        session_meta = save_session_jsonl(session_path, history, session_meta, last_consolidated)
        system_str = system_content_for_model()
    return session_meta, last_consolidated


@dataclass
class SkillEntry:
    name: str
    path: Path
    source: str
    description: str
    always: bool
    body: str


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, text
    meta: dict[str, str] = {}
    for raw in lines[1:end]:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, "\n".join(lines[end + 1 :]).strip()


class SkillsLoader:
    def __init__(self, workspace: Path, builtin_skills_dir: Path) -> None:
        self.workspace_skills = workspace / "skills"
        self.builtin_skills = builtin_skills_dir

    def _entries_from_dir(self, root: Path, source: str, skip: set[str]) -> list[SkillEntry]:
        if not root.exists():
            return []
        entries: list[SkillEntry] = []
        for skill_dir in sorted(root.iterdir(), key=lambda p: p.name):
            skill_file = skill_dir / "SKILL.md"
            if not skill_dir.is_dir() or not skill_file.exists() or skill_dir.name in skip:
                continue
            text = skill_file.read_text(encoding="utf-8")
            meta, body = split_frontmatter(text)
            name = skill_dir.name
            entries.append(
                SkillEntry(
                    name=name,
                    path=skill_file,
                    source=source,
                    description=meta.get("description") or name,
                    always=meta.get("always", "false").lower() == "true",
                    body=body,
                )
            )
        return entries

    def list_skills(self) -> list[SkillEntry]:
        workspace_entries = self._entries_from_dir(self.workspace_skills, "workspace", set())
        workspace_names = {entry.name for entry in workspace_entries}
        builtin_entries = self._entries_from_dir(self.builtin_skills, "builtin", workspace_names)
        return workspace_entries + builtin_entries

    def load_skill(self, name: str) -> str | None:
        for root in (self.workspace_skills, self.builtin_skills):
            path = root / name / "SKILL.md"
            if path.exists():
                return path.read_text(encoding="utf-8")
        return None


def build_skills_summary(entries: list[SkillEntry]) -> str:
    summarized = [entry for entry in entries if not entry.always]
    if not summarized:
        return ""
    return "\n".join(
        f"- **{entry.name}** - {entry.description} `{entry.path.relative_to(WORKSPACE)}`"
        for entry in summarized
    )


def build_system_prompt(loader: SkillsLoader) -> str:
    parts = [get_identity()]
    memory = memory_block_for_system()
    if memory:
        parts.append(memory)

    entries = loader.list_skills()
    active = [entry for entry in entries if entry.always]
    if active:
        body = "\n\n---\n\n".join(f"### Skill: {entry.name}\n\n{entry.body}" for entry in active)
        parts.append("# Active Skills\n\n" + body)

    summary = build_skills_summary(entries)
    if summary:
        intro = (
            "下列技能可擴充你的能力。若要使用某技能，請用 read_file 讀取清單中該技能路徑下的 SKILL.md。\n"
            "若該技能需額外套件或環境，請先依 SKILL.md 或專案說明安裝相依項目後再操作。\n\n"
        )
        parts.append("# Skills\n\n" + intro + summary)
    return "\n\n---\n\n".join(parts)


def system_content_for_model() -> str:
    loader = SkillsLoader(WORKSPACE, WORKSPACE / "builtin_skills")
    return build_system_prompt(loader)


def run_react_turn(
    llm_tools: ChatOpenAI,
    system_message: SystemMessage,
    past: list[BaseMessage],
    history_human_message: HumanMessage,
    model_human_message: HumanMessage,
    *,
    stream_stdout: bool = True,
    on_token: Any | None = None,
) -> tuple[str, list[BaseMessage]]:
    messages = messages_for_model(system_message, past, model_human_message)
    turn_messages: list[BaseMessage] = [history_human_message]

    while True:
        acc: AIMessageChunk | None = None
        for chunk in llm_tools.stream(messages):
            acc = chunk if acc is None else acc + chunk
            if chunk.content:
                if on_token is not None:
                    on_token(str(chunk.content))
                elif stream_stdout:
                    print(chunk.content, end="", flush=True)
        if acc is None:
            raise RuntimeError("模型串流未回傳任何 chunk")
        response = message_chunk_to_message(acc)

        if response.tool_calls:
            if stream_stdout:
                print()
            messages.append(response)
            turn_messages.append(response)
            for tool_call in response.tool_calls:
                name = tool_call["name"]
                tool_obj, params, error = prepare_tool_call(name, tool_call.get("args") or {})
                if error:
                    result = f"Error: {error}"
                else:
                    try:
                        result = tool_obj.invoke(params)
                    except Exception as exc:
                        result = f"Error: {exc}"
                tool_message = ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                messages.append(tool_message)
                turn_messages.append(tool_message)
        else:
            messages.append(response)
            turn_messages.append(response)
            break

    final_ai = next((m for m in reversed(turn_messages) if isinstance(m, AIMessage)), None)
    final_text = ((final_ai.content if final_ai else None) or "").strip()
    return final_text, turn_messages


class Agent:
    """Reusable WG-22 agent core without CLI input/output ownership."""

    def __init__(
        self,
        *,
        session_path: str,
        history: list[BaseMessage],
        session_meta: dict[str, Any] | None,
        last_consolidated: int,
        llm: ChatOpenAI,
        llm_tools: Any,
    ) -> None:
        self.session_path = session_path
        self.history = history
        self.session_meta = session_meta
        self.last_consolidated = last_consolidated
        self.llm = llm
        self.llm_tools = llm_tools

    @classmethod
    def from_env(cls, *, session_path: str | None = None) -> "Agent":
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY. Add it to .env before starting the agent.")

        resolved_session_path = session_path or os.getenv("SESSION_JSONL_PATH", "session.jsonl")
        model = os.getenv("OPENAI_MODEL", "gemma4:26b")
        # base_url = os.getenv("OPENAI_BASE_URL", "http://203.71.78.31:8000/v1")

        history, session_meta = load_session_jsonl(resolved_session_path)
        last_consolidated = int((session_meta or {}).get("last_consolidated", 0) or 0)
        last_consolidated = max(0, min(last_consolidated, len(history)))

        llm_kwargs: dict[str, Any] = {
            "model": model,
            "temperature": 0.2,
            "api_key": api_key,
        }
        # if base_url:
        #     llm_kwargs["base_url"] = base_url
        llm = ChatOpenAI(**llm_kwargs)
        llm_tools = llm.bind_tools(TOOLS)

        return cls(
            session_path=resolved_session_path,
            history=history,
            session_meta=session_meta,
            last_consolidated=last_consolidated,
            llm=llm,
            llm_tools=llm_tools,
        )

    def chat(
        self,
        user_text: str,
        *,
        image_path: str | None = None,
        on_token: Any | None = None,
    ) -> str:
        media_type = guess_media_type(Path(image_path)) if image_path else None
        history_human, model_human = build_current_human_messages(
            user_text,
            image_path,
            media_type,
        )

        system_str = system_content_for_model()
        self.session_meta, self.last_consolidated = maybe_consolidate_memory(
            self.llm,
            system_str,
            self.history,
            model_human,
            self.session_path,
            self.session_meta,
            self.last_consolidated,
        )
        system_str = system_content_for_model()
        system_message = SystemMessage(content=system_str)

        past0 = self.history[self.last_consolidated:]
        cost = request_cost_chars(system_str, past0, model_human)
        if cost <= TOKEN_BUDGET:
            past = past0
        else:
            tokens_to_remove = max(0, cost - TOKEN_BUDGET // 2)
            boundary = pick_consolidation_boundary(
                self.history,
                self.last_consolidated,
                tokens_to_remove,
            )
            past = self.history[boundary[0] :] if boundary is not None else past0

        final_text, turn_messages = run_react_turn(
            self.llm_tools,
            system_message,
            past,
            history_human,
            model_human,
            stream_stdout=on_token is None,
            on_token=on_token,
        )

        self.history.extend(turn_messages)
        self.session_meta = save_session_jsonl(
            self.session_path,
            self.history,
            self.session_meta,
            self.last_consolidated,
        )
        return final_text


def get_token_budget() -> int:
    return TOKEN_BUDGET
