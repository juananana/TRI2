"""
Mechanism and workflow visualization for TRI paper.
Creates timeline, flow diagrams, and conceptual illustrations.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 8

COLORS = {
    'preserve': '#E8F3F1',
    'reevaluate': '#F8ECE7',
    'bind': '#126F66',
    'refresh': '#7A8793',
    'write': '#B64926',
    'state': '#CBD2D9',
}


def create_temporal_flow_diagram(output_path: Path) -> None:
    """
    Create a comprehensive temporal flow showing:
    - Timeline with events
    - State transitions
    - Decision points
    - Authorization boundaries
    """
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6),
                            gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.4})

    fig.suptitle('Temporal Referent Integrity: Timeline and Decision Flow',
                fontsize=11, fontweight='bold', y=0.96)

    # Panel A: Preserve flow
    plot_preserve_timeline(axes[0])
    axes[0].text(-0.08, 1.05, 'A', transform=axes[0].transAxes,
                fontsize=12, fontweight='bold', va='top')

    # Panel B: Reevaluate flow
    plot_reevaluate_timeline(axes[1])
    axes[1].text(-0.08, 1.05, 'B', transform=axes[1].transAxes,
                fontsize=12, fontweight='bold', va='top')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created temporal flow diagram: {output_path}")


def plot_preserve_timeline(ax):
    """Plot preserve timeline with binding before refresh."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    ax.text(5, 3.7, 'PRESERVE: "Choose A now, refresh, then act on it"',
           ha='center', fontsize=9, fontweight='bold', color=COLORS['bind'])

    # Timeline
    timeline_y = 2.5
    ax.plot([0.5, 9.5], [timeline_y, timeline_y], 'k-', linewidth=2)

    # Events
    events = [
        (1.5, 'Observe\nS₀', COLORS['state']),
        (3.5, 'Bind\nA', COLORS['bind']),
        (5.5, 'Refresh\nS₀→S₁', COLORS['refresh']),
        (7.5, 'Write\nA', COLORS['write']),
    ]

    for x, label, color in events:
        # Event marker
        circle = Circle((x, timeline_y), 0.15, color=color, ec='black',
                       linewidth=1.5, zorder=10)
        ax.add_patch(circle)

        # Label
        ax.text(x, timeline_y - 0.6, label, ha='center', va='top',
               fontsize=8, fontweight='bold')

    # State boxes
    state_y = 1.0
    # S0
    rect1 = FancyBboxPatch((0.5, state_y - 0.3), 2.5, 0.6,
                          boxstyle="round,pad=0.05",
                          facecolor=COLORS['state'],
                          edgecolor='black', linewidth=1)
    ax.add_patch(rect1)
    ax.text(1.75, state_y, 'S₀: A wins q', ha='center', va='center',
           fontsize=8, fontweight='bold')

    # S1
    rect2 = FancyBboxPatch((5, state_y - 0.3), 3, 0.6,
                          boxstyle="round,pad=0.05",
                          facecolor=COLORS['state'],
                          edgecolor='black', linewidth=1)
    ax.add_patch(rect2)
    ax.text(6.5, state_y, 'S₁: B wins q, A valid', ha='center', va='center',
           fontsize=8, fontweight='bold')

    # Authorization highlight
    auth_box = FancyBboxPatch((3, 3.2), 1.5, 0.5,
                             boxstyle="round,pad=0.05",
                             facecolor=COLORS['preserve'],
                             edgecolor=COLORS['bind'], linewidth=2)
    ax.add_patch(auth_box)
    ax.text(3.75, 3.45, 'B(A)', ha='center', va='center',
           fontsize=9, fontweight='bold', color=COLORS['bind'])

    # Result annotation
    result_box = FancyBboxPatch((7, 0.1), 2, 0.5,
                               boxstyle="round,pad=0.05",
                               facecolor='lightgreen', alpha=0.4,
                               edgecolor='green', linewidth=1.5)
    ax.add_patch(result_box)
    ax.text(8, 0.35, '✓ Correct: Write A', ha='center', va='center',
           fontsize=8, fontweight='bold', color='darkgreen')


