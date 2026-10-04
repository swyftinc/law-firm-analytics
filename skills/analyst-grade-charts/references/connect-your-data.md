# Connect your data

How to get a firm's numbers into the skills, whatever system they live in. The skills are not tied to one system. They read exports and, where it is safe and available, connectors.

Claude's job here is to find out where the person's records live, check what is already connected, and walk them to the shortest safe path. Ask for the one or two reports the question needs, and leave the rest.

## The order to try things

1. **Already attached or connected.** If files are attached, or the session has a connector or MCP tool for the person's system, use it. For a connector, read only what the question needs, write the result to CSV in the working folder so the engine can read it, and check one small pull first.
2. **Export a report (the default).** Every system exports something. This is the path for most firms: no accounts, no tokens, nothing leaves their hands except a file they chose. Read `systems/<system>.md` for the exact steps and the reports worth exporting.
3. **An official connector**, if the system's own vendor offers one and the person's plan can use it. See the system's guide.
4. **A community-built MCP server**, with the vetting checklist below and the disclaimer. Only for people comfortable running code.
5. **Build your own read-only MCP server** in Claude Code, against the firm's own API credentials. Opt in, advanced, see `build-an-mcp.md`.

Say which path you recommend and why in one sentence. For a non-technical owner it is almost always the export. Do not offer path 4 or 5 unless the person asks for something that runs without exports, or is technical.

## What to ask them for

Start from the question, then name the report:

| The question | What to export |
|---|---|
| Where is our marketing money working? | The lead report with source and outcome, plus a monthly spend sheet by source |
| Are leads getting answered fast enough? | A log of when each lead arrived and when someone first reached out |
| Are we getting paid for the work we do? | The time and billing report (realization), plus receivables aging |
| Which practice areas make money? | The revenue report by matter, for two comparable periods |
| What is stuck or slow? | The matter list with open and close dates |

If the person does not know which report, send them to the system's guide and describe the report by what it contains, not by menu path alone: menus move.

## File formats

CSV and Excel (.xlsx) are supported and tested. Other formats work when they happen to, but do not promise them:

- Old `.xls`: ask them to Save As `.xlsx` or CSV.
- PDF reports: a person can read them and extraction is unreliable. Ask for the CSV or Excel version of the same report.
- Google Sheets: ask them to download as `.xlsx` or CSV.
- A pasted table works for small data.

Exports often have a title line above the header, blank lines, and a totals row at the bottom. The inspector finds the real header and skips totals. Tell the person what you skipped.

## Official connectors

Status as of 2026-10-03. Re-check before relying on any of this, and see each system's file for sources.

- **Clio:** we found no official Claude connector for firm data as of 2026-10-03. The only first-party MCP item we found from Clio is Vincent legal research inside Perplexity, announced 2026-06-24 (https://www.clio.com/about/press/clio-perplexity-partnership/, which blocked our automated check, so open it yourself). Say "works with Clio exports," never "connects to Clio."
- **MyCase:** its maker announced an official MCP server on 2026-09-23 and calls it a beta service. Read tools work for every connected firm, and write tools are off by default and limited to firms in a write beta. MyCase's tool catalog says a Claude Team or Enterprise plan is required. Check the system's guide for the current state.
- **Litify:** no Litify-branded connector. Salesforce offers hosted MCP servers that a Salesforce admin can set up. This takes an admin and some setup time.
- **Actionstep:** an MCP endpoint appears live, but the vendor has not announced it. Treat as unconfirmed.
- Everything else: none found. Use the export.

On claude.ai, every plan can add a custom connector. Free plans are limited to one, and on Team and Enterprise plans only an owner (or an Enterprise role with the right access) can add one. Check the person's plan before suggesting it.

For the systems checked here, Zapier's MCP tools create and look up single records. They do not pull reports in bulk, so they do not fit this job.

## Community-built MCP servers: the vetting checklist

Anyone can publish an MCP server. A server you connect can see whatever the credentials allow, and it runs on the person's machine. This repo does not vouch for any community server. If the person wants one, go through this list with them and tell them to read the code or have someone technical do it.

1. **Who made it and are they still around?** Last commit in the past few months, an issue tracker with replies, more than one contributor if possible.
2. **License.** A standard open source license (MIT, Apache 2.0). No license means no right to use it.
3. **Read-only mode.** Does it have one? Can you give it credentials that cannot write? Prefer a server that only reads.
4. **Scopes.** What does the token it asks for allow? Ask for the narrowest scopes the vendor offers.
5. **Where does data go?** It should talk to the vendor's API and nothing else. Look for any other network calls, analytics, or telemetry.
6. **Where does the token live?** An environment variable or the system keychain, never a file in a shared folder and never pasted into chat.
7. **Tested for real?** Some servers are generated and tested only against mocked responses. A README that says so is honest. One that does not say is a risk.
8. **Pin it.** Install a specific version, not "latest," and review before updating.
9. **Try it on fake data first** if the vendor offers a sandbox.

If it fails any of 3, 5 or 6, do not use it.

The disclaimer to give, in plain words: "This server is community-built. This repo does not vouch for it, and nobody here has audited it. You are trusting its author with access to your firm's data."

## Your own MCP server

For a technical person using Claude Code who wants data pulled without exports. The firm creates its own read-only API credentials with the vendor, and a small local server exposes a handful of read-only tools. Nothing is hosted, nothing is shared. See `build-an-mcp.md`. This does not work on claude.ai.

## Client data and confidentiality

Law firms hold privileged information. Treat every connection and every upload as a decision.

- **Ask for the least.** Aggregates and counts are enough for almost everything in these skills. Client names and matter details are not needed for charts or a briefing. Prefer exports without free-text fields and note fields. If a file has them, say so and ignore those columns.
- **Never ask for passwords, API keys or tokens in the chat.** If a step needs a secret, tell the person to put it in an environment variable or their system keychain themselves.
- **Check the firm's rules first.** Lawyers have duties about client information and about the tools they use. Point them to their state bar's guidance on generative AI and client confidentiality, and to their own firm policy and their Claude plan's data terms. [ABA Formal Opinion 512](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/) on generative AI tools is a starting point. This is not legal advice, and you should not give any.
- **Keep it local when you can.** Files stay in the person's own account or machine. Do not send them anywhere else, and do not store them beyond the session unless the person asks.

## When nothing works

If the system has no export that fits, no connector, and the person is not technical: ask for whatever report they do have, even a printout converted to a spreadsheet by hand for one month, and do what the data supports. Say what the missing data would make possible. A small honest chart beats a large invented one.
