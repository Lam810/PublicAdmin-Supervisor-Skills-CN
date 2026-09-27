<div align="center">

<img src="assets/icon.svg" alt="PublicAdmin-Supervisor-Skills-CN" height="220" />

</div>

# PublicAdmin-Supervisor-Skills-CN: the research craft of leading Chinese public-administration scholars, distilled into your AI co-supervisor.

English · [中文](README.md)

<p align="center">
  <a href="https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/stargazers"><img src="https://img.shields.io/github/stars/Lam810/PublicAdmin-Supervisor-Skills-CN?style=flat-square&logo=github" alt="GitHub stars"></a>
  <a href="https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/network/members"><img src="https://img.shields.io/github/forks/Lam810/PublicAdmin-Supervisor-Skills-CN?style=flat-square&logo=github" alt="GitHub forks"></a>
  <a href="https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Lam810/PublicAdmin-Supervisor-Skills-CN/ci.yml?branch=main&style=flat-square&label=CI" alt="CI"></a>
  <a href="LICENSE-NOTE.md"><img src="https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0%20%7C%20MIT-lightgrey?style=flat-square" alt="License"></a>
</p>

## 📰 News

> - **[2026-09-27]** ✍️ **v0.3**: a **writing-architecture lens** abstracted from Ma Liang's and Ma Xiao's published advice on paper writing and research design ("small cut, big question", the canonical sections of an empirical paper, how to write up identification threats), plus 14 writing-move codes so that the conventional structure of a public-administration paper can be counted and validated in full texts. The corpus now lists 171 verified records from 9 scholars. See the [CHANGELOG](CHANGELOG.md).
> - **[2026-09-27]** 🚀 **v0.2, first public release**: 17 skills from topic to revision; a new policy-implementation lens (Ding Huang); the rule registry, the verbatim-quote distillation harness and the evaluation pre-registration are all open.
> - **[2026-09-27]** 🔎 Verification found three papers in the model-generated first draft of our bibliography that **do not exist**. They are removed and documented in [corpus/README.md](corpus/README.md), which is exactly why this project insists on evidence discipline.

---

## Why this project?

Writing a Chinese public-administration paper, many researchers get stuck in the same places:

*   **A topic, not a question**: "the impact of digital government on grassroots governance" is a subject, not a puzzle.
*   **Borrowed theory**: "Western theory + a Chinese case = an enriched theory", without saying which premise or mechanism the Chinese institutional setting actually changes.
*   **Material without mechanism**: interviews, ledgers and regressions, but the arrow in "pressure causes formalism" is still a black box.
*   **Fluent AI is dangerous AI**: large models write convincing academic Chinese and invent references with a straight face. Our own first bibliography contained three.

Behind these sits the "last mile" of public-administration research: problem consciousness, theoretical dialogue, mechanism, evidence and contribution. How to do them well is embedded in how leading scholars write, and rarely written down as rules one can follow.

This project distils that tacit knowledge. From research moves that recur across the published papers of Zhou Xueguang, Zhou Li-An, He Yanling, Zhu Xufeng, Ma Jun, Yu Jianxing and Ding Huang, and from Ma Liang's and Ma Xiao's advice on writing and research design, it builds **AI skills** that large language models (Claude, GPT, DeepSeek, Qwen and others) can execute.

Unlike a prompt collection, every rule here **records its sources, can be overturned by full-text data, and enters a skill only after validation**. Skills contain no scholar names and must not be used to imitate anyone: the lenses are abstractions of research moves and do not imply endorsement by the scholars concerned.

The project is early. The 17 skills are usable today, but every rule is still a seed hypothesis awaiting full-text annotation and held-out validation. The whole process is public, and colleagues are welcome to annotate, validate and correct. If this helps you, please star the repository.

## Community

- Questions, rules that look wrong, corpus additions: open an [issue](https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN/issues).
- To contribute skills, annotations or evaluation, read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## Structure

Three tracks: **Handbook** (method), **Skills** (executable), **Distillation and validation** (making rules falsifiable).

