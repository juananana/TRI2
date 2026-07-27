"""
Final refined results figures for TRI AAAI submission.
Using real data with innovative, publication-quality visualizations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

# Clean 3-color palette
TEAL = '#2A7B7E'
TERRA = '#C96D5A'
GRAY = '#3D4852'
TEAL_LIGHT = '#E8F4F4'
TERRA_LIGHT = '#F9EBE8'
GRID = '#E0E3E6'

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Times'],
    'font.size': 9,
    'axes.labelsize': 9,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'axes.linewidth': 0.8,
})


def load_data(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def create_main_results_figure(output_path: Path, data: dict) -> None:
    """
    Main results: 3-panel figure showing controller comparison.
    Panel A: PairAcc comparison (slope chart)
    Panel B: Preserve vs Reevaluate breakdown (grouped)
    Panel C: Changed-winner core focus (heatmap-style)
    """
    fig = plt.figure(figsize=(7.2, 2.6))
    gs = GridSpec(1, 3, figure=fig, wspace=0.38,
                  left=0.08, right=0.98, top=0.86, bottom=0.20)

    # Extract data
    generic_qwen = next(r for r in data['results']
                       if r['controller'] == 'Generic' and 'Qwen' in r['model'])
    generic_glm = next(r for r in data['results']
                      if r['controller'] == 'Generic' and 'GLM' in r['model'])
    cta_qwen = next(r for r in data['results']
                   if r['controller'] == 'CTA' and 'Qwen' in r['model'])
    cta_glm = next(r for r in data['results']
                  if r['controller'] == 'CTA' and 'GLM' in r['model'])

    ax_a = fig.add_subplot(gs[0, 0])
    plot_pairacc_slopes(ax_a, generic_qwen, generic_glm, cta_qwen, cta_glm)
    ax_a.text(-0.22, 1.05, 'A', transform=ax_a.transAxes,
              fontsize=12, fontweight='bold')

    ax_b = fig.add_subplot(gs[0, 1])
    plot_preserve_reevaluate(ax_b, generic_qwen, generic_glm, cta_qwen, cta_glm)
    ax_b.text(-0.22, 1.05, 'B', transform=ax_b.transAxes,
              fontsize=12, fontweight='bold')

    ax_c = fig.add_subplot(gs[0, 2])
    plot_changed_winner_matrix(ax_c, generic_qwen, generic_glm, cta_qwen, cta_glm)
    ax_c.text(-0.22, 1.05, 'C', transform=ax_c.transAxes,
              fontsize=12, fontweight='bold')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path.name}")


def plot_pairacc_slopes(ax, gen_q, gen_g, cta_q, cta_g):
    """Slope chart showing Generic→CTA improvement."""
    models = ['Qwen', 'GLM']

    gen_scores = [
        gen_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
        gen_g['slices']['changed_winner_core']['pair_accuracy'] * 100
    ]
    cta_scores = [
        cta_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
        cta_g['slices']['changed_winner_core']['pair_accuracy'] * 100
    ]

    x_pos = [0, 1]

    for i, model in enumerate(models):
        # Connection line
        ax.plot(x_pos, [gen_scores[i], cta_scores[i]],
               'o-', linewidth=2.5, markersize=9,
               color=TEAL, alpha=0.8, zorder=3)

        # Labels
        ax.text(-0.08, gen_scores[i], f'{gen_scores[i]:.1f}%',
               ha='right', va='center', fontsize=9,
               color=GRAY, fontweight='bold')
        ax.text(1.08, cta_scores[i], f'{cta_scores[i]:.1f}%',
               ha='left', va='center', fontsize=9,
               color=TEAL, fontweight='bold')

        # Model label
        mid_y = (gen_scores[i] + cta_scores[i]) / 2
        ax.text(0.5, mid_y + 3, model,
               ha='center', fontsize=8, style='italic', color=GRAY)

    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(0, 105)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Generic', 'CTA'], fontweight='bold')
    ax.set_ylabel('Changed-Pair Accuracy (%)', fontweight='bold')
    ax.set_title('Controller Improvement', fontweight='bold', pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID, zorder=0)


def plot_preserve_reevaluate(ax, gen_q, gen_g, cta_q, cta_g):
    """Grouped bars showing Preserve vs Reevaluate accuracy."""
    labels = ['Generic\nQwen', 'Generic\nGLM', 'CTA\nQwen', 'CTA\nGLM']

    preserve = [
        gen_q['slices']['changed_winner_core']['preserve_accuracy'] * 100,
        gen_g['slices']['changed_winner_core']['preserve_accuracy'] * 100,
        cta_q['slices']['changed_winner_core']['preserve_accuracy'] * 100,
        cta_g['slices']['changed_winner_core']['preserve_accuracy'] * 100,
    ]
    reevaluate = [
        gen_q['slices']['changed_winner_core']['reevaluate_accuracy'] * 100,
        gen_g['slices']['changed_winner_core']['reevaluate_accuracy'] * 100,
        cta_q['slices']['changed_winner_core']['reevaluate_accuracy'] * 100,
        cta_g['slices']['changed_winner_core']['reevaluate_accuracy'] * 100,
    ]

    x = np.arange(len(labels))
    width = 0.38

    # Preserve bars (terracotta - the challenge)
    bars1 = ax.bar(x - width/2, preserve, width,
                   label='Preserve', color=TERRA,
                   edgecolor='white', linewidth=1.2, zorder=3)

    # Reevaluate bars (teal - easier)
    bars2 = ax.bar(x + width/2, reevaluate, width,
                   label='Reevaluate', color=TEAL,
                   edgecolor='white', linewidth=1.2, zorder=3)

    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 1.5,
                   f'{h:.0f}', ha='center', va='bottom',
                   fontsize=7.5, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_ylim(0, 108)
    ax.legend(loc='lower right', frameon=True, framealpha=0.95)
    ax.set_title('Preserve vs Reevaluate', fontweight='bold', pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID, zorder=0)


def plot_changed_winner_matrix(ax, gen_q, gen_g, cta_q, cta_g):
    """Compact matrix showing changed-winner performance."""
    data_matrix = np.array([
        [gen_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
         gen_g['slices']['changed_winner_core']['pair_accuracy'] * 100],
        [cta_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
         cta_g['slices']['changed_winner_core']['pair_accuracy'] * 100]
    ])

    im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto',
                   vmin=0, vmax=100, zorder=2)

    # Cell annotations
    for i in range(2):
        for j in range(2):
            value = data_matrix[i, j]
            color = 'white' if value < 60 else 'black'
            ax.text(j, i, f'{value:.1f}%',
                   ha='center', va='center',
                   fontsize=11, fontweight='bold',
                   color=color, zorder=3)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Qwen', 'GLM'], fontweight='bold')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Generic', 'CTA'], fontweight='bold')
    ax.set_title('Changed-Winner\nPairAcc (%)', fontweight='bold', pad=6)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=7)
    cbar.set_label('%', rotation=0, labelpad=10, fontsize=8)


def create_policy_identifiability_figure(output_path: Path, data: dict) -> None:
    """
    Policy identifiability: 2-panel comparison.
    Panel A: One-sided evaluation problem
    Panel B: Matched pairs solution
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.4))
    fig.subplots_adjust(wspace=0.32, left=0.09, right=0.98, top=0.88, bottom=0.18)

    # Get Always-Lock and Always-Reevaluate data
    lock_data = next((r for r in data['results']
                     if r['controller'] == 'Always-Lock+validity'), None)
    reeval_data = next((r for r in data['results']
                       if r['controller'] == 'Always-Reevaluate'), None)

    plot_one_sided_problem(axes[0], lock_data, reeval_data)
    axes[0].text(-0.18, 1.05, 'A', transform=axes[0].transAxes,
                fontsize=12, fontweight='bold')

    plot_matched_solution(axes[1], data)
    axes[1].text(-0.18, 1.05, 'B', transform=axes[1].transAxes,
                fontsize=12, fontweight='bold')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path.name}")


