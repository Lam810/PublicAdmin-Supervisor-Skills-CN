<div align="center">

<img src="assets/icon.svg" alt="PublicAdmin-Supervisor-Skills-CN" height="220" />

</div>

# PublicAdmin-Supervisor-Skills-CN：把中国公共管理顶尖学者的研究功夫，炼化为你的 AI 副导师。

[English](README.en.md) · 中文

<p align="center">
  <a href="https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/stargazers"><img src="https://img.shields.io/github/stars/Lam810/PublicAdmin-Supervisor-Skills-CN?style=flat-square&logo=github" alt="GitHub stars"></a>
  <a href="https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/network/members"><img src="https://img.shields.io/github/forks/Lam810/PublicAdmin-Supervisor-Skills-CN?style=flat-square&logo=github" alt="GitHub forks"></a>
  <a href="https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Lam810/PublicAdmin-Supervisor-Skills-CN/ci.yml?branch=main&style=flat-square&label=CI" alt="CI"></a>
  <a href="LICENSE-NOTE.md"><img src="https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0%20%7C%20MIT-lightgrey?style=flat-square" alt="License"></a>
</p>

## 📰 News

> - **[2026-09-27]** ✍️ **v0.3**：新增**写作架构镜头**，抽象自马亮、马啸关于论文写作与研究设计的公开主张（学术「八股文」、「小切口·大问题」、识别威胁的写法）；编码本新增 14 个写作动作，公共管理论文的「八股」第一次可以在全文中计数和验证。语料扩至 9 位学者 171 篇经核验书目。详见 [CHANGELOG](CHANGELOG.md)。
> - **[2026-09-27]** 🚀 **v0.2 公开发布**：17 个技能覆盖从选题到退修的全流程；新增丁煌研究传统（执行博弈镜头）；规则登记表、逐字核验的蒸馏工具链、评测预注册一并开源。
> - **[2026-09-27]** 🔎 核验中发现，由大模型生成的第一版书目清单里有三篇论文**查无出处**，已删除并公开记录在 [corpus/README.md](corpus/README.md)。这正是本项目坚持证据纪律的原因。

---

## 为什么做这个项目？

写中文公共管理论文，很多人卡在同样几个地方：

*   **有题目，没问题**：「数字政府对基层治理的影响研究」只是一个主题，不是研究问题；读者看不出这篇文章为什么非写不可。
*   **套理论**：「西方理论 + 中国案例 = 丰富了理论」，但说不清中国的制度条件究竟改变了理论的哪个前提、哪条机制。
*   **有材料，没机制**：访谈、台账、回归都有了，「压力导致形式主义」式的箭头中间却还是黑箱。
*   **AI 越流畅越危险**：大模型能写出漂亮的公共管理腔，也能一本正经地编出不存在的文献。我们自己的第一版书目就被编进了三篇。

这些问题背后，是公共管理研究的**「最后一公里」**：问题意识、理论对话、机制、证据、贡献。怎样把这些做好，藏在顶尖学者一篇篇论文的写法里，很少被写成可以照着执行的规则。

这个项目想做的，是把这些隐性知识**蒸馏**出来：从周雪光、周黎安、何艳玲、朱旭峰、马骏、郁建兴、丁煌等学者公开论文中反复出现的研究动作，以及马亮、马啸关于论文写作与研究设计的主张中，提炼出一套可以被大语言模型（Claude、GPT、DeepSeek、Qwen 等）执行的 **AI 技能（Skills）**。

和一般的提示词合集不同，这里的每条规则都**登记来源、可以被全文数据推翻、只有通过验证才会进入技能**。技能里不出现学者姓名，也不用来模仿任何学者说话：它们是研究动作的抽象，不代表相关学者认可本项目。

项目还在早期：17 个技能已经可以直接使用，但所有规则仍是种子假设，还没有完成全文标注与留出验证。我们会把这个过程完整公开，也欢迎同行一起标注、验证、纠错。如果这个项目对你有帮助，请点亮右上角的 ⭐ Star！

## 社区与交流

- 使用中遇到问题、发现规则不对、想补充语料，欢迎在 [Issues](https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/issues) 里提出；
- 想贡献技能、标注或评测，请先读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 教程结构

