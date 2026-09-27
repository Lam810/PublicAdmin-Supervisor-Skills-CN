"""Task B: blind revision-utility evaluation (packing and scoring)."""

from __future__ import annotations

import csv
import json
import random
import string
from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import HarnessError, now_iso, read_json, write_json
from .stats import bootstrap_ci, krippendorff_alpha, mean

DIMENSIONS = [
    ("D1", "问题意识提升"),
    ("D2", "理论对话提升"),
    ("D3", "机制清晰度提升"),
    ("D4", "证据—结论匹配"),
    ("D5", "未引入虚假或过度理论化"),
]


def _load_items(path: Path) -> list[dict[str, Any]]:
    items = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if not obj.get("item_id") or not isinstance(obj.get("outputs"), dict) or len(obj["outputs"]) < 2:
                raise HarnessError(f"{path}:{i}: each item needs item_id, draft and >=2 outputs")
            items.append(obj)
    systems = {tuple(sorted(it["outputs"])) for it in items}
    if len(systems) != 1:
        raise HarnessError("all items must contain outputs from the same set of systems")
    return items


def pack(items_path: Path, out_dir: Path, raters: int, seed: int = 7) -> dict[str, Any]:
    items = _load_items(items_path)
    rng = random.Random(seed)
    key: dict[str, dict[str, str]] = {}
    for it in items:
        systems = list(it["outputs"])
        rng.shuffle(systems)
        key[it["item_id"]] = {string.ascii_uppercase[i]: s for i, s in enumerate(systems)}
    out_dir.mkdir(parents=True, exist_ok=True)
    for r in range(1, raters + 1):
        order = items[:]
        random.Random(seed * 1000 + r).shuffle(order)
        md = [f"# 盲评材料 · 评分人 R{r}", "", "请独立评分，不要与其他评分人讨论。每个维度 1–5 分，评分标准见 eval/rubric.md。", ""]
        rows = []
        for it in order:
            md += [f"## 条目 {it['item_id']}", "", "### 原稿片段", "", it.get("draft", "").strip(), ""]
            for label, system in sorted(key[it["item_id"]].items()):
                md += [f"### 修改稿 {label}", "", it["outputs"][system].strip(), ""]
                rows.append({"item_id": it["item_id"], "label": label, **{d: "" for d, _ in DIMENSIONS}, "comment": ""})
        (out_dir / f"packet_R{r}.md").write_text("\n".join(md), encoding="utf-8")
        with open(out_dir / f"scores_R{r}.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["item_id", "label"] + [d for d, _ in DIMENSIONS] + ["comment"], lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    write_json(out_dir / "_key.json", {"created_at": now_iso(), "seed": seed, "key": key})
    return {"items": len(items), "raters": raters, "key": str(out_dir / "_key.json")}


def score(pack_dir: Path, baseline: str, margin: float = 0.5, n_boot: int = 5000, seed: int = 0) -> dict[str, Any]:
    key = read_json(pack_dir / "_key.json")["key"]
    sheets = sorted(pack_dir.glob("scores_R*.csv"))
    if not sheets:
        raise HarnessError(f"no scores_R*.csv in {pack_dir}")
    # ratings[(item, system)][dim] -> {rater: value}
    ratings: dict[tuple[str, str], dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for sheet in sheets:
        rater = sheet.stem.split("_", 1)[1]
        with open(sheet, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                system = key.get(row["item_id"], {}).get(row["label"])
                if system is None:
                    raise HarnessError(f"{sheet.name}: unknown item/label {row['item_id']}/{row['label']}")
                for d, _ in DIMENSIONS:
                    val = (row.get(d) or "").strip()
                    if not val:
                        continue
                    x = float(val)
                    if not 1 <= x <= 5:
                        raise HarnessError(f"{sheet.name}: {d}={val} outside 1..5")
                    ratings[(row["item_id"], system)][d][rater] = x
    systems = sorted({s for _, s in ratings})
    if baseline not in systems:
        raise HarnessError(f"baseline system {baseline!r} not among {systems}")
    items = sorted({i for i, _ in ratings})
    raters = sorted({r for v in ratings.values() for dd in v.values() for r in dd})
    result: dict[str, Any] = {"generated_at": now_iso(), "items": len(items), "raters": raters, "systems": {}, "vs_baseline": {}, "alpha": {}}
    item_mean: dict[tuple[str, str, str], float] = {}
    for (item, system), dims in ratings.items():
        for d, by_r in dims.items():
            item_mean[(item, system, d)] = mean(list(by_r.values()))
    for s in systems:
        result["systems"][s] = {d: round(mean([item_mean[(i, s, d)] for i in items if (i, s, d) in item_mean]), 3) for d, _ in DIMENSIONS}
    for s in systems:
        if s == baseline:
            continue
        result["vs_baseline"][s] = {}
        for d, _ in DIMENSIONS:
            diffs = [item_mean[(i, s, d)] - item_mean[(i, baseline, d)] for i in items if (i, s, d) in item_mean and (i, baseline, d) in item_mean]
            m, lo, hi = bootstrap_ci(diffs, n_boot=n_boot, seed=seed)
            entry = {"mean": round(m, 3), "ci95": [round(lo, 3), round(hi, 3)], "n": len(diffs)}
            if d == "D5":
                entry["noninferior"] = bool(lo > -margin)
                entry["margin"] = margin
            result["vs_baseline"][s][d] = entry
    for d, _ in DIMENSIONS:
        units = [[ratings[(i, s)][d].get(r) for r in raters] for i in items for s in systems if (i, s) in ratings]
        a = krippendorff_alpha(units, "interval")
        result["alpha"][d] = None if a != a else round(a, 3)
    write_json(pack_dir / "blind_results.json", result)
    (pack_dir / "blind_report.md").write_text(blind_report(result, baseline), encoding="utf-8")
    return result


def blind_report(res: dict[str, Any], baseline: str) -> str:
    dims = [d for d, _ in DIMENSIONS]
    names = dict(DIMENSIONS)
    lines = ["# 盲评 Task B：修改效用", "", f"- 条目 {res['items']} 个，评分人 {len(res['raters'])} 位；基线系统：{baseline}",
             "- 评分者一致性：Krippendorff's alpha（interval）。alpha < 0.667 时，均值差只能作为探索性结果。", "",
             "| 系统 | " + " | ".join(f"{d} {names[d]}" for d in dims) + " |", "|---|" + "---|" * len(dims)]
    for s, v in res["systems"].items():
        lines.append(f"| {s} | " + " | ".join(str(v[d]) for d in dims) + " |")
    lines += ["", "| 对比基线 | " + " | ".join(dims) + " |", "|---|" + "---|" * len(dims)]
    for s, v in res["vs_baseline"].items():
        cells = []
        for d in dims:
            e = v[d]
            cell = f"{e['mean']} [{e['ci95'][0]}, {e['ci95'][1]}]"
            if d == "D5":
                cell += " 非劣" if e.get("noninferior") else " 未证非劣"
            cells.append(cell)
        lines.append(f"| {s} | " + " | ".join(cells) + " |")
    lines += ["", "| 维度 | alpha |", "|---|---|"] + [f"| {d} | {res['alpha'][d]} |" for d in dims]
    return "\n".join(lines) + "\n"
