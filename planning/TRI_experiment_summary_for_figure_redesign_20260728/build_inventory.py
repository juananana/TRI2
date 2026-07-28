from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sources" / "current_experiment_registry.md"
OUTPUT = ROOT / "data" / "experiment_registry.csv"


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip().replace("`", "") for cell in line.strip().strip("|").split("|")]


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    table_rows: list[list[str]] = []
    in_registry = False
    for line in lines:
        if line == "## Registry":
            in_registry = True
            continue
        if in_registry and line.startswith("## "):
            break
        if not in_registry or not line.startswith("|"):
            continue
        cells = split_markdown_row(line)
        if not cells or cells[0] == "Experiment" or set(cells[0]) <= {"-", ":"}:
            continue
        if len(cells) != 6:
            raise ValueError(f"Unexpected registry row with {len(cells)} cells: {line}")
        table_rows.append(cells)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "experiment",
                "research_question_and_contrast",
                "inventory_and_estimand",
                "inclusion_failure_rule",
                "evidence_status",
                "supported_claim_and_boundary",
            ]
        )
        writer.writerows(table_rows)
    print(f"wrote {len(table_rows)} experiment families to {OUTPUT}")


if __name__ == "__main__":
    main()
