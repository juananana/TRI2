from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.wjx_human_audit import (
    analyze,
    dump_report,
    load_allocation,
    load_key,
    normalize_export_row,
    read_csv,
    select_frozen_sample,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze the frozen six-form WJX construct audit.")
    parser.add_argument("--answer-key", type=Path, required=True)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--responses", type=Path, nargs="+", required=True)
    parser.add_argument("--participant-map", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    key_rows = load_key(args.answer_key)
    allocation = load_allocation(args.allocation)
    participant_map = (
        json.loads(args.participant_map.read_text(encoding="utf-8"))
        if args.participant_map
        else {}
    )
    normalized = [
        normalize_export_row(
            row,
            key_rows=key_rows,
            allocation=allocation,
            participant_map=participant_map,
        )
        for path in args.responses
        for row in read_csv(path)
    ]
    selected, ledger = select_frozen_sample(normalized)
    report = analyze(selected, key_rows)
    report["selection_ledger"] = ledger
    dump_report(report, args.output)
    print(json.dumps({key: report[key] for key in ("evidence_status", "participants", "items", "complete_changed_pairs")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
