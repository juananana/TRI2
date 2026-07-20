#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$ARTIFACT_DIR/../.." && pwd)"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv-toolsandbox/bin/python}"
MODEL="${1:-Qwen/Qwen3.5-122B-A10B}"
MODE="${MODE:-health}"
CONTROLLERS="${CONTROLLERS:-full_history}"
DATA="$ARTIFACT_DIR/data/toolsandbox_tri_single_turn_2x2_v1.jsonl"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY in the environment. The key is never stored by this script." >&2
  exit 2
fi
if [[ ! -x "$PYTHON" ]]; then
  echo "Python environment not found at $PYTHON" >&2
  exit 2
fi
if [[ ! -f "$DATA" ]]; then
  echo "Frozen dataset not found at $DATA" >&2
  exit 2
fi
if [[ "$CONTROLLERS" == *,* ]]; then
  echo "Set one controller per run; invoke this script separately for each controller." >&2
  exit 2
fi

case "$MODE" in
  health)
    LIMIT=8
    ;;
  full)
    LIMIT=96
    ;;
  *)
    echo "MODE must be health or full" >&2
    exit 2
    ;;
esac

SAFE_MODEL="${MODEL//\//_}"
OUTPUT="$ARTIFACT_DIR/runs/toolsandbox_tri_single_turn_${SAFE_MODEL}_${CONTROLLERS}_${MODE}_v1.jsonl"

cd "$PROJECT_DIR"
PYTHONPATH="$ARTIFACT_DIR" "$PYTHON" -m external_pilots.toolsandbox_tri.agent_runner \
  --model "$MODEL" \
  --controllers "$CONTROLLERS" \
  --data "$DATA" \
  --output "$OUTPUT" \
  --temperature 0 \
  --timeout 180 \
  --max-api-retries 1 \
  --retry-backoff 5 \
  --max-tokens 700 \
  --limit "$LIMIT"

echo "$OUTPUT"
