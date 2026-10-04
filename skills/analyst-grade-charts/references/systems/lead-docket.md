# Lead Docket

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Lead Docket is made by Filevine, which acquired it in 2020. Run a report in Lead Docket and download it as CSV or Excel. Lead Docket has a self-serve API key, but a report download is simpler and is the path to start with. We found no official connector.

## Export the reports you need

1. Open Reporting, then Reports, and run the report you want.
2. Choose Download, then .csv or Excel.

Lead Docket's help center documents a Leads Report and a general page on running reports. For "where is our marketing money working," you want one row per lead with the date it came in, its source and its outcome. For "are leads getting answered fast enough," you need when each lead arrived and when someone first reached out. By default the Leads Report has Lead ID, First Name, Last Name and Created Date, and you add other fields yourself. We did not confirm that source, outcome or first-contact fields are among the ones you can add, so check, and tell Claude if the report does not have them. Claude will say what is missing instead of guessing. Cost per lead also needs a monthly marketing spend sheet by source, and Claude will ask you for it.

You can also save a report, schedule it by email, and have it sent to AWS or Azure. A person without technical staff does not need that. A manual download is enough.

## What to tell Claude

> I use Lead Docket. Here is my Leads Report as a CSV.

Lead Docket has no preset. Claude reads the column headings, matches them by meaning to lead fields (date created, source, outcome, outcome date, practice area) and shows you the match. Nothing is used until you confirm it.

## Connectors and MCP servers

Official: none found.

Community: the Advocate-Cloud-Solutions Filevine MCP server (0 stars, last pushed 2026-05-11) says it covers Lead Docket intake. Its README calls it "pre-alpha." Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: we found no Zapier app for Lead Docket. The Zapier page at zapier.com/apps/lead-docket returns 404. Zapier works with Lead Docket through webhooks instead, and Lead Docket's own help center has an article on setting up a Zapier webhook. Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. Lead Docket has a self-serve API key. Go to Manage, then Settings, then the bottom of Account Settings. The API console is at `https://{hostname}.leaddocket.com/api/`, where the hostname is your firm's own. The help article for this was last updated on 2022-01-07, so confirm the menu path in the product.

Do not paste the key into a chat. Keep it in an environment variable or your system keychain.

## What we could not verify

- Whether the Leads Report, or any other Lead Docket report, has source, outcome and first-contact fields.
- Who in a firm can see the API key setting. We did not confirm the permission needed.
- Whether Lead Docket reports carry first-contact times. We did not confirm it.

## Sources

https://support.leaddocket.com/hc/en-us/articles/40003522542875-Run-Reports
https://support.leaddocket.com/hc/en-us/articles/38843107195675-Leads-Report
https://support.leaddocket.com/hc/en-us/articles/4414934625563
https://support.leaddocket.com/hc/en-us/articles/360045258952-Setting-Up-a-Zapier-Webhook-Example
https://www.lawnext.com/2020/04/case-management-company-filevine-acquires-lead-management-company-lead-docket.html
