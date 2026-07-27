"""
Redesigned high-quality results figures for TRI paper.
- Clean 3-color palette inspired by top conferences
- Proper AAAI font sizing (9-10pt body text in figures)
- Innovative layouts with clear visual hierarchy
- Focus on key results with appropriate density
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np

# Professional 3-color palette inspired by Nature/Science publications
# Primary: Deep teal (main results)
# Secondary: Warm terracotta (comparisons/highlights)
# Neutral: Charcoal gray (baselines/context)
TEAL = '#2A7B7E'
TERRACOTTA = '#C96D5A'
CHARCOAL = '#3D4852'
LIGHT_TEAL = '#E8F4F4'
LIGHT_TERRA = '#F9EBE8'
LIGHT_GRAY = '#F5F6F7'
GRID_COLOR = '#E0E3E6'

# AAAI spec: Times for text, figure fonts should be 9-10pt for body text
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
    'font.size': 9,
    'axes.labelsize': 9,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.titlesize': 10,
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.5,
    'patch.linewidth': 0.8,
})


def load_ablation_data(path: Path) -> dict:
    """Load call-matched ablation data."""
    return json.loads(path.read_text(encoding='utf-8'))


def create_main_results_figure(output_path: Path, ablation_data: dict) -> None:
    """
    Main results figure with 3 focused panels:
    - Panel A: Decision visibility impact (before/after comparison)
    - Panel B: Substitution elimination (dramatic drop visualization)
    - Panel C: Model consistency (cross-model validation)
    """
    fig = plt.figure(figsize=(7.2, 3.2))
    gs = GridSpec(1, 3, figure=fig, wspace=0.32,
                  left=0.08, right=0.98, top=0.88, bottom=0.18)

    models_data = ablation_data['models']

    # Panel A: Before/After Decision Visibility
    ax_a = fig.add_subplot(gs[0, 0])
    plot_decision_impact(ax_a, models_data)
    ax_a.text(-0.18, 1.08, 'A', transform=ax_a.transAxes,
              fontsize=12, fontweight='bold', va='top', family='serif')

    # Panel B: Substitution Elimination
    ax_b = fig.add_subplot(gs[0, 1])
    plot_substitution_drop(ax_b, models_data)
    ax_b.text(-0.18, 1.08, 'B', transform=ax_b.transAxes,
              fontsize=12, fontweight='bold', va='top', family='serif')

    # Panel C: Cross-Model Consistency
    ax_c = fig.add_subplot(gs[0, 2])
    plot_model_consistency(ax_c, models_data)
    ax_c.text(-0.18, 1.08, 'C', transform=ax_c.transAxes,
              fontsize=12, fontweight='bold', va='top', family='serif')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created main results figure: {output_path}")


def plot_decision_impact(ax, models_data):
    """Clean before/after comparison with connected arrows."""
    models = [m['model'].split('/')[-1] for m in models_data]

    baseline = [m['metrics']['history_only']['changed_pairacc']['rate'] * 100
                for m in models_data]
    visible = [m['metrics']['decision_visible']['changed_pairacc']['rate'] * 100
               for m in models_data]

    x = np.arange(len(models))
    width = 0.28

    # Before bars (lighter)
    bars1 = ax.bar(x - width/2, baseline, width,
                   label='History Only',
                   color=LIGHT_GRAY, edgecolor=CHARCOAL,
                   linewidth=1.2, zorder=3)

    # After bars (primary color)
    bars2 = ax.bar(x + width/2, visible, width,
                   label='Decision Visible',
                   color=TEAL, edgecolor=TEAL,
                   linewidth=1.2, zorder=3)

    # Improvement arrows
    for i, (b, v) in enumerate(zip(baseline, visible)):
        if v > b + 5:
            ax.annotate('', xy=(i + width/2, v - 3),
                       xytext=(i - width/2 + 0.05, b + 3),
                       arrowprops=dict(arrowstyle='->', lw=1.8,
                                     color=TEAL, alpha=0.7))
            # Gain label
            gain = v - b
            ax.text(i, max(b, v) + 4, f'+{gain:.0f}pp',
                   ha='center', fontsize=8, fontweight='bold',
                   color=TEAL)

    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                   f'{height:.0f}',
                   ha='center', va='bottom', fontsize=8)

    ax.set_ylabel('Changed-Pair Accuracy (%)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 75)
    ax.legend(loc='upper left', frameon=True, framealpha=0.95)
    ax.grid(axis='y', alpha=0.3, linestyle='--', color=GRID_COLOR, zorder=0)
    ax.set_title('Decision Visibility Impact', fontweight='bold', pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_substitution_drop(ax, models_data):
    """Waterfall-style visualization of substitution elimination."""
    models = [m['model'].split('/')[-1] for m in models_data]

    hist_subs = [m['metrics']['history_only']['preserve_conditional_substitution']['rate'] * 100
                 for m in models_data]
    vis_subs = [m['metrics']['decision_visible']['preserve_conditional_substitution']['rate'] * 100
                for m in models_data]

    x = np.arange(len(models))

    # Starting level (history only) - terracotta for problems
    ax.bar(x, hist_subs, width=0.6,
           color=TERRACOTTA, alpha=0.7,
           edgecolor=TERRACOTTA, linewidth=1.2,
           label='History Only', zorder=3)

    # Overlay final level (decision visible) - teal for solution
    ax.bar(x, vis_subs, width=0.6,
           color=TEAL, alpha=0.9,
           edgecolor=TEAL, linewidth=1.2,
           label='Decision Visible', zorder=4)

    # Reduction annotations with dramatic styling
    for i, (h, v) in enumerate(zip(hist_subs, vis_subs)):
        drop = h - v
        if drop > 10:
            # Vertical drop line
            ax.plot([i, i], [v, h], 'k--', linewidth=1.5, alpha=0.4, zorder=2)

            # Drop amount
            mid_y = (h + v) / 2
            ax.text(i + 0.35, mid_y, f'↓{drop:.0f}pp',
                   fontsize=9, fontweight='bold',
                   color=TEAL, rotation=0,
                   bbox=dict(boxstyle='round,pad=0.3',
                           facecolor='white',
                           edgecolor=TEAL, linewidth=1))

    ax.set_ylabel('Substitution Rate (%)', fontweight='bold')
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 70)
    ax.legend(loc='upper right', frameon=True, framealpha=0.95)
    ax.grid(axis='y', alpha=0.3, linestyle='--', color=GRID_COLOR, zorder=0)
    ax.set_title('Substitution Elimination', fontweight='bold', pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_model_consistency(ax, models_data):
    """Scatter plot showing consistent improvement across models."""
    models = [m['model'].split('/')[-1] for m in models_data]

    baseline_pair = [m['metrics']['history_only']['changed_pairacc']['rate'] * 100
                     for m in models_data]
    visible_pair = [m['metrics']['decision_visible']['changed_pairacc']['rate'] * 100
                    for m in models_data]

    baseline_sub = [m['metrics']['history_only']['preserve_conditional_substitution']['rate'] * 100
                    for m in models_data]
    visible_sub = [m['metrics']['decision_visible']['preserve_conditional_substitution']['rate'] * 100
                   for m in models_data]

    # Diagonal reference line (no improvement)
    ax.plot([0, 70], [0, 70], 'k--', linewidth=1, alpha=0.3, zorder=1)

    # Scatter points with model-specific markers
    markers = ['o', 's']
    for i, model in enumerate(models):
        # PairAcc improvement
        ax.scatter(baseline_pair[i], visible_pair[i],
                  s=180, marker=markers[i],
                  color=TEAL, edgecolor='white', linewidth=2,
                  zorder=5, label=f'{model} PairAcc')

        # Connection line
        ax.plot([baseline_pair[i], baseline_pair[i]],
               [baseline_pair[i], visible_pair[i]],
               color=TEAL, linewidth=2, alpha=0.6, zorder=3)

        # Model label
        ax.text(baseline_pair[i] - 2, visible_pair[i] + 2, model,
               fontsize=8, ha='right', style='italic')

    # Shading for improvement region
    ax.fill_between([0, 70], [0, 70], [70, 70],
                    color=LIGHT_TEAL, alpha=0.3, zorder=0)
    ax.text(58, 62, 'Improvement\nRegion',
           fontsize=8, ha='center', color=TEAL, style='italic')

    ax.set_xlabel('Baseline Performance (%)', fontweight='bold')
    ax.set_ylabel('With Decision Visible (%)', fontweight='bold')
    ax.set_xlim(15, 65)
    ax.set_ylim(15, 65)
    ax.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=7)
    ax.grid(True, alpha=0.3, linestyle='--', color=GRID_COLOR, zorder=0)
    ax.set_title('Cross-Model Consistency', fontweight='bold', pad=8)
    ax.set_aspect('equal')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def create_schema_transfer_figure(output_path: Path) -> None:
    """
    Schema transfer results with clean 2-panel layout:
    - Panel A: Wrong-entity writes cascade (stacked+line)
    - Panel B: Accuracy trade-off space
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    fig.subplots_adjust(wspace=0.35, left=0.09, right=0.98, top=0.88, bottom=0.18)

    # Mock data - replace with actual
    models = ['Qwen', 'GLM', 'DeepSeek']
    generic_subs = np.array([43, 38, 59])
    generic_total = np.array([72, 80, 79])
    generic_correct = generic_total - generic_subs
    cta_total = np.array([71, 70, 70])

    generic_acc = np.array([47.5, 70.0, 73.8])
    cta_acc = np.array([70.8, 94.2, 91.2])

    # Panel A
    plot_substitution_cascade(axes[0], models, generic_subs, generic_correct,
                             cta_total, generic_acc, cta_acc)
    axes[0].text(-0.18, 1.08, 'A', transform=axes[0].transAxes,
                fontsize=12, fontweight='bold', va='top', family='serif')

    # Panel B
    plot_accuracy_space(axes[1], models, generic_acc, cta_acc,
                       generic_subs / generic_total * 100)
    axes[1].text(-0.18, 1.08, 'B', transform=axes[1].transAxes,
                fontsize=12, fontweight='bold', va='top', family='serif')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created schema transfer figure: {output_path}")


