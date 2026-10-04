# Needles and Neos

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

Needles and Neos are both made by Assembly. This guide covers both. The research is stronger for Neos, and it is thin for desktop Needles.

## The short version

If you use Neos, export from Advanced Search as CSV or Excel. A Neos report may export too, but we could not confirm it. If you use desktop Needles, we could not confirm what your export options are, so ask Assembly support which reports export to CSV or Excel. We found no official connector. API access appears to be gated, but that rests on one third-party source only.

## Export the reports you need

Assembly's May 2026 Neos release notes say Advanced Search exports to Excel, CSV and PDF. Assembly's Neos analytics page may say the same, but its text did not show an export mention when we fetched it, so we do not rely on it. We did not capture the click path or the names of the reports. So the steps are short.

1. Run the Neos report you want, or run an Advanced Search.
2. Choose the export option and pick CSV or Excel. PDF is there too, but Claude reads CSV and Excel more reliably.

For "what is stuck or slow," look for a case list with open and close dates and status. For "are we getting paid for the work we do," look for time, billing and receivables. For "where is our marketing money working," look for an intake or lead list with source and outcome. Leave out notes and free-text fields. Claude does not need them.

For desktop Needles, we found nothing that confirms the export options. If you can already produce a report on screen, even a printout you can turn into a spreadsheet for one month, send that. A small, honest chart from one month of real data is better than a large chart built on guesses.

## What to tell Claude

> I use Neos. Here is my case list from Advanced Search, exported as CSV.

or

> I use Needles. Here is the report I can export. I am not sure about the format.

Neither system has a preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match to confirm before it uses any of it.

## Connectors and MCP servers

Official: none found.

Community: none were found on 2026-10-03.

Third party: Zapier's Neos MCP (Neos only) has File Upload, Create Intake, Create New Case and Post Note, plus Find Case or Intake by First Party and Find Case or Intake by Number. Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. We found no public documentation. One third-party source says API access is gated. We could not confirm that, and we do not know how a firm would request it.

## What we could not verify

- The export options in desktop Needles.
- Whether Neos reports, and not only Advanced Search, export. The Assembly analytics page may say so, and we could not confirm it. Check in a browser.
- The names and columns of Neos reports, and the exact click path to export.
- Whether Assembly offers API access, and on what terms. The only source is a third-party report.
- Whether Zapier supports desktop Needles. The Zapier page we found covers Neos only.

## Sources

https://www.assemblysoftware.com/post/whats-new-in-neos-may-2026
https://www.assemblysoftware.com/neos-analytics
https://supergood.ai/api-report-card/needles-neos
https://zapier.com/mcp/neos
