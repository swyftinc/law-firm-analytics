# Foundations

The ideas in these skills are not new, and neither are their authors'. This file maps each rule to the book or source it draws on, so you can read the original. Ideas are paraphrased and credited. No text is reproduced beyond a few words. No author or publisher has endorsed or sponsored this repo.

A tag like `[src: knaflic-swd]` in the other reference files resolves here. Each claim below was checked against a public source on 2026-10-03. Where only a secondary source supports it, or a primary page blocked automated checks, the entry says so. Where a claim could not be verified, it is not used.

## Chart craft

**`knaflic-swd`: Cole Nussbaumer Knaflic, *Storytelling with Data: A Data Visualization Guide for Business Professionals*, Wiley, 2015.**
Used for: start from context and the question; choose an appropriate visual; eliminate clutter; focus attention; think like a designer; tell a story. These are the book's six lessons, and its chapter titles include "Clutter is your enemy!" and "Focus your audience's attention." The "Big Idea," one complete sentence that states your point of view and what is at stake, shapes the briefing's lede. Source: https://www.wiley-vch.de/en/areas-interest/mathematics-statistics/storytelling-with-data-978-1-119-00225-3 and the author's post at https://www.storytellingwithdata.com/blog/2014/02/whats-big-idea

**`knaflic-lp`, `knaflic-swy`, `knaflic-ba`: *Storytelling with Data: Let's Practice!* (Wiley, 2019), *Storytelling with You* (Wiley, 2022), and *Storytelling with Data: Before & After* (Wiley, 2025, with Mike Cisneros and Alex Velez).**
Used for: the before and after image in the README follows the "makeover" format of *Before & After*, which presents 20 before-and-after redesigns. *Let's Practice!* is the workbook of exercises. *Storytelling with You* covers planning, creating and delivering a presentation. Sources: https://www.storytellingwithdata.com/books, https://www.storytellingwithdata.com/blog/2019/8/27/lets-practice and https://www.porchlightbooks.com/products/storytelling-with-data-cole-nussbaumer-knaflic-9781394289615

**`tufte-vdqi`: Edward R. Tufte, *The Visual Display of Quantitative Information*, Graphics Press, 1983 (2nd edition 2001).**
Used for: show the data and cut ink that carries none (the data-ink idea); graphical integrity, so a chart's visual effect matches the size of the effect in the data; small multiples, the same small chart repeated for comparison. The short line quoted is "Above all else show the data." Sources: https://www.edwardtufte.com/book/the-visual-display-of-quantitative-information/ and https://dannyreviews.com/h/Visual_Display.html . The "lie factor" idea (the size of the effect shown in the graphic divided by the size of the effect in the data) is defined at https://en.wikipedia.org/wiki/Misleading_graph , a secondary source.

**`tufte-be`: Edward R. Tufte, *Beautiful Evidence*, Graphics Press, 2006.**
Used for: sparklines, the tiny word-sized trend lines in the KPI tiles. The book has a chapter on them. Source: https://www.peterme.com/2006/07/20/tuftes-beautiful-evidence-chapter-2/

**`cairo-fa`: Alberto Cairo, *The Functional Art: An Introduction to Information Graphics and Visualization*, New Riders, 2012.**
Used for: Cairo's argument that function constrains form, and that decoration must not cover the information. Source: https://eagereyes.org/blog/2012/review-alberto-cairo-functional-art

**`cairo-ta`: Alberto Cairo, *The Truthful Art: Data, Charts, and Maps for Communication*, New Riders, 2016.**
Used for: the five qualities of a good visualization, truthful, functional, beautiful, insightful and, as a consequence, enlightening. These are the standard the "five questions" check borrows. Sources: https://infogram.com/blog/interview-alberto-cairo-and-the-truthful-art/ and https://www.peachpit.com/store/truthful-art-data-charts-and-maps-for-communication-9780321934079

