# Maintaining this repo

Amin owns triage, the quarterly re-check, and releases. Brandon approves anything that changes the promise on the coupon: "Make Claude chart like an analytics engineer. Two free Claude skills: analyst-grade charts, and a Monday 8am briefing written from your numbers. Open source and yours to keep." That means the two skills, their names, and their price.

## What goes stale, and how often

Every system guide in `src/shared/references/systems/` carries the date it was checked. Vendors change menus, plans and connectors, and they do it quickly. Re-check the guides every quarter, and sooner when a vendor announces something.

1. For each guide, open the vendor pages listed under Sources. Confirm the export steps, the report names, the connector status, and any plan or price statement.
2. For community-built servers, run `gh api repos/<owner>/<name>` and update the stars, license and last-push date. Remove a server that is archived or has gone quiet for a year.
3. Re-check the Clio report columns against Clio's help center. If a column changed, update `references/systems/clio.md`, the preset in `scripts/schema.py`, and `tools/generate_sample_data.py` together, then regenerate the sample data.
4. Update the "Last checked" line only when you checked.
5. Rebuild and test (below), then cut a release.

Anything you cannot confirm stays marked as unconfirmed. Never fill a gap from memory.

## Changing the skills

Edit `src/`, never `skills/`. The folders under `skills/` are built output, and CI fails if they drift.

```
python3 tools/build.py            # rebuild skills/, validate them, write dist/*.zip
python3 -m unittest discover -s tests
claude plugin eval . --scaffold --trust-plugin --allow-tools Bash Write Edit --model sonnet --max-cost-usd 30
```

The build checks that each skill's `name` matches its folder, that descriptions fit claude.ai's 200 character limit, that no em dash appears anywhere, that every source tag resolves in `foundations.md`, and, if you keep a local `tools/denylist.local.txt`, that no listed name leaked in. That file is ignored by git on purpose: the list itself should not be public.

Evals are plain files under `evals/`. A new rule needs a new case. The answer key in `evals/ground_truth.py` is computed without any engine code, so a bug in the engine cannot hide in both places.

## Releasing

1. Rebuild and run the tests and the evals. Read the failures, don't average them away.
2. Test the zips on claude.ai following `tools/claude-ai-test-runbook.md`, on a free and a paid account, with someone who has never installed a skill.
3. Run `python3 tools/run_api_evals.py` with an API key.
4. Tag `vX.Y.Z` and attach `dist/analyst-grade-charts.zip` and `dist/monday-8am-briefing.zip` to the release. The README links to the latest release.

## Rules that do not bend

The skills never mention who made them. They never ask for a password, key or token in the chat. Every number in a briefing comes from the scripts. No em dashes anywhere. The audience is "law firms."
