# Systems index

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

One short guide per practice management system. Each guide says how to export the reports a question needs, what to tell Claude, what connectors exist, and what we could not verify. If your system is not listed, read [generic.md](generic.md). For the order of paths to try, the file formats, and the vetting checklist for community-built servers, read [../connect-your-data.md](../connect-your-data.md).

For a firm with no technical staff, the usual path today is the export, as the table shows.

| System | Best path today | Official connector? | Date checked |
|---|---|---|---|
| [Clio](clio.md) (Manage and Grow) | Export Classic reports as CSV. Six reports are recognized automatically. | No | 2026-10-03 |
| [MyCase](mycase.md) | Export the Case List Report and the Financial Reports as CSV. The official connector is in beta. | Yes, in beta | 2026-10-03 |
| [PracticePanther](practicepanther.md) | Reports, then Export to Excel. | No | 2026-10-03 |
| [Smokeball](smokeball.md) | Download billing reports as CSV. | No | 2026-10-03 |
| [Filevine](filevine.md) | Build a report in Report Builder and export it to Excel. A CSV Report option exists, but your Filevine rep must enable it and it can take up to 24 hours. | No | 2026-10-03 |
| [Lead Docket](lead-docket.md) | Run a report and download it as CSV or Excel. | No | 2026-10-03 |
| [Litify](litify.md) | Export a Salesforce report. A Salesforce admin can set up Salesforce's hosted MCP server. | No, not from Litify | 2026-10-03 |
| [CosmoLex](cosmolex.md) | Use the Export icon on list screens. | No | 2026-10-03 |
| [Rocket Matter](rocket-matter.md) | Advanced Search, then Export, which downloads a CSV. | No | 2026-10-03 |
| [Lawmatics](lawmatics.md) | Open a custom report from the Reports tab and export a CSV. | No | 2026-10-03 |
| [Actionstep](actionstep.md) | Run the Data Export Report. It gives one CSV per data source. | Yes, in beta | 2026-10-03 |
| [CARET Legal](caret-legal.md) (formerly Zola Suite) | Use Download Spreadsheet from the actions menu. CSV is also offered. | No | 2026-10-03 |
| [Centerbase](centerbase.md) | Use Export to Excel on a grid. Each user needs the Export Data permission. | No | 2026-10-03 |
| [Needles and Neos](neos-needles.md) | Export from Neos Advanced Search. Desktop Needles is unconfirmed. | No | 2026-10-03 |
| [CASEpeer](casepeer.md) | A paid data export by email request. An in-app report export is unconfirmed. For programmatic access, the Advanced tier has a read-only Data Sync API. | No | 2026-10-03 |
| [SmartAdvocate](smartadvocate.md) | Schedule a report to be emailed to you. | No | 2026-10-03 |
| [LEAP](leap.md) | Export the Matter List as CSV, with steps from a competitor's guide. | No | 2026-10-03 |
| Any other system | See [generic.md](generic.md). | Not researched | n/a |

## What the columns mean

**Official connector?** Yes means the vendor built or runs it. Yes, in beta means the vendor itself says the connector is still in beta. No means we found no official connector on 2026-10-03. For MyCase, the connector is a live beta, read tools work for every connected firm, and a Claude Team or Enterprise plan is required, per the vendor's tool catalog. For Actionstep, the beta is documented in Actionstep's own API docs, and you contact your Customer Service Manager to join. Litify has no connector of its own, but Salesforce offers hosted MCP servers. We could not confirm that they work with Litify's custom objects. A third-party listing for SmartAdvocate exists and we could not verify it.

**Best path today.** What a firm with no technical staff can do now, with no accounts, tokens or code. Only Clio has reports that Claude recognizes automatically by their column headings. For every other system, Claude maps the columns by meaning and confirms the match with you first.

## Things to know

Clio has no official Claude connector for firm data. Say "works with Clio exports," not "connects to Clio."

Zola Suite and CARET Legal are the same product. Zola Suite was rebranded as CARET Legal.

Lead Docket is made by Filevine, CASEpeer and MyCase are made by 8am, CosmoLex and Rocket Matter are made by ProfitSolv, and Needles and Neos are made by Assembly. Each system still has its own guide.

Zapier's MCP tools create and look up single records. They do not pull reports in bulk, so they do not fit this job, and the guides mention them only so you know they exist.

## About these guides

These are independent notes compiled from public sources. Nothing here is a vendor statement unless a guide says so. Anything we could not confirm is marked in plain words in the "What we could not verify" section of each guide. A gap there is a gap, not a fact.

Community-built servers are named in some guides with stars and last-push dates as we recorded them on 2026-10-03. This repo does not vouch for any of them. See the vetting checklist in connect-your-data.md.
