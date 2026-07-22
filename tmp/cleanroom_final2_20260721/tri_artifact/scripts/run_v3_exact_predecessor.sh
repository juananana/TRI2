#!/usr/bin/env bash
set -euo pipefail

: "${LLM_API_KEY:?Set LLM_API_KEY before running. The key is intentionally not stored.}"

DATA="data/temporal_referent_v3_language_clusters.jsonl"
MODE="compile_then_act"

run_model() {
  local model="$1"
  local label="$2"
  local smoke="runs/v3_exact_predecessor_${label}_healthcheck.jsonl"
  local full="runs/v3_exact_predecessor_${label}_full.jsonl"

  PYTHONPATH=. python3 -m tri.run_models \
    --model "$model" --mode "$MODE" --data "$DATA" --split all --paraphrase all \
    --temperature 0 --timeout 180 --max-api-retries 1 --retry-backoff 5 \
    --max-tokens 1200 --disable-thinking --limit 4 --output "$smoke"

  PYTHONPATH=. python3 - "$smoke" <<'PY'
import json
import sys

rows = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8") if line.strip()]
failures = sum(row.get("status") != "ok" or row.get("result", {}).get("errors") for row in rows)
if len(rows) != 4 or failures > 1:
    raise SystemExit(f"health check failed: rows={len(rows)}, API/parse failures={failures}")
PY

  PYTHONPATH=. python3 -m tri.run_models \
    --model "$model" --mode "$MODE" --data "$DATA" --split all --paraphrase all \
    --temperature 0 --timeout 180 --max-api-retries 1 --retry-backoff 5 \
    --max-tokens 1200 --disable-thinking --output "$full"
}

run_model "Qwen/Qwen3.5-122B-A10B" "qwen"
run_model "Pro/zai-org/GLM-5.1" "glm"
