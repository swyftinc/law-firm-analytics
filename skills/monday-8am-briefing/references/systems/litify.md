# Litify

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Our research found that Litify's data is reached through Salesforce: the API is the Salesforce platform APIs, and exports are standard Salesforce reports. So the path for a firm without technical staff is a Salesforce report export. We found no Litify-branded connector. Salesforce offers hosted MCP servers that Claude can connect to, but a firm admin has to set one up, and we could not confirm that it works with Litify's own objects. We also found no Litify-specific export guide, so treat the steps below as the general Salesforce path.

## Export the reports you need

1. Open Reports in Salesforce and open the report that matches your question.
2. Choose Export.
3. Pick "Formatted" or "Details Only," as xlsx or csv.

We did not check these steps against a Salesforce Help page, and we found no Litify-specific documentation on this. So we could not confirm the option names, the file formats or what each option includes. Check the file. You want one header row and one row per record. Claude will tell you if the file is laid out like a printed report and ask for a different export.

Which report depends on your question. For "what is stuck or slow," ask for a matter list with open and close dates and status. For "are we getting paid for the work we do," ask for time and billing, and receivables. For "where is our marketing money working," ask for leads with source and outcome. Leave out notes and free-text fields. Claude does not need them.

## What to tell Claude

> I use Litify. Here is a Salesforce report of my matters, exported as CSV.

Litify has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match to confirm. Litify uses custom objects, so expect Claude to ask what a few column headings mean.

## Connectors and MCP servers

Official: Litify has no connector of its own. Salesforce offers Hosted MCP Servers. Salesforce's developer blog, published 2026-05-26, says they are now generally available. One example is the sobject-all server, and the blog suggests naming the connector `salesforce-sobject-all`. That server can also create, update and delete records, so your admin should scope its access. Hosted MCP servers use OAuth with PKCE through an External Client App that a firm admin sets up. A third-party blog says this works with Litify's custom objects. The same blog says it takes a Salesforce admin and a paid Claude plan, and that whether a given Litify object is reachable depends on your org's configuration and the permissions of the user running it. We could not confirm any of that with Salesforce or Litify.

Community: none were found on 2026-10-03.

Third party: our research did not check Zapier or Pipedream for Litify.

## API access

This is the advanced path. Litify data is reached through the Salesforce platform APIs. A firm admin has to set up an External Client App in Salesforce Setup, which needs admin access.

Do not paste credentials or tokens into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- Whether Salesforce's hosted MCP servers work with Litify's custom objects. The only source is a third-party blog.
- The Salesforce report export steps above, including the Formatted and Details Only options and the xlsx and csv formats. We cited no Salesforce Help page for them.
- Any Litify-specific export documentation, and the difference between the Formatted and Details Only options for a Litify report.
- Which reports and fields your Litify holds. We have not seen your account.

## Sources

https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/claude.html
https://developer.salesforce.com/blogs/2026/05/connect-claude-with-salesforce-hosted-mcp-servers
https://www.usecarly.com/blog/claude-litify-integration/
