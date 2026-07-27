#!/bin/bash
# Generate all high-density figures for TRI paper submission

set -e

echo "===================================="
echo "Generating TRI Paper Figures"
echo "===================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Create output directory
mkdir -p reports/figures

echo "[1/3] Generating comprehensive analysis figure..."
python scripts/make_comprehensive_figures.py --output-dir reports/figures
echo "✓ Complete"
echo ""

echo "[2/3] Generating high-density results figures..."
python scripts/make_high_density_results_figures.py --output-dir reports/figures
echo "✓ Complete"
echo ""

echo "[3/3] Generating mechanism flow diagrams..."
python scripts/make_mechanism_flow_figures.py --output-dir reports/figures
echo "✓ Complete"
echo ""

echo "===================================="
echo "All figures generated successfully!"
echo "===================================="
echo ""
echo "Generated files:"
echo "  - tri_comprehensive_analysis.pdf"
echo "  - tri_new_schema_comprehensive.pdf"
echo "  - tri_policy_identifiability_comprehensive.pdf"
echo "  - tri_temporal_flow_comprehensive.pdf"
echo "  - tri_controller_architectures.pdf"
echo ""
echo "Output directory: reports/figures/"
