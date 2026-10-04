# PracticePanther

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Export a report from the Reports menu to Excel and give the file to Claude. We found no official connector. The API needs a request to PracticePanther, so it is not a path for a firm without technical staff. Our research confirmed the export path but not the individual report names or their columns, so this guide is thinner than most.

## Export the reports you need

1. Open More, then Reports.
2. Pick the report that matches your question.
3. At the top right, choose Export to Excel. Export to PDF is there too, but use Excel.

PracticePanther's help article confirms this path. It does not list the individual reports or their columns, and neither did our research. So choose by what the report contains, not by name. For "are we getting paid for the work we do," look for a time and billing report and a receivables aging report. For "which practice areas make money," look for a revenue report by matter. For "what is stuck or slow," look for a matter list with open and close dates.

If the file comes out as an old .xls, open it and Save As .xlsx or CSV. If no report has what your question needs, say so. Claude will tell you what is missing instead of guessing.

## What to tell Claude

> I use PracticePanther. Here is my [name of the report], exported to Excel.

PracticePanther has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match to confirm before it uses any of it.

## Connectors and MCP servers

Official: none found.

Community: sanjibani/practicepanther-mcp has 1 star and was last pushed 2026-09-18. RosenAdvertising/practicepanther-mcp has 0 stars and was pushed 2026-10-02. Its README says it was "tested with mocked API responses... not verified against a live account." Our research does not treat the RosenAdvertising repos as credible. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier has an MCP page for PracticePanther (it loads, but we did not check its actions). Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. PracticePanther's API is REST with OAuth 2 and OData. You submit a request for API access to get a client ID. The redirect URI has to be registered with PracticePanther's dev team. The API reference is at the link below, and it links to a Swagger UI.

Do not paste credentials into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- The names and columns of PracticePanther's individual reports.
- Whether the Excel export is .xlsx or an older format.
- What actions the Zapier MCP page offers. We confirmed only that the page loads.

## Sources

https://support.practicepanther.com/en/articles/479891-how-do-i-export-my-practicepanther-reports-into-excel-or-pdf
https://support.practicepanther.com/en/articles/479897-practicepanther-api
https://app.practicepanther.com/content/apidocs/index.html
https://github.com/RosenAdvertising/practicepanther-mcp
https://zapier.com/mcp/practicepanther-legal-software
