from __future__ import annotations

import argparse
from pathlib import Path

from tri_figures.data import load_tables
from tri_figures.distinctive import build_all_distinctive


def main() -> None:
    root = Path(__file__).parent
    parser = argparse.ArgumentParser(description="Generate distinctive TRI figure candidates.")
    parser.add_argument("--data-dir", type=Path, default=root / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=root / "outputs" / "distinctive")
    args = parser.parse_args()
    build_all_distinctive(load_tables(args.data_dir), args.output_dir)


if __name__ == "__main__":
    main()
