# Any other system

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

This repo has not researched your system, so there is no guide for it. That is fine. Most of the 17 systems in this folder can export a report or a list as CSV or Excel, so look for that first. Send the one or two reports your question needs, and Claude maps the columns by meaning and confirms the match with you.

Do not assume your system has a connector. We did not check. If a vendor offers an official one, its own website will say so.

## Find the export

Systems keep exports in a few usual places, and the 17 guides in this folder show the range. Look for a Reports menu with a download or export button on each report. Look for an Export, Download or spreadsheet icon on list screens such as matters, contacts or time entries. Look for an advanced search that can export its results. Look for an admin data export. Some systems can email you a report on a schedule.

If you cannot find it, search the vendor's help center for "export" and "reports," or ask their support: "Which reports can I export to CSV or Excel, and how?" Describe the report by what it should contain, such as one row per lead with the date, source and outcome, not by menu name alone. Menus move.

Two things can get in the way. Some systems need a permission before the export button appears, and Centerbase is one. Ask whoever manages user access at your firm. And at least one system we looked at, CASEpeer, charges for a full data export. If the vendor quotes a price, ask what report exports your plan already includes before you pay.

Choose CSV or Excel (.xlsx). If you only get an older .xls, open it and Save As .xlsx or CSV. If it is a Google Sheet, download it as .xlsx or CSV. PDF reports are hard to read reliably, so ask for the CSV or Excel version of the same report.

## What to ask the person for

Start from the question, then name the report.

| The question | What to export |
|---|---|
| Where is our marketing money working? | The lead report with source and outcome, plus a monthly spend sheet by source |
| Are leads getting answered fast enough? | A log of when each lead arrived and when someone first reached out |
| Are we getting paid for the work we do? | The time and billing report (realization), plus receivables aging |
| Which practice areas make money? | The revenue report by matter, for two comparable periods |
| What is stuck or slow? | The matter list with open and close dates |

Ask for the least. Counts and totals are enough for almost everything. Client names, notes and free-text fields are not needed for charts or a briefing. Prefer an export without them. If the file has them, Claude will say so and ignore those columns.

## What to tell Claude

> I use [your system]. Here is my [report name], exported as CSV.

Add the period it covers, such as "January to June," if the file does not say. Some files, like a receivables aging report or a revenue report, do not carry their own date or date range in the columns, and Claude will ask you.

## How Claude maps columns by meaning

Claude reads the file and finds the real header row. Exports often have a title line above it, blank lines, and a totals row at the bottom. Claude skips those and tells you what it skipped.

Then it matches each heading to a field it needs, by what the heading means. The table shows some of the headings it treats as a match. It is not a complete list.

| What Claude looks for | Headings it often matches |
|---|---|
| When a lead or matter was created | created at, date created, lead date, inquiry date, intake date, date received, date opened |
| Where a lead came from | source, lead source, referral source, marketing source, channel, how did you hear |
| What happened to the lead | status, stage, outcome, hired, retained, matter status |
| When that happened | status date, date hired, retained date, signed date, closed date |
| Practice area | practice area, practice, matter type, case type |
| Attorney | attorney, responsible attorney, lawyer, lawyer in charge, user, timekeeper |
| Matter | matter, matter id, matter number, case, case number, file number |
| Opened and closed dates | opened, open date, date opened, closed, close date, date closed |
| Billed and collected | billed, invoiced, collected, paid, payments |
| Money amounts | spend, cost, amount, ad spend, total, balance, outstanding |
| When a lead arrived | received at, inquiry time, lead time, call time |
| When someone first reached out | first contact, first response, contacted at, first reply |

If a heading does not match, or two could match, Claude asks you. It also asks what your outcome and status words mean when they are unusual, so it can sort them into signed, lost or open for leads, and open or closed for matters. Nothing is used until you confirm the match.

## When nothing fits

If your system has no export that fits, no connector, and no one on staff is technical, send whatever report you do have. Even a printout turned into a spreadsheet by hand for one month is useful. Claude will do what the data supports and say what the missing data would add. A small honest chart beats a large invented one.

## Connectors and MCP servers

Check the vendor's own site for an official connector, and check that your plan can use it. If you find a community-built server on GitHub or elsewhere, treat it with care. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Zapier's MCP tools create and look up single records. They do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path, and it is for someone technical. If your system has an API, the vendor's developer documentation says how to get credentials, and some need an approval step. Do not paste credentials, keys or tokens into a chat. Keep them in an environment variable or your system keychain. See build-an-mcp.md for the read-only approach.

## What we could not verify

- Anything about your specific system. We did not research it.
- Whether your system has an official connector, an API, or a report that fits.

## Sources

This guide draws on connect-your-data.md and on the column matching rules in scripts/schema.py. It has no vendor sources of its own.