def plot_one_sided_problem(ax, lock_data, reeval_data):
    """Show how one-sided evaluation fails."""
    categories = ['Changed\nPreserve', 'Changed\nReevaluate']

    if lock_data and reeval_data:
        lock_preserve = lock_data['slices']['changed_winner_core']['preserve_accuracy'] * 100
        lock_reeval = lock_data['slices']['changed_winner_core']['reevaluate_accuracy'] * 100
        reeval_preserve = reeval_data['slices']['changed_winner_core']['preserve_accuracy'] * 100
        reeval_reeval = reeval_data['slices']['changed_winner_core']['reevaluate_accuracy'] * 100
    else:
        # Fallback to theoretical values
        lock_preserve, lock_reeval = 100, 0
        reeval_preserve, reeval_reeval = 0, 100

    lock_scores = [lock_preserve, lock_reeval]
    reeval_scores = [reeval_preserve, reeval_reeval]

    x = np.arange(len(categories))
    width = 0.38

    ax.bar(x - width/2, lock_scores, width,
           label='Always-Lock', color=GRAY,
           edgecolor='white', linewidth=1.2)
    ax.bar(x + width/2, reeval_scores, width,
           label='Always-Reevaluate', color=TERRA,
           edgecolor='white', linewidth=1.2)

    # Highlight the problem
    ax.axhspan(80, 105, alpha=0.12, color='red', zorder=0)
    ax.text(0.98, 0.92, '⚠ One-sided\nevaluation\nfavors extremes',
           transform=ax.transAxes, ha='right', va='top',
           fontsize=7.5, style='italic',
           bbox=dict(boxstyle='round,pad=0.4', facecolor=TERRA_LIGHT,
                    edgecolor=TERRA, linewidth=1))

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_ylim(0, 110)
    ax.legend(loc='upper left', frameon=True, fontsize=7.5)
    ax.set_title('One-Sided Evaluation Problem', fontweight='bold', pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID)


