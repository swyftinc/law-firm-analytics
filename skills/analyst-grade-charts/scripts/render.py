#!/usr/bin/env python3
"""Render a chart spec (JSON) into one self-contained HTML page with inline SVG.

Usage:
    python3 render.py spec.json --out page.html [--strict]

The page is restrained on purpose: white ground, near-black ink, grays, and ONE accent color that
marks the thing to look at first. Red, amber and green appear only to show status, always with an
arrow and a word. No legends when direct labels work. Bars start at zero. The renderer also lints the
spec against those rules and writes any warnings next to the output. Standard library only.

Spec shape:
    {"title": "...", "subtitle": "...", "kind": "charts" | "memo",
     "accent": "#2620f6",                      # optional, must have 4.5:1 contrast on white
     "meta": {"source": "...", "as_of": "2026-10-04"},
     "blocks": [ {"type": "chart", "kind": "bar_h", ...}, {"type": "p", "text": "..."}, ... ]}

Block types: h2, p, lede, callout, note, kpi_row, table, chart (kinds: bar_h, column, line, dumbbell,
small_multiples, stacked_bar), footnote. See references/chart-doctrine.md for when to use each.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from datetime import date, datetime

INK = "#14161a"
INK2 = "#4f555f"
MUTED = "#7a808b"
HAIR = "#e5e7eb"
QUIET = "#c4c9d2"       # the quiet bars
QUIET_DARK = "#9aa1ad"  # quiet lines and secondary marks
GOOD, WATCH, BAD = "#17703f", "#a35a00", "#c0262d"
GOOD_BG, WATCH_BG, BAD_BG = "#e8f4ed", "#fbf0e1", "#fbe9ea"
DEFAULT_ACCENT = "#2620f6"
STATUS = {"green": (GOOD, GOOD_BG, "better"), "amber": (WATCH, WATCH_BG, "watch"), "red": (BAD, BAD_BG, "worse"),
          "gray": (MUTED, "#f1f2f4", "")}
FONT = 'ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
W = 680  # svg width


def esc(s):
    return html.escape(str(s), quote=True)


def rich(text):
    """Escape, then allow **bold**."""
    t = esc(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


def clean(text):
    """No em dashes in anything we render."""
    return str(text).replace("\N{EM DASH}", ", ").replace(" – ", ", ")


def luminance(hex_):
    h = hex_.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b="#ffffff"):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


# ----------------------------------------------------------------------------- number formats


def fmt_val(v, unit, short=False):
    if v is None:
        return ""
    if unit == "usd":
        a = abs(v)
        s = "-" if v < 0 else ""
        if a >= 1e6:
            return f"{s}${a / 1e6:.1f}M"
        if a >= 1e4 or (short and a >= 1e3):
            return f"{s}${a / 1e3:.0f}K" if a < 1e5 or short else f"{s}${a / 1e3:,.0f}K"
        return f"{s}${a:,.0f}"
    if unit == "pct":
        return f"{v * 100:.0f}%" if short or abs(v) >= .995 else f"{v * 100:.1f}%"
    if unit == "pts":
        return f"{v * 100:+.1f} pts"
    if unit == "minutes":
        if v < 90:
            return f"{v:.0f} min"
        if v < 2880:
            return f"{v / 60:.1f} h" if short else f"{v / 60:.1f} hours"
        return f"{v / 1440:.1f} days"
    if unit == "days":
        return f"{v:,.0f}" if short else f"{v:,.0f} days"
    if unit == "hours":
        return f"{v:.1f} h"
    return f"{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else f"{v:,.1f}"


def nice_ticks(lo, hi, n=5):
    if hi == lo:
        hi = lo + 1
    span = hi - lo
    raw = span / max(1, n - 1)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if step >= raw:
            break
    start = math.floor(lo / step) * step
    ticks = []
    t = start
    while t <= hi + step * .5:
        ticks.append(round(t, 10))
        t += step
    return ticks


def parse_x(x):
    if isinstance(x, (date, datetime)):
        return x if isinstance(x, date) and not isinstance(x, datetime) else x.date()
    s = str(x)
    for f in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d"):
        try:
            return datetime.strptime(s[:10] if f == "%Y-%m-%d" else s[:7] if f == "%Y-%m" else s, f).date()
        except ValueError:
            continue
    return None


def x_label(d, gran):
    if gran == "year":
        return str(d.year)
    if gran == "month":
        return d.strftime("%b") if d.month != 1 else d.strftime("%b %Y")
    return f"{d.strftime('%b')} {d.day}"


def tw(text, size):
    """Rough text width in px for the system sans stack."""
    return len(str(text)) * size * .56


# ----------------------------------------------------------------------------- svg helpers


def svg_open(w, h, title, desc=""):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{esc(title)}" '
            f'preserveAspectRatio="xMinYMin meet" xmlns="http://www.w3.org/2000/svg">'
            f'<title>{esc(title)}</title><desc>{esc(desc or title)}</desc>')


def text(x, y, s, size=12, fill=INK2, anchor="start", weight=400, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {extra}>{esc(s)}</text>')


def spread(ys, min_gap=14, lo=0, hi=1e9):
    """Push label y positions apart so direct labels do not collide."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    out = list(ys)
    for k in range(1, len(order)):
        a, b = order[k - 1], order[k]
        if out[b] - out[a] < min_gap:
            out[b] = out[a] + min_gap
    over = out[order[-1]] - hi if order else 0
    if over > 0:
        for i in order:
            out[i] -= over
    return [max(lo, y) for y in out]


