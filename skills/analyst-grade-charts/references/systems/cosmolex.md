# CosmoLex

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

CosmoLex is made by ProfitSolv. For a firm without technical staff, the path is the Export icon that appears on most list screens. It gives you Excel, PDF or CSV. We found no official connector, and API access is unclear. Our sources disagree on whether a public API exists.

## Export the reports you need

1. Open the screen with the list you want. CosmoLex shows an Export icon on Matters, Activities, Accounting, Contacts and other screens.
2. Click the Export icon.
3. Choose Excel or CSV. PDF is there too, but Claude reads Excel and CSV more reliably.
4. Export the current page, or enter a custom page range.

Because the export covers the current page or a page range, a long list may come out in pieces. Set the page range wide enough to cover everything, or export each page and tell Claude they are parts of one list.

CosmoLex's help page does not name specific reports or columns, and neither did our research. Choose the screen by what it holds. For "are we getting paid for the work we do," try Activities and Accounting, and look for hours, billed amounts and collected amounts. For "what is stuck or slow," try Matters, and look for open and close dates. For "which practice areas make money," try Matters or Accounting, and look for practice area and amounts. Leave out notes and free-text fields.

## What to tell Claude

> I use CosmoLex. Here is my Matters list, exported as CSV.

CosmoLex has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match. Nothing is used until you confirm it.

## Connectors and MCP servers

Official: none found.

Community: RosenAdvertising/cosmolex-mcp has 0 stars. It targets the "ProfitSolv LCS Integration API" with OAuth plus an API key. All of the RosenAdvertising repos were pushed 2026-10-02, and our research does not treat them as credible. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier has an MCP page for CosmoLex. It lists 9 triggers and 7 create actions, and no lookup actions. Zapier's tools work on single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path, and it is unclear. One third party says CosmoLex has no public REST API. The community repo above uses a gated ProfitSolv Integration API instead. We could not settle which is right. Treat API access as unverified and gated.

## What we could not verify

- Whether CosmoLex has a public API, and how a firm would get access to the ProfitSolv Integration API.
- The columns of any CosmoLex export.
- Which screens hold open and close dates, practice area, and billed and collected amounts.

## Sources

https://support.cosmolex.com/knowledge-base/export-your-data/
https://supergood.ai/api-report-card/cosmolex
https://github.com/RosenAdvertising/cosmolex-mcp
https://zapier.com/mcp/cosmolex
