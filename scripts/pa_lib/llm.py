"""Minimal OpenAI-compatible chat client (stdlib only).

Configuration comes from environment variables so that no endpoint or key is
ever written into the repository:

    PA_LLM_BASE_URL   e.g. http://127.0.0.1:8000/v1   (falls back to OPENAI_BASE_URL)
    PA_LLM_API_KEY    optional bearer token           (falls back to OPENAI_API_KEY)
    PA_LLM_MODEL      model name as served            (falls back to OPENAI_MODEL)
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from .common import HarnessError


@dataclass
class LLMConfig:
    base_url: str
    model: str
    api_key: str = ""
    temperature: float = 0.0
    max_tokens: int | None = None
    timeout: int = 900
    json_mode: bool = False
    extra_body: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls, **overrides: Any) -> "LLMConfig":
        base = overrides.pop("base_url", None) or os.environ.get("PA_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL", "")
        model = overrides.pop("model", None) or os.environ.get("PA_LLM_MODEL") or os.environ.get("OPENAI_MODEL", "")
        key = overrides.pop("api_key", None) or os.environ.get("PA_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
        if not base or not model:
            raise HarnessError(
                "LLM endpoint not configured: set PA_LLM_BASE_URL (…/v1) and PA_LLM_MODEL, "
                "or pass --base-url/--model. Use --dry-run to only render prompts."
            )
        return cls(base_url=base.rstrip("/"), model=model, api_key=key, **{k: v for k, v in overrides.items() if v is not None})

    def public(self) -> dict[str, Any]:
        """Config safe to store next to outputs (no key)."""
        return {"base_url_host": re.sub(r"^https?://", "", self.base_url).split("/")[0],
                "model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens,
                "json_mode": self.json_mode, "extra_body": self.extra_body}


def chat(cfg: LLMConfig, messages: list[dict[str, str]], retries: int = 3) -> tuple[str, dict[str, Any]]:
    body: dict[str, Any] = {"model": cfg.model, "messages": messages, "temperature": cfg.temperature}
    if cfg.max_tokens:
        body["max_tokens"] = cfg.max_tokens
    if cfg.json_mode:
        body["response_format"] = {"type": "json_object"}
    body.update(cfg.extra_body)
    headers = {"Content-Type": "application/json"}
    if cfg.api_key:
        headers["Authorization"] = f"Bearer {cfg.api_key}"
    data = json.dumps(body).encode("utf-8")
    url = cfg.base_url + "/chat/completions"
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=cfg.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            msg = payload["choices"][0]["message"]
            return (msg.get("content") or ""), payload.get("usage", {}) or {}
        except urllib.error.HTTPError as exc:
            last = exc
            detail = exc.read().decode("utf-8", "replace")[:300]
            if exc.code in (408, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
            raise HarnessError(f"LLM HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise HarnessError(f"unexpected LLM response shape: {exc}") from exc
    raise HarnessError(f"LLM request failed after {retries} attempts: {last}")


_THINK = re.compile(r"<think>.*?</think>", re.S | re.I)


def extract_json(content: str) -> Any:
    """Pull the first JSON object out of a model reply.

    Handles <think>…</think> blocks, an unclosed leading reasoning block that
    ends in </think>, and ```json fences.  Raises ValueError when nothing
    parseable is found.
    """
    text = _THINK.sub("", content)
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in reply")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("unbalanced JSON object in reply")
