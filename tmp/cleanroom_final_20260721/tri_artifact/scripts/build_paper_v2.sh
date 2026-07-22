#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SUBMISSION_DIR="${PROJECT_ROOT}/outputs/aaai_submission"
TEX_NAME="tri_aaai2027_submission_v2"

cd "${SUBMISSION_DIR}"

if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error "${TEX_NAME}.tex"
elif command -v pdflatex >/dev/null 2>&1 && command -v bibtex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error "${TEX_NAME}.tex"
  bibtex "${TEX_NAME}"
  pdflatex -interaction=nonstopmode -halt-on-error "${TEX_NAME}.tex"
  pdflatex -interaction=nonstopmode -halt-on-error "${TEX_NAME}.tex"
else
  echo "TeX Live is not available on PATH. Install it or open a shell where pdflatex is available." >&2
  exit 1
fi

echo "${SUBMISSION_DIR}/${TEX_NAME}.pdf"
