#!/usr/bin/env python3
"""Check that every number in a briefing or chart page came from facts.json.

Usage:
    python3 check_grounding.py memo.html --facts facts.json [--strict]
    python3 check_grounding.py page.html --facts facts.json --spec spec.json

Reads the visible text of an .html, .md or .txt file, pulls out each dollar amount, percentage,
duration, multiple and large count, and looks for it in facts.json (values, prior values, changes,
sample sizes, dollars at stake, series points). Anything it cannot find is reported as ungrounded.
Dates, years, and small counts under 10 are not checked. Standard library only.
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys

MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
DATE_RE = re.compile(rf"\b{MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?\b|\b\d{{1,2}}\s+{MONTHS}(?:\s+\d{{4}})?\b|\b(?:19|20)\d{{2}}(?:-\d{{2}}-\d{{2}})?\b|\b\d{{1,2}}(?::\d{{2}})?\s?(?:am|pm|a\.m\.|p\.m\.)", re.I)
TOKEN_RE = re.compile(r"""
    (?P<usd>-?\$\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:[KkMm]\b|million\b|thousand\b))?)
  | (?P<pts>\d+(?:\.\d+)?\s?(?:pts|points|percentage\ points)\b)
  | (?P<pct>\d+(?:\.\d+)?\s?%)
  | (?P<dur>\d+(?:\.\d+)?\s?(?:hours?|hrs?|minutes?|mins?|days?)\b)
  | (?P<mult>\d+(?:\.\d+)?\s?(?:x|times)\b)
  | (?P<num>\b\d{1,3}(?:,\d{3})+\b|\b\d{2,}(?:\.\d+)?\b)
