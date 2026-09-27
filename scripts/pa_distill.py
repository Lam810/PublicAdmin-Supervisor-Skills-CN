#!/usr/bin/env python3
"""Scholar-to-skill distillation harness for PublicAdmin-Supervisor-Skills-CN.

Pipeline (see distill/README.md):

    import / split / status      build and inspect the corpus registry (corpus/papers.csv)
    annotate                     per-paper structural annotation with an OpenAI-compatible model
    validate                     schema + codebook + verbatim-quote verification (anti-fabrication gate)
    agree                        inter-annotator agreement (Cohen's kappa per move family)
    aggregate                    rule support on the train split -> rules/support.json + report
    mine                         frequent move combinations as hints for new rules
    holdout                      Task A: held-out structure prediction, rules vs baselines
    blind-pack / blind-score     Task B: blind revision-utility rating
    comments                     Route B: supervisor-comment distillation report

Exit codes: 0 ok, 1 a gate failed (--strict), 2 usage / configuration error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pa_lib import __version__  # noqa: E402
from pa_lib.common import (PAPERS, REPO, SUPPORT, HarnessError, info, load_moves,  # noqa: E402
                           load_registry, now_iso, read_papers, write_json, write_papers)


def _select(rows, ids: str | None, scholar: str | None, split: str | None):
    out = rows
    if ids:
        wanted = {x.strip() for x in ids.split(",") if x.strip()}
        out = [r for r in out if r["paper_id"] in wanted]
    if scholar:
        out = [r for r in out if r["scholar_key"] == scholar]
    if split:
        out = [r for r in out if r["split"] == split]
    return out


def cmd_import(a) -> int:
    from pa_lib.corpus import import_file
    added, dup = import_file(Path(a.file), a.format, a.scholar, a.scholar_name or "")
    info(f"imported {added} new record(s); {dup} duplicate title(s) skipped -> {PAPERS.relative_to(REPO)}")
    return 0


def cmd_split(a) -> int:
    from pa_lib.corpus import assign_ids, assign_split
    rows = read_papers()
    assign_ids(rows)
    counts = assign_split(rows, ratio=a.ratio, seed=a.seed)
    write_papers(rows)
    for (key, split), n in sorted(counts.items()):
        info(f"  {key:5s} {split:8s} {n}")
    return 0


def cmd_status(a) -> int:
    from pa_lib.corpus import status_table
    annotated = set()
    for d in a.annotations or []:
        annotated |= {p.stem for p in Path(d).glob("*.json") if not p.name.startswith("_")}
    print(status_table(read_papers(), annotated))
    return 0


def cmd_annotate(a) -> int:
    from pa_lib.annotate import annotate_many
    from pa_lib.llm import LLMConfig
    rows = _select(read_papers(), a.ids, a.scholar, a.split)
    if not rows:
        raise HarnessError("no papers selected")
    cfg = None
    if not a.dry_run:
        extra = json.loads(a.extra_body) if a.extra_body else {}
        cfg = LLMConfig.from_env(base_url=a.base_url, model=a.model, temperature=a.temperature,
                                 max_tokens=a.max_tokens, json_mode=a.json_mode, extra_body=extra)
    res = annotate_many(rows, Path(a.out), cfg, workers=a.workers, max_chars=a.max_chars,
                        allow_truncate=a.allow_truncate, force=a.force, dry_run=a.dry_run,
                        annotator_id=a.annotator_id or "")
    bad = [r for r in res if r["status"] in ("error", "invalid_after_retries", "too_long")]
    missing = [r for r in res if r["status"] == "no_fulltext"]
    info(f"done: {len(res)} selected, {len(bad)} failed, {len(missing)} without full text")
    return 1 if (a.strict and bad) else 0


def cmd_validate(a) -> int:
    from pa_lib.corpus import find_fulltext, load_fulltext
    from pa_lib.validate import load_annotations, verify_annotation
    moves = load_moves()
    known = {m["code"] for m in moves["moves"]}
    rows = {r["paper_id"]: r for r in read_papers()}
    stamp_time = now_iso()
    table = []
    failed = 0
    for path, ann in load_annotations([Path(d) for d in a.dirs]):
        pid = str(ann.get("paper_id", path.stem))
        row = rows.get(pid)
        ft = find_fulltext(row) if row else None
        if ft is None:
            table.append((pid, "NO-TEXT", "", "", ""))
            failed += 1
            continue
        v = verify_annotation(ann, load_fulltext(ft), known, fuzzy=a.fuzzy, accept_fuzzy=a.accept_fuzzy)
        ok = v.passed(a.min_hit_rate)
        failed += not ok
        table.append((pid, "PASS" if ok else "FAIL", f"{v.hit_rate:.0%} of {v.n_quotes}",
                      f"moves {len(v.verified_moves)}/{len(v.verified_moves) + len(v.unsupported_moves)}",
                      "; ".join(filter(None, [f"schema:{len(v.schema_errors)}" if v.schema_errors else "",
                                              f"unknown:{','.join(v.unknown_codes)}" if v.unknown_codes else "",
                                              f"misses:{len(v.misses)}" if v.misses else ""]))))
        if a.verbose:
            for e in v.schema_errors[:10]:
                print(f"    schema  {e}")
            for m in v.misses[:10]:
                print(f"    {m['status']:10s} {m['where']}: {m['quote']}")
        if a.write:
            ann.setdefault("meta", {})["verification"] = v.stamp(
                accept_fuzzy=a.accept_fuzzy, min_hit_rate=a.min_hit_rate,
                codebook_version=str(moves["version"]), checked_at=stamp_time)
            write_json(path, ann)
    print("| paper | result | quote hit rate | verified moves | notes |\n|---|---|---|---|---|")
    for row in table:
        print("| " + " | ".join(row) + " |")
    info(f"{len(table) - failed}/{len(table)} passed (min hit rate {a.min_hit_rate:.0%})")
    return 1 if (a.strict and failed) else 0


def cmd_agree(a) -> int:
    from pa_lib.stats import cohen_kappa
    from pa_lib.validate import load_annotations
    moves = load_moves()
    fam_of = {m["code"]: m["family"] for m in moves["moves"]}

    def codes(ann):
        ver = (ann.get("meta") or {}).get("verification")
        if ver:
            return set(ver.get("verified_moves", []))
        return {m.get("code") for m in ann.get("moves", []) if isinstance(m, dict)}

    A = {str(x.get("paper_id")): codes(x) for _, x in load_annotations([Path(a.dir_a)])}
    B = {str(x.get("paper_id")): codes(x) for _, x in load_annotations([Path(a.dir_b)])}
    common = sorted(set(A) & set(B))
    if not common:
        raise HarnessError("no paper annotated in both directories")
    print(f"papers in common: {len(common)}\n\n| family | kappa | positives A/B | flag |\n|---|---|---|---|")
    low = 0
    for fam in moves["families"]:
        fam_codes = [c for c, f in fam_of.items() if f == fam]
        pairs = [(c in A[p], c in B[p]) for p in common for c in fam_codes]
        k = cohen_kappa(pairs)
        pa = sum(x for x, _ in pairs)
        pb = sum(y for _, y in pairs)
        flag = "LOW (<0.6): revise codebook definitions before counting" if k == k and k < 0.6 else ""
        low += bool(flag)
        print(f"| {fam} | {k:.3f} | {pa}/{pb} | {flag} |")
    return 1 if (a.strict and low) else 0


def cmd_aggregate(a) -> int:
    from pa_lib.aggregate import compute_support, load_records, support_report
    registry = load_registry()
    records, problems = load_records([Path(d) for d in a.dirs], read_papers(), require_verified=not a.allow_unverified)
    for p in problems:
        info(f"  [skip] {p}")
    sup = compute_support(records, registry, allow_unsplit=a.allow_unsplit)
    if a.allow_unverified or a.allow_unsplit:
        sup["contaminated"] = {"allow_unverified": a.allow_unverified, "allow_unsplit": a.allow_unsplit}
    out = Path(a.out)
    write_json(out, sup)
    report = Path(a.report)
    report.write_text(support_report(sup), encoding="utf-8")
    passed = [rid for rid, e in sup["rules"].items() if e["pass"]]
    info(f"{sup['n_train']} train annotations; {len(passed)} rule(s) pass admission -> {out.name}, {report.name}")
    return 0


def cmd_mine(a) -> int:
    from pa_lib.aggregate import load_records, mine_itemsets
    records, problems = load_records([Path(d) for d in a.dirs], read_papers())
    for p in problems:
        info(f"  [skip] {p}")
    print(mine_itemsets(records, load_registry(), top=a.top))
    return 0


def cmd_holdout(a) -> int:
    from pa_lib.holdout import VARIANTS, run_holdout
    from pa_lib.llm import LLMConfig
    variants = [v.strip() for v in a.variants.split(",") if v.strip()]
    bad = set(variants) - set(VARIANTS)
    if bad:
        raise HarnessError(f"unknown variant(s) {sorted(bad)}; choose from {VARIANTS}")
    cfg = None
    if not a.dry_run:
        extra = json.loads(a.extra_body) if a.extra_body else {}
        cfg = LLMConfig.from_env(base_url=a.base_url, model=a.model, extra_body=extra)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = run_holdout([Path(d) for d in a.dirs], read_papers(), load_registry(), cfg, variants, out,
                          n_boot=a.boot, seed=a.seed, dry_run=a.dry_run)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_blind_pack(a) -> int:
    from pa_lib.blind import pack
    print(json.dumps(pack(Path(a.items), Path(a.out), a.raters, a.seed), ensure_ascii=False, indent=2))
    return 0


def cmd_blind_score(a) -> int:
    from pa_lib.blind import score
    res = score(Path(a.dir), a.baseline, a.margin, a.boot, a.seed, a.fab_margin)
    print((Path(a.dir) / "blind_report.md").read_text(encoding="utf-8"))
    return 0 if res else 1


def cmd_comments(a) -> int:
    from pa_lib.aggregate import aggregate_comments
    print(aggregate_comments(Path(a.file), a.min_comments, a.min_drafts))
    return 0


def _llm_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--base-url", help="OpenAI-compatible base URL ending in /v1 (default: $PA_LLM_BASE_URL)")
    p.add_argument("--model", help="model name (default: $PA_LLM_MODEL)")
    p.add_argument("--extra-body", help='JSON merged into the request, e.g. \'{"chat_template_kwargs":{"enable_thinking":false}}\'')


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pa_distill.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("import", help="import a CNKI/Wanfang/Google Scholar export (RIS or EndNote)")
    p.add_argument("file")
    p.add_argument("--format", choices=["ris", "endnote"], required=True)
    p.add_argument("--scholar", required=True, help="scholar key, e.g. ZXG")
    p.add_argument("--scholar-name", help="scholar's Chinese name, used to infer author_role")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("split", help="assign ids and a sticky per-scholar train/held-out split")
    p.add_argument("--ratio", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=2026)
    p.set_defaults(func=cmd_split)

    p = sub.add_parser("status", help="corpus coverage table")
    p.add_argument("--annotations", nargs="*", help="annotation dirs to count")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("annotate", help="annotate papers (or --dry-run to render prompts only)")
    p.add_argument("--out", required=True, help="output dir, e.g. corpus/annotations/qwen-run1")
    p.add_argument("--ids", help="comma-separated paper ids")
    p.add_argument("--scholar")
    p.add_argument("--split", choices=["train", "heldout"])
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--max-chars", type=int, default=60000)
    p.add_argument("--allow-truncate", action="store_true", help="truncate over-long texts instead of failing (recorded in meta)")
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--strict", action="store_true", help="exit 1 if any paper failed")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int)
    p.add_argument("--json-mode", action="store_true", help="send response_format=json_object")
    p.add_argument("--annotator-id", help="label stored in meta (default: model name)")
    _llm_args(p)
    p.set_defaults(func=cmd_annotate)

    p = sub.add_parser("validate", help="schema + codebook + verbatim quote checks")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--write", action="store_true", help="store the verification stamp in each annotation")
    p.add_argument("--strict", action="store_true", help="exit 1 if any annotation fails")
    p.add_argument("--min-hit-rate", type=float, default=0.9)
    p.add_argument("--fuzzy", type=float, help="report near-matches at this ratio (e.g. 0.92)")
    p.add_argument("--accept-fuzzy", action="store_true", help="count fuzzy matches as verified (not recommended)")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("agree", help="inter-annotator agreement between two annotation dirs")
    p.add_argument("dir_a")
    p.add_argument("dir_b")
    p.add_argument("--strict", action="store_true")
    p.set_defaults(func=cmd_agree)

    p = sub.add_parser("aggregate", help="rule support on the train split")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--out", default=str(SUPPORT))
    p.add_argument("--report", default=str(REPO / "rules" / "support-report.md"))
    p.add_argument("--allow-unverified", action="store_true", help="count unverified annotations (output is stamped as contaminated)")
    p.add_argument("--allow-unsplit", action="store_true", help="treat papers without a split as train (stamped as contaminated)")
    p.set_defaults(func=cmd_aggregate)

    p = sub.add_parser("mine", help="frequent move combinations per tradition")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--top", type=int, default=30)
    p.set_defaults(func=cmd_mine)

    p = sub.add_parser("holdout", help="Task A: held-out structure prediction")
    p.add_argument("dirs", nargs="+")
    p.add_argument("--variants", default="baseline,rules,rules_named")
    p.add_argument("--out", default=str(REPO / "eval" / "results" / "holdout"))
    p.add_argument("--boot", type=int, default=5000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--dry-run", action="store_true")
    _llm_args(p)
    p.set_defaults(func=cmd_holdout)

    p = sub.add_parser("blind-pack", help="Task B: build blind rating packets")
    p.add_argument("items", help="JSONL with item_id, draft, outputs{system: text}")
    p.add_argument("--out", required=True)
    p.add_argument("--raters", type=int, default=3)
    p.add_argument("--seed", type=int, default=7)
    p.set_defaults(func=cmd_blind_pack)

    p = sub.add_parser("blind-score", help="Task B: unblind and score")
    p.add_argument("dir")
    p.add_argument("--baseline", required=True)
    p.add_argument("--margin", type=float, default=0.5, help="non-inferiority margin on the harm dimensions D7/D8 (1-5 scale)")
    p.add_argument("--fab-margin", type=float, default=0.05, help="non-inferiority margin on the fabrication rate (proportion)")
    p.add_argument("--boot", type=int, default=5000)
    p.add_argument("--seed", type=int, default=0)
    p.set_defaults(func=cmd_blind_score)

    p = sub.add_parser("comments", help="Route B: supervisor-comment distillation report")
    p.add_argument("file", help="JSONL, see distill/schema/comment.schema.json")
    p.add_argument("--min-comments", type=int, default=3)
    p.add_argument("--min-drafts", type=int, default=2)
    p.set_defaults(func=cmd_comments)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
