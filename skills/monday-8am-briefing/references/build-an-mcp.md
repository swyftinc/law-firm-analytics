# Build your own read-only MCP server

An advanced, opt-in path for a technical person using **Claude Code in a terminal**. It does not work on claude.ai. Most firms should export a report instead (see `connect-your-data.md`). Offer this only when the person asks for data pulled without exports, or is clearly comfortable with a terminal.

The idea: the firm creates its own read-only credentials with its vendor. A small program on the firm's own computer reads from the vendor's API and saves the result as CSV files. Claude Code asks that program to fetch reports. Nothing is hosted and nothing is shared.

One design choice protects client data: **the tool saves the data to a file and tells Claude only the file name, the row count and the column names.** Client rows never have to pass through the chat. The skills then read the file with their scripts.

## What Claude should check before starting

- The person is in Claude Code, not claude.ai.
- The vendor has an API they can reach. See the system's guide under `systems/` for how access works and who can grant it. Some vendors need a request or an approval first. Some have no open API.
- They can create read-only credentials (an API key, a personal access token, or an OAuth app limited to read scopes). If the vendor only offers read and write together, say so and recommend the export path.
- Their firm allows it. Ask whether anyone needs to sign off. This is not legal advice.
- Python 3.10 or newer is available. macOS ships an older Python. The official MCP guide uses `uv`, which installs what it needs.

## Rules for the whole build

1. **Read-only.** Use credentials that cannot write. Define only tools that call GET endpoints. The server has an allow list of endpoints and refuses anything else.
2. **No secrets in chat or in files in the project.** The person puts the token in an environment variable in their own terminal or shell profile. The server reads it from there. Never ask the person to paste a token to you.
3. **No stdout.** A stdio server talks to Claude over stdout, so a stray `print()` breaks it. Log with the `logging` module, which writes to stderr. [src: mcp-build-server]
4. **Ask for the least.** Request only the fields the metrics need. Skip names, notes and free text where the vendor lets you.
5. **Local only.** Do not host it, share it, or point it at anything but the vendor's API.
6. **Try it on fake or sandbox data first** if the vendor has a sandbox.

## The steps

1. **Pick the reports.** From the question, choose one to three reports and the fields each needs (see the table in `connect-your-data.md`). Read the vendor's API docs with the person and write down, for each: the endpoint, the filters, how pagination works, and the field names. Do not guess any of these.
2. **Create a project folder** and a Python environment with the SDK:

   ```
   uv init firm-data
   cd firm-data
   uv venv
   source .venv/bin/activate
   uv add "mcp[cli]"
   ```

3. **Write `server.py`** from the skeleton below, filling in the endpoint list, the pagination and the field mapping from step 1. Keep it short and readable. Read it back to the person in plain words so they know what it can and cannot do.
4. **Have the person set the credential** in their own terminal, for example `export FIRM_API_TOKEN=...`, and the base URL, `export FIRM_API_BASE_URL=...`. If the vendor uses OAuth, write a one-time local script for the authorization step that stores the refresh token outside the project folder. Never print a token.
5. **Register the server with Claude Code** so the token never lands in a config file. Create `.mcp.json` in the project folder and reference the variables:

   ```json
   {
     "mcpServers": {
       "firm-data": {
         "command": "uv",
         "args": ["run", "server.py"],
         "env": {
           "FIRM_API_TOKEN": "${FIRM_API_TOKEN}",
           "FIRM_API_BASE_URL": "${FIRM_API_BASE_URL}"
         }
       }
     }
   }
   ```

   Claude Code expands `${VAR}` in `env` from the shell at startup, so start Claude Code from the terminal where you exported the variables. If one is unset, the server receives the literal text `${FIRM_API_TOKEN}`. [src: claude-code-mcp] The alternative is the command line form `claude mcp add --env KEY=value --transport stdio firm-data -- uv run server.py`, but that saves the value as part of the server's stored configuration in `~/.claude.json`, so prefer the `.mcp.json` form for tokens. If you use the command line form, keep `--transport stdio` between `--env` and the server name, or the name is read as another variable. [src: claude-code-mcp]
