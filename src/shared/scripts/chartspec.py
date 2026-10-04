#!/usr/bin/env python3
"""Build chart specs straight from facts.json, so no number is retyped by hand.

Usage:
    python3 chartspec.py facts.json --list
    python3 chartspec.py facts.json --preset lead_sources_cost [--source "Google LSA"] [--area "Family law"] [--out block.json]
    python3 chartspec.py facts.json --scorecard --out spec.json          # a ready KPI row + charts page

A preset prints one chart block. Paste it into the "blocks" array of a page spec, edit the title
so it states the finding in your own words, then run render.py. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys

PRESETS = {
    "lead_sources_trend": "Cost per signed matter by paid source: 12-month average against last month (dumbbell). Question: where is the money working now, and where has that changed?",
    "lead_sources_cost": "Cost per signed matter by paid source (bar). Question: where is our marketing money working?",
    "lead_sources_rate": "Signed rate by lead source (bar). Question: which sources turn into clients?",
    "lead_sources_mix": "New leads by source (sorted bar). Question: where do our leads come from? Use this instead of a pie.",
    "cost_trend": "Cost per signed matter by month for one source against all paid sources (line).",
    "leads_trend": "New leads per week for one source against the firm (line). Question: did volume change?",
    "response_vs_signed": "Signed rate by how fast the first contact happened (bar). Question: does speed matter?",
    "speed_by_arrival": "Median time to first contact by when the lead arrived (bar).",
    "realization_by_area": "Realization before and now by practice area (dumbbell).",
    "realization_by_attorney": "Realization before and now by attorney within one practice area (dumbbell). People-level.",
    "realization_trend": "Realization by month for one practice area against the firm (line).",
    "ar_aging": "Receivables by age, two snapshots (stacked bar), 91+ days highlighted.",
    "ar_concentration": "Receivables over 90 days by matter (bar).",
    "revenue_by_area": "Collected revenue by practice area, now against the period before (dumbbell).",
    "scorecard": "KPI row for the headline numbers.",
}


def F(facts):
    return {f["id"]: f for f in facts}


def slug(s):
    return str(s).lower().replace(" ", "-")


def pick(facts, metric, **scope):
    for f in facts:
        if f["metric"] == metric and all(f["scope"].get(k) == v for k, v in scope.items()) and len(f["scope"]) == len(scope):
            return f
    return None


def win_note(f):
    w = f.get("window") or {}
    return w.get("label") or ""


def preset_lead_sources_cost(d, source=None, **_):
    facts = d["facts"]
    rows = [f for f in facts if f["metric"] == "cost_per_signed" and "source" in f["scope"] and f["scope"]["source"] != "All paid sources"]
    if not rows:
        raise SystemExit("No cost per signed matter facts. This needs a marketing spend file and the lead export.")
    items = []
    worst = max((f for f in rows if not f["thin"]), key=lambda f: f["value"], default=None)
    hl = source or (worst["scope"]["source"] if worst else None)
    for f in rows:
        items.append({"label": f["scope"]["source"], "value": f["value"], "display": f["display"],
                      "sample": f"{f['n']} signed", "thin": f["thin"], "highlight": f["scope"]["source"] == hl})
    month = rows[0]["window"]["label"]
    title = "Cost per signed matter, by paid source"
    if hl:
        f = next(x for x in rows if x["scope"]["source"] == hl)
        if f.get("prior") and f["prior"].get("value"):
            title = f"{hl} now costs {f['display']} per signed matter, up from {f['prior']['display']}"
    return {"type": "chart", "kind": "bar_h", "title": title, "unit": "usd", "lower_is_better": True,
            "subtitle": f"Marketing spend divided by matters signed, {month}. Sources with under 10 signed matters are flagged.",
            "data": items, "footnote": "Spend from the marketing spend sheet; signed matters from the lead export, by date signed."}


def preset_lead_sources_trend(d, source=None, **_):
    facts = d["facts"]
    now = {f["scope"]["source"]: f for f in facts if f["metric"] == "cost_per_signed" and f["scope"].get("source") not in (None, "All paid sources")}
    base = {f["scope"]["source"]: f for f in facts if f["metric"] == "cost_per_signed_12m" and f["scope"].get("source") not in (None, "All paid sources")}
    if not base:
        raise SystemExit("No 12-month cost per signed matter facts. Needs at least 6 months of spend plus the lead export.")
    items, thin = [], []
    for src, b in base.items():
        n = now.get(src)
        if not n or (n["n"] or 0) < 10 or (b["n"] or 0) < 10:
            thin.append(src)
            continue
        worse = n["change_class"] == "worsened" or (n["value"] > b["value"] * 1.25)
        items.append({"label": src, "before": b["value"], "after": n["value"], "highlight": (src == source) if source else
                      (worse and n["significance"]["level"] in ("clear", "likely"))})
    if not items:
        raise SystemExit("Every source is too thin to compare. Say so rather than charting it.")
    worst = max(items, key=lambda i: i["after"] / i["before"])
    if not any(i["highlight"] for i in items):
        worst["highlight"] = True
    w = next(iter(now.values()))["window"]["label"]
    sub = f"Marketing spend divided by matters signed. Last 12 months against {w}. Lower is better."
    if thin:
        sub += f" Left out as too thin to call: {', '.join(sorted(thin))}."
    return {"type": "chart", "kind": "dumbbell", "unit": "usd", "lower_is_better": True,
            "title": f"{worst['label']} was the cheapest way to sign a matter, and last month it cost {worst['after'] / worst['before']:.1f} times its average"
            if worst["after"] > worst["before"] * 1.25 else "Cost per signed matter by paid source, 12-month average and last month",
            "subtitle": sub, "before_label": "12-month average", "after_label": "Last month", "data": items, "order": "given"}


def preset_lead_sources_rate(d, source=None, **_):
    facts = d["facts"]
    rows = [f for f in facts if f["metric"] == "signed_rate_12m" and set(f["scope"]) == {"source"}]
    if not rows:
        raise SystemExit("No signed rate facts by source. Needs the lead export with an outcome (hired, signed or retained).")
    firm = pick(facts, "signed_rate_12m")
    firm_val = firm["value"] if firm else None
    real = [f for f in rows if not f["thin"]]
    best = max(real, key=lambda f: f["value"]) if real else None
    worst = min(real, key=lambda f: f["value"]) if real else None
    hl = source or (best["scope"]["source"] if best else None)
    items = [{"label": f["scope"]["source"], "value": f["value"], "display": f["display"],
              "sample": f"{f['n']} leads", "thin": f["thin"], "highlight": f["scope"]["source"] == hl} for f in rows]
    # when the top sources are within two points of each other, one accent would pick a winner that is not there
    tied = [i for i in items if best and not i["thin"] and best["value"] - i["value"] <= .02]
    if len(tied) > 1:
        for i in items:
            i["highlight"] = False
        if not source:
            for i in tied[:2]:
                i["highlight"] = True
    w = rows[0]["window"]["label"]
    title = "Share of leads that become signed matters, by source"
    if best and worst and best is not worst:
        top = sorted([f for f in real if best["value"] - f["value"] <= .02], key=lambda f: -f["value"])
        names = " and ".join(f["scope"]["source"] for f in top[:2])
        verb = "sign" if len(top) < 2 else "both sign"
        title = f"{names} leads {verb} at about {best['value'] * 100:.0f}%; {worst['scope']['source']} at {worst['display']}"
    return {"type": "chart", "kind": "bar_h", "title": title, "unit": "pct", "higher_is_better": True,
            "allow_multi_highlight": sum(1 for i in items if i["highlight"]) > 1,
            "subtitle": f"Signed divided by all leads, {w}. Newest leads are left out until they have had time to decide. "
                        "Sources under 10 leads are too thin to call.",
            "data": items, "ref": {"value": firm_val, "label": "All leads"} if firm_val is not None else None}


def preset_lead_sources_mix(d, source=None, **_):
    # lead_volume windows differ by source (the engine widens the window for small sources), so a mix is built from
    # lead_source_share, which uses one window for every source.
    rows = [f for f in d["facts"] if f["metric"] == "lead_source_share" and set(f["scope"]) == {"source"}]
    if not rows:
        raise SystemExit("No lead share by source. Needs the lead export with a source column.")
    top = max(rows, key=lambda f: f["value"])
    hl = source or top["scope"]["source"]
    items = [{"label": f["scope"]["source"], "value": f["value"], "display": f["display"], "sample": f"{f['n']} leads",
              "highlight": f["scope"]["source"] == hl} for f in rows]
    w = win_note(top)
    return {"type": "chart", "kind": "bar_h", "title": f"{top['scope']['source']} is {top['display']} of new leads, more than any other source",
            "unit": "pct", "data": items,
            "subtitle": "Share of new leads by source" + (f", {w}." if w else ".")}


def preset_cost_trend(d, source=None, **_):
    sers = {s["scope"].get("source"): s for s in d["series"] if s["id"].startswith("cost_per_signed.monthly")}
    src = source or "Google LSA"
    if src not in sers:
        raise SystemExit(f"No monthly cost series for {src}. Available: {sorted(k for k in sers if k)}")
    series = [{"name": src, "highlight": True, "points": sers[src]["points"]}]
    allp = sers.get("All paid sources")
    if allp:
        series.append({"name": "All paid sources", "points": allp["points"]})
    return {"type": "chart", "kind": "line", "title": f"Cost per signed matter, {src} against all paid sources", "unit": "usd",
            "lower_is_better": True, "granularity": "month", "series": series,
            "subtitle": "By month. Months with few signed matters swing a lot, so read the direction before the exact value."}


def preset_leads_trend(d, source=None, **_):
    sers = {s["scope"].get("source"): s for s in d["series"] if s["id"].startswith("lead_volume.weekly")}
    src = source
    series = []
    if src and src in sers:
        series.append({"name": src, "highlight": True, "points": sers[src]["points"]})
        series.append({"name": "All sources", "points": sers[None]["points"]})
        unit_note = "Weekly new leads."
    else:
        series.append({"name": "All sources", "highlight": True, "points": sers[None]["points"]})
        unit_note = "Weekly new leads."
    return {"type": "chart", "kind": "line", "title": "New leads per week" + (f", {src} against the firm" if src else ""),
            "unit": "count", "granularity": "week", "series": series, "subtitle": unit_note}


def preset_response_vs_signed(d, **_):
    rows = [f for f in d["facts"] if f["metric"] == "signed_rate_by_response"]
    if not rows:
        raise SystemExit("No response-time facts. This needs a log of when each lead arrived and was first contacted.")
    order = ["Within 1 hour", "1 to 4 hours", "4 to 24 hours", "Over 24 hours or never"]
    rows.sort(key=lambda f: order.index(f["scope"]["first_contact"]) if f["scope"]["first_contact"] in order else 9)
    items = [{"label": f["scope"]["first_contact"], "value": f["value"], "display": f["display"], "sample": f"{f['n']} leads",
              "highlight": i == 0, "thin": f["thin"]} for i, f in enumerate(rows)]
    fast, slow = rows[0], rows[-1]
    return {"type": "chart", "kind": "bar_h", "title": f"Leads reached within an hour sign at {fast['display']}; after a day, {slow['display']}",
            "unit": "pct", "higher_is_better": True, "order": "given", "data": items,
            "subtitle": "Signed rate by how long the first contact took. " + (win_note(fast) and f"Leads from {win_note(fast)}.")}


def preset_speed_by_arrival(d, **_):
    rows = [f for f in d["facts"] if f["metric"] == "speed_to_lead" and "arrival" in f["scope"]]
    if not rows:
        raise SystemExit("No speed to lead facts by arrival time.")
    items = [{"label": f["scope"]["arrival"], "value": f["value"], "display": f["display"], "sample": f"{f['n']} leads",
              "highlight": False} for f in rows]
    worst = max(items, key=lambda i: i["value"])
    worst["highlight"] = True
    return {"type": "chart", "kind": "bar_h", "title": f"{worst['label']} leads wait {worst['display']} for a first contact",
            "unit": "minutes", "lower_is_better": True, "data": items,
            "subtitle": "Median time from a lead arriving to the first reach-out."}


def preset_realization_by_area(d, **_):
    rows = [f for f in d["facts"] if f["metric"] == "realization" and set(f["scope"]) == {"practice_area"} and f.get("prior")]
    if not rows:
        raise SystemExit("No realization facts by practice area with a prior period.")
    items = [{"label": f["scope"]["practice_area"], "before": f["prior"]["value"], "after": f["value"],
              "highlight": f["status"] in ("red", "amber") and f["change_class"] == "worsened"} for f in rows]
    w = rows[0]
    return {"type": "chart", "kind": "dumbbell", "unit": "pct", "higher_is_better": True,
            "title": "Realization by practice area, before and now",
            "subtitle": f"Billed divided by worked, on work from {win_note(w)} against the 90 days before.",
            "before_label": "Before", "after_label": "Now", "data": items}


def preset_realization_by_attorney(d, area=None, **_):
    rows = [f for f in d["facts"] if f["metric"] == "realization_contribution" and (not area or f["scope"]["practice_area"] == area)]
    if not rows:
        raise SystemExit("No attorney-level realization facts. They appear for practice areas whose realization moved.")
    area = rows[0]["scope"]["practice_area"]
    rows = [f for f in rows if f["scope"]["practice_area"] == area]
    items = []
    for f in rows:
        items.append({"label": f["scope"]["attorney"], "before": f["attorney_prior_realization"],
                      "after": f["attorney_realization"], "highlight": (f.get("share_of_change") or 0) >= .5})
    return {"type": "chart", "kind": "dumbbell", "unit": "pct", "higher_is_better": True,
            "title": f"Where {area.lower()} realization moved, by attorney",
            "subtitle": "Billed divided by worked, before and now. A question to ask, not a verdict.",
            "before_label": "Before", "after_label": "Now", "data": items}


def preset_realization_trend(d, area=None, **_):
    sers = {s["scope"].get("practice_area"): s for s in d["series"] if s["id"].startswith("realization.monthly")}
    area = area or next((k for k in sers if k), None)
    if area not in sers:
        raise SystemExit(f"No monthly realization series for {area}.")
    series = [{"name": area, "highlight": True, "points": sers[area]["points"]}]
    if None in sers:
        series.append({"name": "All practice areas", "points": sers[None]["points"]})
    return {"type": "chart", "kind": "line", "title": f"{area} realization by month", "unit": "pct", "higher_is_better": True,
            "granularity": "month", "series": series, "y_zero": True,
            "subtitle": "Billed divided by worked, for work old enough to have been invoiced."}


def preset_ar_aging(d, **_):
    snaps = sorted([s for s in d["series"] if s["id"].startswith("ar_aging.")], key=lambda s: s["scope"]["snapshot"])
    if not snaps:
        raise SystemExit("No receivables aging snapshots.")
    from datetime import datetime
    rows = []
    for s in snaps[-2:]:
        dt = datetime.strptime(s["scope"]["snapshot"], "%Y-%m-%d")
        rows.append({"label": f"{dt.strftime('%b')} {dt.day}",
                     "parts": [{"name": p["x"], "value": p["y"], "highlight": p["x"] == "91+ days"} for p in s["points"]]})
    over = next((f for f in d["facts"] if f["metric"] == "ar_over_90"), None)
    title = "Receivables by age"
    if over and over.get("prior"):
        title = f"Receivables over 90 days went from {over['prior']['display']} to {over['display']}"
    return {"type": "chart", "kind": "stacked_bar", "title": title, "unit": "usd", "lower_is_better": True, "rows": rows,
            "subtitle": "Unpaid bills by how long they are past due."}


def preset_ar_concentration(d, **_):
    c = next((f for f in d["facts"] if f["metric"] == "ar_over_90_concentration"), None)
    if not c:
        raise SystemExit("No receivables concentration fact.")
    items = [{"label": m["matter"], "value": m["amount"], "highlight": i == 0, "sample": f"{m['share'] * 100:.0f}% of the total"}
             for i, m in enumerate(c["top_matters"])]
    return {"type": "chart", "kind": "bar_h", "title": f"One matter holds {c['display']} of receivables over 90 days", "unit": "usd",
            "lower_is_better": True, "data": items, "subtitle": "Largest matters by amount more than 90 days past due."}


def preset_revenue_by_area(d, **_):
    rows = [f for f in d["facts"] if f["metric"] == "collected_revenue" and set(f["scope"]) == {"practice_area"} and f.get("prior")]
    if not rows:
        raise SystemExit("No collected revenue by practice area with a prior period.")
    items = [{"label": f["scope"]["practice_area"], "before": f["prior"]["value"], "after": f["value"]} for f in rows]
    big = max(items, key=lambda i: abs(i["after"] - i["before"]))
    big["highlight"] = True
    return {"type": "chart", "kind": "dumbbell", "unit": "usd", "higher_is_better": True,
            "title": "Collected revenue by practice area, before and now",
            "subtitle": "Collected in the latest period against the period before. Contingency and flat fee revenue is lumpy.",
            "before_label": "Before", "after_label": "Now", "data": items}


def scorecard_items(d):
    facts = d["facts"]
    spec = [("cost_per_signed", {"source": "All paid sources"}), ("signed_rate", {}), ("speed_to_lead", {}),
            ("realization", {}), ("ar_over_90", {}), ("collected_revenue", {})]
    tiles = []
    for metric, sc in spec:
        f = pick(facts, metric, **sc)
        if not f:
            continue
        dd = None
        if f.get("prior") and f.get("delta_abs") is not None:
            dd = "up" if f["delta_abs"] > 0 else "down" if f["delta_abs"] < 0 else None
        delta = ""
        if f.get("delta_rel_display") and f["unit"] != "pct":
            delta = f["delta_rel_display"].lstrip("+-")
        elif f.get("delta_display"):
            delta = f["delta_display"].lstrip("+-").replace(" pts", " pts")
        pri = f.get("prior")
        wlab = win_note(f)
        if f.get("window") and f["window"].get("kind") == "snapshot":
            from datetime import datetime as _dt
            e = _dt.strptime(f["window"]["end"], "%Y-%m-%d")
            wlab = f"As of {e.strftime('%b')} {e.day}"
        word = {"flat": "normal range", "thin": "too thin", "changed": ""}.get(f["change_class"])
        tiles.append({"word": word if word is not None else None, "metric": f["metric"], "label": f["label"], "value": f["display"], "direction": f["direction"],
                      "status": f["status"], "delta": delta if f["change_class"] not in ("no_comparison",) else "",
                      "delta_dir": dd, "vs": f"vs {pri['display']} before" if pri else "", "n": f["n"],
                      "sample": ("Too thin to call" if f["thin"] else (wlab or ""))})
    return tiles


def build_scorecard(d):
    tiles = scorecard_items(d)
    for t in tiles:
        if t.get("word") is None:
            t.pop("word", None)
    blocks = [{"type": "kpi_row", "items": tiles[:3]}, {"type": "kpi_row", "items": tiles[3:6]}]
    return {"title": f"{d.get('firm') or 'Firm'} scorecard", "subtitle": f"As of {d['as_of']}", "kind": "charts",
            "meta": {"eyebrow": "Scorecard"}, "blocks": blocks,
            }


FUNCS = {"lead_sources_trend": preset_lead_sources_trend, "lead_sources_cost": preset_lead_sources_cost, "lead_sources_rate": preset_lead_sources_rate,
         "lead_sources_mix": preset_lead_sources_mix,
         "cost_trend": preset_cost_trend, "leads_trend": preset_leads_trend, "response_vs_signed": preset_response_vs_signed,
         "speed_by_arrival": preset_speed_by_arrival, "realization_by_area": preset_realization_by_area,
         "realization_by_attorney": preset_realization_by_attorney, "realization_trend": preset_realization_trend,
         "ar_aging": preset_ar_aging, "ar_concentration": preset_ar_concentration, "revenue_by_area": preset_revenue_by_area}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("facts")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--preset")
    ap.add_argument("--source")
    ap.add_argument("--area")
    ap.add_argument("--scorecard", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.list:
        for k, v in PRESETS.items():
            print(f"{k:26} {v}")
        return
    d = json.load(open(a.facts))
    if a.scorecard or a.preset == "scorecard":
        out = build_scorecard(d)
    elif a.preset in FUNCS:
        out = FUNCS[a.preset](d, source=a.source, area=a.area)
    else:
        sys.exit(f"Unknown preset. Run with --list. Got: {a.preset}")
    txt = json.dumps(out, indent=1)
    if a.out:
        open(a.out, "w").write(txt)
        print(f"Wrote {a.out}")
    else:
        print(txt)


if __name__ == "__main__":
    main()
