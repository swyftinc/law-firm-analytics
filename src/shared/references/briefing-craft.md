# Briefing craft

How to write the one-page memo an owner reads before the Monday meeting. The reader has five minutes, knows the firm better than you do, and wants to walk into the room knowing what changed, why it probably changed, and what to look at. The memo exists for that meeting. Nobody files it.

## The shape

1. **A headline that is the finding.** "Google LSA cost per signed matter nearly doubled in September." Not "Weekly performance update."
2. **A lede of one or two sentences.** The most important change, with its number, its comparison, and its size. A reader who stops here still knows the main thing. [src: knaflic-swd] (the "Big Idea": one sentence that states your point of view and what is at stake)
3. **Two or three findings, each a short paragraph.** What changed, with the number, the window and the sample. Why it probably changed, with the evidence in the data. What to look at, as a specific check or question.
4. **One "look at this first" line.** The single thing to do before or in the meeting.
5. **A "too thin to call" note** when a number is tempting but rests on a handful of cases.
6. **One line on what moved but is inside normal variation**, so no one chases it.
7. **A footnote**: as-of date, the windows, the source files, and how the numbers were computed.

It prints on one page. About 300 to 450 words of prose plus at most two small charts. If it does not fit, cut findings, not detail inside the findings.

## What goes first

Take `look_at[0]` from `ranked.json`: the worsened topic with the most dollars at stake and the most support. Lead with good news only if it is far larger, high confidence and not lumpy. A drop in a number nobody watches doesn't lead. A swing in a lumpy line (a few big settlements) does not lead.

Do not recite every metric. If a number does not change what the owner does on Monday, it is not in the memo. Three findings is the ceiling.

## Every claim ties to a number on the page

- Every number in the memo comes from `facts.json`. You do not compute, round differently, or estimate. Run `check_grounding.py` before delivering. A memo with an ungrounded number is not done.
- Every comparison names its comparator and window: "$861, up from $450 in August", "76.8% against 87.8% over the prior 90 days."
- Say how many cases stand behind a rate or a median: "12 signed matters", "259 leads". Under 10 cases, say it is too thin to call and stop there.
- Dollars at stake come from the facts and carry their method in one clause: "about $159K in estimated fees, using the firm's own estimated value field."
- If you cannot tie a sentence to a number, cut the sentence.

## Why it probably changed

This is the part that separates an analyst from a dashboard. Rules:

- **State a mechanism as a hypothesis, with the evidence.** "Google LSA leads now arrive after hours or on weekends 83% of the time, up from 33%, and across all sources leads reached within an hour sign at 51% against 5.7% when contact takes over a day. That is the most likely explanation for the drop." [src: silver-snn] (separate the signal from the noise, and weigh new evidence against what you already knew)
- **Use the right strength of word.** `clear` in the facts: "fell," "rose." `likely`: "looks like," "probably." `normal range`: "moved within normal variation." Never a causal verb without evidence for the cause. Correlation is not cause: say what else could explain it, and what would confirm it. [src: wheelan-ns]
- **Say what would confirm it.** "Pull September's LSA leads that came in after 6pm or on weekends and check how long each waited."
- **Do not stretch.** If the data supports "the mix shifted," do not write "Google changed its algorithm."
- **Say the limit out loud.** Sample size, window, and anything missing: "Twelve signed matters is a small base, so treat the size as approximate. The direction is consistent across three measures."

## People

When a finding is about one person's matters or calls, it is a question to ask, not a verdict. Name the person once, plainly, and frame the next step as a conversation: "Most of the drop is on one attorney's matters (87% to 53%). It is worth asking what changed: rates, a dispute, a new matter type." Don't rank people, don't use fault language, and don't turn a person-level number into a score. [src: oneil-wmd] (opaque, scaled scoring of people is how analytics does harm)

## Voice

Write the way a smart operator who has read the numbers would write to the owner. Direct, specific, calm.

- Lead with the point. No setup, no scene-setting, no "this week we looked at."
- Short paragraphs, one idea each. Prose, not bullet lists. Plain headings in sentence case.
- Contractions are fine. "You" for the firm. No "I."
- Specific beats abstract: the source, the practice area, the dollar amount, the day. Concrete nouns, plain verbs.
- Hedge the future and the causes. Do not hedge the facts.
- End on the action, not on a flourish.

Never use em dashes. Use a period, a comma, or a new sentence.

Avoid these tells. A single one is a reason to rewrite the sentence:

- Em dashes. "It's not X, it's Y." "Not X. Y." fragment pairs used for rhythm.
- "Here's the thing," "let me be clear," "the reality is," "but here's what," "at the end of the day," "in today's [anything]."
- Significance inflation: pivotal, crucial, testament, underscores, landscape, journey.
- Superficial -ing tails: "highlighting," "reflecting," "showcasing."
- Rule-of-three lists forced to sound complete. Use the natural number of items.
- Rotating synonyms for one thing. If it is "signed matters," keep it "signed matters."
- Vague attributions ("experts say," "many firms"). Name the source or cut it.
- Consultant words: leverage, synergy, optimize, streamline, actionable insights, best-in-class.
- "Genuinely," "honestly," "straightforward," "I hope this helps," "Great question."
- Generic closers: "the future looks bright," "exciting times ahead."
- Title Case headings, emoji, exclamation points.

If a sentence could appear in a consulting deck for any company, it does not belong in this memo.

## Words for the numbers

- Round to what the owner can act on: "$861", "51%", "3.7 hours", "about 80%". Keep the exact figure in the facts.
- Write "up from X to Y" or "X against Y", and one of them is the comparator.
- Percent change and percentage points are different. "Realization fell 11 points, from 88% to 77%." Not "fell 11%."
- Write "median" for medians. Write "signed matters," "leads," "hours" so the unit is always visible.

## Cadence and the audience

A briefing on a fixed day builds a habit: the same shape every week, so the reader knows where to look. Keep the headings and the order stable from one Monday to the next.

Write for the person in the profile. An owner wants dollars and decisions. An operations lead wants volumes, speed and backlog. A lawyer wants their own matters. If you do not know, ask once, or write for the owner.

## Delivery

1. The memo as a single HTML page that prints to one US letter page.
2. The same memo as plain text for pasting into an email, with a subject line that is the headline. No tables, no markdown symbols, no sign-off.
3. A line under the memo listing anything you could not compute and the file that would make it possible.

## Before you hand it over

- Run `check_grounding.py`. Fix anything it flags.
- Search the text for em dashes and the tells above.
- Read the lede alone. Does it say the main thing?
- Check each status word against its direction: cost up is bad, speed minutes down is good.
- Check the memo fits on one page.
- Make sure the memo never mentions this skill or who wrote it. It is the firm's memo. Name the firm's own systems when it helps ("Clio export", "Google Ads").
