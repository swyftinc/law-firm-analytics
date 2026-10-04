# Example briefing

A worked example, written from the sample firm's numbers (Super Duper Law, as of October 4, 2026). Study its shape. Never reuse its sentences or its numbers: every memo you write comes from the firm's own `facts.json`, and `check_grounding.py` will fail any number that is not in it.

## The memo

# Google LSA cost per signed matter nearly doubled in September

Google LSA now costs $861 per signed matter, up from $450 in August, on the same lead volume: 68 leads in the last 30 days against 67 before. The likely cause is when those leads arrive and how long they wait.

### LSA leads now arrive after hours, when first contact is slow

Cost per signed matter went from $450 to $861, September against August. Only 12 matters signed in September against 20 in August, so treat the size as approximate. Over the last month, 20.9% of LSA leads have signed, against 31.9% the month before. That's a likely drop, not a certain one. If it holds, it is worth about $159K in estimated fees on those leads, using the firm's own estimated value field.

The likely reason is timing. After-hours and weekend leads were 32.9% of LSA leads and are now 83.3%. Across every source, leads reached within an hour signed at 51.0%, and leads that waited more than a day or were never reached signed at 5.7%. More leads arriving after hours, and waiting longer for a first contact, could account for much of this drop. Lead quality could also have slipped, and these numbers can't rule that out.

[chart: Leads reached within an hour sign at 51.0%; after a day, 5.7%]

### Family law realization fell, mostly on one attorney's matters

Family law realization is 76.8%, against 87.8% the 90 days before, on 314 time entries. That is about $21K of recorded work that did not reach a bill. About 81% of the change sits on one attorney's matters, 87.4% down to 53.2%. It's worth asking what changed on those matters: a rate, a dispute, a new matter type.

### Receivables over 90 days are up, and one matter holds most of it

Receivables more than 90 days past due rose from $122,048 to $151,178 between the two aging reports, up 24%. One matter holds 78% of that total, so this is a collections conversation about one account, not a slide across the firm.

**Look at this first:** Pull September's LSA leads that arrived after 6pm or on a weekend and check how long each one waited for a first contact.

**Too thin to call:** A new wealth advisor referral source has four leads that reached a decision, and all four signed. That's too few to call it your best source.

New leads are up 6% (181 against 170). That's inside normal variation.

*As of October 4, 2026. Leads and speed to lead cover the last 30 days. Realization covers the 90 days ending 35 days ago, so the work has had time to be invoiced. Receivables compare the two aging reports. Dollars at stake use the firm's estimated value field. Every number is computed from the firm's exports.*

## What to notice

The headline is the finding, with its size. The lede gives the number, the comparison and the sample, and says what probably explains it, in two sentences.

The first finding states the change, then the sample ("only 12 matters signed"), then the strength of the evidence ("a likely drop, not a certain one"), then the dollars at stake with the method in one clause. The next paragraph gives the mechanism as a hypothesis with its evidence, and names another explanation the numbers cannot rule out. The chart under it answers the one question the memo raises, whether speed to first contact matters.

The second finding is about one attorney's matters. It states the share of the change that sits there, frames it as a question to ask, and names no verdict. The third finding says the money is concentrated in one matter, which turns a firm-wide worry into a collections conversation.

"Look at this first" is one specific check a person can do before the meeting. "Too thin to call" names the tempting number and says why it cannot carry a conclusion. The line on normal variation tells the reader what not to chase. The footnote gives the as-of date, the windows and how the numbers were made.

Every number on the page appears in `facts.json`. Nothing is rounded in a way that changes its meaning. No sentence could appear in a consulting deck for any other firm.
