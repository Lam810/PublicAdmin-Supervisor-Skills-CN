---
name: pa-prose-polisher
description: Polish Chinese academic prose without changing evidence, arguments or citation meaning. Use when 用户要求公共管理论文语言润色、降AI味、学术表达、精简段落或中译中改写；不自动扩展成结构审稿。
license: CC-BY-NC-SA-4.0
---

# 中文学术语体润色

读 [语体约束](references/prose-guardrails.md) 与 [证据纪律](references/evidence-discipline.md)。

默认保留论点、因果强度、概念、事实、数值、引用指向和作者立场。
优先修复主语缺失、名词堆叠、长串递进、指代不明、重复与空泛评价。
每次重写检查行动者、行为、条件、证据是否更清楚。

遇到逻辑缺口可以在正文外提示，并给谨慎的局部表达；不要因发现理论问题就拒绝用户已经明确要求的语言修改。
不把“相关”升为“导致”，不把局部观察扩成普遍规律，不替换引文内部文字。
含义可能变化时保留原意，说明歧义；不要猜一个新理论来消除歧义。

## 交付

默认交付润色后的完整目标文本，另简列实质调整。
只有用户需要时给逐句对照或多版本。不能承诺检测器分数、录用或“绝无AI痕迹”。
