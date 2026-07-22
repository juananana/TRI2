#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$ARTIFACT_DIR/../.." && pwd)"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv-toolsandbox/bin/python}"
MODEL="Pro/zai-org/GLM-5.1"
SAFE_MODEL="Pro_zai-org_GLM-5.1"
HEALTH="$ARTIFACT_DIR/runs/toolsandbox_tri_single_turn_${SAFE_MODEL}_full_history_health_v1.jsonl"
FULL="$ARTIFACT_DIR/runs/toolsandbox_tri_single_turn_${SAFE_MODEL}_full_history_full_v1.jsonl"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY in the environment. The key is never stored by this script." >&2
  exit 2
fi

cd "$PROJECT_DIR"
MODE=health CONTROLLERS=full_history \
  "$SCRIPT_DIR/run_toolsandbox_single_turn_2x2.sh" "$MODEL"

PYTHONPATH="$ARTIFACT_DIR" "$PYTHON" -m tri.toolsandbox_health_gate "$HEALTH"

MODE=full CONTROLLERS=full_history \
  "$SCRIPT_DIR/run_toolsandbox_single_turn_2x2.sh" "$MODEL"

cd "$ARTIFACT_DIR"
PYTHONPATH=. "$PYTHON" -m tri.toolsandbox_single_turn_report "$FULL" \
  --json reports/toolsandbox_single_turn_glm_full_history_full_v1.json \
  --markdown reports/toolsandbox_single_turn_glm_full_history_full_v1.md

echo "GLM full-history stage completed and analyzed."
