<!--
  Held-out structure prediction (Task A) prompt for scripts/pa_distill.py holdout.
  Placeholders: {{RULES}} {{CODEBOOK}} {{TITLE}} {{ABSTRACT_HALF}} {{EVIDENCE}}
-->
你将看到一篇中文公共管理论文的标题、摘要前半部分和研究材料说明。请预测这篇论文**实际使用了**哪些研究动作。

只输出一个 JSON 对象，格式如下，不要输出其他文字：

```json
{"PZ": ["…"], "GAP": ["…"], "CON": ["…"], "MECH": ["…"], "CTR": ["…"]}
```

要求：每族最多 3 个编码；编码必须来自下方编码本且属于对应族；没有把握的族给空数组。不要猜测作者身份，也不要依赖你对这篇论文的任何记忆。

{{RULES}}

# 编码本

{{CODEBOOK}}

# 论文信息

- 标题：{{TITLE}}
- 摘要（前半部分）：{{ABSTRACT_HALF}}
- 研究材料：{{EVIDENCE}}
