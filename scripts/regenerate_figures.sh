#!/usr/bin/env bash
# Regenerate all TRI paper figures from frozen data
# Usage: ./regenerate_figures.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "TRI Figure Regeneration"
echo "======================"
echo ""

# Setup Python environment
if [ ! -d "$PROJECT_ROOT/.fig_venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.fig_venv"
    "$PROJECT_ROOT/.fig_venv/bin/pip" install matplotlib numpy --quiet
fi

echo "Activating environment..."
source "$PROJECT_ROOT/.fig_venv/bin/activate"

# Generate main paper figures
echo ""
echo "Generating main paper figures..."
python "$PROJECT_ROOT/experiments/tri_artifact/scripts/make_new_paper_figures.py"

# Generate supplement figures
echo ""
echo "Generating supplement figures..."
python "$PROJECT_ROOT/experiments/tri_artifact/scripts/make_supplement_figures.py"

echo ""
echo "✓ All figures generated successfully"
echo ""
echo "Output locations:"
echo "  - experiments/tri_artifact/reports/figures/"
echo "  - paper/Figures/"
echo ""
echo "Next steps:"
echo "  1. cd paper"
echo "  2. pdflatex AnonymousSubmission2027.tex"
echo "  3. bibtex AnonymousSubmission2027"
echo "  4. pdflatex AnonymousSubmission2027.tex (2x)"
echo "  5. pdflatex supplementary_material.tex"
