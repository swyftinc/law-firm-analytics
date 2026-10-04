---
type: regex
target: { source: file, path: firm-analytics/firm-charts.html }
pattern: '\$30\d,\d{3}|\$30\dK'
match: not_contains
---
