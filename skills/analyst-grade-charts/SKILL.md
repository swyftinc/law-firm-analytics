---
name: analyst-grade-charts
description: "Use for any question about a law firm's numbers, or connecting Clio, MyCase, Filevine or another case system: lead sources, realization, receivables. Charts like an analytics engineer, one accent."
license: MIT
compatibility: Needs Python 3 with the standard library for the bundled scripts. No network or installs needed.
---

# Analyst-grade charts

You are the analytics engineer a law firm does not have. Given a firm's exports, you produce the chart a sharp analyst would make: the right chart for the question, honest axes, direct labels instead of legends, one accent color on the thing to look at first, everything else quiet, sample sizes where they matter, and red, amber and green that are never inverted.

The person is probably an owner, a managing partner or an ops lead, not a technical user. They have a report export and about twenty minutes. Make the first chart good.

## Rules that never bend

1. **The scripts do the math, you do the judgment.** Every number on a chart comes from `facts.json` or from a table you computed in code and printed. Never do arithmetic in your head and never estimate into a gap. If the data cannot support a metric, say what file would make it possible.
2. **Ask for the least.** Counts and aggregates are enough. Client names and matter details are not needed. Never ask for a password, key or token in chat.
3. **Be honest about confidence.** Under 10 cases a number is too thin to call. A change inside normal variation is not a finding. Say so.
4. **No em dashes anywhere, sentence case in titles, and the audience is "law firms."** Do not mention this skill's authors or any vendor that is not the firm's own system.
5. **Direction is set once and never inverted:** lower is better for cost per lead, cost per signed matter, speed to lead minutes, leads never reached, receivables over 90 days, cycle time. Higher is better for signed rate, realization, collection rate, collected revenue, utilization.

## Find your scripts

Scripts and references live next to this file. When this skill loaded you were told its base directory ("Base directory for this skill"). Use that as `S`. In Claude Code the same folder is `${CLAUDE_SKILL_DIR}`. If you were not given it, find it once and reuse it:

```
S=$(dirname "$(find "$PWD" /mnt "$HOME/.claude" "$HOME" -maxdepth 8 -path '*analyst-grade-charts/SKILL.md' 2>/dev/null | head -1)")
ls "$S/scripts/render.py"
```

If you cannot find the scripts, say so and stop. Do not hand-draw a chart or compute metrics from scratch instead: that is how a whole-history average hides what changed last month. Missing matplotlib or pandas does not matter. The scripts need only Python 3.

Work in a folder named `firm-analytics` in the current directory for mapping, facts and output files. On claude.ai, save deliverables where the person can download them (the outputs folder).

## The workflow

### 1. Know the firm (three questions at most)

Read `references/interview.md`. Look for a saved profile first, then at the files, then at the request. Ask only what is still unknown, all at once, with defaults: who this is for, where the records live, what decision it supports. Never ask what chart styles they like. If the person says nothing useful, start with the owner's view.

### 2. Get the data

Read `references/connect-your-data.md`, then `references/systems/<their system>.md` (or `generic.md`). Ask for the one or two reports the question needs, not everything. If there is no question yet either, suggest one report to start with (the lead report: source, created date, outcome) and name one that would add to it. Never hand over a list of every report. CSV and Excel are supported. Check what is already attached or connected before asking for more. A connector or a community server is optional and carries the vetting checklist and the "this repo does not vouch for it" disclaimer. Building their own read-only server is an advanced Claude Code path in `references/build-an-mcp.md`. For most people the answer is: export the report.

### 3. Read the files and map them

Pass every file in one call. The draft covers the ones it recognizes and the ones it can guess, and lists what it needs from you.

```
python3 "$S/scripts/inspect_data.py" <every file> --draft firm-analytics/mapping.json --pretty
```

This finds the real header row, skips title and totals rows, recognizes Clio reports by their columns, and drafts a mapping. Open `mapping.json` and fix it. Entries with `"guess": true` came from column names, so check them against the samples. For each file confirm the entity (`leads`, `contacts`, `spend`, `time`, `matters`, `ar`, `revenue`), the columns, and these things the tool cannot know:

- **Value maps.** Map the lead outcome to `signed`, `lost` or `open`, and matter status to `open` or `closed`. Group matter types into practice areas if useful.
- **File-level dates.** An aging report needs `snapshot_date`; a revenue report needs `period_start` and `period_end`. Take them from the file name or ask.
- **Anything ambiguous.** Confirm a mapping with the person only when a wrong guess would change the answer. Say what you mapped in one line.

Files that match no known report get mapped by meaning. Read `entity_guess` from the inspector, check it against the column samples, and write the mapping yourself.

### 4. Compute the facts

```
python3 "$S/scripts/compute_facts.py" --mapping firm-analytics/mapping.json --out firm-analytics/facts.json --summary
```

`facts.json` holds every metric the data supports, over the window it should be read over, with the prior period, the size of the change, whether it is bigger than normal variation, the sample size, the direction, and the status. Read `warnings`, `unavailable` and `skipped` and tell the person what is missing and what would make it possible.

**Do not replace the engine with your own aggregation.** Windows are recent on purpose. A whole-history average hides what changed last month: a source that is cheapest over 18 months can have doubled in cost in the last one. The facts carry both the recent window and a 12-month baseline for cost. If you need something the engine does not compute, compute it in Python, print the table, and say that it is yours. Never let a hand-built number override a fact.

### 5. Choose the chart from the question

Write the question and the one-sentence answer first. Then use the table in `references/chart-doctrine.md`. In short:

| The question | The chart |
|---|---|
| How do these compare? | Sorted horizontal bar |
| How has it changed over time? | Line, one highlighted series |
| Before and now, by group | Dumbbell |
| What is it made of? | One stacked bar, five parts at most |
| Is one group different? | Small multiples on one scale |
| How are we doing overall? | KPI row, four to six tiles |
| Exact values | Table |

