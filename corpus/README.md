# 语料登记表（corpus/）

`papers.csv` 是蒸馏语料的书目登记表：**只有元数据与公开来源链接，不含任何全文或摘要。**

## 当前规模（2026-09-27）

| 学者键 | 研究传统（镜头） | 篇数 | 训练 / 留出 |
|---|---|---|---|
| ZXG | 周雪光（制度逻辑） | 20 | 16 / 4 |
| ZLA | 周黎安（概念工程） | 25 | 20 / 5 |
| ZXF | 朱旭峰（政策过程） | 16 | 13 / 3 |
| MJ | 马骏（改革次序） | 26 | 21 / 5 |
| YJX | 郁建兴（理论适用） | 15 | 12 / 3 |
| DH | 丁煌（执行博弈） | 18 | 14 / 4 |
| HYL | 何艳玲（多目标治理） | 核验中 | — |

每条记录都至少有一个检索到的网页同时显示题名、作者、刊名与年份（`verify_status=verified`），或在 `notes` 中写明缺哪一项（`partial`）。核验来源记在 `source_url`，被核实的字段记在 `verified_fields`。

## 字段

| 字段 | 含义 |
|---|---|
| paper_id | `学者键-年份-序号`，一经分配不再改变 |
| author_role | sole / first / co |
| paper_type | concept / theory / case / historical / quant / review / mixed（按题名与来源的初判，标注时以全文为准） |
| period | ≤2009 / 2010-2015 / 2016-2020 / 2021-2026 |
| verify_status | verified / partial / db-export（从 CNKI 等数据库导出） |
| seed_source | 1 = 该文参与了种子规则的形成，**永远留在训练集**，避免规则来源泄漏进留出验证 |
| split | train / heldout，由 `pa_distill.py split` 按学者分层、确定性、粘性地分配（新增论文不会打乱已有分配） |
| fulltext | 可选：全文相对路径；留空时默认找 `corpus/fulltext/<paper_id>.txt|.md|.pdf` |

## 已移除的条目

MVP 版清单中有两条郁建兴的条目经多轮检索**无法找到任何来源**，已删除，也不再作为任何规则的依据：

- 《迈向精准治理：后小康时代中国农业农村的再出发》，《公共管理学报》2022(3)
- 《从"督促"到"支持"：数字时代的纵向政府治理范式转型》，《江淮论坛》2026(1)

## 如何扩充

1. 在 CNKI / 万方检索作者，导出 RIS 或 EndNote 格式；
2. `python scripts/pa_distill.py import export.ris --format ris --scholar ZXG --scholar-name 周雪光`（按题名去重，导出的摘要写入被忽略的 `corpus/abstracts/`）；
3. `python scripts/pa_distill.py split`，为新论文分配训练/留出；
4. 从合法渠道获取全文，存为 `corpus/fulltext/<paper_id>.txt`（被 `.gitignore` 忽略，不会进入仓库）；
5. `python scripts/pa_distill.py status` 查看覆盖情况。

多数条目缺页码；公开引用前请在 CNKI 逐条复核。
