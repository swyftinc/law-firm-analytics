# claude.ai test runbook

For whoever installs the skills cold on claude.ai (a non-technical person is the best tester). The point is to find where someone stalls. Write down every place you hesitated, even if it worked in the end.

You need: a claude.ai account (note which plan: Free or Pro), the two zip files (`analyst-grade-charts.zip` and `monday-8am-briefing.zip`, built by `python3 tools/build.py` into `dist/`), and a stopwatch. If you have a real Clio export, bring one report. Do not bring client names or privileged data. Use a test export or the sample files.

## The test, in order

1. **Start the clock.** Open claude.ai in a fresh browser profile if you can.
2. **Turn on code execution.** Settings, then Capabilities, then **Code execution and file creation**. Note whether it was already on.
3. **Upload the first skill.** Customize, then Skills, press **+**, then **+ Create skill**, then **Upload a skill**, and pick `analyst-grade-charts.zip`. Note any error text exactly.
4. **Upload the second skill** the same way.
5. **Stop the clock.** Install time: ______ minutes. The bar is five.
6. **Run the three prompts**, each in a new chat:
   1. `Use analyst-grade-charts on the sample firm. Which lead sources should it put more money into?`
   2. `Use monday-8am-briefing on the sample firm and write this Monday's briefing.`
   3. `I use Clio. Use analyst-grade-charts. Which reports should I export to see where my ad money is going, and how?`
7. **Try your own file** if you have one: attach a Clio report (CSV or Excel) and ask a question about it.

## What to record for each prompt

| Check | Prompt 1 | Prompt 2 | Prompt 3 | Own file |
|---|---|---|---|---|
| Claude said it was using the skill | | | | |
| It found the sample data without help | | | n/a | n/a |
| It ran scripts without an error | | | n/a | |
| A file was created (name it) | | | n/a | |
| You could open or download the file | | | n/a | |
| The first chart looked deliberate, not generic | | | n/a | |
| The answer was right (Prompt 1: Google LSA cost doubled; Prompt 2: leads with it) | | | n/a | |
| Time from sending to result (minutes) | | | | |

Prompt 1 should say Google LSA now costs about twice its usual cost per signed matter. Prompt 2 should lead with that and mention family law realization and receivables over 90 days. Prompt 3 should say there is no official Claude connector for Clio and name specific reports to export.

## Also note

- Anywhere you got stuck, confused, or had to guess.
- Whether the HTML file opened inline or had to be downloaded and opened separately.
- Any message that mentioned network access, packages, or permissions.
- Your plan (Free, Pro, Team) and the date.

Send the filled-in table and screenshots to the maintainer. Anything that fails goes in as an issue with the exact text of the error.
