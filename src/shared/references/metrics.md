# Law firm metrics

What each metric means, which way is good, and the window it should be read over. The engine in `scripts/compute_facts.py` implements these. When a firm's export does not support a metric, say what file would make it possible. Do not estimate into a gap.

Organized by what the firm sells, because the billing model decides which metrics matter: hourly firms live on realization and collections, flat fee firms on scope and cycle time, contingency firms on intake and case flow. Most firms mix. Read every section that applies.

## How to read any metric

**Windows.** A window is the stretch of time a number covers. Pick it so the sample stays honest.

| Window | Meaning | Use for |
|---|---|---|
| `t30` | Last 30 days against the 30 before | High-volume counts and rates: leads, calls |
| `t90` | Last 90 days against the 90 before | Lower-volume rates and medians |
| `t12m` | Last 12 months | Long cycles, where 30 days is noise |
| `month` | Last full calendar month against the one before | Anything driven by a monthly sheet, like marketing spend |
| `snapshot` | As of a day, against the previous snapshot | Open matters, receivables |

The engine tries `t30` first and moves to `t90` or `t12m` when there are too few cases. It never compares a partial period with a full one.

**Mature cohorts.** Some outcomes take time to show up. A lead from yesterday has not decided yet. Work that was done last week has not been billed. A bill sent last month has not been paid. So measure the rate on a cohort old enough to have finished: signed rate on leads from at least the usual decision time ago, realization on work old enough to have been invoiced, collection rate on work old enough to have been paid. The engine reads the lag from the data (for example, the 90th percentile of days from inquiry to decision) and states it in the footnote. [src: kabiri-aaw] on the lockup idea: the days between work and cash.

**Recompute from rows.** Year-to-date and multi-month rates are `sum(numerator) / sum(denominator)`, never an average of monthly percentages. Medians are never averaged. Totals are rebuilt from rows, not rolled up from per-person values.

**Normal variation.** Every comparison carries a test. Counts use a Poisson ratio, rates a two-proportion test, medians a rank test, dollar ratios a ratio estimator. A change is "clear" at p under .05, "likely" under .15, otherwise "normal range." People-level facts use a stricter bar because a false alarm about a person costs more. When one metric is checked across many groups, a few swings happen by chance, and the facts say so. [src: silver-snn] [src: wheelan-ns]

**Too thin.** Under 10 cases, a rate or median is too thin to call. Say it, with the count. Do not draw a bar or color it.

**People-level metrics** (anything split by attorney, intake rep, or timekeeper) are a reason to ask a question, not a verdict. Never rank people or write a sentence that pins a result on someone as a fault. "Realization on one attorney's matters fell from 87% to 53%. It is worth finding out what changed on those matters." [src: oneil-wmd]

---

## Leads and intake (every firm)

**New leads** `[src: clio-grow]`. Count of inquiries created in the window. Higher is better, but volume without conversion is a cost. Window `t30`. Poisson test.

**Lead source mix.** Each source's share of new leads. Neutral. Window `t90`.

