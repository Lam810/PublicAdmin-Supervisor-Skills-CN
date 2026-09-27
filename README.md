# PublicAdmin-Supervisor-Skills-CN

**把中国公共管理顶尖学者怎样发现问题、制造概念、构造机制、组织证据和提出理论贡献的隐性知识，蒸馏成可执行、可验证的 AI Skills。**

面向中文公共行政、公共管理与中国治理研究的 AI 科研副导师 Skill Pack。它不模仿任何学者的措辞，而是把公开论文中反复出现的**研究动作**提炼为规则，每条规则都有可被证伪的来源、统计门槛和状态；Skill 只在运行时加载通过验证的规则。

> **当前版本 v0.2.0-dev。** 17 个 Skill 可以安装使用；规则登记表、编码本、经核验的书目清单、蒸馏工具链、评测预注册均已就位。**所有规则目前仍是 `seed`（种子假设）**：还没有完成全文标注与留出验证，因此运行时的镜头卡里暂时只有启发式追问、没有已验证规则。下一步是全文标注，见「路线图」。

## 这个项目和「写作提示词合集」的区别

```text
经核验书目 → 合法全文 → 训练/留出划分 → 逐篇结构标注（逐字摘录 + 段落位置）
  → 摘录与全文逐字比对（防编造）→ 标注一致性 → 训练集计数与准入门槛
  → 人工改状态 seed / candidate / validated / rejected → 生成 Skill 参考 → 留出验证 + 真实稿件盲评
```

- **规则有出处，也会被淘汰。** 每条规则登记在 [`rules/registry.yaml`](rules/registry.yaml)：触发条件、Agent 下一步动作、检验方式、反模式，以及用研究动作编码写成的「怎样算一篇论文支持了它」。准入门槛：训练集中 ≥3 篇、跨 ≥2 个时期、在本传统中的出现率是其他传统的 ≥1.5 倍。
- **Skill 只加载已验证规则。** `scripts/build_refs.py` 只把 `validated` 规则渲染进 Skill；seed 与 candidate 留在研究区预览 [`rules/preview/`](rules/preview/lens-cards-preview.md)；被判为 rejected 的规则重新 build 后从 Skill 消失。
- **标注不能编造证据。** 每个字段、每个研究动作都要附原文逐字摘录与段落位置，程序逐字比对，对不上的一律不计入。单元测试专门验证：伪造或改写的摘录必须被拦下。
- **留出验证防泄漏。** 语料按学者分层分出 20% 留出集；参与种子规则形成的论文永远留在训练集；评测判据在看结果之前写进 [`eval/prereg.md`](eval/prereg.md)。
- **Skill 里没有学者姓名。** 姓名只出现在 README、规则登记表、研究区预览和书目清单中，用于说明来源；`lint_skills.py` 禁止 `skills/` 中出现姓名。去掉姓名 Skill 仍须可用，否则就只是名人角色扮演。

## 七个研究镜头

| 镜头 | 抽象自 | 关注什么 |
|---|---|---|
| IL 制度逻辑 | 周雪光 | 稳定、反复、看似违背正式制度目标的现象；结构张力 → 策略 → 稳定化 |
| CE 概念工程 | 周黎安 | 理想类型、维度化、相邻概念逐维比较、由概念推出可反驳命题 |
| GT 多目标治理 | 何艳玲 | 多目标张力、结构变化下的治理回应、从实践提炼分析范畴 |
| PP 政策过程 | 朱旭峰 | 行动者、渠道与可检验关系；扩散、知识与议程 |
| RS 改革次序 | 马骏 | 目标—条件—次序；制度能力与「形式上实施」的区分 |
| TA 理论适用 | 郁建兴 | 理论前提还原；结构条件 × 行动者选择；范式修正 |
| PI 执行博弈 | 丁煌 | 利益得失、偏差类型、监督与信息条件下的策略均衡、对策逐条对应阻滞环节 |

> 以上是研究动作的抽象，不代表相关学者认可本项目，也不构成对其学术观点的概括。

## 17 个 Skills

