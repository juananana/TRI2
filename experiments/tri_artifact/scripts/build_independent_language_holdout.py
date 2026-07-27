from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.independent_language_holdout import write_packet


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "data" / "temporal_referent_v7_core_replication.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "human_studies" / "independent_language_holdout_v1",
    )
    args = parser.parse_args()
    manifest = write_packet(args.source, args.output)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
