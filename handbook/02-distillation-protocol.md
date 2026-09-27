# Scholar-to-Skill Distillation Protocol

目标不是总结“某学者说过什么”，而是识别他/她在不同论文中**反复执行的研究动作**，再把稳定动作转成 Agent 可执行规则。

## 1. Corpus sampling

每位学者建议第一轮 15–25 篇，第二轮扩到 40–60 篇。

最低覆盖：
- 至少 3 个时间阶段；
- 至少 3 类主题；
- 独著/第一作者论文优先，同时保留部分合作论文；
- 理论/概念文、定量文、案例文分别抽样；
- 不要只抽“最出名的三篇”，否则会把单篇技巧误认成稳定风格。

### MVP 六组
- 周雪光：制度逻辑、官僚组织、运动型治理、控制权、历史制度分析；
- 周黎安：行政发包、官员激励、地方政府行为、制度比较；
- 何艳玲：城市/地方治理、行政体制改革、大国有效治理、自主知识体系；
- 朱旭峰：政策过程、专家知识、政策扩散、政策创新、实验/调查；
- 马骏：公共预算、财政制度、问责、改革能力；
- 郁建兴：治理理论、国家—社会关系、社会治理、精准治理、数字治理。

## 2. Per-paper annotation schema

每篇论文只提炼以下字段，不做泛泛摘要：

```yaml
paper_id:
bibliography:
paper_type:
empirical_phenomenon:
default_expectation:
puzzle:
research_question:
theoretical_target:
literature_families:
precise_gap:
core_concepts:
concept_neighbors:
actors:
institutional_conditions:
actor_goals_constraints:
mechanism_chain:
rival_explanations:
evidence_type:
evidence_to_mechanism_map:
main_findings:
theoretical_move:
boundary_conditions:
normative_implication:
intro_structure:
discussion_structure:
recurring_research_moves:
```

## 3. What counts as a distilled rule

一条“导师规则”进入 Skill，至少满足：

1. **Repeatability**：同一学者至少 3 篇不同论文出现；
2. **Cross-period stability**：最好跨两个时间阶段；
3. **Operationality**：能改写成“Agent 下一步做什么”，而不是人格描述；
4. **Discriminativeness**：不是所有社会科学论文都一样的常识；
5. **Evidence traceability**：能回指支持该规则的论文；
6. **Non-stylistic**：优先蒸馏研究判断，不蒸馏个人措辞。

例如：

坏规则：
> 周雪光善于从中国现实出发，理论深刻。

好规则：
> 当正式制度目标与基层反复行为不一致时，不先归因为执行偏差；先寻找两个同时存在但彼此冲突的制度要求，再检查行动者策略是否是对该结构张力的稳定响应。

## 4. From annotations to skill rules

### Frequency matrix
对每位学者统计：
- Puzzle 类型；
- Gap 类型；
- Concept move；
- Mechanism move；
- Evidence move；
- Contribution move。

### Separate three layers
- **Shared PA core**：六位都反复使用的动作；
- **Archetype-specific**：某一研究传统特别强的动作；
- **Paper-specific trick**：只在一两篇出现，不进入核心 Skill。

## 5. Avoid pseudo-distillation

以下不能算蒸馏：
- 把论文摘要拼在一起；
- 统计高频词；
- 让 LLM 直接回答“某教授的风格是什么”；
- 从引用次数推断研究方法；
- 用一篇成名作代表整个学术生涯；
- 只学句式，不学 problem → mechanism → evidence 的结构。

## 6. Hold-out validation

每位学者留出 20% 论文不参与规则生成。

验证任务：

### Task A — Structure prediction
只给标题、摘要前半和研究材料，让 Skill 预测：
- 文章会如何定义 puzzle；
- 会选择什么理论对话；
- 机制应该如何展开。
再与留出论文实际结构比较。

### Task B — Revision utility
准备 20 篇匿名公共管理草稿片段：
- baseline LLM；
- 通用学术写作 prompt；
- 本 Skill。
由公共管理博士生/教师盲评：
1. 问题意识提升；
2. 理论对话提升；
3. 机制清晰度提升；
4. 证据—结论匹配；
5. 是否引入虚假/过度理论化。

### Task C — Attribution sanity
把学者名字全部去掉，检查 Skill 的规则是否仍然有用。
若去掉名字就失去价值，说明做的是“名人角色扮演”，不是知识蒸馏。

## 7. Recommended repository growth

```text
corpus/
  metadata/
  annotations/
  heldout/
references/
  scholar-archetypes.md
  evidence-rules.md
skills/
handbook/
eval/
  blind_revision_set/
  rubric.md
  results/
```

## 8. Release criterion for v1.0

从 MVP 升到 v1.0 前至少做到：
- 6 位学者 × 15 篇 = 90 篇人工/半自动结构标注；
- 每条 archetype rule 有 ≥3 篇来源；
- 20 篇 held-out 论文验证；
- 20 个匿名稿件修改对照；
- 关键引用可以回溯；
- Skill 不依赖学者名字也能工作。