def plot_substitution_cascade(ax, models, subs, correct, cta_total, gen_acc, cta_acc):
    """Horizontal stacked bars showing substitution problem."""
    y = np.arange(len(models))
    height = 0.35

    # Generic: substituted (bad) + correct
    ax.barh(y - height/2, subs, height,
           label='Generic: Substituted',
           color=TERRACOTTA, edgecolor='white', linewidth=1.5, zorder=3)
    ax.barh(y - height/2, correct, height, left=subs,
           label='Generic: Correct',
           color=LIGHT_GRAY, edgecolor='white', linewidth=1.5, zorder=3)

    # CTA: all correct
    ax.barh(y + height/2, cta_total, height,
           label='CTA: Correct',
           color=TEAL, edgecolor='white', linewidth=1.5, zorder=3)

    # Annotations
    for i, (sub, tot) in enumerate(zip(subs, subs + correct)):
        # Generic substitution rate
        rate = sub / tot * 100
        ax.text(sub/2, i - height/2, f'{sub}/{int(tot)}',
               ha='center', va='center', fontsize=8,
               fontweight='bold', color='white')
        if rate > 30:
            ax.text(tot + 2, i - height/2, f'{rate:.0f}%',
                   va='center', fontsize=8, color=TERRACOTTA, fontweight='bold')

    for i, ct in enumerate(cta_total):
        ax.text(ct/2, i + height/2, f'0/{ct}',
               ha='center', va='center', fontsize=8,
               fontweight='bold', color='white')

    ax.set_yticks(y)
    ax.set_yticklabels(models)
    ax.set_xlabel('Eligible Cases', fontweight='bold')
    ax.set_xlim(0, max(subs + correct) * 1.12)
    ax.legend(loc='lower right', frameon=True, framealpha=0.95, fontsize=7)
    ax.grid(axis='x', alpha=0.3, linestyle='--', color=GRID_COLOR, zorder=0)
    ax.set_title('Substitution After Correct Binding', fontweight='bold', pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_accuracy_space(ax, models, generic_acc, cta_acc, sub_rates):
    """2D space showing accuracy vs substitution trade-off."""
    # Ideal region (high accuracy, low substitution)
    ax.axhspan(85, 100, alpha=0.15, color=TEAL, zorder=0)
    ax.text(68, 92, 'High Accuracy\nZero Substitution',
           fontsize=8, ha='center', style='italic', color=TEAL)

    colors_list = [TERRACOTTA, CHARCOAL, CHARCOAL]

    for i, model in enumerate(models):
        # Generic (problematic)
        ax.scatter(sub_rates[i], generic_acc[i], s=200,
                  marker='X', color=colors_list[i],
                  edgecolor='white', linewidth=2,
                  alpha=0.7, zorder=4)

        # CTA (solution)
        ax.scatter(0, cta_acc[i], s=200,
                  marker='o', color=TEAL,
                  edgecolor='white', linewidth=2,
                  zorder=5)

        # Improvement arrow
        ax.annotate('', xy=(1, cta_acc[i]),
                   xytext=(sub_rates[i] - 2, generic_acc[i]),
                   arrowprops=dict(arrowstyle='->', lw=2.5,
                                 color=TEAL, alpha=0.6))

        # Labels
        ax.text(sub_rates[i] + 2, generic_acc[i], f'{model}\nGeneric',
               fontsize=7, ha='left', va='center')
        if i == 1:  # Label CTA once
            ax.text(2, cta_acc[i] + 2, f'{model}\nCTA',
                   fontsize=7, ha='left', va='bottom', color=TEAL,
                   fontweight='bold')

    ax.set_xlabel('Substitution Rate (%)', fontweight='bold')
    ax.set_ylabel('End-to-End Accuracy (%)', fontweight='bold')
    ax.set_xlim(-5, 85)
    ax.set_ylim(40, 100)
    ax.grid(True, alpha=0.3, linestyle='--', color=GRID_COLOR, zorder=0)
    ax.set_title('Accuracy-Substitution Trade-off', fontweight='bold', pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def main():
    parser = argparse.ArgumentParser(description='Generate refined TRI results figures')
    parser.add_argument('--ablation-data', type=Path,
                       default=Path('reports/call_matched_authorization_ablation_v2.json'))
    parser.add_argument('--output-dir', type=Path,
                       default=Path('reports/figures'))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    ablation_data = load_ablation_data(args.ablation_data)

    # Create refined figures
    create_main_results_figure(
        args.output_dir / 'tri_results_clean.pdf', ablation_data)

    create_schema_transfer_figure(
        args.output_dir / 'tri_schema_transfer_clean.pdf')

    print("\n✓ All refined figures generated successfully!")
    print("\nKey improvements:")
    print("  • Clean 3-color palette (Teal, Terracotta, Charcoal)")
    print("  • AAAI-compliant font sizing (9-10pt)")
    print("  • Focused panels with clear visual hierarchy")
    print("  • Innovative layouts (waterfall, connected scatter)")


if __name__ == '__main__':
    main()
