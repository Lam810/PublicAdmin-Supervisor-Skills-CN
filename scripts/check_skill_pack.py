#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(__file__).resolve().parents[1]
skills = sorted((root / "skills").glob("*/SKILL.md"))
failed = False

for p in skills:
    txt = p.read_text(encoding="utf-8")
    ok_frontmatter = txt.startswith("---\n") and "\n---\n" in txt[4:]
    has_name = bool(re.search(r"^name:\s*\S+", txt, flags=re.M))
    has_desc = bool(re.search(r"^description:\s*.+", txt, flags=re.M))
    if not (ok_frontmatter and has_name and has_desc):
        failed = True
        print(f"FAIL {p.relative_to(root)}")
    else:
        print(f"OK   {p.relative_to(root)}")

print(f"\nSkills checked: {len(skills)}")
sys.exit(1 if failed else 0)
