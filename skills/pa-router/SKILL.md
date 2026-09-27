---
name: pa-router
description: Route a Chinese public administration/public management research task to the right reasoning workflow based on the paper's actual contribution and method.
---

# PA Research Router

## Trigger
用户给出选题、摘要、论文草稿或“这能不能写成公共管理论文”，需要先判断文章到底是什么类型。

## Goal
不要立刻润色。先确认论文的**主贡献载体**，再决定后续分析。

## Classify into one primary type

1. **制度逻辑 / 机制解释**：解释一个稳定、反常或反复出现的治理现象。
2. **概念 / 理论构造**：提出新概念、理想类型、分析框架或理论命题。
3. **政策过程 / 实证检验**：行动者、信息、扩散、政策选择或执行机制，有明确变量和数据。
4. **制度改革 / 政策设计**：讨论目标、条件、制度能力、改革顺序。
5. **治理范式 / 理论适用性**：修正既有理论在中国情境中的机制或边界。
6. **规范理论**：核心是价值、合法性、责任性、公正等规范论证。
7. **综述 / 学科反思**：重组已有文献或提出研究议程。

## Routing
- 问题不清楚 → `pa-question-framer`
- 概念或机制含糊 → `pa-concept-mechanism-builder`
- 有明显“西方理论 + 中国案例” → `pa-theory-localizer`
- Introduction 需要重写 → `pa-intro-drafter`
- 全文已成形 → `pa-paper-reviewer`
- 需要多角度会诊 → `pa-supervisor-panel`

## Output
只给：
- Primary type
- Secondary type（若有）
- 当前论文真正的“承重梁”
- 最大结构风险（最多 3 个）
- 下一步应该调用哪个 Skill，以及原因

不要把“数据很多”“用了新方法”自动判为贡献。
