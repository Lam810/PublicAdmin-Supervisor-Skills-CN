# PublicAdmin-Supervisor-Skills-CN

**把中国公共管理顶尖学者怎样发现问题、制造概念、构造机制、组织证据和提出理论贡献的隐性知识，蒸馏成可执行的 AI Skills。**

面向中文公共行政、公共管理与中国治理研究的 AI 科研副导师 Skill Pack。它不模仿任何学者的措辞，而是把公开论文中反复出现的**研究动作**提炼为可执行规则，并且给每条规则配上可以被证伪的来源与统计门槛。

> 当前版本：**v0.2.0-dev（持续升级中）**。7 个 MVP Skill 可直接使用；规则登记表、编码本、经核验的语料清单与蒸馏工具链已就位；8 个新 Skill、测试与评测文档正在补齐，见文末「路线图」。

## 设计要点

- **规则有出处，也会被淘汰。** 每条导师规则登记在 [`rules/registry.yaml`](rules/registry.yaml)，写明触发条件、Agent 下一步动作、检验方式和反模式，并用研究动作编码定义「怎样算一篇论文支持了它」。准入门槛：训练集中至少 3 篇、跨 2 个时期、在本传统中的出现率是其他传统的 1.5 倍以上。
- **目前所有规则都是 `seed`（种子假设）。** 它们来自代表作的题名、摘要与公开信息，还没有经过全文标注的交叉验证。机器只计数、出报告，状态由人来改。
- **标注不能编造证据。** 标注工具要求每个字段、每个研究动作都附原文逐字摘录与段落位置，程序会把摘录与全文逐字比对，对不上的一律不计入。
- **留出验证防泄漏。** 语料按学者分层分出 20% 留出集；参与种子规则形成的论文永远留在训练集。
- **Skill 里没有学者姓名。** 姓名只出现在 README、规则登记表和语料清单中，用于说明来源。去掉姓名后 Skill 仍须可用，否则就只是名人角色扮演。

## 七个研究镜头

| 镜头 | 抽象自 | 关注什么 |
|---|---|---|
| IL 制度逻辑 | 周雪光 | 稳定、反复、看似违背正式制度目标的现象；结构张力 → 策略 → 稳定化 |
| CE 概念工程 | 周黎安 | 理想类型、维度化、相邻概念逐维比较、由概念推出可反驳命题 |
| GT 多目标治理 | 何艳玲 | 多目标张力、结构变化下的治理回应、从实践提炼分析范畴 |
| PP 政策过程 | 朱旭峰 | 行动者、渠道与可检验关系；扩散、知识与议程 |
| RS 改革次序 | 马骏 | 目标—条件—次序；制度能力与「形式上实施」的区分 |
| TA 理论适用 | 郁建兴 | 理论前提还原；结构条件 × 行动者选择；范式修正 |
| PI 执行博弈 | 丁煌 | 利益分析、偏差类型化、监督与信息条件下的博弈均衡、对策逐条对应阻滞环节 |

> 以上是研究动作的抽象，不代表相关学者认可本项目，也不构成对其学术观点的概括。

## 现有 Skills

| Skill | 用途 |
|---|---|
| `pa-router` | 判断论文类型与「承重梁」，决定下一步调用哪个 Skill |
| `pa-question-framer` | 把主题、现象、政策热点压成真正的研究困惑与问题 |
| `pa-concept-mechanism-builder` | 概念构造、机制链与可观察含义 |
| `pa-theory-localizer` | 修复「西方理论 + 中国案例」式的套理论问题 |
| `pa-intro-drafter` | 按中文公共管理论文逻辑重构或撰写引言 |
| `pa-paper-reviewer` | 投稿前结构化审稿，先抓致命问题 |
| `pa-supervisor-panel` | 多个研究镜头并行会诊，再由总编辑合并修改路线 |

正在补齐：`pa-literature-mapper`（文献地图与引用核验）、`pa-research-design`（案例选择、过程追踪、识别策略）、`pa-section-writer`（正文各节）、`pa-title-abstract`（题目摘要关键词）、`pa-prose-polisher`（中文学术语体）、`pa-journal-fit`（期刊画像）、`pa-revision-responder`（退修与审稿回复）、`pa-scholar-distiller`（蒸馏执行）。

## 目录

```text
skills/        可调用的 Skill（每个目录一个 SKILL.md）
rules/         导师规则登记表（唯一真源）
vocab/         研究动作编码本（7 族 68 码）与稿件缺陷编码（8 组 34 码）
corpus/        经核验的书目清单 papers.csv（不含全文）
distill/       标注提示词与 JSON Schema
scripts/       蒸馏工具链 pa_distill.py 及其库
handbook/      给人读的方法说明
references/    MVP 版的镜头卡与证据规则
tests/         测试夹具（虚构教学论文）
```

## 安装 Skill

把 `skills/` 下的各个目录复制或软链到你的 Agent 的 skills 目录，例如 Claude Code 的 `~/.claude/skills/` 或项目内 `.claude/skills/`；Codex、Qwen Code 等工具以其文档规定的 skills 目录为准。每个包含 `SKILL.md` 的目录是一个独立 Skill，不要把仓库根目录当作一个 Skill 安装。

## 蒸馏工具链快速上手

```bash
pip install -r requirements.txt
python scripts/pa_distill.py status                        # 语料覆盖
# 全文放入 corpus/fulltext/<paper_id>.txt 之后：
export PA_LLM_BASE_URL=http://<host>:<port>/v1 PA_LLM_MODEL=<model>
python scripts/pa_distill.py annotate --out corpus/annotations/run1 --split train
python scripts/pa_distill.py validate corpus/annotations/run1 --write --strict   # 逐字核验证据
python scripts/pa_distill.py aggregate corpus/annotations/run1                   # 规则支持度报告
python scripts/pa_distill.py holdout corpus/annotations/run1                     # 留出验证
```

任何 OpenAI 兼容的接口都可以（vLLM、SGLang、各类云服务）。没有接口时，`annotate --dry-run` 只渲染提示词，可以让 Claude Code 等 Agent 直接按提示词完成标注，再用 `validate` 核验。

## 路线图

- [x] 规则登记表：7 个研究镜头加共享核心、38 条种子规则，每条可计数、可被证伪
- [x] 编码本与缺陷编码
- [x] 语料：6 位学者 120 篇经核验的书目元数据，已分好训练/留出（何艳玲核验中）
- [x] 蒸馏工具链：导入、分集、标注、逐字核验、一致性、支持度、挖掘、留出验证、盲评、批注蒸馏
- [ ] 8 个新 Skill，并把 7 个 MVP Skill 升级为「SKILL.md + references/」结构
- [ ] 单元测试、Skill 结构 lint、共享参考文件同步检查、CI
- [ ] 评测预注册（成功与失败判据）与盲评量表
- [ ] 全文标注：7 位学者 × 15 篇起步，统计后淘汰或强化规则（v1.0 的前提）

## 许可

内容 CC BY-NC-SA 4.0，代码 MIT，详见 [LICENSE-NOTE.md](LICENSE-NOTE.md)。架构受 [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills) 启发，内容为针对中文公共行政论文的重新撰写。
