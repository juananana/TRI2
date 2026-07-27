#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/../../.venv-toolsandbox/bin/python}"

if [[ -z "${SILICONFLOW_API_KEY:-${LLM_API_KEY:-}}" ]]; then
  printf "SiliconFlow key: "
  stty -echo
  IFS= read -r SILICONFLOW_API_KEY
  stty echo
  printf "\n"
  export SILICONFLOW_API_KEY
fi

cd "$ROOT"
PYTHONPATH=. "$PYTHON" scripts/run_external_public_annotation.py --smoke --retry-failed-transport
PYTHONPATH=. "$PYTHON" scripts/report_external_public_annotation.py --smoke \
  --report-json reports/external_public_annotation_smoke_v1.json \
  --report-md reports/external_public_annotation_smoke_v1.md
PYTHONPATH=. "$PYTHON" scripts/run_external_public_annotation.py --retry-failed-transport
PYTHONPATH=. "$PYTHON" scripts/report_external_public_annotation.py
