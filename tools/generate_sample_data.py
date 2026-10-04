#!/usr/bin/env python3
"""Generate the synthetic Super Duper Law sample data.

Super Duper Law is a fictional 12-lawyer firm. Nothing here comes from a real firm.
Four practice areas, three billing models: hourly (family law, business litigation),
flat fee (estate planning), contingency (personal injury).

Files that mirror Clio exports use column names taken from Clio's help center.
Files that do not (the matter list, the intake log, the spend sheet) are written the way a
firm would build them by hand.

Planted signals the evals check (see evals/ground_truth.py, which recomputes them
independently from the files this script writes):

  1. Google LSA cost per signed matter roughly doubles in September 2026 while LSA lead
     volume holds flat. Mechanism: after a schedule change, more LSA leads arrive on
     evenings and weekends, and those leads wait longer for a first contact.
  2. Family law realization drops. One attorney's write-downs jump from June 2026.
  3. Accounts receivable over 90 days climbs between the two aging snapshots,
     concentrated in one business litigation matter.
  4. Median speed to lead is far slower on weekends than on weekdays.
  5. Thin data: a brand new referral source sends four leads and all four hire.
  6. A non-signal: total lead volume is up a few percent, inside normal variation.

Usage:  python3 tools/generate_sample_data.py [--out sample-data/super-duper-law] [--seed N]
Needs the standard library, plus openpyxl for the one .xlsx file.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
from collections import defaultdict
from datetime import date, datetime, timedelta

AS_OF = date(2026, 10, 4)          # a Sunday, so the Monday briefing is for Oct 5
START = date(2025, 4, 5)           # 18 months of history
LSA_CHANGE = date(2026, 9, 1)      # the LSA schedule change
FAMILY_DROP = date(2026, 6, 1)
LSA_BH_AFTER = .26                 # share of LSA leads arriving in business hours after the change
PLANTS = True                      # --no-plants builds a quiet firm where nothing planted happens (used by the evals)     # one family attorney's write-downs jump
NEW_SOURCE_START = date(2026, 8, 10)
STUCK_NAME = "Delacroix Supply v. Harlan Industrial"

# ---------------------------------------------------------------- people

ATTORNEYS = {
    # name: (practice area, billing method, hourly rate)
    "Elena Brightwater": ("Family law", "Hourly", 450),
    "Tomas Ferreira": ("Family law", "Hourly", 300),
    "Wren Kowalczyk": ("Family law", "Hourly", 275),
    "Jordan Pemberton": ("Business litigation", "Hourly", 500),
    "Imani Rourke": ("Business litigation", "Hourly", 475),
    "Aisha Lindqvist": ("Business litigation", "Hourly", 325),
    "Caleb Moreau": ("Business litigation", "Hourly", 275),
    "Rosalind Achterberg": ("Estate planning", "Flat fee", 0),
    "Hiro Vandermeer": ("Estate planning", "Flat fee", 0),
    "Gideon Strand": ("Personal injury", "Contingency", 0),
    "Noor Castellanos": ("Personal injury", "Contingency", 0),
    "Luca Bergstrom": ("Personal injury", "Contingency", 0),
}
PARTNERS = ["Elena Brightwater", "Jordan Pemberton", "Imani Rourke", "Rosalind Achterberg", "Gideon Strand"]
ASSIGN_WEIGHTS = {
    "Family law": [("Elena Brightwater", .30), ("Tomas Ferreira", .28), ("Wren Kowalczyk", .42)],
    "Business litigation": [("Jordan Pemberton", .30), ("Imani Rourke", .28), ("Aisha Lindqvist", .22), ("Caleb Moreau", .20)],
    "Estate planning": [("Rosalind Achterberg", .5), ("Hiro Vandermeer", .5)],
    "Personal injury": [("Gideon Strand", .40), ("Noor Castellanos", .35), ("Luca Bergstrom", .25)],
}
HOURLY_ATTORNEYS = [a for a, v in ATTORNEYS.items() if v[1] == "Hourly"]
BILLING = {"Family law": "Hourly", "Business litigation": "Hourly", "Estate planning": "Flat fee", "Personal injury": "Contingency"}

GIVEN = ("Ada Amara Beatrix Callum Dara Eamon Farah Gus Hana Ines Jonas Kira Lars Mina Nico Odette Pia Quinn Rafa "
         "Sana Theo Una Vera Wes Xena Yusuf Zara Anders Bryn Cleo Dev Elio Fern Greta Hugo Isla Joss Kai Leona "
         "Milo Nora Orla Pax Remy Sol Tess Uri Vik Wynn Yara Zane Aldo Bea Cyrus Dion Edie Finn Gail Hal Iris").split()
SURNAME = ("Abernathy Bellweather Castellane Dunmore Everhart Fairbairn Galloway Hartnell Ingram Jessup Kettering "
           "Lockhart Merriweather Northcott Ostrander Penhallow Quillfeather Radcliffe Stanhope Thistlewood "
           "Underhill Vandenberg Whitlock Yarborough Zimmerman Ashdown Brackenridge Cavendish Dunleavy Eastwick "
           "Fitzwilliam Grayling Holloway Ivesley Jarrow Kingsley Lindgren Montrose Nightingale Okonkwo Pemberley "
           "Rothwell Sutcliffe Tillman Ullman Valdez Wetherby Xiong Yoshida Zeller Aldridge Birchfield Cranmer "
           "Delacourt Ellsworth Fenwick Gilchrist Hargrove").split()
ORGS = ("Harlan Industrial|Delacroix Supply|Northgate Freight|Brightline Dental|Copperfield Roasters|Evergreen Outfitters|"
        "Marlow Building Group|Pinecrest Logistics|Redwood Analytics|Silverleaf Foods|Tidewater Marine|"
        "Umber Creative|Westfall Tool and Die|Alder Street Bakery|Kestrel Aviation|Lumen Optics|"
        "Granite State Roofing|Foxglove Florals|Bellwether Pet Care|Ironbark Fabrication").split("|")

MATTER_TYPES = {
    "Family law": [("Divorce", .5), ("Child custody", .3), ("Spousal support", .2)],
    "Business litigation": [("Contract dispute", .5), ("Partnership dispute", .3), ("Non-compete", .2)],
    "Estate planning": [("Will and trust", .55), ("Probate", .25), ("Power of attorney", .20)],
    "Personal injury": [("Car accident", .55), ("Slip and fall", .3), ("Dog bite", .15)],
}
EST_VALUE = {"Family law": (5000, 12000), "Business litigation": (15000, 60000),
             "Estate planning": (2500, 6500), "Personal injury": (20000, 90000)}
LIFETIME_MEDIAN = {"Family law": 200, "Business litigation": 330, "Estate planning": 40, "Personal injury": 450}

# source: monthly leads, base sign prob, business-hours share, practice mix
SOURCES = {
    "Google LSA": dict(vol=70, base=.46, bh=.76, mix={"Family law": .38, "Personal injury": .34, "Estate planning": .20, "Business litigation": .08}),
    "Google Ads": dict(vol=28, base=.34, bh=.78, mix={"Family law": .30, "Business litigation": .25, "Estate planning": .20, "Personal injury": .25}),
    "Website": dict(vol=22, base=.38, bh=.72, mix={"Family law": .30, "Business litigation": .20, "Estate planning": .30, "Personal injury": .20}),
    "Attorney referral": dict(vol=14, base=.75, bh=.85, mix={"Business litigation": .35, "Personal injury": .30, "Family law": .20, "Estate planning": .15}),
    "Past client": dict(vol=9, base=.85, bh=.80, mix={"Estate planning": .40, "Family law": .25, "Business litigation": .20, "Personal injury": .15}),
    "Avvo": dict(vol=10, base=.26, bh=.70, mix={"Family law": .40, "Personal injury": .30, "Estate planning": .20, "Business litigation": .10}),
    "Facebook": dict(vol=14, base=.19, bh=.60, mix={"Family law": .45, "Personal injury": .35, "Estate planning": .15, "Business litigation": .05}),
}
SPEND_BASE = {"Google LSA": 9000, "Google Ads": 6500, "Facebook": 2800, "Avvo": 1200}
PRACTICE_SIGN = {"Family law": 1.0, "Business litigation": .85, "Estate planning": 1.1, "Personal injury": .9}
REFERRERS = ["Harper & Cole, CPAs", "Nguyen Wealth Advisors", "Judge Alder (ret.)", "Cobalt Bank trust group", "Dr. Amara Fenn", "Lindqvist Realty"]
WEALTH_REFERRER = "Cobalt Bank trust group"


def pick(rng, pairs):
    r = rng.random() * sum(w for _, w in pairs)
    for v, w in pairs:
        r -= w
        if r <= 0:
            return v
    return pairs[-1][0]


def poisson(rng, lam):
    if lam <= 0:
        return 0
    if lam > 40:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    l, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= l:
            return k
        k += 1


def lognorm(rng, median, sigma):
    return rng.lognormvariate(math.log(median), sigma)


def daterange(a, b):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def resp_factor(delay):
    if delay is None:
        return .05
    if delay <= 60:
        return 1.0
    if delay <= 240:
        return .70
    if delay <= 720:
        return .40
    if delay <= 1440:
        return .25
    return .15


# ---------------------------------------------------------------- leads

DOW = [1.0, 1.05, 1.05, 1.0, .95, .50, .42]  # Mon..Sun


def simulate_leads(rng):
    leads = []
    seq = 0
    for day in daterange(START, AS_OF):
        # gentle seasonality and growth
        month_idx = (day.year - START.year) * 12 + day.month - START.month
        season = 1 + .08 * math.sin((day.month - 1) / 12 * 2 * math.pi)
        growth = 1 + .004 * month_idx
        for src, p in SOURCES.items():
            dows = list(DOW)
            bh = p["bh"]
            if src == "Google LSA" and day >= LSA_CHANGE:
                if PLANTS:
                    bh = LSA_BH_AFTER
                    dows[5] *= 2.0
                    dows[6] *= 2.0
            lam = p["vol"] / 30.4 * (dows[day.weekday()] / (sum(dows) / 7.0)) * season * (growth if src != "Google LSA" else 1.0)
            # lead-volume lift in the last 60 days for non-LSA sources (the non-signal)
            if PLANTS and src != "Google LSA" and day >= AS_OF - timedelta(days=29):
                lam *= 1.11
            if src == "Google LSA":
                count = max(0, int(round(rng.gauss(lam, math.sqrt(lam) * .4))))   # budget-capped, steadier than organic
            else:
                count = poisson(rng, lam)
            for _ in range(count):
                seq += 1
                leads.append(make_lead(rng, seq, day, src, bh))
    # the new referral source: four leads, all hire
    for i, d in enumerate([date(2026, 8, 10), date(2026, 8, 17), date(2026, 8, 24), date(2026, 8, 31)]):
        seq += 1
        l = make_lead(rng, seq, d, "Wealth advisor referral", .9, practice="Estate planning", force_hire=True)
        leads.append(l)
    seq += 1
    l = make_lead(rng, seq, date(2026, 9, 28), "Wealth advisor referral", .9, practice="Estate planning")
    leads.append(l)
    leads.sort(key=lambda x: x["created"])
    return leads


def make_lead(rng, seq, day, src, bh, practice=None, force_hire=False):
    p = SOURCES.get(src)
    practice = practice or pick(rng, list(p["mix"].items()))
    mtype = pick(rng, MATTER_TYPES[practice])
    weekend = day.weekday() >= 5
    if weekend:
        ctx, hour = "weekend", rng.randint(9, 21)
    elif rng.random() < bh:
        ctx, hour = "business", rng.randint(8, 16)
    else:
        ctx = "after_hours"
        hour = rng.randint(17, 23) if rng.random() < .8 else rng.randint(5, 7)
    created = datetime(day.year, day.month, day.day, hour, rng.randint(0, 59))
    if ctx == "business":
        delay = None if rng.random() < .03 else lognorm(rng, 20, .9)
    elif ctx == "after_hours":
        delay = None if rng.random() < .07 else lognorm(rng, 660, .7)
    else:
        delay = None if rng.random() < .10 else lognorm(rng, 540, 1.0)
    if delay is not None:
        delay = min(delay, 7200)
    base = p["base"] if p else .8
    ps = base * resp_factor(delay) * PRACTICE_SIGN[practice] * rng.uniform(.9, 1.1)
    hired = True if force_hire else rng.random() < min(ps, .95)
    fast = src in ("Attorney referral", "Past client", "Wealth advisor referral")
    if hired:
        lag = 1 + int(lognorm(rng, 2 if fast else 4, .6))
        decide = created.date() + timedelta(days=min(lag, 21))
    else:
        lag = 2 + int(lognorm(rng, 6, .6))
        decide = created.date() + timedelta(days=min(lag, 25))
    given, sur = rng.choice(GIVEN), rng.choice(SURNAME)
    client = rng.choice(ORGS) if practice == "Business litigation" and rng.random() < .55 else f"{given} {sur}"
    surname_for_matter = client.split()[0] if client in ORGS else sur
    return dict(seq=seq, created=created, source=src, practice=practice, mtype=mtype, ctx=ctx,
                delay=delay, hired=hired, decide=decide, client=client, given=given, sur=sur,
                surname=surname_for_matter, email=f"{given}.{sur}{seq}@example.com".lower(),
                referred=rng.choice(REFERRERS) if src == "Attorney referral" else (WEALTH_REFERRER if src == "Wealth advisor referral" else ""),
                est=int(rng.uniform(*EST_VALUE[practice]) / 100) * 100)


def outcome(lead):
    if lead["decide"] > AS_OF:
        return "Intake", rng_status_open(lead), lead["created"].date()
    if lead["hired"]:
        return "Hired", "Retainer signed", lead["decide"]
    return "Did Not Hire", NOT_HIRED[lead["seq"] % len(NOT_HIRED)], lead["decide"]


NOT_HIRED = ["Chose another firm", "Not a fit", "No response", "Conflict of interest", "Fee concerns"]
OPEN_DETAIL = ["New", "Consultation scheduled", "Awaiting documents"]


def rng_status_open(lead):
    return OPEN_DETAIL[lead["seq"] % len(OPEN_DETAIL)]


# ---------------------------------------------------------------- matters

def new_matter(rng, num, name_surname, client, practice, open_date, desc, source="", force_attorney=None):
    attorney = force_attorney or pick(rng, ASSIGN_WEIGHTS[practice])
    life = max(14, int(lognorm(rng, LIFETIME_MEDIAN[practice], .5)))
    close = open_date + timedelta(days=life)
    closed = close <= AS_OF
    status = "Closed" if closed else ("Pending" if rng.random() < .06 else "Open")
    return dict(num=num, name=f"{num:05d}-{name_surname}", client=client, practice=practice,
                billing=BILLING[practice], open=open_date, close=close if closed else None,
                end=close, status=status, attorney=attorney,
                orig=rng.choice(PARTNERS), desc=desc, source=source, location="Downtown",
                fee=None, invoices=[])


def build_matters(rng, leads):
    matters = []
    num = 100
    # backlog at START
    for attorney, (practice, billing, _) in ATTORNEYS.items():
        count = {"Hourly": 24, "Flat fee": 7, "Contingency": 16}[billing]
        for _ in range(count):
            num += 1
            open_date = START - timedelta(days=rng.randint(10, 540))
            m = new_matter(rng, num, rng.choice(SURNAME), f"{rng.choice(GIVEN)} {rng.choice(SURNAME)}",
                           practice, open_date, pick(rng, MATTER_TYPES[practice]), force_attorney=attorney)
            if m["end"] <= START:
                m["end"] = START + timedelta(days=rng.randint(30, 300))
                m["close"] = m["end"] if m["end"] <= AS_OF else None
                m["status"] = "Closed" if m["close"] else "Open"
            matters.append(m)
    # hired leads
    lead_to_matter = {}
    for l in leads:
        st, _, sdate = outcome(l)
        if st != "Hired":
            continue
        num += 1
        m = new_matter(rng, num, l["surname"], l["client"], l["practice"], sdate, l["mtype"], source=l["source"])
        l["matter_name"] = m["name"]
        matters.append(m)
    # the stuck matter
    num += 1
    stuck = new_matter(rng, num, "Delacroix", "Delacroix Supply", "Business litigation",
                       date(2025, 11, 12), "Contract dispute", force_attorney="Jordan Pemberton")
    stuck["end"] = date(2027, 3, 1)
    stuck["close"] = None
    stuck["status"] = "Open"
    stuck["stuck"] = True
    stuck["desc"] = STUCK_NAME
    stuck["orig"] = "Jordan Pemberton"
    matters.append(stuck)
    return matters


# ---------------------------------------------------------------- time and billing

def build_time(rng, matters):
    by_att = defaultdict(list)
    for m in matters:
        if m["billing"] == "Hourly":
            by_att[m["attorney"]].append(m)
    holidays = {date(2025, 5, 26), date(2025, 7, 4), date(2025, 9, 1), date(2025, 11, 27), date(2025, 12, 25),
                date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 5, 25), date(2026, 7, 3), date(2026, 9, 7)}
    entries = []
    stuck = [m for m in matters if m.get("stuck")][0]
    for att in HOURLY_ATTORNEYS:
        rate = ATTORNEYS[att][2]
        pool = by_att[att]
        for day in daterange(START, AS_OF):
            if day.weekday() >= 5 or day in holidays:
                continue
            n = pick(rng, [(0, .15), (1, .30), (2, .35), (3, .20)])
            active = [m for m in pool if m["open"] <= day <= m["end"]]
            if not active:
                continue
            for _ in range(n):
                m = rng.choice(active)
                qty = round(min(6.0, max(.2, lognorm(rng, 1.5, .6))) * 10) / 10
                entries.append(dict(date=day, att=att, rate=rate, qty=qty, matter=m))
    # the stuck matter: heavy trial prep Jan to Aug 2026
    for day in daterange(date(2026, 1, 5), date(2026, 8, 31)):
        if day.weekday() >= 5:
            continue
        for att in ("Jordan Pemberton", "Imani Rourke", "Caleb Moreau"):
            if rng.random() < .25:
                qty = round(rng.uniform(3, 6.0) * 10) / 10
                entries.append(dict(date=day, att=att, rate=ATTORNEYS[att][2], qty=qty, matter=stuck))
    entries.sort(key=lambda e: (e["date"], e["att"]))
    return entries


def realization_factor(rng, att, day):
    r = rng.random()
    if PLANTS and att == "Wren Kowalczyk" and day >= FAMILY_DROP:
        return 1.0 if r < .15 else (.6 if r < .40 else .3)
    return 1.0 if r < .60 else (.8 if r < .85 else .5)


def build_invoices(rng, entries, matters):
    """One invoice per matter per entry month. Returns dict key -> invoice."""
    invs = {}
    seq = 1000
    for e in entries:
        key = (e["matter"]["num"], e["date"].year, e["date"].month)
        if key not in invs:
            seq += 1
            y, mo = e["date"].year, e["date"].month
            month_end = date(y + (mo == 12), (mo % 12) + 1, 1) - timedelta(days=1)
            inv_date = month_end + timedelta(days=10 if e["matter"].get("stuck") else rng.randint(5, 14))
            due = inv_date + timedelta(days=30)
            m = e["matter"]
            unpaid = False
            if PLANTS and m.get("stuck") and inv_date >= date(2026, 3, 1):
                unpaid = True               # disputed from the Feb work onward
            elif rng.random() < .02:
                unpaid = True               # a few small invoices never get paid
            pay = None
            if not unpaid:
                pay = due + timedelta(days=int(lognorm(rng, 10, .9)) - 12)
            invs[key] = dict(no=f"INV-{seq:05d}", date=inv_date, due=due, pay=pay, matter=m, billed=0.0, entries=[])
        invs[key]["entries"].append(e)
    for key, inv in invs.items():
        for e in inv["entries"]:
            e["inv"] = inv
            orig = e["qty"] * e["rate"]
            f = realization_factor(rng, e["att"], e["date"])
            e["orig"] = orig
            e["billed"] = round(orig * f, 2)
            e["factor"] = f
            inv["billed"] += e["billed"]
        inv["billed"] = round(inv["billed"], 2)
        inv["matter"]["invoices"].append(inv)
    return invs


# ---------------------------------------------------------------- non-hourly fees

def build_fees(rng, matters):
    """Flat fee and contingency collections. Returns list of (matter, date, amount, kind)."""
    fees = []
    for m in matters:
        if m["billing"] == "Flat fee":
            fee = int(rng.uniform(2500, 6500) / 50) * 50
            m["fee"] = fee
            half = round(fee / 2, 2)
            if m["open"] >= START - timedelta(days=60) and m["open"] <= AS_OF:
                fees.append((m, m["open"] + timedelta(days=rng.randint(1, 5)), half, "retainer"))
            if m["close"]:
                fees.append((m, m["close"], fee - half, "balance"))
        elif m["billing"] == "Contingency" and m["close"]:
            gross = lognorm(rng, 55000, .9)
            fee = round(gross * .33, 2)
            m["fee"] = fee
            fees.append((m, m["close"], fee, "settlement"))
    return fees


# ---------------------------------------------------------------- writers

def money(x):
    return f"{x:.2f}"


def us(d):
    return d.strftime("%m/%d/%Y")


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def ar_snapshot(matters, snap):
    """Outstanding invoices at a snapshot date, aged by days past due."""
    rows = []
    for m in matters:
        for inv in m["invoices"]:
            if inv["date"] > snap:
                continue
            if inv["pay"] is not None and inv["pay"] <= snap:
                continue
            past = (snap - inv["due"]).days
            b = [0.0] * 5
            idx = 0 if past <= 0 else 1 if past <= 30 else 2 if past <= 60 else 3 if past <= 90 else 4
            b[idx] = inv["billed"]
            rows.append((m, inv, b))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sample-data/super-duper-law")
    ap.add_argument("--seed", type=int, default=354)
    ap.add_argument("--no-plants", action="store_true", help="a quiet firm: no planted signals")
    args = ap.parse_args()
    global PLANTS
    PLANTS = not args.no_plants
    os.makedirs(args.out, exist_ok=True)
    rng = random.Random(args.seed)

    leads = simulate_leads(rng)
    matters = build_matters(rng, leads)
    entries = build_time(rng, matters)
    invs = build_invoices(rng, entries, matters)
    fees = build_fees(rng, matters)

    # 1. Clio Grow, Matter revenue report (Grow columns)
    rows = []
    for l in leads:
        st, detail, sdate = outcome(l)
        rows.append([l["client"], l["email"], l["source"], l["referred"], f"{l['surname']}-{l['mtype']}",
                     l["mtype"], l["mtype"], st, detail, us(sdate),
                     l["created"].strftime("%m/%d/%Y %I:%M %p"), "Downtown", l["est"]])
    write_csv(f"{args.out}/clio-grow-matter-revenue-report.csv",
              ["Contact", "Email", "Source", "Referred by", "Matter", "Description", "Matter type",
               "Matter status - top level", "Matter status - detailed", "Status date", "Created at", "Location",
               "Estimated value"], rows)

    # 2. Intake call log (owner-built)
    rows = []
    for l in leads:
        first = ""
        if l["delay"] is not None:
            fc = l["created"] + timedelta(minutes=l["delay"])
            if fc <= datetime(AS_OF.year, AS_OF.month, AS_OF.day, 23, 59):   # no contacts logged in the future
                first = fc.strftime("%Y-%m-%d %H:%M")
        handler = "On-call" if l["ctx"] != "business" else ("Maya" if l["seq"] % 2 else "Josh")
        rows.append([l["email"], l["created"].strftime("%Y-%m-%d %H:%M"), first, handler])
    write_csv(f"{args.out}/intake-call-log.csv", ["Contact email", "Received at", "First contact at", "Handled by"], rows)

    # 3. Clio realization report
    rows = []
    for e in entries:
        inv, m = e["inv"], e["matter"]
        billed_flag = inv["date"] <= AS_OF
        billed = e["billed"] if billed_flag else 0.0
        discount = round(e["orig"] - e["billed"], 2) if billed_flag else 0.0
        collected = billed if (billed_flag and inv["pay"] is not None and inv["pay"] <= AS_OF) else 0.0
        outstanding = round(billed - collected, 2)
        status = "Unbilled" if not billed_flag else ("Paid" if collected else "Open")
        rows.append([us(e["date"]), e["att"], "Time", status, inv["no"] if billed_flag else "", "Hourly",
                     money(e["rate"]), e["qty"], money(e["orig"]), "0.00", money(e["orig"]), e["qty"],
                     money(discount), money(round(e["qty"] * (1 - e["factor"]), 2)) if billed_flag else "0.00",
                     money(billed), round(e["qty"] * e["factor"], 2) if billed_flag else 0, money(collected), "0.00",
                     money(outstanding), m["name"], "Hourly", m["practice"], m["attorney"], m["orig"]])
    write_csv(f"{args.out}/clio-realization-report.csv",
              ["Time entry date", "User", "Time Entry Type", "Invoice Status", "Invoice Number", "Rate Type", "Rate",
               "Quantity", "Original Billable Total", "Original Non-Billable Total", "Adjusted Amount", "Adjusted Hours",
               "Amount Discounted", "Hours Discounted", "Billed Time Amount", "Billed Hours", "Billed Time Collected",
               "Billed Time Credited", "Billed Time Outstanding", "Matter Number", "Matter Billing Method",
               "Practice Area", "Responsible Attorney", "Originating Attorney"], rows)

    # 4. AR aging snapshots (two exports a month apart)
    for snap in (date(2026, 9, 6), AS_OF):
        data = ar_snapshot(matters, snap)
        rows = []
        tot = [0.0] * 5
        for m, inv, b in sorted(data, key=lambda t: (t[0]["name"], t[1]["date"])):
            rows.append([m["name"], m["orig"], m["attorney"], inv["no"]] + [f"${x:,.2f}" if x else "$0.00" for x in b]
                        + [f"${sum(b):,.2f}"])
            tot = [a + c for a, c in zip(tot, b)]
        rows.append(["Total", "", "", ""] + [f"${x:,.2f}" for x in tot] + [f"${sum(tot):,.2f}"])
        write_csv(f"{args.out}/clio-ar-aging-{snap.isoformat()}.csv",
                  ["Matter", "Originating attorney", "Responsible attorney", "Bill id", "Current", "1-30 days",
                   "31-60 days", "61-90 days", "91+ days", "Total"], rows)

    # 5. Matters report
    ar_now = defaultdict(float)
    for m, inv, b in ar_snapshot(matters, AS_OF):
        ar_now[m["num"]] += sum(b)
    rows = []
    for m in sorted(matters, key=lambda x: x["num"]):
        last = max([i["date"] for i in m["invoices"] if i["date"] <= AS_OF], default=None)
        rows.append([m["client"], m["name"], m["desc"], m["practice"], m["status"], m["attorney"], m["orig"],
                     "Yes", money(ar_now.get(m["num"], 0.0)), us(last) if last else ""])
    write_csv(f"{args.out}/clio-matters-report.csv",
              ["Client", "Matter", "Description", "Practice area", "Status", "Responsible attorney",
               "Originating attorney", "Billable", "Accounts receivable", "Latest bill"], rows)

    # 6. Matter list export (hand-built headers, US dates)
    rows = [[m["name"], m["client"], m["practice"], m["billing"], m["status"], us(m["open"]),
             us(m["close"]) if m["close"] else "", m["attorney"], ""] for m in sorted(matters, key=lambda x: x["num"])]
    write_csv(f"{args.out}/matter-list-export.csv",
              ["Matter", "Client", "Practice", "Billing", "Stage", "Opened", "Closed", "Lawyer in charge", "Notes"], rows)

    # 7. Revenue reports, last 90 days and the 90 before
    for label, a, b in (("last-90-days", AS_OF - timedelta(days=89), AS_OF),
                        ("prior-90-days", AS_OF - timedelta(days=179), AS_OF - timedelta(days=90))):
        agg = defaultdict(lambda: defaultdict(float))
        for e in entries:
            m, inv = e["matter"], e["inv"]
            k = m["num"]
            if inv["date"] <= AS_OF and a <= inv["date"] <= b:
                agg[k]["billed"] += e["billed"]
                agg[k]["billed_h"] += e["qty"] * e["factor"]
            if inv["date"] <= AS_OF and inv["pay"] is not None and a <= inv["pay"] <= b:
                agg[k]["collected"] += e["billed"]
            if inv["date"] > b and e["date"] <= b:
                agg[k]["unbilled"] += e["orig"]
                agg[k]["unbilled_h"] += e["qty"]
        for m, d, amt, kind in fees:
            if a <= d <= b:
                agg[m["num"]]["billed"] += amt
                agg[m["num"]]["collected"] += amt
        by_num = {m["num"]: m for m in matters}
        rows = []
        for k, v in sorted(agg.items()):
            m = by_num[k]
            total = v["collected"]
            rows.append([m["name"], "Downtown", money(v["unbilled"]), f"{v['unbilled_h']:.1f}", "0.00",
                         money(v["billed"]), f"{v['billed_h']:.1f}", "0.00", "0.00", "0.00", "0.00", "0.00", "0.00",
                         money(v["collected"]), "0.00", "0.00", "0.00", "0.00", money(total),
                         m["client"], m["practice"], m["desc"], m["attorney"], "0.00", "0.00"])
        write_csv(f"{args.out}/clio-revenue-report-{label}.csv",
                  ["Matter", "Location", "Unbilled time", "Unbilled hours", "Unbilled expense", "Billed time",
                   "Billed hours", "Billed expense", "Billed tax 1", "Billed tax 2", "Discounted time",
                   "Discounted expense", "Credit notes", "Collected time", "Collected expense", "Collected tax 1",
                   "Collected tax 2", "Collected uncategorized", "Client total", "Client", "Practice Area",
                   "Matter Description", "Responsible Attorney", "Billed Interest", "Collected Interest"], rows)

    # 8. Marketing spend (owner-built xlsx)
    spend_rows = []
    months = []
    y, mo = START.year, START.month
    while (y, mo) <= (2026, 9):
        months.append(date(y, mo, 1))
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1
    for md in months:
        for src, base in SPEND_BASE.items():
            v = base * rng.uniform(.95, 1.05)
            if PLANTS and src == "Google LSA" and md >= date(2026, 9, 1):
                v = 10400 * rng.uniform(.99, 1.01)
            spend_rows.append((md, src, round(v / 10) * 10))
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Spend"
        ws.append(["Month", "Source", "Spend"])
        for md, src, v in spend_rows:
            ws.append([md, src, v])
        for r in range(2, len(spend_rows) + 2):
            ws.cell(row=r, column=1).number_format = "mmm yyyy"
            ws.cell(row=r, column=3).number_format = '"$"#,##0'
        wb.save(f"{args.out}/marketing-spend.xlsx")
    except ImportError:
        write_csv(f"{args.out}/marketing-spend.csv", ["Month", "Source", "Spend"],
                  [[md.isoformat(), s, v] for md, s, v in spend_rows])
        print("openpyxl missing: wrote marketing-spend.csv instead of .xlsx")

    # summary stats for tuning (not shipped)
    stats = dict(leads=len(leads), matters=len(matters), entries=len(entries))
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