```
PublicAdmin-Supervisor-Skills-CN/
├── handbook/                           # 📖 Method (Chinese)
│   ├── 01-chinese-pa-paper-logic.md    # the argument chain of a PA paper
│   ├── 02-distillation-protocol.md     # from scholars' papers to skills
│   └── 03-writing-architecture.md      # the "eight-legged" structure and nested arguments
├── skills/                             # 🛠️ 17 self-contained skills (SKILL.md each), guide in skills/README.md
├── rules/                              # 🔬 rule registry (single source of truth) and research preview
├── vocab/                              # research-move codebook and manuscript defect codes
├── corpus/                             # verified bibliography (no full texts) and writing sources
├── distill/                            # annotation prompts, JSON schema, pipeline guide
├── eval/                               # pre-registration and blind-rating rubric
└── scripts/                            # distillation harness, reference generator, linter, installer
```

### 📖 Handbook

| Chapter | Content | Link |
|---|---|---|
| **1. Paper logic** | the minimum argument chain of a PA paper; three fake novelties (context swap, concept renaming, method upgrade); what a mechanism needs | [01](handbook/01-chinese-pa-paper-logic.md) |
| **2. Distillation protocol** | how recurring research moves are identified; what counts as a supervisor rule; validation and release criteria | [02](handbook/02-distillation-protocol.md) |
| **3. Writing architecture** | the conventional structure as eight reader questions; small cut, big question; writing up research design; causal and argumentative chains on four levels | [03](handbook/03-writing-architecture.md) |

### 🛠️ Skills

| Skill | What it does | Link |
|---|---|---|
| **Router** `pa-router` | identifies the paper's contribution type and current bottleneck; recommends only the next step | [Use](skills/pa-router/SKILL.md) |
| **Question framer** `pa-question-framer` | turns a policy topic, phenomenon or dataset into a puzzle-driven research question with rival explanations | [Use](skills/pa-question-framer/SKILL.md) |
| **Literature mapper** `pa-literature-mapper` | groups literature by explanation, states a precise gap, verifies both that citations exist and that they support the claim | [Use](skills/pa-literature-mapper/SKILL.md) |
| **Concepts and mechanisms** `pa-concept-mechanism-builder` | necessary attributes, examples and non-examples, neighbouring concepts; mechanism arrows with actors, evidence and rival mechanisms | [Use](skills/pa-concept-mechanism-builder/SKILL.md) |
| **Theory localizer** `pa-theory-localizer` | turns "the Chinese context" into institutional conditions and states whether they change a theory's scope, relationships, mechanisms or concepts | [Use](skills/pa-theory-localizer/SKILL.md) |
| **Research design** `pa-research-design` | case selection, process tracing, quantitative identification, mixed methods; claim-evidence tables and a minimum viable design | [Use](skills/pa-research-design/SKILL.md) |
| **Paper architect** `pa-paper-architect` | genre-specific paper blueprints, explaining why each section sits where it does | [Use](skills/pa-paper-architect/SKILL.md) |
| **Argument architect** `pa-argument-architect` | separates the causal chain in the world from the argumentative chain in the text, checked at paper, section, paragraph and sentence level | [Use](skills/pa-argument-architect/SKILL.md) |
| **Introduction drafter** `pa-intro-drafter` | writes introductions around the argument chain | [Use](skills/pa-intro-drafter/SKILL.md) |
| **Section writer** `pa-section-writer` | literature, theory, design, analysis, discussion and conclusion sections; never invents evidence | [Use](skills/pa-section-writer/SKILL.md) |
| **Title and abstract** `pa-title-abstract` | titles, abstracts and keywords whose claims match the paper, consistent across Chinese and English | [Use](skills/pa-title-abstract/SKILL.md) |
| **Prose polisher** `pa-prose-polisher` | meaning-preserving polishing of academic Chinese; removes officialese and AI tone | [Use](skills/pa-prose-polisher/SKILL.md) |
| **Paper reviewer** `pa-paper-reviewer` | pre-submission structural review with defect codes, fixes and acceptance criteria | [Use](skills/pa-paper-reviewer/SKILL.md) |
| **Supervisor panel** `pa-supervisor-panel` | seven research lenses diagnose separately, then merge into one dependency-ordered revision plan | [Use](skills/pa-supervisor-panel/SKILL.md) |
| **Journal fit** `pa-journal-fit` | compares fit using journal websites, current author guidelines and recent articles | [Use](skills/pa-journal-fit/SKILL.md) |
| **Revision responder** `pa-revision-responder` | comment-decision-action-location-criterion matrix and point-by-point responses written after the revisions are made | [Use](skills/pa-revision-responder/SKILL.md) |
| **Scholar distiller** `pa-scholar-distiller` | distils research moves from papers or anonymised supervisor comments; rule support and held-out validation | [Use](skills/pa-scholar-distiller/SKILL.md) |

