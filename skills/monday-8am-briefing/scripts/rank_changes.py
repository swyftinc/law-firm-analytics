#!/usr/bin/env python3
"""Rank what changed so a briefing can lead with what matters most.

Usage:
    python3 rank_changes.py facts.json [--out ranked.json] [--top 6]

Groups related facts into topics (one paid lead source, one practice area's realization,
receivables), scores each topic by the dollars it plausibly moves, and rates how sure we are.
It also lists what is too thin to call, and what moved but is inside normal variation, so a
briefing can say so out loud. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys


def by_id(facts):
    return {f["id"]: f for f in facts}


def real(f):
    return f["change_class"] in ("worsened", "improved") and f["significance"]["level"] in ("clear", "likely")


def build_topics(facts):
    topics = {}

    def topic(key, title):
        return topics.setdefault(key, {"key": key, "title": title, "headline": None, "members": [], "mechanism": [],
                                       "caveats": [], "people_level": False})

    resp = [f for f in facts if f["metric"] == "signed_rate_by_response"]
    gradient = None
    if len(resp) >= 2:
        fast = next((f for f in resp if f["scope"].get("first_contact") == "Within 1 hour"), None)
        slow = next((f for f in resp if f["scope"].get("first_contact") == "Over 24 hours or never"), None)
        if fast and slow and fast["n"] >= 30 and slow["n"] >= 15 and slow["value"] and fast["value"] >= 1.5 * slow["value"]:
            gradient = (fast, slow)

    for f in facts:
        m, sc = f["metric"], f["scope"]
        if m in ("cost_per_lead", "cost_per_signed", "signed_rate", "lead_volume", "lead_source_share", "after_hours_share") \
                and "source" in sc and sc["source"] != "All paid sources":
            topic(("source", sc["source"]), f"{sc['source']}: lead conversion and cost")["members"].append(f["id"])
        elif m in ("realization", "realization_contribution") and "practice_area" in sc:
            t = topic(("practice", sc["practice_area"]), f"{sc['practice_area']}: realization")
            t["members"].append(f["id"])
            if "attorney" in sc:
                t["people_level"] = True
        elif m in ("ar_total", "ar_over_90", "ar_over_90_share", "ar_over_90_concentration", "collection_rate"):
            topic(("receivables", None), "Receivables and collections")["members"].append(f["id"])
        elif m == "collected_revenue" and "attorney" not in sc:
            topic(("revenue", None), "Collected revenue")["members"].append(f["id"])
        elif m in ("speed_to_lead", "contacted_within_hour", "uncontacted_share", "signed_rate_by_response") or \
                (m == "after_hours_share" and not sc):
            topic(("intake", None), "Speed to lead")["members"].append(f["id"])
    F = by_id(facts)
    # attach attorney realization facts to the practice area where the attorney shows up
    att_area = {f["scope"]["attorney"]: f["scope"]["practice_area"] for f in facts if f["metric"] == "realization_contribution"}
    for f in facts:
        if f["metric"] == "realization" and "attorney" in f["scope"] and f["scope"]["attorney"] in att_area:
            t = topic(("practice", att_area[f["scope"]["attorney"]]), "")
            t["members"].append(f["id"])
            t["people_level"] = True

    out = []
    for key, t in topics.items():
        mem = [F[i] for i in t["members"]]
        kind = key[0]
        # headline: the member with the largest real dollar impact, else the largest real relative change
        cands = [f for f in mem if real(f) and f["metric"] not in ("lead_source_share",)]
        cands = [f for f in cands if not f["people_level"]] or cands
        if kind == "source":
            cands = [f for f in cands if f["metric"] in ("cost_per_signed", "signed_rate", "cost_per_lead")]
        if kind == "intake":
            cands = [f for f in cands if f["metric"] in ("speed_to_lead", "contacted_within_hour", "uncontacted_share")]
        if not cands:
            continue
        head = max(cands, key=lambda f: (abs(f["impact_usd"]) if f.get("impact_usd") else 0, abs(f.get("delta_rel") or 0)))
        impact = max([abs(f["impact_usd"]) for f in mem if real(f) and f.get("impact_usd")] or [0])
        t.update({"headline": head["id"], "impact_usd": impact or None, "direction": head["change_class"],
                  "confidence": head.get("confidence"), "corroboration": []})
        # corroboration and mechanism
        if kind == "source":
            ah = F.get(f"after_hours_share.{key[1].lower().replace(' ', '-')}")
            if ah and ah["change_class"] == "changed" and ah["significance"]["level"] == "clear" and gradient:
                fast, slow = gradient
                t["mechanism"] = [ah["id"], fast["id"], slow["id"]]
                t["corroboration"] = [f"{key[1]}'s mix of after-hours and weekend leads changed sharply "
                                      f"({ah['prior']['display']} to {ah['display']}), and across all leads, those reached within "
                                      f"an hour signed at {fast['display']} versus {slow['display']} when contact took over a day."]
                if head["direction"] if False else head["change_class"] == "worsened":
                    t["confidence"] = "high" if head.get("confidence") in ("low", "medium", "high") else t["confidence"]
        if kind == "practice":
            contribs = sorted([F[i] for i in t["members"] if F[i]["metric"] == "realization_contribution"],
                              key=lambda f: -(f.get("share_of_change") or 0))
            if contribs and (contribs[0].get("share_of_change") or 0) >= .5:
                c = contribs[0]
                t["mechanism"] = [c["id"]]
                t["corroboration"] = [f"{c['scope']['attorney']} accounts for about {c['share_of_change'] * 100:.0f}% of the change "
                                      f"in {key[1].lower()} realization ({c['attorney_prior_realization'] * 100:.0f}% to "
                                      f"{c['attorney_realization'] * 100:.0f}%)."]
                t["people_level"] = True
                t["caveats"].append("People-level finding. Frame it as a question to ask, not a verdict.")
                t["confidence"] = "high" if head.get("confidence") in ("medium", "high") else t["confidence"]
        if kind == "revenue":
            overall = next((f for f in mem if not f["scope"]), None)
            if overall and overall.get("delta_abs"):
                big = [f for f in mem if f["scope"] and f.get("lumpy") and f.get("delta_abs") is not None
                       and abs(f["delta_abs"]) >= .5 * abs(overall["delta_abs"])]
                if big:
                    t["lumpy"] = True
                    t["caveats"].append(f"Most of the change is {big[0]['scope_label']}, which is lumpy: a few large matters "
                                        "decide it. Read it as timing, not a trend.")
                    t["confidence"] = "low"
        if kind == "receivables":
            conc = next((F[i] for i in t["members"] if F[i]["metric"] == "ar_over_90_concentration"), None)
            if conc and conc["value"] >= .5:
                tm = conc.get("top_matters", [])
                t["mechanism"] = [conc["id"]]
                t["corroboration"] = [f"One matter holds {conc['value'] * 100:.0f}% of everything over 90 days."]
            t["confidence"] = "medium" if head.get("confidence") in ("medium", "high") else "low"
        for i in t["members"]:
            for c in F[i].get("caveats", []):
                if c not in t["caveats"]:
                    t["caveats"].append(c)
        out.append(t)
    # speed to lead is the mechanism behind a lead-source topic when one exists, so it supports rather than competes
    supported = any(t["mechanism"] and t["key"][0] == "source" for t in out)
    for t in out:
        t["supporting"] = bool(t["key"][0] == "intake" and supported)
        t.setdefault("lumpy", False)
    out.sort(key=lambda t: (-(t["impact_usd"] or 0), t["key"][0]))
    for i, t in enumerate(out, 1):
        t["rank"] = i
        t["key"] = list(t["key"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("facts")
    ap.add_argument("--out")
    ap.add_argument("--top", type=int, default=8)
    a = ap.parse_args(argv)
    d = json.load(open(a.facts))
    facts = d["facts"]
    topics = build_topics(facts)
    F = by_id(facts)
    thin = []
    for f in facts:
        if f["thin"] and f["metric"] in ("signed_rate", "cost_per_signed", "realization", "speed_to_lead") and f["n"]:
            ov = F.get(f"{f['metric']}.all")
            tempt = abs(f["value"] - ov["value"]) / ov["value"] if ov and ov["value"] else 0
            thin.append({"id": f["id"], "display": f["display"], "n": f["n"], "label": f["label"], "scope": f["scope_label"],
                         "vs_firm_wide": ov["display"] if ov else None, "tempting": round(tempt, 2)})
    thin.sort(key=lambda x: -x["tempting"])
    flat = []
    for f in facts:
        if not f["scope"] and f["change_class"] == "flat" and f.get("delta_rel") is not None and abs(f["delta_rel"]) >= .04 \
                and f["metric"] in ("lead_volume", "signed_rate", "cost_per_signed", "collection_rate", "realization"):
            flat.append({"id": f["id"], "label": f["label"], "display": f["display"], "prior": f["prior"]["display"],
                         "delta": f.get("delta_rel_display"), "p": f["significance"]["p"]})
    main_topics = [t for t in topics if not t["supporting"]]
    # A finding needs more than one swing in one group: real support (high confidence) or a mechanism that explains it.
    firm = [t for t in main_topics if t["confidence"] == "high" or t["corroboration"] or
            (t["confidence"] == "medium" and not t["lumpy"] and t["key"][0] in ("receivables", "revenue"))]
    unconfirmed = [t for t in main_topics if t not in firm]
    look_at = [t for t in firm if t["direction"] == "worsened"]
    going_well = [t for t in firm if t["direction"] == "improved"]
    out = {"as_of": d["as_of"],
           "guidance": "Lead with the first item in look_at unless going_well holds something far larger that is high "
                       "confidence and not lumpy. Supporting topics explain a look_at item and belong inside it. "
                       "unconfirmed items are single swings with no mechanism behind them: do not lead with them, and "
                       "mention at most one as 'worth watching'. If look_at and going_well are both empty, it was a quiet "
                       "week: say so plainly and keep the memo short.",
           "look_at": look_at[:a.top], "going_well": going_well[:4],
           "supporting": [t for t in topics if t["supporting"]],
           "unconfirmed": unconfirmed[:4],
           "too_thin_to_call": thin[:6], "moved_within_normal_variation": flat,
           "unavailable": d.get("unavailable", []), "skipped": d.get("skipped", []), "warnings": d.get("warnings", [])}
    txt = json.dumps(out, indent=1, default=str)
    if a.out:
        open(a.out, "w").write(txt)
        print(f"Wrote {a.out}: {len(topics)} topics.")
    else:
        print(txt)


if __name__ == "__main__":
    main()