# ----------------------------------------------------------------------------- charts


def chart_bar_h(c, accent):
    items = [dict(i) for i in c["data"]]
    unit = c.get("unit", "count")
    if c.get("order", "value") == "value":
        items.sort(key=lambda i: (bool(i.get("thin")), i.get("value") is None, -(i.get("value") or 0)))
    left = min(230, max(90, max(tw(i["label"], 13) for i in items) + 14))
    right = 150
    bar_h, gap, top = (17, 8, 4) if c.get("compact") else (22, 12, 6)
    vals = [i["value"] for i in items if i.get("value") is not None and not i.get("thin")]
    vmax = max(vals + [(c.get("ref") or {}).get("value", 0)]) or 1
    plot = W - left - right
    x0 = left
    H = top + len(items) * (bar_h + gap) + 4 + (18 if c.get("ref") else 0)
    out = [svg_open(W, H, c["title"], c.get("desc", ""))]
    body_end = top + len(items) * (bar_h + gap)
    if c.get("ref"):   # drawn first so it sits behind the bars and labels
        rx = x0 + plot * c["ref"]["value"] / vmax
        out.append(f'<line x1="{rx:.1f}" y1="{top - 2}" x2="{rx:.1f}" y2="{body_end}" stroke="{INK2}" stroke-width="1" stroke-dasharray="3 3"/>')
        out.append(text(rx, body_end + 14, f"{c['ref'].get('label', 'Average')} {fmt_val(c['ref']['value'], unit)}", 11, INK2, "middle"))
    out.append(f'<line x1="{x0}" y1="{top - 2}" x2="{x0}" y2="{body_end}" stroke="{QUIET_DARK}" stroke-width="1"/>')
    for k, it in enumerate(items):
        y = top + k * (bar_h + gap)
        v = it.get("value")
        thin = it.get("thin")
        out.append(text(x0 - 10, y + bar_h / 2 + 4.5, it["label"], 13, MUTED if thin else INK, "end", 500 if it.get("highlight") else 400))
        if v is None:
            continue
        lab = it.get("display") or fmt_val(v, unit)
        sub = it.get("sample")
        if thin:
            # a value on too few cases gets no bar: a bar would look like evidence
            msg = f"{lab}  ({sub + ', ' if sub else ''}too thin to call)"
            out.append(f'<line x1="{x0 + 2}" y1="{y + bar_h / 2}" x2="{x0 + 14}" y2="{y + bar_h / 2}" stroke="{QUIET}" stroke-width="2" stroke-dasharray="2 3"/>')
            out.append(text(x0 + 22, y + bar_h / 2 + 4.5, msg, 12, MUTED))
            continue
        w = max(1.5, plot * max(v, 0) / vmax)
        col = accent if it.get("highlight") else QUIET
        out.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="2" fill="{col}" data-value="{v}"/>')
        out.append(text(x0 + w + 8, y + bar_h / 2 + 4.5, lab, 13, INK, "start", 600 if it.get("highlight") else 500))
        if sub:
            out.append(text(x0 + w + 8 + tw(lab, 13) + 8, y + bar_h / 2 + 4.5, sub, 11, MUTED))
    out.append("</svg>")
    return "".join(out), H


def chart_column(c, accent):
    items = c["data"]
    unit = c.get("unit", "count")
    n = len(items)
    left, right, top, bottom = 8, 8, 24, 30
    H = 230
    plot_w, plot_h = W - left - right, H - top - bottom
    vmax = max([i["value"] for i in items if i.get("value") is not None] + [1e-9])
    slot = plot_w / n
    bw = min(46, slot * .66) if not c.get("gapless") else slot
    out = [svg_open(W, H, c["title"], c.get("desc", ""))]
    base_y = top + plot_h
    out.append(f'<line x1="{left}" y1="{base_y}" x2="{W - right}" y2="{base_y}" stroke="{QUIET_DARK}" stroke-width="1"/>')
    for k, it in enumerate(items):
        v = it.get("value")
        if v is None:
            continue
        h = max(1.5, plot_h * v / vmax)
        x = left + k * slot + (slot - bw) / 2
        col = accent if it.get("highlight") else QUIET
        out.append(f'<rect x="{x:.1f}" y="{base_y - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="{col}" data-value="{v}"/>')
        if n <= 14:
            out.append(text(x + bw / 2, base_y - h - 6, it.get("display") or fmt_val(v, unit, True), 11.5, INK, "middle",
                            600 if it.get("highlight") else 400))
        if n <= 14 or k % math.ceil(n / 12) == 0:
            out.append(text(x + bw / 2, base_y + 17, it["label"], 11.5, MUTED, "middle"))
    out.append("</svg>")
    return "".join(out), H


