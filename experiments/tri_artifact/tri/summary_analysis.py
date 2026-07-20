from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_rows(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    if row.get("status") == "ok" and row.get("result", {}).get("mode") == "lossy_summary_controller":
                        rows.append(row)
    return rows


def memory_text(row: dict) -> str:
    raw = row.get("result", {}).get("raw_outputs", [])
    return raw[1].strip().replace("\n", " ") if len(raw) > 1 and isinstance(raw[1], str) else ""


def has_temporal_anchor(text: str) -> bool:
    lowered = text.lower()
    markers = ["original", "initial", "before", "pre-refresh", "previous", "remember"]
    return any(marker in lowered for marker in markers)


def has_entity_id(text: str, task: dict) -> bool:
    ids = [item["id"] for item in task["initial_state"]] + [item["id"] for item in task["refreshed_state"]]
    return any(entity_id in text for entity_id in ids)


def markdown(rows: list[dict]) -> str:
    lines = [
        "# Lossy Summary Controller Case Study",
        "",
        "The bounded memory module was instructed to summarize the controller transcript in at most 18 words without entity IDs, exact names, or exact numeric values. These summaries are model-generated controller state, not hand-edited benchmark inputs.",
        "",
        "## Aggregate",
        "",
        "| Binding | Update | n | Accuracy | Drift | Temporal Anchor in Summary | Entity ID in Summary |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        task = row["task"]
        groups.setdefault((task["binding"], task["update"]), []).append(row)
    for (binding, update), group in sorted(groups.items()):
        n = len(group)
        correct = sum(bool(row["result"].get("success")) for row in group)
        drift = sum(bool(row["result"].get("drift_to_new_leader")) for row in group)
        temporal = sum(has_temporal_anchor(memory_text(row)) for row in group)
        ids = sum(has_entity_id(memory_text(row), row["task"]) for row in group)
        lines.append(
            f"| {binding} | {update} | {n} | {100 * correct / n:.1f} | "
            f"{100 * drift / n:.1f} | {100 * temporal / n:.1f} | {100 * ids / n:.1f} |"
        )
    lines.extend([
        "",
        "## Representative Anchored-Flip Summaries",
        "",
        "| Task | Summary | Predicted | Correct | Outcome |",
        "|---|---|---|---|---|",
    ])
    anchored = [row for row in rows if row["task"]["binding"] == "anchored" and row["task"]["update"] == "flip"]
    examples = anchored[:5] + [row for row in anchored if row["result"].get("success")][:2]
    seen = set()
    for row in examples:
        task = row["task"]
        if task["id"] in seen:
            continue
        seen.add(task["id"])
        result = row["result"]
        outcome = "correct" if result.get("success") else ("drift" if result.get("drift_to_new_leader") else "invalid/other")
        summary = memory_text(row).replace("|", "\\|")
        lines.append(
            f"| {task['id']} | {summary} | {result.get('predicted_target')} | "
            f"{task['correct_target']} | {outcome} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    rows = load_rows([Path(p) for p in args.input])
    Path(args.output).write_text(markdown(rows), encoding="utf-8")
    print(markdown(rows))


if __name__ == "__main__":
    main()