def plot_reevaluate_timeline(ax):
    """Plot reevaluate timeline with binding after refresh."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    ax.text(5, 3.7, 'REEVALUATE: "Refresh first, then choose and act on winner"',
           ha='center', fontsize=9, fontweight='bold', color=COLORS['write'])

    # Timeline
    timeline_y = 2.5
    ax.plot([0.5, 9.5], [timeline_y, timeline_y], 'k-', linewidth=2)

    # Events
    events = [
        (1.5, 'Observe\nS₀', COLORS['state']),
        (3.5, 'Refresh\nS₀→S₁', COLORS['refresh']),
        (5.5, 'Bind\nB', COLORS['bind']),
        (7.5, 'Write\nB', COLORS['write']),
    ]

    for x, label, color in events:
        circle = Circle((x, timeline_y), 0.15, color=color, ec='black',
                       linewidth=1.5, zorder=10)
        ax.add_patch(circle)
        ax.text(x, timeline_y - 0.6, label, ha='center', va='top',
               fontsize=8, fontweight='bold')

    # State boxes
    state_y = 1.0
    rect1 = FancyBboxPatch((0.5, state_y - 0.3), 2.5, 0.6,
                          boxstyle="round,pad=0.05",
                          facecolor=COLORS['state'],
                          edgecolor='black', linewidth=1)
    ax.add_patch(rect1)
    ax.text(1.75, state_y, 'S₀: A wins q', ha='center', va='center',
           fontsize=8, fontweight='bold')

    rect2 = FancyBboxPatch((3.5, state_y - 0.3), 4.5, 0.6,
                          boxstyle="round,pad=0.05",
                          facecolor=COLORS['state'],
                          edgecolor='black', linewidth=1)
    ax.add_patch(rect2)
    ax.text(6, state_y, 'S₁: B wins q, A valid', ha='center', va='center',
           fontsize=8, fontweight='bold')

    # Authorization highlight
    auth_box = FancyBboxPatch((5, 3.2), 1.5, 0.5,
                             boxstyle="round,pad=0.05",
                             facecolor=COLORS['reevaluate'],
                             edgecolor=COLORS['write'], linewidth=2)
    ax.add_patch(auth_box)
    ax.text(5.75, 3.45, 'U(q)→B(B)', ha='center', va='center',
           fontsize=9, fontweight='bold', color=COLORS['write'])

    # Result annotation
    result_box = FancyBboxPatch((7, 0.1), 2, 0.5,
                               boxstyle="round,pad=0.05",
                               facecolor='lightgreen', alpha=0.4,
                               edgecolor='green', linewidth=1.5)
    ax.add_patch(result_box)
    ax.text(8, 0.35, '✓ Correct: Write B', ha='center', va='center',
           fontsize=8, fontweight='bold', color='darkgreen')


def create_controller_architecture_diagram(output_path: Path) -> None:
    """
    Create diagram showing controller architectures:
    - Generic (implicit state)
    - CTA (explicit compile)
    - Lifecycle (typed + gated)
    """
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.5))
    fig.suptitle('Controller Architectures for Temporal Referent Integrity',
                fontsize=11, fontweight='bold', y=0.96)

    plot_generic_architecture(axes[0])
    axes[0].text(-0.15, 1.05, 'A', transform=axes[0].transAxes,
                fontsize=12, fontweight='bold', va='top')
    axes[0].set_title('Generic\n(Implicit)', fontsize=9, fontweight='bold', pad=10)

    plot_cta_architecture(axes[1])
    axes[1].text(-0.15, 1.05, 'B', transform=axes[1].transAxes,
                fontsize=12, fontweight='bold', va='top')
    axes[1].set_title('CTA\n(Compile-Then-Act)', fontsize=9, fontweight='bold', pad=10)

    plot_lifecycle_architecture(axes[2])
    axes[2].text(-0.15, 1.05, 'C', transform=axes[2].transAxes,
                fontsize=12, fontweight='bold', va='top')
    axes[2].set_title('Lifecycle-Gated\n(Typed + Enforced)', fontsize=9, fontweight='bold', pad=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Created controller architecture diagram: {output_path}")


def plot_generic_architecture(ax):
    """Plot Generic controller architecture."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Components
    components = [
        (5, 8.5, 'Instruction', '#CBD2D9', 1.5, 0.6),
        (5, 7.0, 'Model\nCall 1', '#AAB2BA', 1.8, 0.7),
        (5, 5.5, 'Store:\nID, State,\nSelector', '#7A8793', 2.0, 0.8),
        (5, 4.0, 'Refresh', '#5B6570', 1.5, 0.6),
        (5, 2.5, 'Model\nCall 2', '#AAB2BA', 1.8, 0.7),
        (5, 1.0, 'Execute', '#B64926', 1.5, 0.6),
    ]

    for x, y, label, color, w, h in components:
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                             boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center',
               fontsize=7, fontweight='bold', color='white')

    # Arrows
    for i in range(len(components) - 1):
        y1 = components[i][1] - components[i][5]/2
        y2 = components[i+1][1] + components[i+1][5]/2
        ax.annotate('', xy=(5, y2), xytext=(5, y1),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    # Annotation
    ax.text(8, 5, '⚠\nImplicit\nresolution\ntiming', ha='center', va='center',
           fontsize=7, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))


