---
name: monday-8am-briefing
description: "Write the one-page Monday 8am briefing a law firm owner reads before the partner meeting: what changed, why it probably changed, what to look at. Every number comes from the firm's exports."
license: MIT
compatibility: Needs Python 3 with the standard library for the bundled scripts. No network or installs needed.
---

# Monday 8am briefing

You write the memo an owner reads before the Monday meeting: what changed, why it probably changed, and what to look at. It leads with the change that matters most, does not recite every metric, ties every claim to a number, and says plainly when the data is too thin to conclude anything. It reads like a smart operator wrote it.

The reader is an owner, a managing partner or an ops lead with five minutes. The numbers come from the firm's own exports, computed by scripts. Your job is judgment and writing.

## Rules that never bend

1. **Every number comes from `facts.json`.** You do not compute, round differently or estimate. If a sentence cannot tie to a number on the page, cut it. Run the grounding check before you hand anything over.
2. **Lead with what matters most.** Not what changed first, not everything that changed. Two or three findings at most.
3. **A mechanism is a hypothesis, stated with its evidence and what would confirm it.** Use the strength of word the facts allow: clear, likely, or inside normal variation. Never a causal verb without evidence.
4. **Say the limit out loud.** Sample size, window, and anything missing. Under 10 cases is too thin to call. A change inside normal variation is not a finding, but name it in one line so no one chases it.
5. **People-level findings are questions, not verdicts.** Name a person once, plainly, and never rank people or imply fault.
6. **Ask for the least.** Aggregates are enough. Never ask for a password, key or token in chat.
7. **No em dashes, sentence case, "law firms."** The memo never mentions this skill, its authors or any vendor that is not the firm's own system.
8. **Direction is never inverted.** Cost per signed matter up is bad. Speed to lead minutes down is good.

## Find your scripts

Scripts and references live next to this file. When this skill loaded you were told its base directory ("Base directory for this skill"). Use that as `S`. In Claude Code the same folder is `${CLAUDE_SKILL_DIR}`. If you were not given it, find it once and reuse it:

```
S=$(dirname "$(find "$PWD" /mnt "$HOME/.claude" "$HOME" -maxdepth 8 -path '*monday-8am-briefing/SKILL.md' 2>/dev/null | head -1)")
ls "$S/scripts/render.py"
```

If you cannot find the scripts, say so and stop. Do not compute the metrics from scratch instead. Missing matplotlib or pandas does not matter. The scripts need only Python 3.

Work in a folder named `firm-analytics`. On claude.ai, save deliverables where the person can download them (the outputs folder).

## The workflow

### 1. Know the firm (three questions at most)

Read `references/interview.md`. Check for a saved profile, then the files, then the request. Ask only what is unknown, all at once, with defaults: who the memo is for, where the records live, what decision or meeting it supports. If you hear nothing, write for the owner and Monday's partner meeting.

### 2. Get the data

Read `references/connect-your-data.md` and `references/systems/<their system>.md` (or `generic.md`). The memo gets richer with more of: the lead report (with source and outcome), a monthly marketing spend sheet, a log of when each lead arrived and was first contacted, the time and billing report, a receivables aging report, a revenue report. Start with what they have and say what more would add. CSV and Excel are supported. The export is the default path. A connector or community server carries the vetting checklist and the "this repo does not vouch for it" disclaimer. Building their own read-only server is the advanced Claude Code path in `references/build-an-mcp.md`.

### 3. Read, map and compute

```
python3 "$S/scripts/inspect_data.py" <files> --draft firm-analytics/mapping.json --pretty
# review and fix mapping.json: entities, columns, value maps (outcome: signed/lost/open), file-level dates
python3 "$S/scripts/compute_facts.py" --mapping firm-analytics/mapping.json --out firm-analytics/facts.json --summary
python3 "$S/scripts/rank_changes.py" firm-analytics/facts.json --out firm-analytics/ranked.json
```

Read `warnings`, `unavailable` and `skipped` in the facts. They are what you could not do and what file would make it possible. Say so in the memo's last line.

`ranked.json` groups related facts into topics and sorts them by dollars at stake. Read it in this order:

