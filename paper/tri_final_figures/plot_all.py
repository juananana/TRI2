from __future__ import annotations

import argparse
from pathlib import Path

from tri_figures.data import load_tables
from tri_figures.phase_space import build as build_phase_space
from tri_figures.target_flow import build as build_target_flow
from tri_figures.wrong_writes import build as build_wrong_writes
from tri_figures.effect_sizes import build as build_effect_sizes
from tri_figures.transfer_fingerprints import build as build_transfer
from tri_figures.enforcement import build as build_enforcement


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final TRI paper figures.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "outputs")
    args = parser.parse_args()

    tables = load_tables(args.data_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    build_phase_space(tables["phase"], args.output_dir / "fig_resolution_policy_phase_space")
    build_target_flow(tables["flow"], args.output_dir / "fig_shared_eligible_target_flow")
    build_wrong_writes(tables["writes"], args.output_dir / "fig_wrong_write_decomposition")
    build_effect_sizes(tables["gains"], args.output_dir / "fig_decision_visibility_effect_sizes")
    build_transfer(tables["transfer"], args.output_dir / "fig_source_model_transfer_fingerprints")
    build_enforcement(tables["enforcement"], args.output_dir / "fig_enforcement_repairs_harms")


if __name__ == "__main__":
    main()