def _series_xy(series, gran):
    pts = []
    for s in series:
        for p in s["points"]:
            d = parse_x(p["x"])
            pts.append(d)
    return pts


def chart_line(c, accent):
    series = c["series"]
    unit = c.get("unit", "count")
    gran = c.get("granularity", "week")
    left, right, top, bottom = 46, 150, 20, 28
    H = c.get("height", 190 if c.get("compact") else 270)
    plot_w, plot_h = W - left - right, H - top - bottom
    xs = [d for d in _series_xy(series, gran) if d]
    numeric_x = not xs
    if numeric_x:
        allx = [p["x"] for s in series for p in s["points"]]
        xmin, xmax = min(allx), max(allx)
    else:
        xmin, xmax = min(xs), max(xs)
    span = (xmax - xmin) if numeric_x else max(1, (xmax - xmin).days)
    ys = [p["y"] for s in series for p in s["points"] if p.get("y") is not None]
    ymin, ymax = min(ys), max(ys)
    zero = c.get("y_zero", True)
    lo = 0 if zero else ymin - (ymax - ymin) * .08
    if zero and ymin < 0:
        lo = ymin
    ticks = nice_ticks(lo, ymax, 5)
    lo, hi = min(lo, ticks[0]), max(ymax, ticks[-1])

    def X(p):
        x = p["x"] if numeric_x else parse_x(p["x"])
        f = ((x - xmin) if numeric_x else (x - xmin).days) / float(span)
        return left + plot_w * f

    def Y(v):
        return top + plot_h * (1 - (v - lo) / float(hi - lo))
    out = [svg_open(W, H, c["title"], c.get("desc", ""))]
    for t in ticks:
        y = Y(t)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="{HAIR}" stroke-width="1"/>')
        out.append(text(left - 8, y + 4, fmt_val(t, unit, True), 11, MUTED, "end"))
    # x labels
    if not numeric_x:
        nt = 6
        for i in range(nt):
            d = xmin.fromordinal(xmin.toordinal() + int(span * i / (nt - 1)))
            out.append(text(left + plot_w * i / (nt - 1), H - 8, x_label(d, gran), 11, MUTED,
                            "start" if i == 0 else "end" if i == nt - 1 else "middle"))
    for mk in c.get("markers", []):
        d = parse_x(mk["x"])
        if d and xmin <= d <= xmax:
            mx = left + plot_w * ((d - xmin).days / float(span))
            out.append(f'<line x1="{mx:.1f}" y1="{top}" x2="{mx:.1f}" y2="{top + plot_h}" stroke="{INK2}" stroke-width="1" stroke-dasharray="3 3"/>')
            out.append(text(mx + 4, top + 10, mk.get("label", ""), 11, INK2))
    labels = []
    order = sorted(series, key=lambda s: bool(s.get("highlight")))   # highlight drawn last
    for s in order:
        pts = [(X(p), Y(p["y"])) for p in s["points"] if p.get("y") is not None]
        if not pts:
            continue
        hl = s.get("highlight")
        col = accent if hl else QUIET_DARK
        out.append(f'<polyline fill="none" stroke="{col}" stroke-width="{2.6 if hl else 1.5}" stroke-linejoin="round" '
                   f'stroke-linecap="round" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
                   f'data-series="{esc(s["name"])}" data-accent="{1 if hl else 0}"/>')
        lx, ly = pts[-1]
        out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{3.4 if hl else 2.4}" fill="{col}"/>')
        last = [p for p in s["points"] if p.get("y") is not None][-1]
        labels.append((ly, s["name"], fmt_val(last["y"], unit), hl))
    ys_l = spread([l[0] + 4 for l in labels], 15, top + 8, top + plot_h + 4)
    for (ly, name, val, hl), yy in zip(labels, ys_l):
        out.append(text(W - right + 10, yy, f"{name}  {val}", 12, INK if hl else INK2, "start", 600 if hl else 400))
    out.append("</svg>")
    return "".join(out), H


