#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 BASE_RUN_JSONL MODEL MODE" >&2
  echo "Example: $0 runs/base.jsonl Qwen/Qwen3.5-397B-A17B compile_then_act" >&2
  exit 1
fi

if [[ -z "${LLM_API_KEY:-}" ]]; then
  echo "Set LLM_API_KEY before running. The key is intentionally not stored in this script." >&2
  exit 1
fi

BASE_RUN="$1"
MODEL="$2"
MODE="$3"
DATA="data/temporal_referent_v2_api_scalar.jsonl"
export LLM_BASE_URL="${LLM_BASE_URL:-https://api.siliconflow.cn/v1}"

safe_model="${MODEL//\//_}"
safe_model="${safe_model//:/_}"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
retry_data="data/${stamp}_${safe_model}_${MODE}_api_retry_subset.jsonl"
retry_run="runs/${stamp}_${safe_model}_${MODE}_api_retry.jsonl"
merged_run="runs/${stamp}_${safe_model}_${MODE}_merged_retry.jsonl"

PYTHONPATH=. python3 -m tri.v2_retry_subset \
  --data "${DATA}" \
  --run "${BASE_RUN}" \
  --output "${retry_data}" \
  --failure api

PYTHONPATH=. python3 -m tri.run_models \
  --model "${MODEL}" \
  --mode "${MODE}" \
  --split dev \
  --paraphrase all \
  --condition all \
  --data "${retry_data}" \
  --output "${retry_run}" \
  --temperature 0.0 \
  --timeout 120

PYTHONPATH=. python3 -m tri.v2_merge_retry \
  --base "${BASE_RUN}" \
  --retry "${retry_run}" \
  --output "${merged_run}"

echo "${merged_run}"