6. **Check it connects.** Run `claude` once and approve the server when Claude Code asks, since it asks the first time it sees a project server. Until you do, `claude mcp list` shows it as pending approval. After that, `claude mcp list` or `/mcp` in a session should show it connected. [src: claude-code-mcp]
7. **Test with one small pull.** Export one report for a short date range. Check the row count and the columns against the vendor's own screen. Then run the skill's normal flow on the file.
8. **Review what it can do.** List the tools and the endpoints on the allow list. Confirm there is no write path.

## The skeleton

This is a starting point, not a finished server. The marked lines are vendor-specific and must be filled in from the vendor's documentation.

```python
import csv
import logging
import os
import pathlib

import httpx2
from mcp.server import MCPServer

logging.basicConfig(level=logging.INFO)          # goes to stderr, never stdout
log = logging.getLogger("firm-data")

BASE_URL = os.environ["FIRM_API_BASE_URL"].rstrip("/")
TOKEN = os.environ["FIRM_API_TOKEN"]              # set in the shell, never in this file
OUT_DIR = pathlib.Path(os.environ.get("FIRM_EXPORT_DIR", "firm-analytics/exports"))
MAX_ROWS = 50_000

# Allow list: only these GET endpoints can ever be called. FILL IN from the vendor docs.
REPORTS = {
    "matters": {"path": "/REPLACE/matters", "fields": ["id", "practice_area", "status", "open_date", "close_date"]},
    # "time_entries": {...},
    # "bills": {...},
}

mcp = MCPServer("firm-data")


@mcp.tool()
async def list_reports() -> str:
    """List the reports this server can export. Read-only."""
    return "\n".join(f"{name}: {', '.join(spec['fields'])}" for name, spec in REPORTS.items())


@mcp.tool()
async def export_report(name: str, since: str = "") -> str:
    """Save one report to a CSV file in the exports folder and return the file name, row count and columns.
    Read-only. `since` is an optional start date (YYYY-MM-DD)."""
    if name not in REPORTS:
        return f"Unknown report. Choose one of: {', '.join(REPORTS)}"
    spec = REPORTS[name]
    rows = []
    url = BASE_URL + spec["path"]
    params = {"since": since} if since else {}          # FILL IN the vendor's date filter name
    headers = {"Authorization": f"Bearer {TOKEN}"}      # FILL IN the vendor's auth scheme
    seen = set()                                        # stops a vendor that keeps returning the same page
    async with httpx2.AsyncClient() as client:
        while url and url not in seen and len(rows) < MAX_ROWS:
            seen.add(url)
            kwargs = {"params": params} if params else {}   # an empty params would wipe the query in a "next" link
            response = await client.get(url, headers=headers, timeout=60.0, **kwargs)
            response.raise_for_status()
            body = response.json()
            for item in body.get("data", []):           # FILL IN where the records are in the response
                rows.append({f: item.get(f) for f in spec["fields"]})
            url = body.get("next")                      # FILL IN the vendor's pagination
            params = {}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=spec["fields"])
        writer.writeheader()
        writer.writerows(rows)
    log.info("wrote %s rows to %s", len(rows), path)
    return f"Saved {len(rows)} rows to {path}. Columns: {', '.join(spec['fields'])}."


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The imports and the `MCPServer`, `@mcp.tool()` and `mcp.run(transport="stdio")` shape follow the official MCP guide for Python, which asks for Python 3.10 or newer and version 2.0.0 or higher of the SDK. [src: mcp-build-server] Check the current guide before relying on it, since the SDK is young and moves.

## Treat every server as untrusted code, including yours

Claude Code's own documentation says to verify you trust each server before connecting it, because servers that fetch external content can expose you to prompt injection. [src: claude-code-mcp] Fields that come from the vendor's API, such as a matter description or a note, can hold text that tries to instruct Claude. That is another reason to keep the tools read-only, save to files, and skip free text.

## What was tested

The skeleton was run against a local mock REST API with the Python MCP SDK 2.3.0 on Python 3.12 in October 2026. The tools registered, a paginated export saved exactly the allow-listed columns to a CSV, and Claude Code ran both tools with the token supplied through a `${VAR}` entry in `.mcp.json`. It has not been run against any vendor's live API, so expect to adjust the authentication, the pagination and the field names for yours.

## Sources

- `mcp-build-server`: https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server
- `claude-code-mcp`: https://code.claude.com/docs/en/mcp
