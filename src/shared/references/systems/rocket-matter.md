# Rocket Matter

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Rocket Matter is made by ProfitSolv. Use Advanced Search to export a list as CSV, and use the Reports menu for the Origination report. We found no official connector and no public API documentation.

## Export the reports you need

1. Click the gear icon in global search to open Advanced Search.
2. Choose what to search for: Clients, Contacts, Matters, Activities or Tags.
3. Run the search, then choose Export, which downloads a CSV.

To return all records, set a From and To date range and put * in the Client field. Rocket Matter's vendor article was last updated 2022-09-08, so confirm the steps in the product.

For "what is stuck or slow," export Matters and look for open and close dates and status. For "are we getting paid for the work we do," export Activities and look for hours, billed amounts and collected amounts. Rocket Matter's help page does not list the columns for any of these, so check what the file has.

Rocket Matter also has a Reports menu, and it includes an Origination report. Its columns are Originator, Client, Invoice, Invoice Amount, Payments, Paid to Fees and Paid to Costs. It is part of the Advanced Analytics Module, it needs an originator assigned to each client, and it exports to CSV with Export Report. It helps with the question of who brings in revenue. Our research found no other report names for Rocket Matter, so look through the Reports menu for a revenue or billing report and tell Claude what it contains.

Leave out notes and free-text fields. Claude does not need them.

## What to tell Claude

> I use Rocket Matter. Here is my Matters export from Advanced Search, as a CSV.

Rocket Matter has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match to confirm before it uses any of it.

## Connectors and MCP servers

Official: none found.

Community: RosenAdvertising/rocketmatter-mcp has 0 stars. It targets the ProfitSolv LCS API. All of the RosenAdvertising repos were pushed 2026-10-02, and our research does not treat them as credible. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier has an MCP page for Rocket Matter. It lists 9 triggers and 7 create actions. Zapier's tools work on single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. We found no public API documentation. The ProfitSolv Integration API appears to need a registered OAuth integration, and we could not confirm that.

## What we could not verify

- Whether Rocket Matter has a public API, and how a firm would get access to the ProfitSolv Integration API.
- The columns of any Advanced Search export.
- What other reports sit in the Reports menu.

## Sources

https://rocketmatter.screenstepslive.com/s/1166/m/54811/l/1368408-how-to-export-rocket-matter-data-like-clients-contacts-or-matters-with-advanced-search
https://rocketmatter.screenstepslive.com/s/1166/a/551128
https://github.com/RosenAdvertising/rocketmatter-mcp
https://zapier.com/mcp/rocket-matter
