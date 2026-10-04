# Actionstep

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Use the Data Export Report under Matter Reports. It gives you one CSV file for each data source. Actionstep runs an official MCP server, in beta. Its docs say to contact your Customer Service Manager to join. Its listed tools cover documents, tasks, file notes, matters and contacts, not reports or billing. For a firm with no technical staff, export the CSV files.

## Export the reports you need

1. Open Reports.
2. Open Matter Reports.
3. Choose Export, then Data Export Report.

The report gives you one CSV for each data source. Actionstep's help page describes this path. We read it from a search extract, because the page blocked our automated checks, so confirm it in the product. The page lists the sources: Action (Matter), Action participant, specific participant types, specific matter-type data collections and Tasks.

You may end up with several files. Do not send all of them. Ask Claude which ones the question needs, and send only those. For "what is stuck or slow," you want the Action (Matter) file. It has matter status and date created, with the matter name, matter type, assigned person and current step. It has no billing columns. For "are we getting paid for the work we do," you need time and billing files. We could not confirm which source holds them, so check what your export produces. Leave out notes and free-text files. Claude does not need them.

If one file is not enough on its own, Claude will tell you which other file would fill the gap and why.

## What to tell Claude

> I use Actionstep. Here is the matter CSV from my Data Export Report.

Actionstep has no preset. Claude reads the column headings of each file, matches them by meaning to the fields it needs and shows you the match to confirm before it uses any of it.

## Connectors and MCP servers

Official: yes, in beta. Actionstep's own API docs have an MCP Server page at https://docs.actionstep.com/mcp-server/. It says the server connects your Actionstep practice management data to AI assistants like Claude, and that it is currently in beta. To take part in the beta, you contact your Customer Service Manager. The server uses OAuth 2.0 with your Actionstep sign-in. It lists 40+ tools for documents, folders, custom fields, tasks, file notes, matter and contact lookup, contacts, participant and contact types, and users. Reports, Data Export Reports, time entries and billing are not in that list. Release notes at https://docs.actionstep.com/mcp-server-release-notes/ show versions up to 1.18.2 on 2026-09-28.

The docs do not state the server's address. We matched `https://mcp.actionstep.com/mcp` by its domain and what it does. We checked it on 2026-10-03 without credentials. It returns a 401 response, and its OAuth metadata names its own domain as the authorization server.

Community: RosenAdvertising/actionstep-mcp has 1 star. All of the RosenAdvertising repos were pushed 2026-10-02, and our research does not treat them as credible. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier has an MCP for Actionstep. Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job. Actionstep also documents its own Zapier app, with 7 triggers and 18 actions, including Create Time Entry and Create Disbursement (https://docs.actionstep.com/zapier/).

## API access

This is the advanced path. Actionstep's API is REST with OAuth2. You request access from Global Support and describe your project. You then get a sandbox plus credentials. There is a $500 set-up fee, per Actionstep's Getting Started page. Actionstep's separate API credentials page does not mention the fee, so confirm it when you ask.

Do not paste credentials into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- Which plans can join the MCP beta, and whether mcp.actionstep.com/mcp is its endpoint. The docs do not name the URL.
- The full column list of every data source in the Data Export Report, and where the time and billing files come from. We read the source list from a search extract of a page that blocked automated checks.
- What the Zapier MCP offers. We did not check its actions.

## Sources

https://docs.actionstep.com/mcp-server/
https://docs.actionstep.com/mcp-server-release-notes/
https://support.actionstep.com/hc/en-us/articles/50482557645075-Data-Export-Report
https://docs.actionstep.com/getting-started/
https://docs.actionstep.com/authentication/
https://docs.actionstep.com/zapier/
https://mcp.actionstep.com/mcp
https://github.com/RosenAdvertising/actionstep-mcp
https://zapier.com/mcp/actionstep
