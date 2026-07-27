"""
Redesigned TRI figures - Clean 1-2 column layouts without overlaps.
Focus on essential results only.
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


def create_single_column_comparison(output_path: Path, data: dict) -> None:
    """
    Single column figure: Generic vs CTA comparison.
    Clean bar chart showing the dramatic improvement.
    """
    fig, ax = plt.subplots(1, 1, figsize=(3.3, 2.8))
    fig.subplots_adjust(left=0.16, right=0.96, top=0.90, bottom=0.15)

    # Extract data
    gen_q = next(r for r in data['results']
                if r['controller'] == 'Generic' and 'Qwen' in r['model'])
    gen_g = next(r for r in data['results']
                if r['controller'] == 'Generic' and 'GLM' in r['model'])
    cta_q = next(r for r in data['results']
                if r['controller'] == 'CTA' and 'Qwen' in r['model'])
    cta_g = next(r for r in data['results']
                if r['controller'] == 'CTA' and 'GLM' in r['model'])

    categories = ['Qwen3.5', 'GLM-5.1']

    generic_scores = [
        gen_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
        gen_g['slices']['changed_winner_core']['pair_accuracy'] * 100
    ]
    cta_scores = [
        cta_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
        cta_g['slices']['changed_winner_core']['pair_accuracy'] * 100
    ]

    x = np.arange(len(categories))
    width = 0.36

    # Generic bars (problem - terracotta)
    bars1 = ax.bar(x - width/2, generic_scores, width,
                   label='Generic', color=TERRA, alpha=0.85,
                   edgecolor='white', linewidth=1.5, zorder=3)

    # CTA bars (solution - teal)
    bars2 = ax.bar(x + width/2, cta_scores, width,
                   label='CTA', color=TEAL, alpha=0.9,
                   edgecolor='white', linewidth=1.5, zorder=3)

    # Value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.1f}',
                   ha='center', va='bottom',
                   fontsize=9, fontweight='bold')

    # Improvement annotations
    for i, (g, c) in enumerate(zip(generic_scores, cta_scores)):
        improvement = c - g
        mid_x = x[i]
        mid_y = (g + c) / 2
        ax.annotate('', xy=(mid_x + width/2 - 0.02, c - 4),
                   xytext=(mid_x - width/2 + 0.02, g + 4),
                   arrowprops=dict(arrowstyle='->', lw=2,
                                 color=TEAL, alpha=0.6))
        ax.text(mid_x + width + 0.12, mid_y, f'+{improvement:.0f}',
               fontsize=8.5, fontweight='bold', color=TEAL)

    ax.set_ylabel('Changed-Pair Accuracy (%)', fontweight='bold', fontsize=9)
    ax.set_xlabel('Model', fontweight='bold', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 105)
    ax.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=8.5)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID, zorder=0)
    ax.set_title('Controller Comparison on Changed-Winner Pairs',
                fontweight='bold', pad=8, fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path.name}")


def create_two_column_breakdown(output_path: Path, data: dict) -> None:
    """
    Two column figure: Preserve vs Reevaluate breakdown.
    Shows why Generic fails (poor on Preserve) and CTA succeeds.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
    fig.subplots_adjust(wspace=0.28, left=0.09, right=0.98, top=0.88, bottom=0.16)

    # Extract data
    gen_q = next(r for r in data['results']
                if r['controller'] == 'Generic' and 'Qwen' in r['model'])
    gen_g = next(r for r in data['results']
                if r['controller'] == 'Generic' and 'GLM' in r['model'])
    cta_q = next(r for r in data['results']
                if r['controller'] == 'CTA' and 'Qwen' in r['model'])
    cta_g = next(r for r in data['results']
                if r['controller'] == 'CTA' and 'GLM' in r['model'])

    # Panel A: Generic breakdown
    plot_controller_breakdown(axes[0], gen_q, gen_g, 'Generic', TERRA)
    axes[0].text(-0.15, 1.06, 'A', transform=axes[0].transAxes,
                fontsize=12, fontweight='bold')

    # Panel B: CTA breakdown
    plot_controller_breakdown(axes[1], cta_q, cta_g, 'CTA', TEAL)
    axes[1].text(-0.15, 1.06, 'B', transform=axes[1].transAxes,
                fontsize=12, fontweight='bold')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path.name}")