def chart_dumbbell(c, accent):
    items = [dict(i) for i in c["data"]]
    unit = c.get("unit", "pct")
    if c.get("order", "value") == "value":
        items.sort(key=lambda i: -(i["after"]))
    left = min(220, max(90, max(tw(i["label"], 13) for i in items) + 14))
    right = 30
    row, top = (27 if c.get("compact") else 34), 26
    H = top + len(items) * row + 8
    vals = [i["before"] for i in items] + [i["after"] for i in items]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * .15 or abs(hi) * .1 or 1
    lo, hi = lo - pad, hi + pad
    plot = W - left - right - 70

    def X(v):
        return left + 40 + plot * (v - lo) / float(hi - lo)
    out = [svg_open(W, H, c["title"], c.get("desc", ""))]
    out.append(text(left + 40, 12, c.get("before_label", "Before"), 11, MUTED))
    out.append(f'<circle cx="{left + 40 + tw(c.get("before_label", "Before"), 11) + 14}" cy="8" r="4" fill="{QUIET_DARK}"/>')
    out.append(text(left + 40 + tw(c.get("before_label", "Before"), 11) + 26, 12, c.get("after_label", "Now"), 11, INK))
    out.append(f'<circle cx="{left + 40 + tw(c.get("before_label", "Before"), 11) + 26 + tw(c.get("after_label", "Now"), 11) + 12}" cy="8" r="4" fill="{accent}"/>')
    for k, it in enumerate(items):
        y = top + k * row + row / 2
        a, b = X(it["before"]), X(it["after"])
        hl = it.get("highlight")
        out.append(text(left, y + 4.5, it["label"], 13, INK, "end", 600 if hl else 400))
        out.append(f'<line x1="{left + 40}" y1="{y}" x2="{left + 40 + plot}" y2="{y}" stroke="{HAIR}" stroke-width="1"/>')
        out.append(f'<line x1="{a:.1f}" y1="{y}" x2="{b:.1f}" y2="{y}" stroke="{accent if hl else QUIET_DARK}" stroke-width="{3 if hl else 2}"/>')
        out.append(f'<circle cx="{a:.1f}" cy="{y}" r="5" fill="{QUIET_DARK}" data-value="{it["before"]}"/>')
        out.append(f'<circle cx="{b:.1f}" cy="{y}" r="6" fill="{accent if hl else INK2}" data-value="{it["after"]}"/>')
        lo_x, hi_x = (a, b) if a <= b else (b, a)
        left_is_before = a <= b
        out.append(text(lo_x - 9, y + 4, fmt_val(it["before"] if left_is_before else it["after"], unit), 12, MUTED if left_is_before else INK, "end"))
        out.append(text(hi_x + 9, y + 4, fmt_val(it["after"] if left_is_before else it["before"], unit), 12,
                        INK if left_is_before else MUTED, "start", 600 if hl and left_is_before else 400))
    out.append("</svg>")
    return "".join(out), H


