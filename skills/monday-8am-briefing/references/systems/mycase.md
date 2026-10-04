# MyCase

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

For most firms the path today is a report export from the Reports tab. The Case List Report gives you your matter list, and the Financial Reports give you revenue. MyCase's maker, 8am, announced an official connector in September 2026, and it is live now as a beta. Read tools work for every connected firm. Write tools are in a limited beta. If you have no technical staff, export a report and hand it to Claude.

## Export the reports you need

The report names below are confirmed. What each one contains is partly our reading of the name, so look at the report before you export it.

1. Open Reports in the left navigation.
2. Under Case & Contact Reports, open the Case List Report.
3. Use Customize Columns if you want to trim the file, then export as CSV.

The Case List Report is your matter list. It exports as CSV or PDF, so choose CSV. It can answer "what is stuck or slow," if the columns you pick include status and dates.

The Financial Reports include Case Revenue, Fee Allocation and Transaction Report. Case Revenue and Fee Allocation export as PDF or CSV, so choose CSV. We did not confirm the export format of the Transaction Report. MyCase's help article says Case Revenue shows billed and collected amounts, and you can filter it by date range and case status. The article does not mention practice area, so check for it before you use this report for "which practice areas make money." MyCase's help article says Fee Allocation shows what has been billed and collected by specific users. By its name, the Transaction Report lists the money movements. For "are we getting paid for the work we do," start with Case Revenue and tell Claude what columns it has.

## What to tell Claude

> I use MyCase. Here is my Case Revenue report as a CSV.

MyCase has no preset, so Claude reads the column headings, matches them by meaning to the fields it needs (matter, practice area, attorney, billed, collected) and shows you the match. Nothing is used until you confirm it.

## Connectors and MCP servers

Official: MyCase runs an MCP server at https://mcp.mycase.com/mcp, with documentation at https://mcp.mycase.com/docs. It was announced on 2026-09-23. The docs call it a beta service, and it is live now. You add it in Claude as a custom connector and sign in with OAuth as your own MyCase user. MyCase's support article also says to find MyCase in the Claude Marketplace. Read tools work for every connected firm. Write tools are off by default and appear in Claude only for firms enrolled in a write beta, which you request through MyCase support (support@mycase.com). The vendor's tool catalog says a Claude Team or Enterprise plan is required. The mid-October beta and December general availability dates in press coverage belong to a different 8am product, 8am IQ Firm Agent, not to this connector.

Sources disagree on whether your MyCase tier limits what data it can reach. LawNext says customers may be restricted by their MyCase subscription tier. MyCase's own support article says it is included at no extra cost on all MyCase plans. Ask MyCase support whether it is turned on for your account.

Community: oktopeak/mycase-mcp has 5 stars and was last pushed 2026-10-02. RosenAdvertising/mycase-mcp has 1 star and was pushed 2026-10-02. It is one of 16 public RosenAdvertising repos, all pushed 2026-10-02 with 0 to 4 stars each, and we do not treat the group as credible. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier's MyCase MCP has 5 triggers, 19 write actions and 10 searches. Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. MyCase's Open API is available on the Advanced tier only. You contact MyCase support to get OAuth client credentials.

Do not paste credentials into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- Which MyCase tiers can reach which data through the MCP server. LawNext and MyCase's support article disagree.
- The tool count. LawNext's announcement coverage said 73 actions and the docs list 128 tools. MyCase's support article says 73 read-only actions and that it cannot create, edit or delete anything, which conflicts with the docs' beta write tools. We did not reconcile them.
- The columns of the Case List Report, the Fee Allocation report and the Transaction Report, and the export format of the Transaction Report.

## Sources

https://supportcenter.mycase.com/en/articles/9370107-case-list-report
https://supportcenter.mycase.com/en/articles/9370110-case-revenue-report
https://supportcenter.mycase.com/en/articles/9370112-fee-allocation-report
https://supportcenter.mycase.com/en/articles/9370105-8am-mycase-reports-overview
https://supportcenter.mycase.com/en/articles/9370198-open-api
https://supportcenter.mycase.com/en/articles/16237229-mycase-mcp
https://mcp.mycase.com/docs
https://www.lawnext.com/2026/09/at-its-user-conference-in-las-vegas-8am-announces-mcp-integration-and-new-ai-tools-for-mycase-plus-new-law-firm-funding-program-through-lawpay.html
https://github.com/oktopeak/mycase-mcp
https://zapier.com/mcp/mycase
