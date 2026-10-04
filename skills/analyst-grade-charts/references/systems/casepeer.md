# CASEpeer

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

The only data export we could verify is paid. CASEpeer, which is made by 8am, sells full data exports by email request. Documents can be downloaded case by case for free. CASEpeer Advanced also has API access, which needs a developer. If CASEpeer lets you export a report from inside the product, start there. We could not confirm that it does. Ask CASEpeer support what report exports your plan includes before you pay for anything.

## Export the reports you need

CASEpeer's help center says full data exports are paid. A CSV export costs $1,000, and a complete export costs $2,500. You request either one by emailing support. CASEpeer describes the CSV export as meant for data engineers. It is delivered at least one business day after the invoice is paid, and it is emailed as a zip link to the firm admin or a user with the data export permission. The complete export includes documents, takes 4 to 6 weeks, and does not keep folders. The help article is dated 2026-03-02, so confirm the prices with CASEpeer before you commit.

Documents, but not data, can also be downloaded case by case for free.

We did not find a verified way to export a report from inside the product. That does not mean there is none. It means we could not confirm one, and we have no menu path to give you. This is a general check, not a CASEpeer instruction:

1. Open the report or list screen in CASEpeer that has what you want.
2. Look for an export, download or print option on that screen.
3. If there is one, choose a spreadsheet or CSV format, not PDF.

If there is no option, ask CASEpeer support which reports can be exported on your plan. If the answer is none, send Claude whatever you can produce, even a printout that you retype into a spreadsheet for one month. Claude will tell you what the data supports and what a fuller export would add.

If you do pay for an export, Claude needs only a few columns, such as dates, source, status and attorney. If the file has notes or other free-text columns, tell Claude and it will ignore them.

## What to tell Claude

> I use CASEpeer. Here is the export I was able to get. It covers [period].

CASEpeer has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match to confirm before it uses any of it.

## Connectors and MCP servers

Official: none found.

Community: none were found on 2026-10-03.

Third party: Zapier's CASEpeer MCP has write actions for Create Case, Create Case Note, Create Case Task and Create Lead, search actions for Case Search, Caseworker Search and Case Type Search, and 4 triggers. Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. CASEpeer's help center, in an article published 2026-04-01, says CASEpeer Advanced offers two APIs. The Data Sync API gives read-only access to your firm's data, for dashboards in tools such as Tableau or Microsoft Power BI. You get an API key at Account Settings, then Additional Features, then Data Sync, and enter it in your BI tool. The Partner API can read and write, but its current endpoints are limited. You request access by email with an application name, a redirect URL and a logo. CASEpeer does not provide direct support for API implementations, so a firm needs a developer. CASEpeer's tiers page lists API access in the Advanced tier. CASEpeer also offers Zapier.

Do not paste an API key into a chat. Keep it in an environment variable or your system keychain.

## What we could not verify

- Whether CASEpeer has an in-app report export, and which reports have it.
- Whether the $1,000 and $2,500 export prices are still current, and what each export contains.
- What the Data Sync API costs. The tiers page lists API access in the Advanced tier at $160 per month and does not say per what.
- What the Data Sync API delivers beyond "read-only access to your firm's data," and how often it refreshes.

## Sources

https://supportcenter.casepeer.com/en/articles/9343458-what-exports-can-8am-casepeer-provide
https://supportcenter.casepeer.com/en/articles/9343509-does-casepeer-have-an-open-api
https://supportcenter.casepeer.com/en/articles/9343553-activate-data-sync-integration-functionality-for-reporting
https://supportcenter.casepeer.com/en/articles/9343450-casepeer-tiers
https://supportcenter.casepeer.com/en/articles/9343493-8am-casepeer-additional-features-integrations-overview
https://zapier.com/mcp/casepeer
