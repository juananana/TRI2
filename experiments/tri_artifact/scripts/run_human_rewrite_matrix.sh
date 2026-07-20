#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA="$ROOT/data/temporal_referent_human_rewrites_v1.jsonl"
RUNS="$ROOT/runs"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LIMIT="${LIMIT:-}"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY in the environment. The key is never stored by this script." >&2
  exit 2
fi

if [[ ! -f "$DATA" ]]; then
  echo "Missing frozen data: $DATA" >&2
  exit 2
fi

mkdir -p "$RUNS"

models=(
  "Qwen/Qwen3.5-122B-A10B"
  "Pro/zai-org/GLM-5.1"
)
modes=(
  "generic_structured_ledger_then_act"
  "compile_then_act"
  "factorized_schema_compile_then_act"
  "factorized_hybrid_compile_then_act"
)

limit_args=()
if [[ -n "$LIMIT" ]]; then
  limit_args=(--limit "$LIMIT")
fi

for model in "${models[@]}"; do
  model_slug="${model//\//_}"
  for mode in "${modes[@]}"; do
    timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
    output="$RUNS/${timestamp}_${model_slug}_${mode}_human_rewrites_v1.jsonl"
    echo "Running $model / $mode -> $output"
    "$PYTHON_BIN" "$ROOT/tri/run_models.py" \
      --model "$model" \
      --mode "$mode" \
      --split all \
      --paraphrase all \
      --data "$DATA" \
      --output "$output" \
      --temperature 0.0 \
      --timeout 180 \
      --max-api-retries 1 \
      --retry-backoff 5 \
      --max-tokens 1200 \
      --disable-thinking \
      ${limit_args[@]+"${limit_args[@]}"}

    expected_rows="${LIMIT:-50}"
    actual_rows="$(awk 'END { print NR + 0 }' "$output")"
    if [[ "$actual_rows" -ne "$expected_rows" ]]; then
      echo "Incomplete run: expected $expected_rows rows, found $actual_rows in $output" >&2
      exit 3
    fi
  done
done
