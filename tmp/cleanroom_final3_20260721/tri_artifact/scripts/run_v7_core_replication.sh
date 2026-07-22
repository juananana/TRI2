#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON="$ROOT/../../.venv-toolsandbox/bin/python"
FULL="$ROOT/data/temporal_referent_v7_core_replication.jsonl"
SMOKE="$ROOT/data/temporal_referent_v7_core_replication_smoke.jsonl"

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
  mode=$2
  data=$3
  output=$4
  expected=$5

  if [ -f "$output" ]; then
    rows=$(wc -l < "$output" | tr -d ' ')
    if [ "$rows" = "$expected" ]; then
      printf "Skipping complete %s (%s rows)\n" "$output" "$rows"
      return
    fi
  fi

  "$PYTHON" -m tri.run_models \
    --model "$model" \
    --mode "$mode" \
    --data "$data" \
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

health_gate() {
  "$PYTHON" -c 'import json,sys; paths=sys.argv[1:]; bad=[]
for path in paths:
 rows=[json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
 errors=sum(r.get("status") != "ok" or bool(r.get("result",{}).get("errors")) for r in rows)
 if len(rows) != 12 or errors > 1: bad.append((path,len(rows),errors))
print("health_gate", "pass" if not bad else f"fail: {bad}")
raise SystemExit(bool(bad))' "$@"
}

QWEN="Qwen/Qwen3.5-122B-A10B"
GLM="Pro/zai-org/GLM-5.1"
MODES="generic_structured_ledger_then_act compile_then_act factorized_hybrid_compile_then_act"

qwen_health=""
for mode in $MODES; do
  output="$ROOT/runs/v7_qwen_${mode}_health.jsonl"
  run_one "$QWEN" "$mode" "$SMOKE" "$output" 12
  qwen_health="$qwen_health $output"
done
# shellcheck disable=SC2086
health_gate $qwen_health

for mode in $MODES; do
  run_one "$QWEN" "$mode" "$FULL" "$ROOT/runs/v7_qwen_${mode}_full.jsonl" 240
done

glm_health=""
for mode in $MODES; do
  output="$ROOT/runs/v7_glm_${mode}_health.jsonl"
  run_one "$GLM" "$mode" "$SMOKE" "$output" 12
  glm_health="$glm_health $output"
done
# shellcheck disable=SC2086
health_gate $glm_health

for mode in $MODES; do
  run_one "$GLM" "$mode" "$FULL" "$ROOT/runs/v7_glm_${mode}_full.jsonl" 240
done

"$PYTHON" -m tri.v7_core_report \
  --input \
    "$ROOT/runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl" \
    "$ROOT/runs/v7_qwen_compile_then_act_full.jsonl" \
    "$ROOT/runs/v7_qwen_factorized_hybrid_compile_then_act_full.jsonl" \
    "$ROOT/runs/v7_glm_generic_structured_ledger_then_act_full.jsonl" \
    "$ROOT/runs/v7_glm_compile_then_act_full.jsonl" \
    "$ROOT/runs/v7_glm_factorized_hybrid_compile_then_act_full.jsonl" \
  --pair "$ROOT/runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl" "$ROOT/runs/v7_qwen_compile_then_act_full.jsonl" \
  --pair "$ROOT/runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl" "$ROOT/runs/v7_qwen_factorized_hybrid_compile_then_act_full.jsonl" \
  --pair "$ROOT/runs/v7_glm_generic_structured_ledger_then_act_full.jsonl" "$ROOT/runs/v7_glm_compile_then_act_full.jsonl" \
  --pair "$ROOT/runs/v7_glm_generic_structured_ledger_then_act_full.jsonl" "$ROOT/runs/v7_glm_factorized_hybrid_compile_then_act_full.jsonl" \
  --output "$ROOT/reports/v7_core_replication.json"
