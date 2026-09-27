# Skills: a reader's guide

English · [中文](README.md)

Seventeen skills cover a Chinese public-administration paper from topic to revision. Read them as checklists without installing anything, or install them as Agent Skills and trigger them in plain language. The skills write in Chinese by default, because they target Chinese-language journals.

| Entry | Reader | Purpose |
|---|---|---|
| [README.en.md](../README.en.md) | first-time visitors | why, what, how to install, where the knowledge comes from |
| [handbook/](../handbook/) | readers who want the method (Chinese) | paper logic, distillation protocol, writing architecture |
| **this file** | people who want to start | what each skill does, when to use it, what comes next |
| `SKILL.md` in each directory | the agent | executable instructions, gates and output formats |

## Three paths

**Empirical papers** (mechanism explanation, case studies, effect estimation): `pa-question-framer` → `pa-literature-mapper` → `pa-concept-mechanism-builder` → `pa-research-design` → `pa-paper-architect` → `pa-intro-drafter` and `pa-section-writer` → `pa-title-abstract` → `pa-prose-polisher` → `pa-paper-reviewer` and `pa-supervisor-panel`.

**Concept and theory papers** (concept building, theory applicability, normative arguments, reviews): `pa-question-framer` → `pa-concept-mechanism-builder` or `pa-theory-localizer` → `pa-paper-architect` → writing and review as above. Normative papers are not forced into empirical puzzles, and reviews are not forced into causal mechanisms.

**After submission**: `pa-journal-fit` → `pa-revision-responder`.

Two cross-cutting skills: `pa-argument-architect`, usable whenever a causal chain or the order of sections cannot be justified, and `pa-scholar-distiller`, for maintainers and researchers rather than for everyday writing. Start with `pa-router` if you are unsure where you are.

## The seventeen skills

| Skill | Use it when | Key discipline | Output |
|---|---|---|---|
| `pa-router` | you have a topic, abstract or draft and need the route | recommends only the first bottleneck; no contribution from novelty or data volume alone | main type, load-bearing judgement, ≤3 risks, next step |
| `pa-question-framer` | you have a topic but no puzzle | describe the phenomenon neutrally; check that the anomaly is real; no invented theory to argue against | phenomenon → expectation → puzzle → question → rivals → minimum evidence |
| `pa-literature-mapper` | reviewing literature or checking citations | record the search; bibliographic existence and claim support are two checks; unverified items stay out of the reference list | explanation map, gaps, citation verification table |
| `pa-concept-mechanism-builder` | a new concept or an arrow nobody believes | necessary attributes, non-examples, neighbouring concepts; evidence and a rival for every arrow | concept card, arrow table, weakest link |
| `pa-theory-localizer` | "the Chinese context extends theory X" with no specifics | reconstruct the theory fairly; translate context into institutional conditions; "existing theory already explains it" is allowed | revision type, conditional proposition, one safe and one overclaiming sentence |
| `pa-research-design` | selecting cases, operationalising, worrying about identification | name a rival and the observation that separates it; planned work is written as a plan; method citations from a verified list | claim-evidence table, case or sample plan, threats and remedies |
| `pa-paper-architect` | "lay out the paper", "what goes in each section" | the convention is a set of reader questions, not fixed headings; keep sound existing structure | reasoned outline, paragraph plans, material-to-section map |
| `pa-argument-architect` | "does this causal claim hold", "why write it this way" | structure is not evidence, sequence is not causation; four levels, top-down and bottom-up | nested outline or revision, reasoning table, key break and two repairs |
| `pa-intro-drafter` | writing or restructuring an introduction | background only as needed; no "first" without a search; contributions mirror gaps | introduction text plus evidence gaps |
| `pa-section-writer` | writing a body section | claim → material → reasoning → qualification; no invented cases, quotes or statistics | usable text plus open evidence gaps |
| `pa-title-abstract` | titles, abstracts, keywords | every claim traceable to the paper; same scope and strength in both languages | title options, abstract, keywords |
| `pa-prose-polisher` | polishing, removing officialese or AI tone | keep claims, causal strength, facts and citations; no detector promises | polished text plus substantive changes |
| `pa-paper-reviewer` | pre-submission review | state what was reviewed; judge by paper type; location, defect code, fix and acceptance criterion per issue | strongest defensible claim, top issues, ordered plan |
| `pa-supervisor-panel` | a multi-perspective diagnosis | lenses are research moves, not people; conflicts resolved by paper type, not votes; validated rules only | one load-bearing issue, ≤5 ordered changes, four-line skeleton |
| `pa-journal-fit` | choosing or comparing journals | official scope, current guidelines and recent articles, with access dates; no acceptance promises | comparison table, first choice and fallback |
| `pa-revision-responder` | answering reviewers | keep original numbering; revise first, then write in the completed tense; never auto-send | priorities, point-by-point responses, locations, open items |
| `pa-scholar-distiller` | annotating papers or distilling supervisor comments | bibliography ≠ full text ≠ correct annotation ≠ valid rule; verbatim quotes; machines count, humans change status | corpus report, annotations, candidate rules, support and evaluation status |

## How to use them

- **Installed (recommended)**: follow the [quick start](../README.en.md#quick-start), then speak naturally, e.g. "帮我把这个选题提炼成研究问题" or "Review this draft before submission".
- **Explicitly**: type `/pa-paper-reviewer` in Claude Code, or say "use the pa-paper-reviewer skill" in any tool.
- **Without installing**: paste a `SKILL.md` (and, if needed, files from its `references/`) into any assistant as a system prompt, or use it as a paper checklist.

Lens cards read by `pa-supervisor-panel`, `pa-paper-architect` and `pa-argument-architect` contain **validated rules only**. All rules are still seeds, so the cards currently hold each lens's focus and questions, which are heuristics. The full list of seed rules and their sources is in [rules/preview/lens-cards-preview.md](../rules/preview/lens-cards-preview.md).

---

English · [中文](README.md)