def chart_small_multiples(c, accent):
    panels = c["panels"]
    unit = c.get("unit", "count")
    cols = c.get("cols", 3)
    pw, ph = (W - (cols - 1) * 16) / cols, 118
    rows = math.ceil(len(panels) / cols)
    H = rows * (ph + 34)
    allv = [p["y"] for pn in panels for p in pn["points"] if p.get("y") is not None]
    lo, hi = (0 if c.get("y_zero", True) else min(allv)), max(allv)
    out = [svg_open(W, H, c["title"], c.get("desc", ""))]
    for i, pn in enumerate(panels):
        gx, gy = (i % cols) * (pw + 16), (i // cols) * (ph + 34)
        hl = pn.get("highlight")
        out.append(text(gx, gy + 12, pn["name"], 12.5, INK, "start", 600 if hl else 500))
        pts = [p for p in pn["points"] if p.get("y") is not None]
        if not pts:
            continue
        n = len(pts)
        xy = [(gx + 4 + (pw - 8) * k / max(1, n - 1), gy + 22 + ph * (1 - (p["y"] - lo) / float(hi - lo or 1))) for k, p in enumerate(pts)]
        out.append(f'<line x1="{gx}" y1="{gy + 22 + ph}" x2="{gx + pw}" y2="{gy + 22 + ph}" stroke="{HAIR}"/>')
        out.append(f'<polyline fill="none" stroke="{accent if hl else QUIET_DARK}" stroke-width="{2.4 if hl else 1.6}" '
                   f'stroke-linejoin="round" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in xy)}" data-accent="{1 if hl else 0}"/>')
        out.append(f'<circle cx="{xy[-1][0]:.1f}" cy="{xy[-1][1]:.1f}" r="3" fill="{accent if hl else QUIET_DARK}"/>')
        out.append(text(gx + pw, gy + 12, fmt_val(pts[-1]["y"], unit), 12.5, INK if hl else INK2, "end", 600 if hl else 400))
    out.append("</svg>")
    return "".join(out), H


def chart_stacked_bar(c, accent):
    rows = c["rows"]
    unit = c.get("unit", "usd")
    left, right = 74, 12
    barh, gap, top = (20, 40, 24) if c.get("compact") else (26, 44, 24)
    H = top + len(rows) * (barh + gap)
    plot = W - left - right
    vmax = max(sum(p["value"] for p in r["parts"]) for r in rows) or 1
    out = [svg_open(W, H, c["title"], c.get("desc", ""))]
    shades = ["#e4e7ec", "#d3d7de", "#c0c5ce", "#adb3be", "#9aa1ad"]
    for k, r in enumerate(rows):
        y = top + k * (barh + gap)
        out.append(text(left - 10, y + barh / 2 + 4.5, r["label"], 13, INK, "end", 500))
        x = left
        used_to = -1e9
        for j, p in enumerate(r["parts"]):
            w = plot * p["value"] / vmax
            hl = p.get("highlight")
            col = accent if hl else shades[min(j, len(shades) - 1)]
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w, 0):.1f}" height="{barh}" fill="{col}" data-value="{p["value"]}" data-accent="{1 if hl else 0}"/>')
            if k == 0:
                label_w = tw(p["name"], 11)
                if hl:
                    out.append(text(x + w, y - 7, p["name"], 11, INK, "end", 600))
                elif x >= used_to + 6 and x + label_w < left + plot - (tw("91+ days", 11) + 12):
                    out.append(text(x + 2, y - 7, p["name"], 11, MUTED))
                    used_to = x + label_w
            if w > 38 or hl:
                out.append(text(x + 2 if not hl else x + w, y + barh + 15, fmt_val(p["value"], unit, True), 11.5,
                                INK if hl else INK2, "end" if hl else "start", 600 if hl else 400))
            x += w
        total = sum(p["value"] for p in r["parts"])
        out.append(text(left, y + barh + 32, f"Total {fmt_val(total, unit, True)}", 11, MUTED))
    out.append("</svg>")
    return "".join(out), H


CHARTS = {"bar_h": chart_bar_h, "column": chart_column, "line": chart_line, "dumbbell": chart_dumbbell,
          "small_multiples": chart_small_multiples, "stacked_bar": chart_stacked_bar}


def render_chart(c, accent):
    svg, _ = CHARTS[c["kind"]](c, accent)
    attrs = {"data-chart": c["kind"], "data-baseline": "zero" if c["kind"] in ("bar_h", "column", "stacked_bar") or c.get("y_zero", True) and c["kind"] in ("line", "small_multiples") else "nonzero",
             "data-direct-labels": "true", "data-legend": "false",
             "data-lower-better": "true" if c.get("lower_is_better") else "false"}
    note = ""
    if c.get("lower_is_better"):
        note = '<span class="dir">Lower is better</span>'
    elif c.get("higher_is_better"):
        note = '<span class="dir">Higher is better</span>'
    sub = c.get("subtitle", "")
    head = f'<h3>{esc(clean(c["title"]))}</h3>'
    subl = f'<p class="sub">{esc(clean(sub))}{(" " + note) if note else ""}</p>' if sub or note else ""
    foot = f'<p class="foot">{esc(clean(c["footnote"]))}</p>' if c.get("footnote") else ""
    a = " ".join(f'{k}="{esc(v)}"' for k, v in attrs.items())
    return f'<figure class="chart" {a}>{head}{subl}{svg}{foot}</figure>'


# ----------------------------------------------------------------------------- html blocks


def spark(points, color, w=96, h=26):
    if not points or len(points) < 2:
        return ""
    lo, hi = min(points), max(points)
    rng = (hi - lo) or 1
    xy = [(2 + (w - 4) * i / (len(points) - 1), 3 + (h - 6) * (1 - (p - lo) / rng)) for i, p in enumerate(points)]
    pl = " ".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true">'
            f'<polyline fill="none" stroke="{QUIET_DARK}" stroke-width="1.5" stroke-linejoin="round" points="{pl}"/>'
            f'<circle cx="{xy[-1][0]:.1f}" cy="{xy[-1][1]:.1f}" r="2.6" fill="{color}"/></svg>')


