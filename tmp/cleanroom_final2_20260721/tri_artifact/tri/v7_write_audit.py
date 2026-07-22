from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .v2_model_report import short_model
from .v7_core_report import core_drift, core_opportunity, load


def load_replay(path: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            key = (str(row.get("model", "")), str(row.get("mode", "")), row["task_id"])
            rows[key] = row
    return rows


def build_report(run_paths: list[Path], replay_path: Path) -> dict[str, Any]:
    replay = load_replay(replay_path)
    groups: dict[tuple[str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    missing: list[tuple[str, str, str]] = []
    for path in run_paths:
        for row in load(path):
            key = (
                str(row.get("model", "")),
                str(row.get("result", {}).get("mode", "")),
                row["task"]["id"],
            )
            replay_row = replay.get(key)
            if replay_row is None:
                missing.append(key)
                continue
            groups[(key[0], key[1])].append((row, replay_row))

    summary = []
    for (model, controller), pairs in sorted(groups.items()):
        wrong = [pair for pair in pairs if pair[1]["action_status"] == "wrong_entity_write"]
        core_writes = [pair for pair in wrong if core_drift(pair[0])]
        dynamic_old = [
            pair
            for pair in wrong
            if pair[0]["task"]["binding"] == "dynamic"
            and pair[0]["task"]["pre_refresh_target"]
            != pair[0]["task"]["post_refresh_target"]
            and pair[0]["result"].get("predicted_target")
            == pair[0]["task"]["pre_refresh_target"]
        ]
        stable = [pair for pair in wrong if pair[0]["task"]["update"] == "stable"]
        core = [pair for pair in pairs if core_opportunity(pair[0])]
        summary.append({
            "model": short_model(model),
            "controller": controller,
            "n": len(pairs),
            "core_opportunities": len(core),
            "core_tri_writes": len(core_writes),
            "all_wrong_writes": len(wrong),
            "dynamic_old_target_writes": len(dynamic_old),
            "stable_wrong_writes": len(stable),
            "other_wrong_writes": len(wrong) - len(core_writes) - len(dynamic_old) - len(stable),
            "invalid_target_attempts": sum(
                replay_row["action_status"] == "invalid_target_attempt"
                for _, replay_row in pairs
            ),
            "unnecessary_rejections": sum(
                replay_row["action_status"] == "unnecessary_rejection"
                for _, replay_row in pairs
            ),
        })
    return {
        "replay_file": str(replay_path),
        "missing_replay_rows": [list(key) for key in missing],
        "summary": summary,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v7 Conditional SQLite Write Audit",
        "",
        "Core TRI writes require a correct initial binding, an anchored flip/name-collision,",
        "continued validity of the old entity, and an executed write to the refreshed winner.",
        "Dynamic-old writes are the opposite error: preserving the old target when reevaluation",
        "was authorized. Invalid attempts are blocked by action preconditions and are not writes.",
        "",
        "| Model | Controller | n | Core TRI writes | All wrong writes | Dynamic-old writes | Stable wrong writes | Other wrong writes | Invalid attempts | Unneeded rejects |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['n']} | "
            f"{row['core_tri_writes']}/{row['core_opportunities']} | "
            f"{row['all_wrong_writes']} | {row['dynamic_old_target_writes']} | "
            f"{row['stable_wrong_writes']} | {row['other_wrong_writes']} | "
            f"{row['invalid_target_attempts']} | {row['unnecessary_rejections']} |"
        )
    if report["missing_replay_rows"]:
        lines.extend(["", f"Missing replay rows: {len(report['missing_replay_rows'])}."])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("reports/v7_write_audit.json"))
    args = parser.parse_args()
    report = build_report(args.runs, args.replay)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
