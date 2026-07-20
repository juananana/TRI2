#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$ARTIFACT_DIR/../.." && pwd)"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv-appworld312/bin/python}"
MODEL="${1:-Qwen/Qwen3.5-122B-A10B}"
MODE="${MODE:-full}"
DATA="$ARTIFACT_DIR/data/appworld_tri_simple_note_mvp_v1.jsonl"
RUNTIME="$ARTIFACT_DIR/external_pilots/appworld_runtime"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY in the environment. The key is never stored by this script." >&2
  exit 2
fi
if [[ ! -x "$PYTHON" ]]; then
  echo "AppWorld Python environment missing at $PYTHON" >&2
  exit 2
fi
if [[ ! -d "$RUNTIME/data/tasks/82e2fac_1" ]]; then
  echo "AppWorld data is not installed at $RUNTIME" >&2
  exit 2
fi

case "$MODE" in
  health) LIMIT=2 ;;
  full) LIMIT=8 ;;
  *) echo "MODE must be health or full" >&2; exit 2 ;;
esac

SAFE_MODEL="${MODEL//\//_}"
OUTPUT="$ARTIFACT_DIR/runs/appworld_tri_simple_note_${SAFE_MODEL}_full_history_${MODE}_v1.jsonl"

cd "$PROJECT_DIR"
HOME="$RUNTIME/home" \
APPWORLD_ROOT="$RUNTIME" \
PYTHONPATH="$ARTIFACT_DIR" \
"$PYTHON" -m external_pilots.appworld_tri.simple_note_agent_runner \
  --model "$MODEL" \
  --data "$DATA" \
  --output "$OUTPUT" \
  --temperature 0 \
  --timeout 180 \
  --max-api-retries 1 \
  --retry-backoff 5 \
  --max-tokens 700 \
  --limit "$LIMIT"

echo "$OUTPUT"
