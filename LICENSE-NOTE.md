# 许可与署名说明

- **内容**（skills/、handbook/、rules/、vocab/、corpus/ 元数据、distill/ 的提示词与 schema、eval/ 文档、README）：CC BY-NC-SA 4.0，见 `LICENSE`。
- **代码**（scripts/、tests/）：MIT，见 `LICENSE-CODE`。

## 架构来源

「Handbook + 可调用 Skills」的组织方式受 HKUST(GZ) 骆昱宇团队 [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills)（CC BY-NC-SA 4.0）启发。本仓库内容针对中文公共行政论文重新撰写，未复制其文本；如后续引入其材料，须按其许可署名并保持相同许可。

## 关于学者姓名

仓库在 README、`rules/registry.yaml` 与 `corpus/` 中出现的学者姓名，只用于说明研究动作规则**从哪些公开研究传统中抽象而来**，以及标注语料的书目来源。这不代表相关学者认可本项目，也不构成对其学术观点的概括。`skills/` 目录内不出现学者姓名，Skill 不得被用来生成「某教授本人会怎么说」。

## 语料版权

`corpus/papers.csv` 只收录书目元数据与公开来源链接，不分发任何论文全文或摘要。全文请从合法渠道（学校数据库订阅、期刊官网开放获取、作者主页）自行获取，放入被 `.gitignore` 忽略的 `corpus/fulltext/`。
