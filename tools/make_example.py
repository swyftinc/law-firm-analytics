#!/usr/bin/env python3
"""Build the worked example memo and the example scorecard from the sample data.

Every number is read from facts.json, so the example can never drift from the engine.
Writes docs/example/*.json, then render.py turns them into HTML.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "src", "shared", "scripts")
OUT = os.path.join(ROOT, "docs", "example")
os.makedirs(OUT, exist_ok=True)


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True, check=True).stdout


def main():
    facts_path = os.path.join(OUT, "facts.json")
    run(os.path.join(S, "compute_facts.py"), "--mapping", os.path.join(ROOT, "sample-data/super-duper-law/mapping.json"),
        "--out", facts_path)
    run(os.path.join(S, "rank_changes.py"), facts_path, "--out", os.path.join(OUT, "ranked.json"))
    d = json.load(open(facts_path))
    F = {f["id"]: f for f in d["facts"]}
    g = lambda i: F[i]
    cps, sr, lv = g("cost_per_signed.google-lsa"), g("signed_rate.google-lsa"), g("lead_volume.google-lsa")
    ah, fast, slow = g("after_hours_share.google-lsa"), g("signed_rate_by_response.within-1-hour"), g("signed_rate_by_response.over-24-hours-or-never")
    fam, wren, con = g("realization.family-law"), g("realization.wren-kowalczyk"), g("realization_contribution.family-law_wren-kowalczyk")
    ar, conc = g("ar_over_90.all"), g("ar_over_90_concentration.01266-delacroix")
    thin, vol = g("signed_rate.wealth-advisor-referral"), g("lead_volume.all")

    def block(preset, *extra):
        b = json.loads(run(os.path.join(S, "chartspec.py"), facts_path, "--preset", preset, *extra))
        b["compact"] = True
        return b

    blocks = [
        {"type": "lede", "text": f"Google LSA now costs **{cps['display']} per signed matter**, up from {cps['prior']['display']} in August, "
                                 f"on the same lead volume: {lv['display']} leads in the last 30 days against {lv['prior']['display']} before. "
                                 f"The likely cause is when those leads arrive and how long they wait."},
        {"type": "h2", "text": "LSA leads now arrive after hours, when first contact is slow"},
        {"type": "p", "text": f"Cost per signed matter went from {cps['prior']['display']} to {cps['display']}, September against August. "
                              f"Only {cps['n']} matters signed in September against {cps['prior']['n']} in August, so treat the size as approximate. "
                              f"Over the last month, {sr['display']} of LSA leads have signed, against {sr['prior']['display']} the month before. "
                              f"That's a likely drop, not a certain one. If it holds, it is worth about ${sr['impact_usd'] / 1000:,.0f}K in estimated fees "
                              f"on those leads, using the firm's own estimated value field."},
        {"type": "p", "text": f"The likely reason is timing. After-hours and weekend leads were {ah['prior']['display']} of LSA leads and are now {ah['display']}. "
                              f"Across every source, leads reached within an hour signed at {fast['display']}, and leads that waited more than a day or were never "
                              f"reached signed at {slow['display']}. More leads arriving after hours, and waiting longer for a first contact, could account for much of this drop. "
                              f"Lead quality could also have slipped, and these numbers can't rule that out."},
        block("response_vs_signed"),
        {"type": "h2", "text": "Family law realization fell, mostly on one attorney's matters"},
        {"type": "p", "text": f"Family law realization is {fam['display']}, against {fam['prior']['display']} the 90 days before, on {fam['n']} time entries. "
                              f"That is about ${fam['impact_usd'] / 1000:,.0f}K of recorded work that did not reach a bill. "
                              f"About {con['share_of_change'] * 100:.0f}% of the change sits on one attorney's matters, {wren['prior']['display']} down to {wren['display']}. "
                              f"It's worth asking what changed on those matters: a rate, a dispute, a new matter type."},
        {"type": "h2", "text": "Receivables over 90 days are up, and one matter holds most of it"},
        {"type": "p", "text": f"Receivables more than 90 days past due rose from {ar['prior']['display']} to {ar['display']} between the two aging reports, "
                              f"up {ar['delta_rel_display'].lstrip('+')}. One matter holds {conc['value'] * 100:.0f}% of that total, so this is a collections conversation about one account, "
                              f"not a slide across the firm."},
        {"type": "callout", "label": "Look at this first",
         "text": "Pull September's LSA leads that arrived after 6pm or on a weekend and check how long each one waited for a first contact."},
        {"type": "note", "label": "Too thin to call",
         "text": f"A new wealth advisor referral source has four leads that reached a decision, and all four signed. That's too few to call it your best source."},
        {"type": "p", "text": f"New leads are up {vol['delta_rel_display'].lstrip('+')} ({vol['display']} against {vol['prior']['display']}). That's inside normal variation."},
        {"type": "footnote", "text": f"As of October 4, 2026. Leads and speed to lead cover the last 30 days. Realization covers the 90 days ending {d['billing_lag_days']} days ago, "
                                      f"so the work has had time to be invoiced. Receivables compare the two aging reports. Dollars at stake use the firm's estimated "
                                      f"value field. Every number is computed from the firm's exports."},
    ]
    memo = {"title": "Google LSA cost per signed matter nearly doubled in September", "kind": "memo",
            "meta": {"eyebrow": f"Monday briefing, Super Duper Law, {'October 5, 2026'}"}, "blocks": blocks}
    json.dump(memo, open(os.path.join(OUT, "memo-spec.json"), "w"), indent=1)
    write_reference(memo)
    # scorecard
    sc = json.loads(run(os.path.join(S, "chartspec.py"), facts_path, "--scorecard"))
    pages = [json.loads(run(os.path.join(S, "chartspec.py"), facts_path, "--preset", p, *a)) for p, a in [
        ("lead_sources_cost", []), ("cost_trend", ["--source", "Google LSA"]), ("realization_by_attorney", ["--area", "Family law"]),
        ("ar_aging", [])]]
    spec = {"title": "Super Duper Law scorecard", "subtitle": f"As of {d['as_of']}", "kind": "charts",
            "meta": {"eyebrow": "Scorecard", "source": "Source: the firm's exports, computed on the sample data."},
            "blocks": sc["blocks"] + pages}
    json.dump(spec, open(os.path.join(OUT, "scorecard-spec.json"), "w"), indent=1)
    print("wrote", OUT)


def write_reference(memo):
    """The worked example the briefing skill studies. Written from the same spec, so it cannot drift."""
    sys.path.insert(0, S)
    import memo_text  # noqa: F401  (clean() is reused below)
    lines = []
    for b in memo["blocks"]:
        t = b["type"]
        if t in ("lede", "p"):
            lines.append(memo_text.clean(b["text"]))
        elif t == "h2":
            lines.append("### " + memo_text.clean(b["text"]))
        elif t == "callout":
            lines.append(f"**{b.get('label', 'Look at this first')}:** " + memo_text.clean(b["text"]))
        elif t == "note":
            lines.append(f"**{b.get('label', 'Too thin to call')}:** " + memo_text.clean(b["text"]))
        elif t == "footnote":
            lines.append("*" + memo_text.clean(b["text"]) + "*")
        elif t == "chart":
            lines.append(f"[chart: {b.get('title', '')}]")
    body = "\n\n".join(lines)
    text = f"""# Example briefing