def plot_controller_breakdown(ax, model_q, model_g, controller_name, color):
    """Helper to plot preserve vs reevaluate breakdown."""
    categories = ['Preserve', 'Reevaluate']

    qwen_scores = [
        model_q['slices']['changed_winner_core']['preserve_accuracy'] * 100,
        model_q['slices']['changed_winner_core']['reevaluate_accuracy'] * 100
    ]
    glm_scores = [
        model_g['slices']['changed_winner_core']['preserve_accuracy'] * 100,
        model_g['slices']['changed_winner_core']['reevaluate_accuracy'] * 100
    ]

    x = np.arange(len(categories))
    width = 0.36

    # Qwen bars
    bars1 = ax.bar(x - width/2, qwen_scores, width,
                   label='Qwen3.5', color=color, alpha=0.7,
                   edgecolor='white', linewidth=1.2)

    # GLM bars
    bars2 = ax.bar(x + width/2, glm_scores, width,
                   label='GLM-5.1', color=color, alpha=0.95,
                   edgecolor='white', linewidth=1.2)

    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                   f'{height:.0f}',
                   ha='center', va='bottom',
                   fontsize=8.5, fontweight='bold')

    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 108)
    ax.legend(loc='lower right', frameon=True, framealpha=0.95, fontsize=8)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID, zorder=0)
    ax.set_title(f'{controller_name} Performance', fontweight='bold', pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def create_single_column_policy(output_path: Path, data: dict) -> None:
    """
    Single column: Policy identifiability demonstration.
    Shows matched pairs reject unconditional policies.
    """
    fig, ax = plt.subplots(1, 1, figsize=(3.3, 2.8))
    fig.subplots_adjust(left=0.18, right=0.96, top=0.90, bottom=0.18)

    # Get data
    gen_q = next(r for r in data['results']
                if r['controller'] == 'Generic' and 'Qwen' in r['model'])
    cta_q = next(r for r in data['results']
                if r['controller'] == 'CTA' and 'Qwen' in r['model'])

    policies = ['Always-\nLock', 'Always-\nReevaluate', 'Generic', 'CTA']
    pairacc = [
        0,  # Always-Lock
        0,  # Always-Reevaluate
        gen_q['slices']['changed_winner_core']['pair_accuracy'] * 100,
        cta_q['slices']['changed_winner_core']['pair_accuracy'] * 100
    ]

    colors_list = [GRAY, GRAY, TERRA, TEAL]

    # Create bars individually to set different alphas
    bars = []
    for i, (score, color) in enumerate(zip(pairacc, colors_list)):
        alpha = 0.6 if i < 2 else 0.85 if i == 2 else 0.95
        bar = ax.bar(i, score, color=color, alpha=alpha,
                    edgecolor='white', linewidth=1.2)
        bars.append(bar)

    # Value labels
    for i, score in enumerate(pairacc):
        if score > 5:
            ax.text(i, score + 2,
                   f'{score:.1f}%', ha='center', va='bottom',
                   fontsize=9, fontweight='bold')
        else:
            ax.text(i, 5,
                   f'{score:.0f}%', ha='center', va='bottom',
                   fontsize=8, color=GRAY)

    # Success threshold line
    ax.axhline(y=80, color=TEAL, linestyle='--', linewidth=1.5,
              alpha=0.4, zorder=0)
    ax.text(3.5, 82, 'High performance', fontsize=7.5,
           ha='right', style='italic', color=TEAL)

    ax.set_xticks(range(len(policies)))
    ax.set_xticklabels(policies, fontsize=8.5)
    ax.set_ylabel('Matched-Pair Accuracy (%)', fontweight='bold')
    ax.set_ylim(0, 105)
    ax.set_title('Policy Discrimination with Matched Pairs',
                fontweight='bold', pad=8, fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID)

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path.name}")


