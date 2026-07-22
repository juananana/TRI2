#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON="$ROOT/../../.venv-toolsandbox/bin/python"
DATA="$ROOT/data/temporal_referent_v7_repeat_stability_v1.jsonl"

if [ -z "${LLM_API_KEY:-}" ]; then
  printf "SiliconFlow key: "
  stty -echo
  IFS= read -r LLM_API_KEY
  stty echo
  printf "\n"
  export LLM_API_KEY
fi

export LLM_BASE_URL="${LLM_BASE_URL:-https://api.siliconflow.cn/v1}"
export PYTHONPATH="$ROOT"

run_one() {
  model=$1
  model_label=$2
  mode=$3
  mode_label=$4
  repeat=$5
  output="$ROOT/runs/v7_repeat_${model_label}_${mode_label}_r${repeat}_v1.jsonl"

  if [ -f "$output" ] && [ "$(wc -l < "$output" | tr -d ' ')" = "40" ]; then
    printf "Skipping complete %s\n" "$output"
    return
  fi

  "$PYTHON" -m tri.run_models \
    --model "$model" \
    --mode "$mode" \
    --data "$DATA" \
    --output "$output" \
    --split all \
    --paraphrase all \
    --temperature 0 \
    --timeout 180 \
    --max-api-retries 2 \
    --retry-backoff 5 \
    --max-tokens 1200 \
    --disable-thinking
}

for repeat in 2 3; do
  run_one "Qwen/Qwen3.5-122B-A10B" qwen generic_structured_ledger_then_act generic "$repeat"
  run_one "Qwen/Qwen3.5-122B-A10B" qwen compile_then_act cta "$repeat"
  run_one "Pro/zai-org/GLM-5.1" glm generic_structured_ledger_then_act generic "$repeat"
  run_one "Pro/zai-org/GLM-5.1" glm compile_then_act cta "$repeat"
done
