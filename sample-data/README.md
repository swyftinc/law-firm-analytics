# Sample data: Super Duper Law

Super Duper Law is a fictional law firm with about 12 lawyers. Everything here is synthetic. No file comes from a real firm, and every name, email and amount is made up. The files are shaped like what a firm would export from Clio and from its own spreadsheets, so the skills can show what they do before you bring your own numbers.

The firm has four practice areas and three billing models: family law and business litigation bill hourly, estate planning charges flat fees, and personal injury works on contingency. The data runs from April 2025 to October 4, 2026.

Both skills carry a copy of these files in `assets/sample-data/`. Ask either skill to "show me what this does with the sample firm."

## The files

| File | Shaped like | What it holds |
|---|---|---|
| `clio-grow-matter-revenue-report.csv` | Clio Grow, Matter revenue report | One row per lead: source, matter type, status, dates, estimated value. About 3,000 rows. |
| `intake-call-log.csv` | A log an intake team keeps by hand | When each lead arrived and when someone first reached out. Matches the lead file on email. |
| `marketing-spend.xlsx` | A spreadsheet the owner keeps | Spend by month and source (Google LSA, Google Ads, Facebook, Avvo). |
| `clio-realization-report.csv` | Clio Manage, Realization report | One row per time entry on hourly matters: what was worked, billed and collected. |
| `clio-ar-aging-2026-09-06.csv`, `clio-ar-aging-2026-10-04.csv` | Clio Manage, Accounts receivable aging report | One row per unpaid bill, aged in buckets, with a totals row at the bottom. Two snapshots a month apart. |
| `clio-matters-report.csv` | Clio Manage, Matters report | One row per matter: practice area, status, attorney, receivables. |
| `matter-list-export.csv` | A matter list exported with its own column names | Open and close dates and billing method per matter. Clio does not publish the columns of its matter list export, so this file uses ordinary names and the skill maps them by meaning. |
| `clio-revenue-report-last-90-days.csv`, `clio-revenue-report-prior-90-days.csv` | Clio Manage, Revenue report (CSV) | Collected revenue by matter for two comparable 90 day periods. |
| `mapping.json` | The skills' own file | Which column means what, for each file above. |

The column names in the Clio-shaped files are the ones Clio documents in its help center (checked 2026-10-03). The values inside them, such as status names, are invented. If a Clio export differs from these, the skills read the file by meaning, not by position.

## What is planted

So you can see the skills find real stories, the data has a few built in. The eval suite checks that each one is found and that nothing else is invented.

1. **Google LSA cost per signed matter nearly doubled in September** on flat lead volume. The cause built in: more LSA leads arrive after hours and on weekends, and those wait longer for a first contact.
2. **Family law realization fell**, mostly on one attorney's matters, starting in June.
3. **Receivables over 90 days grew** between the two aging reports, and one business litigation matter holds most of them.
4. **Median speed to lead** is far slower on weekends and after hours than during business hours.
5. **A thin result:** a new referral source has four leads that have reached a decision, and all four signed. Four is too few to call.
6. **A non-event:** total new leads are up a few percent, inside normal variation.

## Rebuilding the data

`python3 tools/generate_sample_data.py` writes these files from a fixed random seed, so the same command makes the same files. `--no-plants` makes a quiet firm where none of the stories above happen, which the evals use to check that a briefing does not invent a crisis. `evals/ground_truth.py` recomputes the planted numbers straight from the files, without any of the skills' code, as an answer key.
