#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import os
import subprocess
import sys
from pathlib import Path

from tri.toolsandbox_health_gate import evaluate


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
PYTHON = PROJECT / ".venv-toolsandbox" / "bin" / "python"
DATA = ROOT / "data" / "toolsandbox_tri_single_turn_2x2_v1.jsonl"
ADDENDUM = ROOT / "reports" / "TRI_submission_critical_replication_addendum_20260728.md"
MODELS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
}
CONDITIONS = ("full_history", "matched_generic_state_observed")


def _safe(model: str) -> str:
    return model.replace("/", "_").replace(":", "_")


def _paths(alias: str, model: str, condition: str) -> tuple[Path, Path, Path, Path]:
    safe = _safe(model)
    stem = f"toolsandbox_tri_single_turn_{safe}_{condition}"
    health = ROOT / "runs" / f"{stem}_health_v2.jsonl"
    full = ROOT / "runs" / f"{stem}_full_v2.jsonl"
    report_stem = f"toolsandbox_single_turn_{alias}_{condition}_repeat_v2"
    return (
        health,
        full,
        ROOT / "reports" / f"{report_stem}.json",
        ROOT / "reports" / f"{report_stem}.md",
    )


def _run(command: list[str]) -> None:
    subprocess.run(
        command,
        cwd=PROJECT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"},
        check=True,
    )


def _runner_command(model: str, condition: str, output: Path, limit: int) -> list[str]:
    if condition == "full_history":
        module = "external_pilots.toolsandbox_tri.agent_runner"
        controller = "full_history"
    else:
        module = "external_pilots.toolsandbox_tri.matched_runner"
        controller = "generic"
    command = [
        str(PYTHON),
        "-m",
        module,
        "--model",
        model,
        "--controllers",
        controller,
        "--data",
        str(DATA),
        "--output",
        str(output),
        "--temperature",
        "0",
        "--timeout",
        "180",
        "--max-api-retries",
        "1",
        "--retry-backoff",
        "5",
        "--max-tokens",
        "700",
        "--limit",
        str(limit),
        "--protocol-addendum",
        str(ADDENDUM),
    ]
    if output.exists():
        command.append("--resume")
    return command


def run_cell(alias: str, model: str, condition: str) -> Path:
    health, full, json_report, md_report = _paths(alias, model, condition)
    if not health.exists() or not evaluate(health, 8)["passed"]:
        _run(_runner_command(model, condition, health, 8))
    gate = evaluate(health, 8)
    if not gate["passed"]:
        raise RuntimeError(f"health gate failed for {alias}/{condition}: {gate}")
    if not full.exists() or len(full.read_text(encoding="utf-8").splitlines()) < 96:
        _run(_runner_command(model, condition, full, 96))
    _run(
        [
            str(PYTHON),
            "-m",
            "tri.toolsandbox_single_turn_report",
            str(full),
            "--json",
            str(json_report),
            "--markdown",
            str(md_report),
        ]
    )
    return full


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the frozen four-cell ToolSandbox null repeat.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    jobs = [(alias, model, condition) for alias, model in MODELS.items() for condition in CONDITIONS]
    if args.dry_run:
        for alias, model, condition in jobs:
            health, full, _, _ = _paths(alias, model, condition)
            print(f"{alias}\t{condition}\thealth={health.name}\tfull={full.name}\trows=8+96")
        return
    if not (os.environ.get("LLM_API_KEY") or os.environ.get("SILICONFLOW_API_KEY")):
        raise SystemExit("Set LLM_API_KEY or SILICONFLOW_API_KEY before starting the repeat.")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_cell, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            print(future.result(), flush=True)


if __name__ == "__main__":
    main()

