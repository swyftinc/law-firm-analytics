---
type: llm
weight: 1
focus: { source: file, path: firm-analytics/monday-briefing.txt }
---

PASS if the final message gives the person the email text (or says where it is), starting with a subject line that states the main finding, in plain text with no tables or markdown symbols and no sign-off.

FAIL if the email is a wall of tables, lacks a subject line, or leads with anything but the biggest change.
