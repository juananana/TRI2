#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:?model required}"
SPLIT="${2:-dev}"
PARA="${3:-p0}"

python3 -m tri.run_models --model "$MODEL" --mode interactive --split "$SPLIT" --paraphrase "$PARA"
python3 -m tri.run_models --model "$MODEL" --mode direct --split "$SPLIT" --paraphrase "$PARA"
python3 -m tri.run_models --model "$MODEL" --mode compiler --split "$SPLIT" --paraphrase "$PARA"

