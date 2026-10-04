# Chart doctrine

How a sharp analytics engineer decides what to draw and how to draw it. Every rule here is one an owner can check with their eyes. Where a rule traces to a book, it carries a source tag in square brackets that resolves in `foundations.md`.

## Start with the question, not the data

A chart answers one question. Write the question first, then the sentence that answers it, then pick the chart. If you cannot say the takeaway out loud in one sentence, you are not ready to draw.

Good questions are decisions: "Which lead sources should we spend more on?" beats "Here is a chart of lead sources." Ask what someone would do differently after seeing the chart, and what good versus bad would look like. [src: knaflic-swd] (her first lesson is to understand the context)

The title of every chart is the answer, in plain words: "Google LSA now costs $861 per signed matter, up from $450." The subtitle says what is measured, over what window, from how many cases.

## Pick the chart from the question

| The question | Use | Notes |
|---|---|---|
| How do these compare? | Horizontal bar, sorted by value | Long labels read left to right. Sort unless the categories have a natural order (stages, age buckets, time). |
| How has this changed over time? | Line for a continuous series, column for discrete periods | Time runs left to right. Highlight one line, gray the rest. |
| Before and now, by group | Dumbbell | Shows the move for each group in one glance. No zero needed. |
| What is it made of? | One stacked bar, five parts at most | More than five parts is a sorted bar. |
| Is this one group different from the rest? | Small multiples, same scale | Repeat the same small chart. The eye does the comparing. [src: tufte-vdqi] |
| How is it distributed? | Histogram | Only when the spread is the story. |
| What is the status of a handful of numbers? | KPI row: value, change, tiny trend, direction | Four to six tiles. Each tile answers a question. |
| Exact values, fewer than ten rows, or a scorecard | Table | A table is a real answer, not a fallback. |
| Where? | Map | Only if place is the story. Rarely is for a law firm. |

Pie and donut charts: three slices or fewer and only when "about half" is the point. Otherwise a sorted bar. Never 3D, never a second y-axis. If you want a second axis, you want two charts. These limits are this repo's own rules. *The Big Book of Dashboards* has a chapter on the topic, "The Allure of Pies and Donuts." [src: wexler-bbd]

## The look: quiet, with one voice

- **One accent color marks the thing to look at first.** Everything else is gray. If two things are blue, nothing is. The accent is the same on every chart in a page. [src: knaflic-swd] (see her chapter "Focus your audience's attention")
- **Ink is near black, not pure black. Ground is white.** Gridlines are hairlines or absent. No borders around charts, no shadows, no gradients, no background tints that do not encode anything.
- **Label directly.** Put the value at the end of the bar and the series name at the end of the line. A legend means the eye has to travel and match colors. With four or fewer series there is never a legend.
- **Cut ink that carries no data.** Remove heavy gridlines, tick marks, redundant labels, decoration. Keep axis units and anything a reader needs to read a value. "Above all else show the data." [src: tufte-vdqi]
- **Type is sentence case**, left-aligned, with numbers in tabular figures and right-aligned in tables. Never Title Case or ALL CAPS in titles.
- **Name things for what they show**, never "Chart 1." Use one term per concept across a page: if it is "signed matters" once, it is never "retained clients" later.

## Honest axes

- **Bars start at zero.** Always. A truncated bar axis turns a slight decline into a collapse, the kind of distortion Tufte's lie factor measures. [src: tufte-vdqi]
- **Lines may start above zero when the range is narrow**, but then say so in the subtitle and label the axis. Volume and money lines start at zero by default.
- **Same scale across compared panels.** Small multiples share one y-axis.
- **Do not cherry-pick the window.** Show enough history that the reader can see what normal looks like. If this month looks bad, show the months around it.
- **Compare equal windows.** Thirty days against thirty days. Never a partial month against a full one.
- **Round to the resolution a reader can act on.** "26 days" beats "26.4." Cards use two significant figures (`$1.2M`); tables show whole dollars.

## Status colors never invert

Red, amber and green mean worse, watch, better. They mark status only, never a category. Every status carries an arrow and a word ("worse"), not just color, because some readers cannot tell red from green. [src: wexler-bbd] (see the chapter "The Allure of Red and Green")

Direction is a property of the metric, set once:

- **Higher is better:** lead volume, signed rate, realization, collection rate, utilization, collected revenue, share of leads reached within an hour.
- **Lower is better:** cost per lead, cost per signed matter, speed to lead (minutes), leads never reached, receivables over 90 days, matter cycle time, days in a stage, write-offs.
- **Neutral, so gray:** marketing spend, source mix, open matters, revenue by a single person. They are levers or context, not scores.

So a rise in cost per signed matter is red. A fall in speed to lead minutes is green. Check the direction before choosing a color, every time, and say "Lower is better" on the chart.

A status color needs a real change behind it: big enough to matter, not inside normal variation, and on enough cases. Otherwise the tile stays gray and says "normal range" or "too thin."

## Sample size shows when it matters

A rate or median with no sample size is not a number. Show the count next to it in muted type ("12 signed", "259 leads"), not as a cryptic badge. Under 10 cases a value is **too thin to call**: draw no bar, no status color, and say so in words. A bar would look like evidence. [src: wheelan-ns] [src: silver-snn]

Money and time are skewed, so lead with the median and say "median." Recompute rates from the underlying rows, never by averaging monthly percentages. Do not draw a trend or forecast you cannot derive from the data.

## What a good chart page looks like

1. A KPI row if the question is "how are we doing" (four to six tiles), else go straight to the chart.
2. Each chart: title that states the finding, a subtitle with measure, window and sample, the chart, a one-line source note.
3. One accent per chart, the same accent on the whole page.
4. A closing line that says what is too thin to call and what is not in the data.

The page must work in black and white and on a phone. It should print on one page without surprises.

## Five questions before showing anything

1. What question does this answer?
2. What is the one takeaway, said out loud in one sentence?
3. Will someone get it in five seconds?
4. Is it honest: axis, window, sample, direction?
5. Would I stake my name on it?

If any answer is "no" or "not sure," stop and fix it first. [src: cairo-ta] (Cairo's five qualities of a good chart: truthful, functional, beautiful, insightful, enlightening.)

## Anti-patterns to refuse

- A legend far from the data. A rainbow of colors. More than four or five lines on one chart.
- Dual axes. 3D. Radial layouts for data that is not cyclical.
- Pies of near-equal slices. Alphabetical sorting of bars.
- A KPI grid of totals and averages that answers no question. Three of anything because the layout has three slots.
- An AI summary or narrative that states a number the page does not show.
- A percentage with no sample size. A trend arrow with no basis.
- Inverting a status color "to make the chart tell a better story."

## When a chart is the wrong answer

If the answer is one number, write the number big. If the answer is a sentence, write the sentence. If the reader needs to look up exact values, give a table. Charts are for patterns and comparisons.
