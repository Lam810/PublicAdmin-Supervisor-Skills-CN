---
name: pa-scholar-distiller
description: Distill research moves from verified papers or anonymized supervisor comments into testable rules. Use when 用户要求论文蒸馏、导师经验提炼、研究动作标注、规则支持度统计或留出验证；不模仿学者口吻。
license: CC-BY-NC-SA-4.0
---

# 研究动作蒸馏

读 [蒸馏协议](references/distillation-protocol.md)。
论文标注用 [研究动作编码本](references/move-codebook.md)；
批注路线用 [缺陷编码](references/defect-codes.md)。

这个技能可以单独指导人工标注；批量命令需要完整项目仓库，先定位仓库及其 distill/README.md，不假设当前目录拥有脚本。
没有全文、运行结果或评审者评分时，如实报告缺失；不能用题名推断出来的解释冒充全文标注。

## 路线 A：公开论文

核实书目与作者身份 → 合法全文 → 预先划分训练／留出 → 结构字段和研究动作标注 → 逐字证据核验 → 独立复核与分歧裁决 → 训练集计数 → 留出评测。
每条标注保留短摘录、段落位置、文本版本；摘录命中只证明文字存在，不证明编码解释正确。
缺失、模糊、未编码与被否定是不同状态，不能用无标注自动证明规则不成立。
规则记录触发、动作、检验、反模式、支持和反例。至少跨三篇、两个时期等门槛以当前登记表为准。

## 路线 B：导师批注

只使用获准分析的材料，以化名标记批注者和稿件，保留批注对应的论证位置。
区分稿件特定修复与可泛化判断；重复批注不重复计数，多个版本不冒充多个独立稿件。
先提炼候选规则，再用未参与提炼的稿件检验。不能把频率直接当成正确性。

## 交付

语料与缺失报告、可复查标注、候选规则及反例、支持度／一致性／评测状态、下一步最小补证方案。
状态分 seed、candidate、validated、rejected；只有实际证据达到对应条件才建议迁移。
全套规则改进不等于每条规则单独有效；没有消融或针对性验证时不逐条宣称 validated。
