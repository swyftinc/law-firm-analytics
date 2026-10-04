# CARET Legal

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

CARET Legal was formerly Zola Suite. Zola Suite was rebranded as CARET Legal, so they are the same product. If someone says they use Zola Suite, this is the guide.

## The short version

Use the Download Spreadsheet option in the actions menu, or the export icons on the Accounting Reports tab, to get an Excel file. CSV is also offered. We found no connector. CARET's API is being opened in phases, and billing may not be covered yet.

## Export the reports you need

1. Open the screen with the list you want.
2. Open the actions menu at the right end of the tab bar.
3. Choose Download Spreadsheet, which gives you Excel. You can also choose Export to CSV. PDF and Print are also there, but use the spreadsheet or the CSV.

For financial reports, go to Accounting, then the Reports tab. It has the same export icons.

CARET's help article describes these export paths. We read it from a search extract, because CARET's help center blocked our automated checks, so confirm the steps in the product. The export article does not list the reports or their columns. CARET's separate article, "What Reports does CARET Legal Offer?", lists report names in six categories: Client, Compensation, Productivity, Accounting, Trust and Vendor. Named reports include AR Aging Summary, Statement of Account, Client Payments, Fee Allocation, Originating Attorney, WIP/AR/Trust and Billed & Collected. We did not capture the columns. So pick the screen by what it holds. For "are we getting paid for the work we do," use the Accounting Reports tab and look for reports such as AR Aging Summary, Billed & Collected and Timekeeper Productivity. For "what is stuck or slow," export your matter list and look for open and close dates and status. For "which practice areas make money," look for revenue by matter. Leave out notes and free-text fields. Claude does not need them.

If a report you need is not there, say so. Claude will tell you what is missing instead of guessing.

## What to tell Claude

> I use CARET Legal, which used to be Zola Suite. Here is my matter list, downloaded as a spreadsheet.

CARET has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match. Nothing is used until you confirm it.

## Connectors and MCP servers

Official: none found. We also found no Zapier app.

Community: none were found on 2026-10-03.

## API access

This is the advanced path. CARET is opening its API in phases. Phase 1 covers matters, contacts, notes and custom fields. Access is through a request form on CARET's site. CARET's page says only Phase 1 is released and gives no detail on later phases. A third-party report says billing and trust accounting are not covered. We could not confirm that.

Do not paste credentials into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- Whether CARET's API covers billing and trust. The only source is a third-party report.
- The columns of CARET's reports. We have report names from CARET's help center, not the columns.
- Which screens have the Download Spreadsheet option. We read about the menu in a search extract of CARET's help article, and we did not confirm every screen it appears on.
- Whether CARET offers an official connector. We found none.

## Sources

https://support.caretlegal.com/hc/en-us/articles/17775816334484-How-do-I-Print-or-Export-in-CARET-Legal
https://support.caretlegal.com/hc/en-us/articles/17775724736276-What-Reports-does-CARET-Legal-Offer
https://caretlegal.com/?p=37300
https://supergood.ai/api-report-card/caret
https://www.globenewswire.com/news-release/2023/02/21/2612226/0/en/AbacusNext-Rebrands-as-CARET-to-Unify-Technology-and-Automation-Solutions-for-Legal-and-Accounting-Professionals.html
