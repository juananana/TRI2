#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob
files=(runs/*v2*.jsonl)
if (( ${#files[@]} == 0 )); then
  echo "No v2 run files found under runs/." >&2
  exit 1
fi

PYTHONPATH=. python3 -m tri.v2_model_report \
  --input "${files[@]}" \
  --output reports/v2_model_report.json
