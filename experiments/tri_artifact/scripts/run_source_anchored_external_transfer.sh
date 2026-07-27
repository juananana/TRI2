#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/../../.venv-toolsandbox/bin/python}"
FULL_AFTER_SMOKE=false
if [[ "${1:-}" == "--full-after-smoke" ]]; then
  FULL_AFTER_SMOKE=true
fi

if [[ -z "${SILICONFLOW_API_KEY:-${LLM_API_KEY:-}}" ]]; then
  printf "SiliconFlow key: "
  stty -echo
  IFS= read -r SILICONFLOW_API_KEY
  stty echo
  printf "\n"
  export SILICONFLOW_API_KEY
fi

cd "$ROOT"
PYTHONPATH=. "$PYTHON" scripts/build_source_anchored_external_transfer.py

ZERO_API_GATE="$($PYTHON -c 'import json,sys; print(json.load(open(sys.argv[1]))["gate"])' \
  reports/source_anchored_external_transfer_zero_api_v1.json)"
if [[ "$ZERO_API_GATE" != "GO" ]]; then
  printf "Zero-API gate is %s; model run stopped.\n" "$ZERO_API_GATE"
  exit 1
fi

RUN_OUTPUT="runs/source_anchored_external_transfer_siliconflow_v1.jsonl"
SMOKE_JSON="reports/source_anchored_external_transfer_smoke_v1.json"
SMOKE_MD="reports/source_anchored_external_transfer_smoke_v1.md"
REPAIRED_OUTPUT="runs/source_anchored_external_transfer_siliconflow_repaired_v1.jsonl"
if [[ -f "$REPAIRED_OUTPUT" ]]; then
  RUN_OUTPUT="$REPAIRED_OUTPUT"
  SMOKE_JSON="reports/source_anchored_external_transfer_smoke_repaired_v1.json"
  SMOKE_MD="reports/source_anchored_external_transfer_smoke_repaired_v1.md"
fi

PYTHONPATH=. "$PYTHON" scripts/run_source_anchored_external_transfer.py --smoke --output "$RUN_OUTPUT"
PYTHONPATH=. "$PYTHON" scripts/report_source_anchored_external_transfer.py --smoke \
  --input "$RUN_OUTPUT" --report-json "$SMOKE_JSON" --report-md "$SMOKE_MD"

SMOKE_GATE="$($PYTHON -c 'import json,sys; print(json.load(open(sys.argv[1]))["smoke_gate"])' \
  "$SMOKE_JSON")"
if [[ "$SMOKE_GATE" != "GO" ]]; then
  printf "Smoke gate is %s; full run stopped.\n" "$SMOKE_GATE"
  exit 1
fi

if [[ "$FULL_AFTER_SMOKE" != true ]]; then
  printf "Smoke gate is GO; full run was not requested.\n"
  exit 0
fi

PYTHONPATH=. "$PYTHON" scripts/run_source_anchored_external_transfer.py --output "$RUN_OUTPUT"
PYTHONPATH=. "$PYTHON" scripts/report_source_anchored_external_transfer.py --input "$RUN_OUTPUT"
