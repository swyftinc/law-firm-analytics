#!/usr/bin/env python3
"""Look at the files a firm exported and say what they are.

Usage:
    python3 inspect_data.py FILE [FILE ...] [--draft mapping.json] [--pretty]

For each file it reports the real header row, the columns and what is in them, and whether the
columns match a known Clio report. With --draft it writes a first-pass mapping.json that Claude
then reviews, fixes and confirms with the person. Nothing here changes the files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (Table, date_fraction, load_tables, numeric_fraction, parse_column_dates, parse_num,  # noqa: E402
                    _blank)
from schema import ENTITIES, PRESETS, SYNONYMS  # noqa: E402


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def profile_column(name, values):
    vals = [v for v in values if not _blank(v)]
    out = {"name": name, "non_null": len(vals), "null": len(values) - len(vals)}
    if not vals:
        out["kind"] = "empty"
        return out
    df = date_fraction(values)
    nf = numeric_fraction(values)
    if df >= .8:
        kind = "date"
    elif nf >= .9:
        kind = "number"
    else:
        kind = "text"
    out["kind"] = kind
    out["sample"] = [str(v)[:60] for v in vals[:3]]
    distinct = {}
    for v in vals:
        distinct[str(v)] = distinct.get(str(v), 0) + 1
    out["distinct"] = len(distinct)
    if kind == "date":
        parsed = [d for d in parse_column_dates(values) if d]
        if parsed:
            out["min"], out["max"] = min(parsed).strftime("%Y-%m-%d"), max(parsed).strftime("%Y-%m-%d")
    elif kind == "number":
        nums = [x for x in (parse_num(v) for v in values) if x is not None]
        if nums:
            out["min"], out["max"] = min(nums), max(nums)
    elif len(distinct) <= 25:
        out["values"] = dict(sorted(distinct.items(), key=lambda kv: -kv[1]))
    return out


def match_preset(header):
    hs = {norm(h) for h in header}
    best, best_score = None, 0.0
    for key, p in PRESETS.items():
        sig = p["signature"]
        score = sum(1 for c in sig if norm(c) in hs) / float(len(sig))
        if score > best_score:
            best, best_score = key, score
    if best and best_score >= .7:
        return best, round(best_score, 2)
    return None, round(best_score, 2)


KIND_OK = {"date": {"date"}, "number": {"number"}, "text": {"text", "number"}, "key": {"text", "number"}}


def guess_columns(entity, header, prof):
    kinds = {p["name"]: p["kind"] for p in prof}
    fields = ENTITIES[entity]["fields"]
    taken, found = set(), {}
    for fld, fkind in fields.items():
        syns = SYNONYMS.get(fld, [])
        cand = None
        for syn in syns:
            for h in header:
                if h in taken:
                    continue
                if norm(h) == norm(syn) and kinds.get(h) in KIND_OK[fkind]:
                    cand = h
                    break
            if cand:
                break
        if not cand:
            for syn in syns:
                if len(norm(syn)) < 4:
                    continue
                for h in header:
                    if h in taken:
                        continue
                    if norm(syn) in norm(h) and kinds.get(h) in KIND_OK[fkind]:
                        cand = h
                        break
                if cand:
                    break
        if cand:
            found[fld] = cand
            taken.add(cand)
    return found


def guess_entities(header, prof):
    out = []
    for ent, spec in ENTITIES.items():
        cols = guess_columns(ent, header, prof)
        req = spec["required"]
        have = sum(1 for r in req if r in cols)
        if have == 0:
            continue
        out.append({"entity": ent, "confidence": round(have / float(len(req)), 2), "columns": cols,
                    "missing_required": [r for r in req if r not in cols]})
    out.sort(key=lambda d: (-d["confidence"], -len(d["columns"])))
    return out[:3]


def date_from_name(path):
    m = re.search(r"(20\d{2})[-_.](\d{1,2})[-_.](\d{1,2})", os.path.basename(path))
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"(\d{1,2})[-_.](\d{1,2})[-_.](20\d{2})", os.path.basename(path))
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return None


def inspect_table(t, base):
    header = t.header
    cols = [profile_column(h, t.column(h)) for h in header]
    info = {"path": os.path.relpath(t.path, base) if base else t.path, "sheet": t.sheet,
            "n_rows": len(t.rows), "header_row": len(t.title_rows) + 1,
            "title_rows_skipped": [[str(c) for c in r if not _blank(c)] for r in t.title_rows if any(not _blank(c) for c in r)],
            "total_rows_dropped": t.dropped, "columns": cols}
    key, score = match_preset(header)
    notes = []
    if key:
        p = PRESETS[key]
        info["match"] = {"preset": key, "system": p["system"], "report": p["report"], "confidence": score}
        entity = p["entity"]
        cols_map = {k: v for k, v in p["columns"].items()
                    if all(c in header for c in (v if isinstance(v, list) else [v]))}
        draft = {"path": info["path"], "sheet": t.sheet, "entity": entity, "columns": cols_map}
        if p.get("value_maps"):
            draft["value_maps"] = p["value_maps"]
        needs = []
        for nf in p.get("needs_value_map", []):
            c = cols_map.get(nf)
            prof = next((x for x in cols if x["name"] == c), None)
            if prof and "values" in prof:
                needs.append({"value_map": nf, "column": c, "values": list(prof["values"].keys()),
                              "why": "Group these into the firm's practice areas, or leave them as they are."})
            elif prof:
                needs.append({"value_map": nf, "column": c, "why": "Many distinct values; group them if useful."})
        fl = {}
        for k in p.get("needs_file_level", []):
            if k == "snapshot_date":
                d = date_from_name(t.path)
                if d:
                    fl[k] = d
                    notes.append("snapshot_date read from the file name. Confirm it.")
                else:
                    needs.append({"file_level": k, "why": "What date was this export run? It is not in the file."})
            else:
                needs.append({"file_level": k, "why": "What date range does this report cover? It is not in the file."})
        if fl:
            draft["file_level"] = fl
        info["suggested_mapping"] = draft
        info["needs"] = needs
        missing = [k for k, v in p["columns"].items() if k not in cols_map]
        if missing:
            notes.append("Preset columns not found in this file: " + ", ".join(missing))
    else:
        info["match"] = None
        info["entity_guess"] = guess_entities(header, cols)
        notes.append("Not a known Clio report. Check entity_guess, then write the mapping by meaning.")
        top = info["entity_guess"][0] if info["entity_guess"] else None
        if top and top["confidence"] >= .99:
            draft = {"path": info["path"], "sheet": t.sheet, "entity": top["entity"], "columns": top["columns"],
                     "guess": True}
            needs = []
            for fld in ("outcome", "status", "practice_area"):
                c = top["columns"].get(fld)
                prof = next((x for x in cols if x["name"] == c), None)
                if prof and "values" in prof:
                    needs.append({"value_map": fld, "column": c, "values": list(prof["values"].keys()),
                                  "why": "Map these to the firm's meaning: outcome to signed, lost or open; status to open or closed."
                                  if fld != "practice_area" else "Group these into practice areas if useful."})
            for k in ENTITIES[top["entity"]].get("file_level", []):
                needs.append({"file_level": k, "why": "Not in the file. Ask the person, or read it from the file name."})
            info["suggested_mapping"] = draft
            info["needs"] = needs
            notes.append("Guessed from the column names. Confirm the columns, then add any value maps listed in needs.")
    if t.dropped:
        notes.append(f"{t.dropped} total or subtotal row(s) will be ignored.")
    info["notes"] = notes
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--draft", help="write a first-pass mapping.json here")
    ap.add_argument("--pretty", action="store_true")
    a = ap.parse_args(argv)
    base = os.path.dirname(os.path.abspath(a.draft)) if a.draft else os.getcwd()
    files = []
    for f in a.files:
        if not os.path.exists(f):
            files.append({"path": f, "error": "File not found."})
            continue
        try:
            for t in load_tables(f):
                files.append(inspect_table(t, base))
        except Exception as e:  # report and keep going
            files.append({"path": f, "error": f"{type(e).__name__}: {e}"})
    out = {"files": files}
    if a.draft:
        draft = {"as_of": None, "files": [x["suggested_mapping"] for x in files if x.get("suggested_mapping")],
                 "profile": {}}
        with open(a.draft, "w") as fh:
            json.dump(draft, fh, indent=2)
        out["draft_written"] = a.draft
        out["unmatched"] = [x["path"] for x in files if not x.get("suggested_mapping") and not x.get("error")]
    json.dump(out, sys.stdout, indent=2 if a.pretty else None, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
