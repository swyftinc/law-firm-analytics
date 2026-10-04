---
type: llm
weight: 1
---

PASS if the answer recognizes it as a Clio accounts receivable aging report, ignores the totals row (receivables over 90 days are about $151K, total about $349K), and says it has only one snapshot, so it cannot say whether receivables are getting better or worse.

FAIL if it counts the totals row as a bill, or claims a trend from a single snapshot.
