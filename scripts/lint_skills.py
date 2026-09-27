#!/usr/bin/env python3
"""Structural linter for the skills/ directory.

Rules:
- every skill dir has SKILL.md with YAML frontmatter: name (== dir name, kebab-case),
  description (80..1024 chars, contains "Use when" and at least one Chinese trigger),
  license;
- SKILL.md body <= 500 lines;
- every `references/X.md` mentioned in SKILL.md exists, and every file in references/
  is mentioned in SKILL.md (orphans are never loaded by an agent);
- references are one level deep: a reference file may not point to another references/ file;
- reference files longer than 100 lines have a table of contents (## 目录) in the first 25 lines;
- no scholar names anywhere under skills/ (names come from rules/registry.yaml):
  skills must work without them, and must never invite impersonation;
- no leftover placeholders (TODO, TBD, XXX, 待补充).

Exit 0 when clean, 1 on any violation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pa_lib.common import load_registry, load_yaml  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
CJK = re.compile(r"[一-鿿]")
REF = re.compile(r"references/([A-Za-z0-9_\-]+\.md)")
PLACEHOLDER = re.compile(r"\b(TODO|TBD|XXX)\b|待补充")


def frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter opener")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("missing frontmatter closer")
    import yaml  # type: ignore
    fm = yaml.safe_load(text[4:end])
    if not isinstance(fm, dict):
        raise ValueError("frontmatter is not a mapping")
    return fm, text[end + 5:]


def main() -> int:
    names = sorted({s for lens in load_registry()["lenses"] for s in lens["tradition"]["scholars"]})
    errors: list[str] = []
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    for sd in skill_dirs:
        md = sd / "SKILL.md"
        rel = md.relative_to(REPO)
        if not md.exists():
            errors.append(f"{sd.relative_to(REPO)}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        try:
            fm, body = frontmatter(text)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel}: {exc}")
            continue
        name = fm.get("name")
        if name != sd.name:
            errors.append(f"{rel}: name {name!r} must equal directory name {sd.name!r}")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}[a-z0-9]", name or ""):
            errors.append(f"{rel}: name must be kebab-case")
        desc = fm.get("description")
        if not isinstance(desc, str):
            errors.append(f"{rel}: description missing")
        else:
            if not 80 <= len(desc) <= 1024:
                errors.append(f"{rel}: description length {len(desc)} not in 80..1024")
            if "Use when" not in desc:
                errors.append(f"{rel}: description needs a 'Use when' clause")
            if not CJK.search(desc):
                errors.append(f"{rel}: description needs Chinese trigger phrases")
        if not fm.get("license"):
            errors.append(f"{rel}: license missing")
        if len(body.splitlines()) > 500:
            errors.append(f"{rel}: body has {len(body.splitlines())} lines (> 500)")
        mentioned = set(REF.findall(body))
        ref_dir = sd / "references"
        present = {p.name for p in ref_dir.glob("*.md")} if ref_dir.is_dir() else set()
        for m in sorted(mentioned - present):
            errors.append(f"{rel}: points to missing references/{m}")
        for o in sorted(present - mentioned):
            errors.append(f"{rel}: references/{o} is never mentioned (orphan)")
        files = [md] + sorted(ref_dir.glob("*.md")) if ref_dir.is_dir() else [md]
        for f in files:
            t = f.read_text(encoding="utf-8")
            frel = f.relative_to(REPO)
            for n in names:
                if n in t:
                    errors.append(f"{frel}: contains scholar name {n!r} (keep names out of skills/)")
            if PLACEHOLDER.search(t):
                errors.append(f"{frel}: leftover placeholder {PLACEHOLDER.search(t).group(0)!r}")
            if f != md:
                if REF.search(_strip_comment(t)):
                    errors.append(f"{frel}: nested reference pointer (references must be one level deep)")
                lines = t.splitlines()
                if len(lines) > 100 and "## 目录" not in "\n".join(lines[:25]):
                    errors.append(f"{frel}: {len(lines)} lines but no '## 目录' in the first 25 lines")
    if errors:
        print(f"lint: {len(errors)} violation(s)")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"lint: {len(skill_dirs)} skill(s) clean")
    return 0


def _strip_comment(t: str) -> str:
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)


if __name__ == "__main__":
    sys.exit(main())