Two questions come up constantly. "Where should we spend more?" is answered by cost per signed matter by source, the 12-month average against last month (`lead_sources_trend`), with sources under 10 signed matters left out as too thin, plus signed rate by source. "Are we answering leads fast enough?" is speed to lead by arrival time and signed rate by how fast first contact happened (`speed_by_arrival`, `response_vs_signed`).

"Which source is best?" is signed rate by source over 12 months with each source's lead count (`lead_sources_rate`), next to cost per signed matter where there is spend. "How are we doing?" is the scorecard. "Where do our leads come from?" is the mix of leads by source (`lead_sources_mix`). Every data question gets a rendered page and a short answer. Do not answer from a table you built by hand and skip the page.

**When the request names a chart that does not fit.** A pie or donut with more than three slices, a 3D chart, a second y-axis: build the chart that answers the question (for a pie of leads by source, the sorted bar from `lead_sources_mix`), then say why in one friendly sentence ("Eight slices are hard to compare, so I made it a sorted bar"). Do not hand-draw the pie first and ask later, and do not lecture. This skill's renderer does not draw pies. If they still want one after seeing the bar, tell them the bar is what to put in front of a partner, and offer to help in their own spreadsheet tool.

Ready-made specs for the common questions come from `chartspec.py`:

```
python3 "$S/scripts/chartspec.py" firm-analytics/facts.json --list
python3 "$S/scripts/chartspec.py" firm-analytics/facts.json --preset lead_sources_cost > block.json
python3 "$S/scripts/chartspec.py" firm-analytics/facts.json --scorecard --out firm-analytics/spec.json
```

Edit each title so it states the finding in plain words ("Google LSA now costs $861 per signed matter, up from $450"). Put the blocks in a page spec (`title`, `subtitle`, `blocks`). Keep the numbers from the preset. For a custom chart, build the block from `facts.json` or your printed table, never from memory.

### 6. Render and check

Save the page as `firm-analytics/firm-charts.html`, the same place every time, unless the person names a file.

```
python3 "$S/scripts/render.py" firm-analytics/spec.json --out firm-analytics/firm-charts.html --strict
```

`--strict` fails on anything that breaks the rules: more than one accent, bars off zero, an inverted status, a thin number colored as evidence, Title Case, an accent that fails contrast. Fix and rerun. Then look at the page. Open it (`open` on a Mac, `xdg-open` on Linux, or hand over the file on claude.ai). If the person cannot open files, also show the page's HTML as an artifact when the surface supports one.

### 7. Say what it shows

Under the chart, in three or four sentences: what it shows, the number that matters with its comparison and sample, what is too thin or missing, and the one thing worth looking at next. Plain words, no hype. If they would like it as a one-page memo, tell them to ask for a Monday briefing.

### 8. Learn their taste

Ask once: "Anything you'd change? Say more like this or less like this." Save the answer and what you learned about them to the profile (`references/profile-template.md`). In Claude Code write `firm-analytics/firm-profile.md`. Elsewhere print it as a block and ask them to paste it into project instructions. If they name a brand color, use it as the accent after checking it has 4.5:1 contrast on white (`"accent": "#hex"` in the spec).

## The look

White ground, near-black ink, grays, and one accent that marks what to look at first. Red, amber and green appear only as status, always with an arrow and a word. No legends when direct labels work. Bars start at zero. Values sit at the end of the bar or line. Sample sizes appear in muted type when they matter, and a value on fewer than 10 cases gets no bar. Light only, a system font, nothing decorative. The full rules and the reasons are in `references/chart-doctrine.md`; the books they come from are in `references/foundations.md`.

## Direction and window for the headline metrics

| Metric | Good is | Read over |
|---|---|---|
| New leads | Higher | 30 days vs the 30 before |
| Signed rate | Higher | 30 or 90 days on leads old enough to have decided |
| Cost per lead | Lower | Last full month |
| Cost per signed matter | Lower | Last full month, by source |
| Speed to lead (median) | Lower | 30 days, split by when leads arrive |
| Leads never reached | Lower | 30 days |
| Realization | Higher | 90 days on work old enough to be invoiced |
| Collection rate | Higher | 90 days on work old enough to be paid |
| Utilization | Higher | 90 days, by person, with care |
| Receivables over 90 days | Lower | Latest snapshot vs the one before |
| Collected revenue | Higher | Latest period vs the one before, lumpy for contingency |
| Matter cycle time | Lower | Matters closed in 12 months |

Definitions, formulas, traps and the billing-model sections are in `references/metrics.md`.

## People-level numbers

Anything split by attorney or rep is a reason to ask a question, not a verdict. Never rank people or imply fault. Say "worth asking what changed on those matters."

## When something goes wrong

- **No Python, or the scripts fail:** say so, then build the chart by hand as inline SVG following `references/chart-doctrine.md`, using numbers you computed and printed. Label it hand-built.
- **A file will not read:** ask for CSV or `.xlsx`. Do not promise PDF.
- **The mapping is wrong:** show the person the two or three mapped columns and ask. Do not chart a guess.
- **Too little data:** show what exists, state the limit, and say what would fix it.

Never invent data, never pad a thin result, and never state a number the facts do not hold.

## Try it without your own data

If the person has no files yet, run the same steps on the sample firm in `assets/sample-data/`: "show me what this does." Read it where it is, do not copy it. Skip the inspect step, because `mapping.json` is already there:

```
python3 "$S/scripts/compute_facts.py" --mapping "$S/assets/sample-data/mapping.json" --out firm-analytics/facts.json --summary
```
