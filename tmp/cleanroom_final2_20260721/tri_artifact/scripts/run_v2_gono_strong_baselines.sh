#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY before running. The key is intentionally not stored in this script." >&2
  exit 1
fi

MODEL="${MODEL:-Pro/zai-org/GLM-5.1}"
DATA="${DATA:-data/temporal_referent_v2_api_scalar.jsonl}"

export LLM_BASE_URL="${LLM_BASE_URL:-https://api.siliconflow.cn/v1}"

MODES=(
  "state_overwrite_once"
  "full_history_once"
  "generic_plan_then_act"
  "compile_then_act"
  "schema_compile_then_act"
)

safe_model="${MODEL//\//_}"
safe_model="${safe_model//:/_}"

for mode in "${MODES[@]}"; do
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  output="runs/${stamp}_${safe_model}_${mode}_v2_gono.jsonl"
  echo "Running ${MODEL} ${mode} on TRI-v2 Go/No-Go matrix"
  if [[ -n "${LIMIT:-}" ]]; then
    PYTHONPATH=. python3 -m tri.run_models \
      --model "${MODEL}" \
      --mode "${mode}" \
      --split dev \
      --paraphrase all \
      --condition all \
      --data "${DATA}" \
      --output "${output}" \
      --temperature 0.0 \
      --timeout 120 \
      --limit "${LIMIT}"
  else
    PYTHONPATH=. python3 -m tri.run_models \
      --model "${MODEL}" \
      --mode "${mode}" \
      --split dev \
      --paraphrase all \
      --condition all \
      --data "${DATA}" \
      --output "${output}" \
      --temperature 0.0 \
      --timeout 120
  fi
done
