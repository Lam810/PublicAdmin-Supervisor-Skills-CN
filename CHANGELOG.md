# 更新记录

## v0.2.0-dev（2026-09-27）

### 规则与语料
- 新增 `rules/registry.yaml`：7 个研究镜头（新增执行博弈镜头 PI）加共享核心，38 条规则，每条带触发、动作、检验、反模式、可计数定义与状态；全部为 `seed`。
- 新增 `vocab/research-moves.yaml`（7 族 68 码）与 `vocab/defects.yaml`（8 组 34 码）。
- 新增 `corpus/papers.csv`：7 位学者 138 篇经网页核验的书目元数据，按学者分层的粘性训练/留出划分（110 / 28），形成种子规则的论文固定在训练集；`corpus/fulltext-plan.csv` 第一轮 105 篇全文获取清单。
- 删除 MVP 清单中三条无法找到任何来源的条目，更正一条、补全两条（见 `corpus/README.md`）。
- 29 + 4 条传统特有规则在全文标注前登记了预测来源论文，`aggregate` 报告预测命中率。

### Skills
- 17 个 Skill 全部改为「简短工作流 + 自包含 references/」结构，描述中带中文触发词。
- 新增 8 个：文献地图、研究设计、正文写作、题目摘要、语体润色、选刊适配、退修回复、研究动作蒸馏。
- 新增 `pa-paper-architect`（按体裁规划全文骨架，即公共管理论文的「八股」，并说明每节为什么放在那里）与 `pa-argument-architect`（世界中的因果链与文本中的论证链，四层嵌套）。
- Skill 不再手写镜头规则：`scripts/build_refs.py` 从登记表生成镜头卡，运行时只加载 `validated` 规则；seed 与 candidate 进入 `rules/preview/`。

### 工具与评测
- `scripts/pa_distill.py`：导入（RIS/EndNote）、划分、状态、标注（OpenAI 兼容接口）、逐字核验、Cohen's κ、支持度与准入、组合挖掘、Task A 留出验证、Task B 盲评、导师批注蒸馏。
- Task B 采用 8 个维度，其中「未过度理论化」「事实可靠」与捏造率做非劣检验。
- 新增 `eval/prereg.md`（预注册）、`eval/rubric.md`（量表）、`eval/blind_revision_set/README.md`（稿件规范）。
- 新增 `scripts/lint_skills.py`（含 skills/ 禁止出现学者姓名）、`scripts/build_refs.py --check`、`scripts/install.sh`、34 个单元测试与 GitHub Actions CI。
- 许可：内容 CC BY-NC-SA 4.0，代码 MIT。

## v0.1.0（未公开）

由 ChatGPT 生成的 MVP：7 个 Skill、handbook 两章、6 组学者研究传统卡片与种子书目清单。