本项目采用 **Handbook（方法指南）+ Skills（可执行技能）+ 蒸馏与验证（让规则可以被证伪）** 的三轨结构：

```
PublicAdmin-Supervisor-Skills-CN/
├── README.md                           # 本文件
│
├── handbook/                           # 📖 方法指南
│   ├── 01-chinese-pa-paper-logic.md    # 第一章：中文公共管理论文的核心逻辑
│   ├── 02-distillation-protocol.md     # 第二章：从学者论文到技能的蒸馏协议
│   └── 03-writing-architecture.md      # 第三章：写作架构——「八股」与层层嵌套的论证
│
├── skills/                             # 🛠️ 17 个可执行技能（每个目录一个 SKILL.md）
│   ├── README.md                       # 技能导读：怎么选、怎么用、怎么接龙
│   ├── pa-router/                      # 路由
│   ├── pa-question-framer/             # 选题与理论阶段
│   ├── pa-literature-mapper/
│   ├── pa-concept-mechanism-builder/
│   ├── pa-theory-localizer/
│   ├── pa-research-design/
│   ├── pa-paper-architect/             # 架构阶段
│   ├── pa-argument-architect/
│   ├── pa-intro-drafter/               # 写作阶段
│   ├── pa-section-writer/
│   ├── pa-title-abstract/
│   ├── pa-prose-polisher/
│   ├── pa-paper-reviewer/              # 审稿与投稿阶段
│   ├── pa-supervisor-panel/
│   ├── pa-journal-fit/
│   ├── pa-revision-responder/
│   └── pa-scholar-distiller/           # 蒸馏
│
├── rules/                              # 🔬 规则登记表（唯一真源）与研究区预览
├── vocab/                              # 研究动作编码本与稿件缺陷编码
├── corpus/                             # 经核验的书目清单（不含全文）与写作来源
├── distill/                            # 标注提示词、JSON Schema、流水线说明
├── eval/                               # 评测预注册、盲评量表
└── scripts/                            # 蒸馏工具链、参考文件生成、结构检查、安装脚本
```

### 📖 Handbook：方法指南

| 章节 | 内容 | 链接 |
|---|---|---|
| **第一章：论文逻辑** | 一篇公共管理论文最低限度要形成的论证链；三种常见的假创新（情境替换、概念换名、方法升级）；好机制的最低构成 | [01 中文公共管理论文的核心逻辑](handbook/01-chinese-pa-paper-logic.md) |
| **第二章：蒸馏协议** | 怎样从学者的论文中识别反复出现的研究动作；什么算一条合格的「导师规则」；留出验证与发布条件 | [02 蒸馏协议](handbook/02-distillation-protocol.md) |
| **第三章：写作架构** | 公共管理论文的「八股」其实是读者依次要问的八个问题；「小切口·大问题」；研究设计怎么写；因果链与论证链的四层嵌套 | [03 写作架构](handbook/03-writing-architecture.md) |

### 🛠️ Skills：可执行的 AI 技能

这里是本仓库的核心。每个技能都是一个自包含的目录，可以安装到 Claude Code、Codex、Cursor 等 Agent 中，用自然语言触发；也可以不安装，把 `SKILL.md` 当作系统提示词或检查清单使用。完整导读见 [skills/README.md](skills/README.md)。

