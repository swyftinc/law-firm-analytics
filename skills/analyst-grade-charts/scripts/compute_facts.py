#!/usr/bin/env python3
"""Turn mapped exports into facts.json: every number a chart or a briefing may use.

Usage:
    python3 compute_facts.py --mapping mapping.json --out facts.json [--as-of YYYY-MM-DD] [--summary]

The model never does arithmetic. This script reads the files, computes each metric over the
window it should be read over, compares it with the period before, tests whether the change
is bigger than normal variation, and writes the result with its sample size and direction.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (_blank, add_months, count_ratio_z, fmt_money, fmt_range, load_tables, log_ratio_z,  # noqa: E402
                    mannwhitney_z, median, month_end, month_start, p_two_sided, parse_column_dates, parse_num,
                    percentile, prior_window, ratio_z, two_prop_z, window)
from schema import ENTITIES  # noqa: E402

VERSION = "1.0"

# metric: label, unit, direction. Direction is set once, here, and never inverted.
METRICS = {
    "lead_volume": ("New leads", "count", "higher_better"),
    "lead_source_share": ("Share of new leads", "pct", "neutral"),
    "signed_rate": ("Signed rate", "pct", "higher_better"),
    "signed_rate_12m": ("Signed rate, last 12 months", "pct", "higher_better"),
    "cost_per_lead": ("Cost per lead", "usd", "lower_better"),
    "cost_per_signed": ("Cost per signed matter", "usd", "lower_better"),
    "cost_per_signed_12m": ("Cost per signed matter, last 12 months", "usd", "lower_better"),
    "cost_per_lead_12m": ("Cost per lead, last 12 months", "usd", "lower_better"),
    "speed_to_lead": ("Speed to lead (median)", "minutes", "lower_better"),
    "contacted_within_hour": ("Leads reached within an hour", "pct", "higher_better"),
    "uncontacted_share": ("Leads never reached", "pct", "lower_better"),
    "after_hours_share": ("Leads arriving after hours or on weekends", "pct", "neutral"),
    "signed_rate_by_response": ("Signed rate by speed of first contact", "pct", "neutral"),
    "realization": ("Realization rate", "pct", "higher_better"),
    "realization_contribution": ("Contribution to the change in realization", "pts", "neutral"),
    "collection_rate": ("Collection rate", "pct", "higher_better"),
    "utilization": ("Utilization", "pct", "higher_better"),
    "ar_total": ("Accounts receivable", "usd", "lower_better"),
    "ar_over_90": ("Receivables over 90 days", "usd", "lower_better"),
    "ar_over_90_share": ("Share of receivables over 90 days", "pct", "lower_better"),
    "ar_over_90_concentration": ("Largest matter's share of receivables over 90 days", "pct", "neutral"),
    "matter_cycle_time": ("Matter cycle time (median)", "days", "lower_better"),
    "active_matters": ("Open matters", "count", "neutral"),
    "collected_revenue": ("Collected revenue", "usd", "higher_better"),
}
PEOPLE_LEVEL_SCOPES = ("attorney",)
CENSOR_DAYS = 3          # leads received in the last 3 days may not have been contacted yet
COLLECTION_EXTRA_LAG = 75  # days after billing before most invoices are paid
MIN_N = 10               # a rate or median on fewer than this is "too thin to call"


# ----------------------------------------------------------------------------- formatting


def disp(unit, v):
    if v is None:
        return ""
    if unit == "usd":
        return fmt_money(v)
    if unit == "pct":
        return f"{v * 100:.1f}%"
    if unit == "pts":
        return f"{v * 100:+.1f} pts"
    if unit == "count":
        return f"{v:,.0f}"
    if unit == "minutes":
        if v < 90:
            return f"{v:.0f} min"
        if v < 48 * 60:
            return f"{v / 60:.1f} hours"
        return f"{v / 1440:.1f} days"
    if unit == "days":
        return f"{v:,.0f} days"
    return f"{v:g}"


def scope_label(scope):
    return " / ".join(str(v) for v in scope.values()) if scope else "Firm-wide"


def iso(d):
    return d.isoformat() if d else None


# ----------------------------------------------------------------------------- loading


class Ctx:
    def __init__(self):
        self.T = {}
        self.warnings = []
        self.files = []
        self.facts = []
        self.series = []
        self.range = {}
        self.as_of = None
        self.skipped = []
        self.counter = defaultdict(int)


def _map_value(v, vm):
    if v is None:
        return None
    s = str(v).strip()
    if s in vm:
        return vm[s]
    low = {k.lower(): val for k, val in vm.items()}
    return low.get(s.lower(), None)


def load_entity_rows(spec, base, ctx):
    path = spec["path"] if os.path.isabs(spec["path"]) else os.path.join(base, spec["path"])
    entity = spec["entity"]
    if entity not in ENTITIES:
        ctx.warnings.append(f"{spec['path']}: unknown entity '{entity}'.")
        return []
    tables = load_tables(path, spec.get("sheet"))
    if not tables:
        ctx.warnings.append(f"{spec['path']}: no readable table found.")
        return []
    t = tables[0]
    hidx = {h: i for i, h in enumerate(t.header)}
    cols = spec.get("columns", {})
    vmaps = spec.get("value_maps", {})
    fields = ENTITIES[entity]["fields"]
    file_level = spec.get("file_level", {})
    out_cols = {}
    unmapped = defaultdict(set)
    for fld, kind in fields.items():
        src = cols.get(fld)
        if not src:
            continue
        names = src if isinstance(src, list) else [src]
        missing = [n for n in names if n not in hidx]
        if missing:
            ctx.warnings.append(f"{spec['path']}: column {missing} not found for '{fld}'.")
            continue
        raw = [[r[hidx[n]] for n in names] for r in t.rows]
        if kind == "date":
            vals = parse_column_dates([x[0] for x in raw])
            bad = sum(1 for a, b in zip(raw, vals) if not _blank(a[0]) and b is None)
            if bad:
                ctx.warnings.append(f"{spec['path']}: {bad} value(s) in '{names[0]}' did not read as dates.")
        elif kind == "number":
            vals = []
            for x in raw:
                nums = [parse_num(c) for c in x]
                vals.append(None if all(n is None for n in nums) else sum(n for n in nums if n is not None))
        else:
            vals = [None if _blank(x[0]) else (x[0] if not isinstance(x[0], float) else f"{x[0]:g}") for x in raw]
            vals = [str(v).strip() if v is not None else None for v in vals]
            if fld in vmaps:
                vm = vmaps[fld]
                mapped = []
                for v in vals:
                    m = _map_value(v, vm)
                    if v is not None and m is None:
                        if fld in ("outcome", "status"):
                            unmapped[fld].add(v)
                            m = None
                        else:
                            m = v  # leave practice areas, sources and the like as they are
                    mapped.append(m)
                vals = mapped
        out_cols[fld] = vals
    for fld, vs in unmapped.items():
        ctx.warnings.append(f"{spec['path']}: values not in the '{fld}' map were left blank: {sorted(vs)[:8]}")
    n = len(t.rows)
    rows = []
    for i in range(n):
        r = {f: out_cols[f][i] for f in out_cols}
        for k, v in file_level.items():
            d = parse_column_dates([v])[0] if isinstance(v, str) else v
            r[k] = d
        rows.append(r)
    req = ENTITIES[entity]["required"]
    keep = [r for r in rows if all(r.get(q) is not None for q in req)]
    if len(keep) < len(rows):
        ctx.warnings.append(f"{spec['path']}: {len(rows) - len(keep)} row(s) skipped for missing {req}.")
    ctx.files.append({"path": spec["path"], "entity": entity, "rows": len(keep), "skipped": len(rows) - len(keep),
                      "total_rows_ignored": t.dropped})
    return keep


def load_all(mapping, base, ctx):
    T = defaultdict(list)
    matters = {}
    for spec in mapping.get("files", []):
        rows = load_entity_rows(spec, base, ctx)
        if spec["entity"] == "matters":
            for r in rows:
                k = str(r["matter_id"]).strip()
                cur = matters.setdefault(k, {})
                for f, v in r.items():
                    if v is not None and cur.get(f) is None:
                        cur[f] = v
        else:
            T[spec["entity"]].extend(rows)
    T["matters"] = list(matters.values())
    ctx.T = T


def set_ranges(ctx):
    def dr(rows, f):
        ds = [r[f].date() for r in rows if r.get(f)]
        return (min(ds), max(ds)) if ds else None
    T = ctx.T
    ctx.range["leads"] = dr(T["leads"], "created_date")
    ctx.range["contacts"] = dr(T["contacts"], "received_at")
    ctx.range["time"] = dr(T["time"], "date")
    ctx.range["spend"] = dr(T["spend"], "period")
    ctx.range["matters"] = dr(T["matters"], "opened_date")
    for r in T["leads"]:
        r["cd"] = r["created_date"].date()
        r["od"] = r["outcome_date"].date() if r.get("outcome_date") else None
    for r in T["contacts"]:
        r["rd"] = r["received_at"].date()
    for r in T["time"]:
        r["d"] = r["date"].date()


# ----------------------------------------------------------------------------- facts


def classify(value, prior, direction, z, n1, n0, min_n, strict=False):
    if prior is None:
        return dict(change_class="no_comparison", status="gray", level=None, p=None, thin=(n1 is not None and n1 < min_n))
    thin = min(n1 if n1 is not None else 1e9, n0 if n0 is not None else 1e9) < min_n
    rel = (value - prior) / prior if prior else None
    p = p_two_sided(z) if z is not None else None
    if thin:
        return dict(change_class="thin", status="gray", level=None, p=p, thin=True)
    # People-level facts use a stricter bar: pinning a change on one person has a higher cost of being wrong.
    clear_p, likely_p = (.01, .05) if strict else (.05, .15)
    clear_r, likely_r = (.30, .15) if strict else (.20, .10)
    if p is not None:
        level = "clear" if p < clear_p else "likely" if p < likely_p else "noise"
    else:
        a = abs(rel) if rel is not None else 0
        level = "clear" if a >= clear_r else "likely" if a >= likely_r else "noise"
    if rel is not None and abs(rel) < .03:
        level = "noise"
    if level == "noise":
        return dict(change_class="flat", status="gray", level=level, p=p, thin=False)
    up = value > prior
    if direction == "neutral":
        return dict(change_class="changed", status="gray", level=level, p=p, thin=False)
    good = up == (direction == "higher_better")
    if good:
        return dict(change_class="improved", status="green", level=level, p=p, thin=False)
    red = level == "clear" and rel is not None and abs(rel) >= .10
    return dict(change_class="worsened", status="red" if red else "amber", level=level, p=p, thin=False)


def add_fact(ctx, metric, value, scope=None, n=None, win=None, prior=None, z=None, test=None, min_n=MIN_N,
             formula="", inputs=(), caveats=None, extra=None, impact=None, impact_note="", label=None,
             unit=None, direction=None):
    lab, u, d = METRICS[metric]
    unit = unit or u
    direction = direction or d
    scope = scope or {}
    ctx.counter[metric] += 1
    slug = "_".join(str(v).lower().replace(" ", "-") for v in scope.values()) or "all"
    fid = f"{metric}.{slug}"
    wkind, wspan = (win if win else (None, None))
    f = {"id": fid, "metric": metric, "label": label or lab, "scope": scope, "scope_label": scope_label(scope),
         "unit": unit, "value": value, "display": disp(unit, value), "n": n,
         "window": {"kind": wkind, "start": iso(wspan[0]) if wspan else None, "end": iso(wspan[1]) if wspan else None,
                    "label": (f"As of {wspan[1].strftime('%b')} {wspan[1].day}" if wkind == "snapshot" else fmt_range(wspan)) if wspan else None}
         if win else None,
         "direction": direction}
    pv = None
    if prior:
        pv, pn, pwin = prior
        f["prior"] = {"value": pv, "display": disp(unit, pv), "n": pn,
                      "window": {"start": iso(pwin[0]), "end": iso(pwin[1]), "label": fmt_range(pwin)} if pwin else None}
        if pv is not None and value is not None:
            f["delta_abs"] = value - pv
            f["delta_rel"] = (value - pv) / pv if pv else None
            if unit == "pct":
                f["delta_display"] = f"{(value - pv) * 100:+.1f} pts"
            elif unit == "usd":
                f["delta_display"] = f"{'+' if value >= pv else '-'}{fmt_money(abs(value - pv))}"
            elif unit == "minutes":
                f["delta_display"] = ("+" if value >= pv else "-") + disp("minutes", abs(value - pv))
            else:
                f["delta_display"] = f"{value - pv:+,.0f}"
            if f["delta_rel"] is not None:
                f["delta_rel_display"] = f"{f['delta_rel'] * 100:+.0f}%"
    else:
        f["prior"] = None
    strict = any(k in PEOPLE_LEVEL_SCOPES for k in scope)
    c = classify(value, pv, direction, z, n, (prior[1] if prior else None), min_n, strict) if value is not None else \
        dict(change_class="no_comparison", status="gray", level=None, p=None, thin=True)
    f["significance"] = {"test": test, "z": round(z, 3) if z is not None else None,
                         "p": round(c["p"], 4) if c["p"] is not None else None, "level": c["level"]}
    f["change_class"] = c["change_class"]
    f["status"] = c["status"]
    f["thin"] = bool(c["thin"]) or (n is not None and n < min_n and unit in ("pct", "minutes", "days", "usd") and metric not in ("ar_total",))
    if f["thin"] and prior is None:
        f["status"] = "gray"
    f["people_level"] = any(k in PEOPLE_LEVEL_SCOPES for k in scope)
    f["caveats"] = list(caveats or [])
    f["formula"] = formula
    f["inputs"] = list(inputs)
    keep_impact = impact is not None and c["change_class"] in ("worsened", "improved")
    f["impact_usd"] = impact if keep_impact else None
    f["impact_note"] = impact_note if keep_impact else ""
    if extra:
        f.update(extra)
    ctx.facts.append(f)
    return f


def choose_window(ctx, entity, end, count_fn, min_n, ladder=((30, "t30"), (90, "t90"))):
    """Shortest window where both this period and the one before have enough rows.
    If none does, fall back to a trailing 12 months with no comparison."""
    rng = ctx.range.get(entity)
    for days, kind in ladder:
        cur = window(end, days)
        pri = prior_window(cur)
        if rng and pri[0] >= rng[0] - timedelta(days=3):
            n1, n0 = count_fn(cur), count_fn(pri)
            if n1 >= min_n and n0 >= min_n:
                return kind, cur, pri, n1, n0
    cur = window(end, 365)
    if rng and cur[0] < rng[0]:
        cur = (rng[0], end)
        kind = "all_data"
    else:
        kind = "t12m"
    return kind, cur, None, count_fn(cur), None


# ---- leads ---------------------------------------------------------------------


def m_leads(ctx):
    leads = ctx.T["leads"]
    if not leads:
        return
    end = ctx.as_of
    sources = sorted({r["source"] for r in leads if r.get("source")})
    scopes = [None] + sources

    def rows_for(scope):
        return leads if scope is None else [r for r in leads if r["source"] == scope]

    def cnt(rows, w):
        return sum(1 for r in rows if w[0] <= r["cd"] <= w[1])

    for sc in scopes:
        rows = rows_for(sc)
        kind, cur, pri, n1, n0 = choose_window(ctx, "leads", end, lambda w: cnt(rows, w), 30)
        z = count_ratio_z(n1, n0) if pri else None
        add_fact(ctx, "lead_volume", n1, scope={"source": sc} if sc else None, n=n1, win=(kind, cur),
                 prior=(n0, n0, pri) if pri else None, z=z, test="poisson count ratio", min_n=0,
                 formula="Leads created in the window, counted from the lead export.", inputs=["leads"])
    # source mix over the last 90 days
    cur = window(end, 90)
    pri = prior_window(cur)
    tot1, tot0 = cnt(leads, cur), cnt(leads, pri)
    for s in sources:
        a = cnt(rows_for(s), cur)
        b = cnt(rows_for(s), pri)
        if tot1 and a:
            add_fact(ctx, "lead_source_share", a / tot1, scope={"source": s}, n=a, win=("t90", cur),
                     prior=(b / tot0, b, pri) if tot0 and ctx.range["leads"][0] <= pri[0] else None,
                     min_n=0, formula="Leads from this source divided by all leads in the window.", inputs=["leads"])
    # weekly series
    weekly = defaultdict(lambda: defaultdict(int))
    for r in leads:
        wk = r["cd"] - timedelta(days=r["cd"].weekday())
        weekly[None][wk] += 1
        weekly[r["source"]][wk] += 1
    last_wk = end - timedelta(days=end.weekday())
    for sc, m in weekly.items():
        pts = []
        d = last_wk - timedelta(weeks=26)
        while d < last_wk:   # the current week is partial, so leave it out
            pts.append({"x": iso(d), "y": m.get(d, 0)})
            d += timedelta(weeks=1)
        ctx.series.append({"id": f"lead_volume.weekly.{(sc or 'all').lower().replace(' ', '-')}", "metric": "lead_volume",
                           "scope": {"source": sc} if sc else {}, "unit": "count", "granularity": "week", "points": pts})


def decision_lag(leads):
    lags = [(r["od"] - r["cd"]).days for r in leads if r.get("outcome") in ("signed", "lost") and r.get("od")]
    lags = [x for x in lags if x >= 0]
    if len(lags) < 30:
        return 14
    return int(max(7, min(45, math.ceil(percentile(lags, .9)))))


def m_signed_rate(ctx):
    leads = [r for r in ctx.T["leads"] if r.get("outcome") is not None or r.get("od")]
    if not [r for r in ctx.T["leads"] if r.get("outcome")]:
        ctx.skipped.append(("signed_rate", "leads need an outcome column (hired, signed or retained)"))
        return
    allv = ctx.T["leads"]
    lag = decision_lag(allv)
    ctx.cohort_lag = lag
    end = ctx.as_of - timedelta(days=lag)
    sources = sorted({r["source"] for r in allv if r.get("source")})
    areas = sorted({r["practice_area"] for r in allv if r.get("practice_area")})
    scopes = [({}, allv)] + [({"source": s}, [r for r in allv if r["source"] == s]) for s in sources] + \
             [({"practice_area": a}, [r for r in allv if r.get("practice_area") == a]) for a in areas]
    have_est = sum(1 for r in allv if r.get("outcome") == "signed" and r.get("est_value")) >= \
        .7 * max(1, sum(1 for r in allv if r.get("outcome") == "signed"))
    for scope, rows in scopes:
        def cnt(w, rows=rows):
            return sum(1 for r in rows if w[0] <= r["cd"] <= w[1])
        kind, cur, pri, n1, n0 = choose_window(ctx, "leads", end, cnt, 30)

        def stat(w, rows=rows):
            sel = [r for r in rows if w[0] <= r["cd"] <= w[1]]
            return sum(1 for r in sel if r.get("outcome") == "signed"), len(sel), sel
        s1, m1, sel1 = stat(cur)
        if m1 == 0:
            continue
        v1 = s1 / m1
        prior = None
        z = None
        impact = None
        note = ""
        if pri:
            s0, m0, sel0 = stat(pri)
            if m0:
                prior = (s0 / m0, m0, pri)
                z = two_prop_z(s1, m1, s0, m0)
                if have_est and s0 / m0 > v1:
                    vals = [r["est_value"] for r in sel1 + sel0 if r.get("outcome") == "signed" and r.get("est_value")]
                    if vals:
                        avg = sum(vals) / len(vals)
                        impact = (s0 / m0 - v1) * m1 * avg
                        note = (f"Estimated fees not signed: {m1} leads x the {(s0 / m0 - v1) * 100:.1f} point drop x "
                                f"the average estimated value of signed leads ({fmt_money(avg)}). Uses the firm's own estimate field.")
        # the long-run rate for the same group: the last 12 months of leads old enough to have decided
        start = ctx.range["leads"][0]
        w12 = (max(end - timedelta(days=364), start), end)
        sel12 = [r for r in rows if w12[0] <= r["cd"] <= w12[1]]
        if sel12:
            sg12 = sum(1 for r in sel12 if r.get("outcome") == "signed")
            add_fact(ctx, "signed_rate_12m", sg12 / len(sel12), scope=scope, n=len(sel12), win=("t12m", w12),
                     formula="Signed leads divided by all leads created in the last 12 months, leaving out the newest leads "
                             "that have not had time to decide.", inputs=["leads"], extra={"signed": sg12})
        add_fact(ctx, "signed_rate", v1, scope=scope, n=m1, win=(kind, cur), prior=prior, z=z, test="two-proportion z",
                 formula=f"Signed leads divided by all leads created in the window. Windows end {lag} days ago so "
                         f"recent leads have had time to reach a decision.",
                 inputs=["leads"], impact=impact, impact_note=note,
                 extra={"signed": s1, "cohort_lag_days": lag})


def m_cost(ctx):
    T = ctx.T
    if not T["spend"] or not T["leads"]:
        ctx.skipped.append(("cost_per_lead / cost_per_signed", "needs a marketing spend file and the lead export"))
        return
    months = sorted({month_start(r["period"].date()) for r in T["spend"]})
    usable = [m for m in months if month_end(m) <= ctx.as_of]
    if len(usable) < 1:
        return
    M = usable[-1]
    P = add_months(M, -1)
    has_prior = P in months and ctx.range["leads"][0] <= P
    spend = defaultdict(float)
    for r in T["spend"]:
        spend[(month_start(r["period"].date()), r["source"])] += r["amount"]
    sources = sorted({s for (m, s) in spend if m == M})
    leads = T["leads"]
    outcome_ok = any(r.get("outcome") for r in leads)

    def lead_count(src, m):
        return sum(1 for r in leads if (src is None or r["source"] == src) and month_start(r["cd"]) == m)

    def signed_count(src, m):
        return sum(1 for r in leads if (src is None or r["source"] == src) and r.get("outcome") == "signed"
                   and r["od"] and month_start(r["od"]) == m)

    wM, wP = (M, month_end(M)), (P, month_end(P))
    series_cps = defaultdict(list)
    all_months = [m for m in usable[-12:]]
    for src in sources + [None]:
        srcs = sources if src is None else [src]
        sp1 = sum(spend[(M, s)] for s in srcs)
        sp0 = sum(spend[(P, s)] for s in srcs) if has_prior else None
        scope = {"source": src} if src else {"source": "All paid sources"}
        l1, l0 = lead_count(src, M) if src else sum(lead_count(s, M) for s in srcs), None
        if src is None:
            l1 = sum(lead_count(s, M) for s in srcs)
            l0 = sum(lead_count(s, P) for s in srcs)
        else:
            l0 = lead_count(src, P)
        if l1:
            prior = (sp0 / l0, l0, wP) if has_prior and sp0 and l0 else None
            z = log_ratio_z(sp1 / l1, l1, sp0 / l0, l0) if prior else None
            add_fact(ctx, "cost_per_lead", sp1 / l1, scope=scope, n=l1, win=("month", wM), prior=prior, z=z,
                     test="log ratio of rates", formula="Marketing spend for the month divided by leads created that month.",
                     inputs=["spend", "leads"], extra={"spend": sp1})
        if outcome_ok:
            s1 = sum(signed_count(s, M) for s in srcs)
            s0 = sum(signed_count(s, P) for s in srcs)
            if s1:
                prior = (sp0 / s0, s0, wP) if has_prior and sp0 and s0 else None
                z = log_ratio_z(sp1 / s1, s1, sp0 / s0, s0) if prior else None
                impact = (sp1 / s1 - sp0 / s0) * s1 if prior else None
                add_fact(ctx, "cost_per_signed", sp1 / s1, scope=scope, n=s1, win=("month", wM), prior=prior, z=z,
                         test="log ratio of rates",
                         formula="Marketing spend for the month divided by matters signed that month (by sign date).",
                         inputs=["spend", "leads"], impact=impact,
                         impact_note="Extra spend to sign the same number of matters at the new cost." if impact else "",
                         extra={"spend": sp1, "signed": s1})
        # the long-run baseline: the same ratios over the last 12 complete months
        yr = [m for m in usable[-12:] if m in months]
        if len(yr) >= 6:
            sp_y = sum(spend[(m, s)] for m in yr for s in srcs)
            ld_y = sum(lead_count(s, m) for m in yr for s in srcs)
            sg_y = sum(signed_count(s, m) for m in yr for s in srcs) if outcome_ok else 0
            span = (yr[0], month_end(yr[-1]))
            if ld_y:
                add_fact(ctx, "cost_per_lead_12m", sp_y / ld_y, scope=scope, n=ld_y, win=("t12m", span), min_n=MIN_N,
                         formula="Marketing spend over the last 12 complete months divided by leads created in them.",
                         inputs=["spend", "leads"], extra={"spend": sp_y})
            if sg_y:
                add_fact(ctx, "cost_per_signed_12m", sp_y / sg_y, scope=scope, n=sg_y, win=("t12m", span), min_n=MIN_N,
                         formula="Marketing spend over the last 12 complete months divided by matters signed in them.",
                         inputs=["spend", "leads"], extra={"spend": sp_y, "signed": sg_y})
        # monthly series
        for m in all_months:
            sg = sum(signed_count(s, m) for s in srcs)
            sp = sum(spend[(m, s)] for s in srcs)
            if outcome_ok and sg and sp:
                series_cps[src].append({"x": iso(m), "y": sp / sg, "n": sg})
    for src, pts in series_cps.items():
        ctx.series.append({"id": f"cost_per_signed.monthly.{(src or 'all-paid').lower().replace(' ', '-')}",
                           "metric": "cost_per_signed", "scope": {"source": src or "All paid sources"}, "unit": "usd",
                           "granularity": "month", "points": pts})


def daytype(dt):
    if dt.weekday() >= 5:
        return "Weekend"
    if 8 <= dt.hour < 18:
        return "Weekday, business hours"
    return "Weekday, after hours"


def m_speed(ctx):
    C = ctx.T["contacts"]
    if not C:
        ctx.skipped.append(("speed_to_lead", "needs a log with when each lead arrived and when someone first reached out"))
        return
    end = ctx.as_of - timedelta(days=CENSOR_DAYS)
    rows = [r for r in C if r["rd"] <= end]
    for r in rows:
        fc = r.get("first_contact_at")
        r["delay"] = (fc - r["received_at"]).total_seconds() / 60.0 if fc and fc >= r["received_at"] else None
        r["dt"] = daytype(r["received_at"])
    ctx.range["contacts_c"] = ctx.range["contacts"]

    def sel(w, f=None):
        return [r for r in rows if w[0] <= r["rd"] <= w[1] and (f is None or f(r))]

    def delays(w, f=None):
        return [r["delay"] for r in sel(w, f) if r["delay"] is not None]

    scopes = [({}, None)] + [({"arrival": t}, (lambda r, t=t: r["dt"] == t))
                             for t in ("Weekday, business hours", "Weekday, after hours", "Weekend")]
    for scope, f in scopes:
        kind, cur, pri, n1, n0 = choose_window(ctx, "contacts", end, lambda w, f=f: len(delays(w, f)), 30,
                                               ladder=((30, "t30"), (90, "t90")))
        d1 = delays(cur, f)
        if not d1:
            continue
        v1 = median(d1)
        prior, z = None, None
        if pri:
            d0 = delays(pri, f)
            prior = (median(d0), len(d0), pri)
            z = mannwhitney_z(d1, d0)
        add_fact(ctx, "speed_to_lead", v1, scope=scope, n=len(d1), win=(kind, cur), prior=prior, z=z,
                 test="Mann-Whitney", formula="Median minutes from a lead arriving to the first reach-out. Leads from the last "
                 f"{CENSOR_DAYS} days are left out because many have not been contacted yet.", inputs=["contacts"],
                 extra={"p90_minutes": percentile(d1, .9)})
    # share within an hour, never reached, after-hours mix
    def share_fact(metric, pred, base_pred, scope_key=None, w_ladder=((30, "t30"), (90, "t90")), f=None):
        scopes2 = [({}, None)]
        if scope_key == "source":
            srcs = sorted({r["source"] for r in ctx.T["leads"] if r.get("source")})
        for scope, ff in scopes2:
            kind, cur, pri, n1, n0 = choose_window(ctx, "contacts", end, lambda w: len(sel(w)), 30, ladder=w_ladder)
            a = sel(cur)
            x1 = sum(1 for r in a if pred(r))
            n_1 = len(a)
            if not n_1:
                continue
            prior, z = None, None
            if pri:
                b = sel(pri)
                x0 = sum(1 for r in b if pred(r))
                prior = (x0 / len(b), len(b), pri)
                z = two_prop_z(x1, n_1, x0, len(b))
            add_fact(ctx, metric, x1 / n_1, scope=scope, n=n_1, win=(kind, cur), prior=prior, z=z, test="two-proportion z",
                     formula="Share of leads received in the window.", inputs=["contacts"])

    share_fact("contacted_within_hour", lambda r: r["delay"] is not None and r["delay"] <= 60, None)
    share_fact("uncontacted_share", lambda r: r["delay"] is None, None)
    share_fact("after_hours_share", lambda r: r["dt"] != "Weekday, business hours", None)
    # by source: after-hours share needs the lead file for the source
    if ctx.T["leads"]:
        src_of = {str(r["lead_key"]).strip().lower(): r["source"] for r in ctx.T["leads"] if r.get("lead_key")}
        for r in rows:
            r["source"] = src_of.get(str(r["lead_key"]).strip().lower())
        sources = sorted({r["source"] for r in rows if r["source"]})
        for s in sources:
            def cnt(w, s=s):
                return len(sel(w, lambda r: r["source"] == s))
            kind, cur, pri, n1, n0 = choose_window(ctx, "contacts", end, cnt, 30, ladder=((30, "t30"), (90, "t90")))
            a = sel(cur, lambda r: r["source"] == s)
            if len(a) < 5:
                continue
            x1 = sum(1 for r in a if r["dt"] != "Weekday, business hours")
            prior, z = None, None
            if pri:
                b = sel(pri, lambda r: r["source"] == s)
                if b:
                    prior = (sum(1 for r in b if r["dt"] != "Weekday, business hours") / len(b), len(b), pri)
                    z = two_prop_z(x1, len(a), prior[0] * len(b), len(b))
            add_fact(ctx, "after_hours_share", x1 / len(a), scope={"source": s}, n=len(a), win=(kind, cur), prior=prior,
                     z=z, test="two-proportion z", formula="Share of this source's leads that arrive after 6pm, before 8am, or on a weekend.",
                     inputs=["contacts"])
    # monthly median series
    by_month = defaultdict(list)
    for r in rows:
        if r["delay"] is not None:
            by_month[month_start(r["rd"])].append(r["delay"])
    ms = sorted(by_month)[-12:]
    ctx.series.append({"id": "speed_to_lead.monthly.all", "metric": "speed_to_lead", "scope": {}, "unit": "minutes",
                       "granularity": "month",
                       "points": [{"x": iso(m), "y": median(by_month[m]), "n": len(by_month[m])} for m in ms if len(by_month[m]) >= 10]})
    # does speed matter? signed rate by response bucket, on a mature cohort
    if ctx.T["leads"] and getattr(ctx, "cohort_lag", None) is not None:
        lead_out = {str(r["lead_key"]).strip().lower(): r for r in ctx.T["leads"] if r.get("lead_key")}
        cend = ctx.as_of - timedelta(days=ctx.cohort_lag)
        w = window(cend, 90)
        buckets = [("Within 1 hour", lambda d: d is not None and d <= 60), ("1 to 4 hours", lambda d: d is not None and 60 < d <= 240),
                   ("4 to 24 hours", lambda d: d is not None and 240 < d <= 1440),
                   ("Over 24 hours or never", lambda d: d is None or d > 1440)]
        pool = [r for r in C if w[0] <= r["rd"] <= w[1] and str(r["lead_key"]).strip().lower() in lead_out]
        for r in pool:
            if "delay" not in r:
                fc = r.get("first_contact_at")
                r["delay"] = (fc - r["received_at"]).total_seconds() / 60.0 if fc and fc >= r["received_at"] else None
        for name, pred in buckets:
            sel_b = [r for r in pool if pred(r["delay"])]
            if not sel_b:
                continue
            sg = sum(1 for r in sel_b if lead_out[str(r["lead_key"]).strip().lower()].get("outcome") == "signed")
            add_fact(ctx, "signed_rate_by_response", sg / len(sel_b), scope={"first_contact": name}, n=len(sel_b),
                     win=("t90", w), formula="Signed leads divided by leads in that response-time group, on leads "
                     "old enough to have reached a decision.", inputs=["contacts", "leads"], extra={"signed": sg})


# ---- time and billing ----------------------------------------------------------


def infer_billing_lag(rows, as_of):
    """How many days until time entries are normally invoiced. Read from the share of unbilled entries."""
    weeks = defaultdict(lambda: [0, 0])
    for r in rows:
        if not r.get("billable_amount"):
            continue
        wk = r["d"] - timedelta(days=r["d"].weekday())
        weeks[wk][1] += 1
        if not r.get("billed_amount"):
            weeks[wk][0] += 1
    order = sorted(weeks, reverse=True)
    share = lambda k: weeks[k][0] / float(weeks[k][1]) if weeks[k][1] else 0
    for i, wk in enumerate(order):
        if all(share(order[j]) < .05 for j in range(i, min(i + 3, len(order)))):
            mature_end = wk + timedelta(days=6)
            return int(max(7, min(120, (as_of - mature_end).days)))
    return 45


def m_billing(ctx):
    rows = ctx.T["time"]
    if not rows:
        ctx.skipped.append(("realization / collection / utilization", "needs a time and billing report like Clio's realization report"))
        return
    lag = infer_billing_lag(rows, ctx.as_of)
    ctx.billing_lag = lag
    end = ctx.as_of - timedelta(days=lag)
    areas = sorted({r["practice_area"] for r in rows if r.get("practice_area")})
    atts = sorted({r["attorney"] for r in rows if r.get("attorney")})
    scopes = [({}, rows)] + [({"practice_area": a}, [r for r in rows if r.get("practice_area") == a]) for a in areas] + \
             [({"attorney": a}, [r for r in rows if r.get("attorney") == a]) for a in atts]

    def ratio(sel, num, den):
        n, d = [r.get(num) or 0.0 for r in sel], [r.get(den) or 0.0 for r in sel]
        return (sum(n) / sum(d) if sum(d) > 0 else None), n, d

    area_vals = {}
    for scope, srows in scopes:
        def cnt(w, srows=srows):
            return sum(1 for r in srows if w[0] <= r["d"] <= w[1])
        kind, cur, pri, n1, n0 = choose_window(ctx, "time", end, cnt, 40, ladder=((90, "t90"),))
        sel1 = [r for r in srows if cur[0] <= r["d"] <= cur[1] and (r.get("billable_amount") or 0) > 0]
        v1, a1, b1 = ratio(sel1, "billed_amount", "billable_amount")
        if v1 is None:
            continue
        prior, z, impact, note = None, None, None, ""
        if pri:
            sel0 = [r for r in srows if pri[0] <= r["d"] <= pri[1] and (r.get("billable_amount") or 0) > 0]
            v0, a0, b0 = ratio(sel0, "billed_amount", "billable_amount")
            if v0 is not None:
                prior = (v0, len(sel0), pri)
                z = ratio_z(a1, b1, a0, b0)
                impact = (v0 - v1) * sum(b1)
                note = f"Realization points lost x {fmt_money(sum(b1))} of work recorded in the window."
        f = add_fact(ctx, "realization", v1, scope=scope, n=len(sel1), win=(kind, cur), prior=prior, z=z, test="ratio estimator z",
                     formula="Billed amount divided by the original billable amount. The window ends "
                             f"{lag} days ago so the work has had time to be invoiced.",
                     inputs=["time"], impact=impact, impact_note=note,
                     extra={"billable": sum(b1), "billed": sum(a1)})
        if scope.get("practice_area"):
            area_vals[scope["practice_area"]] = (f, sel1, cur, pri)
    # who is behind a practice area's change
    for area, (f, sel1, cur, pri) in area_vals.items():
        if not f.get("prior") or f["prior"]["value"] is None or f["change_class"] not in ("worsened", "improved"):
            continue
        pool0 = [r for r in rows if r.get("practice_area") == area and pri[0] <= r["d"] <= pri[1] and (r.get("billable_amount") or 0) > 0]
        tot1 = sum(r["billable_amount"] for r in sel1)
        drop = f["prior"]["value"] - f["value"]
        for att in sorted({r["attorney"] for r in sel1 if r.get("attorney")}):
            a1 = [r for r in sel1 if r.get("attorney") == att]
            a0 = [r for r in pool0 if r.get("attorney") == att]
            if len(a1) < 15 or len(a0) < 15:
                continue
            r1 = sum(r["billed_amount"] or 0 for r in a1) / sum(r["billable_amount"] for r in a1)
            r0 = sum(r["billed_amount"] or 0 for r in a0) / sum(r["billable_amount"] for r in a0)
            share1 = sum(r["billable_amount"] for r in a1) / tot1
            contrib = (r0 - r1) * share1          # realization points this attorney moved the practice area
            add_fact(ctx, "realization_contribution", -contrib, scope={"practice_area": area, "attorney": att},
                     n=len(a1), win=("t90", cur), min_n=0, unit="pts",
                     formula="If this attorney had kept the earlier realization on the work recorded now, the practice "
                             "area would have moved this many points differently.",
                     inputs=["time"], extra={"attorney_realization": r1, "attorney_prior_realization": r0,
                                              "share_of_billable": share1,
                                              "share_of_change": (contrib / drop) if drop else None},
                     caveats=["People-level. A reason to ask a question, not a verdict."])
    # collection rate
    cend = ctx.as_of - timedelta(days=lag + COLLECTION_EXTRA_LAG)
    for scope, srows in [({}, rows)] + [({"practice_area": a}, [r for r in rows if r.get("practice_area") == a]) for a in areas]:
        if not any(r.get("collected_amount") is not None for r in srows):
            continue

        def cnt(w, srows=srows):
            return sum(1 for r in srows if w[0] <= r["d"] <= w[1] and (r.get("billed_amount") or 0) > 0)
        kind, cur, pri, n1, n0 = choose_window(ctx, "time", cend, cnt, 40, ladder=((90, "t90"),))
        sel1 = [r for r in srows if cur[0] <= r["d"] <= cur[1] and (r.get("billed_amount") or 0) > 0]
        v1, a1, b1 = ratio(sel1, "collected_amount", "billed_amount")
        if v1 is None:
            continue
        prior, z, impact = None, None, None
        if pri:
            sel0 = [r for r in srows if pri[0] <= r["d"] <= pri[1] and (r.get("billed_amount") or 0) > 0]
            v0, a0, b0 = ratio(sel0, "collected_amount", "billed_amount")
            if v0 is not None:
                prior = (v0, len(sel0), pri)
                z = ratio_z(a1, b1, a0, b0)
                impact = (v0 - v1) * sum(b1)
        add_fact(ctx, "collection_rate", v1, scope=scope, n=len(sel1), win=(kind, cur), prior=prior, z=z, test="ratio estimator z",
                 formula="Amount collected divided by the amount billed, on work old enough to have been paid "
                         f"(the window ends {lag + COLLECTION_EXTRA_LAG} days ago).",
                 inputs=["time"], impact=impact,
                 impact_note="Collection points lost x amount billed in the window." if impact else "")
    # utilization
    if any(r.get("hours") for r in rows):
        w = window(ctx.as_of, 90)
        pw = prior_window(w)

        def weekdays(w):
            return sum(1 for i in range((w[1] - w[0]).days + 1) if (w[0] + timedelta(days=i)).weekday() < 5)

        for scope in [{}] + [{"attorney": a} for a in atts]:
            def hrs(win_):
                sel = [r for r in rows if win_[0] <= r["d"] <= win_[1] and (not scope or r.get("attorney") == scope["attorney"])]
                people = {r["attorney"] for r in sel if r.get("attorney")}
                return sum(r.get("hours") or 0 for r in sel), len(sel), max(1, len(people) if not scope else 1)
            h1, n1, p1 = hrs(w)
            h0, n0, p0 = hrs(pw)
            if n1 < 20:
                continue
            u1 = h1 / (8.0 * weekdays(w) * p1)
            prior = (h0 / (8.0 * weekdays(pw) * p0), n0, pw) if ctx.range["time"][0] <= pw[0] and n0 >= 20 else None
            add_fact(ctx, "utilization", u1, scope=scope, n=n1, win=("t90", w), prior=prior,
                     formula="Hours recorded divided by 8 hours on every weekday in the window. Does not know about "
                             "vacations or part-time schedules.", inputs=["time"],
                     caveats=["Compare with the firm's own history first. Clio's Legal Trends report publishes a yearly benchmark."])
    # monthly realization series on mature months
    for scope, srows in scopes[:1 + len(areas)]:
        pts = []
        by = defaultdict(lambda: [0.0, 0.0, 0])
        for r in srows:
            if r["d"] <= end and (r.get("billable_amount") or 0) > 0:
                k = month_start(r["d"])
                by[k][0] += r.get("billed_amount") or 0
                by[k][1] += r["billable_amount"]
                by[k][2] += 1
        for k in sorted(by)[-12:]:
            if by[k][2] >= 15 and month_end(k) <= end:
                pts.append({"x": iso(k), "y": by[k][0] / by[k][1], "n": by[k][2]})
        ctx.series.append({"id": f"realization.monthly.{(scope.get('practice_area') or 'all').lower().replace(' ', '-')}",
                           "metric": "realization", "scope": scope, "unit": "pct", "granularity": "month", "points": pts})


# ---- receivables ---------------------------------------------------------------


def m_ar(ctx):
    rows = ctx.T["ar"]
    if not rows:
        ctx.skipped.append(("receivables over 90 days", "needs an accounts receivable aging report"))
        return
    snaps = sorted({r.get("snapshot_date") for r in rows if r.get("snapshot_date")})
    if not snaps:
        ctx.skipped.append(("receivables", "the aging report needs a snapshot date (what day was it run?)"))
        return
    by = {s: [r for r in rows if r.get("snapshot_date") == s] for s in snaps}
    s1 = snaps[-1]
    s0 = snaps[-2] if len(snaps) > 1 else None

    def tot(rs, f):
        return sum(r.get(f) or 0 for r in rs)

    def over90(rs):
        return tot(rs, "b_91_plus")

    win1 = ("snapshot", (s1.date(), s1.date()))
    win0 = (s0.date(), s0.date()) if s0 else None
    t1, t0 = tot(by[s1], "total"), tot(by[s0], "total") if s0 else None
    a1, a0 = over90(by[s1]), over90(by[s0]) if s0 else None
    n1 = sum(1 for r in by[s1] if (r.get("b_91_plus") or 0) > 0)
    n0 = sum(1 for r in by[s0] if (r.get("b_91_plus") or 0) > 0) if s0 else None
    add_fact(ctx, "ar_total", t1, n=len(by[s1]), win=win1, prior=(t0, len(by[s0]), win0) if s0 else None,
             min_n=0, formula="Sum of the Total column of the aging report.", inputs=["ar"])
    add_fact(ctx, "ar_over_90", a1, n=n1, win=win1, prior=(a0, n0, win0) if s0 else None, min_n=0,
             formula="Sum of the 91+ days column of the aging report.", inputs=["ar"],
             impact=(a1 - a0) if s0 else None, impact_note="Change in dollars sitting more than 90 days past due." if s0 else "")
    if t1:
        add_fact(ctx, "ar_over_90_share", a1 / t1, n=len(by[s1]), win=win1,
                 prior=(a0 / t0, len(by[s0]), win0) if s0 and t0 else None, min_n=0,
                 formula="Receivables over 90 days divided by total receivables.", inputs=["ar"])
    # concentration
    def conc(rs):
        m = defaultdict(float)
        for r in rs:
            m[r["matter_id"]] += r.get("b_91_plus") or 0
        tot_ = sum(m.values())
        top = sorted(m.items(), key=lambda kv: -kv[1])[:3]
        return tot_, top

    tt1, top1 = conc(by[s1])
    if tt1 > 0:
        tt0, top0 = conc(by[s0]) if s0 else (0, [])
        add_fact(ctx, "ar_over_90_concentration", top1[0][1] / tt1, scope={"matter": top1[0][0]}, n=n1, win=win1,
                 prior=(top0[0][1] / tt0, n0, win0) if s0 and tt0 and top0 else None, min_n=0,
                 formula="The matter with the most receivables over 90 days, as a share of all receivables over 90 days.",
                 inputs=["ar"], extra={"top_matters": [{"matter": m, "amount": a, "share": a / tt1} for m, a in top1]})
    for s in snaps[-2:]:
        rs = by[s]
        ctx.series.append({"id": f"ar_aging.{iso(s.date())}", "metric": "ar_total", "scope": {"snapshot": iso(s.date())},
                           "unit": "usd", "granularity": "snapshot",
                           "points": [{"x": lbl, "y": tot(rs, f)} for lbl, f in
                                      (("Current", "b_current"), ("1-30 days", "b_1_30"), ("31-60 days", "b_31_60"),
                                       ("61-90 days", "b_61_90"), ("91+ days", "b_91_plus"))]})


# ---- matters and revenue -------------------------------------------------------


def m_matters(ctx):
    ms = ctx.T["matters"]
    if not ms:
        return
    end = ctx.as_of
    closed = [m for m in ms if m.get("closed_date") and m.get("opened_date")]
    if closed:
        cur = window(end, 365)
        pri = prior_window(cur)
        rng = (min(m["opened_date"].date() for m in ms if m.get("opened_date")), end)
        # closing dates before the first export are not in the data, so the prior year is only usable with enough rows
        for scope, sel in [({}, closed)] + [({"practice_area": a}, [m for m in closed if m.get("practice_area") == a])
                                            for a in sorted({m["practice_area"] for m in closed if m.get("practice_area")})]:
            d1 = [(m["closed_date"] - m["opened_date"]).days for m in sel if cur[0] <= m["closed_date"].date() <= cur[1]]
            d1 = [x for x in d1 if x >= 0]
            if len(d1) < 5:
                continue
            add_fact(ctx, "matter_cycle_time", median(d1), scope=scope, n=len(d1), win=("t12m", cur),
                     formula="Median days from opening to closing, for matters closed in the last 12 months.",
                     inputs=["matters"], caveats=["Matters still open are not counted, so this reads shorter than the true average."])
    openm = [m for m in ms if m.get("status") == "open"]
    if openm:
        win = ("snapshot", (end, end))
        add_fact(ctx, "active_matters", len(openm), n=len(openm), win=win, min_n=0,
                 formula="Matters with an open or pending status.", inputs=["matters"])
        for key in ("practice_area", "attorney"):
            groups = defaultdict(int)
            for m in openm:
                if m.get(key):
                    groups[m[key]] += 1
            for g, c in sorted(groups.items(), key=lambda kv: -kv[1]):
                add_fact(ctx, "active_matters", c, scope={key: g}, n=c, win=win, min_n=0,
                         formula="Matters with an open or pending status.", inputs=["matters"])


def m_revenue(ctx):
    rows = ctx.T["revenue"]
    if not rows:
        ctx.skipped.append(("collected revenue", "needs a revenue report with its date range"))
        return
    periods = sorted({(r.get("period_start"), r.get("period_end")) for r in rows if r.get("period_end")}, key=lambda p: p[1])
    if not periods:
        ctx.skipped.append(("collected revenue", "the revenue report needs a date range (what period does it cover?)"))
        return
    cur_p = periods[-1]
    cur_len = (cur_p[1] - cur_p[0]).days
    pri_p = next((p for p in reversed(periods[:-1]) if abs((p[1] - cur_p[0]).days - 1) <= 4 or abs((cur_p[0] - p[1]).days) <= 4), None)
    win1 = ("period", (cur_p[0].date(), cur_p[1].date()))
    pwin = (pri_p[0].date(), pri_p[1].date()) if pri_p else None

    def sel(p):
        return [r for r in rows if (r.get("period_start"), r.get("period_end")) == p]
    r1 = sel(cur_p)
    r0 = sel(pri_p) if pri_p else None
    areas = sorted({r["practice_area"] for r in r1 if r.get("practice_area")})
    atts = sorted({r["attorney"] for r in r1 if r.get("attorney")})
    for scope, f in [({}, None)] + [({"practice_area": a}, ("practice_area", a)) for a in areas] + \
                    [({"attorney": a}, ("attorney", a)) for a in atts]:
        def tot(rs):
            return sum(r.get("collected") or 0 for r in rs if f is None or r.get(f[0]) == f[1])
        v1 = tot(r1)
        sel1 = [r for r in r1 if (f is None or r.get(f[0]) == f[1]) and (r.get("collected") or 0) > 0]
        if v1 <= 0:
            continue
        prior = (tot(r0), len([r for r in r0 if (f is None or r.get(f[0]) == f[1]) and (r.get("collected") or 0) > 0]), pwin) \
            if r0 and tot(r0) > 0 else None
        top3 = sorted((r.get("collected") or 0 for r in sel1), reverse=True)[:3]
        lumpy = len(sel1) >= 3 and sum(top3) / v1 >= .5
        caveats = []
        if lumpy:
            caveats.append(f"Lumpy: the three largest matters are {sum(top3) / v1 * 100:.0f}% of this total, so a swing here may be one or two cases.")
        impact = (v1 - prior[0]) if prior else None
        add_fact(ctx, "collected_revenue", v1, scope=scope, n=len(sel1), win=win1, prior=prior, min_n=0,
                 formula="Collected amounts from the revenue report for the period.", inputs=["revenue"],
                 caveats=caveats, impact=impact if (not scope) else None,
                 direction="neutral" if "attorney" in scope else None,   # revenue by person is lumpy, so no red or green
                 extra={"lumpy": lumpy, "period_days": cur_len + 1})


# ---- aggregated lead report -----------------------------------------------------


def m_lead_summary(ctx):
    rows = ctx.T["lead_summary"]
    if not rows:
        return
    for r in rows:
        intake = r.get("intake") or 0
        hired = r.get("hired") or 0
        denom = intake if intake else hired + (r.get("not_hired") or 0)
        if not denom:
            continue
        rate = (r.get("conversion_rate") or 0) / 100.0 if r.get("conversion_rate") and r["conversion_rate"] > 1 else (r.get("conversion_rate") or hired / float(denom))
        add_fact(ctx, "signed_rate", rate, scope={"source": r["source"]}, n=int(denom), win=None, min_n=MIN_N,
                 formula="Hired matters divided by intake matters, as reported by the lead source report. The report has no dates, so there is no trend.",
                 inputs=["lead_summary"], extra={"signed": hired, "static": True})
        if r.get("spend") and hired:
            add_fact(ctx, "cost_per_signed", r["spend"] / hired, scope={"source": r["source"]}, n=int(hired), win=None,
                     formula="Spend divided by hired matters, as reported.", inputs=["lead_summary"], extra={"static": True})


def annotate_scans(ctx):
    """When one metric is checked across many groups, a few swings happen by chance. Say so,
    and give each fact a plain confidence label."""
    fam = defaultdict(list)
    for f in ctx.facts:
        if f["scope"]:
            fam[(f["metric"], tuple(f["scope"].keys()))].append(f)
    for (metric, keys), fs in fam.items():
        k = keys[0]
        for f in fs:
            if len(fs) >= 4 and f["significance"]["level"] in ("clear", "likely") and (f["significance"]["p"] or 0) > .01:
                f["caveats"].append(f"One of {len(fs)} {k.replace('_', ' ')} groups checked. Swings this size sometimes happen by chance.")
    for f in ctx.facts:
        p, lvl = f["significance"]["p"], f["significance"]["level"]
        if f["change_class"] in ("no_comparison",):
            f["confidence"] = None
        elif f["thin"]:
            f["confidence"] = "too thin"
        elif p is not None:
            f["confidence"] = "high" if p < .01 else "medium" if p < .05 else "low"
        else:
            f["confidence"] = {"clear": "medium", "likely": "low"}.get(lvl, "low")


# ----------------------------------------------------------------------------- main

NEEDS = [("leads", "lead volume, source mix, signed rate"), ("spend", "cost per lead, cost per signed matter"),
         ("contacts", "speed to lead"), ("time", "realization, collection rate, utilization"),
         ("ar", "receivables over 90 days"), ("matters", "cycle time, open matters"), ("revenue", "collected revenue")]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--out", default="facts.json")
    ap.add_argument("--as-of")
    ap.add_argument("--summary", action="store_true", help="print a short readable summary")
    a = ap.parse_args(argv)
    mapping = json.load(open(a.mapping))
    base = os.path.dirname(os.path.abspath(a.mapping))
    ctx = Ctx()
    load_all(mapping, base, ctx)
    set_ranges(ctx)
    asof = a.as_of or mapping.get("as_of")
    if asof:
        ctx.as_of = parse_column_dates([asof])[0].date()
    else:
        cands = [r[1] for k, r in ctx.range.items() if r and k in ("leads", "contacts", "time")]
        ctx.as_of = max(cands) if cands else date.today()
    for fn in (m_leads, m_signed_rate, m_cost, m_speed, m_billing, m_ar, m_matters, m_revenue, m_lead_summary):
        try:
            fn(ctx)
        except Exception as e:  # keep going, and say so
            ctx.warnings.append(f"{fn.__name__} failed: {type(e).__name__}: {e}")
    annotate_scans(ctx)
    have = {e for e in ctx.T if ctx.T[e]}
    unavailable = [{"needs": e, "unlocks": u} for e, u in NEEDS if e not in have]
    out = {"version": VERSION, "firm": mapping.get("firm"), "as_of": iso(ctx.as_of), "files": ctx.files,
           "billing_lag_days": getattr(ctx, "billing_lag", None), "lead_decision_lag_days": getattr(ctx, "cohort_lag", None),
           "unavailable": unavailable, "skipped": [{"metric": m, "reason": r} for m, r in ctx.skipped],
           "warnings": ctx.warnings, "facts": ctx.facts, "series": ctx.series, "profile": mapping.get("profile", {})}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    if a.summary:
        print(f"as of {out['as_of']}  facts: {len(ctx.facts)}  series: {len(ctx.series)}  warnings: {len(ctx.warnings)}")
        for w in ctx.warnings:
            print("  warning:", w)
        for f in ctx.facts:
            if f["change_class"] in ("worsened", "improved") or f["metric"] in ("cost_per_signed",):
                pv = f["prior"]["display"] if f.get("prior") else "-"
                print(f"  {f['status']:5} {f['id']:55} {f['display']:>10}  vs {pv:>10}  {f['change_class']} {f['significance']['level']} n={f['n']}")
    else:
        print(f"Wrote {a.out}: {len(ctx.facts)} facts, {len(ctx.series)} series, {len(ctx.warnings)} warnings.")


if __name__ == "__main__":
    main()