### 🔬 Where the knowledge comes from

| Lens | Abstracted from | Focus |
|---|---|---|
| Institutional logic | Zhou Xueguang | stable, recurring behaviour that contradicts formal goals; structural tension → strategy → stabilisation |
| Concept engineering | Zhou Li-An | ideal types, dimensions, dimension-by-dimension contrasts, refutable propositions |
| Multi-goal governance | He Yanling | tensions among goals; governance responses to structural change; categories from practice |
| Policy process | Zhu Xufeng | actors, channels and testable relationships; diffusion, knowledge and agenda setting |
| Reform sequencing | Ma Jun | goals, conditions and sequence; institutional capacity versus formal adoption |
| Theory applicability | Yu Jianxing | reconstructing a theory's premises; structural conditions × actors' choices; paradigm revision |
| Implementation games | Ding Huang | interests, deviation types, equilibria under supervision and information, remedies mapped to obstruction links |
| Writing architecture | Ma Liang, Ma Xiao | canonical sections, small cut and big question, direct introductions; naming identification threats and placebo-style contrasts |

Every rule lives in [rules/registry.yaml](rules/registry.yaml) with a trigger, an action, a check, an anti-pattern and a countable definition. Admission requires support in at least 3 training papers across 2 periods and a lift of at least 1.5 over other traditions. **Skills load validated rules only**; seeds and candidates stay in the [research preview](rules/preview/lens-cards-preview.md). Annotations must quote the paper verbatim with paragraph locators, and quotes are checked against the full text. Evaluation criteria are pre-registered in [eval/prereg.md](eval/prereg.md). See [distill/README.md](distill/README.md) for the pipeline.

## Quick start

Send this to your AI assistant (Claude Code, Codex, Cursor, …):

```
Help me install every skill under the skills/ directory of https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN. Treat each directory containing SKILL.md as a separate skill; do not install the repository root as one skill.
```

Or install manually:

```bash
git clone https://github.com/Lam810/PublicAdmin-Supervisor-Skills-CN.git
cd PublicAdmin-Supervisor-Skills-CN
bash scripts/install.sh --target claude            # ~/.claude/skills
bash scripts/install.sh --dir <your tool's skills directory>
```

Then just talk, in Chinese or English: "Can this topic become a public-administration paper?" → `pa-router`; "Turn this topic into a research question" → `pa-question-framer`; "Lay out the paper following the conventional structure" → `pa-paper-architect`; "Review this before I submit" → `pa-paper-reviewer`. In Claude Code you can also type `/pa-question-framer`. The full guide is in [skills/README.en.md](skills/README.en.md). The skills produce Chinese output by default because they target Chinese-language journals.

## Contributing

Issues and pull requests are welcome, especially: a rule that fails in a specific paper (with the passage), verified bibliographic records, annotations of legally obtained full texts, and anonymised manuscript excerpts (with the author's consent) for blind evaluation. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Acknowledgements

- The "handbook + executable skills" layout is inspired by [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills) by Yuyu Luo's team at HKUST(GZ). Content here is written anew for Chinese public-administration papers.
- The lenses are abstracted from the published work of the scholars listed above. Any distortion is this project's responsibility and does not represent their views or endorsement.

## TODO

- [ ] Full-text annotation of the first 127 papers; demote or promote rules accordingly
- [ ] Task A: held-out structure prediction
- [ ] Task B: blind rating on 30–50 real, anonymised manuscripts

## License

Content: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Code (`scripts/`, `tests/`): MIT. See [LICENSE-NOTE.md](LICENSE-NOTE.md).
