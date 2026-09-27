# 蒸馏流水线（distill/）

从「经核验的书目」到「可进入 Skill 的规则」的完整流程。所有命令都在仓库根目录运行，只依赖 Python 3.10+ 与 PyYAML。

```text
书目核验 → 合法全文 → 训练/留出划分 → 逐篇标注 → 逐字核验 → 一致性检验
        → 训练集计数与准入 → 人工改状态 → build_refs 生成 Skill 参考 → 留出验证 / 盲评
```

每一步的产物不同，不能互相冒充：**书目核验 ≠ 读过全文 ≠ 标注正确 ≠ 规则有效。**

## 目录

| 路径 | 内容 |
|---|---|
| `prompts/annotate_paper.md` | 逐篇标注提示词（逐字摘录 + 段落位置，禁止使用外部记忆） |
| `prompts/holdout_predict.md` | Task A 结构预测提示词 |
| `schema/annotation.schema.json` | 标注 JSON Schema（20 个字段 + 研究动作） |
| `schema/comment.schema.json` | 导师批注记录（路线 B） |
| `templates/annotation.example.json` | 虚构教学论文的完整标注示例，被单元测试用来验证核验闸门 |

## 1. 语料

```bash
python scripts/pa_distill.py status                     # 各学者篇数、核验、全文、划分、时期覆盖
python scripts/pa_distill.py import cnki.ris --format ris --scholar ZXG --scholar-name 周雪光
python scripts/pa_distill.py split                      # 粘性、按学者分层；seed_source=1 永远在训练集
```

全文放 `corpus/fulltext/<paper_id>.txt`（或 .md/.pdf；PDF 需要 `pip install pypdf`）。该目录被 `.gitignore` 忽略。

## 2. 标注

```bash
export PA_LLM_BASE_URL=http://<host>:<port>/v1
export PA_LLM_MODEL=<served-model-name>
export PA_LLM_API_KEY=<可选>
python scripts/pa_distill.py annotate --out corpus/annotations/run1 --split train --workers 2
```

- 任何 OpenAI 兼容接口都可以；Qwen3 一类推理模型建议关闭思考：`--extra-body '{"chat_template_kwargs":{"enable_thinking":false}}'`。
- 超过 `--max-chars`（默认 6 万字）的全文会**报错而不是静默截断**；确需截断用 `--allow-truncate`，截断会写进标注的 `meta`。
- 输出无效 JSON 或出现编码本外的编码时自动带错误信息重试（最多 3 次），原始回复存于 `_raw/`。
- 同一提示词与同一全文已标注过会跳过；`--force` 强制重跑。
- **Agent 模式**：没有接口时 `--dry-run` 把渲染好的提示词写到 `<out>/_prompts/`，由 Claude Code 等 Agent 逐篇读提示词写出 JSON，再进入第 3 步核验。

## 3. 核验（防编造闸门）

```bash
python scripts/pa_distill.py validate corpus/annotations/run1 --write --strict -v
```

- 检查 JSON Schema、编码是否在编码本中、每条摘录是否逐字出现在全文（归一化空白、全半角标点与脚注符号后）。
- 摘录对不上的字段或动作不计入统计；逐字命中率低于 `--min-hit-rate`（默认 0.9）整篇判为不通过。
- `--write` 把核验结果写入每篇标注的 `meta.verification`；后续统计只认这个印记。
- 逐字命中只证明文字存在，不证明编码解释正确：计数之前还要人工抽查语义。

## 4. 一致性

```bash
python scripts/pa_distill.py agree corpus/annotations/human_A corpus/annotations/run1
```

按族计算 Cohen's κ；低于 0.6 的族先修订编码本定义，再重标校准集。同一个模型重复调用不等于独立复核，至少一名标注者应为人。

## 5. 计数、准入与挖掘

```bash
python scripts/pa_distill.py aggregate corpus/annotations/run1   # → rules/support.json + rules/support-report.md
python scripts/pa_distill.py mine corpus/annotations/run1        # 高频研究动作组合，供起草新规则参考
```

只计训练集、只计通过核验的论文。准入门槛写在 `rules/registry.yaml` 的 `admission`。机器只输出建议（candidate / rejected / insufficient_data），**状态由人改**：编辑 `registry.yaml`，提交说明里引用报告。

## 6. 生成 Skill 参考

```bash
python scripts/build_refs.py --write
```

只有 `build.runtime_statuses`（默认只有 `validated`）的规则进入 `skills/pa-supervisor-panel/references/lens-cards.md`；seed 与 candidate 只出现在 `rules/preview/lens-cards-preview.md`；rejected 永不渲染。规则被打成 rejected 后重新 build，它就从 Skill 中消失。

## 7. 验证

见 `eval/README.md` 与 `eval/prereg.md`：Task A 留出集结构预测，Task B 真实稿件盲评。

## 路线 B：导师批注

把获准分析的批注按 `schema/comment.schema.json` 记为 JSONL（批注者与稿件用化名），然后：

```bash
python scripts/pa_distill.py comments comments.jsonl --min-comments 3 --min-drafts 2
```

候选规则仍要在未参与提炼的稿件上检验；出现频率高不等于判断正确。
