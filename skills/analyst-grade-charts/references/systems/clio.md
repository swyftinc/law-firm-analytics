# Clio

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Clio has no official Claude connector for firm data. This repo works with Clio exports. It does not connect to Clio.

If you have no technical staff, export a few reports from Clio as CSV and give them to Claude. Six Clio reports are recognized automatically by their column headings: the Matters report, Revenue report, Realization report, Accounts receivable aging report, and two Clio Grow reports (Matter revenue and Lead source revenue). Any other Clio report can be used too. Claude maps its columns by meaning and confirms the match with you first.

## Export the reports you need

Where the reports live in Clio Manage:

1. Open Reports.
2. Choose Classic reports, then the Reports subtab.
3. Pick a category, then the report.
4. Under Output format, choose CSV.

Clio says most reports come out as CSV and PDF, and some also as Excel and Web. Use CSV or Excel. Some columns only appear in CSV or Excel, and a PDF is hard to read reliably. For the revenue, originating attorney revenue, fee allocation, matter balance summary, matter productivity by user, billing rate, client activity, trust ledger and trust management reports, you can hide and reorder columns in CSV. Hide the `Description` and `Note` columns if you can. Claude does not need them.

Clio's presets and history article limits scheduling a preset to run automatically to US Core, Signature and Elite plans. It states no plan limit for saving presets or viewing history.

Clio's newer Custom Reports are in beta, under Reports Beta. You can build them on US Signature and Elite plans, and the fields you pick become the column headers. Claude maps those by meaning, because the columns are whatever you chose.

### Which report answers which question

Are we getting paid for the work we do? Start with the Realization report, and add the Accounts receivable aging report. Which practice areas make money? The Revenue report, for two comparable periods. What is stuck or slow? The Matters report shows what is open, and the Matter balance summary shows work in progress and receivables. Where is our marketing money working? The Clio Grow Matter revenue report and the Lead source revenue report. Which referral sources send us work? The Referral report in Clio Grow.

### Every report the skill can use

The columns below are the exact names from Clio's help center, copied on 2026-10-03. Each report name links to the article it came from.

