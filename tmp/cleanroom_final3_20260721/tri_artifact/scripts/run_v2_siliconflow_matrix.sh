#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY before running. The key is intentionally not stored in this script." >&2
  exit 1
fi

export LLM_BASE_URL="${LLM_BASE_URL:-https://api.siliconflow.cn/v1}"

DATA="data/temporal_referent_v2_api_scalar.jsonl"
MODELS=(
  "Pro/zai-org/GLM-5.1"
  "Qwen/Qwen3.5-397B-A17B"
  "Pro/MiniMaxAI/MiniMax-M2.5"
)
MODES=(
  "state_overwrite_once"
  "compile_then_act"
)

for model in "${MODELS[@]}"; do
  for mode in "${MODES[@]}"; do
    safe_model="${model//\//_}"
    safe_model="${safe_model//:/_}"
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    output="runs/${stamp}_${safe_model}_${mode}_v2_scalar.jsonl"
    echo "Running ${model} ${mode} on TRI-v2 scalar API subset"
    PYTHONPATH=. python3 -m tri.run_models \
      --model "${model}" \
      --mode "${mode}" \
      --split dev \
      --paraphrase all \
      --condition all \
      --data "${DATA}" \
      --output "${output}" \
      --temperature 0.0 \
      --timeout 90
  done
done
