"""Turn verified annotations into rule support, admission decisions and rule-mining hints.

Only *train* papers count.  Held-out papers are excluded so that the rules can
later be evaluated on papers that did not shape them.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .common import PERIODS, HarnessError, now_iso, warn
from .validate import load_annotations


@dataclass
class Record:
    paper_id: str
    scholar_key: str
    period: str
    split: str
    codes: set[str] = field(default_factory=set)
    fields: set[str] = field(default_factory=set)


def load_records(dirs: list[Path], papers: list[dict[str, str]], *, require_verified: bool = True) -> tuple[list[Record], list[str]]:
    by_id = {p["paper_id"]: p for p in papers}
    records: list[Record] = []
    problems: list[str] = []
    seen: set[str] = set()
    for path, ann in load_annotations(dirs):
        pid = str(ann.get("paper_id", path.stem))
        if pid in seen:
            problems.append(f"{pid}: duplicate annotation ({path}); keeping the first — adjudicate before aggregating")
            continue
        row = by_id.get(pid)
        if row is None:
            problems.append(f"{pid}: not in corpus/papers.csv; skipped")
            continue
        ver = (ann.get("meta") or {}).get("verification")
        if not ver:
            if require_verified:
                problems.append(f"{pid}: no verification stamp — run `pa_distill.py validate --write` first; skipped")
                continue
            codes = {m.get("code") for m in ann.get("moves", []) if isinstance(m, dict)}
            flds = {k for k, v in (ann.get("fields") or {}).items() if isinstance(v, dict) and v.get("status") == "present"}
        else:
            if require_verified and not ver.get("passed"):
                problems.append(f"{pid}: verification failed (hit rate {ver.get('hit_rate')}); skipped")
                continue
            codes = set(ver.get("verified_moves", []))
            flds = set(ver.get("verified_fields", []))
        seen.add(pid)
        records.append(Record(pid, row["scholar_key"], row["period"], row.get("split", ""), codes, flds))
    return records, problems


def clause_ok(clause: str, rec: Record) -> bool:
    if clause.startswith("field:"):
        return clause[len("field:"):] in rec.fields
    for alt in clause.split("|"):
        alt = alt.strip()
        if alt.endswith("-*"):
            prefix = alt[:-1]
            if any(c.startswith(prefix) for c in rec.codes):
                return True
        elif alt in rec.codes:
            return True
    return False


def satisfies(rule: dict[str, Any], rec: Record) -> bool:
    req = rule.get("requires") or []
    return bool(req) and all(clause_ok(c, rec) for c in req)


def _lift(s_in: int, n_in: int, s_out: int, n_out: int) -> float | None:
    if n_in == 0 or n_out == 0:
        return None
    return ((s_in + 0.5) / (n_in + 1)) / ((s_out + 0.5) / (n_out + 1))


def compute_support(records: list[Record], registry: dict[str, Any], *, allow_unsplit: bool = False) -> dict[str, Any]:
    adm = registry["admission"]
    unsplit = [r.paper_id for r in records if r.split not in ("train", "heldout")]
    if unsplit and not allow_unsplit:
        raise HarnessError(f"{len(unsplit)} annotated paper(s) have no split (e.g. {unsplit[:3]}); run `pa_distill.py split` first")
    train = [r for r in records if r.split != "heldout"]
    n_heldout = len(records) - len(train)
    lens_keys = {lens["id"]: set(lens["tradition"]["keys"]) for lens in registry["lenses"]}
    per_key = Counter(r.scholar_key for r in train)
    keys_with_data = sorted(k for k, n in per_key.items() if n > 0)
    out_rules: dict[str, Any] = {}
    for rule in registry["rules"]:
        sat = [r for r in train if satisfies(rule, r)]
        reasons: list[str] = []
        entry: dict[str, Any] = {"lens": rule["lens"], "layer": rule["layer"], "status": rule["status"]}
        if rule["layer"] == "shared":
            by_key = Counter(r.scholar_key for r in sat)
            share = (sum(1 for k in keys_with_data if by_key[k] > 0) / len(keys_with_data)) if keys_with_data else 0.0
            n_support = len(sat)
            periods = sorted({r.period for r in sat if r.period}, key=_pidx)
            if n_support < adm["min_papers"]:
                reasons.append(f"支持篇数 {n_support} < {adm['min_papers']}")
            if share < adm["shared_min_scholar_share"]:
                reasons.append(f"传统覆盖率 {share:.2f} < {adm['shared_min_scholar_share']}")
            n_annotated = len(train)
            entry.update({"support_papers": sorted(r.paper_id for r in sat), "n_support": n_support,
                          "periods": periods, "share": round(share, 3), "by_scholar": dict(by_key)})
        else:
            keys = lens_keys.get(rule["lens"], set())
            inside = [r for r in train if r.scholar_key in keys]
            outside = [r for r in train if r.scholar_key not in keys]
            s_in = [r for r in sat if r.scholar_key in keys]
            s_out = [r for r in sat if r.scholar_key not in keys]
            periods = sorted({r.period for r in s_in if r.period}, key=_pidx)
            lift = _lift(len(s_in), len(inside), len(s_out), len(outside))
            n_support = len(s_in)
            n_annotated = len(inside)
            if n_support < adm["min_papers"]:
                reasons.append(f"本传统支持篇数 {n_support} < {adm['min_papers']}")
            if len(periods) < adm["min_periods"]:
                reasons.append(f"覆盖时期 {len(periods)} < {adm['min_periods']}")
            if lift is None:
                reasons.append("缺少对照数据，无法计算区分度")
            elif lift < adm["min_lift"]:
                reasons.append(f"区分度 lift {lift:.2f} < {adm['min_lift']}")
            entry.update({"support_papers": sorted(r.paper_id for r in s_in), "n_support": n_support,
                          "periods": periods, "n_tradition_annotated": n_annotated,
                          "n_other_support": len(s_out), "n_other_annotated": len(outside),
                          "lift": None if lift is None else round(lift, 3)})
        passed = not reasons
        if passed:
            suggestion = "candidate" if rule["status"] == "seed" else rule["status"]
        elif n_annotated >= adm["min_annotated_for_rejection"]:
            suggestion = "rejected"
        else:
            suggestion = "insufficient_data"
        entry.update({"pass": passed, "suggestion": suggestion, "reasons": reasons})
        out_rules[rule["id"]] = entry
    matrix: dict[str, dict[str, int]] = defaultdict(dict)
    for r in train:
        for c in r.codes:
            matrix[c][r.scholar_key] = matrix[c].get(r.scholar_key, 0) + 1
    return {
        "generated_at": now_iso(),
        "registry_version": registry.get("version"),
        "admission": adm,
        "n_annotations": len(records),
        "n_train": len(train),
        "n_heldout_excluded": n_heldout,
        "per_scholar_train": dict(per_key),
        "rules": out_rules,
        "code_matrix": {c: matrix[c] for c in sorted(matrix)},
    }


def _pidx(p: str) -> int:
    return PERIODS.index(p) if p in PERIODS else 99


def support_report(sup: dict[str, Any]) -> str:
    lines = [
        "# 规则支持度报告",
        "",
        f"- 生成时间：{sup['generated_at']}",
        f"- 已核验标注：{sup['n_annotations']} 篇；计入训练集：{sup['n_train']} 篇；排除留出集：{sup['n_heldout_excluded']} 篇",
        f"- 各传统训练集篇数：{json.dumps(sup['per_scholar_train'], ensure_ascii=False)}",
        f"- 准入门槛：{json.dumps(sup['admission'], ensure_ascii=False)}",
        "",
        "机器只计数与建议；状态变更须人工在 rules/registry.yaml 中完成（见 rules/README.md）。",
        "",
        "| 规则 | 镜头 | 当前状态 | 支持 | 时期 | lift/覆盖率 | 通过 | 建议 | 未通过原因 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for rid, e in sup["rules"].items():
        metric = e.get("lift") if e["layer"] != "shared" else e.get("share")
        lines.append(f"| {rid} | {e['lens']} | {e['status']} | {e['n_support']} | {len(e['periods'])} | "
                     f"{'—' if metric is None else metric} | {'是' if e['pass'] else '否'} | {e['suggestion']} | "
                     f"{'；'.join(e['reasons']) or '—'} |")
    keys = sorted(sup["per_scholar_train"])
    if sup["code_matrix"]:
        lines += ["", "## 研究动作 × 传统频次（训练集，按论文计）", "", "| 编码 | " + " | ".join(keys) + " |",
                  "|---|" + "---|" * len(keys)]
        for code, row in sup["code_matrix"].items():
            lines.append(f"| {code} | " + " | ".join(str(row.get(k, 0)) for k in keys) + " |")
    return "\n".join(lines) + "\n"


def mine_itemsets(records: list[Record], registry: dict[str, Any], top: int = 30) -> str:
    adm = registry["admission"]
    train = [r for r in records if r.split != "heldout"]
    keys = sorted({r.scholar_key for r in train})
    lens_of_key = {k: [l["id"] for l in registry["lenses"] if k in l["tradition"]["keys"]] for k in keys}
    lines = ["# 候选规则挖掘（仅供人工起草规则参考）", ""]
    for key in keys:
        inside = [r for r in train if r.scholar_key == key]
        outside = [r for r in train if r.scholar_key != key]
        if len(inside) < adm["min_papers"]:
            continue
        counts: Counter = Counter()
        periods: dict[tuple, set] = defaultdict(set)
        for r in inside:
            for size in (1, 2, 3):
                for combo in itertools.combinations(sorted(r.codes), size):
                    counts[combo] += 1
                    periods[combo].add(r.period)
        rows = []
        for combo, n in counts.items():
            if n < adm["min_papers"] or len(periods[combo]) < adm["min_periods"]:
                continue
            n_out = sum(1 for r in outside if set(combo) <= r.codes)
            lift = _lift(n, len(inside), n_out, len(outside))
            if lift is None or lift < adm["min_lift"]:
                continue
            covered = [rule["id"] for rule in registry["rules"] if rule["lens"] in lens_of_key[key]
                       and satisfies(rule, Record("", key, "", "train", set(combo)))]
            rows.append((lift, n, combo, covered))
        rows.sort(key=lambda x: (-x[0], -x[1], len(x[2])))
        lines += [f"## {key}（训练集 {len(inside)} 篇，对照 {len(outside)} 篇）", "",
                  "| 动作组合 | 篇数 | lift | 已被规则覆盖 |", "|---|---|---|---|"]
        for lift, n, combo, covered in rows[:top]:
            lines.append(f"| {' + '.join(combo)} | {n} | {lift:.2f} | {', '.join(covered) or '—'} |")
        lines.append("")
    if len(lines) == 2:
        lines.append("训练集数据不足，暂无可报告的组合。")
    return "\n".join(lines) + "\n"


def aggregate_comments(path: Path, min_comments: int = 3, min_drafts: int = 2) -> str:
    """Route B: supervisor-comment distillation (see handbook/03)."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise HarnessError(f"{path}:{i}: invalid JSON ({exc})") from exc
    by_adv: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_adv[str(r.get("advisor", "unknown"))].append(r)
    lines = ["# 导师批注蒸馏报告", "", f"共 {len(rows)} 条批注，{len(by_adv)} 位批注者。", ""]
    for adv, rs in sorted(by_adv.items()):
        code_drafts: dict[str, set] = defaultdict(set)
        code_n: Counter = Counter()
        code_gen: Counter = Counter()
        for r in rs:
            for c in (r.get("defect_codes") or []) + (r.get("move_codes") or []):
                code_n[c] += 1
                code_drafts[c].add(r.get("draft_id"))
                if r.get("generalizable"):
                    code_gen[c] += 1
        lines += [f"## 批注者 {adv}（{len(rs)} 条，{len({r.get('draft_id') for r in rs})} 份稿件）", "",
                  "| 编码 | 批注数 | 涉及稿件 | 可泛化占比 | 候选规则 |", "|---|---|---|---|---|"]
        for c, n in code_n.most_common():
            nd = len(code_drafts[c])
            gen = code_gen[c] / n
            cand = "是" if n >= min_comments and nd >= min_drafts and gen >= 0.5 else ""
            lines.append(f"| {c} | {n} | {nd} | {gen:.0%} | {cand} |")
        lines.append("")
    lines.append(f"候选规则门槛：≥{min_comments} 条批注、≥{min_drafts} 份稿件、可泛化占比 ≥50%。")
    return "\n".join(lines) + "\n"
