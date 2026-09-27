"""Unit tests for the distillation harness (stdlib unittest; run: python -m unittest discover tests)."""

from __future__ import annotations

import copy
import csv
import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pa_lib import aggregate, blind, corpus, llm, stats, textnorm  # noqa: E402
from pa_lib.annotate import annotate_one  # noqa: E402
from pa_lib.common import load_moves, load_registry  # noqa: E402
from pa_lib.validate import schema_errors, verify_annotation  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "fictional_paper.txt"
EXAMPLE = ROOT / "distill" / "templates" / "annotation.example.json"


def fixture_text() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


KNOWN = {m["code"] for m in load_moves()["moves"]}


class TextNormTests(unittest.TestCase):
    def test_normalize_is_width_and_space_insensitive(self):
        a = "“材料精简”改革， 要求  街道（试点）"
        b = '"材料精简"改革,要求街道(试点)'
        self.assertEqual(textnorm.normalize(a), textnorm.normalize(b))

    def test_footnote_markers_are_ignored(self):
        self.assertEqual(textnorm.normalize("形式主义①依然存在[12]"), textnorm.normalize("形式主义依然存在"))

    def test_paragraphs_and_loc(self):
        pars = textnorm.split_paragraphs(fixture_text())
        self.assertEqual(len(pars), 19)
        self.assertTrue(pars[6].startswith("为什么以减负为目标"))
        self.assertEqual(textnorm.parse_loc("P12-P14"), [12, 13, 14])
        self.assertEqual(textnorm.parse_loc("第三段"), [])

    def test_quote_checker(self):
        qc = textnorm.QuoteChecker(textnorm.split_paragraphs(fixture_text()), fuzzy=0.9)
        self.assertEqual(qc.check("两项要求在纸质条件下相互冲突", "P12").status, "exact")
        self.assertEqual(qc.check("两项要求在纸质条件下相互冲突", "P3").status, "loc_mismatch")
        self.assertEqual(qc.check("材料", "P5").status, "too_short")
        # a paraphrase must not verify
        self.assertEqual(qc.check("改革的两个目标彼此矛盾，基层只能二选一", "P12").status, "miss")
        # one changed character is reported as fuzzy, never as exact
        res = qc.check("两项要求在纸面条件下相互冲突", "P12")
        self.assertEqual(res.status, "fuzzy")

    def test_abstract_extraction(self):
        self.assertTrue(textnorm.extract_abstract(fixture_text()).startswith("C省于2021年启动"))


class StatsTests(unittest.TestCase):
    def test_kappa_textbook(self):
        pairs = [("y", "y")] * 20 + [("y", "n")] * 5 + [("n", "y")] * 10 + [("n", "n")] * 15
        self.assertAlmostEqual(stats.cohen_kappa(pairs), 0.4, places=6)

    def test_krippendorff_canonical_example(self):
        n = None
        coders = [
            [1, 2, 3, 3, 2, 1, 4, 1, 2, n, n, n],
            [1, 2, 3, 3, 2, 2, 4, 1, 2, 5, n, 3],
            [n, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, n],
            [1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, n],
        ]
        units = list(zip(*coders))
        self.assertAlmostEqual(stats.krippendorff_alpha(units, "nominal"), 0.743, places=3)
        self.assertAlmostEqual(stats.krippendorff_alpha(units, "interval"), 0.849, places=3)

    def test_bootstrap_is_deterministic_and_brackets_mean(self):
        diffs = [0.1, 0.2, -0.05, 0.3, 0.15, 0.0, 0.25]
        m1 = stats.bootstrap_ci(diffs, n_boot=2000, seed=3)
        m2 = stats.bootstrap_ci(diffs, n_boot=2000, seed=3)
        self.assertEqual(m1, m2)
        self.assertLessEqual(m1[1], m1[0])
        self.assertLessEqual(m1[0], m1[2])

    def test_set_f1(self):
        self.assertIsNone(stats.set_f1(set(), set()))
        self.assertEqual(stats.set_f1({"A"}, set()), 0.0)
        self.assertAlmostEqual(stats.set_f1({"A", "B"}, {"A"}), 2 / 3)