A worked example, written from the sample firm's numbers (Super Duper Law, as of October 4, 2026). Study its shape. Never reuse its sentences or its numbers: every memo you write comes from the firm's own `facts.json`, and `check_grounding.py` will fail any number that is not in it.

## The memo

# {memo_text.clean(memo['title'])}

{body}

## What to notice

The headline is the finding, with its size. The lede gives the number, the comparison and the sample, and says what probably explains it, in two sentences.

The first finding states the change, then the sample ("only 12 matters signed"), then the strength of the evidence ("a likely drop, not a certain one"), then the dollars at stake with the method in one clause. The next paragraph gives the mechanism as a hypothesis with its evidence, and names another explanation the numbers cannot rule out. The chart under it answers the one question the memo raises, whether speed to first contact matters.

The second finding is about one attorney's matters. It states the share of the change that sits there, frames it as a question to ask, and names no verdict. The third finding says the money is concentrated in one matter, which turns a firm-wide worry into a collections conversation.

"Look at this first" is one specific check a person can do before the meeting. "Too thin to call" names the tempting number and says why it cannot carry a conclusion. The line on normal variation tells the reader what not to chase. The footnote gives the as-of date, the windows and how the numbers were made.

Every number on the page appears in `facts.json`. Nothing is rounded in a way that changes its meaning. No sentence could appear in a consulting deck for any other firm.
"""
    out = os.path.join(ROOT, "src", "shared", "references", "example-briefing.md")
    open(out, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
