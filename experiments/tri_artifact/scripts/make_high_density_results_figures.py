"""
High-density results figures for TRI paper.
Combines multiple result dimensions in publication-ready visualizations.
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
from matplotlib.patches import Rectangle, FancyBboxPatch

# Publication style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.linewidth'] = 0.8

COLORS = {
    'qwen': '#B64926',
    'glm': '#126F66',
    'deepseek': '#7A8793',
    'generic': '#AAB2BA',
    'cta': '#126F66',
    'lifecycle_free': '#69B7AA',
    'lifecycle_gate': '#126F66',
    'lock': '#65717C',
    'reeval': '#7A8793',
}


def create_new_schema_consequence_figure(output_path: Path) -> None:
    """
    Multi-panel figure showing new schema replication results:
    - Panel A: Wrong-entity writes by model/controller
    - Panel B: Substitution cascade visualization
    - Panel C: Accuracy vs substitution trade-off
    """
    fig = plt.figure(figsize=(7.2, 6))
    gs = GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3,
                  left=0.09, right=0.97, top=0.95, bottom=0.08)

    # Mock data - replace with actual data loading
    models = ['Qwen', 'GLM', 'DeepSeek']
    generic_subs = [43, 38, 59]
    generic_total = [72, 80, 79]
    cta_subs = [0, 0, 0]
    cta_total = [71, 70, 70]

    generic_acc = [47.5, 70.0, 73.8]
    cta_acc = [70.8, 94.2, 91.2]

    generic_writes = [44, 38, 60]
    cta_writes = [8, 14, 17]

    # Panel A: Wrong-entity writes comparison (full width)
    ax_a = fig.add_subplot(gs[0, :])
    plot_wrong_writes_comparison(ax_a, models, generic_writes, cta_writes,
                                 generic_acc, cta_acc)
    ax_a.text(-0.06, 1.12, 'A', transform=ax_a.transAxes,
              fontsize=12, fontweight='bold', va='top')

    # Panel B: Substitution rates with denominators
    ax_b = fig.add_subplot(gs[1, :])
    plot_substitution_cascade(ax_b, models, generic_subs, generic_total,
                             cta_subs, cta_total)
    ax_b.text(-0.06, 1.12, 'B', transform=ax_b.transAxes,
              fontsize=12, fontweight='bold', va='top')

    # Panel C: Accuracy-Substitution scatter
    ax_c = fig.add_subplot(gs[2, 0])
    plot_accuracy_substitution_tradeoff(ax_c, models, generic_acc, cta_acc,
                                       generic_subs, generic_total)
    ax_c.text(-0.14, 1.12, 'C', transform=ax_c.transAxes,
              fontsize=12, fontweight='bold', va='top')

    # Panel D: Error type breakdown
    ax_d = fig.add_subplot(gs[2, 1])
    plot_error_breakdown(ax_d, models, generic_writes, cta_writes)
    ax_d.text(-0.14, 1.12, 'D', transform=ax_d.transAxes,
              fontsize=12, fontweight='bold', va='top')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created new schema consequence figure: {output_path}")


def plot_wrong_writes_comparison(ax, models, generic_writes, cta_writes,
                                 generic_acc, cta_acc):
    """Plot wrong-entity writes with accuracy context."""
    x = np.arange(len(models))
    width = 0.35

    # Bar plot for wrong writes
    bars1 = ax.bar(x - width/2, generic_writes, width, label='Generic',
                   color=COLORS['generic'], alpha=0.8, edgecolor='black', linewidth=0.6)
    bars2 = ax.bar(x + width/2, cta_writes, width, label='CTA',
                   color=COLORS['cta'], alpha=0.8, edgecolor='black', linewidth=0.6)

    # Add value labels
    for i, (g, c) in enumerate(zip(generic_writes, cta_writes)):
        ax.text(i - width/2, g + 1.5, f'{g}', ha='center', va='bottom',
               fontsize=8, fontweight='bold', color=COLORS['qwen'])
        ax.text(i + width/2, c + 1.5, f'{c}', ha='center', va='bottom',
               fontsize=8, fontweight='bold')

    ax.set_ylabel('Wrong-Entity Writes', fontweight='bold', fontsize=9)
    ax.set_xlabel('Model', fontweight='bold', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, max(generic_writes) * 1.2)
    ax.legend(loc='upper right', frameon=True, fontsize=8)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add secondary axis for accuracy
    ax2 = ax.twinx()
    ax2.plot(x - width/2, generic_acc, 'o--', color=COLORS['qwen'],
            markersize=6, alpha=0.6, linewidth=1.5, label='Generic Acc')
    ax2.plot(x + width/2, cta_acc, 's-', color=COLORS['glm'],
            markersize=6, alpha=0.8, linewidth=1.5, label='CTA Acc')
    ax2.set_ylabel('End-to-End Accuracy (%)', fontweight='bold', fontsize=9)
    ax2.set_ylim(0, 105)
    ax2.legend(loc='upper left', frameon=True, fontsize=7)

    ax.set_title('Wrong-Entity Writes vs Accuracy (New Schema Replication)',
                fontsize=10, fontweight='bold', pad=10)


def plot_substitution_cascade(ax, models, generic_subs, generic_total,
                              cta_subs, cta_total):
    """Plot substitution rates showing the cascade effect."""
    x = np.arange(len(models))
    width = 0.7

    # Calculate rates
    generic_rates = [s/t*100 if t > 0 else 0 for s, t in zip(generic_subs, generic_total)]
    cta_rates = [s/t*100 if t > 0 else 0 for s, t in zip(cta_subs, cta_total)]

    # Stacked bars showing substitutions vs correct
    generic_correct = [t - s for s, t in zip(generic_subs, generic_total)]
    cta_correct = [t - s for s, t in zip(cta_subs, cta_total)]

    # Generic bars
    p1 = ax.barh(x - width/2, generic_subs, width, label='Substituted',
                color=COLORS['qwen'], alpha=0.8, edgecolor='black', linewidth=0.5)
    p2 = ax.barh(x - width/2, generic_correct, width, left=generic_subs,
                label='Correct', color='lightgray', alpha=0.6,
                edgecolor='black', linewidth=0.5)

    # CTA bars
    p3 = ax.barh(x + width/2, cta_subs, width,
                color=COLORS['qwen'], alpha=0.3, edgecolor='black', linewidth=0.5)
    p4 = ax.barh(x + width/2, cta_correct, width, left=cta_subs,
                color=COLORS['glm'], alpha=0.8, edgecolor='black', linewidth=0.5)

    # Add labels
    for i, (gs, gt, gr, cs, ct, cr) in enumerate(zip(generic_subs, generic_total,
                                                      generic_rates, cta_subs,
                                                      cta_total, cta_rates)):
        # Generic labels
        if gs > 0:
            ax.text(gs/2, i - width/2, f'{gs}/{gt}', ha='center', va='center',
                   fontsize=8, fontweight='bold', color='white')
        ax.text(gt + 1, i - width/2, f'{gr:.1f}%', va='center',
               fontsize=7, color=COLORS['qwen'], fontweight='bold')

        # CTA labels
        ax.text(ct/2, i + width/2, f'{cs}/{ct}', ha='center', va='center',
               fontsize=8, fontweight='bold')
        ax.text(ct + 1, i + width/2, f'{cr:.1f}%', va='center',
               fontsize=7, color=COLORS['glm'], fontweight='bold')

    ax.set_yticks(x)
    ax.set_yticklabels([f'{m}\nGeneric\n{m}\nCTA' for m in models])
    ax.set_xlabel('Eligible Cases', fontweight='bold', fontsize=9)
    ax.set_xlim(0, max(generic_total + cta_total) * 1.15)

    # Custom legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['qwen'], alpha=0.8, edgecolor='black',
                      label='Generic Substitutions'),
        mpatches.Patch(facecolor=COLORS['glm'], alpha=0.8, edgecolor='black',
                      label='CTA Correct'),
        mpatches.Patch(facecolor='lightgray', alpha=0.6, edgecolor='black',
                      label='Generic Correct')
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, fontsize=7)
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    ax.set_title('Conditional Substitution After Correct Binding',
                fontsize=10, fontweight='bold', pad=10)


def plot_accuracy_substitution_tradeoff(ax, models, generic_acc, cta_acc,
                                       generic_subs, generic_total):
    """Scatter plot showing accuracy vs substitution trade-off."""
    generic_sub_rates = [s/t*100 for s, t in zip(generic_subs, generic_total)]
    cta_sub_rates = [0, 0, 0]

    colors_map = [COLORS['qwen'], COLORS['glm'], COLORS['deepseek']]

    for i, model in enumerate(models):
        # Generic
        ax.scatter(generic_sub_rates[i], generic_acc[i], s=150,
                  color=colors_map[i], alpha=0.5, marker='o',
                  edgecolor='black', linewidth=1.5, label=f'{model} Generic')
        # CTA
        ax.scatter(cta_sub_rates[i], cta_acc[i], s=150,
                  color=colors_map[i], alpha=0.9, marker='s',
                  edgecolor='black', linewidth=1.5, label=f'{model} CTA')

        # Connect with arrow
        ax.annotate('', xy=(cta_sub_rates[i], cta_acc[i]),
                   xytext=(generic_sub_rates[i], generic_acc[i]),
                   arrowprops=dict(arrowstyle='->', lw=2, color=colors_map[i],
                                 alpha=0.6))

        # Add labels
        ax.text(generic_sub_rates[i] + 2, generic_acc[i], model,
               fontsize=7, va='center', alpha=0.7)

    ax.set_xlabel('Substitution Rate (%)', fontweight='bold', fontsize=9)
    ax.set_ylabel('Accuracy (%)', fontweight='bold', fontsize=9)
    ax.set_xlim(-5, max(generic_sub_rates) * 1.1)
    ax.set_ylim(40, 100)
    ax.grid(alpha=0.3, linestyle='--')

    # Shade the ideal region (low substitution, high accuracy)
    ax.axhspan(80, 100, alpha=0.1, color='green')
    ax.axvspan(-5, 10, alpha=0.1, color='green')

    ax.set_title('Accuracy-Substitution Trade-off',
                fontsize=10, fontweight='bold', pad=10)

    # Add text annotation
    ax.text(0.98, 0.02, 'Ideal: High accuracy,\nLow substitution',
           transform=ax.transAxes, fontsize=7, ha='right', va='bottom',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))


def plot_error_breakdown(ax, models, generic_writes, cta_writes):
    """Plot error type breakdown as stacked bars."""
    # Mock breakdown - replace with actual data
    generic_wrong_target = np.array(generic_writes) * 0.9
    generic_invalid = np.array(generic_writes) * 0.1

    cta_wrong_target = np.array(cta_writes) * 0.3
    cta_invalid = np.array(cta_writes) * 0.7

    x = np.arange(len(models))
    width = 0.35

    # Generic stacked
    ax.bar(x - width/2, generic_wrong_target, width, label='Wrong Target',
          color=COLORS['qwen'], alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.bar(x - width/2, generic_invalid, width, bottom=generic_wrong_target,
          label='Invalid Attempt', color=COLORS['qwen'], alpha=0.4,
          edgecolor='black', linewidth=0.5)

    # CTA stacked
    ax.bar(x + width/2, cta_wrong_target, width,
          color=COLORS['glm'], alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.bar(x + width/2, cta_invalid, width, bottom=cta_wrong_target,
          color=COLORS['glm'], alpha=0.4, edgecolor='black', linewidth=0.5)

    # Add total labels
    for i in range(len(models)):
        g_total = generic_wrong_target[i] + generic_invalid[i]
        c_total = cta_wrong_target[i] + cta_invalid[i]
        ax.text(i - width/2, g_total + 1, f'{int(g_total)}', ha='center',
               fontsize=8, fontweight='bold')
        ax.text(i + width/2, c_total + 1, f'{int(c_total)}', ha='center',
               fontsize=8, fontweight='bold')

    ax.set_ylabel('Error Count', fontweight='bold', fontsize=9)
    ax.set_xlabel('Model', fontweight='bold', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(loc='upper right', frameon=True, fontsize=7)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_title('Error Type Breakdown', fontsize=10, fontweight='bold', pad=10)


def create_policy_identifiability_figure(output_path: Path) -> None:
    """
    Create figure showing how evaluation regimes identify policies:
    - Different evaluation strategies (Stable-only, Changed-only, Matched pairs)
    - Policy performance under each regime
    """
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6))
    fig.suptitle('Evaluation Regimes and Policy Identifiability',
                fontsize=11, fontweight='bold', y=0.98)

    # Panel A: Stable-only evaluation (can't distinguish)
    plot_stable_only_regime(axes[0, 0])
    axes[0, 0].text(-0.15, 1.1, 'A', transform=axes[0, 0].transAxes,
                   fontsize=12, fontweight='bold', va='top')

    # Panel B: Changed preserve-only (favors Lock)
    plot_preserve_only_regime(axes[0, 1])
    axes[0, 1].text(-0.15, 1.1, 'B', transform=axes[0, 1].transAxes,
                   fontsize=12, fontweight='bold', va='top')

    # Panel C: Changed reevaluate-only (favors Reevaluate)
    plot_reevaluate_only_regime(axes[1, 0])
    axes[1, 0].text(-0.15, 1.1, 'C', transform=axes[1, 0].transAxes,
                   fontsize=12, fontweight='bold', va='top')

    # Panel D: Matched pairs (distinguishes all)
    plot_matched_pairs_regime(axes[1, 1])
    axes[1, 1].text(-0.15, 1.1, 'D', transform=axes[1, 1].transAxes,
                   fontsize=12, fontweight='bold', va='top')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created policy identifiability figure: {output_path}")


def plot_stable_only_regime(ax):
    """Plot performance under stable-only evaluation."""
    policies = ['Lock', 'Reevaluate', 'Selective']
    scores = [100, 100, 100]
    colors = [COLORS['lock'], COLORS['reeval'], COLORS['cta']]

    bars = ax.bar(policies, scores, color=colors, alpha=0.7,
                 edgecolor='black', linewidth=1)

    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
               f'{score}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylim(0, 115)
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_title('Stable-Only: Cannot Distinguish', fontsize=9, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    ax.text(0.5, 0.5, '⚠ All policies pass\nNo discrimination',
           transform=ax.transAxes, ha='center', va='center',
           fontsize=9, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))


def plot_preserve_only_regime(ax):
    """Plot performance under preserve-only changed evaluation."""
    policies = ['Lock', 'Reevaluate', 'Selective']
    scores = [100, 0, 100]
    colors = [COLORS['lock'], COLORS['reeval'], COLORS['cta']]

    bars = ax.bar(policies, scores, color=colors, alpha=0.7,
                 edgecolor='black', linewidth=1)

    for bar, score in zip(bars, scores):
        height = max(bar.get_height(), 5)
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
               f'{score}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylim(0, 115)
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_title('Preserve-Only: Favors Lock', fontsize=9, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    ax.text(0.5, 0.5, '⚠ Lock succeeds\nOne-sided bias',
           transform=ax.transAxes, ha='center', va='center',
           fontsize=9, bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))


def plot_reevaluate_only_regime(ax):
    """Plot performance under reevaluate-only changed evaluation."""
    policies = ['Lock', 'Reevaluate', 'Selective']
    scores = [0, 100, 100]
    colors = [COLORS['lock'], COLORS['reeval'], COLORS['cta']]

    bars = ax.bar(policies, scores, color=colors, alpha=0.7,
                 edgecolor='black', linewidth=1)

    for bar, score in zip(bars, scores):
        height = max(bar.get_height(), 5)
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
               f'{score}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylim(0, 115)
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_title('Reevaluate-Only: Favors Reevaluate', fontsize=9, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    ax.text(0.5, 0.5, '⚠ Reevaluate succeeds\nOpposite bias',
           transform=ax.transAxes, ha='center', va='center',
           fontsize=9, bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))


def plot_matched_pairs_regime(ax):
    """Plot performance under matched pairs evaluation."""
    policies = ['Lock', 'Reevaluate', 'Selective']
    scores = [0, 0, 100]
    colors = [COLORS['lock'], COLORS['reeval'], COLORS['cta']]

    bars = ax.bar(policies, scores, color=colors, alpha=0.7,
                 edgecolor='black', linewidth=1)

    for bar, score in zip(bars, scores):
        height = max(bar.get_height(), 5)
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
               f'{score}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_ylim(0, 115)
    ax.set_ylabel('PairAcc (%)', fontweight='bold')
    ax.set_title('Matched Pairs: Distinguishes All', fontsize=9, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    ax.text(0.5, 0.5, '✓ Only selective succeeds\nFull discrimination',
           transform=ax.transAxes, ha='center', va='center',
           fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))


def main():
    parser = argparse.ArgumentParser(description='Generate high-density TRI figures')
    parser.add_argument('--output-dir', type=Path,
                       default=Path('reports/figures'))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Create figures
    create_new_schema_consequence_figure(
        args.output_dir / 'tri_new_schema_comprehensive.pdf')

    create_policy_identifiability_figure(
        args.output_dir / 'tri_policy_identifiability_comprehensive.pdf')

    print("\nAll high-density figures generated successfully!")


if __name__ == '__main__':
    main()
