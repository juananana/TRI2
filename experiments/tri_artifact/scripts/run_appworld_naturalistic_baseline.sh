#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$ARTIFACT_DIR/../.." && pwd)"
PYTHON="${PYTHON:-$PROJECT_DIR/.venv-appworld312/bin/python}"
MODEL="${1:-Qwen/Qwen3.5-122B-A10B}"
APP="${APP:-todoist}"
MODE="${MODE:-full}"
RUNTIME="$ARTIFACT_DIR/external_pilots/appworld_runtime"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY in the environment." >&2
  exit 2
fi
case "$APP" in
  todoist) DATA="$ARTIFACT_DIR/data/appworld_tri_todoist_mvp_v1.jsonl" ;;
  simple_note) DATA="$ARTIFACT_DIR/data/appworld_tri_simple_note_mvp_v1.jsonl" ;;
  *) echo "APP must be todoist or simple_note" >&2; exit 2 ;;
esac
case "$MODE" in
  health) LIMIT=2 ;;
  full) LIMIT=8 ;;
  *) echo "MODE must be health or full" >&2; exit 2 ;;
esac
if [[ ! -x "$PYTHON" || ! -d "$RUNTIME/data/tasks/82e2fac_1" ]]; then
  echo "AppWorld runtime is not installed." >&2
  exit 2
fi

SAFE_MODEL="${MODEL//\//_}"
OUTPUT="$ARTIFACT_DIR/runs/appworld_naturalistic_${APP}_${SAFE_MODEL}_full_v1.jsonl"

cd "$PROJECT_DIR"
HOME="$RUNTIME/home" \
APPWORLD_ROOT="$RUNTIME" \
PYTHONPATH="$ARTIFACT_DIR" \
"$PYTHON" -m external_pilots.appworld_tri.naturalistic_agent_runner \
  --app "$APP" \
  --model "$MODEL" \
  --data "$DATA" \
  --output "$OUTPUT" \
  --temperature 0 \
  --timeout 180 \
  --max-api-retries 1 \
  --retry-backoff 5 \
  --max-tokens 500 \
  --limit "$LIMIT"

echo "$OUTPUT"
