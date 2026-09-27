"""Batch annotation of papers with an OpenAI-compatible model (or prompt rendering only)."""

from __future__ import annotations

import concurrent.futures as cf
import json
import traceback
from pathlib import Path
from typing import Any

from .common import (PROMPT_DIR, HarnessError, info, load_moves, now_iso, read_json,
                     sha256_text, warn, write_json)
from .corpus import find_fulltext, load_fulltext
from .llm import LLMConfig, chat, extract_json
from .textnorm import number_paragraphs, split_paragraphs
from .validate import schema_errors

TEMPLATE = PROMPT_DIR / "annotate_paper.md"


def render_codebook(moves: dict[str, Any], families: list[str] | None = None) -> str:
    lines = []
    for fam, meta in moves["families"].items():
        if families and fam not in families:
            continue
        lines.append(f"## {fam} {meta['label']}：{meta['question']}")
        for m in moves["moves"]:
            if m["family"] == fam:
                lines.append(f"- `{m['code']}` {m['label']}：{m['definition']}（纳入：{m['include']}；排除：{m['exclude']}）")
        lines.append("")
    return "\n".join(lines).strip()


def _template_body() -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    if text.lstrip().startswith("<!--"):
        text = text.split("-->", 1)[1].lstrip("\n")
    return text


def render_prompt(paper_id: str, numbered_text: str, moves: dict[str, Any]) -> str:
    return (_template_body()
            .replace("{{PAPER_ID}}", paper_id)
            .replace("{{CODEBOOK_VERSION}}", str(moves["version"]))
            .replace("{{CODEBOOK}}", render_codebook(moves))
            .replace("{{PAPER_TEXT}}", numbered_text))


def _repair_message(errors: list[str], unknown: list[str]) -> str:
    parts = ["你上一次的输出不符合要求，请只输出修正后的完整 JSON 对象。问题如下："]
    parts += [f"- {e}" for e in errors[:25]]
    if unknown:
        parts.append(f"- 以下编码不在编码本中，请删除或替换：{', '.join(sorted(set(unknown)))}")
    return "\n".join(parts)


def annotate_one(row: dict[str, str], out_dir: Path, cfg: LLMConfig | None, moves: dict[str, Any], *,
                 max_chars: int, allow_truncate: bool, force: bool, dry_run: bool,
                 max_attempts: int = 3, annotator_id: str = "") -> dict[str, Any]:
    pid = row["paper_id"]
    path = find_fulltext(row)
    if path is None:
        return {"paper_id": pid, "status": "no_fulltext"}
    full = load_fulltext(path)
    text_sha = sha256_text(full)
    raw = full
    truncated = False
    if len(full) > max_chars:
        if not allow_truncate:
            return {"paper_id": pid, "status": "too_long", "chars": len(full)}
        raw = full[:max_chars]
        truncated = True
    numbered = number_paragraphs(split_paragraphs(raw))
    prompt = render_prompt(pid, numbered, moves)
    prompt_sha = sha256_text(_template_body() + "\n" + str(moves["version"]))
    target = out_dir / f"{pid}.json"
    if dry_run:
        pdir = out_dir / "_prompts"
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / f"{pid}.md").write_text(prompt, encoding="utf-8")
        return {"paper_id": pid, "status": "rendered", "chars": len(prompt), "truncated": truncated}
    if target.exists() and not force:
        old = read_json(target).get("meta", {})
        if old.get("prompt_sha256") == prompt_sha and old.get("fulltext_sha256") == text_sha:
            return {"paper_id": pid, "status": "skipped_existing"}
    assert cfg is not None
    known = {m["code"] for m in moves["moves"]}
    messages = [{"role": "user", "content": prompt}]
    attempts: list[dict[str, Any]] = []
    raw_dir = out_dir / "_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    ann: Any = None
    for attempt in range(1, max_attempts + 1):
        content, usage = chat(cfg, messages)
        (raw_dir / f"{pid}.try{attempt}.txt").write_text(content, encoding="utf-8")
        try:
            ann = extract_json(content)
        except (ValueError, json.JSONDecodeError) as exc:
            errs, unknown = [f"无法解析 JSON：{exc}"], []
        else:
            errs = schema_errors(ann)
            unknown = [str(m.get("code")) for m in (ann.get("moves") or []) if isinstance(m, dict) and m.get("code") not in known] if isinstance(ann, dict) else []
        attempts.append({"attempt": attempt, "schema_errors": len(errs), "unknown_codes": len(unknown), "usage": usage})
        if not errs and not unknown:
            break
        messages += [{"role": "assistant", "content": content}, {"role": "user", "content": _repair_message(errs, unknown)}]
    else:
        return {"paper_id": pid, "status": "invalid_after_retries", "attempts": attempts}
    ann["paper_id"] = pid
    ann["meta"] = {
        "annotator": {"type": "llm", "id": annotator_id or cfg.model},
        "llm": cfg.public(),
        "prompt_sha256": prompt_sha,
        "fulltext_sha256": text_sha,
        "fulltext_file": path.name,
        "evidence_level": "E1",
        "truncated": truncated,
        "created_at": now_iso(),
        "attempts": attempts,
    }
    write_json(target, ann)
    return {"paper_id": pid, "status": "ok", "attempts": len(attempts)}


def annotate_many(rows: list[dict[str, str]], out_dir: Path, cfg: LLMConfig | None, *, workers: int,
                  max_chars: int, allow_truncate: bool, force: bool, dry_run: bool, annotator_id: str = "") -> list[dict[str, Any]]:
    moves = load_moves()
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    def job(row: dict[str, str]) -> dict[str, Any]:
        try:
            return annotate_one(row, out_dir, cfg, moves, max_chars=max_chars, allow_truncate=allow_truncate,
                                force=force, dry_run=dry_run, annotator_id=annotator_id)
        except HarnessError as exc:
            return {"paper_id": row["paper_id"], "status": "error", "error": str(exc)}
        except Exception as exc:  # keep the batch alive; record the traceback
            return {"paper_id": row["paper_id"], "status": "error", "error": repr(exc), "trace": traceback.format_exc()[-800:]}

    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for res in pool.map(job, rows):
            results.append(res)
            info(f"  {res['paper_id']}: {res['status']}" + (f" ({res.get('error')})" if res.get("error") else ""))
    log = out_dir / "_annotate_log.jsonl"
    with open(log, "a", encoding="utf-8") as fh:
        for res in results:
            fh.write(json.dumps({"at": now_iso(), **res}, ensure_ascii=False) + "\n")
    n_bad = sum(r["status"] in ("error", "invalid_after_retries") for r in results)
    if n_bad:
        warn(f"{n_bad} paper(s) failed; see {log}")
    return results