| 技能 | 功能描述 | 链接 |
|---|---|---|
| **研究路由** `pa-router` | 判断论文的贡献载体（机制解释、概念构造、政策过程、改革设计、理论适用、规范、综述）和当前瓶颈，只推荐最先该解决的一步 | [使用技能](skills/pa-router/SKILL.md) |
| **问题提炼** `pa-question-framer` | 把政策主题、现象或数据压成有困惑、有竞争解释、材料能回答的研究问题 | [使用技能](skills/pa-question-framer/SKILL.md) |
| **文献地图** `pa-literature-mapper` | 按解释路径而不是按作者组织文献，写出精确缺口；书目真实性与引文是否支持论断分两次核验 | [使用技能](skills/pa-literature-mapper/SKILL.md) |
| **概念与机制** `pa-concept-mechanism-builder` | 概念的必要属性、正例与非例、相邻概念比较；机制箭头的行动者、证据与最强替代机制 | [使用技能](skills/pa-concept-mechanism-builder/SKILL.md) |
| **理论本土化** `pa-theory-localizer` | 把「中国情境」拆成制度条件，判断改变的是理论的边界、关系、机制还是概念，写成可检验的条件命题 | [使用技能](skills/pa-theory-localizer/SKILL.md) |
| **研究设计** `pa-research-design` | 案例选择、过程追踪、定量识别、混合方法；主张—证据对照表与最小可行设计 | [使用技能](skills/pa-research-design/SKILL.md) |
| **论文架构** `pa-paper-architect` | 按体裁规划全文骨架（公共管理论文的「八股」），并说明每一节为什么放在那里 | [使用技能](skills/pa-paper-architect/SKILL.md) |
| **论证架构** `pa-argument-architect` | 分开世界中的因果链与文本中的论证链，在论文、章节、段落、句子四层上逐级检查 | [使用技能](skills/pa-argument-architect/SKILL.md) |
| **引言写作** `pa-intro-drafter` | 围绕论证链写引言：现象与困惑、解释路径、精确缺口、设计的区分力、与缺口对应的贡献 | [使用技能](skills/pa-intro-drafter/SKILL.md) |
| **正文写作** `pa-section-writer` | 文献、理论、设计、分析、讨论、结论与政策含义；主张—材料—推理—限定，绝不编造 | [使用技能](skills/pa-section-writer/SKILL.md) |
| **题目摘要** `pa-title-abstract` | 与正文结论强度一致的题目、摘要、关键词，中英文范围与强度一致 | [使用技能](skills/pa-title-abstract/SKILL.md) |
| **语体润色** `pa-prose-polisher` | 不改变证据、论点与引用含义的中文学术语体润色；拆公文腔与 AI 腔，不承诺检测器分数 | [使用技能](skills/pa-prose-polisher/SKILL.md) |
| **投稿前审稿** `pa-paper-reviewer` | 先审文章成不成立，再审写得顺不顺；每条问题给出位置、缺陷编码、改法与验收条件 | [使用技能](skills/pa-paper-reviewer/SKILL.md) |
| **导师组会诊** `pa-supervisor-panel` | 七个研究镜头分别诊断，再合并成一份按依赖排序、最多五项的修改计划 | [使用技能](skills/pa-supervisor-panel/SKILL.md) |
| **选刊适配** `pa-journal-fit` | 依据期刊官网、当前投稿指南与近期真实刊文比较适配度，不承诺分区与录用 | [使用技能](skills/pa-journal-fit/SKILL.md) |
| **退修回复** `pa-revision-responder` | 意见—判断—行动—修改位置—验收条件矩阵；先改稿，再写已完成式的逐条回复 | [使用技能](skills/pa-revision-responder/SKILL.md) |
| **经验蒸馏** `pa-scholar-distiller` | 从论文或匿名导师批注中蒸馏研究动作，统计规则支持度，做留出验证 | [使用技能](skills/pa-scholar-distiller/SKILL.md) |

### 🔬 这些技能的知识从哪里来

技能里的研究判断来自七个**研究镜头**和一个**写作镜头**，每个镜头抽象自一个公开研究传统：

| 镜头 | 抽象自 | 关注什么 |
|---|---|---|
| 制度逻辑 | 周雪光 | 稳定、反复、看似违背正式制度目标的现象；结构张力 → 策略 → 稳定化 |
| 概念工程 | 周黎安 | 理想类型、维度化、相邻概念逐维比较、由概念推出可反驳命题 |
| 多目标治理 | 何艳玲 | 多目标张力、结构变化下的治理回应、从实践提炼分析范畴 |
| 政策过程 | 朱旭峰 | 行动者、渠道与可检验关系；扩散、知识与议程 |
| 改革次序 | 马骏 | 目标—条件—次序；制度能力与「形式上实施」的区分 |
| 理论适用 | 郁建兴 | 理论前提还原；结构条件 × 行动者选择；范式修正 |
| 执行博弈 | 丁煌 | 利益得失、偏差类型、监督与信息条件下的策略均衡、对策逐条对应阻滞环节 |
| 写作架构 | 马亮、马啸 | 学术「八股文」、「小切口·大问题」、引言开门见山；识别威胁要点名、在不该有效应处做对照 |

规则怎样进入技能：