def plot_cta_architecture(ax):
    """Plot CTA controller architecture."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    components = [
        (5, 8.5, 'Instruction', '#CBD2D9', 1.5, 0.6),
        (5, 7.0, 'Compiler', '#126F66', 1.8, 0.7),
        (5, 5.5, 'Store:\nMode,\nBound ID,\nSelector', '#69B7AA', 2.2, 0.8),
        (5, 4.0, 'Refresh', '#5B6570', 1.5, 0.6),
        (5, 2.5, 'Actor\n(+decision)', '#126F66', 1.8, 0.7),
        (5, 1.0, 'Execute', '#B64926', 1.5, 0.6),
    ]

    for x, y, label, color, w, h in components:
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                             boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        text_color = 'white' if y < 6 else 'black'
        ax.text(x, y, label, ha='center', va='center',
               fontsize=7, fontweight='bold', color=text_color)

    for i in range(len(components) - 1):
        y1 = components[i][1] - components[i][5]/2
        y2 = components[i+1][1] + components[i+1][5]/2
        ax.annotate('', xy=(5, y2), xytext=(5, y1),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    ax.text(8, 5, '✓\nExplicit\ncompiled\ndecision', ha='center', va='center',
           fontsize=7, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.4))


def plot_lifecycle_architecture(ax):
    """Plot Lifecycle-Gated controller architecture."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    components = [
        (5, 8.5, 'Instruction', '#CBD2D9', 1.5, 0.6),
        (5, 7.0, 'Compiler', '#126F66', 1.8, 0.7),
        (5, 5.5, 'Typed Record:\nMode, ID,\nSelector, Policy', '#69B7AA', 2.4, 0.8),
        (5, 4.0, 'Refresh', '#5B6570', 1.5, 0.6),
    ]

    for x, y, label, color, w, h in components:
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                             boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        text_color = 'black' if y > 6 else 'white'
        ax.text(x, y, label, ha='center', va='center',
               fontsize=7, fontweight='bold', color=text_color)

    # Branching paths
    # Gate box
    gate = FancyBboxPatch((2.5, 2.3), 2, 0.8,
                         boxstyle="round,pad=0.05",
                         facecolor='#126F66', edgecolor='black', linewidth=1.5)
    ax.add_patch(gate)
    ax.text(3.5, 2.7, 'Gate:\nCheck\nValidity', ha='center', va='center',
           fontsize=7, fontweight='bold', color='white')

    # Actor box
    actor = FancyBboxPatch((5.5, 2.3), 2, 0.8,
                          boxstyle="round,pad=0.05",
                          facecolor='#69B7AA', edgecolor='black', linewidth=1.5)
    ax.add_patch(actor)
    ax.text(6.5, 2.7, 'Actor:\nSelect\nfrom S₁', ha='center', va='center',
           fontsize=7, fontweight='bold')

    # Execute box
    execute = FancyBboxPatch((4, 0.7), 2, 0.6,
                            boxstyle="round,pad=0.05",
                            facecolor='#B64926', edgecolor='black', linewidth=1.5)
    ax.add_patch(execute)
    ax.text(5, 1.0, 'Execute', ha='center', va='center',
           fontsize=7, fontweight='bold', color='white')

    # Arrows
    for i in range(len(components) - 1):
        y1 = components[i][1] - components[i][5]/2
        y2 = components[i+1][1] + components[i+1][5]/2
        ax.annotate('', xy=(5, y2), xytext=(5, y1),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    # Branch arrows
    ax.annotate('', xy=(3.5, 2.3), xytext=(4.5, 3.4),
               arrowprops=dict(arrowstyle='->', lw=1.2, color='black'))
    ax.text(4.0, 3.0, 'Preserve', fontsize=6, rotation=-45)

    ax.annotate('', xy=(6.5, 2.3), xytext=(5.5, 3.4),
               arrowprops=dict(arrowstyle='->', lw=1.2, color='black'))
    ax.text(6.0, 3.0, 'Reevaluate', fontsize=6, rotation=45)

    # Convergence arrows
    ax.annotate('', xy=(4.7, 1.3), xytext=(3.5, 2.3),
               arrowprops=dict(arrowstyle='->', lw=1.2, color='black'))
    ax.annotate('', xy=(5.3, 1.3), xytext=(6.5, 2.3),
               arrowprops=dict(arrowstyle='->', lw=1.2, color='black'))

    ax.text(8.2, 3.5, '✓✓\nTyped +\nDeterministic\nGate', ha='center', va='center',
           fontsize=7, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))


def main():
    parser = argparse.ArgumentParser(description='Generate mechanism flow figures')
    parser.add_argument('--output-dir', type=Path,
                       default=Path('reports/figures'))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    create_temporal_flow_diagram(
        args.output_dir / 'tri_temporal_flow_comprehensive.pdf')

    create_controller_architecture_diagram(
        args.output_dir / 'tri_controller_architectures.pdf')

    print("\nAll mechanism flow figures generated successfully!")


if __name__ == '__main__':
    main()
