#!/usr/bin/env python3
"""Turn a memo spec into plain text for pasting into an email.

Usage:
    python3 memo_text.py memo-spec.json [--out monday-briefing.txt]

The first line is the subject (the memo title). Charts, tables and KPI tiles are left out, since
they do not survive a paste. No markdown symbols, no sign-off. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re


def clean(t):
    t = str(t).replace("\N{EM DASH}", ", ")
    return re.sub(r"\*\*(.+?)\*\*", r"\1", t)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    spec = json.load(open(a.spec))
    lines = [f"Subject: {clean(spec['title'])}", ""]
    for b in spec.get("blocks", []):
        t = b.get("type")
        if t in ("lede", "p"):
            lines += [clean(b["text"]), ""]
        elif t == "h2":
            lines += [clean(b["text"]), ""]
        elif t == "callout":
            lines += [f"{clean(b.get('label', 'Look at this first'))}: {clean(b['text'])}", ""]
        elif t == "note":
            lines += [f"{clean(b.get('label', 'Too thin to call'))}: {clean(b['text'])}", ""]
        elif t == "footnote":
            lines += [clean(b["text"]), ""]
    out = "\n".join(lines).rstrip() + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
        print(f"Wrote {a.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
