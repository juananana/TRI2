#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/data/temporal_referent_v3_language_clusters.jsonl"

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY before running." >&2
  exit 1
fi

MODELS=(
  "Qwen/Qwen3.5-122B-A10B"
  "Pro/zai-org/GLM-5.1"
)

for model in "${MODELS[@]}"; do
  safe_model="${model//\//_}"
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  output="$ROOT/runs/${stamp}_${safe_model}_generic_reference_mode_v3_language_clusters.jsonl"
  echo "Running ${model} Generic+reference_mode on frozen TRI-v3 language clusters"
  (
    cd "$ROOT"
    PYTHONPATH=. python3 -m tri.run_models \
      --model "$model" \
      --mode generic_reference_mode_ledger_then_act \
      --split all \
      --paraphrase all \
      --temperature 0.0 \
      --disable-thinking \
      --timeout 180 \
      --max-api-retries 2 \
      --retry-backoff 5 \
      --data "$DATA" \
      --output "$output"
  )
  echo "Completed: $output"
done
