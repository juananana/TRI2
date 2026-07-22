#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$ARTIFACT_DIR/../.." && pwd)"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv-toolsandbox/bin/python}"
MODEL="${1:?Usage: $0 MODEL}"
SAFE_MODEL="${MODEL//\//_}"
REPORT_STEM="${2:-toolsandbox_single_turn_matched_generic_${SAFE_MODEL}_full_v1}"
DATA="$ARTIFACT_DIR/data/toolsandbox_tri_single_turn_2x2_v1.jsonl"
HEALTH="$ARTIFACT_DIR/runs/toolsandbox_tri_single_turn_${SAFE_MODEL}_matched_generic_state_observed_health_v1.jsonl"
FULL="$ARTIFACT_DIR/runs/toolsandbox_tri_single_turn_${SAFE_MODEL}_matched_generic_state_observed_full_v1.jsonl"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY in the environment. The key is never stored by this script." >&2
  exit 2
fi

cd "$PROJECT_DIR"
PYTHONPATH="$ARTIFACT_DIR" "$PYTHON" -m external_pilots.toolsandbox_tri.matched_runner \
  --model "$MODEL" --controllers generic --data "$DATA" --output "$HEALTH" \
  --temperature 0 --timeout 180 --max-api-retries 1 --retry-backoff 5 --max-tokens 700 --limit 8
PYTHONPATH="$ARTIFACT_DIR" "$PYTHON" -m tri.toolsandbox_health_gate "$HEALTH"
PYTHONPATH="$ARTIFACT_DIR" "$PYTHON" -m external_pilots.toolsandbox_tri.matched_runner \
  --model "$MODEL" --controllers generic --data "$DATA" --output "$FULL" \
  --temperature 0 --timeout 180 --max-api-retries 1 --retry-backoff 5 --max-tokens 700 --limit 96

cd "$ARTIFACT_DIR"
PYTHONPATH=. "$PYTHON" -m tri.toolsandbox_single_turn_report "$FULL" \
  --json "reports/${REPORT_STEM}.json" \
  --markdown "reports/${REPORT_STEM}.md"
echo "Matched Generic Structured Ledger stage completed and analyzed."
