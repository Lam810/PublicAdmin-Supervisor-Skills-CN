"""Task A: held-out structure prediction with and without the distilled rules."""

from __future__ import annotations

import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .aggregate import load_records
from .annotate import render_codebook
from .common import PROMPT_DIR, HarnessError, info, load_moves, now_iso, write_json
from .corpus import find_fulltext, load_abstract, load_fulltext
from .llm import LLMConfig, chat, extract_json
from .stats import bootstrap_ci, mean, set_f1
from .validate import load_annotations

FAMILIES = ["PZ", "GAP", "CON", "MECH", "CTR"]
VARIANTS = ("baseline", "rules", "rules_named")


def render_rules_block(registry: dict[str, Any], named: bool) -> str:
    lines = ["# 可参考的研究动作规则", "", "以下规则抽象自公共管理研究传统，只描述研究动作，不代表任何学者的观点。", ""]
    for lens in registry["lenses"]:
        rules = [r for r in registry["rules"] if r["lens"] == lens["id"] and r["status"] != "rejected"]
        if not rules:
            continue
        head = f"## {lens['id']} {lens['name']}"
        if named and lens["tradition"]["scholars"]:
            head += f"（抽象自{'、'.join(lens['tradition']['scholars'])}等的研究传统）"
        lines.append(head)
        for q in lens.get("questions") or []:
            lines.append(f"- 追问：{q}")
        for r in rules:
            lines.append(f"- {r['id']}：当{r['trigger'].rstrip('。')}时，{r['action']}")
        lines.append("")
    return "\n".join(lines).strip()


def _template() -> str:
    text = (PROMPT_DIR / "holdout_predict.md").read_text(encoding="utf-8")
    return text.split("-->", 1)[1].lstrip("\n") if text.lstrip().startswith("<!--") else text


