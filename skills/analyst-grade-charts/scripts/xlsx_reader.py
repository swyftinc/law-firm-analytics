#!/usr/bin/env python3
"""Read .xlsx files with the standard library only.

Returns every sheet as a list of rows. Dates are returned as datetime objects when the cell
carries a date number format. Formulas return their cached value. No pip installs, so it
works in sandboxes without network access.
"""
from __future__ import annotations

import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "pr": "http://schemas.openxmlformats.org/package/2006/relationships"}
BUILTIN_DATE_IDS = set(range(14, 23)) | set(range(27, 37)) | set(range(45, 48)) | set(range(50, 59))
EPOCH = datetime(1899, 12, 30)


def _col_index(ref):
    letters = re.match(r"([A-Z]+)", ref).group(1)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _is_date_format(code):
    code = code.lower()
    if code in ("general", "standard", "@"):
        return False
    code = re.sub(r'"[^"]*"', "", code)
    code = re.sub(r"\[[^\]]*\]", "", code)
    code = re.sub(r"\\.", "", code)
    return bool(re.search(r"[ymdhs]", code))


def _shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    out = []
    for si in root.findall("m:si", NS):
        out.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    return out


def _date_styles(z):
    if "xl/styles.xml" not in z.namelist():
        return set()
    root = ET.fromstring(z.read("xl/styles.xml"))
    custom = {}
    nf = root.find("m:numFmts", NS)
    if nf is not None:
        for f in nf.findall("m:numFmt", NS):
            custom[int(f.get("numFmtId"))] = f.get("formatCode", "")
    out = set()
    xfs = root.find("m:cellXfs", NS)
    if xfs is None:
        return out
    for i, xf in enumerate(xfs.findall("m:xf", NS)):
        fid = int(xf.get("numFmtId", "0"))
        if fid in BUILTIN_DATE_IDS or (fid in custom and _is_date_format(custom[fid])):
            out.add(i)
    return out


def _sheet_paths(z):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rmap = {r.get("Id"): r.get("Target") for r in rels.findall("pr:Relationship", NS)}
    out = []
    sheets = wb.find("m:sheets", NS)
    for s in sheets.findall("m:sheet", NS):
        rid = s.get("{%s}id" % NS["r"])
        target = rmap[rid]
        target = target.lstrip("/")
        path = target if target.startswith("xl/") else "xl/" + target
        out.append((s.get("name"), path, s.get("state", "visible")))
    return out


def _read_sheet(z, path, strings, date_styles):
    rows = []
    for _, el in ET.iterparse(z.open(path), events=("end",)):
        if el.tag != "{%s}row" % NS["m"]:
            continue
        row = []
        for c in el.findall("m:c", NS):
            idx = _col_index(c.get("r"))
            while len(row) < idx:
                row.append(None)
            t = c.get("t")
            v = c.find("m:v", NS)
            val = None
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            elif v is None or v.text is None:
                val = None
            elif t == "s":
                val = strings[int(v.text)]
            elif t in ("str", "e"):
                val = v.text
            elif t == "b":
                val = v.text == "1"
            else:
                num = float(v.text)
                if int(c.get("s", "0")) in date_styles:
                    val = EPOCH + timedelta(days=num)
                else:
                    val = int(num) if num == int(num) and abs(num) < 1e15 else num
            row.append(val)
        rows.append(row)
        el.clear()
    return rows


def read_xlsx(path):
    """Return {sheet name: rows} for every visible sheet."""
    with zipfile.ZipFile(path) as z:
        strings = _shared_strings(z)
        ds = _date_styles(z)
        out = {}
        for name, p, state in _sheet_paths(z):
            if state != "visible":
                continue
            out[name] = _read_sheet(z, p, strings, ds)
        return out


if __name__ == "__main__":
    for name, rows in read_xlsx(sys.argv[1]).items():
        print(name, len(rows))
        for r in rows[:5]:
            print(r)