| Report | Exact columns | Preset | Metrics it supports |
|---|---|---|---|
| [Matters report](https://help.clio.com/hc/en-us/articles/14349646533787-Clio-Manage-Matter-Reports) | `Client`, `Matter`, `Description`, `Practice area`, `Status` (Open, Pending or Closed), `Responsible attorney`, `Originating attorney`, `Billable`, `Accounts receivable`, `Latest bill` | `clio_matters` | Open matters by practice area and attorney, receivable balance by matter. Its documented columns have no open or close dates, so it does not support cycle time on its own. |
| Matters by responsible attorney report (same article) | `Matter`, `Client`, `Description` | None | Which matters each attorney is responsible for. |
| Billing rate report (same article) | `Client`, `Matter number`, `Matter description`, `User`, `Practice area`, `Rate type`, `User's matter rate`, `User's client rate`, `User's default rate`, `Matter open date`, `Originating attorney`, `Responsible attorney` | None | A matter open date. Cycle time also needs a close date. |
| Contact information report (same article) | `Client name`, `Matter`, `Primary phone number`, `Primary email address` | None | Contact details only. Not needed for charts or a briefing, so we would not ask for it. |
| [Revenue report](https://help.clio.com/hc/en-us/articles/14352205073051-Clio-Manage-Revenue-Reports), Web or PDF | `Matter`, `Location`, `Unbilled time`, `Unbilled hours`, `Unbilled expense`, `Billed time`, `Billed hours`, `Billed expense`, `Billed tax 1`, `Billed tax 2`, `Discounted time`, `Discounted expense`, `Credit notes`, `Collected time`, `Collected expense`, `Collected tax 1`, `Collected tax 2`, `Collected uncategorized`, `Client total` | None | Use the CSV or Excel version instead. |
| Revenue report, CSV or Excel (adds these columns) | `Client`, `Practice Area`, `Matter Description`, `Responsible Attorney`, `Billed Interest`, `Collected Interest` | `clio_revenue` | Collected revenue and billed amounts by practice area and attorney. |
| Originating attorney revenue report (same article) | `Attorney`, `Collected time`, `Collected expense`, `Collected interest`, `Collected tax`, `Collected secondary tax`, `Grand total` | None | Collected revenue by originating attorney. It reflects only the matter's Originating Lawyer, not fee splits. |
| Fee allocation report, all formats (same article) | `User`, `Matter`, `Client`, `Invoice`, `Practice area`, `Responsible attorney`, `Originating attorney`, `Billed hours`, `Billed time`, `Billed time allocation`, `Collected time`, `Outstanding time` | None | Collected revenue split between people. |
| Fee allocation report, CSV only (adds these columns) | `Billed expense`, `Expense allocation`, `Collected expense`, `Outstanding expense`, `Total collected`, `Total outstanding`, `Interest collected`, `Interest outstanding`, `Collected tax 1`, `Outstanding tax 1`, `Collected tax 2`, `Outstanding tax 2`, `Collected time allocated to responsible attorney`, `Collected time allocated to originating attorney`, `Matter billing method`, `Non-billable time amount`, `Non-billable time allocation` | None | The same, with expenses and the billing method. |
| [Billing history report](https://help.clio.com/hc/en-us/articles/14330519112987-Clio-Manage-Billing-Reports) | `Invoice number`, `Status`, `Due date`, `Amount`, `Payments`, `Credit notes`, `Balance`, plus totals `Matter total`, `Client total`, `Attorney total` | None | Invoice by invoice: what was billed, paid and still owed. |
| Accounts receivable report (same article) | The same columns as the Billing history report. `Status` is Past Due or Open. | None | What is past due. |
| Invoice payments report (same article) | `Date`, `Client`, `Matter`, `Transaction`, `Invoice`, `Debit`, `Credit`, `Total` | None | Payments over time, by invoice. |
| Accounts receivable aging report (same article) | `Matter`, `Originating attorney`, `Responsible attorney`, `Bill id`, `Current`, `1-30 days`, `31-60 days`, `61-90 days`, `91+ days`, `Total`, plus totals `Matter total`, `Client total`, `Attorney total`, `Total uncategorized` | `clio_ar_aging` | Receivables over 90 days and their share of the total, and whether one matter holds most of it. |
| Matter balance summary report (same article) | `Matter`, `Accounts receivable`, `Work in progress`, `Expenses in progress`, `Total`, and optionally `Client trust funds` and `Matter trust funds` | None | `Work in progress` and `Accounts receivable` are the inputs for lockup. We found no Clio definition of lockup. |
| [Realization report](https://help.clio.com/hc/en-us/articles/14351524759707-Clio-Manage-Productivity-Reports) (CSV only) | `Time entry date`, `User`, `Time Entry Type`, `Invoice Status`, `Invoice Number`, `Rate Type`, `Rate`, `Quantity`, `Original Billable Total`, `Original Non-Billable Total`, `Adjusted Amount`, `Adjusted Hours`, `Amount Discounted`, `Hours Discounted`, `Billed Time Amount`, `Billed Hours`, `Billed Time Collected`, `Billed Time Credited`, `Billed Time Outstanding`, `Matter Number`, `Matter Billing Method`, `Practice Area`, `Responsible Attorney`, `Originating Attorney` | `clio_realization` | Realization and collection rate. It also has hours by user and date, which Claude can use for utilization. That last use is our reading of the columns, not a Clio statement. |
| Productivity by user, also called the lawyer productivity report (same article) | `Activity class`, `Unbilled`, `Billed`, `Total`. The "Reporting fact" filter switches between Money and Time. | None | Billed and unbilled work by activity class, in dollars or hours. |
| Productivity by client (same article) | `Client`, `Amount`, `Percentage` | None | Each client's share of the work. |
| Matter productivity by user (same article) | `Date`, `Status`, `Description`, `Note`, `Quantity`, `Rate`, `Total`, `Unbilled total`, `Billed total`, `Matter total` | None | Entry-level detail. It carries `Description` and `Note` text that Claude does not need. |
| [Work in progress report](https://help.clio.com/hc/en-us/articles/14344842681115-Clio-Manage-Client-Reports) | `Date`, `User`, `Description`, `Note`, `Quantity`, `Price`, `Total`, `Matter total`, `Client total` | None | Unbilled work, entry by entry. |
| Client activity report (same article) | `Date`, `Activity type`, `Status`, `User`, `Activity category`, `Description`, `Quantity`, `Price`, `Total`, plus totals `Billed total` and `Matter total` | None | Activity entries by user and category. |
| [Clio Grow Matter revenue report](https://help.clio.com/hc/en-us/articles/29739406189339-Clio-Grow-Reports) (Download CSV) | Grow columns: `Contact`, `Email`, `Source`, `Referred by`, `Matter`, `Description`, `Matter type`, `Matter status - top level`, `Matter status - detailed`, `Status date`, `Created at`, `Location`, `Estimated value`. Manage columns: `Matter`, `Description`, `Practice area`, `Matter status`, `Status date`, `Created at`, `Location`, `Originating attorney`, `Responsible attorney`. Revenue columns: `Unbilled time`, `Unbilled hours`, `Unbilled expenses`, `Billed time`, `Billed hours`, `Billed expenses`, `Collected time`, `Collected expenses`, `Revenue` | `clio_grow_matter_revenue` | New leads, lead source mix, signed rate, and revenue by source. `Created at` and `Status date` are the inputs for time from intake to hire. |
| Clio Grow Lead source revenue report (same article) | `Source`, `Intake matters`, `Hired matters`, `Not hired matters`, `Hired conversion rate`, `Estimated value`, `Revenue`, `Spend`, `ROI (as a multiplier)`, `ROI (as a percentage)` | `clio_grow_lead_source` | Conversion and revenue by source. `Spend` and ROI only apply to US firms using Google Local Services Ads. |
| Clio Grow Matters added report (same article) | Chart metrics rather than columns: `Matters added`, `Pipeline value`, `Conversion rate`. Use the table view, then Download CSV. | None | Leads added over time and conversion rate. |
| Clio Grow Referral report (same article) | `Name`, `Total Referrals`, `Total Matters`, `Intake`, `Hired`, `Did Not Hire`, `Total Value`, `Average Value`, `Intake Value`, `Hired Value`, `Did Not Hire Value`, `Conversion Rate %` | None | Which referral sources send work that hires. |

A few rules from Clio's Revenue report article. Unbilled amounts use the entry's created date. Billed amounts use the bill issue date. Collected amounts use the payment date. Partial payments are allocated proportionally by default, and that setting can be changed. Tell Claude if your firm changed it.

There is no Clio report named "Collected time." Collected time is a column in the Revenue, Originating attorney and Fee allocation reports. If you need fee splits by role, percentage or additional users set in your fee allocation settings, Clio points to the Fee allocation dataset in Custom Reports.

### The matter list, the contact list and the bulk export

These exist, but Clio does not publish their column lists. Claude maps them by meaning and confirms the match with you.

The Matters tab has an Export at the bottom of the page, after you apply any filters. It gives a CSV with all columns or only the visible ones, or another format. Clio says it includes only the data you entered in the matter form. If your file has open and close dates, Claude can use it for matter cycle time. We could not confirm that it does.

The Contacts tab also has an Export, as CSV or PDF. Clio says it includes basic contact information and any contact custom fields, without billing preferences.

Clio Grow has its own export. Go to Matters, choose View all, Intake or Hired, then "Export all matters to CSV." Clio emails the file as a link.

Clio's admin bulk export lives at app.clio.com/export (the North America address) and offers "Excel ready CSV" for Calendar entries, Communications, Contact notes, Contact related matters, Contacts, Expense entries, Matter notes, Matters, Tasks and Time entries. Expect to need an administrator. Ask only for Matters, Time entries and Expense entries. Notes and communications are free text, and Claude does not need them.

### How Clio defines utilization, realization and collection

Clio's Legal Trends report defines the utilization rate as "the percentage of an eight-hour day that gets put towards billable work." It defines the realization rate as "the percentage of billable work that gets invoiced to clients." It defines the collection rate as "the percentage of invoiced work that gets paid."

We could not load the clio.com page directly, because it sits behind Cloudflare. This wording came from search-engine extracts of the page, and it was consistent across several queries. Confirm the wording on the page before you quote it.

Clio's own blog defines utilization against an employee's available time instead of a fixed eight-hour day, so definitions differ even within Clio. The same page gives 2025 benchmarks: utilization 38% (about 3.0 billable hours a day), realization 88% (2.6 hours invoiced) and collection 93% (2.4 hours collected). The same caveat applies.

Clio Grow defines conversion as hired matters divided by all matters added, and "Hired conversion rate" as hires divided by intakes for each lead source. It defines lead source ROI as revenue divided by ad spend. Clio publishes no definition we could find for lockup, work in progress or matter cycle time. Define those with Claude. The inputs exist: `Work in progress` and `Accounts receivable` in the Matter balance summary, and `Created at` and `Status date` in the Grow report.

## What to tell Claude

Paste a sentence like one of these along with the file:

> I use Clio Manage. Here is my Realization report, exported as CSV.

> I use Clio Grow. Here is my Matter revenue report.

Claude recognizes six reports by their column headings, so you do not need to rename or reformat anything. The preset names are `clio_matters`, `clio_revenue`, `clio_realization`, `clio_ar_aging`, `clio_grow_matter_revenue` and `clio_grow_lead_source`.

Here is how each one is read. In the Matters report, Open and Pending count as open and Closed counts as closed. In the Revenue report, Claude adds up the billed and collected columns by practice area and attorney, and asks which period the report covers, since the file does not say. In the Realization report, Claude reads `Time entry date`, `User`, `Original Billable Total`, `Billed Time Amount`, `Billed Time Collected` and `Billed Time Outstanding` as worked, billed, collected and outstanding work. In the aging report, each row is a bill sorted into aging buckets, and Claude asks what date you ran it. In the Grow Matter revenue report, Hired counts as signed, Not hired (or Did Not Hire, the wording the Referral report uses) as lost and Intake as open, and Claude confirms the practice area names with you. Clio's article does not list the exact status labels for this report, so Claude also reads the status values from your file and confirms them with you. The Lead source report is one row per source with no dates.

The Grow Matter revenue report includes contact names and emails. Claude uses the email only to tell leads apart. Every other Clio report is read by meaning. Claude shows you which columns it matched and waits for a yes.

## Connectors and MCP servers

Official: none for firm data. Clio has no official MCP server or Claude connector for Manage or Grow data. The one MCP-related item from Clio is a June 24, 2026 partnership with Perplexity to put Vincent legal research into Computer for Counsel through an MCP connector, announced as launching in the coming months for large law firms. It is about legal research, not your firm's Manage data. Clio's page blocked automated checks, so open it once yourself to confirm the wording. Say "works with Clio exports," not "connects to Clio."

Community: oktopeak/clio-mcp has 25 stars, an MIT license, about 37 tools and a read-only mode, and was last pushed 2026-10-01. It does not mention Grow support. Mahender22/legal-mcp has 68 stars, an MIT license and was last pushed 2026-06-19. We did not record what it covers. protomated/legal-context-ce has 29 stars, an MPL-2.0 license and was last pushed 2026-05-01, and covers documents only. lawyered0/clio-mcp has 8 stars, an MIT license and was last pushed 2026-04-24. Star counts and dates were checked on 2026-10-03 and drift. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: Zapier's Clio MCP lists 17 write actions and 8 "Find" searches (counted from the names on its page), plus 3 find-or-create actions and 12 triggers such as New Bill and New Activity. It has no way to list or export bills or time entries in bulk. Pipedream has Clio apps for the US, EU and Canada, each with 3 actions and 3 triggers. Zapier's tools create and look up single records and do not pull reports in bulk, so they do not fit this job.

## API access

This is the advanced path. Clio's public API is REST v4 with OAuth 2.0. To use it you create a Developer Application in the Clio Developer Portal, which gives you a client ID and client secret, and you need a Clio account in each region. Clio Grow uses a separate API, the Clio Platform API (Grow API). Private apps skip Clio's approval process. Public apps need approval. The older Grow Lead Inbox API only accepts POSTs, so it cannot read data out.

Do not paste a client secret or any token into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- Whether Anthropic's May 12, 2026 "Claude for Legal" launch includes any practice management connector. We saw only a summary list, and it showed none. We could not confirm that in detail.
- Whether every Clio plan tier gets API access.
- The columns in the Matters tab export, the Contacts tab export, the Grow matter export and the bulk export at app.clio.com/export. Clio does not publish them.
- The exact Legal Trends wording and 2025 benchmarks. The clio.com page was not fetched directly.
- Clio's description of `Hired Value` in the Referral report repeats the "Intake status" wording, which looks like a typo in Clio's docs. Check what the number means in your account before relying on it.
- The menu path to Reports inside Clio Grow. We captured the report names and columns, not the clicks.
- Any Clio definition of lockup, work in progress or matter cycle time. We found none.
- What the Mahender22/legal-mcp server covers.

## Sources

https://help.clio.com/hc/en-us/articles/9290078155803-Clio-Manage-Reports-Presets-and-History (updated 2026-08-31)
https://help.clio.com/hc/en-us/articles/37685184870299-Custom-Reports-in-Clio-Manage
https://help.clio.com/hc/en-us/articles/14349646533787-Clio-Manage-Matter-Reports (updated 2026-09-04)
https://help.clio.com/hc/en-us/articles/14352205073051-Clio-Manage-Revenue-Reports (updated 2026-10-01)
https://help.clio.com/hc/en-us/articles/14330519112987-Clio-Manage-Billing-Reports (updated 2026-09-04)
https://help.clio.com/hc/en-us/articles/14351524759707-Clio-Manage-Productivity-Reports (updated 2026-09-04)
https://help.clio.com/hc/en-us/articles/14344842681115-Clio-Manage-Client-Reports (updated 2026-09-11)
https://help.clio.com/hc/en-us/articles/29739406189339-Clio-Grow-Reports (updated 2026-04-08)
https://help.clio.com/hc/en-us/articles/55326718151195-Filter-and-Export-Matters-in-Clio-Manage
https://help.clio.com/hc/en-us/articles/9290532034843-Filter-and-Export-Contacts
https://help.clio.com/hc/en-us/articles/55326679120795-Filter-and-Export-Matters-in-Clio-Grow
https://help.clio.com/hc/en-us/articles/50633368921243-Export-Data-From-Clio-Manage
https://www.clio.com/resources/legal-trends/benchmarks/
https://www.clio.com/blog/how-to-calculate-utilization-rate/
https://www.clio.com/about/press/clio-perplexity-partnership/
https://oktopeak.com/blog/clio-mcp-connectors-compared/
https://claude.com/blog/claude-for-the-legal-industry
https://github.com/oktopeak/clio-mcp
https://zapier.com/mcp/clio
https://pipedream.com/apps/clio
https://pipedream.com/apps/clio-eu
https://pipedream.com/apps/clio-canada
https://docs.developers.clio.com/api-docs/clio-manage/applications/
https://docs.developers.clio.com/api-docs/clio-platform/applications/
https://docs.developers.clio.com/guides/clio-grow/lead-inbox-api/