**`wexler-bbd`: Steve Wexler, Jeffrey Shaffer and Andy Cotgreave, *The Big Book of Dashboards*, Wiley, 2017.**
Used for: designing a page for one scenario, which is how the Monday briefing is built. Its chapters on pies and donuts and on red and green are where we point readers on those two topics. The specific limits, three slices at most and an arrow and a word with every status color, are our own rules. Only the table of contents was verified, so the book is credited for the topics its chapters cover ("The Allure of Pies and Donuts," "The Allure of Red and Green," "Beware the Dead-End Dashboard," "Make Your Dashboards Personal"), not for any specific rule inside them. Source: https://www.wiley-vch.de/en/areas-interest/finance-economics-law/the-big-book-of-dashboards-978-1-119-28271-6

## Reasoning about numbers

**`wheelan-ns`: Charles Wheelan, *Naked Statistics: Stripping the Dread from the Data*, W. W. Norton, 2013.**
Used for: mean versus median, so skewed money and time lead with the median; the central limit theorem and why sampling matters; common biases (selection, survivorship, recall) that make a number look better or worse than it is. Sources: https://www.kirkusreviews.com/book-reviews/charles-wheelan/naked-statistics and https://thelivinglib.org/garbage-in-garbage-out-or-how-to-lie-with-bad-data/

**`silver-snn`: Nate Silver, *The Signal and the Noise: Why So Many Predictions Fail, but Some Don't*, Penguin Press, 2012.**
Used for: separating signal from noise, which is the job of the "normal range" label; overfitting, described as mistaking noise for signal; weighing new evidence against what you already knew, in the Bayesian way. Sources: https://www.slate.com/articles/business/books/2012/10/nate_silver_s_book_the_signal_and_the_noise_reviewed_.single.html and, secondary, https://markhneedham.com/blog/2013/05/14/book-review-the-signal-and-the-noise-nate-silver

**`provost-dsb`: Foster Provost and Tom Fawcett, *Data Science for Business*, O'Reilly, 2013.**
Used for: "data-analytic thinking," the book's term for framing a business problem as a question data can answer. The briefing's "what to look at" step applies the habit. Sources: https://www.data-science-for-biz.com/ and https://books.google.com/books?vid=ISBN9781449361327

**`stephens-davidowitz-el`: Seth Stephens-Davidowitz, *Everybody Lies*, Dey Street Books (HarperCollins), 2017.**
Used for: the theme that what people say can differ from what they do, which is why a lead source built only from an intake question is treated as lower confidence than a tracked source. Source: https://en.wikipedia.org/wiki/Seth_Stephens-Davidowitz

**`oneil-wmd`: Cathy O'Neil, *Weapons of Math Destruction*, Crown, 2016.**
Used for: the three traits of a harmful model, opacity, scale and damage, and its warning about feedback loops. This is why every number here is traceable to its inputs, why no composite "health score" is invented, and why people-level numbers are framed as questions, never verdicts. Sources: https://scholarlykitchen.sspnet.org/2016/09/14/book-review-the-traps-of-big-data-revealed-in-weapons-of-math-destruction-by-cathy-oneil/ and https://www.penguinrandomhouse.com/books/241363/weapons-of-math-destruction-by-cathy-oneil/

## Law firm metrics and operations

**`kabiri-aaw`: Mori Kabiri, "Law Firm KPIs: 5 Metrics to Track for Pricing, Profit and Predictability," *Attorney at Work*, September 2, 2025.**
Used for: the standard definitions of utilization (billable hours over available hours), billing realization (billed over worked), collection realization (collected over billed), profit margin, pricing variance, and total lockup (days from work to cash). Source: https://www.attorneyatwork.com/law-firm-kpis-5-metrics-for-pricing-profit-predictability/ . The article's prose describes margin as fees left after direct costs, while its formula is revenue minus expenses over revenue. This repo uses only the formula.

