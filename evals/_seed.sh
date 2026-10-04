#!/usr/bin/env bash
# Seed an eval workspace with the files a person would have in a folder.
# Usage (from a case's fixture.sh): _seed.sh <mode>
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
DATA="$ROOT/sample-data/super-duper-law"
mode="${1:-all}"
mkdir -p exports
case "$mode" in
  all)            cp "$DATA"/*.csv "$DATA"/*.xlsx exports/ ;;
  none)           ;;
  ar-raw)         cp "$DATA/clio-ar-aging-2026-10-04.csv" exports/ ;;
  generic-matters) cp "$DATA/matter-list-export.csv" exports/ ;;
  tiny)           head -1 "$DATA/clio-grow-matter-revenue-report.csv" > exports/leads-this-month.csv
                  tail -32 "$DATA/clio-grow-matter-revenue-report.csv" >> exports/leads-this-month.csv ;;
  quiet)          python3 "$ROOT/tools/generate_sample_data.py" --out exports --no-plants --seed 2 >/dev/null ;;
  *)              echo "unknown mode $mode" >&2; exit 1 ;;
esac
