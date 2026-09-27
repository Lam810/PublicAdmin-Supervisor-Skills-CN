"""Paths, YAML/CSV loaders and small helpers shared by the harness."""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[2]
VOCAB_MOVES = REPO / "vocab" / "research-moves.yaml"
VOCAB_DEFECTS = REPO / "vocab" / "defects.yaml"
REGISTRY = REPO / "rules" / "registry.yaml"
SUPPORT = REPO / "rules" / "support.json"
PAPERS = REPO / "corpus" / "papers.csv"
FULLTEXT_DIR = REPO / "corpus" / "fulltext"
ABSTRACT_DIR = REPO / "corpus" / "abstracts"
PROMPT_DIR = REPO / "distill" / "prompts"
SCHEMA_DIR = REPO / "distill" / "schema"

PAPER_COLUMNS = [
    "paper_id", "scholar_key", "authors", "title", "journal", "year", "issue", "pages",
    "author_role", "topic", "paper_type", "period", "verify_status", "verified_fields",
    "source_url", "oa_url", "seed_source", "split", "fulltext", "notes",
]

PERIODS = ["≤2009", "2010-2015", "2016-2020", "2021-2026"]


class HarnessError(RuntimeError):
    """A user-facing error: printed without a traceback, exit code 2."""


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise HarnessError("PyYAML is required: python -m pip install -r requirements.txt") from exc
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_moves(path: Path = VOCAB_MOVES) -> dict[str, Any]:
    data = load_yaml(path)
    codes = [m["code"] for m in data["moves"]]
    dup = {c for c in codes if codes.count(c) > 1}
    if dup:
        raise HarnessError(f"duplicate move codes in {path.name}: {sorted(dup)}")
    unknown_fam = {m["code"] for m in data["moves"] if m["family"] not in data["families"]}
    if unknown_fam:
        raise HarnessError(f"moves with unknown family in {path.name}: {sorted(unknown_fam)}")
    return data


def load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    data = load_yaml(path)
    lens_ids = {lens["id"] for lens in data["lenses"]}
    ids = [r["id"] for r in data["rules"]]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise HarnessError(f"duplicate rule ids in registry: {sorted(dup)}")
    for rule in data["rules"]:
        if rule["lens"] not in lens_ids:
            raise HarnessError(f"rule {rule['id']} points to unknown lens {rule['lens']}")
        if rule["status"] not in data["statuses"]:
            raise HarnessError(f"rule {rule['id']} has unknown status {rule['status']}")
    return data


def read_papers(path: Path = PAPERS) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for col in PAPER_COLUMNS:
            row.setdefault(col, "")
    return rows


def write_papers(rows: Iterable[dict[str, str]], path: Path = PAPERS) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=PAPER_COLUMNS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in PAPER_COLUMNS})
    tmp.replace(path)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp.replace(path)


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(msg, file=sys.stderr)
