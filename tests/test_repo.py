"""Repository integrity: lint, generated references, installer, and gates that must be able to fail."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pa_lib import blind  # noqa: E402
from pa_lib.common import load_registry  # noqa: E402


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def scratch_copy(tmp: Path) -> Path:
    dst = tmp / "repo"
    for part in ("scripts", "skills", "rules", "vocab"):
        shutil.copytree(ROOT / part, dst / part, ignore=shutil.ignore_patterns("__pycache__"))
    return dst


class RepoTests(unittest.TestCase):
    def test_lint_and_sync_pass_on_repo(self):
        lint = run([sys.executable, "scripts/lint_skills.py"], ROOT)
        self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)
        sync = run([sys.executable, "scripts/build_refs.py", "--check"], ROOT)
        self.assertEqual(sync.returncode, 0, sync.stdout + sync.stderr)

    def test_lint_fails_on_names_orphans_and_missing_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = scratch_copy(Path(tmp))
            scholar = load_registry()["lenses"][1]["tradition"]["scholars"][0]
            with open(repo / "skills" / "pa-router" / "SKILL.md", "a", encoding="utf-8") as fh:
                fh.write(f"\n{scholar}认为……\n见 references/does-not-exist.md\n")
            (repo / "skills" / "pa-journal-fit" / "references" / "orphan.md").write_text("# x\n", encoding="utf-8")
            res = run([sys.executable, "scripts/lint_skills.py"], repo)
            self.assertEqual(res.returncode, 1)
            self.assertIn("scholar name", res.stdout)
            self.assertIn("orphan", res.stdout)
            self.assertIn("missing references/does-not-exist.md", res.stdout)

    def test_sync_check_fails_on_edited_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = scratch_copy(Path(tmp))
            with open(repo / "skills" / "pa-router" / "references" / "argument-chain.md", "a", encoding="utf-8") as fh:
                fh.write("\n手工改动\n")
            res = run([sys.executable, "scripts/build_refs.py", "--check"], repo)
            self.assertEqual(res.returncode, 1)

    def test_only_runtime_statuses_reach_skills(self):
        reg = load_registry()
        runtime = set(reg["build"]["runtime_statuses"])
        cards = (ROOT / "skills" / "pa-supervisor-panel" / "references" / "lens-cards.md").read_text(encoding="utf-8")
        preview = (ROOT / "rules" / "preview" / "lens-cards-preview.md").read_text(encoding="utf-8")
        for rule in reg["rules"]:
            token = f"**{rule['id']}**"
            if rule["status"] in runtime:
                self.assertIn(token, cards)
            else:
                self.assertNotIn(token, cards, f"{rule['id']} ({rule['status']}) leaked into runtime cards")
            if rule["status"] != "rejected":
                self.assertIn(token, preview)
        names = {s for lens in reg["lenses"] for s in lens["tradition"]["scholars"]}
        self.assertFalse([n for n in names if n in cards])
        self.assertTrue(all(n in preview for n in names))
        # consumer lenses (e.g. writing architecture) follow the same rule in every consuming skill
        for lens in [l for l in reg["lenses"] if l.get("consumers")]:
            for skill in lens["consumers"]:
                card = (ROOT / "skills" / skill / "references" / f"{lens['card']}.md").read_text(encoding="utf-8")
                self.assertFalse([n for n in names if n in card], skill)
                for rule in [r for r in reg["rules"] if r["lens"] == lens["id"]]:
                    token = f"**{rule['id']}**"
                    (self.assertIn if rule["status"] in runtime else self.assertNotIn)(token, card)

    @unittest.skipUnless(shutil.which("bash"), "bash not available")
    def test_installer_copies_every_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = run(["bash", "scripts/install.sh", "--dir", tmp], ROOT)
            self.assertEqual(res.returncode, 0, res.stderr)
            expected = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())
            got = sorted(p.name for p in Path(tmp).iterdir() if (p / "SKILL.md").exists())
            self.assertEqual(got, expected)
            again = run(["bash", "scripts/install.sh", "--dir", tmp], ROOT)
            self.assertIn(f"skipped {len(expected)}", again.stdout)


class BlindHarmGateTests(unittest.TestCase):
    def test_more_fabrication_fails_noninferiority(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            items = tmp / "items.jsonl"
            with open(items, "w", encoding="utf-8") as fh:
                for i in range(10):
                    fh.write(json.dumps({"item_id": f"I{i}", "draft": "原稿", "outputs": {"baseline": "甲", "skill": "乙"}}, ensure_ascii=False) + "\n")
            blind.pack(items, tmp / "pk", raters=2, seed=3)
            key = json.loads((tmp / "pk" / "_key.json").read_text(encoding="utf-8"))["key"]
            for sheet in sorted((tmp / "pk").glob("scores_R*.csv")):
                with open(sheet, encoding="utf-8") as fh:
                    rows = list(csv.DictReader(fh))
                for row in rows:
                    skill = key[row["item_id"]][row["label"]] == "skill"
                    for d in ("D1", "D2", "D3", "D4", "D5", "D6"):
                        row[d] = "5" if skill else "3"
                    row["D7"] = "2" if skill else "4"
                    row["D8"] = "2" if skill else "4"
                    row["fabrications"] = "2" if (skill and int(row["item_id"][1:]) % 2 == 0) else "0"
                with open(sheet, "w", encoding="utf-8", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                    w.writeheader()
                    w.writerows(rows)
            res = blind.score(tmp / "pk", baseline="baseline", n_boot=500)
            vs = res["vs_baseline"]["skill"]
            self.assertGreater(vs["D1"]["mean"], 0)          # looks better on the benefit dimensions
            self.assertFalse(vs["D7"]["noninferior"])        # but the harm gates must fail
            self.assertFalse(vs["D8"]["noninferior"])
            self.assertEqual(res["fabrication_rate"]["skill"], 0.5)
            self.assertFalse(vs["fabrication_rate"]["noninferior"])


if __name__ == "__main__":
    unittest.main()
