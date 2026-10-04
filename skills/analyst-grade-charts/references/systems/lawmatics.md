# Lawmatics

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Open a report from the Reports tab and export it as CSV. Large reports are emailed to you instead of downloading. We found no official connector. The API needs Lawmatics to switch on Developer Settings for you first.

## Export the reports you need

1. Open the Reports tab in the left navigation.
2. Open the report you want, using the eye icon.
3. Click the export button. The report downloads as a CSV.

The help article is about exporting custom reports, and it does not name specific reports or columns. So build or open a report that fits your question. For "where is our marketing money working," you want one row per lead with the date it came in, its source and its outcome. For "are leads getting answered fast enough," you want the arrival time and the time someone first reached out, if Lawmatics holds both. We could not confirm that it does.

Two details from Lawmatics' help article matter here. Groupings are not kept in the export, so the CSV is a flat list, and a report grouped by source will lose its groups. If you want a count by source, Claude can rebuild it from the rows, so ask for the flat list with a source column. And large reports are emailed to you rather than downloaded, so if nothing arrives on screen, check your inbox.

Lawmatics also has a bulk export under Settings, then Export. It exports all matters, contacts or companies with all fields.

Leave out notes and free-text fields. Claude does not need them.

## What to tell Claude

> I use Lawmatics. Here is my leads report from the Reports tab, exported as CSV.

Lawmatics has no preset. Claude reads the column headings, matches them by meaning to lead fields (date created, source, outcome, outcome date, practice area) and shows you the match. Nothing is used until you confirm it.

## Connectors and MCP servers

Official: none found.

Community: oktopeak/lawmatics-mcp has 0 stars and was last pushed 2026-09-09. It is listed in the official MCP Registry (checked 2026-10-03). dschnurbusch/lawmatics-mcp-server has 2 stars and was last pushed 2026-06-11. RosenAdvertising/lawmatics-mcp has 0 stars and is one of a group of RosenAdvertising repos, all pushed 2026-10-02 with 0 to 4 stars each. Our research does not treat the group as credible. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier has an MCP for Lawmatics with 8 triggers, 7 write actions and 5 search actions, and Pipedream has a Lawmatics app. Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. Lawmatics' API is REST with OAuth2 using the authorization code flow. You contact support@lawmatics.com or your Account Manager to have Developer Settings turned on. API questions go to api@lawmatics.com. Then you create an app at app.lawmatics.com/settings/developers.

Do not paste a client secret or any token into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- The names and columns of Lawmatics' standard reports.
- Whether Lawmatics holds the first-contact time of a lead.
- What the Pipedream app offers. We did not check its actions.

## Sources

https://help.lawmatics.com/en/articles/10699961-exporting-custom-reports
https://help.lawmatics.com/en/articles/10699766-exporting-data
https://help.lawmatics.com/en/articles/15939403-api-authentication-oauth2-setup-guide
https://github.com/oktopeak/lawmatics-mcp
https://zapier.com/mcp/lawmatics
https://pipedream.com/apps/lawmatics