**`kabiri-lfk`: Mori Kabiri, *Law Firm KPIs: The Professional's Handbook for Pricing, Productivity, Profitability*, 2025.**
Used for: the shape of the field, a book of more than 80 metrics across finance, pricing, marketing and client acquisition, individual performance, and alternative fee arrangements. Little beyond the table of contents is visible publicly, so this repo does not copy or mirror the book's list, order or groupings, and draws on it only for names and standard formulas confirmed from public sources. Sources: https://books.google.com/books?id=1W92EQAAQBAJ and https://legalopskpis.com/lf/book

**`lambreth-lpm`: Susan Raridon Lambreth and David A. Rueff Jr., *The Power of Legal Project Management*, American Bar Association (first edition 2014; second edition, *A Practical Handbook*, 2021 or 2022, depending on the source).**
Used for: treating a matter as something you scope, budget, execute and evaluate at the end. A 2015 National Law Journal article by Allen W. Nelson and David A. Rueff Jr. quotes the first edition's definition of legal project management, which begins as a proactive, disciplined approach to managing legal work that involves defining, planning, budgeting, executing and evaluating a legal matter. The second edition's table of contents follows the same arc, with chapters on planning, budgeting, executing, and evaluating and closing the matter. This is the root of the budget-versus-actual and effective-rate metrics for flat fee work. Sources: https://www.bakerdonelson.com/files/LPM_Art__Science_02_17_2015.pdf and https://countrybookshelf.com/book/9781641059909

**`brenton-rlb`: Connie Brenton and Susan Raridon Lambreth, *Running Legal Like a Business: The Fundamentals of Legal Operations for Law Departments*, Practising Law Institute, 2021.**
Used for: the book's emphasis on reporting on a legal department's activity and on choosing the right metrics for day-to-day decisions. It is written for corporate legal departments, so we borrow the stance and not the metrics. Chapter titles could not be confirmed from a public page, so none are cited. Source: https://libraryrelations.pli.edu/9740

**`walters-ddl`: Edward J. Walters, ed., *Data-Driven Law: Data Analytics and the New Legal Services*, Auerbach Publications, 2019.**
Used for: the idea that firms gain when they collect and standardize matter data across a matter's whole life, which is why this repo defines each metric once and states its inputs. Source: https://www.routledge.com/Data-Driven-Law-Data-Analytics-and-the-New-Legal-Services/Walters/p/book/9781498766654

## Vendor definitions

**`clio-legal-trends`: Clio, "Law Firm Key Performance Indicators: Insights from the Legal Trends Report."**
Used for: the definitions of utilization, realization and collection rates, and the yearly benchmarks. The figures are from the 2025 report. Clio's page blocked automated checks, so the wording came from search extracts of that page. Two secondary pages attribute the same 38%, 88% and 93% to Clio's 2025 report: https://www.tlturnergroup.com/post/what-we-learned-from-the-2025-clio-legal-trends-report-and-why-it-matters-for-your-firm and https://pointone.com/blog/blog-law-firm-kpis-managing-partner . Benchmarks change every year, so confirm the wording at https://www.clio.com/resources/legal-trends/benchmarks/ before quoting it.

**`clio-grow`: Clio Grow reports help pages.**
Used for: how Clio Grow defines lead conversion (hired matters divided by all matters added) and the columns of its reports. Sources: https://help.clio.com/hc/en-us/articles/29739406189339-Clio-Grow-Reports and, when that page blocks bots, https://help.clio.com/api/v2/help_center/en-us/articles/29739406189339.json

## What is not claimed

- No claim is made about what is inside the Kabiri books beyond what is public.
- *The Big Book of Dashboards* is credited for its topics, not for rules inside its chapters.
- Chapter titles of *Running Legal Like a Business* are not cited, because no public page printed them.
- Regression to the mean, and the exact "correlation is not causation" framing, are not attributed to *Naked Statistics*, because those could not be confirmed from a public source.
- Nothing here says an author or publisher endorses these skills.
