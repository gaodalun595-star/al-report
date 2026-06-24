#!/usr/bin/env python3
"""Vans Coding Router image generation CLI (POST /v1/images)."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://ai.vanscoding.com/v1"
DEFAULT_MODEL = "openrouter@black-forest-labs/flux.2-klein-4b"
DEFAULT_EDIT_MODEL = "openrouter@openai/gpt-5.4-image-2"
DEFAULT_PRESETS: dict[str, str] = {
    "icon": "openrouter@black-forest-labs/flux.2-klein-4b",
    "ui_mockup": "openrouter@openai/gpt-5.4-image-2",
    "photo": "openrouter@bytedance-seed/seedream-4.5",
}
MODEL_REF_LIMITS: dict[str, int] = {
    "openrouter@openai/gpt-5.4-image-2": 16,
    "openrouter@openai/gpt-5-image": 16,
    "openrouter@openai/gpt-5-image-mini": 16,
    "openrouter@google/gemini-3.1-flash-image": 14,
    "openrouter@bytedance-seed/seedream-4.5": 14,
    "openrouter@black-forest-labs/flux.2-klein-4b": 4,
    "openrouter@black-forest-labs/flux.2-pro": 8,
}


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    text = raw.decode("utf-8").strip()
    if not text:
        raise ValueError(f"Prompt file is empty: {path}")
    return text


def _load_config(cwd: Path) -> dict[str, Any]:
    config_path = cwd / ".vans" / "image.json"
    if not config_path.is_file():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{config_path} must be a JSON object")
    return data


def _resolve_base_url(config: dict[str, Any]) -> str:
    for key in ("VCR_BASE_URL", "OPENAI_BASE_URL"):
        value = os.environ.get(key, "").strip()
        if value:
            return value.rstrip("/")
    cfg = config.get("base_url")
    if isinstance(cfg, str) and cfg.strip():
        return cfg.strip().rstrip("/")
    return DEFAULT_BASE_URL


def _resolve_api_key() -> str:
    value = os.environ.get("VSROUTER_API_KEY", "").strip()
    if value:
        return value
    raise ValueError(
        "Missing API key. Set VSROUTER_API_KEY (vcr_sk_... from Portal)."
    )


def _resolve_model(
    *,
    config: dict[str, Any],
    cli_model: str | None,
    preset: str | None,
    reference_paths: list[Path],
) -> str:
    if cli_model:
        return cli_model
    if reference_paths:
        edit = config.get("edit_model")
        if isinstance(edit, str) and edit.strip():
            return edit.strip()
        return DEFAULT_EDIT_MODEL
    if preset:
        models = config.get("models")
        if isinstance(models, dict):
            chosen = models.get(preset)
            if isinstance(chosen, str) and chosen.strip():
                return chosen.strip()
        fallback = DEFAULT_PRESETS.get(preset)
        if fallback:
            return fallback
        raise ValueError(f"Unknown preset: {preset}")
    env_model = os.environ.get("VCR_IMAGE_MODEL", "").strip()
    if env_model:
        return env_model
    default = config.get("default_model")
    if isinstance(default, str) and default.strip():
        return default.strip()
    return DEFAULT_MODEL


def _max_references(model: str, config: dict[str, Any]) -> int:
    cfg = config.get("max_references")
    if isinstance(cfg, int) and cfg > 0:
        return cfg
    return MODEL_REF_LIMITS.get(model, 4)


def _mime_for_path(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    if guessed in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        return guessed
    suffix = path.suffix.lower()
    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime = mapping.get(suffix)
    if not mime:
        raise ValueError(f"Unsupported image type: {path}")
    return mime


def _encode_reference(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Reference image not found: {path}")
    mime = _mime_for_path(path)
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime};base64,{b64}"},
    }


def _resolve_output_path(cwd: Path, output_path: str, config: dict[str, Any]) -> Path:
    if not output_path.strip():
        output_dir = config.get("output_dir")
        if isinstance(output_dir, str) and output_dir.strip():
            output_path = str(Path(output_dir.strip()) / "image.png")
        else:
            output_path = "assets/generated/image.png"
    target = (cwd / output_path).resolve()
    cwd_resolved = cwd.resolve()
    if cwd_resolved not in target.parents and target != cwd_resolved:
        raise ValueError(f"OutputPath must be inside project root: {cwd_resolved}")
    return target


def _parse_error_body(raw: bytes) -> str:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return raw.decode("utf-8", errors="replace")
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            parts = [str(err.get("message", ""))]
            code = err.get("code")
            if code:
                parts.append(f"code={code}")
            return " ".join(p for p in parts if p)
        detail = payload.get("detail")
        if detail:
            return str(detail)
    return json.dumps(payload, ensure_ascii=False)


def _post_images(
    url: str,
    api_key: str,
    body: dict[str, Any],
    timeout_sec: int,
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = _parse_error_body(exc.read())
        raise RuntimeError(f"HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc.reason}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected response shape from /v1/images")
    return payload


def _extract_b64(response: dict[str, Any]) -> bytes:
    data = response.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            b64 = first.get("b64_json")
            if isinstance(b64, str) and b64:
                return base64.b64decode(b64)
    raise RuntimeError("Response missing data[0].b64_json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate images via Vans Coding Router /v1/images")
    parser.add_argument("image_prompt", nargs="?", default="", help="Image prompt text")
    parser.add_argument("--prompt-file", dest="prompt_file", default="")
    parser.add_argument("--output-path", dest="output_path", default="")
    parser.add_argument("--cwd", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--preset", choices=sorted(DEFAULT_PRESETS.keys()), default="")
    parser.add_argument("--aspect-ratio", dest="aspect_ratio", default="")
    parser.add_argument("--resolution", default="")
    parser.add_argument("--reference-path", dest="reference_path", action="append", default=[])
    parser.add_argument("--reference-paths", dest="reference_paths", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout-sec", dest="timeout_sec", type=int, default=0)
    args = parser.parse_args(argv)

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd().resolve()
    config = _load_config(cwd)

    if args.prompt_file:
        prompt = _read_text(Path(args.prompt_file))
    elif args.image_prompt.strip():
        prompt = args.image_prompt.strip()
    else:
        print("error: ImagePrompt or --prompt-file is required", file=sys.stderr)
        return 2

    ref_strings: list[str] = list(args.reference_path or [])
    if args.reference_paths.strip():
        ref_strings.extend(p.strip() for p in args.reference_paths.split(",") if p.strip())
    reference_paths = [(cwd / p).resolve() for p in ref_strings]

    model = _resolve_model(
        config=config,
        cli_model=args.model.strip() or None,
        preset=args.preset.strip() or None,
        reference_paths=reference_paths,
    )
    output_file = _resolve_output_path(cwd, args.output_path, config)

    aspect_ratio = args.aspect_ratio.strip()
    if not aspect_ratio:
        cfg_ratio = config.get("aspect_ratio")
        if isinstance(cfg_ratio, str):
            aspect_ratio = cfg_ratio.strip()
    resolution = args.resolution.strip()
    if not resolution:
        cfg_res = config.get("resolution")
        if isinstance(cfg_res, str):
            resolution = cfg_res.strip()

    max_refs = _max_references(model, config)
    if len(reference_paths) > max_refs:
        print(
            f"warning: truncating references from {len(reference_paths)} to {max_refs} for {model}",
            file=sys.stderr,
        )
        reference_paths = reference_paths[:max_refs]

    body: dict[str, Any] = {"model": model, "prompt": prompt}
    if aspect_ratio:
        body["aspect_ratio"] = aspect_ratio
    if resolution:
        body["resolution"] = resolution
    if reference_paths:
        body["input_references"] = [_encode_reference(p) for p in reference_paths]

    base_url = _resolve_base_url(config)
    url = f"{base_url.rstrip('/')}/images"
    timeout = args.timeout_sec or (180 if reference_paths else 120)

    rel_output = output_file.relative_to(cwd).as_posix()
    ref_rel = [p.relative_to(cwd).as_posix() for p in reference_paths]

    if args.dry_run:
        summary = {
            "dry_run": True,
            "url": url,
            "model": model,
            "path": rel_output,
            "reference_paths": ref_rel,
            "aspect_ratio": aspect_ratio or None,
            "resolution": resolution or None,
            "prompt_chars": len(prompt),
        }
        print(json.dumps(summary, ensure_ascii=False))
        return 0

    api_key = _resolve_api_key()
    response = _post_images(url, api_key, body, timeout)
    image_bytes = _extract_b64(response)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(image_bytes)

    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    total_tokens = int(usage.get("total_tokens") or 0)
    result = {
        "path": rel_output,
        "model": model,
        "total_tokens": total_tokens,
        "reference_paths": ref_rel,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
