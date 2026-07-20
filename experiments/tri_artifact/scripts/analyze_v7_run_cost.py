from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def summarize(path: Path) -> dict[str, Any]:
    rows = load(path)
    first = rows[0]
    usage = [record for row in rows for record in row.get("api_usage", [])]
    return {
        "file": str(path),
        "model": first.get("model"),
        "controller": first.get("result", {}).get("mode"),
        "tasks": len(rows),
        "successful_tasks": sum(bool(row.get("result", {}).get("success")) for row in rows),
        "api_errors": sum(row.get("status") != "ok" for row in rows),
        "api_request_attempts": sum(int(row.get("api_request_attempts", 0)) for row in rows),
        "api_retries": sum(int(row.get("api_retries", 0)) for row in rows),
        "latency_s": sum(float(row.get("latency_s", 0.0)) for row in rows),
        "usage_records": len(usage),
        "prompt_tokens": sum(int(record.get("prompt_tokens", 0)) for record in usage),
        "completion_tokens": sum(int(record.get("completion_tokens", 0)) for record in usage),
        "total_tokens": sum(int(record.get("total_tokens", 0)) for record in usage),
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# V7 Run Cost Audit",
        "",
        "| Model | Controller | Tasks | Correct | Requests | Retries | Latency s | Prompt tokens | Completion tokens | Total tokens |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["runs"]:
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['tasks']} | "
            f"{row['successful_tasks']} | {row['api_request_attempts']} | "
            f"{row['api_retries']} | {row['latency_s']:.1f} | {row['prompt_tokens']} | "
            f"{row['completion_tokens']} | {row['total_tokens']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {"runs": [summarize(path) for path in args.input]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
