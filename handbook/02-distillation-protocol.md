# Scholar-to-Skill Distillation Protocol

> **v0.2 说明**：本章是方法原则。可执行的命令、门槛与判据以这三处为准：`distill/README.md`（流水线）、`rules/registry.yaml`（准入门槛 `admission` 与运行时状态 `build`）、`eval/prereg.md`（留出验证与盲评判据）。

目标不是总结“某学者说过什么”，而是识别他/她在不同论文中**反复执行的研究动作**，再把稳定动作转成 Agent 可执行规则。

## 1. Corpus sampling

每位学者建议第一轮 15–25 篇，第二轮扩到 40–60 篇。

最低覆盖：
- 至少 3 个时间阶段；
- 至少 3 类主题；
- 独著/第一作者论文优先，同时保留部分合作论文；
- 理论/概念文、定量文、案例文分别抽样；
- 不要只抽“最出名的三篇”，否则会把单篇技巧误认成稳定风格。

### 七组研究传统（v0.2）
- 周雪光：制度逻辑、官僚组织、运动型治理、控制权、历史制度分析；
- 周黎安：行政发包、官员激励、地方政府行为、制度比较；
- 何艳玲：城市/地方治理、行政体制改革、大国有效治理、自主知识体系；
- 朱旭峰：政策过程、专家知识、政策扩散、政策创新、实验/调查；
- 马骏：公共预算、财政制度、问责、改革能力；
- 郁建兴：治理理论、国家—社会关系、社会治理、精准治理、数字治理；
- 丁煌：政策执行、利益分析与执行阻滞、博弈模型、行政学说史。

写作架构镜头另有两组来源（马亮、马啸：论文写作与发表、研究设计写法），见 `handbook/03-writing-architecture.md` 与 `corpus/writing-sources.md`。

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
准备 30–50 段匿名公共管理稿件（作者书面同意），分别由 baseline（原生模型）、generic（通用学术写作提示词）、skill（本仓库）修改；
≥3 名公共管理博士生/教师盲评 D1–D8：问题意识、理论对话、概念精确、机制清晰、证据匹配、贡献清晰、未过度理论化、事实可靠，并记录捏造条数。
量表见 `eval/rubric.md`，成功判据（含两项危害维度与捏造率的非劣检验）见 `eval/prereg.md`。

### Task C — Attribution sanity
把学者名字全部去掉，检查 Skill 的规则是否仍然有用。
若去掉名字就失去价值，说明做的是“名人角色扮演”，不是知识蒸馏。

## 7. 仓库中的对应位置

```text
corpus/papers.csv          书目登记（只有元数据）；fulltext/ annotations/ 被忽略
vocab/                     研究动作编码本与缺陷编码
rules/registry.yaml        规则唯一真源：触发、动作、检验、反模式、可计数定义、状态
rules/support.json         机器计数结果（aggregate 生成）
rules/preview/             研究区预览（含 seed/candidate 与来源传统，不被 Skill 加载）
skills/*/references/       build_refs.py 生成：只含 runtime_statuses（默认 validated）的规则
eval/                      预注册、盲评量表、盲评稿件规范
```

## 8. v1.0 发布条件

- 7 位学者 × 至少 15 篇 = 105 篇全文结构标注，全部通过逐字核验，并抽样人工复核语义；
- 各族编码一致性 κ ≥ 0.60（至少一名人类标注者）；
- 每条进入 Skill 的规则状态为 validated，且有可回溯的支持论文；
- Task A 与 Task B 按 `eval/prereg.md` 的判据报告，无论成败；
- Skill 不依赖学者姓名也能工作（`scripts/lint_skills.py` 禁止 skills/ 中出现姓名）。
