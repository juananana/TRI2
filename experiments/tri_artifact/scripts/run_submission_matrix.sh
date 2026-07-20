#!/usr/bin/env bash
set -euo pipefail

# Run from supplement/tri_artifact after exporting LLM_API_KEY.

MODELS=(
  "Pro/zai-org/GLM-5.1"
  "Qwen/Qwen3.5-397B-A17B"
  "deepseek-ai/DeepSeek-V4-Pro"
  "Pro/MiniMaxAI/MiniMax-M2.5"
)

DOMAINS_DEV="incident,meeting,ticket,repo,shipment,experiment"
DOMAINS_HELDOUT="invoice,device,patient,dataset"

echo "[1/5] Main all-paraphrase dev anchored-flip"
python3 scripts/run_silicon_batch.py \
  --models "${MODELS[@]}" \
  --modes state_overwrite_once \
  --split dev \
  --paraphrase all \
  --condition anchored-flip \
  --domains "$DOMAINS_DEV" \
  --timeout 90

echo "[2/5] Main all-paraphrase dev dynamic-flip"
python3 scripts/run_silicon_batch.py \
  --models "${MODELS[@]}" \
  --modes state_overwrite_once \
  --split dev \
  --paraphrase all \
  --condition dynamic-flip \
  --domains "$DOMAINS_DEV" \
  --timeout 90

echo "[3/5] Heldout anchored-flip and dynamic-flip"
python3 scripts/run_silicon_batch.py \
  --models "${MODELS[@]}" \
  --modes state_overwrite_once \
  --split heldout \
  --paraphrase all \
  --condition anchored-flip \
  --domains "$DOMAINS_HELDOUT" \
  --timeout 90

python3 scripts/run_silicon_batch.py \
  --models "${MODELS[@]}" \
  --modes state_overwrite_once \
  --split heldout \
  --paraphrase all \
  --condition dynamic-flip \
  --domains "$DOMAINS_HELDOUT" \
  --timeout 90

echo "[4/5] Compiler controls on GLM"
python3 scripts/run_silicon_batch.py \
  --models "Pro/zai-org/GLM-5.1" \
  --modes compile_then_act compressed_memory natural_memory ledger_safe \
  --split dev \
  --paraphrase all \
  --condition anchored-flip \
  --domains "incident,meeting,ticket" \
  --timeout 90

python3 scripts/run_silicon_batch.py \
  --models "Pro/zai-org/GLM-5.1" \
  --modes compile_then_act compressed_memory \
  --split dev \
  --paraphrase all \
  --condition dynamic-flip \
  --domains "incident,meeting,ticket" \
  --timeout 90

python3 scripts/run_silicon_batch.py \
  --models "Pro/zai-org/GLM-5.1" \
  --modes compile_then_act ledger_safe natural_memory \
  --split dev \
  --paraphrase all \
  --condition anchored-removed \
  --domains "incident,meeting,ticket" \
  --timeout 90

python3 scripts/run_silicon_batch.py \
  --models "Pro/zai-org/GLM-5.1" \
  --modes summary_controller lossy_summary_controller \
  --split dev \
  --paraphrase all \
  --condition anchored-flip \
  --domains "incident,meeting,ticket" \
  --timeout 90

python3 scripts/run_silicon_batch.py \
  --models "Pro/zai-org/GLM-5.1" \
  --modes summary_controller lossy_summary_controller \
  --split dev \
  --paraphrase all \
  --condition dynamic-flip \
  --domains "incident,meeting,ticket" \
  --timeout 90

echo "[5/5] Summarize field ablation"
python3 -m tri.field_ablation --output reports/field_ablation.json

echo "Done. Re-run paper_tables over selected run files after checking for API timeouts."
