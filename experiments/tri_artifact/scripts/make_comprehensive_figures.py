"""
Comprehensive high-density figures for TRI paper submission.
Creates information-rich visualizations combining multiple dimensions.
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
import seaborn as sns

# Set style for publication quality
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['lines.linewidth'] = 1.5

# Color scheme
COLORS = {
    'qwen': '#B64926',
    'glm': '#126F66',
    'deepseek': '#7A8793',
    'generic': '#7A8793',
    'cta': '#126F66',
    'lifecycle': '#126F66',
    'preserve': '#E8F3F1',
    'reevaluate': '#F8ECE7',
    'accent': '#B64926',
    'muted': '#5B6570',
    'line': '#CBD2D9',
}


def load_ablation_data(path: Path) -> dict:
    """Load call-matched ablation data."""
    return json.loads(path.read_text(encoding='utf-8'))


def load_results_data(path: Path) -> dict:
    """Load main results data."""
    return json.loads(path.read_text(encoding='utf-8'))


def create_comprehensive_panel_figure(output_path: Path, ablation_data: dict) -> None:
    """
    Create a comprehensive 4-panel figure showing:
    - Panel A: Ablation comparison (PairAcc improvements)
    - Panel B: Conditional substitution rates
    - Panel C: Enforcement effects (repairs vs harms)
    - Panel D: Model comparison matrix
    """
    fig = plt.figure(figsize=(7.2, 8.5))
    gs = GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.3,
                  left=0.08, right=0.98, top=0.96, bottom=0.05)

    # Panel A: PairAcc Improvement (full width)
    ax_a = fig.add_subplot(gs[0, :])
    plot_pairacc_improvement(ax_a, ablation_data)
    ax_a.text(-0.05, 1.08, 'A', transform=ax_a.transAxes,
              fontsize=12, fontweight='bold', va='top')

    # Panel B: Conditional Substitution Rates
    ax_b = fig.add_subplot(gs[1, :])
    plot_substitution_rates(ax_b, ablation_data)
    ax_b.text(-0.05, 1.08, 'B', transform=ax_b.transAxes,
              fontsize=12, fontweight='bold', va='top')

    # Panel C: Enforcement Effects
    ax_c = fig.add_subplot(gs[2, 0])
    plot_enforcement_effects(ax_c, ablation_data)
    ax_c.text(-0.12, 1.08, 'C', transform=ax_c.transAxes,
              fontsize=12, fontweight='bold', va='top')

    # Panel D: Accuracy Breakdown
    ax_d = fig.add_subplot(gs[2, 1])
    plot_accuracy_breakdown(ax_d, ablation_data)
    ax_d.text(-0.12, 1.08, 'D', transform=ax_d.transAxes,
              fontsize=12, fontweight='bold', va='top')

    # Panel E: Full metrics heatmap (bottom row, full width)
    ax_e = fig.add_subplot(gs[3, :])
    plot_metrics_heatmap(ax_e, ablation_data)
    ax_e.text(-0.05, 1.08, 'E', transform=ax_e.transAxes,
              fontsize=12, fontweight='bold', va='top')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created comprehensive panel figure: {output_path}")


def plot_pairacc_improvement(ax, data: dict) -> None:
    """Plot PairAcc improvement from baseline to decision-visible/enforced."""
    models_data = data['models']

    x_pos = np.arange(len(models_data))
    width = 0.25

    baselines = []
    visible = []
    enforced = []

    for model_data in models_data:
        baselines.append(model_data['metrics']['history_only']['changed_pairacc']['rate'] * 100)
        visible.append(model_data['metrics']['decision_visible']['changed_pairacc']['rate'] * 100)
        enforced.append(model_data['metrics']['decision_enforced']['changed_pairacc']['rate'] * 100)

    ax.bar(x_pos - width, baselines, width, label='History Only',
           color=COLORS['muted'], alpha=0.7, edgecolor='black', linewidth=0.5)
    ax.bar(x_pos, visible, width, label='Decision Visible',
           color=COLORS['glm'], alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.bar(x_pos + width, enforced, width, label='Decision Enforced',
           color=COLORS['accent'], alpha=0.8, edgecolor='black', linewidth=0.5)

    # Add value labels
    for i, (b, v, e) in enumerate(zip(baselines, visible, enforced)):
        ax.text(i - width, b + 1.5, f'{b:.0f}', ha='center', va='bottom', fontsize=7)
        ax.text(i, v + 1.5, f'{v:.0f}', ha='center', va='bottom', fontsize=7, fontweight='bold')
        ax.text(i + width, e + 1.5, f'{e:.0f}', ha='center', va='bottom', fontsize=7)

    # Add improvement arrows
    for i, (b, v) in enumerate(zip(baselines, visible)):
        if v > b:
            ax.annotate('', xy=(i, v - 2), xytext=(i - width + 0.08, b + 2),
                       arrowprops=dict(arrowstyle='->', lw=1.2, color=COLORS['glm']))

    ax.set_ylabel('Changed-Winner PairAcc (%)', fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([m['model'].split('/')[-1] for m in models_data])
    ax.set_ylim(0, 80)
    ax.legend(loc='upper left', frameon=True, fontsize=7)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_title('Decision Visibility Improves PairAcc Across Models', fontsize=9, fontweight='bold', pad=8)


def plot_substitution_rates(ax, data: dict) -> None:
    """Plot conditional substitution rates before/after decision visibility."""
    models_data = data['models']

    x_pos = np.arange(len(models_data))
    width = 0.35

    history_subs = []
    visible_subs = []

    for model_data in models_data:
        hist = model_data['metrics']['history_only']['preserve_conditional_substitution']
        history_subs.append(hist['rate'] * 100)

        vis = model_data['metrics']['decision_visible']['preserve_conditional_substitution']
        visible_subs.append(vis['rate'] * 100)

    bars1 = ax.bar(x_pos - width/2, history_subs, width, label='History Only',
                   color=COLORS['accent'], alpha=0.6, edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x_pos + width/2, visible_subs, width, label='Decision Visible',
                   color=COLORS['glm'], alpha=0.8, edgecolor='black', linewidth=0.5)

    # Add value labels and confidence intervals
    for i, (h, v) in enumerate(zip(history_subs, visible_subs)):
        ax.text(i - width/2, h + 2, f'{h:.1f}%', ha='center', va='bottom', fontsize=7)
        ax.text(i + width/2, v + 2, f'{v:.1f}%', ha='center', va='bottom', fontsize=7, fontweight='bold')

        # Add CI error bars
        model_data = models_data[i]
        hist_ci = model_data['metrics']['history_only']['preserve_conditional_substitution']['ci95_state_cluster']
        vis_ci = model_data['metrics']['decision_visible']['preserve_conditional_substitution']['ci95_state_cluster']

        hist_err = [(h - hist_ci[0]*100), (hist_ci[1]*100 - h)]
        vis_err = [(v - vis_ci[0]*100), (vis_ci[1]*100 - v)]

        ax.errorbar(i - width/2, h, yerr=[[hist_err[0]], [hist_err[1]]],
                   fmt='none', ecolor='black', capsize=3, linewidth=1, alpha=0.6)
        ax.errorbar(i + width/2, v, yerr=[[vis_err[0]], [vis_err[1]]],
                   fmt='none', ecolor='black', capsize=3, linewidth=1, alpha=0.6)

    ax.set_ylabel('Preserve Substitution Rate (%)', fontweight='bold')
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([m['model'].split('/')[-1] for m in models_data])
    ax.set_ylim(0, 85)
    ax.legend(loc='upper right', frameon=True, fontsize=7)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_title('Decision Visibility Eliminates Wrong-Target Substitutions', fontsize=9, fontweight='bold', pad=8)

    # Add annotation for dramatic drops
    for i, (h, v) in enumerate(zip(history_subs, visible_subs)):
        if h > 40 and v < 5:
            ax.annotate(f'↓{h-v:.0f}pp', xy=(i, (h+v)/2), fontsize=8,
                       color=COLORS['glm'], fontweight='bold', ha='center')


def plot_enforcement_effects(ax, data: dict) -> None:
    """Plot enforcement repairs vs harms."""
    models_data = data['models']

    models = [m['model'].split('/')[-1] for m in models_data]
    repairs = [m['enforcement']['repair_rate']['rate'] * 100 for m in models_data]
    harms = [m['enforcement']['harm_rate']['rate'] * 100 for m in models_data]

    x_pos = np.arange(len(models))

    # Diverging bar chart
    ax.barh(x_pos, repairs, height=0.35, label='Repairs',
            color=COLORS['glm'], alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.barh(x_pos, [-h for h in harms], height=0.35, label='Harms',
            color=COLORS['accent'], alpha=0.8, edgecolor='black', linewidth=0.5)

    # Add value labels
    for i, (r, h) in enumerate(zip(repairs, harms)):
        if r > 0:
            ax.text(r + 0.5, i, f'{r:.1f}%', va='center', fontsize=7, fontweight='bold')
        if h > 0:
            ax.text(-h - 0.5, i, f'{h:.1f}%', va='center', ha='right', fontsize=7, fontweight='bold')

    ax.set_yticks(x_pos)
    ax.set_yticklabels(models)
    ax.set_xlabel('Effect Rate (%)', fontweight='bold')
    ax.set_xlim(-12, 8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.legend(loc='upper left', frameon=True, fontsize=7)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_title('Enforcement: Mixed Effects', fontsize=9, fontweight='bold', pad=8)


def plot_accuracy_breakdown(ax, data: dict) -> None:
    """Plot preserve vs reevaluate accuracy breakdown."""
    models_data = data['models']

    conditions = ['History\nOnly', 'Decision\nVisible', 'Decision\nEnforced']

    for idx, model_data in enumerate(models_data):
        model_name = model_data['model'].split('/')[-1]
        color = COLORS['qwen'] if 'Qwen' in model_name else COLORS['glm']

        preserve_accs = []
        reeval_accs = []

        for cond in ['history_only', 'decision_visible', 'decision_enforced']:
            preserve_accs.append(model_data['metrics'][cond]['preserve_e2e']['rate'] * 100)
            reeval_accs.append(model_data['metrics'][cond]['reevaluate_e2e']['rate'] * 100)

        x_offset = idx * 0.3 - 0.15
        x_pos = np.arange(len(conditions)) + x_offset

        ax.plot(x_pos, preserve_accs, marker='o', label=f'{model_name} Preserve' if idx == 0 else None,
               color=color, linestyle='--', alpha=0.7, markersize=5)
        ax.plot(x_pos, reeval_accs, marker='s', label=f'{model_name} Reevaluate' if idx == 0 else None,
               color=color, linestyle='-', alpha=0.9, markersize=5)

    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_xticks(np.arange(len(conditions)))
    ax.set_xticklabels(conditions, fontsize=7)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right', frameon=True, fontsize=6)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_title('Preserve vs Reevaluate Breakdown', fontsize=9, fontweight='bold', pad=8)


def plot_metrics_heatmap(ax, data: dict) -> None:
    """Plot comprehensive metrics heatmap."""
    models_data = data['models']

    metrics_names = ['E2E Acc', 'PairAcc', 'Preserve Acc', 'Reeval Acc', 'Subst Rate']
    conditions = []
    matrix = []

    for model_data in models_data:
        model_name = model_data['model'].split('/')[-1]

        for cond_key, cond_label in [('history_only', 'History'),
                                      ('decision_visible', 'Visible'),
                                      ('decision_enforced', 'Enforced')]:
            conditions.append(f"{model_name}\n{cond_label}")
            metrics = model_data['metrics'][cond_key]

            row = [
                metrics['e2e']['rate'] * 100,
                metrics['changed_pairacc']['rate'] * 100,
                metrics['preserve_e2e']['rate'] * 100,
                metrics['reevaluate_e2e']['rate'] * 100,
                metrics['preserve_conditional_substitution']['rate'] * 100,
            ]
            matrix.append(row)

    matrix = np.array(matrix).T

    # Create heatmap with annotations
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    # Add text annotations
    for i in range(len(metrics_names)):
        for j in range(len(conditions)):
            value = matrix[i, j]
            text_color = 'white' if value < 50 else 'black'
            ax.text(j, i, f'{value:.1f}', ha='center', va='center',
                   fontsize=7, fontweight='bold', color=text_color)

    ax.set_xticks(np.arange(len(conditions)))
    ax.set_xticklabels(conditions, rotation=45, ha='right', fontsize=7)
    ax.set_yticks(np.arange(len(metrics_names)))
    ax.set_yticklabels(metrics_names, fontsize=8)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Performance (%)', rotation=270, labelpad=15, fontweight='bold', fontsize=8)

    ax.set_title('Comprehensive Metrics Matrix', fontsize=9, fontweight='bold', pad=8)


def main():
    parser = argparse.ArgumentParser(description='Generate comprehensive TRI figures')
    parser.add_argument('--ablation-data', type=Path,
                       default=Path('reports/call_matched_authorization_ablation_v2.json'))
    parser.add_argument('--output-dir', type=Path,
                       default=Path('reports/figures'))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    ablation_data = load_ablation_data(args.ablation_data)

    # Create comprehensive panel figure
    output_path = args.output_dir / 'tri_comprehensive_analysis.pdf'
    create_comprehensive_panel_figure(output_path, ablation_data)

    print("All comprehensive figures generated successfully!")


if __name__ == '__main__':
    main()