def render_kpi_row(b, accent):
    tiles = []
    for t in b["items"]:
        status = t.get("status", "gray")
        col, bg, word = STATUS.get(status, STATUS["gray"])
        word = t.get("word", word)
        arrow = ""
        if t.get("delta_dir") in ("up", "down"):
            arrow = "▲" if t["delta_dir"] == "up" else "▼"
        delta = ""
        if t.get("delta"):
            w = f" {word}" if word else ""
            delta = (f'<div class="delta" style="color:{col}"><span class="chip" style="background:{bg}">{arrow} {esc(t["delta"])}'
                     f'{esc(w)}</span><span class="vs">{esc(t.get("vs", ""))}</span></div>')
        dirn = ""
        if t.get("direction") == "lower_better":
            dirn = '<div class="dir">Lower is better</div>'
        elif t.get("direction") == "higher_better":
            dirn = '<div class="dir">Higher is better</div>'
        samp = f'<div class="samp">{esc(t["sample"])}</div>' if t.get("sample") else ""
        tiles.append(f'<div class="kpi" data-metric="{esc(t.get("metric", ""))}" data-direction="{esc(t.get("direction", ""))}" '
                     f'data-status="{esc(status)}" data-delta="{esc(t.get("delta_dir", ""))}">'
                     f'<div class="klabel">{esc(clean(t["label"]))}</div><div class="kvalue">{esc(t["value"])}</div>{delta}'
                     f'{spark(t.get("spark"), accent if t.get("highlight") else QUIET_DARK)}{dirn}{samp}</div>')
    return f'<div class="kpis" data-chart="kpi_row">{"".join(tiles)}</div>'


def render_table(b):
    cols = b["columns"]
    head = "".join(f'<th class="{c.get("align", "left")}">{esc(c["label"])}</th>' for c in cols)
    body = []
    for r in b["rows"]:
        tds = []
        for c in cols:
            v = r.get(c["key"], "")
            if c.get("status") and r.get(c["key"] + "_status"):
                col, bg, word = STATUS.get(r[c["key"] + "_status"], STATUS["gray"])
                tds.append(f'<td class="{c.get("align", "left")}"><span class="chip" style="color:{col};background:{bg}">{esc(v)}</span></td>')
            else:
                tds.append(f'<td class="{c.get("align", "left")}">{esc(v)}</td>')
        body.append(f'<tr class="{"hl" if r.get("highlight") else ""}">{"".join(tds)}</tr>')
    title = f'<h3>{esc(clean(b["title"]))}</h3>' if b.get("title") else ""
    foot = f'<p class="foot">{esc(clean(b["footnote"]))}</p>' if b.get("footnote") else ""
    return f'<figure class="chart" data-chart="table">{title}<table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>{foot}</figure>'


