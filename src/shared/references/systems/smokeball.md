# Smokeball

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Smokeball's Billing area has a list of reports, and they download as CSV. For a firm with no technical staff, that is the path: export two or three of them and hand them to Claude. We found no official connector. API access is by request: partners apply to the Partner Program, and firms ask their Smokeball account manager.

## Export the reports you need

1. Open the Reports page in Smokeball Billing.
2. Choose a report and download it as CSV. PDF is also offered, but use CSV.

Smokeball's help article says the reports are available on Smokeball Bill, Boost and the Grow and Prosper+ Cloud Companion App.

The report names below come from Smokeball's help center. What each contains is our reading of the name. We did not verify the columns, so check the preview first.

For "are we getting paid for the work we do," start with the Realization Report, and add the Aging Summary. By its name, the Aging Summary shows what is owed and how old it is. Unpaid Invoices and Unbilled & Unpaid Overview should help with the same question. Work in Progress Summary, Work in Progress Details and Historical WIP should show work that has not been billed yet. Billed Fees & Expenses and Invoice History should show what went out the door. Matter Balances should show what each matter owes.

For "what is stuck or slow," the Matter-Full List is the matter list. Whether it carries open and close dates, we could not confirm.

## What to tell Claude

> I use Smokeball. Here is my Realization Report as a CSV.

Smokeball has no preset. Claude reads the column headings, matches them by meaning to the fields it needs (worked, billed, collected, attorney, practice area) and shows you the match. Nothing is used until you confirm it.

## Connectors and MCP servers

Official: none found.

Community: RosenAdvertising/smokeball-mcp has 0 stars and was pushed 2026-10-02. It needs partner credentials, and our research does not treat the RosenAdvertising repos as credible. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier's Smokeball MCP has 16 triggers, 9 write actions and only 2 searches (Find Contact and Find Matter). Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. Partners apply to the Smokeball Partner Program. A firm requests API access through its Smokeball account manager. Either way, you then get the Developer Console (console.smokeball.com).

Do not paste credentials into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- The columns of any Smokeball report.
- Whether the Matter-Full List has open and close dates.
- Whether any user role limits who can see the Reports page.

## Sources

https://support.smokeball.com/hc/en-us/articles/5885848282135
https://docs.smokeball.com/docs/platform-docs/va20w41tid7py-get-started-overview
https://github.com/RosenAdvertising/smokeball-mcp
https://zapier.com/mcp/smokeball-1
