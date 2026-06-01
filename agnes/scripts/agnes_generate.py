#!/usr/bin/env python3
"""Generate images or videos with the Agnes API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1").rstrip("/")
KEY_ENV = "AGNES_API_KEY"


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def parse_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def parse_params(values: list[str] | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for item in values or []:
        if "=" not in item:
            fail(f"--param must be key=value, got {item!r}")
        key, raw = item.split("=", 1)
        key = key.strip()
        if not key:
            fail("--param key cannot be empty")
        params[key] = parse_value(raw)
    return params


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    key = os.environ.get(KEY_ENV)
    if not key:
        fail(f"{KEY_ENV} is not set")

    body = None
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(f"{BASE_URL}{path}", data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fail(f"HTTP {exc.code} from Agnes: {detail}")
    except urllib.error.URLError as exc:
        fail(f"Could not reach Agnes API: {exc.reason}")


def add_optional(payload: dict[str, Any], args: argparse.Namespace, names: list[str]) -> None:
    for name in names:
        value = getattr(args, name, None)
        if value is not None:
            payload[name] = value


def slug(text: str, limit: int = 48) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip()).strip("-")
    return (cleaned[:limit] or "agnes-output").lower()


def collect_urls(obj: Any) -> list[str]:
    urls: list[str] = []
    if isinstance(obj, dict):
        for _key, value in obj.items():
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                urls.append(value)
            else:
                urls.extend(collect_urls(value))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(collect_urls(item))
    return urls


def collect_b64_images(obj: Any) -> list[str]:
    values: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and key.lower() in {"b64_json", "base64", "image_base64"}:
                values.append(value)
            else:
                values.extend(collect_b64_images(value))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(collect_b64_images(item))
    return values


def extension_from_url(url: str, fallback: str) -> str:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix and len(suffix) <= 8:
        return suffix
    return fallback


def download(url: str, out_path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "codex-agnes-skill/1.0"})
    with urllib.request.urlopen(req, timeout=300) as response:
        out_path.write_bytes(response.read())


def save_media(response: dict[str, Any], download_dir: str | None, stem: str) -> list[str]:
    if not download_dir:
        return []
    out_dir = Path(download_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []

    for index, url in enumerate(dict.fromkeys(collect_urls(response)), start=1):
        ext = extension_from_url(url, ".bin")
        out_path = out_dir / f"{slug(stem)}-{index}{ext}"
        download(url, out_path)
        saved.append(str(out_path))

    for index, b64_value in enumerate(collect_b64_images(response), start=1):
        out_path = out_dir / f"{slug(stem)}-b64-{index}.png"
        out_path.write_bytes(base64.b64decode(b64_value))
        saved.append(str(out_path))

    return saved


def print_result(response: dict[str, Any], saved: list[str] | None = None) -> None:
    result = {"response": response}
    if saved:
        result["saved"] = saved
    print(json.dumps(result, ensure_ascii=False, indent=2))


def chat(args: argparse.Namespace) -> None:
    messages: list[dict[str, str]] = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.prompt})
    payload: dict[str, Any] = {"model": args.model, "messages": messages}
    add_optional(payload, args, ["temperature", "max_tokens"])
    payload.update(parse_params(args.param))
    response = request_json("POST", "/chat/completions", payload)
    print_result(response)


def image(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {"model": args.model, "prompt": args.prompt}
    add_optional(payload, args, ["size", "quality", "seed", "n", "response_format"])
    if args.image_url:
        payload["image"] = args.image_url if len(args.image_url) > 1 else args.image_url[0]
    payload.update(parse_params(args.param))
    response = request_json("POST", "/images/generations", payload)
    saved = save_media(response, args.download_dir, args.stem or args.prompt)
    print_result(response, saved)


def extract_video_id(response: dict[str, Any]) -> str | None:
    for key in ("id", "task_id", "video_id"):
        value = response.get(key)
        if isinstance(value, str):
            return value
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("id", "task_id", "video_id"):
            value = data.get(key)
            if isinstance(value, str):
                return value
    return None


def status_is_done(response: dict[str, Any]) -> bool:
    status = str(response.get("status") or response.get("state") or "").lower()
    return status in {"succeeded", "success", "completed", "complete", "done", "failed", "error", "cancelled"}


def video_create(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {"model": args.model, "prompt": args.prompt}
    add_optional(payload, args, ["seconds", "width", "height", "fps", "seed"])
    if args.image_url:
        payload["image"] = args.image_url if len(args.image_url) > 1 else args.image_url[0]
    payload.update(parse_params(args.param))
    response = request_json("POST", "/videos", payload)

    if args.poll:
        video_id = extract_video_id(response)
        if not video_id:
            fail("could not find a video task id in the create response")
        response = poll_video(video_id, args.poll_interval, args.timeout)

    saved = save_media(response, args.download_dir, args.stem or args.prompt)
    print_result(response, saved)


def video_get(args: argparse.Namespace) -> None:
    response = request_json("GET", f"/videos/{urllib.parse.quote(args.video_id)}")
    saved = save_media(response, args.download_dir, args.stem or args.video_id)
    print_result(response, saved)


def poll_video(video_id: str, interval: float, timeout: float) -> dict[str, Any]:
    start = time.monotonic()
    last: dict[str, Any] = {}
    while time.monotonic() - start <= timeout:
        last = request_json("GET", f"/videos/{urllib.parse.quote(video_id)}")
        if status_is_done(last) or collect_urls(last):
            return last
        time.sleep(interval)
    fail(f"timed out waiting for video {video_id}; last response: {json.dumps(last, ensure_ascii=False)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate images or videos with Agnes.")
    sub = parser.add_subparsers(dest="command", required=True)

    chat_parser = sub.add_parser("chat", help="Call chat completions.")
    chat_parser.add_argument("--prompt", required=True)
    chat_parser.add_argument("--model", default="agnes-2.0-flash")
    chat_parser.add_argument("--system")
    chat_parser.add_argument("--temperature", type=float)
    chat_parser.add_argument("--max-tokens", dest="max_tokens", type=int)
    chat_parser.add_argument("--param", action="append", help="Extra JSON field as key=value.")
    chat_parser.set_defaults(func=chat)

    img = sub.add_parser("image", help="Create an image.")
    img.add_argument("--prompt", required=True)
    img.add_argument("--model", default="agnes-image-2.0-flash")
    img.add_argument("--size")
    img.add_argument("--quality")
    img.add_argument("--seed", type=int)
    img.add_argument("--n", type=int)
    img.add_argument("--response-format", dest="response_format")
    img.add_argument("--image-url", action="append")
    img.add_argument("--param", action="append", help="Extra JSON field as key=value.")
    img.add_argument("--download-dir")
    img.add_argument("--stem")
    img.set_defaults(func=image)

    create = sub.add_parser("video-create", help="Create a video task.")
    create.add_argument("--prompt", required=True)
    create.add_argument("--model", default="agnes-video-v2.0")
    create.add_argument("--image-url", action="append")
    create.add_argument("--seconds")
    create.add_argument("--width", type=int)
    create.add_argument("--height", type=int)
    create.add_argument("--fps", type=int)
    create.add_argument("--seed", type=int)
    create.add_argument("--param", action="append", help="Extra JSON field as key=value.")
    create.add_argument("--poll", action="store_true")
    create.add_argument("--poll-interval", type=float, default=10.0)
    create.add_argument("--timeout", type=float, default=900.0)
    create.add_argument("--download-dir")
    create.add_argument("--stem")
    create.set_defaults(func=video_create)

    get = sub.add_parser("video-get", help="Fetch a video task by id.")
    get.add_argument("video_id")
    get.add_argument("--download-dir")
    get.add_argument("--stem")
    get.set_defaults(func=video_get)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
