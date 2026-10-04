---
type: regex
target: { source: file, path: firm-analytics/firm-charts.html }
pattern: 'data-direction="lower_better" data-status="red" data-delta="down"'
match: not_contains
---
