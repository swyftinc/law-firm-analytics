# SmartAdvocate

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

SmartAdvocate can email you a report on a schedule, and that is the export path we could verify. Case Browse is a wide report, so pick only the columns your question needs. We could not confirm which file formats the reports come in. We found no official connector and no community MCP server. What we know of SmartAdvocate's APIs is reported, not verified.

## Export the reports you need

SmartAdvocate calls this a report subscription. In the report, select the Schedule This Report button in the upper right corner. Choose how often it should run, which can be hourly, daily, weekly, monthly or a single delivery, and add the email recipients. SmartAdvocate then emails you the report. Confirm the steps in the product.

Case Browse is a wide report, so choose the columns that answer your question, such as dates, status, source and attorney, if Case Browse has them. Leave out client names, notes and free-text columns. Claude does not need them.

For "what is stuck or slow," you want case open and close dates and status. For "where is our marketing money working," you want the source of each case or lead, and the outcome. For "are we getting paid for the work we do," SmartAdvocate's reports may not cover it. We found no report names for billing, so ask SmartAdvocate support which report holds fees and collections.

The help article says nothing about file format. We could not confirm whether the emailed report arrives as Excel, CSV or PDF. If it arrives as PDF, ask support for a CSV or Excel version. PDF extraction is unreliable.

## What to tell Claude

> I use SmartAdvocate. Here is my Case Browse report, emailed to me on a schedule.

SmartAdvocate has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match to confirm before it uses any of it.

## Connectors and MCP servers

Official: none found.

Community: no community MCP server. A GitHub search for "smartadvocate" on 2026-10-03 shows three public repos, and none is an MCP server. The repos are TeejGuy99/casesync-openapi (an OpenAPI spec for a GPT connector, 0 stars, last pushed 2025-11-13), nabeelimtiaz667/smartadvocate-api (0 stars, last pushed 2025-10-08) and Zuldwyn00/Legal_Notebook (a knowledge-base assistant, 0 stars). We did not vet any of them. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: StackOne's page describes a production SmartAdvocate MCP server with 60 pre-built actions and managed auth. That is StackOne's claim, and we could not verify that it works. We found no Zapier app for SmartAdvocate. Zapier's tools create and look up single records and do not pull reports in bulk, so they would not fit this job anyway.

## API access

This is the advanced path, and what we know is reported, not verified. SmartAdvocate may have a Case Sync API. The unofficial OpenAPI spec above suggests it, but we could not read SmartAdvocate's own documentation for it. The one page we cited for it did not load for us without a login. So we do not know what the API covers, whether it is limited or gated, or how a firm gets access. Ask SmartAdvocate.

Do not paste credentials into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- The file formats of an emailed report, including whether Excel or CSV is offered.
- What SmartAdvocate's APIs cover and how a firm gets access, including the Case Sync API.
- Whether the StackOne connector page for SmartAdvocate works.
- Which SmartAdvocate report covers billing and collections.

## Sources

https://smartadvocate.atlassian.net/wiki/spaces/KB/pages/1850540033/How+Can+I+Create+a+Report+Subscription
https://smartadvocate.atlassian.net/wiki/x/BQCoYw
https://www.stackone.com/connectors/smartadvocate/mcp/
https://github.com/TeejGuy99/casesync-openapi