```text
经核验书目 → 合法全文 → 训练/留出划分 → 逐篇结构标注（逐字摘录 + 段落位置）
  → 摘录与全文逐字比对 → 标注一致性 → 训练集计数与准入门槛
  → 人工改状态 seed / candidate / validated / rejected → 生成技能参考 → 留出验证 + 真实稿件盲评
```

- 每条规则登记在 [rules/registry.yaml](rules/registry.yaml)：触发条件、下一步动作、检验方式、反模式，以及「怎样算一篇论文支持了它」。准入门槛：训练集中至少 3 篇、跨 2 个时期、在本传统中的出现率是其他传统的 1.5 倍以上。
- **技能只加载已验证的规则**；种子与候选规则放在[研究区预览](rules/preview/lens-cards-preview.md)，被推翻的规则重新生成后从技能中消失。
- 标注必须附原文逐字摘录与段落位置，程序逐字比对，对不上的不计入；评测判据在看到结果之前写进 [eval/prereg.md](eval/prereg.md)。
- 语料：9 位学者 171 篇经网页核验的书目（不含全文），第一轮全文获取清单 127 篇，见 [corpus/](corpus/README.md)。流水线见 [distill/README.md](distill/README.md)。

## 快速开始 (Quick Start)

把下面这段话发给你的 AI 助手（Claude Code、Codex、Cursor 等）即可完成安装：

```
帮我安装 https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN 仓库 skills/ 目录下的全部技能。每个包含 SKILL.md 的子目录是一个独立技能，不要把仓库根目录当作一个技能安装。
```

也可以手动安装：

```bash
git clone https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN.git
cd PublicAdmin-Supervisor-Skills-CN
bash scripts/install.sh --target claude           # 装到 ~/.claude/skills
bash scripts/install.sh --dir <你的工具的技能目录>   # Codex、Qwen Code 等，以各自文档为准
```

装好之后直接用自然语言说话，不需要记命令：

- 「这个选题能不能写成公共管理论文？」→ `pa-router`
- 「帮我把『数字政府与基层减负』提炼成一个研究问题」→ `pa-question-framer`
- 「我的文献综述像在堆作者，帮我改成解释地图」→ `pa-literature-mapper`
- 「按公共管理论文的八股帮我搭全文框架」→ `pa-paper-architect`
- 「这一段的因果论证站得住吗？为什么要这样写？」→ `pa-argument-architect`
- 「投稿前帮我审一遍」→ `pa-paper-reviewer`；「请几个导师视角一起会诊」→ `pa-supervisor-panel`
- 「这是审稿意见，帮我写修改说明」→ `pa-revision-responder`

在 Claude Code 里也可以直接输入 `/pa-question-framer` 这样的技能名。更多触发方式、推荐顺序和每个技能的详细说明，见 [skills/README.md](skills/README.md)。

## 贡献与反馈

欢迎试用、开 Issue、提 PR，也欢迎：

- 指出某条规则在某篇论文里其实不成立（附原文位置）；
- 补充经核验的书目，或在合法获取全文后贡献标注；
- 提供经作者同意、已匿名化的稿件片段，参与盲评。

提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)：技能结构、书目核验和标注都有硬性要求，并由 CI 检查。

## 致谢

- 「Handbook + 可执行 Skills」的组织方式受 HKUST(GZ) 骆昱宇团队 [Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills) 启发。本仓库内容针对中文公共管理论文重新撰写。
- 研究镜头与写作镜头抽象自上表中各位学者的公开研究。这些抽象可能有偏差，责任在本项目，不代表学者本人的观点或认可。

## TODO

- [ ] **全文标注**：第一轮 127 篇（七个研究传统各 15 篇，写作架构 22 篇），统计后淘汰或升级规则
- [ ] **Task A**：留出论文的结构预测，检验规则能否恢复顶尖论文的研究结构
- [ ] **Task B**：30–50 段真实匿名稿件的盲评，检验技能能否把稿件改好而不引入虚构
- [ ] 为每个研究传统补充若干篇「写作剖析」案例（需在全文标注之后）

## License

内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)，代码（`scripts/`、`tests/`）采用 MIT，详见 [LICENSE-NOTE.md](LICENSE-NOTE.md)。欢迎非商业用途的分享与改编，但请注明出处。
