#!/usr/bin/env python3
"""
Generate publication-quality figures for TRI paper.
Strict evidence boundaries, unified visual system, no decoration.
"""
from __future__ import annotations

import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# Unified color system
INK = '#17212B'
MUTED = '#5B6570'
LINE = '#CBD2D9'
GENERIC_COLOR = '#7A8793'
CTA_COLOR = '#126F66'
LIFECYCLE_COLOR = '#126F66'
RULE_COLOR = '#B64926'
PALE_GREEN = '#E8F3F1'
PALE_ORANGE = '#F8ECE7'
WARN_COLOR = '#D4604A'
NULL_COLOR = '#9BA4AD'

# Font settings
plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['axes.titlesize'] = 9
plt.rcParams['xtick.labelsize'] = 7
plt.rcParams['ytick.labelsize'] = 7
plt.rcParams['legend.fontsize'] = 7
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42


def make_figure_2_core_diagnostic():
    """
    Figure 2: Core diagnostic logic and evidence ladder.
    4-panel: (A) Identifiability table, (B) Evidence chronology,
             (C) Primary actionable core, (D) Method boundary.
    """
    fig = plt.figure(figsize=(7.0, 5.5))

    from matplotlib.gridspec import GridSpec
    gs = GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35,
                  left=0.08, right=0.98, top=0.96, bottom=0.08)

    # Panel A: Policy identifiability (simplified from Table 2)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.axis('off')
    ax_a.set_xlim(0, 10)
    ax_a.set_ylim(0, 10)

    ax_a.text(5, 9.5, 'A  Policy Identifiability', ha='center', fontsize=9, weight='bold')

    # Draw table
    regimes = ['Stable only', 'Preserve only', 'Reevaluate only', 'Changed pair']
    lock_pass = [True, True, False, False]
    reeval_pass = [True, False, True, False]
    y_pos = 8.4

    ax_a.text(2, y_pos, 'Regime', fontsize=7, weight='bold')
    ax_a.text(5, y_pos, 'Lock', fontsize=7, weight='bold')
    ax_a.text(7.5, y_pos, 'Reeval', fontsize=7, weight='bold')

    for i, regime in enumerate(regimes):
        y = y_pos - (i + 1) * 1.3
        ax_a.text(2, y, regime, fontsize=7)

        # Lock status
        lock_marker = 'pass' if lock_pass[i] else 'fail'
        lock_color = CTA_COLOR if lock_pass[i] else WARN_COLOR
        ax_a.text(5, y, lock_marker, fontsize=6.5, color=lock_color, ha='center', weight='bold')

        # Reeval status
        reeval_marker = 'pass' if reeval_pass[i] else 'fail'
        reeval_color = CTA_COLOR if reeval_pass[i] else WARN_COLOR
        ax_a.text(7.5, y, reeval_marker, fontsize=6.5, color=reeval_color, ha='center', weight='bold')

    # Annotation
    ax_a.add_patch(Rectangle((0.5, 0.55), 9, 1.55, fill=True,
                             facecolor=PALE_ORANGE, edgecolor=LINE, linewidth=0.5))
    ax_a.text(5, 1.55, 'Only changed-winner PairAcc', ha='center', fontsize=6.5, style='italic')
    ax_a.text(5, 0.95, 'rejects both unconditional policies', ha='center', fontsize=6.5, style='italic')

    # Panel B: Evidence chronology
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.axis('off')
    ax_b.set_xlim(0, 10)
    ax_b.set_ylim(0, 10)

    ax_b.text(5, 9.5, 'B  Evidence Status', ha='center', fontsize=9, weight='bold')

    evidence_stages = [
        ('Primary/Frozen', 'Matched Timing Diagnostic', CTA_COLOR),
        ('Post-primary', 'Cross-Schema Replication', CTA_COLOR),
        ('Post-primary', 'Full matched-call confirmation', CTA_COLOR),
        ('Post-primary', 'External audits (mostly null)', NULL_COLOR),
        ('Post-hoc', 'Deterministic Rule*', RULE_COLOR),
    ]

    y_start = 8.2
    for i, (status, desc, color) in enumerate(evidence_stages):
        y = y_start - i * 1.5
        # Status box
        ax_b.add_patch(Rectangle((0.5, y - 0.3), 2.2, 0.8,
                                fill=True, facecolor=color, alpha=0.2,
                                edgecolor=color, linewidth=1))
        ax_b.text(1.6, y, status, fontsize=6.5, ha='center', weight='bold')

        # Description
        ax_b.text(3.2, y, desc, fontsize=7, va='center')

    # Legend note
    ax_b.text(5, 0.8, 'Green=supports construct | Gray=null | Orange=post-hoc',
             ha='center', fontsize=6, style='italic', color=MUTED)

    # Panel C: Primary actionable core (128 tasks)
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.set_xlim(-0.5, 2.5)
    ax_c.set_ylim(0, 105)
    ax_c.set_xticks([0, 1, 2])
    ax_c.set_xticklabels(['Generic', 'CTA', 'Gated'], fontsize=7)
    ax_c.set_ylabel('Accuracy (%)', fontsize=8)
    ax_c.set_title('C  Actionable Core (128 tasks)', fontsize=9, weight='bold', loc='left')
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)
    ax_c.grid(axis='y', alpha=0.3, linewidth=0.5)

    # Data from paper: actionable core accuracy
    qwen_data = [74.2, 98.4, 97.7]
    glm_data = [72.7, 99.2, 100.0]

    width = 0.35
    x = np.array([0, 1, 2])

    bars1 = ax_c.bar(x - width/2, qwen_data, width, label='Qwen',
                     color=GENERIC_COLOR, edgecolor=INK, linewidth=0.5)
    bars2 = ax_c.bar(x + width/2, glm_data, width, label='GLM',
                     color=CTA_COLOR, edgecolor=INK, linewidth=0.5)

    # Annotations
    for i, (q, g) in enumerate(zip(qwen_data, glm_data)):
        ax_c.text(i - width/2, q + 2, f'{q:.1f}', ha='center', fontsize=6.5)
        ax_c.text(i + width/2, g + 2, f'{g:.1f}', ha='center', fontsize=6.5)

    ax_c.legend(loc='lower right', frameon=False)
    ax_c.set_ylim(0, 108)

    # Panel D: Method attribution boundary
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.axis('off')
    ax_d.set_xlim(0, 12)
    ax_d.set_ylim(0, 10)

    ax_d.text(6, 9.5, 'D  Controller and Rule Comparison', ha='center', fontsize=9, weight='bold')

    # Comparison on the primary 160-task diagnostic.
    methods = ['Generic', 'Mode only', 'Untyped plan', 'CTA', 'Rule*', 'Gated']
    qwen_acc = [64.4, 75.0, 81.2, 95.0, 92.5, 98.1]
    glm_acc = [71.9, 75.0, 70.6, 96.2, 92.5, 100.0]

    y_start = 8.2
    for i, method in enumerate(methods):
        y = y_start - i * 1.3

        # Method name
        is_posthoc = '*' in method
        color = RULE_COLOR if is_posthoc else INK
        ax_d.text(0.5, y, method, fontsize=7, color=color,
                 weight='bold' if is_posthoc else 'normal')

        # Qwen bar
        bar_width = qwen_acc[i] / 100 * 3.2
        ax_d.add_patch(Rectangle((3.5, y - 0.2), bar_width, 0.4,
                                facecolor=GENERIC_COLOR, edgecolor=GENERIC_COLOR))
        ax_d.text(3.5 + bar_width + 0.1, y, f'{qwen_acc[i]:.1f}', fontsize=6.5, va='center')

        # GLM bar
        bar_width_glm = glm_acc[i] / 100 * 3.2
        ax_d.add_patch(Rectangle((8.0, y - 0.2), bar_width_glm, 0.4,
                                facecolor=CTA_COLOR, edgecolor=CTA_COLOR))
        ax_d.text(8.0 + bar_width_glm + 0.1, y, f'{glm_acc[i]:.1f}', fontsize=6.5, va='center')

    # Column headers
    ax_d.text(5.1, 9.0, 'Qwen', fontsize=7, ha='center', weight='bold', color=GENERIC_COLOR)
    ax_d.text(9.6, 9.0, 'GLM', fontsize=7, ha='center', weight='bold', color=CTA_COLOR)

    # Note
    ax_d.text(6, 0.5, '*Post-hoc rule matches CTA on authored templates',
             ha='center', fontsize=6, style='italic', color=RULE_COLOR)

    return fig