| 阶段 | Skill | 用途 |
|---|---|---|
| 路由 | `pa-router` | 判断贡献载体与当前瓶颈，只推荐最先该解决的一步 |
| 选题 | `pa-question-framer` | 从主题、现象、政策热点形成有竞争解释的研究问题 |
| 文献 | `pa-literature-mapper` | 解释路径地图、精确缺口、书目与引文支持的两次核验 |
| 理论 | `pa-concept-mechanism-builder` | 概念边界与非例、机制箭头与可观察含义 |
| 理论 | `pa-theory-localizer` | 把「中国情境」拆成改变理论前提、机制或范围的制度条件 |
| 设计 | `pa-research-design` | 案例选择、过程追踪、定量识别、混合方法的主张—证据映射 |
| 架构 | `pa-paper-architect` | 按论文体裁规划全文骨架（公共管理论文的「八股」），说明每节为什么放在那里 |
| 架构 | `pa-argument-architect` | 世界中的因果链与文本中的论证链，论文—章节—段落—句子四层嵌套 |
| 写作 | `pa-intro-drafter` | 围绕论证链写引言 |
| 写作 | `pa-section-writer` | 文献、理论、设计、分析、讨论、结论等正文 |
| 写作 | `pa-title-abstract` | 与正文结论强度一致的题目、摘要、关键词 |
| 语言 | `pa-prose-polisher` | 不改变证据与论点的中文学术语体润色 |
| 审稿 | `pa-paper-reviewer` | 投稿前结构审稿，缺陷编码 + 验收条件 |
| 审稿 | `pa-supervisor-panel` | 七个研究镜头会诊，合并成一份按依赖排序的修改计划 |
| 投稿 | `pa-journal-fit` | 依据官网与近期真实刊文的选刊与投稿适配 |
| 退修 | `pa-revision-responder` | 意见—判断—行动—位置—验收矩阵与逐条回复 |
| 蒸馏 | `pa-scholar-distiller` | 论文与导师批注的研究动作蒸馏、规则支持度与留出验证 |

## 安装

```bash
git clone https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN.git
cd PublicAdmin-Supervisor-Skills-CN
bash scripts/install.sh --target claude            # ~/.claude/skills；--target claude-project 装到当前项目
bash scripts/install.sh --dir <你的工具的 skills 目录> --link   # Codex、Qwen Code 等，以其文档为准
```

每个包含 `SKILL.md` 的目录是一个独立 Skill，参考文件都在各自的 `references/` 里，可以单独复制；不要把仓库根目录当作一个 Skill。

## 蒸馏与评测

```bash
pip install -r requirements.txt
python scripts/pa_distill.py status                   # 语料覆盖
export PA_LLM_BASE_URL=http://<host>:<port>/v1 PA_LLM_MODEL=<model>
python scripts/pa_distill.py annotate --out corpus/annotations/run1 --split train
python scripts/pa_distill.py validate corpus/annotations/run1 --write --strict
python scripts/pa_distill.py aggregate corpus/annotations/run1
python scripts/build_refs.py --write                  # 人工改完状态后重新生成 Skill 参考
python scripts/pa_distill.py holdout corpus/annotations/run1
```

完整流程见 [`distill/README.md`](distill/README.md)，评测见 [`eval/README.md`](eval/README.md)。任何 OpenAI 兼容接口都可以；没有接口时 `annotate --dry-run` 只渲染提示词，可由 Claude Code 等 Agent 按提示词完成标注，再用 `validate` 核验。

## 目录

```text
skills/        17 个自包含 Skill（SKILL.md + references/）
rules/         规则登记表（唯一真源）、机器计数结果、研究区预览
vocab/         研究动作编码本（7 族 68 码）与稿件缺陷编码（8 组 34 码）
corpus/        经核验的书目清单 papers.csv（不含全文）
distill/       标注提示词、JSON Schema、示例标注、流水线说明
eval/          评测预注册、盲评量表、盲评稿件规范
scripts/       pa_distill.py（蒸馏与评测）、build_refs.py（生成参考）、lint_skills.py、install.sh
handbook/      给人读的方法说明
tests/         单元测试与虚构教学论文
```

## 语料现状

`corpus/papers.csv` 收录 6 位学者 120 篇经网页核验的书目（何艳玲核验中），每条记录核验来源与已核实字段，已按学者分层划分训练/留出。只收元数据，不分发全文。MVP 清单中有两条条目经多轮检索找不到任何来源，已删除，详见 [`corpus/README.md`](corpus/README.md)。

## 路线图

- [x] 规则登记表：7 个研究镜头加共享核心、38 条种子规则，每条可计数、可被证伪
- [x] 编码本与缺陷编码
- [x] 6 位学者 120 篇经核验书目，已分训练/留出
- [x] 蒸馏工具链（导入、划分、标注、逐字核验、一致性、支持度、挖掘、留出验证、盲评、批注蒸馏）与 31 个单元测试
- [x] 17 个自包含 Skill；registry → Skill 的生成链，运行时只加载 validated 规则
- [x] 评测预注册与 8 维盲评量表，CI（lint、生成文件同步、单元测试）
- [ ] 何艳玲书目并入
- [ ] **全文标注：7 位学者 × 至少 15 篇 = 105 篇**，统计后淘汰或升级规则（v1.0 的前提）
- [ ] Task A 留出验证；Task B 30–50 段真实匿名稿件盲评

## 许可

内容 CC BY-NC-SA 4.0，代码 MIT，详见 [LICENSE-NOTE.md](LICENSE-NOTE.md)。架构受 [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills) 启发，内容为针对中文公共行政论文的重新撰写。