CSS = f"""
:root {{ --ink:{INK}; --ink2:{INK2}; --muted:{MUTED}; --hair:{HAIR}; --accent:{{ACCENT}}; color-scheme: light; }}
* {{ box-sizing: border-box; }}
html {{ background:#fff; }}
body {{ margin:0; background:#fff; color:var(--ink); font:16px/1.55 {FONT}; -webkit-font-smoothing:antialiased; }}
main {{ max-width:720px; margin:0 auto; padding:40px 24px 64px; }}
header.top {{ margin-bottom:28px; }}
.eyebrow {{ font-size:12.5px; color:var(--muted); margin:0 0 6px; letter-spacing:.01em; }}
h1 {{ font-size:28px; line-height:1.2; margin:0 0 8px; font-weight:650; letter-spacing:-.012em; }}
.subtitle {{ margin:0; color:var(--ink2); font-size:15.5px; }}
h2 {{ font-size:17px; margin:34px 0 8px; font-weight:650; letter-spacing:-.005em; }}
h3 {{ font-size:16.5px; margin:0 0 4px; font-weight:650; line-height:1.3; letter-spacing:-.005em; }}
p {{ margin:0 0 14px; }}
.lede {{ font-size:19px; line-height:1.5; font-weight:500; margin:0 0 20px; }}
strong {{ font-weight:650; }}
figure.chart {{ margin:26px 0; padding:0; break-inside:avoid; }}
figure.chart .sub {{ margin:0 0 10px; color:var(--ink2); font-size:13.5px; }}
figure.chart .foot {{ margin:8px 0 0; color:var(--muted); font-size:12px; line-height:1.45; }}
.dir {{ display:inline-block; font-size:11.5px; color:var(--muted); margin-left:6px; }}
svg {{ display:block; max-width:100%; height:auto; overflow:visible; font-family:inherit; }}
svg text {{ font-family:inherit; font-variant-numeric:tabular-nums; paint-order:stroke; stroke:#fff; stroke-width:3px; stroke-linejoin:round; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:0; margin:24px 0; border-top:1px solid var(--hair); border-bottom:1px solid var(--hair); }}
.kpi {{ padding:16px 16px 14px 0; border-right:1px solid var(--hair); padding-left:16px; break-inside:avoid; }}
.kpi:first-child {{ padding-left:0; }} .kpi:last-child {{ border-right:0; }}
.klabel {{ font-size:12.5px; color:var(--ink2); margin-bottom:6px; }}
.kvalue {{ font-size:30px; line-height:1.1; font-weight:650; letter-spacing:-.02em; font-variant-numeric:tabular-nums; }}
.delta {{ margin-top:8px; font-size:12.5px; font-weight:600; }}
.chip {{ display:inline-block; padding:1px 7px; border-radius:99px; font-size:12px; }}
.vs {{ display:block; color:var(--muted); font-weight:400; margin-top:3px; }}
.spark {{ margin-top:8px; }}
.samp {{ color:var(--muted); font-size:11.5px; margin-top:6px; }}
.kpi .dir {{ display:block; margin:6px 0 0; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; margin-top:6px; font-variant-numeric:tabular-nums; }}
th {{ text-align:left; font-weight:600; color:var(--ink2); font-size:12.5px; padding:6px 10px 6px 0; border-bottom:1px solid var(--ink2); }}
td {{ padding:9px 10px 9px 0; border-bottom:1px solid var(--hair); }}
th.right, td.right {{ text-align:right; padding-right:0; padding-left:10px; }}
tr.hl td {{ font-weight:600; }}
.callout {{ border-left:3px solid var(--accent); padding:2px 0 2px 16px; margin:24px 0; }}
.callout .label {{ font-size:12.5px; color:var(--ink2); margin:0 0 4px; font-weight:600; }}
.callout p {{ margin:0; font-weight:500; }}
.note {{ background:#f6f7f9; border-radius:8px; padding:12px 16px; margin:20px 0; font-size:14px; color:var(--ink2); }}
.note .label {{ font-weight:600; color:var(--ink); margin-bottom:3px; }}
footer.page {{ margin-top:40px; padding-top:14px; border-top:1px solid var(--hair); color:var(--muted); font-size:12px; line-height:1.5; }}
.memo main {{ max-width:680px; }}
@media print {{
  @page {{ size: letter; margin: .5in .6in; }}
  body {{ font-size:9.8pt; line-height:1.38; }}
  main {{ padding:0; max-width:none; }}
  header.top {{ margin-bottom:12px; }}
  h1 {{ font-size:19pt; margin-bottom:4px; }} .eyebrow {{ font-size:8.5pt; margin-bottom:3px; }}
  .lede {{ font-size:11.5pt; margin-bottom:8px; line-height:1.42; }}
  h2 {{ font-size:11pt; margin:12px 0 3px; }} h3 {{ font-size:10pt; margin-bottom:2px; }}
  p {{ margin-bottom:7px; }}
  figure.chart {{ margin:8px 0; }} figure.chart .sub {{ font-size:8.5pt; margin-bottom:4px; }}
  figure.chart svg {{ max-height:2.1in; width:auto; }}
  figure.chart .foot {{ font-size:7.5pt; margin-top:3px; }}
  .callout {{ margin:10px 0; }} .note {{ margin:10px 0; padding:8px 12px; font-size:9pt; }}
  footer.page {{ margin-top:12px; padding-top:8px; font-size:7.5pt; }}
  .kvalue {{ font-size:18pt; }}
}}
@media (max-width: 560px) {{ main {{ padding:28px 16px 48px; }} h1 {{ font-size:24px; }} .kpi {{ border-right:0; padding-left:0; border-bottom:1px solid var(--hair); }} }}
"""


def render_page(spec):
    accent = spec.get("accent", DEFAULT_ACCENT)
    parts = []
    blocks = spec.get("blocks", [])
    for b in blocks:
        t = b["type"]
        if t == "h2":
            parts.append(f'<h2>{esc(clean(b["text"]))}</h2>')
        elif t == "p":
            parts.append(f'<p>{rich(clean(b["text"]))}</p>')
        elif t == "lede":
            parts.append(f'<p class="lede">{rich(clean(b["text"]))}</p>')
        elif t == "callout":
            parts.append(f'<div class="callout"><p class="label">{esc(clean(b.get("label", "Look at this first")))}</p>'
                         f'<p>{rich(clean(b["text"]))}</p></div>')
        elif t == "note":
            parts.append(f'<div class="note"><div class="label">{esc(clean(b.get("label", "Too thin to call")))}</div>{rich(clean(b["text"]))}</div>')
        elif t == "kpi_row":
            parts.append(render_kpi_row(b, accent))
        elif t == "table":
            parts.append(render_table(b))
        elif t == "chart":
            parts.append(render_chart(b, accent))
        elif t == "footnote":
            parts.append(f'<footer class="page">{rich(clean(b["text"]))}</footer>')
    meta = spec.get("meta", {})
    eyebrow = f'<p class="eyebrow">{esc(clean(meta.get("eyebrow", "")))}</p>' if meta.get("eyebrow") else ""
    sub = f'<p class="subtitle">{esc(clean(spec["subtitle"]))}</p>' if spec.get("subtitle") else ""
    foot = ""
    if meta.get("source") and not any(b["type"] == "footnote" for b in blocks):
        foot = f'<footer class="page">{esc(clean(meta["source"]))}</footer>'
    body_class = "memo" if spec.get("kind") == "memo" else "charts"
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(clean(spec["title"]))}</title><style>{CSS.replace("{ACCENT}", accent)}</style></head>'
            f'<body class="{body_class}"><main><header class="top">{eyebrow}<h1>{esc(clean(spec["title"]))}</h1>{sub}</header>'
            f'{"".join(parts)}{foot}</main></body></html>')


