---
type: regex
target: { source: file, path: firm-analytics/monday-briefing.txt }
pattern: 'Here.s the thing|But here.s|[Ii]t.s not [^.]{0,40}, it.s|delve|pivotal|landscape|game-changer|leverag'
match: not_contains
---
