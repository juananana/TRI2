#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$ARTIFACT_DIR/../.." && pwd)"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv-toolsandbox/bin/python}"
MODEL="${1:?Usage: $0 MODEL CONTROLLER REPORT_STEM}"
CONTROLLER="${2:?Usage: $0 MODEL CONTROLLER REPORT_STEM}"
REPORT_STEM="${3:?Usage: $0 MODEL CONTROLLER REPORT_STEM}"
SAFE_MODEL="${MODEL//\//_}"
HEALTH="$ARTIFACT_DIR/runs/toolsandbox_tri_single_turn_${SAFE_MODEL}_${CONTROLLER}_health_v1.jsonl"
FULL="$ARTIFACT_DIR/runs/toolsandbox_tri_single_turn_${SAFE_MODEL}_${CONTROLLER}_full_v1.jsonl"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY in the environment. The key is never stored by this script." >&2
  exit 2
fi

cd "$PROJECT_DIR"
MODE=health CONTROLLERS="$CONTROLLER" \
  "$SCRIPT_DIR/run_toolsandbox_single_turn_2x2.sh" "$MODEL"

PYTHONPATH="$ARTIFACT_DIR" "$PYTHON" -m tri.toolsandbox_health_gate "$HEALTH"

MODE=full CONTROLLERS="$CONTROLLER" \
  "$SCRIPT_DIR/run_toolsandbox_single_turn_2x2.sh" "$MODEL"

cd "$ARTIFACT_DIR"
PYTHONPATH=. "$PYTHON" -m tri.toolsandbox_single_turn_report "$FULL" \
  --json "reports/${REPORT_STEM}.json" \
  --markdown "reports/${REPORT_STEM}.md"

echo "$MODEL / $CONTROLLER stage completed and analyzed."
