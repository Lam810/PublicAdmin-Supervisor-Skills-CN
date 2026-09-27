# 评测（eval/）

| 文件 | 内容 |
|---|---|
| [prereg.md](prereg.md) | 预注册：冻结条件、成功与失败判据、无论结果都报告的内容 |
| [rubric.md](rubric.md) | Task B 盲评量表 D1–D8 与捏造计数规则 |
| [blind_revision_set/README.md](blind_revision_set/README.md) | 盲评稿件的格式、匿名化与授权要求 |

## Task A：留出集结构预测

```bash
# 前提：留出论文已有全文、已标注并通过 validate --write
python scripts/pa_distill.py holdout corpus/annotations/<run> --out eval/results/holdout-A1
```

输出 `holdout_results.json` 与 `holdout_report.md`。判读见 prereg.md 第 2 节。`--dry-run` 只渲染提示词，不调用模型。

## Task B：盲评

```bash
python scripts/pa_distill.py blind-pack eval/blind_revision_set/items.jsonl --out eval/packets/B1 --raters 3
# 把 packet_R*.md 与 scores_R*.csv 分发给评分人；_key.json 由组织者保管，不发给评分人
python scripts/pa_distill.py blind-score eval/packets/B1 --baseline baseline
```

`items.jsonl` 每行一个条目：`{"item_id": "...", "draft": "原稿片段", "outputs": {"baseline": "...", "generic": "...", "skill": "..."}}`。三个系统的修改稿须用同一模型、同一温度、同一修改指令生成。

## 结果存放

`eval/results/` 与 `eval/packets/` 被 `.gitignore` 忽略，因为其中含稿件原文与评分人信息。公开报告时只发布汇总表（`*_report.md`），并去除任何可识别信息。