def _half(text: str) -> str:
    return text[: max(1, len(text) // 2)] if text else "（无）"


def _evidence_text(ann: dict[str, Any]) -> str:
    v = ((ann.get("fields") or {}).get("evidence_design") or {}).get("value")
    if isinstance(v, list):
        return "；".join(v)
    return v or "（未说明）"


def _parse_prediction(content: str, fam_of: dict[str, str]) -> dict[str, set[str]]:
    try:
        obj = extract_json(content)
    except (ValueError, json.JSONDecodeError):
        return {f: set() for f in FAMILIES}
    out: dict[str, set[str]] = {}
    for fam in FAMILIES:
        vals = obj.get(fam) if isinstance(obj, dict) else None
        codes = [c for c in (vals or []) if isinstance(c, str) and fam_of.get(c) == fam]
        out[fam] = set(codes[:3])
    return out


def run_holdout(ann_dirs: list[Path], papers: list[dict[str, str]], registry: dict[str, Any], cfg: LLMConfig | None,
                variants: list[str], out_dir: Path, n_boot: int = 5000, seed: int = 0, dry_run: bool = False) -> dict[str, Any]:
    moves = load_moves()
    fam_of = {m["code"]: m["family"] for m in moves["moves"]}
    records, problems = load_records(ann_dirs, papers)
    for p in problems:
        info(f"  [skip] {p}")
    train = [r for r in records if r.split == "train"]
    held = [r for r in records if r.split == "heldout"]
    if not held:
        raise HarnessError("no verified held-out annotations found; annotate and validate held-out papers first")
    anns = {str(a.get("paper_id")): a for _, a in load_annotations(ann_dirs)}
    rows = {p["paper_id"]: p for p in papers}

    def gold(rec) -> dict[str, set[str]]:
        return {f: {c for c in rec.codes if fam_of.get(c) == f} for f in FAMILIES}

    # trivial baselines from the train split only
    freq: dict[str, Counter] = {f: Counter() for f in FAMILIES}
    sizes: dict[str, list[int]] = defaultdict(list)
    for r in train:
        g = gold(r)
        for f in FAMILIES:
            freq[f].update(g[f])
            sizes[f].append(len(g[f]))
    k_of = {f: max(1, round(statistics.median(sizes[f]))) if sizes[f] else 1 for f in FAMILIES}
    majority = {f: {c for c, _ in freq[f].most_common(k_of[f])} for f in FAMILIES}

    def score(pred: dict[str, set[str]], g: dict[str, set[str]]) -> float:
        vals = [set_f1(pred[f], g[f]) for f in FAMILIES]
        vals = [v for v in vals if v is not None]
        return mean(vals) if vals else float("nan")

    rng = random.Random(seed)
    per_paper: dict[str, dict[str, float]] = defaultdict(dict)
    predictions: dict[str, dict[str, Any]] = defaultdict(dict)
    template = _template()
    codebook = render_codebook(moves, FAMILIES)
    blocks = {"baseline": "", "rules": render_rules_block(registry, named=False),
              "rules_named": render_rules_block(registry, named=True)}
    for rec in held:
        g = gold(rec)
        per_paper[rec.paper_id]["majority"] = score(majority, g)
        rand_scores = []
        for _ in range(20):
            pred = {}
            for f in FAMILIES:
                pool = list(freq[f].elements())
                pred[f] = set(rng.sample(pool, min(k_of[f], len(pool)))) if pool else set()
            rand_scores.append(score(pred, g))
        per_paper[rec.paper_id]["random"] = mean([s for s in rand_scores if s == s])
        row = rows[rec.paper_id]
        ft_path = find_fulltext(row)
        abstract = load_abstract(row, load_fulltext(ft_path) if ft_path else None)
        for variant in variants:
            prompt = (template.replace("{{RULES}}", blocks[variant])
                      .replace("{{CODEBOOK}}", codebook)
                      .replace("{{TITLE}}", row["title"])
                      .replace("{{ABSTRACT_HALF}}", _half(abstract))
                      .replace("{{EVIDENCE}}", _evidence_text(anns.get(rec.paper_id, {}))))
            if dry_run:
                (out_dir / "_prompts").mkdir(parents=True, exist_ok=True)
                (out_dir / "_prompts" / f"{rec.paper_id}.{variant}.md").write_text(prompt, encoding="utf-8")
                continue
            assert cfg is not None
            content, _ = chat(cfg, [{"role": "user", "content": prompt}])
            pred = _parse_prediction(content, fam_of)
            predictions[rec.paper_id][variant] = {f: sorted(v) for f, v in pred.items()}
            per_paper[rec.paper_id][variant] = score(pred, g)
        predictions[rec.paper_id]["gold"] = {f: sorted(v) for f, v in g.items()}
    systems = ["majority", "random"] + ([] if dry_run else variants)
    summary: dict[str, Any] = {"generated_at": now_iso(), "n_heldout": len(held), "n_train": len(train),
                               "k_per_family": k_of, "systems": {}, "contrasts": {}}
    for s in systems:
        vals = [per_paper[p][s] for p in per_paper if s in per_paper[p] and per_paper[p][s] == per_paper[p][s]]
        summary["systems"][s] = {"mean_f1": round(mean(vals), 4) if vals else None, "n": len(vals)}
    contrasts = [("rules", "baseline"), ("rules", "majority"), ("baseline", "majority"), ("rules_named", "rules")]
    for a, b in contrasts:
        if a not in systems or b not in systems:
            continue
        diffs = [per_paper[p][a] - per_paper[p][b] for p in per_paper if a in per_paper[p] and b in per_paper[p]]
        m, lo, hi = bootstrap_ci(diffs, n_boot=n_boot, seed=seed)
        summary["contrasts"][f"{a} - {b}"] = {"mean": round(m, 4), "ci95": [round(lo, 4), round(hi, 4)], "n": len(diffs)}
    write_json(out_dir / "holdout_results.json", {"summary": summary, "per_paper": per_paper, "predictions": predictions})
    (out_dir / "holdout_report.md").write_text(holdout_report(summary), encoding="utf-8")
    return summary


def holdout_report(summary: dict[str, Any]) -> str:
    lines = ["# 留出验证 Task A：结构预测", "",
             f"- 留出论文：{summary['n_heldout']} 篇；训练论文：{summary['n_train']} 篇；每族预测个数 k：{summary['k_per_family']}",
             "- 指标：每篇论文在 PZ/GAP/CON/MECH/CTR 五族上的集合 F1 的平均；差值为配对差，95% 区间为自助法百分位区间。",
             "- 判读见 eval/prereg.md：rules 必须同时胜过 baseline 与 majority，且区间不跨 0，才算规则有用。", "",
             "| 系统 | 平均 F1 | n |", "|---|---|---|"]
    for s, v in summary["systems"].items():
        lines.append(f"| {s} | {v['mean_f1']} | {v['n']} |")
    if summary["contrasts"]:
        lines += ["", "| 对比 | 平均差 | 95% 区间 | n |", "|---|---|---|---|"]
        for k, v in summary["contrasts"].items():
            lines.append(f"| {k} | {v['mean']} | [{v['ci95'][0]}, {v['ci95'][1]}] | {v['n']} |")
    return "\n".join(lines) + "\n"