class CorpusTests(unittest.TestCase):
    def rows(self, n, key="AAA", seed_first=False):
        return [{"paper_id": "", "scholar_key": key, "title": f"题名{i}", "year": str(2000 + i),
                 "seed_source": "1" if (seed_first and i == 0) else "0", "split": ""} for i in range(n)]

    def test_ids_and_periods(self):
        rows = self.rows(3)
        corpus.assign_ids(rows)
        self.assertEqual([r["paper_id"] for r in rows], ["AAA-2000-01", "AAA-2001-01", "AAA-2002-01"])
        self.assertEqual(corpus.period_of("2009"), "≤2009")
        self.assertEqual(corpus.period_of("2016"), "2016-2020")

    def test_split_is_sticky_and_protects_seed_sources(self):
        rows = self.rows(10, seed_first=True)
        corpus.assign_ids(rows)
        corpus.assign_split(rows, ratio=0.2, seed=1)
        self.assertEqual(rows[0]["split"], "train")
        self.assertEqual(sum(r["split"] == "heldout" for r in rows), 2)
        before = {r["paper_id"]: r["split"] for r in rows}
        more = self.rows(15, seed_first=False)[10:]
        rows += more
        corpus.assign_ids(rows)
        corpus.assign_split(rows, ratio=0.2, seed=1)
        self.assertTrue(all(r["split"] == before[r["paper_id"]] for r in rows if r["paper_id"] in before))
        self.assertEqual(sum(r["split"] == "heldout" for r in rows), 3)

    def test_parse_ris_and_endnote(self):
        ris = "TY  - JOUR\nAU  - 张三\nAU  - 李四\nTI  - 一个虚构的题名\nT2  - 虚构学报\nPY  - 2019\nIS  - 03\nSP  - 1\nEP  - 20\nER  - \n"
        recs = corpus.records_to_rows(corpus.parse_ris(ris), "ris", "ZS", "张三")
        self.assertEqual(recs[0]["authors"], "张三、李四")
        self.assertEqual(recs[0]["issue"], "3")
        self.assertEqual(recs[0]["pages"], "1-20")
        self.assertEqual(recs[0]["author_role"], "first")
        enw = "%0 Journal Article\n%A 王五\n%T 另一个虚构题名\n%J 虚构研究\n%D 2021\n%N 06\n%P 33-48\n%X 虚构摘要。\n"
        recs = corpus.records_to_rows(corpus.parse_endnote(enw), "endnote", "WW", "王五")
        self.assertEqual((recs[0]["year"], recs[0]["issue"], recs[0]["pages"], recs[0]["author_role"]), ("2021", "6", "33-48", "sole"))
        self.assertEqual(recs[0]["_abstract"], "虚构摘要。")


class ValidateTests(unittest.TestCase):
    def test_example_annotation_is_schema_valid_and_fully_verified(self):
        ann = example()
        self.assertEqual(schema_errors(ann), [])
        v = verify_annotation(ann, fixture_text(), KNOWN)
        self.assertEqual(v.hit_rate, 1.0, v.misses)
        self.assertEqual(len(v.verified_moves), 13)
        self.assertEqual(v.unsupported_moves, [])
        self.assertTrue(v.passed(0.9))

    def test_fabricated_quote_is_caught(self):
        ann = example()
        ann["moves"][4]["evidence"] = [{"quote": "改革的两个目标彼此矛盾，基层只能二选一", "loc": "P12"}]
        v = verify_annotation(ann, fixture_text(), KNOWN)
        self.assertIn("MECH-TENSION", v.unsupported_moves)
        self.assertNotIn("MECH-TENSION", v.verified_moves)
        self.assertLess(v.hit_rate, 1.0)

    def test_gate_fails_when_most_quotes_are_invented(self):
        ann = example()
        for mv in ann["moves"]:
            mv["evidence"] = [{"quote": "这是一句原文里根本不存在的话", "loc": "P1"}]
        for f in ann["fields"].values():
            if f.get("status") == "present":
                f["evidence"] = [{"quote": "这是一句原文里根本不存在的话", "loc": "P1"}]
        v = verify_annotation(ann, fixture_text(), KNOWN)
        self.assertFalse(v.passed(0.9))

    def test_unknown_code_and_schema_errors_fail(self):
        ann = example()
        ann["moves"].append({"code": "MECH-MADE-UP", "evidence": [{"quote": "两项要求在纸质条件下相互冲突", "loc": "P12"}]})
        del ann["fields"]["puzzle"]
        v = verify_annotation(ann, fixture_text(), KNOWN)
        self.assertIn("MECH-MADE-UP", v.unknown_codes)
        self.assertTrue(v.schema_errors)
        self.assertFalse(v.passed(0.0))