# ----------------------------------------------------------------------------- lint

TITLE_CASE = re.compile(r"^(?:[A-Z][a-z]+(?:\s+|$)){3,}")


def lint(spec):
    w = []
    accent = spec.get("accent", DEFAULT_ACCENT)
    if contrast(accent) < 4.5:
        w.append(f"accent {accent} has contrast {contrast(accent):.1f}:1 on white; use something darker (4.5:1 needed).")
    blob = json.dumps(spec, ensure_ascii=False)
    if "\N{EM DASH}" in blob:
        w.append("an em dash was in the spec text; it was replaced when rendering.")
    for b in spec.get("blocks", []):
        t = b.get("type")
        if t == "chart":
            k = b["kind"]
            title = b.get("title", "")
            if not title:
                w.append(f"{k}: chart has no title; the title should state the takeaway.")
            if TITLE_CASE.match(title or ""):
                w.append(f"{k}: title looks like Title Case ('{title}'); use sentence case.")
            if k in ("bar_h", "column"):
                hl = sum(1 for i in b["data"] if i.get("highlight"))
                if hl > 1 and b.get("allow_multi_highlight") is not True:
                    w.append(f"{k}: {hl} highlighted bars; one accent should mark the single thing to look at first.")
                if any((i.get("value") or 0) < 0 for i in b["data"]):
                    w.append(f"{k}: negative values on a bar chart; consider a dumbbell or table.")
                if len(b["data"]) > 12:
                    w.append(f"{k}: {len(b['data'])} bars; fold the tail into 'Other' or use a table.")
            if k == "line":
                hl = sum(1 for s in b["series"] if s.get("highlight"))
                if hl != 1:
                    w.append(f"line: {hl} highlighted series; exactly one should carry the accent.")
                if len(b["series"]) > 5:
                    w.append(f"line: {len(b['series'])} series; more than 4 or 5 turns into spaghetti. Use small multiples.")
                if b.get("y_zero") is False and not b.get("subtitle"):
                    w.append("line: y-axis does not start at zero; say so in the subtitle.")
            if k == "stacked_bar":
                for r in b["rows"]:
                    if len(r["parts"]) > 5:
                        w.append("stacked_bar: more than 5 parts; use a sorted bar chart.")
            if b.get("kind") == "bar_h" and b.get("metric") and b.get("lower_is_better") is None:
                pass
        if t == "kpi_row":
            for it in b["items"]:
                d, st, dd = it.get("direction"), it.get("status", "gray"), it.get("delta_dir")
                if d and dd and st in ("green", "red"):
                    good_move = (dd == "up") == (d == "higher_better")
                    if good_move and st == "red" or (not good_move) and st == "green":
                        w.append(f"kpi '{it['label']}': status {st} contradicts direction ({d}) and move ({dd}). Status is inverted.")
                if it.get("n") is not None and it["n"] < 10 and st in ("green", "red"):
                    w.append(f"kpi '{it['label']}': n={it['n']} is too thin for a red or green status.")
    if spec.get("kind") == "memo":
        words = 0
        charts = 0
        for b in spec.get("blocks", []):
            if b.get("type") in ("lede", "p", "callout", "note", "h2"):
                words += len(re.findall(r"\b\w[\w'$%.,-]*\b", b.get("text", "")))
            if b.get("type") == "chart":
                charts += 1
        if words > 520:
            w.append(f"memo: about {words} words. It should be 300 to 450 to fit one page. Cut findings, not detail inside them.")
        if charts > 2:
            w.append(f"memo: {charts} charts; at most two small ones.")
        kinds = [b.get("type") for b in spec.get("blocks", [])]
        if "lede" not in kinds:
            w.append("memo: no lede. Open with the single most important change.")
        if "callout" not in kinds:
            w.append("memo: no 'look at this first' callout.")
    return w


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--strict", action="store_true", help="exit 1 if the lint finds anything")
    a = ap.parse_args(argv)
    spec = json.load(open(a.spec))
    warnings = lint(spec)
    html_ = render_page(spec)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(html_)
    for x in warnings:
        print("lint:", x, file=sys.stderr)
    print(f"Wrote {a.out} ({len(html_) // 1024} KB). Lint warnings: {len(warnings)}.")
    if warnings and a.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
