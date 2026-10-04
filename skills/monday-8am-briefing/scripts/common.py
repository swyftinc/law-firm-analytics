#!/usr/bin/env python3
"""Shared helpers: read tables, parse dates and numbers, small statistics.

Standard library only. Python 3.8+.
"""
from __future__ import annotations

import csv
import io
import math
import os
import re
from datetime import date, datetime, timedelta

try:
    from xlsx_reader import read_xlsx
except ImportError:  # imported as a package
    from .xlsx_reader import read_xlsx

# ----------------------------------------------------------------------------- tables


class Table:
    def __init__(self, path, sheet, header, rows, title_rows, dropped):
        self.path = path
        self.sheet = sheet
        self.header = header
        self.rows = rows
        self.title_rows = title_rows
        self.dropped = dropped

    def column(self, name):
        i = self.header.index(name)
        return [r[i] if i < len(r) else None for r in self.rows]

    def records(self):
        for r in self.rows:
            yield {h: (r[i] if i < len(r) else None) for i, h in enumerate(self.header)}


def _blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


def _is_number_like(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return True
    if isinstance(v, datetime):
        return True
    if isinstance(v, str):
        s = v.strip().replace(",", "").replace("$", "")
        return bool(re.fullmatch(r"\(?-?\d+(\.\d+)?\)?%?", s))
    return False


def find_header_row(rows, max_scan=30):
    """Index of the header row. Skips title lines, blank lines and notes above the table."""
    scan = rows[:max_scan]
    widths = [sum(0 if _blank(c) else 1 for c in r) for r in scan]
    if not widths or max(widths) == 0:
        return 0
    top = max(widths)
    for i, r in enumerate(scan):
        cells = [c for c in r if not _blank(c)]
        if len(cells) < max(2, int(.6 * top)):
            continue
        texty = sum(1 for c in cells if isinstance(c, str) and not _is_number_like(c))
        if texty / len(cells) < .8:
            continue
        return i
    return 0


TOTAL_RE = re.compile(r"^\s*(grand\s+|sub|matter\s+|client\s+|attorney\s+|report\s+)?totals?\b", re.I)


def _dedupe(names):
    seen, out = {}, []
    for n in names:
        n = ("" if n is None else str(n)).strip() or "column"
        if n in seen:
            seen[n] += 1
            n = f"{n}.{seen[n]}"
        else:
            seen[n] = 1
        out.append(n)
    return out


def rows_to_table(raw, path, sheet=None):
    raw = [list(r) for r in raw]
    h = find_header_row(raw)
    header = _dedupe(raw[h])
    n = len(header)
    body, dropped = [], 0
    for r in raw[h + 1:]:
        if all(_blank(c) for c in r):
            continue
        lead = [c for c in r[:3] if isinstance(c, str)]
        if any(TOTAL_RE.match(c) for c in lead):
            dropped += 1
            continue
        r = list(r) + [None] * (n - len(r))
        body.append(r[:n])
    return Table(path, sheet, header, body, raw[:h], dropped)


def _decode(path):
    data = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeError:
            continue
    return data.decode("latin-1", errors="replace")


def load_tables(path, sheet=None):
    """Return a list of Tables: one per CSV, one per (visible) sheet of an xlsx."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        out = []
        for name, rows in read_xlsx(path).items():
            if sheet and name != sheet:
                continue
            if not rows or all(all(_blank(c) for c in r) for r in rows):
                continue
            out.append(rows_to_table(rows, path, name))
        return out
    if ext == ".xls":
        raise ValueError("Old .xls files are not supported. In Excel, use Save As and pick .xlsx or CSV.")
    text = _decode(path)
    try:
        dialect = csv.Sniffer().sniff(text[:5000], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    return [rows_to_table(rows, path, None)]


# ----------------------------------------------------------------------------- parsing

DATE_FORMATS = [
    "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M",
    "%m/%d/%Y", "%m/%d/%Y %I:%M %p", "%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M", "%m/%d/%Y %H:%M:%S", "%m/%d/%y",
    "%m/%d/%y %I:%M %p", "%d/%m/%Y", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%y", "%m-%d-%Y", "%d-%m-%Y",
    "%Y/%m/%d", "%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%d %b %Y", "%d-%b-%Y", "%d-%b-%y",
    "%b %Y", "%B %Y", "%b-%y", "%Y-%m", "%m/%Y",
]
EXCEL_EPOCH = datetime(1899, 12, 30)


def parse_date(v, fmt=None):
    """Return a datetime, or None. `fmt` pins the format once a column has been detected."""
    if _blank(v):
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if 20000 < v < 70000:
            return EXCEL_EPOCH + timedelta(days=float(v))
        return None
    s = str(v).strip()
    fmts = [fmt] if fmt else DATE_FORMATS
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            continue
    return None


def detect_date_format(values, sample=80):
    """Pick the one format that parses nearly every value. Day-first only if the data forces it."""
    vals = [v for v in values if isinstance(v, str) and v.strip()][:sample]
    if not vals:
        return None
    best, best_score = None, 0.0
    for f in DATE_FORMATS:
        ok = 0
        for s in vals:
            try:
                datetime.strptime(s.strip(), f)
                ok += 1
            except ValueError:
                pass
        score = ok / len(vals)
        if score > best_score + 1e-9:
            best, best_score = f, score
    return best if best_score >= .9 else None


def parse_column_dates(values):
    """Parse a whole column with a single detected format. Returns a list of datetimes or None."""
    fmt = detect_date_format(values)
    return [parse_date(v, fmt) for v in values]


def date_fraction(values, sample=200):
    """Share of non-empty values that look like dates (used to guess which columns are dates)."""
    vals = [v for v in values if not _blank(v)][:sample]
    if not vals:
        return 0.0
    if all(isinstance(v, (datetime, date)) for v in vals):
        return 1.0
    strs = [v for v in vals if isinstance(v, str)]
    if len(strs) < len(vals) * .8:
        return 0.0
    f = detect_date_format(strs)
    if not f:
        return 0.0
    # a bare 4 digit year or small integer is not a date
    return sum(1 for s in strs if parse_date(s, f)) / len(vals)


def parse_num(v):
    if _blank(v):
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", " ")
    if s in ("-", "--", "n/a", "N/A", "NA", "null", "None"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[()$€£\s,]", "", s).rstrip("%")
    if s.startswith("-"):
        neg, s = True, s[1:]
    try:
        x = float(s)
    except ValueError:
        return None
    return -x if neg else x


def numeric_fraction(values, sample=200):
    vals = [v for v in values if not _blank(v)][:sample]
    if not vals:
        return 0.0
    return sum(1 for v in vals if parse_num(v) is not None) / len(vals)


# ----------------------------------------------------------------------------- statistics


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def percentile(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return xs[int(k)] if f == c else xs[f] + (xs[c] - xs[f]) * (k - f)


def norm_cdf(z):
    return .5 * (1 + math.erf(z / math.sqrt(2)))


def p_two_sided(z):
    return 2 * (1 - norm_cdf(abs(z)))


def two_prop_z(x1, n1, x0, n0):
    """z for the difference of two proportions (pooled)."""
    if n1 <= 0 or n0 <= 0:
        return None
    p = (x1 + x0) / float(n1 + n0)
    se = math.sqrt(max(p * (1 - p) * (1.0 / n1 + 1.0 / n0), 1e-12))
    return (x1 / float(n1) - x0 / float(n0)) / se


def count_ratio_z(a, b):
    """z for two Poisson counts over equal exposure."""
    if a + b == 0:
        return 0.0
    return (a - b) / math.sqrt(a + b)


def log_ratio_z(c1, n1, c0, n0):
    """z for a ratio of two rates whose denominators are counts (cost per signed matter)."""
    if min(c1, c0) <= 0 or n1 <= 0 or n0 <= 0:
        return None
    return math.log(c1 / c0) / math.sqrt(1.0 / n1 + 1.0 / n0)


def mannwhitney_z(x, y):
    """Normal approximation of the Mann-Whitney U test. Positive z means x tends higher than y."""
    n1, n2 = len(x), len(y)
    if n1 < 3 or n2 < 3:
        return None
    pooled = sorted([(v, 0) for v in x] + [(v, 1) for v in y])
    ranks, i = [0.0] * len(pooled), 0
    tie_term = 0.0
    while i < len(pooled):
        j = i
        while j + 1 < len(pooled) and pooled[j + 1][0] == pooled[i][0]:
            j += 1
        r = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        t = j - i + 1
        tie_term += t ** 3 - t
        i = j + 1
    r1 = sum(r for r, (_, g) in zip(ranks, pooled) if g == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    n = n1 + n2
    var = n1 * n2 / 12.0 * ((n + 1) - tie_term / (n * (n - 1)))
    if var <= 0:
        return None
    return (u1 - mu) / math.sqrt(var)


def ratio_z(num1, den1, num0, den0):
    """z for the difference between two weighted ratios sum(num)/sum(den) (realization, collection).

    Inputs are lists of per-row numerators and denominators. Uses the linearized variance of a
    ratio estimator, so large rows count for more, the way dollars do.
    """
    def est(num, den):
        d = float(sum(den))
        if d <= 0 or len(num) < 3:
            return None, None
        r = sum(num) / d
        var = sum((n - r * m) ** 2 for n, m in zip(num, den)) / (d * d)
        return r, var

    r1, v1 = est(num1, den1)
    r0, v0 = est(num0, den0)
    if r1 is None or r0 is None or (v1 + v0) <= 0:
        return None
    return (r1 - r0) / math.sqrt(v1 + v0)


# ----------------------------------------------------------------------------- windows


def month_start(d):
    return date(d.year, d.month, 1)


def add_months(d, n):
    y, m = divmod(d.year * 12 + d.month - 1 + n, 12)
    return date(y, m + 1, 1)


def month_end(d):
    return add_months(month_start(d), 1) - timedelta(days=1)


def window(end, days):
    """(start, end) inclusive, `days` long, ending on `end`."""
    return end - timedelta(days=days - 1), end


def prior_window(w):
    s, e = w
    n = (e - s).days + 1
    return s - timedelta(days=n), s - timedelta(days=1)


def fmt_range(w):
    s, e = w
    if s.year == e.year:
        return f"{s.strftime('%b')} {s.day} to {e.strftime('%b')} {e.day}"
    return f"{s.strftime('%b')} {s.day}, {s.year} to {e.strftime('%b')} {e.day}, {e.year}"


def fmt_money(x, short=False):
    if x is None:
        return ""
    a = abs(x)
    sign = "-" if x < 0 else ""
    if short and a >= 1e6:
        return f"{sign}${a / 1e6:.1f}M"
    if short and a >= 1e4:
        return f"{sign}${a / 1e3:.0f}K"
    if short and a >= 1e3:
        return f"{sign}${a / 1e3:.1f}K"
    return f"{sign}${a:,.0f}"
