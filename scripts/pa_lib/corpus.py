"""Corpus registry: import bibliographic exports, assign ids, split, locate full texts."""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

from .common import (ABSTRACT_DIR, FULLTEXT_DIR, PERIODS, REPO, HarnessError, read_papers,
                     warn, write_papers)
from .textnorm import normalize

# ----------------------------------------------------------------- periods & ids


def period_of(year: str) -> str:
    try:
        y = int(str(year)[:4])
    except ValueError:
        return ""
    if y <= 2009:
        return PERIODS[0]
    if y <= 2015:
        return PERIODS[1]
    if y <= 2020:
        return PERIODS[2]
    return PERIODS[3]


def assign_ids(rows: list[dict[str, str]]) -> int:
    """Give every row without a paper_id a stable id KEY-YEAR-NN. Returns #assigned."""
    used = {r["paper_id"] for r in rows if r.get("paper_id")}
    counters: dict[tuple[str, str], int] = defaultdict(int)
    for pid in used:
        m = re.fullmatch(r"([A-Z]+)-(\d{4})-(\d{2})", pid)
        if m:
            key = (m.group(1), m.group(2))
            counters[key] = max(counters[key], int(m.group(3)))
    n = 0
    for row in sorted((r for r in rows if not r.get("paper_id")), key=lambda r: (r["scholar_key"], r["year"], r["title"])):
        key = (row["scholar_key"], str(row["year"])[:4] or "0000")
        counters[key] += 1
        row["paper_id"] = f"{key[0]}-{key[1]}-{counters[key]:02d}"
        n += 1
    return n


def title_key(title: str) -> str:
    return normalize(title).replace('"', "").replace("'", "")


# ----------------------------------------------------------------- import (RIS / EndNote)

_RIS_LINE = re.compile(r"^([A-Z][A-Z0-9])  - ?(.*)$")
_ENW_LINE = re.compile(r"^%(\S)\s+(.*)$")


def parse_ris(text: str) -> list[dict[str, list[str]]]:
    recs: list[dict[str, list[str]]] = []
    cur: dict[str, list[str]] = {}
    for raw in text.splitlines():
        m = _RIS_LINE.match(raw.rstrip())
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "TY":
            cur = {}
        if tag == "ER":
            if cur:
                recs.append(cur)
            cur = {}
            continue
        cur.setdefault(tag, []).append(val)
    if cur:
        recs.append(cur)
    return recs


def parse_endnote(text: str) -> list[dict[str, list[str]]]:
    recs: list[dict[str, list[str]]] = []
    cur: dict[str, list[str]] = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if cur:
                recs.append(cur)
                cur = {}
            continue
        m = _ENW_LINE.match(line)
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "0" and cur:
            recs.append(cur)
            cur = {}
        cur.setdefault(tag, []).append(val)
    if cur:
        recs.append(cur)
    return recs


def _first(rec: dict[str, list[str]], *tags: str) -> str:
    for t in tags:
        if rec.get(t):
            return rec[t][0]
    return ""


def _authors(rec: dict[str, list[str]], *tags: str) -> str:
    names: list[str] = []
    for t in tags:
        for v in rec.get(t, []):
            names.extend(x.strip() for x in re.split(r"[;；,，]", v) if x.strip())
    return "、".join(dict.fromkeys(names))


def records_to_rows(records: list[dict[str, list[str]]], fmt: str, scholar: str, scholar_name: str) -> list[dict[str, str]]:
    rows = []
    for rec in records:
        if fmt == "ris":
            title = _first(rec, "TI", "T1")
            authors = _authors(rec, "AU", "A1")
            journal = _first(rec, "T2", "JO", "JF", "JA")
            year = _first(rec, "PY", "Y1", "DA")[:4]
            issue = _first(rec, "IS")
            sp, ep = _first(rec, "SP"), _first(rec, "EP")
            abstract = _first(rec, "AB", "N2")
        else:
            title = _first(rec, "T")
            authors = _authors(rec, "A")
            journal = _first(rec, "J", "B")
            year = _first(rec, "D")[:4]
            issue = _first(rec, "N")
            pages = _first(rec, "P")
            sp, _, ep = pages.partition("-")
            abstract = _first(rec, "X")
        if not title:
            continue
        issue = issue.lstrip("0") or issue
        names = authors.split("、") if authors else []
        role = ""
        if scholar_name and names:
            if names == [scholar_name]:
                role = "sole"
            elif names[0] == scholar_name:
                role = "first"
            elif scholar_name in names:
                role = "co"
        rows.append({
            "scholar_key": scholar, "authors": authors, "title": title, "journal": journal,
            "year": year, "issue": issue, "pages": f"{sp}-{ep}".strip("-") if sp else "",
            "author_role": role, "period": period_of(year), "verify_status": "db-export",
            "verified_fields": "title;author;journal;year;issue", "seed_source": "0",
            "_abstract": abstract,
        })
    return rows