def make_figure_3_replication():
    """
    Figure 3: Cross-model replication and attribution decomposition.
    Replaces existing Figure 2 with clearer evidence boundaries.
    """
    # Load data
    reports_dir = Path('experiments/tri_artifact/reports')
    v7_data = json.loads((reports_dir / 'v7_shared_eligible_pairacc_v1.json').read_text())
    ablation_data = json.loads((reports_dir / 'call_matched_authorization_ablation_v2.json').read_text())

    fig = plt.figure(figsize=(7.0, 5.0))

    from matplotlib.gridspec import GridSpec
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.35,
                  left=0.10, right=0.98, top=0.96, bottom=0.08)

    # Panel A: Changed-winner PairAcc across models
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_title('A  Changed-Winner PairAcc', fontsize=9, weight='bold', loc='left')
    ax_a.set_ylabel('PairAcc (%)', fontsize=8)
    ax_a.set_ylim(0, 105)
    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)
    ax_a.grid(axis='y', alpha=0.3, linewidth=0.5)

    models = ['Qwen', 'GLM', 'DeepSeek']
    generic_pairacc = [8.75, 18.75, 21.25]  # 7/80, 15/80, 17/80
    cta_pairacc = [38.75, 82.5, 80.0]  # 31/80, 66/80, 64/80

    x = np.arange(len(models))
    width = 0.35

    bars1 = ax_a.bar(x - width/2, generic_pairacc, width, label='Generic',
                     color=GENERIC_COLOR, edgecolor=INK, linewidth=0.5)
    bars2 = ax_a.bar(x + width/2, cta_pairacc, width, label='CTA',
                     color=CTA_COLOR, edgecolor=INK, linewidth=0.5)

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(models, fontsize=7)
    ax_a.legend(loc='upper left', bbox_to_anchor=(0.01, 0.88), frameon=False)

    # Annotations with CIs
    cis = ['+30.0\n[+16.2, +43.8]', '+63.7\n[+52.5, +75.0]', '+58.8\n[+43.8, +72.5]']
    for i, ci in enumerate(cis):
        ax_a.text(i, cta_pairacc[i] + 4, ci, ha='center', fontsize=5.7,
                  color=CTA_COLOR, va='bottom')

    # Panel B: Conditional substitution (shared-eligible)
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_title('B  Conditional Substitution', fontsize=9, weight='bold', loc='left')
    ax_b.set_ylabel('Substitution rate', fontsize=8)
    ax_b.set_ylim(0, 1.05)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.grid(axis='y', alpha=0.3, linewidth=0.5)

    # Shared-eligible substitutions
    generic_subst = [41/66, 30/70, 50/69]
    cta_subst = [0, 0, 0]

    bars1 = ax_b.bar(x - width/2, generic_subst, width, label='Generic',
                     color=WARN_COLOR, edgecolor=INK, linewidth=0.5, alpha=0.8)
    bars2 = ax_b.bar(x + width/2, cta_subst, width, label='CTA',
                     color=CTA_COLOR, edgecolor=INK, linewidth=0.5)

    ax_b.set_xticks(x)
    ax_b.set_xticklabels(models, fontsize=7)
    ax_b.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_b.set_yticklabels(['0', '25%', '50%', '75%', '100%'])

    # Fraction annotations
    fracs = ['41/66', '30/70', '50/69']
    for i, frac in enumerate(fracs):
        ax_b.text(i - width/2, generic_subst[i] + 0.03, frac,
                 ha='center', fontsize=6, color=WARN_COLOR)
        ax_b.text(i + width/2, 0.03, '0', ha='center', fontsize=6, color=CTA_COLOR)

    ax_b.text(1, 0.98, 'Observed CTA count: 0', ha='center', fontsize=6,
             style='italic', color=MUTED, bbox=dict(boxstyle='round,pad=0.3',
             facecolor='white', edgecolor=LINE, linewidth=0.5))

    # Panel C: Call-matched ablation
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.set_title('C  Earlier matched-call test (40 changed pairs)', fontsize=9, weight='bold', loc='left')
    ax_c.set_ylabel('PairAcc (%)', fontsize=8)
    ax_c.set_ylim(0, 75)
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)
    ax_c.grid(axis='y', alpha=0.3, linewidth=0.5)

    conditions = ['History', 'Visible', 'Enforced']
    qwen_pairacc = [30.0, 50.0, 42.5]
    glm_pairacc = [30.0, 60.0, 60.0]

    x_cond = np.arange(len(conditions))
    ax_c.plot(x_cond, qwen_pairacc, 'o-', color=GENERIC_COLOR,
             linewidth=1.5, markersize=5, label='Qwen')
    ax_c.plot(x_cond, glm_pairacc, 's-', color=CTA_COLOR,
             linewidth=1.5, markersize=5, label='GLM')

    ax_c.set_xticks(x_cond)
    ax_c.set_xticklabels(conditions, fontsize=7)
    ax_c.legend(loc='upper left', frameon=False)

    # Annotations
    ax_c.text(0.5, 55, '+20.0\n[+2.5, +37.5]', ha='center', fontsize=6, color=GENERIC_COLOR, va='bottom')
    ax_c.text(0.5, 65, '+30.0\n[+17.5, +45.0]', ha='center', fontsize=6, color=CTA_COLOR, va='bottom')

    # Panel D: Wrong writes (consequence)
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.set_title('D  Wrong-Entity Writes (240 tasks)', fontsize=9, weight='bold', loc='left')
    ax_d.set_ylabel('Wrong writes', fontsize=8)
    ax_d.set_ylim(0, 70)
    ax_d.spines['top'].set_visible(False)
    ax_d.spines['right'].set_visible(False)
    ax_d.grid(axis='y', alpha=0.3, linewidth=0.5)

    x_models = np.arange(3)
    generic_writes = [44, 38, 60]
    cta_writes = [8, 14, 17]

    bars1 = ax_d.bar(x_models - width/2, generic_writes, width, label='Generic',
                     color=WARN_COLOR, edgecolor=INK, linewidth=0.5, alpha=0.8)
    bars2 = ax_d.bar(x_models + width/2, cta_writes, width, label='CTA',
                     color=CTA_COLOR, edgecolor=INK, linewidth=0.5)

    ax_d.set_xticks(x_models)
    ax_d.set_xticklabels(models, fontsize=7)
    ax_d.legend(loc='upper right', frameon=False)

    # Annotations
    for i, (g, c) in enumerate(zip(generic_writes, cta_writes)):
        ax_d.text(i - width/2, g + 2, str(g), ha='center', fontsize=6.5, color=WARN_COLOR)
        ax_d.text(i + width/2, c + 2, str(c), ha='center', fontsize=6.5, color=CTA_COLOR)

    ax_d.text(1, 68, 'CTA writes are non-TRI errors', ha='center',
             fontsize=6, style='italic', color=MUTED, bbox=dict(boxstyle='round,pad=0.3',
             facecolor='white', edgecolor=LINE, linewidth=0.5))

    return fig


if __name__ == '__main__':
    output_dir = Path('experiments/tri_artifact/reports/figures')
    output_dir.mkdir(exist_ok=True, parents=True)

    paper_dir = Path('paper/Figures')
    paper_dir.mkdir(exist_ok=True, parents=True)

    print("Generating Figure 2: Core diagnostic logic...")
    fig2 = make_figure_2_core_diagnostic()
    fig2.savefig(output_dir / 'tri_core_diagnostic.pdf', dpi=300, bbox_inches='tight')
    fig2.savefig(paper_dir / 'tri_core_diagnostic.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig2)

    print("Generating Figure 3: Replication and attribution...")
    fig3 = make_figure_3_replication()
    fig3.savefig(output_dir / 'tri_replication_attribution.pdf', dpi=300, bbox_inches='tight')
    fig3.savefig(paper_dir / 'tri_replication_attribution.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig3)

    print("Done. Figures saved to:")
    print(f"  {output_dir}")
    print(f"  {paper_dir}")