def _registry() -> dict:
    return {
        "admission": {"min_papers": 3, "min_periods": 2, "min_lift": 1.5, "shared_min_scholar_share": 0.6,
                      "min_annotated_for_rejection": 4},
        "lenses": [{"id": "SH", "tradition": {"keys": [], "scholars": []}},
                   {"id": "IL", "tradition": {"keys": ["A"], "scholars": []}},
                   {"id": "CE", "tradition": {"keys": ["B"], "scholars": []}}],
        "rules": [
            {"id": "SH-X", "lens": "SH", "layer": "shared", "status": "seed", "requires": ["PZ-*"]},
            {"id": "IL-X", "lens": "IL", "layer": "archetype", "status": "seed", "requires": ["PZ-ANOMALY|PZ-PERSISTENCE", "MECH-TENSION"]},
            {"id": "IL-Y", "lens": "IL", "layer": "archetype", "status": "seed", "requires": ["MECH-HISTORICAL"]},
            {"id": "CE-X", "lens": "CE", "layer": "archetype", "status": "seed", "requires": ["CON-IDEALTYPE", "field:boundary_conditions"]},
        ],
    }


class AggregateTests(unittest.TestCase):
    def records(self):
        R = aggregate.Record
        periods = ["≤2009", "2010-2015", "2016-2020", "2021-2026"]
        recs = [R(f"A{i}", "A", periods[i], "train", {"PZ-ANOMALY", "MECH-TENSION"}, set()) for i in range(4)]
        recs += [R(f"B{i}", "B", periods[i], "train", {"PZ-VARIATION", "CON-IDEALTYPE"}, {"boundary_conditions"}) for i in range(4)]
        recs.append(R("A9", "A", periods[0], "heldout", {"PZ-ANOMALY", "MECH-TENSION"}, set()))
        return recs

    def test_support_lift_and_heldout_exclusion(self):
        sup = aggregate.compute_support(self.records(), _registry())
        self.assertEqual(sup["n_heldout_excluded"], 1)
        il = sup["rules"]["IL-X"]
        self.assertEqual(il["n_support"], 4)
        self.assertNotIn("A9", il["support_papers"])
        self.assertTrue(il["pass"])
        self.assertEqual(il["suggestion"], "candidate")
        self.assertGreater(il["lift"], 1.5)
        self.assertTrue(sup["rules"]["SH-X"]["pass"])
        self.assertTrue(sup["rules"]["CE-X"]["pass"])

    def test_unsupported_rule_is_suggested_for_rejection_only_with_enough_data(self):
        sup = aggregate.compute_support(self.records(), _registry())
        self.assertEqual(sup["rules"]["IL-Y"]["suggestion"], "rejected")
        reg = _registry()
        reg["admission"]["min_annotated_for_rejection"] = 10
        sup = aggregate.compute_support(self.records(), reg)
        self.assertEqual(sup["rules"]["IL-Y"]["suggestion"], "insufficient_data")

    def test_unsplit_records_are_refused(self):
        recs = self.records()
        recs[0].split = ""
        with self.assertRaises(Exception):
            aggregate.compute_support(recs, _registry())

    def test_real_registry_codes_exist(self):
        reg = load_registry()
        fams = set(load_moves()["families"])
        for rule in reg["rules"]:
            for clause in rule["requires"]:
                if clause.startswith("field:"):
                    continue
                for alt in clause.split("|"):
                    if alt.endswith("-*"):
                        self.assertIn(alt[:-2], fams, rule["id"])
                    else:
                        self.assertIn(alt, KNOWN, rule["id"])


class ExtractJsonTests(unittest.TestCase):
    def test_think_and_fences(self):
        content = "<think>先想一想 {不是JSON}</think>\n```json\n{\"a\": \"含有}括号的字符串\", \"b\": [1, 2]}\n```"
        self.assertEqual(llm.extract_json(content), {"a": "含有}括号的字符串", "b": [1, 2]})

    def test_unclosed_reasoning_prefix(self):
        self.assertEqual(llm.extract_json('reasoning...</think>{"x": 1}'), {"x": 1})

    def test_no_json(self):
        with self.assertRaises(ValueError):
            llm.extract_json("抱歉，我无法完成。")


