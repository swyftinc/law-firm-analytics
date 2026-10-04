# Centerbase

Last checked 2026-10-03. Vendors change menus often, so confirm in the product.

## The short version

Use Export to Excel on the grid that holds the data you want. Each user needs the Export Data permission, so if you do not see the option, that is the first thing to check. We found no official connector. One public community MCP server exists, but its README says it is for one firm's internal use only. Centerbase has public API documentation, but we could not confirm how a firm gets credentials.

## Export the reports you need

1. Open the grid that holds what you want, such as your matter list.
2. Choose Export to Excel.

If you do not see Export to Excel, ask whoever manages user permissions at your firm to give you the Export Data permission. Centerbase's help article says each user needs it. We read that article from a search extract, because the page blocked our automated checks, so confirm it in the product.

Centerbase's help article does not name specific grids or columns, and neither did our research. So choose by what the grid holds. For "what is stuck or slow," export your matters and look for open and close dates and status. For "are we getting paid for the work we do," look for time, billing and receivables. For "which practice areas make money," look for revenue by matter, with practice area. Leave out notes and free-text columns. Claude does not need them.

If a grid does not have what your question needs, say so. Claude will tell you what is missing instead of guessing.

## What to tell Claude

> I use Centerbase. Here is my matter grid, exported to Excel.

Centerbase has no preset. Claude reads the column headings, matches them by meaning to the fields it needs and shows you the match to confirm before it uses any of it.

## Connectors and MCP servers

Official: none found.

Community: frierlevitt1-prog/Centerbase-Integration is a public MCP server with 1 star, last pushed 2026-05-03. Its README describes 21 tools for matters, contacts, time entries, invoices, documents and notes, with read and write access. The README also says it is proprietary and for Frier Levitt's internal use only, so it is not a path for other firms. Community-built. This repo does not vouch for it. See the vetting checklist in connect-your-data.md.

Third party: none found. We found no Zapier connector for Centerbase either.

## API access

This is the advanced path. Centerbase publishes public API documentation. The API is a JSON web service at `https://YourFirmName.centerbase.com/mobile/api.svc/json/`, where YourFirmName is your own firm's name in Centerbase. We read this from a search extract of the documentation page, which our automated checks could not render. We could not confirm whether a firm can get credentials on its own or needs to ask Centerbase.

Do not paste credentials into a chat. Keep them in an environment variable or your system keychain.

## What we could not verify

- Whether API credentials are self-serve.
- Which grids have Export to Excel, and the columns of any grid.
- Whether Centerbase offers an official connector. We found none.

## Sources

https://support.centerbase.com/hc/en-us/articles/12809609510555-Export-to-Excel
https://centerbaseinc.notion.site/Centerbase-Public-API-83a8925a1d1f4494b4cc3e631ac14066
https://github.com/frierlevitt1-prog/Centerbase-Integration