""", re.X | re.I)


def visible_text(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.lower().endswith((".html", ".htm")):
        raw = re.sub(r"(?is)<(script|style|svg).*?</\1>", " ", raw)   # chart text is checked from the spec instead
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        raw = htmllib.unescape(raw)
    return re.sub(r"[ \t]+", " ", raw)


def allowed_numbers(d):
    out = []

    def add(kind, v):
        if v is not None and isinstance(v, (int, float)):
            out.append((kind, float(v)))

    for f in d["facts"]:
        u = f["unit"]
        vals = [f.get("value"), (f.get("prior") or {}).get("value"), f.get("delta_abs")]
        for v in vals:
            if v is None:
                continue
            if u == "pct":
                add("pct", v * 100)
                add("pts", v * 100)
            elif u == "pts":
                add("pts", v * 100)
                add("pct", v * 100)
            elif u == "usd":
                add("usd", v)
            elif u == "minutes":
                add("min", v)
            elif u == "days":
                add("days", v)
            else:
                add("count", v)
        if f.get("delta_rel") is not None:
            add("pct", f["delta_rel"] * 100)
        pv, v = (f.get("prior") or {}).get("value"), f.get("value")
        if pv and v:
            add("mult", v / pv)
            add("mult", pv / v)
        add("count", f.get("n"))
        add("count", (f.get("prior") or {}).get("n"))
        for k in ("signed", "spend", "billable", "billed", "p90_minutes"):
            if f.get(k) is not None:
                add("usd" if k in ("spend", "billable", "billed") else "min" if k == "p90_minutes" else "count", f[k])
        add("usd", f.get("impact_usd"))
        if f.get("share_of_change") is not None:
            add("pct", f["share_of_change"] * 100)
        for k in ("attorney_realization", "attorney_prior_realization", "share_of_billable"):
            if f.get(k) is not None:
                add("pct", f[k] * 100)
        for m in f.get("top_matters", []) or []:
            add("usd", m["amount"])
            add("pct", m["share"] * 100)
        w = f.get("window") or {}
        if w.get("kind") in ("t30", "t90", "t12m"):
            add("days", {"t30": 30, "t90": 90, "t12m": 365}[w["kind"]])
    for s in d.get("series", []):
        for p in s["points"]:
            u = s.get("unit")
            if u == "pct":
                add("pct", p["y"] * 100)
            elif u == "usd":
                add("usd", p["y"])
            elif u == "minutes":
                add("min", p["y"])
            else:
                add("count", p["y"])
            add("count", p.get("n"))
    for k in ("billing_lag_days", "lead_decision_lag_days"):
        add("days", d.get(k))
    return out


def tol_for(token, scale, decimals, cand):
    return max(abs(cand) * .02, .5 * scale * (10 ** -decimals), .5)


def check_token(kind, txt, allowed):
    t = txt.lower().replace(",", "").replace("$", "").strip()
    m = re.match(r"-?(\d+(?:\.\d+)?)", t)
    if not m:
        return None
    num = float(m.group(1))
    dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
    rest = t[m.end():].strip()
    scale = 1.0
    if kind == "usd":
        if rest.startswith(("k", "thousand")):
            num, scale = num * 1e3, 1e3
        elif rest.startswith(("m", "million")):
            num, scale = num * 1e6, 1e6
        pool = [v for k, v in allowed if k == "usd"]
    elif kind in ("pct", "pts"):
        pool = [v for k, v in allowed if k in ("pct", "pts")]
    elif kind == "dur":
        if rest.startswith(("hour", "hr")):
            pool = [v / 60.0 for k, v in allowed if k == "min"]
        elif rest.startswith(("min",)):
            pool = [v for k, v in allowed if k == "min"]
        else:
            pool = [v for k, v in allowed if k == "days"] + [v / 1440.0 for k, v in allowed if k == "min"]
    elif kind == "mult":
        pool = [v for k, v in allowed if k == "mult"]
    else:
        pool = [v for k, v in allowed if k == "count"] + ([v for k, v in allowed if k == "usd"] if num >= 1000 else [])
    if kind == "dur":   # thresholds like "over 90 days" or "within an hour" are definitions, not data
        defs = {"hour": [1, 4, 24, 48], "min": [60], "day": [7, 14, 21, 30, 45, 60, 90, 120, 180, 365]}
        key = "hour" if rest.startswith(("hour", "hr")) else "min" if rest.startswith("min") else "day"
        pool = pool + defs[key]
    return any(abs(num - c) <= tol_for(txt, scale, dec, c) for c in pool)


def scan(text, allowed):
    text = DATE_RE.sub(" ", text)
    found, bad = 0, []
    for m in TOKEN_RE.finditer(text):
        kind = m.lastgroup
        tok = m.group(0)
        if kind == "num":
            val = float(tok.replace(",", ""))
            if val < 10:
                continue
        found += 1
        ok = check_token(kind, tok, allowed)
        if not ok:
            ctx = text[max(0, m.start() - 40): m.end() + 30].replace("\n", " ")
            bad.append({"token": tok.strip(), "kind": kind, "context": ctx.strip()})
    return found, bad


def scan_spec(spec, allowed):
    """Chart data values must also trace to facts.json."""
    bad, n = [], 0
    pool = [v for _, v in allowed]

    def near(x):
        return any(abs(x - c) <= max(abs(c) * .01, 1e-6) for c in pool) or any(abs(x * 100 - c) <= max(abs(c) * .01, 1e-6) for c in pool)

    def walk(o, path=""):
        nonlocal n
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("value", "before", "after", "y") and isinstance(v, (int, float)):
                    n += 1
                    if not near(v):
                        bad.append({"token": str(v), "kind": "chart value", "context": f"{path}/{k}"})
                else:
                    walk(v, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(spec.get("blocks", []))
    return n, bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--facts", required=True)
    ap.add_argument("--spec")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    d = json.load(open(a.facts))
    allowed = allowed_numbers(d)
    found, bad = scan(visible_text(a.file), allowed)
    out = {"file": a.file, "numbers_checked": found, "ungrounded": bad}
    if a.spec:
        n, b2 = scan_spec(json.load(open(a.spec)), allowed)
        out["chart_values_checked"] = n
        out["ungrounded_chart_values"] = b2
        bad = bad + b2
    out["ok"] = not bad
    print(json.dumps(out, indent=1))
    if bad and a.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
