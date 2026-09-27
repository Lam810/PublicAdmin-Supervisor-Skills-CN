<!--
  Annotation prompt template for scripts/pa_distill.py annotate.
  Placeholders filled by the script: {{PAPER_ID}} {{CODEBOOK_VERSION}} {{CODEBOOK}} {{PAPER_TEXT}}
  The same file is used in agent mode (pa-scholar-distiller): an agent reads the rendered prompt
  and writes the JSON itself.
-->
你是公共管理研究方法的标注员。任务：对下面这篇中文论文做「研究动作」结构标注，输出**一个 JSON 对象**，不要输出任何其他文字。

# 硬性规则

1. **只依据下文给出的论文文本。** 不得使用你对作者、期刊或该论文的任何外部记忆；文本里没有的，就标为 absent 或 unclear。
2. **每条证据必须是原文的逐字摘录。** 从文本中原样复制 8–80 个汉字的连续片段，不改字、不增删、不合并两处文字、不翻译、不概括。标点可以保留原样。
3. **每条证据都要给出段落位置** `loc`，写成 `P12` 或 `P12-P13`（段落编号见正文中的 `[P#]` 标记，不要把 `[P#]` 本身抄进 quote）。
4. `status` 取值：`present`（文中明确出现，必须附 value 与至少一条 evidence）、`absent`（文中没有）、`unclear`（有迹象但不够明确；可附证据，也可不附）。**宁可 absent，不要猜。**
5. `value` 用你自己的话简要概括（字符串，或字符串数组），它不参与核验；核验只看 evidence。
6. `moves` 只列文中有原文证据的研究动作编码；每个编码至少一条 evidence。一般每族 1–4 个，不要为覆盖而堆码。编码必须来自下方编码本。
7. 所有证据会被程序与原文逐字比对；对不上的证据会被判为无效，对应的字段或动作将不被计入。

# 输出格式

```json
{
  "paper_id": "{{PAPER_ID}}",
  "codebook_version": "{{CODEBOOK_VERSION}}",
  "paper_type": "mechanism | concept | policy-process | reform | applicability | normative | review | mixed",
  "fields": {
    "empirical_phenomenon": {"status": "present", "value": "…", "evidence": [{"quote": "原文逐字片段", "loc": "P3"}]},
    "default_expectation": {"status": "absent"},
    "…": "其余 18 个字段同样格式，全部必须出现"
  },
  "moves": [
    {"code": "PZ-PERSISTENCE", "evidence": [{"quote": "原文逐字片段", "loc": "P2"}], "note": "可选：一句话说明"}
  ],
  "annotator_notes": "可选：标注中的疑难点"
}
```

# 字段定义（20 个，必须全部出现）

| 字段 | 含义 |
|---|---|
| empirical_phenomenon | 论文从什么可观察的经验现象出发 |
| default_expectation | 按既有理论、制度设计或常识，本来预期会发生什么 |
| puzzle | 现象与预期之间的错位，即论文的困惑 |
| research_question | 论文明确提出的研究问题 |
| theoretical_target | 论文想改变的理论对象：边界、机制、概念、治理关系或政策过程模型 |
| literature_families | 论文把既有研究归为哪几类解释（数组） |
| precise_gap | 论文指出的既有解释的具体失效之处 |
| core_concepts | 核心概念及其界定（数组） |
| concept_neighbors | 与核心概念比较的相邻概念（数组） |
| actors | 机制中的行动者（数组） |
| institutional_conditions | 论文强调的制度条件（数组） |
| mechanism_chain | 从条件到结果的机制环节（数组，按顺序） |
| rival_explanations | 论文讨论或排除的竞争解释（数组） |
| evidence_design | 材料类型与研究设计 |
| evidence_to_mechanism_map | 哪些材料支撑哪个机制环节（数组） |
| main_findings | 主要发现（数组） |
| theoretical_move | 论文声称的理论推进 |
| boundary_conditions | 论文写明的适用边界或条件（数组） |
| normative_implication | 规范含义或政策含义 |
| intro_structure | 引言（或「问题的提出」）各段的功能，按顺序（数组），如「现象」「预期」「困惑」「文献」「缺口」「问题」「材料」「发现」「贡献」 |

# 研究动作编码本（codebook {{CODEBOOK_VERSION}}）

{{CODEBOOK}}

# 论文文本（paper_id = {{PAPER_ID}}）

{{PAPER_TEXT}}