def plot_matched_solution(ax, data):
    """Show how matched pairs distinguish policies."""
    # Get data
    gen_q = next(r for r in data['results']
                if r['controller'] == 'Generic' and 'Qwen' in r['model'])
    cta_q = next(r for r in data['results']
                if r['controller'] == 'CTA' and 'Qwen' in r['model'])

    policies = ['Always-\nLock', 'Always-\nReevaluate', 'Generic', 'CTA']
    pairacc = [0, 0,
               gen_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
               cta_q['slices']['changed_winner_core']['pair_accuracy'] * 100]

    colors_list = [GRAY, GRAY, TERRA, TEAL]

    bars = ax.bar(range(len(policies)), pairacc,
                  color=colors_list, edgecolor='white', linewidth=1.2)

    # Annotations
    for i, (bar, score) in enumerate(zip(bars, pairacc)):
        if score > 5:
            ax.text(bar.get_x() + bar.get_width()/2, score + 2,
                   f'{score:.1f}%', ha='center', va='bottom',
                   fontsize=8, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width()/2, 5,
                   f'{score:.0f}%', ha='center', va='bottom',
                   fontsize=8, color=GRAY)

    # Success region
    ax.axhspan(80, 105, alpha=0.12, color='green', zorder=0)
    ax.text(0.98, 0.92, '✓ Matched pairs\ndiscriminate\nselective policy',
           transform=ax.transAxes, ha='right', va='top',
           fontsize=7.5, style='italic',
           bbox=dict(boxstyle='round,pad=0.4', facecolor=TEAL_LIGHT,
                    edgecolor=TEAL, linewidth=1))

    ax.set_xticks(range(len(policies)))
    ax.set_xticklabels(policies, fontsize=7.5)
    ax.set_ylabel('PairAcc (%)', fontweight='bold')
    ax.set_ylim(0, 110)
    ax.set_title('Matched Pairs Solution', fontweight='bold', pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path,
                       default=Path('reports/matched_pair_consistency.json'))
    parser.add_argument('--output-dir', type=Path,
                       default=Path('reports/figures'))
    args = parser.parse_args()

    data = load_data(args.data)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    create_main_results_figure(
        args.output_dir / 'tri_main_results.pdf', data)

    create_policy_identifiability_figure(
        args.output_dir / 'tri_policy_comparison.pdf', data)

    print("\n✨ Final figures generated!")
    print("  • tri_main_results.pdf - 3-panel main results")
    print("  • tri_policy_comparison.pdf - Policy identifiability")


if __name__ == '__main__':
    main()
