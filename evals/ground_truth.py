#!/usr/bin/env python3
"""Recompute the planted facts straight from the sample files, with no engine code.

This is the answer key. It reads the raw CSVs with the csv module and applies the definitions in
references/metrics.md by hand. tests/test_engine.py checks the engine against it, and evals/check.py
checks what a skill produced against it. Standard library only (reads the .xlsx with the bundled reader).

Usage: python3 evals/ground_truth.py [--data sample-data/super-duper-law] [--out evals/ground_truth.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "shared", "scripts"))
from xlsx_reader import read_xlsx  # noqa: E402

AS_OF = date(2026, 10, 4)


def money(s):
    return float(str(s).replace("$", "").replace(",", "") or 0)


def rows(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))


def compute(data_dir):
    D = lambda f: os.path.join(data_dir, f)
    out = {"as_of": AS_OF.isoformat()}

    # ---- leads
    leads = rows(D("clio-grow-matter-revenue-report.csv"))
    for r in leads:
        r["c"] = datetime.strptime(r["Created at"], "%m/%d/%Y %I:%M %p")
        r["sd"] = datetime.strptime(r["Status date"], "%m/%d/%Y").date()
        r["signed"] = r["Matter status - top level"] == "Hired"
    t30 = (AS_OF - timedelta(days=29), AS_OF)
    p30 = (AS_OF - timedelta(days=59), AS_OF - timedelta(days=30))
    inwin = lambda r, w: w[0] <= r["c"].date() <= w[1]
    out["lead_volume_t30"] = sum(1 for r in leads if inwin(r, t30))
    out["lead_volume_prior30"] = sum(1 for r in leads if inwin(r, p30))
    out["lsa_lead_volume_t30"] = sum(1 for r in leads if r["Source"] == "Google LSA" and inwin(r, t30))
    out["lsa_lead_volume_prior30"] = sum(1 for r in leads if r["Source"] == "Google LSA" and inwin(r, p30))

    # ---- spend and cost per signed matter, September against August
    sp = {}
    for r in list(read_xlsx(D("marketing-spend.xlsx"))["Spend"])[1:]:
        sp[(r[0].date(), r[1])] = r[2]
    for lab, m0, m1 in (("aug", date(2026, 8, 1), date(2026, 8, 31)), ("sep", date(2026, 9, 1), date(2026, 9, 30))):
        for src in ("Google LSA", "Google Ads"):
            n = sum(1 for r in leads if r["Source"] == src and r["signed"] and m0 <= r["sd"] <= m1)
            key = f"{src.lower().replace(' ', '_')}_{lab}"
            out[f"{key}_signed"] = n
            out[f"{key}_cost_per_signed"] = sp[(m0, src)] / n if n else None
    out["lsa_cost_ratio"] = out["google_lsa_sep_cost_per_signed"] / out["google_lsa_aug_cost_per_signed"]

    # ---- speed to lead and the arrival mix (leads from the last 3 days are left out)
    log = rows(D("intake-call-log.csv"))
    cutoff = AS_OF - timedelta(days=3)
    src_of = {r["Email"].lower(): r["Source"] for r in leads}
    dt = lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M")

    def kind(rc):
        if rc.weekday() >= 5:
            return "weekend"
        return "business" if 8 <= rc.hour < 18 else "after_hours"

    recs = []
    for r in log:
        rc = dt(r["Received at"])
        if rc.date() > cutoff:
            continue
        delay = (dt(r["First contact at"]) - rc).total_seconds() / 60 if r["First contact at"] else None
        recs.append((rc, delay, src_of.get(r["Contact email"].lower())))
    w90 = (AS_OF - timedelta(days=3) - timedelta(days=89), AS_OF - timedelta(days=3))
    for k in ("weekend", "business", "after_hours"):
        d = [x[1] for x in recs if w90[0] <= x[0].date() <= w90[1] and kind(x[0]) == k and x[1] is not None]
        out[f"median_minutes_{k}_t90"] = statistics.median(d)
    cw = (AS_OF - timedelta(days=3) - timedelta(days=29), AS_OF - timedelta(days=3))
    cp = (cw[0] - timedelta(days=30), cw[0] - timedelta(days=1))
    for lab, w in (("t30", cw), ("prior30", cp)):
        sel = [x for x in recs if w[0] <= x[0].date() <= w[1] and x[2] == "Google LSA"]
        out[f"lsa_after_hours_share_{lab}"] = sum(1 for x in sel if kind(x[0]) != "business") / len(sel)

    # ---- does speed matter: signed rate by first-contact bucket, on leads old enough to have decided
    decided = sorted((r["sd"] - r["c"].date()).days for r in leads if r["Matter status - top level"] != "Intake")
    pos = (len(decided) - 1) * .9
    lo = int(pos)
    p90 = decided[lo] + (decided[min(lo + 1, len(decided) - 1)] - decided[lo]) * (pos - lo)
    lag = int(max(7, min(45, -(-p90 // 1))))   # the engine reads the usual time to a decision from the data
    out["decision_lag_days"] = lag
    cend = AS_OF - timedelta(days=lag)
    cwin = (cend - timedelta(days=89), cend)
    by = {r["Email"].lower(): r for r in leads}
    pool = []
    for r in log:
        rc = dt(r["Received at"])
        if cwin[0] <= rc.date() <= cwin[1] and r["Contact email"].lower() in by:
            delay = (dt(r["First contact at"]) - rc).total_seconds() / 60 if r["First contact at"] else None
            pool.append((delay, by[r["Contact email"].lower()]["signed"]))
    fast = [s for d, s in pool if d is not None and d <= 60]
    slow = [s for d, s in pool if d is None or d > 1440]
    out["signed_rate_within_hour"] = sum(fast) / len(fast)
    out["signed_rate_over_day_or_never"] = sum(slow) / len(slow)

    # ---- the new referral source
    w = [r for r in leads if r["Source"] == "Wealth advisor referral"]
    out["wealth_advisor_leads"] = len(w)
    out["wealth_advisor_signed"] = sum(1 for r in w if r["signed"])

    # ---- realization: billed over original billable, on work old enough to be invoiced
    tm = rows(D("clio-realization-report.csv"))
    for r in tm:
        r["d"] = datetime.strptime(r["Time entry date"], "%m/%d/%Y").date()
    lagb = 35
    wend = AS_OF - timedelta(days=lagb)
    cur = (wend - timedelta(days=89), wend)
    pri = (cur[0] - timedelta(days=90), cur[0] - timedelta(days=1))

    def real(sel):
        o = sum(float(r["Original Billable Total"]) for r in sel)
        b = sum(float(r["Billed Time Amount"]) for r in sel)
        return b / o, o

    fam = [r for r in tm if r["Practice Area"] == "Family law"]
    f1, bill1 = real([r for r in fam if cur[0] <= r["d"] <= cur[1]])
    f0, _ = real([r for r in fam if pri[0] <= r["d"] <= pri[1]])
    out["family_realization_now"], out["family_realization_prior"] = f1, f0
    out["family_realization_billable_now"] = bill1
    sel1 = [r for r in fam if cur[0] <= r["d"] <= cur[1] and r["User"] == "Wren Kowalczyk"]
    sel0 = [r for r in fam if pri[0] <= r["d"] <= pri[1] and r["User"] == "Wren Kowalczyk"]
    w1, _ = real(sel1)
    w0, _ = real(sel0)
    share1 = sum(float(r["Original Billable Total"]) for r in sel1) / bill1
    out["wren_realization_now"], out["wren_realization_prior"] = w1, w0
    out["wren_share_of_family_change"] = (w0 - w1) * share1 / (f0 - f1)
    for a in ("Elena Brightwater", "Tomas Ferreira"):
        out[f"realization_now_{a.split()[0].lower()}"] = real([r for r in fam if cur[0] <= r["d"] <= cur[1] and r["User"] == a])[0]

    # ---- receivables over 90 days, two snapshots
    for lab, f in (("sep6", "clio-ar-aging-2026-09-06.csv"), ("oct4", "clio-ar-aging-2026-10-04.csv")):
        ar = [r for r in rows(D(f)) if r["Matter"] != "Total"]
        o90 = sum(money(r["91+ days"]) for r in ar)
        out[f"ar_over_90_{lab}"] = o90
        out[f"ar_total_{lab}"] = sum(money(r["Total"]) for r in ar)
        by_m = defaultdict(float)
        for r in ar:
            by_m[r["Matter"]] += money(r["91+ days"])
        top = max(by_m.items(), key=lambda kv: kv[1])
        out[f"ar_top_matter_share_{lab}"] = top[1] / o90
        out[f"ar_top_matter_{lab}"] = top[0]

    # ---- matter cycle time, matters closed in the last 12 months
    ml = rows(D("matter-list-export.csv"))
    win = (AS_OF - timedelta(days=364), AS_OF)
    by_area = defaultdict(list)
    for r in ml:
        if r["Closed"]:
            cl = datetime.strptime(r["Closed"], "%m/%d/%Y").date()
            op = datetime.strptime(r["Opened"], "%m/%d/%Y").date()
            if win[0] <= cl <= win[1] and cl >= op:
                by_area[r["Practice"]].append((cl - op).days)
    for a, v in by_area.items():
        out[f"cycle_days_{a.lower().replace(' ', '_')}"] = statistics.median(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(ROOT, "sample-data", "super-duper-law"))
    ap.add_argument("--out", default=os.path.join(ROOT, "evals", "ground_truth.json"))
    a = ap.parse_args()
    gt = compute(a.data)
    json.dump(gt, open(a.out, "w"), indent=1, sort_keys=True)
    print(f"Wrote {a.out}: {len(gt)} values")


if __name__ == "__main__":
    main()
