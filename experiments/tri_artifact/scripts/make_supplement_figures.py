#!/usr/bin/env python3
"""
Supplementary figures for TRI paper.
Focus on external validity boundary and coverage audits.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# Reuse color system
INK = '#17212B'
MUTED = '#5B6570'
LINE = '#CBD2D9'
GENERIC_COLOR = '#7A8793'
CTA_COLOR = '#126F66'
NULL_COLOR = '#9BA4AD'
WARN_COLOR = '#D4604A'
PALE_GREEN = '#E8F3F1'
PALE_GRAY = '#F1F3F5'

plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['axes.titlesize'] = 9
plt.rcParams['xtick.labelsize'] = 7
plt.rcParams['ytick.labelsize'] = 7
plt.rcParams['legend.fontsize'] = 7
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42


def make_supplement_external_validity():
    """
    Supplement Figure: External validity boundary and human evidence.
    4-panel: (A) Public benchmark coverage, (B) Source-anchored transfer,
             (C) Human agreement slices, (D) Evidence boundary summary.
    """
    fig = plt.figure(figsize=(7.0, 6.5))

    from matplotlib.gridspec import GridSpec
    gs = GridSpec(2, 2, figure=fig, hspace=0.40, wspace=0.35,
                  left=0.10, right=0.98, top=0.96, bottom=0.08)

    # Panel A: Public benchmark strict opportunity coverage
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_title('A  Public Benchmark Coverage', fontsize=9, weight='bold', loc='left')
    ax_a.set_ylabel('Strict opportunities', fontsize=8)
    ax_a.set_ylim(-0.5, 7)
    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)
    ax_a.grid(axis='y', alpha=0.3, linewidth=0.5)

    benchmarks = ['ToolSandbox\n129 families', 'AppWorld\n244 families',
                  '$\\tau^3$-Bench\n2449 tasks', 'API-Bank\n528 units',
                  'BFCL\n800 variants', 'ToolTalk\n50 dialogues']
    opportunities = [0, 0, 0, 0, 0, 0]  # All zero strict opportunities
    near_matches = [1, 1, 0, 0, 0, 0]  # Near-matches noted in paper

    x = np.arange(len(benchmarks))
    bars = ax_a.bar(x, opportunities, color=NULL_COLOR, edgecolor=INK, linewidth=0.5, alpha=0.6)

    # Near-match markers
    for i, nm in enumerate(near_matches):
        if nm > 0:
            ax_a.scatter(i, 0.3, s=40, marker='o', color=WARN_COLOR,
                        edgecolor=INK, linewidth=0.5, zorder=5)
            ax_a.text(i, 0.6, f'{nm} near', ha='center', fontsize=6, color=WARN_COLOR)

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(benchmarks, fontsize=6, rotation=15, ha='right')
    ax_a.set_yticks([0, 2, 4, 6])

    ax_a.text(2.5, 6, 'Zero strict native opportunities under checklist',
             ha='center', fontsize=7, style='italic', color=NULL_COLOR)

    # Panel B: Source-anchored transfer (mixed results)
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_title('B  Source-Anchored Transfer', fontsize=9, weight='bold', loc='left')
    ax_b.set_ylabel('Substitution rate', fontsize=8)
    ax_b.set_ylim(0, 0.35)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.grid(axis='y', alpha=0.3, linewidth=0.5)

    sources = ['AgentDojo\nQwen', 'AgentDojo\nGLM', 'STATE-Bench\nQwen', 'STATE-Bench\nGLM']
    subst_rates = [2/7, 0, 0, 0]  # Only one positive slice

    x_sources = np.arange(len(sources))
    colors = [WARN_COLOR if s > 0 else NULL_COLOR for s in subst_rates]

    bars = ax_b.bar(x_sources, subst_rates, color=colors, edgecolor=INK,
                   linewidth=0.5, alpha=0.7)

    for i, rate in enumerate(subst_rates):
        if rate > 0:
            ax_b.text(i, rate + 0.01, f'{rate:.2f}', ha='center',
                     fontsize=6.5, color=WARN_COLOR)
        else:
            ax_b.text(i, 0.01, '0', ha='center', fontsize=6.5, color=NULL_COLOR)

    ax_b.set_xticks(x_sources)
    ax_b.set_xticklabels(sources, fontsize=6.5, rotation=12, ha='right')
    ax_b.set_yticks([0, 0.1, 0.2, 0.3])
    ax_b.set_yticklabels(['0', '10%', '20%', '30%'])

    ax_b.text(1.5, 0.32, 'Positive transfer in one slice only',
             ha='center', fontsize=6.5, style='italic', color=MUTED)

    # Panel C: Human validation construct slices
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.set_title('C  Human Agreement by Slice', fontsize=9, weight='bold', loc='left')
    ax_c.set_ylabel('Agreement (%)', fontsize=8)
    ax_c.set_ylim(0, 105)
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)
    ax_c.grid(axis='y', alpha=0.3, linewidth=0.5)

    slices = ['All\n(100)', 'Actionable\n(30)', 'Reject\n(20)', 'Dynamic\n(50)']
    maj_gold = [86.0, 86.7, 55.0, 98.0]  # Majority-gold agreement
    unanimous = [72.0, 63.3, 25.0, 96.0]  # Unanimity

    x_slices = np.arange(len(slices))
    width = 0.35

    bars1 = ax_c.bar(x_slices - width/2, maj_gold, width, label='Majority-gold',
                     color=CTA_COLOR, edgecolor=INK, linewidth=0.5)
    bars2 = ax_c.bar(x_slices + width/2, unanimous, width, label='Unanimous',
                     color=GENERIC_COLOR, edgecolor=INK, linewidth=0.5, alpha=0.7)

    ax_c.set_xticks(x_slices)
    ax_c.set_xticklabels(slices, fontsize=6.5)
    ax_c.legend(loc='lower left', frameon=False, fontsize=6.5)

    # Highlight weak Reject slice
    ax_c.add_patch(Rectangle((2 - width, 0), 2*width + 0.5, 60,
                             fill=True, facecolor=PALE_GRAY,
                             edgecolor=WARN_COLOR, linewidth=1, linestyle='--',
                             alpha=0.3, zorder=0))
    ax_c.text(2.25, 50, 'Weak\nsupport', ha='center', fontsize=6,
             color=WARN_COLOR, style='italic')

    # Panel D: Evidence boundary summary
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.axis('off')
    ax_d.set_xlim(0, 10)
    ax_d.set_ylim(0, 10)

    ax_d.text(5, 9.5, 'D  Evidence Boundary Summary', ha='center',
             fontsize=9, weight='bold')

    evidence_items = [
        ('✓', 'Controlled diagnostic pairs', CTA_COLOR),
        ('✓', 'Schema/state transfer (authored)', CTA_COLOR),
        ('✓', 'Human validation (referent core)', CTA_COLOR),
        ('✗', 'Open-language generalization', WARN_COLOR),
        ('✗', 'Public benchmark native coverage', WARN_COLOR),
        ('✗', 'Natural deployment prevalence', WARN_COLOR),
    ]

    y_start = 8.0
    for i, (marker, desc, color) in enumerate(evidence_items):
        y = y_start - i * 1.15

        # Marker
        ax_d.text(1.5, y, marker, fontsize=10, color=color,
                 ha='center', weight='bold')

        # Description
        ax_d.text(2.5, y, desc, fontsize=7, va='center', color=INK)

    # Interpretation note
    ax_d.add_patch(Rectangle((0.5, 0.5), 9, 1.1, fill=True,
                             facecolor=PALE_GREEN, edgecolor=CTA_COLOR,
                             linewidth=0.5))
    ax_d.text(5, 1.3, 'TRI is an evaluation-identifiability diagnostic',
             ha='center', fontsize=6.5, weight='bold', color=CTA_COLOR)
    ax_d.text(5, 0.7, 'for controlled workflows, not a prevalence estimate',
             ha='center', fontsize=6, style='italic', color=MUTED)

    return fig


if __name__ == '__main__':
    output_dir = Path('experiments/tri_artifact/reports/figures')
    output_dir.mkdir(exist_ok=True, parents=True)

    paper_dir = Path('paper/Figures')
    paper_dir.mkdir(exist_ok=True, parents=True)

    print("Generating Supplement Figure: External validity boundary...")
    fig_s1 = make_supplement_external_validity()
    fig_s1.savefig(output_dir / 'tri_external_validity.pdf', dpi=300, bbox_inches='tight')
    fig_s1.savefig(paper_dir / 'tri_external_validity.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig_s1)

    print("Done. Supplement figure saved.")