def import_file(path: Path, fmt: str, scholar: str, scholar_name: str = "", papers_path: Path | None = None) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    records = parse_ris(text) if fmt == "ris" else parse_endnote(text)
    new_rows = records_to_rows(records, fmt, scholar, scholar_name)
    rows = read_papers(papers_path) if papers_path else read_papers()
    seen = {title_key(r["title"]) for r in rows}
    added = 0
    abstracts: list[tuple[dict[str, str], str]] = []
    for r in new_rows:
        k = title_key(r["title"])
        if k in seen:
            continue
        seen.add(k)
        abstract = r.pop("_abstract", "")
        rows.append(r)
        abstracts.append((r, abstract))
        added += 1
    assign_ids(rows)
    for r, abstract in abstracts:
        if abstract:
            ABSTRACT_DIR.mkdir(parents=True, exist_ok=True)
            (ABSTRACT_DIR / f"{r['paper_id']}.txt").write_text(abstract + "\n", encoding="utf-8")
    if papers_path:
        write_papers(rows, papers_path)
    else:
        write_papers(rows)
    return added, len(new_rows) - added


# ----------------------------------------------------------------- split


def _rank(seed: int, pid: str) -> str:
    return hashlib.sha256(f"{seed}:{pid}".encode()).hexdigest()


def assign_split(rows: list[dict[str, str]], ratio: float = 0.2, seed: int = 2026) -> Counter:
    """Sticky, deterministic, per-scholar held-out assignment.

    - rows that already have a split keep it (adding papers never reshuffles);
    - seed_source=1 rows are always train (they shaped the seed rules, so
      holding them out would leak the rules' own sources into evaluation);
    - new rows are ranked by sha256(seed:paper_id) and assigned to held-out
      while the scholar's held-out share is below `ratio`.
    """
    by_scholar: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_scholar[r["scholar_key"]].append(r)
    for scholar_rows in by_scholar.values():
        for r in scholar_rows:
            if r.get("seed_source") == "1":
                if r.get("split") == "heldout":
                    warn(f"{r['paper_id']} is a seed source but was held out; forcing train")
                r["split"] = "train"
        total = len(scholar_rows)
        target = round(total * ratio)
        held = sum(1 for r in scholar_rows if r.get("split") == "heldout")
        for r in sorted((r for r in scholar_rows if not r.get("split")), key=lambda r: _rank(seed, r["paper_id"])):
            if held < target:
                r["split"] = "heldout"
                held += 1
            else:
                r["split"] = "train"
    return Counter((r["scholar_key"], r["split"]) for r in rows)


# ----------------------------------------------------------------- full texts


def find_fulltext(row: dict[str, str]) -> Path | None:
    if row.get("fulltext"):
        p = (REPO / row["fulltext"]).resolve()
        return p if p.exists() else None
    for ext in (".txt", ".md", ".pdf"):
        p = FULLTEXT_DIR / f"{row['paper_id']}{ext}"
        if p.exists():
            return p
    return None


def load_fulltext(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except ModuleNotFoundError as exc:
            raise HarnessError(
                f"{path.name}: PDF input needs `pip install pypdf`, or convert to .txt first "
                "(e.g. pdftotext -layout in.pdf out.txt)"
            ) from exc
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8-sig", errors="replace")


def load_abstract(row: dict[str, str], fulltext: str | None) -> str:
    p = ABSTRACT_DIR / f"{row['paper_id']}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    if fulltext:
        from .textnorm import extract_abstract
        return extract_abstract(fulltext)
    return ""


def status_table(rows: list[dict[str, str]], annotated: set[str] | None = None) -> str:
    annotated = annotated or set()
    by: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by[r["scholar_key"]].append(r)
    head = "| 学者键 | 论文 | 已核验 | 部分核验 | 全文在库 | 已标注 | 训练/留出/未分 | 时期覆盖 |"
    lines = [head, "|---|---|---|---|---|---|---|---|"]
    for key in sorted(by):
        rs = by[key]
        ver = sum(r["verify_status"] in ("verified", "db-export") for r in rs)
        part = sum(r["verify_status"] == "partial" for r in rs)
        ft = sum(find_fulltext(r) is not None for r in rs)
        ann = sum(r["paper_id"] in annotated for r in rs)
        tr = sum(r["split"] == "train" for r in rs)
        ho = sum(r["split"] == "heldout" for r in rs)
        un = len(rs) - tr - ho
        periods = sorted({r["period"] for r in rs if r["period"]}, key=PERIODS.index)
        lines.append(f"| {key} | {len(rs)} | {ver} | {part} | {ft} | {ann} | {tr}/{ho}/{un} | {len(periods)}：{'、'.join(periods)} |")
    return "\n".join(lines)
