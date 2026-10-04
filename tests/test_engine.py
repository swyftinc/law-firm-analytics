"""Tests for the engine. Run: python3 -m unittest discover -s tests -v   (standard library only)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "src", "shared", "scripts")
sys.path.insert(0, S)
sys.path.insert(0, os.path.join(ROOT, "evals"))

import common  # noqa: E402
import chartspec  # noqa: E402
import check_grounding  # noqa: E402
import ground_truth  # noqa: E402
import render  # noqa: E402
import xlsx_reader  # noqa: E402

DATA = os.path.join(ROOT, "sample-data", "super-duper-law")


class Parsing(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(common.parse_num("$1,234.50"), 1234.5)
        self.assertEqual(common.parse_num("(1,200.00)"), -1200.0)
        self.assertEqual(common.parse_num("88%"), 88.0)
        self.assertIsNone(common.parse_num("-"))
        self.assertIsNone(common.parse_num(""))

    def test_dates(self):
        self.assertEqual(common.parse_date("09/14/2026 10:32 AM"), datetime(2026, 9, 14, 10, 32))
        self.assertEqual(common.parse_date("2026-09-14 10:32"), datetime(2026, 9, 14, 10, 32))
        self.assertEqual(common.parse_date(45000).year, 2023)
        self.assertEqual(common.detect_date_format(["25/12/2026", "01/02/2026"]), "%d/%m/%Y")

    def test_header_and_totals(self):
        raw = [["Accounts receivable aging", "", ""], ["", "", ""], ["Matter", "Current", "Total"],
               ["A", "$1.00", "$1.00"], ["B", "$2.00", "$2.00"], ["Total", "$3.00", "$3.00"]]
        t = common.rows_to_table(raw, "x.csv")
        self.assertEqual(t.header, ["Matter", "Current", "Total"])
        self.assertEqual(len(t.rows), 2)
        self.assertEqual(t.dropped, 1)

    def test_stats(self):
        self.assertAlmostEqual(common.median([1, 3, 2, 10]), 2.5)
        z = common.two_prop_z(30, 100, 10, 100)
        self.assertGreater(z, 3)
        self.assertGreater(common.p_two_sided(0.5), 0.5)


class Xlsx(unittest.TestCase):
    def test_reads_what_openpyxl_wrote(self):
        sheets = xlsx_reader.read_xlsx(os.path.join(DATA, "marketing-spend.xlsx"))
        rows = sheets["Spend"]
        self.assertEqual(rows[0], ["Month", "Source", "Spend"])
        self.assertIsInstance(rows[1][0], datetime)
        try:
            import openpyxl
        except ImportError:
            return
        ws = openpyxl.load_workbook(os.path.join(DATA, "marketing-spend.xlsx")).active
        theirs = [list(r) for r in ws.iter_rows(values_only=True)]
        self.assertEqual(len(theirs), len(rows))
        self.assertEqual([r[1] for r in theirs[1:]], [r[1] for r in rows[1:]])
        self.assertEqual([r[2] for r in theirs[1:]], [r[2] for r in rows[1:]])


class Engine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.facts_path = os.path.join(cls.tmp, "facts.json")
        subprocess.run([sys.executable, os.path.join(S, "compute_facts.py"), "--mapping", os.path.join(DATA, "mapping.json"),
                        "--out", cls.facts_path], check=True, capture_output=True)
        cls.d = json.load(open(cls.facts_path))
        cls.F = {f["id"]: f for f in cls.d["facts"]}
        cls.gt = ground_truth.compute(DATA)

    def close(self, a, b, rel=.005):
        self.assertLessEqual(abs(a - b), max(abs(b) * rel, 1e-9), f"{a} vs {b}")

    def test_matches_the_answer_key(self):
        F, gt = self.F, self.gt
        self.close(F["cost_per_signed.google-lsa"]["value"], gt["google_lsa_sep_cost_per_signed"])
        self.close(F["cost_per_signed.google-lsa"]["prior"]["value"], gt["google_lsa_aug_cost_per_signed"])
        self.assertEqual(F["cost_per_signed.google-lsa"]["n"], gt["google_lsa_sep_signed"])
        self.assertEqual(F["lead_volume.google-lsa"]["value"], gt["lsa_lead_volume_t30"])
        self.assertEqual(F["lead_volume.all"]["value"], gt["lead_volume_t30"])
        self.close(F["realization.family-law"]["value"], gt["family_realization_now"])
        self.close(F["realization.family-law"]["prior"]["value"], gt["family_realization_prior"])
        self.close(F["realization.wren-kowalczyk"]["value"], gt["wren_realization_now"])
        self.close(F["realization_contribution.family-law_wren-kowalczyk"]["share_of_change"], gt["wren_share_of_family_change"], .01)
        self.close(F["ar_over_90.all"]["value"], gt["ar_over_90_oct4"])
        self.close(F["ar_over_90.all"]["prior"]["value"], gt["ar_over_90_sep6"])
        self.close(F["after_hours_share.google-lsa"]["value"], gt["lsa_after_hours_share_t30"])
        self.close(F["signed_rate_by_response.within-1-hour"]["value"], gt["signed_rate_within_hour"])
        self.close(F["signed_rate_by_response.over-24-hours-or-never"]["value"], gt["signed_rate_over_day_or_never"])
        self.close(F["speed_to_lead.weekend"]["value"], gt["median_minutes_weekend_t90"], .03)
        self.close(F["matter_cycle_time.business-litigation"]["value"], gt["cycle_days_business_litigation"], .01)

    def test_directions_never_inverted(self):
        for f in self.d["facts"]:
            if f["direction"] == "neutral" or f["status"] not in ("red", "green") or not f.get("prior"):
                continue
            up = f["delta_abs"] > 0
            good = up == (f["direction"] == "higher_better")
            self.assertEqual(f["status"], "green" if good else "red", f["id"])

    def test_thin_is_never_colored(self):
        for f in self.d["facts"]:
            if f["thin"]:
                self.assertEqual(f["status"], "gray", f["id"])

    def test_planted_signals(self):
        F = self.F
        self.assertEqual(F["cost_per_signed.google-lsa"]["change_class"], "worsened")
        self.assertEqual(F["lead_volume.google-lsa"]["change_class"], "flat")
        self.assertEqual(F["lead_volume.all"]["change_class"], "flat")          # the +6% non-signal
        self.assertTrue(F["signed_rate.wealth-advisor-referral"]["thin"])        # four of four
        self.assertEqual(F["realization.family-law"]["status"], "red")
        self.assertEqual(F["ar_over_90.all"]["change_class"], "worsened")

    def test_lead_mix_uses_one_window_for_every_source(self):
        # lead_volume windows differ by source (small sources get a wider window), so the mix must not use them
        block = chartspec.FUNCS["lead_sources_mix"](self.d)
        shares = {f["scope"]["source"]: f for f in self.d["facts"] if f["metric"] == "lead_source_share"}
        self.assertEqual({w["window"]["label"] for w in shares.values()}, {next(iter(shares.values()))["window"]["label"]})
        self.assertEqual(len(block["data"]), len(shares))
        self.assertEqual(block["kind"], "bar_h")
        for item in block["data"]:
            self.assertEqual(item["display"], shares[item["label"]]["display"])
        self.assertEqual(sum(1 for i in block["data"] if i["highlight"]), 1)

    def test_ranking_leads_with_lsa(self):
        out = os.path.join(self.tmp, "ranked.json")
        subprocess.run([sys.executable, os.path.join(S, "rank_changes.py"), self.facts_path, "--out", out], check=True, capture_output=True)
        r = json.load(open(out))
        self.assertIn("Google LSA", r["look_at"][0]["title"])
        self.assertEqual(r["look_at"][0]["confidence"], "high")
        self.assertTrue(any("wealth-advisor" in t["id"] for t in r["too_thin_to_call"]))
        self.assertTrue(any(x["id"] == "lead_volume.all" for x in r["moved_within_normal_variation"]))


class Rendering(unittest.TestCase):
    def test_lint_catches_rule_breaks(self):
        spec = {"title": "A Chart Title In Title Case", "accent": "#aaaaaa", "blocks": [
            {"type": "chart", "kind": "bar_h", "title": "Costs", "data": [{"label": "a", "value": 1, "highlight": True}, {"label": "b", "value": 2, "highlight": True}]},
            {"type": "kpi_row", "items": [{"label": "Cost per signed matter", "value": "$1", "direction": "lower_better", "delta_dir": "up", "status": "green"}]}]}
        w = render.lint(spec)
        self.assertTrue(any("contrast" in x for x in w))
        self.assertTrue(any("highlighted bars" in x for x in w))
        self.assertTrue(any("inverted" in x for x in w))

    def test_em_dash_is_removed(self):
        self.assertNotIn("\N{EM DASH}", render.clean("a \N{EM DASH} b"))

    def test_bars_start_at_zero_and_thin_gets_no_bar(self):
        svg, _ = render.chart_bar_h({"title": "t", "unit": "usd", "data": [
            {"label": "a", "value": 100, "highlight": True}, {"label": "b", "value": 90},
            {"label": "c", "value": 999, "thin": True}]}, "#2620f6")
        self.assertEqual(svg.count("<rect"), 2)
        self.assertIn("too thin to call", svg)


class Grounding(unittest.TestCase):
    def test_flags_invented_numbers(self):
        facts = json.load(open(os.path.join(ROOT, "docs", "example", "facts.json")))
        allowed = check_grounding.allowed_numbers(facts)
        _, bad = check_grounding.scan("Cost went from $450 to $861, a 91% rise. We lost about $480,000.", allowed)
        self.assertEqual([b["token"] for b in bad], ["$480,000"])


if __name__ == "__main__":
    unittest.main()
