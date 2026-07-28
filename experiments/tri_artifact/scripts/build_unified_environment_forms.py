#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.unified_environment_holdout import ANNOTATORS, build_annotator_form, build_writer_forms, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Build redacted unified holdout writer or annotator forms.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--annotator", choices=ANNOTATORS)
    args = parser.parse_args()
    rows = read_jsonl(args.input)
    if args.annotator:
        print(json.dumps(build_annotator_form(rows, args.annotator, args.output), indent=2))
    else:
        print(json.dumps(build_writer_forms(rows, args.output), indent=2))


if __name__ == "__main__":
    main()
