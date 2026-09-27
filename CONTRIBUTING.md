# 贡献指南

欢迎 Issue、PR 与讨论。提交前请读完本文；下面标注「CI」的条目会被自动检查，不通过的 PR 无法合并。

## 可以贡献什么

| 类型 | 说明 |
|---|---|
| 反例 | 某条规则在某篇论文里不成立：给出论文书目、原文位置与理由，开 Issue 即可 |
| 书目 | 补充某个研究传统的论文，必须满足下文的核验要求 |
| 标注 | 在合法获取全文后，按编码本标注论文的研究动作 |
| 盲评稿件 | 经作者书面同意、已匿名化的稿件片段，见 `eval/blind_revision_set/README.md` |
| 技能 | 修订现有技能，或提议新技能（新技能请先开 Issue 讨论，确认它填补了现有技能没有覆盖的缺口） |

## 技能的硬性约定

每个技能是 `skills/<name>/` 下的一个自包含目录：`SKILL.md`，以及按需加载的 `references/*.md`。

- **CI**：`SKILL.md` 有合法的 YAML frontmatter，包含 `name`（与目录名一致，小写短横线）、`description`、`license`；
- **CI**：`description` 长度 80–1024 字符，含英文「Use when」从句和中文触发词（让 Agent 在中文请求下也能命中）；
- **CI**：`SKILL.md` 正文不超过 500 行；
- **CI**：`SKILL.md` 中提到的每个 `references/*.md` 都存在，`references/` 中的每个文件都在 `SKILL.md` 中被提到（没被提到的文件永远不会被加载）；
- **CI**：参考文件只有一层，参考文件之间不互相指向；超过 100 行的参考文件在前 25 行内有「## 目录」；
- **CI**：`skills/` 下任何文件都不得出现学者姓名。技能必须在不知道规则来源的情况下也能工作，也不得诱导模型扮演具体学者；
- **CI**：不得留下 TODO、TBD、XXX、「待补充」之类的占位符；
- 技能写的是工作流与闸门，不手写「某学者会怎么做」的规则；研究判断统一登记在 `rules/registry.yaml`。

### 共享与生成的参考文件

有些参考文件被多个技能使用。为保证每个技能目录可以单独复制，它们在各技能中各有一份：

- **共享文件**（如证据纪律、语体约束、论证链）：只改规范文件（文件头写着 CANONICAL），然后运行 `python scripts/build_refs.py --write` 同步到各副本；
- **生成文件**（镜头卡、编码本、缺陷编码、写作架构卡）：由 `rules/` 与 `vocab/` 生成，不要手改；
- **CI**：`python scripts/build_refs.py --check` 保证所有副本与生成文件是最新的。

## 规则

- 规则只在 `rules/registry.yaml` 中增改。每条规则要写触发、动作、检验、反模式，以及用研究动作编码写成的 `requires`（可计数定义）。
- 新规则一律从 `seed` 开始。状态变更（seed → candidate → validated，或 → rejected）由人完成，并在 PR 说明中引用 `pa_distill.py aggregate` 生成的支持度报告；升为 `validated` 还需要 `eval/prereg.md` 规定的验证证据。
- `candidate_sources` 是在标注之前登记的预测，只能列训练集论文，登记后不要为了「命中」而事后修改。

## 书目

- 每条记录必须有一个你实际看到的网页，同时显示题名、作者、刊名与年份，记为 `source_url`；在 `verified_fields` 中如实写出该页证实了哪些字段。
- **绝不凭记忆补全**作者顺序、刊名、期号或页码；证实不了的字段留空，并在 `notes` 中说明。
- 注意同名学者，必要时写明如何排除。
- 只提交元数据。**不要提交论文全文或摘要**，`corpus/fulltext/`、`corpus/abstracts/` 已被忽略。
- 新增论文后运行 `python scripts/pa_distill.py split`：已有的训练/留出划分不会变，新论文按比例分配。

## 标注

- 按 `distill/prompts/annotate_paper.md` 与编码本标注，每个 `present` 字段和每个研究动作都附 8–80 字的逐字摘录与段落位置；
- 提交前运行 `python scripts/pa_distill.py validate <目录> --write --strict`，逐字核验必须通过；
- 至少一部分论文需要两名独立标注者（至少一名为人），用 `pa_distill.py agree` 报告一致性；
- 标注文件默认不进入公开仓库（含原文摘录）。如需公开，请先确认摘录长度与版权。

## 评测

`eval/prereg.md` 在看到任何留出结果之前登记。需要修改时，在文末「变更记录」中写明日期、内容与理由；已跑出的结果照常报告，不得因为结果不理想而修改判据后重跑。

## 本地检查

```bash
python -m pip install -r requirements.txt
python scripts/lint_skills.py
python scripts/build_refs.py --check
python -m unittest discover -s tests -v
```

这三步与 CI 完全一致。

## 许可

提交即表示你同意贡献内容以 CC BY-NC-SA 4.0（内容）或 MIT（`scripts/`、`tests/` 中的代码）授权，见 [LICENSE-NOTE.md](LICENSE-NOTE.md)。