**Signed rate.** Signed (hired, retained) leads divided by all leads in the cohort. Clio Grow defines conversion as hired matters divided by all matters added `[src: clio-grow]`. Higher is better. Window `t30` on a mature cohort. Trap: a lead from this week has not decided, so a "signed rate" on recent leads reads low. Trap: self-reported source ("how did you hear about us") can disagree with the tracked source, so treat a source mix built only from an intake question as lower confidence. [src: stephens-davidowitz-el] (the book's theme is that what people say can differ from what they do)

**Cost per lead.** Marketing spend for the month divided by leads created that month. Lower is better. Window `month`.

**Cost per signed matter.** Marketing spend for the month divided by matters signed that month, by sign date. Lower is better. Window `month`. At a few signed matters per month this swings a lot: report the count, and call a source with fewer than 10 signed matters too thin. A firm-wide blend can look flat while one source rises and another falls, so show it by source.

**Speed to lead.** Median minutes from a lead arriving to the first reach-out. Lower is better. Window `t30`. Read it by arrival time (weekday business hours, weekday after hours, weekend) because a change in when leads arrive can move the overall median without anyone getting slower. Leads from the last three days are left out, since many have not been contacted yet.

**Leads reached within an hour.** Share of leads whose first contact came within 60 minutes. Higher is better. Pair it with signed rate by response time to show whether speed matters at this firm.

**Leads never reached.** Share of leads with no first contact. Lower is better.

**After-hours share.** Share of leads arriving after hours or on weekends. Neutral. Use it to explain a change in speed or conversion, not to score anyone.

## Hourly billing (family, business litigation, most civil practices)

Clio's Legal Trends report publishes yearly benchmarks for utilization, realization and collection rates. [src: clio-legal-trends] Kabiri defines utilization as billable hours over available hours, realization as billed over worked, and collection as collected over billed. [src: kabiri-aaw] Firms measure these slightly differently, so say which definition you are using.

**Utilization.** Hours recorded divided by 8 hours on every weekday in the window. Higher is better, up to a point. The engine does not know about vacations or part-time schedules, so compare a firm with its own history first. Window `t90`. People-level.

**Realization.** Billed amount divided by original billable amount, on work old enough to have been invoiced. Higher is better. Window `t90` ending after the usual billing lag. A drop means more write-downs, discounts or unbilled time. The engine also reports which attorneys moved a practice area's realization and by how much.

**Collection rate.** Amount collected divided by amount billed, on work old enough to have been paid. Higher is better. Window `t90`, ending later than realization.

**Lockup.** Days between doing the work and having the cash: realization lag plus collection lag. Lower is better. It needs invoice dates, which some exports lack. [src: kabiri-aaw]

**Receivables over 90 days.** Dollars more than 90 days past due on the aging report, and their share of all receivables. Lower is better. Snapshot, compared with the previous snapshot. Read concentration: if one matter holds most of it, that is a collections conversation, not a firm-wide trend.

**Collected revenue.** Dollars collected in the period, by practice area. Higher is better for the firm, neutral by person. Contingency and flat fee revenue is lumpy: a few matters decide the total, so a swing may be timing. The facts flag this.

## Flat fee (estate planning, uncontested matters, many small firms)

**Revenue per matter.** Collected fees divided by matters closed in the window. Higher is better. Window `t12m`.

**Effective hourly rate.** Fee collected divided by hours recorded on the matter. Higher is better. Needs time entries on flat fee matters. It shows whether the fee covers the work. This metric is our own.

**Budget versus actual hours.** Hours recorded against the hours the fee assumed. Lower overrun is better. This is the legal project management habit of budgeting a matter and evaluating it at the end. Needs a budget. [src: lambreth-lpm]

**Matter cycle time.** Median days from open to close, for matters closed in the window. Lower is better, usually. Window `t12m`. Matters still open are not counted, so this reads shorter than the true average.

## Contingency (personal injury and similar)

**Fee per resolved matter.** Fees collected divided by matters resolved. Higher is better. Window `t12m`. Lumpy: report the median and the range, not just the mean.

**Case costs advanced.** Dollars the firm has fronted on open matters, and the share not yet recovered. Lower unrecovered is better. Needs an expense report.

**Case cycle time.** Median days from signing to resolution. Lower is better, with the caveat that a faster case is not always a better outcome. Window `t12m`.

**Intake to signed.** Same as signed rate, and the front of the funnel decides everything here, so speed to lead matters most.

## Firm-wide (every firm)

**Open matters per lawyer.** Open matters divided by lawyers who carry matters. Neutral. A lawyer far above or below the group is a staffing question. People-level.

**Revenue per lawyer.** Collected revenue divided by lawyers. Higher is better. Window `t12m`. Needs the lawyer headcount.

**Profit margin.** (Revenue minus direct costs) divided by revenue. Kabiri applies it per matter and records the final margin at close-out. Higher is better. Needs costs as well as revenue: Kabiri counts timekeeper labor at cost rate plus vendors and experts, so ask whether the firm's export has them. [src: kabiri-aaw]

---

## When the data is missing

Say what is missing and what file would fix it. Examples: "Cost per signed matter needs a marketing spend sheet by month and source." "Speed to lead needs a log of when each lead arrived and when someone first reached out." "Lockup needs invoice dates." Do not guess a number to fill the gap, and do not chart a metric the data cannot support.
