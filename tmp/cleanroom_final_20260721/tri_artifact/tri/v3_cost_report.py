from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from .v2_model_report import is_api_failure, short_model


def load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result = row.get("result", {})
        key = (
            short_model(str(row.get("model", "unknown"))),
            str(result.get("mode", "unknown")),
            str(row.get("task", {}).get("binding", "unknown")),
        )
        groups[key].append(row)

    output = []
    for (model, mode, binding), group in sorted(groups.items()):
        latencies = [float(row.get("latency_s", 0.0)) for row in group]
        attempts = [int(row.get("api_request_attempts", 0)) for row in group]
        retries = [int(row.get("api_retries", 0)) for row in group]
        output.append({
            "model": model,
            "mode": mode,
            "binding": binding,
            "n": len(group),
            "mean_api_requests": sum(attempts) / len(group),
            "total_api_requests": sum(attempts),
            "mean_latency_s": sum(latencies) / len(group),
            "median_latency_s": median(latencies),
            "total_latency_s": sum(latencies),
            "api_retries": sum(retries),
            "api_errors": sum(is_api_failure(row) for row in group),
        })
    return {"groups": output}


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v3 Logged Inference Cost",
        "",
        "Latency is client-observed wall time. API request counts include retries; token usage "
        "is unavailable in the frozen runner and is therefore not estimated.",
        "",
        "| Model | Controller | Binding | n | Requests/task | Total requests | Mean latency (s) | Median latency (s) | Retries | API err. |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["groups"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['binding']} | {row['n']} | "
            f"{row['mean_api_requests']:.2f} | {row['total_api_requests']} | "
            f"{row['mean_latency_s']:.2f} | {row['median_latency_s']:.2f} | "
            f"{row['api_retries']} | {row['api_errors']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", default="reports/v3_cost_report.json")
    args = ap.parse_args()
    report = summarize(load_rows([Path(path) for path in args.input]))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
