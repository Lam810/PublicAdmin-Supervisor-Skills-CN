"""Validate annotations: schema, known codes, and verbatim evidence quotes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .common import SCHEMA_DIR, read_json, sha256_text
from .textnorm import QuoteChecker, split_paragraphs

FIELD_NAMES = [
    "empirical_phenomenon", "default_expectation", "puzzle", "research_question",
    "theoretical_target", "literature_families", "precise_gap", "core_concepts",
    "concept_neighbors", "actors", "institutional_conditions", "mechanism_chain",
    "rival_explanations", "evidence_design", "evidence_to_mechanism_map", "main_findings",
    "theoretical_move", "boundary_conditions", "normative_implication", "intro_structure",
]
PAPER_TYPES = {"mechanism", "concept", "policy-process", "reform", "applicability", "normative", "review", "mixed"}


def schema_errors(ann: Any) -> list[str]:
    """Validate against distill/schema/annotation.schema.json.

    Uses `jsonschema` when installed; otherwise a built-in check covering the
    same required structure (so the gate never silently disappears).
    """
    try:
        import jsonschema  # type: ignore
    except ModuleNotFoundError:
        return _fallback_schema_errors(ann)
    schema = read_json(SCHEMA_DIR / "annotation.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    errs = []
    for e in sorted(validator.iter_errors(ann), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        errs.append(f"{path}: {e.message[:160]}")
    return errs


def _fallback_schema_errors(ann: Any) -> list[str]:
    errs: list[str] = []
    if not isinstance(ann, dict):
        return ["(root): not an object"]
    for key in ("paper_id", "codebook_version", "paper_type", "fields", "moves"):
        if key not in ann:
            errs.append(f"(root): missing {key}")
    if ann.get("paper_type") not in PAPER_TYPES:
        errs.append(f"paper_type: invalid {ann.get('paper_type')!r}")
    fields = ann.get("fields") if isinstance(ann.get("fields"), dict) else {}
    for name in FIELD_NAMES:
        f = fields.get(name)
        if not isinstance(f, dict):
            errs.append(f"fields/{name}: missing")
            continue
        if f.get("status") not in ("present", "absent", "unclear"):
            errs.append(f"fields/{name}/status: invalid")
        if f.get("status") == "present" and (not f.get("value") or not f.get("evidence")):
            errs.append(f"fields/{name}: present requires value and evidence")
        for ev in f.get("evidence", []) or []:
            if not isinstance(ev, dict) or not ev.get("quote") or not ev.get("loc"):
                errs.append(f"fields/{name}/evidence: each item needs quote and loc")
    extra = set(fields) - set(FIELD_NAMES)
    if extra:
        errs.append(f"fields: unexpected {sorted(extra)}")
    for i, mv in enumerate(ann.get("moves", []) or []):
        if not isinstance(mv, dict) or not mv.get("code") or not mv.get("evidence"):
            errs.append(f"moves/{i}: needs code and evidence")
    return errs


@dataclass
class Verification:
    paper_id: str
    schema_errors: list[str] = field(default_factory=list)
    unknown_codes: list[str] = field(default_factory=list)
    n_quotes: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    verified_moves: list[str] = field(default_factory=list)
    unsupported_moves: list[str] = field(default_factory=list)
    verified_fields: list[str] = field(default_factory=list)
    unsupported_fields: list[str] = field(default_factory=list)
    misses: list[dict[str, str]] = field(default_factory=list)
    fulltext_sha256: str = ""

    @property
    def hit_rate(self) -> float:
        ok = self.counts.get("exact", 0) + self.counts.get("loc_mismatch", 0) + self.counts.get("fuzzy", 0)
        return ok / self.n_quotes if self.n_quotes else 0.0

    def passed(self, min_hit_rate: float) -> bool:
        return not self.schema_errors and not self.unknown_codes and self.n_quotes > 0 and self.hit_rate >= min_hit_rate

    def stamp(self, *, accept_fuzzy: bool, min_hit_rate: float, codebook_version: str, checked_at: str) -> dict[str, Any]:
        return {
            "checked_at": checked_at,
            "codebook_version": codebook_version,
            "fulltext_sha256": self.fulltext_sha256,
            "accept_fuzzy": accept_fuzzy,
            "min_hit_rate": min_hit_rate,
            "hit_rate": round(self.hit_rate, 4),
            "counts": self.counts,
            "passed": self.passed(min_hit_rate),
            "verified_moves": self.verified_moves,
            "verified_fields": self.verified_fields,
            "unsupported_moves": self.unsupported_moves,
            "unsupported_fields": self.unsupported_fields,
        }


def verify_annotation(ann: dict[str, Any], fulltext: str, known_codes: set[str], *,
                      fuzzy: float | None = None, accept_fuzzy: bool = False) -> Verification:
    v = Verification(paper_id=str(ann.get("paper_id", "")))
    v.schema_errors = schema_errors(ann)
    v.fulltext_sha256 = sha256_text(fulltext)
    checker = QuoteChecker(split_paragraphs(fulltext), fuzzy=fuzzy)
    ok_status = {"exact", "loc_mismatch"} | ({"fuzzy"} if accept_fuzzy else set())

    def run(evidence: list[dict[str, str]], where: str) -> bool:
        any_ok = False
        for ev in evidence or []:
            if not isinstance(ev, dict):
                continue
            res = checker.check(str(ev.get("quote", "")), str(ev.get("loc", "")))
            v.n_quotes += 1
            v.counts[res.status] = v.counts.get(res.status, 0) + 1
            if res.status in ok_status:
                any_ok = True
            elif res.status != "loc_mismatch":
                v.misses.append({"where": where, "status": res.status, "quote": str(ev.get("quote", ""))[:80]})
        return any_ok

    seen_codes: set[str] = set()
    for mv in ann.get("moves", []) or []:
        if not isinstance(mv, dict):
            continue
        code = str(mv.get("code", ""))
        if code not in known_codes:
            v.unknown_codes.append(code)
            continue
        if run(mv.get("evidence", []), f"move:{code}"):
            if code not in seen_codes:
                v.verified_moves.append(code)
                seen_codes.add(code)
        elif code not in seen_codes:
            v.unsupported_moves.append(code)
    fields = ann.get("fields") if isinstance(ann.get("fields"), dict) else {}
    for name in FIELD_NAMES:
        f = fields.get(name) or {}
        if isinstance(f, dict) and f.get("status") == "present":
            if run(f.get("evidence", []), f"field:{name}"):
                v.verified_fields.append(name)
            else:
                v.unsupported_fields.append(name)
    v.unsupported_moves = [c for c in v.unsupported_moves if c not in seen_codes]
    return v


def load_annotations(dirs: list[Path]) -> list[tuple[Path, dict[str, Any]]]:
    out = []
    for d in dirs:
        for p in sorted(Path(d).glob("*.json")):
            if p.name.startswith("_"):
                continue
            out.append((p, read_json(p)))
    return out