class _MockHandler(BaseHTTPRequestHandler):
    replies: list[str] = []
    calls = 0

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        cls = type(self)
        content = cls.replies[min(cls.calls, len(cls.replies) - 1)]
        cls.calls += 1
        body = json.dumps({"choices": [{"message": {"content": content}}], "usage": {"total_tokens": 1}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class AnnotateEndToEndTests(unittest.TestCase):
    def test_retry_then_valid_output_is_written_and_verifies(self):
        good = example()
        _MockHandler.replies = ["我先给出一个不完整的结果：{\"paper_id\": ", "<think>检查引文</think>```json\n" + json.dumps(good, ensure_ascii=False) + "\n```"]
        _MockHandler.calls = 0
        server = HTTPServer(("127.0.0.1", 0), _MockHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            cfg = llm.LLMConfig(base_url=f"http://127.0.0.1:{server.server_port}/v1", model="mock")
            with tempfile.TemporaryDirectory() as tmp:
                row = {"paper_id": "DEMO-2024-01", "fulltext": str(FIXTURE)}
                res = annotate_one(row, Path(tmp), cfg, load_moves(), max_chars=60000, allow_truncate=False,
                                   force=False, dry_run=False)
                self.assertEqual(res["status"], "ok")
                self.assertEqual(res["attempts"], 2)
                written = json.loads((Path(tmp) / "DEMO-2024-01.json").read_text(encoding="utf-8"))
                self.assertEqual(written["meta"]["llm"]["model"], "mock")
                self.assertNotIn("api_key", json.dumps(written["meta"]))
                v = verify_annotation(written, fixture_text(), KNOWN)
                self.assertTrue(v.passed(0.9))
                # unchanged prompt + text -> skipped on rerun
                res2 = annotate_one(row, Path(tmp), cfg, load_moves(), max_chars=60000, allow_truncate=False,
                                    force=False, dry_run=False)
                self.assertEqual(res2["status"], "skipped_existing")
                # over-long text fails loudly instead of being truncated
                res3 = annotate_one(row, Path(tmp), cfg, load_moves(), max_chars=100, allow_truncate=False,
                                    force=True, dry_run=False)
                self.assertEqual(res3["status"], "too_long")
        finally:
            server.shutdown()
            server.server_close()


class BlindTests(unittest.TestCase):
    def test_pack_and_score_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            items = tmp / "items.jsonl"
            with open(items, "w", encoding="utf-8") as fh:
                for i in range(6):
                    fh.write(json.dumps({"item_id": f"I{i}", "draft": "原稿", "outputs": {"baseline": "甲", "skill": "乙"}}, ensure_ascii=False) + "\n")
            blind.pack(items, tmp / "pk", raters=2, seed=5)
            key = json.loads((tmp / "pk" / "_key.json").read_text(encoding="utf-8"))["key"]
            for sheet in sorted((tmp / "pk").glob("scores_R*.csv")):
                with open(sheet, encoding="utf-8") as fh:
                    rows = list(csv.DictReader(fh))
                for row in rows:
                    system = key[row["item_id"]][row["label"]]
                    base = 3 if system == "baseline" else 4
                    for d in ("D1", "D2", "D3", "D4", "D5", "D6"):
                        row[d] = str(base)
                    row["D7"] = "4"
                    row["D8"] = "4"
                    row["fabrications"] = "0"
                with open(sheet, "w", encoding="utf-8", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                    w.writeheader()
                    w.writerows(rows)
            res = blind.score(tmp / "pk", baseline="baseline", margin=0.5, n_boot=500)
            self.assertAlmostEqual(res["vs_baseline"]["skill"]["D1"]["mean"], 1.0)
            self.assertTrue(res["vs_baseline"]["skill"]["D7"]["noninferior"])
            self.assertTrue(res["vs_baseline"]["skill"]["D8"]["noninferior"])
            self.assertEqual(res["fabrication_rate"], {"baseline": 0.0, "skill": 0.0})
            self.assertTrue(res["vs_baseline"]["skill"]["fabrication_rate"]["noninferior"])
            self.assertTrue((tmp / "pk" / "blind_report.md").exists())


if __name__ == "__main__":
    unittest.main()
