from __future__ import annotations

import argparse
from pathlib import Path

from tri_figures.column_figures import (
    build_effect_sizes,
    build_target_flow,
    build_transfer_fingerprints,
    build_wrong_writes,
)
from tri_figures.data import load_tables


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate single-column TRI paper figures.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "outputs")
    args = parser.parse_args()

    tables = load_tables(args.data_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    build_target_flow(tables["flow"], args.output_dir / "fig_shared_eligible_target_flow_column")
    build_wrong_writes(tables["writes"], args.output_dir / "fig_wrong_write_decomposition_column")
    build_transfer_fingerprints(tables["transfer"], args.output_dir / "fig_source_model_transfer_fingerprints_column")
    build_effect_sizes(tables["gains"], args.output_dir / "fig_decision_visibility_effect_sizes_column")


if __name__ == "__main__":
    main()
