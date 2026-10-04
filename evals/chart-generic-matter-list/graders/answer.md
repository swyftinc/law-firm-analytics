---
type: llm
weight: 1
---

PASS if the answer reports median days from open to close by practice area (about 184 for family law, about 338 for business litigation, about 41 for estate planning, about 364 for personal injury), mentions that matters still open are not counted so the figure reads short, and states that it mapped columns with unusual names (Opened, Closed, Stage, Practice) by meaning.

FAIL if it averages instead of using the median without saying so, or counts open matters as closed.