def create_two_column_schema_transfer(output_path: Path) -> None:
    """
    Two column: Schema transfer results.
    Panel A: Substitution counts, Panel B: Accuracy improvement.
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
    fig.subplots_adjust(wspace=0.30, left=0.10, right=0.98, top=0.88, bottom=0.16)

    models = ['Qwen', 'GLM', 'DeepSeek']
    generic_subs = np.array([43, 38, 59])
    generic_total = np.array([72, 80, 79])
    cta_total = np.array([71, 70, 70])

    generic_acc = np.array([47.5, 70.0, 73.8])
    cta_acc = np.array([70.8, 94.2, 91.2])

    # Panel A: Substitution comparison
    plot_substitution_comparison(axes[0], models, generic_subs, generic_total, cta_total)
    axes[0].text(-0.15, 1.06, 'A', transform=axes[0].transAxes,
                fontsize=12, fontweight='bold')

    # Panel B: Accuracy comparison
    plot_accuracy_comparison(axes[1], models, generic_acc, cta_acc)
    axes[1].text(-0.15, 1.06, 'B', transform=axes[1].transAxes,
                fontsize=12, fontweight='bold')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created: {output_path.name}")


def plot_substitution_comparison(ax, models, subs, gen_total, cta_total):
    """Plot substitution rates."""
    x = np.arange(len(models))
    width = 0.36

    gen_rates = subs / gen_total * 100
    cta_rates = np.zeros(len(models))

    bars1 = ax.bar(x - width/2, gen_rates, width,
                   label='Generic', color=TERRA, alpha=0.85,
                   edgecolor='white', linewidth=1.2)
    bars2 = ax.bar(x + width/2, cta_rates, width,
                   label='CTA', color=TEAL, alpha=0.9,
                   edgecolor='white', linewidth=1.2)

    # Labels
    for i, (rate, sub, tot) in enumerate(zip(gen_rates, subs, gen_total)):
        ax.text(i - width/2, rate + 2, f'{sub}/{int(tot)}',
               ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax.text(i + width/2, 2, '0',
               ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_ylabel('Substitution Rate (%)', fontweight='bold')
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 85)
    ax.legend(loc='upper right', frameon=True, framealpha=0.95)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID, zorder=0)
    ax.set_title('Substitution After Correct Binding', fontweight='bold', pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_accuracy_comparison(ax, models, gen_acc, cta_acc):
    """Plot accuracy comparison."""
    x = np.arange(len(models))
    width = 0.36

    bars1 = ax.bar(x - width/2, gen_acc, width,
                   label='Generic', color=TERRA, alpha=0.85,
                   edgecolor='white', linewidth=1.2)
    bars2 = ax.bar(x + width/2, cta_acc, width,
                   label='CTA', color=TEAL, alpha=0.9,
                   edgecolor='white', linewidth=1.2)

    # Value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                   f'{height:.1f}',
                   ha='center', va='bottom',
                   fontsize=8.5, fontweight='bold')

    ax.set_ylabel('End-to-End Accuracy (%)', fontweight='bold')
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right', frameon=True, framealpha=0.95)
    ax.grid(axis='y', alpha=0.25, linestyle='--', color=GRID, zorder=0)
    ax.set_title('Accuracy on New Schemas', fontweight='bold', pad=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path,
                       default=Path('reports/matched_pair_consistency.json'))
    parser.add_argument('--output-dir', type=Path,
                       default=Path('reports/figures'))
    args = parser.parse_args()

    data = load_data(args.data)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Single column figures
    create_single_column_comparison(
        args.output_dir / 'tri_controller_comparison.pdf', data)

    create_single_column_policy(
        args.output_dir / 'tri_policy_identifiability.pdf', data)

    # Two column figures
    create_two_column_breakdown(
        args.output_dir / 'tri_preserve_reevaluate.pdf', data)

    create_two_column_schema_transfer(
        args.output_dir / 'tri_schema_transfer.pdf')

    print("\n✨ Clean figures generated!")
    print("  • tri_controller_comparison.pdf (1-column)")
    print("  • tri_policy_identifiability.pdf (1-column)")
    print("  • tri_preserve_reevaluate.pdf (2-column)")
    print("  • tri_schema_transfer.pdf (2-column)")


if __name__ == '__main__':
    main()
