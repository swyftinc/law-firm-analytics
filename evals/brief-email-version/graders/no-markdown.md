---
type: regex
target: { source: file, path: firm-analytics/monday-briefing.txt }
pattern: '\*\*|^#|\|[-]{3}'
match: not_contains
flags: m
---