- `look_at`: worsened topics, biggest first. Each has a `headline` fact, a `confidence`, and `corroboration` and `mechanism` facts that explain it.
- `supporting`: facts that belong inside a `look_at` item as its explanation (for example speed to lead supporting a lead source).
- `going_well`: improved topics. Mention the largest one briefly, unless it is lumpy.
- `unconfirmed`: single swings with no mechanism behind them. Never lead with one. Mention at most one as "worth watching," with its sample.
- `too_thin_to_call`: tempting numbers on too few cases. Name the most tempting one.
- `moved_within_normal_variation`: changes that are not bigger than chance. Name the one a reader is likeliest to chase.

### 4. Write the memo

Read `references/briefing-craft.md` first, then `references/example-briefing.md` for the shape. Study the structure, never reuse its sentences or numbers.

The headline is the first `look_at` item, stated as the change the owner feels: for a lead source with spend, what a signed matter now costs and how the signed rate moved. The mechanism (slower first contact, more after-hours leads) goes in the paragraph after, as the likely reason, never in the headline. Give the sample behind the headline number and say what would confirm or rule out the cause.

The shape: a headline that is the finding; a lede of one or two sentences; two or three findings, each a short paragraph covering what changed (number, window, sample), why it probably changed (hypothesis with evidence), and what to look at; one "look at this first" line; a "too thin to call" note; one line on normal variation; a footnote with the as-of date, windows and sources. About 300 to 450 words and at most two small charts.

Build the page as a spec (`"kind": "memo"`) with blocks `lede`, `h2`, `p`, `chart`, `callout`, `note`, `footnote`. Get chart blocks from `chartspec.py` (add `"compact": true`), then edit their titles. Use the facts' `display` strings for numbers.

### 5. Check it, then render it

```
python3 "$S/scripts/render.py" firm-analytics/memo-spec.json --out firm-analytics/monday-briefing.html --strict
python3 "$S/scripts/check_grounding.py" firm-analytics/monday-briefing.html --facts firm-analytics/facts.json --spec firm-analytics/memo-spec.json --strict
python3 "$S/scripts/memo_text.py" firm-analytics/memo-spec.json --out firm-analytics/monday-briefing.txt
```

Fix anything the checks flag. Then reread it: the lede alone should say the main thing, each status word should match its direction, and there should be no tell from the list in `briefing-craft.md`. Open the page (`open` on a Mac) or hand over the file. If the person cannot open files, also show it as an artifact when the surface supports one. The HTML prints to one US letter page.

### 6. Hand it over

Give them the HTML memo, the plain-text version with a subject line for pasting into an email, and one line on what you could not compute and what file would make it possible. Then ask once: "Anything you'd change? Say more like this or less like this." Save the answer in the profile (`references/profile-template.md`): a file in Claude Code, or a block to paste into project instructions elsewhere.

## Charts inside the memo

At most two, small, each answering one question the memo raises, with the accent on the one thing to look at. The rules are in `references/chart-doctrine.md`. Skip a chart if a sentence does the job.

## When something goes wrong

- **No Python or the scripts fail:** say so. Write the memo from numbers you computed and printed in code or a spreadsheet, label it as not checked by the grounding script, and keep every number traceable to a printed table.
- **Too little data:** write a short memo that says what you can and cannot say, and what would fix it. Do not pad.
- **`look_at` and `going_well` are both empty:** it was a quiet week. Say that, plainly, in a few sentences. Name at most one `unconfirmed` item worth watching, with its sample, and say what moved but is inside normal variation. A quiet Monday is a real answer. Do not turn a chance swing into a story.

Never invent a number, never state a cause the evidence does not support, and never name a person as the reason a number moved without framing it as a question.

## Try it without your own data

If there are no files yet, run the same steps on the sample firm in `assets/sample-data/`: "show me what this does." Read it where it is, do not copy it. Skip the inspect step, because `mapping.json` is already there:

```
python3 "$S/scripts/compute_facts.py" --mapping "$S/assets/sample-data/mapping.json" --out firm-analytics/facts.json --summary
python3 "$S/scripts/rank_changes.py" firm-analytics/facts.json --out firm-analytics/ranked.json
```
