#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import os
import subprocess
from pathlib import Path

from scripts.run_convention_told_control import MODEL_IDS as CONVENTION_MODELS
from scripts.run_revision_matrix import validate_existing as validate_revision_existing


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
PYTHON = PROJECT / ".venv-toolsandbox" / "bin" / "python"
ALL_ALIASES = ("qwen", "glm", "deepseek", "minimax")
EXTENSION_ALIASES = ("deepseek", "minimax")


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def _run(command: list[str]) -> None:
    subprocess.run(
        command,
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": ".", "PYTHONDONTWRITEBYTECODE": "1"},
        check=True,
    )


def _convention_paths(alias: str) -> tuple[Path, Path]:
    return (
        ROOT / "runs" / f"convention_told_{alias}_smoke_v1.jsonl",
        ROOT / "runs" / f"convention_told_{alias}_full_v1.jsonl",
    )


def run_convention(alias: str) -> Path:
    smoke, full = _convention_paths(alias)
    smoke_rows = _line_count(smoke) if smoke.exists() else 0
    if smoke_rows > 16:
        raise ValueError(f"Convention smoke output exceeds frozen scope: {smoke}")
    if smoke_rows < 16:
        command = [
            str(PYTHON),
            "scripts/run_convention_told_control.py",
            "--model",
            alias,
            "--stage",
            "smoke",
            "--output",
            str(smoke),
        ]
        if smoke.exists():
            command.append("--resume")
        _run(command)

    full_rows = _line_count(full) if full.exists() else 0
    if full_rows > 80:
        raise ValueError(f"Convention full output exceeds frozen scope: {full}")
    if full_rows < 80:
        command = [
            str(PYTHON),
            "scripts/run_convention_told_control.py",
            "--model",
            alias,
            "--stage",
            "full",
            "--smoke-file",
            str(smoke),
            "--output",
            str(full),
        ]
        if full.exists():
            command.append("--resume")
        _run(command)
    return full


def _revision_paths(audit: str, alias: str) -> tuple[Path, Path]:
    return (
        ROOT / "runs" / f"revision_{audit}_{alias}_health_smoke_v2.jsonl",
        ROOT / "runs" / f"revision_{audit}_{alias}_full_v2.jsonl",
    )


def run_revision(audit: str, alias: str) -> Path:
    smoke, full = _revision_paths(audit, alias)
    if not smoke.exists() or not validate_revision_existing(
        smoke, audit, alias, "health-smoke"
    ):
        command = [
            str(PYTHON),
            "scripts/run_revision_matched_audit.py",
            "--audit",
            audit,
            "--model",
            alias,
            "--stage",
            "health-smoke",
            "--output",
            str(smoke),
        ]
        if smoke.exists():
            command.append("--resume")
        _run(command)
    if not full.exists() or not validate_revision_existing(full, audit, alias, "full"):
        command = [
            str(PYTHON),
            "scripts/run_revision_matched_audit.py",
            "--audit",
            audit,
            "--model",
            alias,
            "--stage",
            "full",
            "--health-smoke",
            str(smoke),
            "--output",
            str(full),
        ]
        if full.exists():
            command.append("--resume")
        _run(command)
    return full


def _parallel(function, jobs: list[tuple], workers: int) -> list[Path]:
    outputs: list[Path] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(function, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            output = future.result()
            outputs.append(output)
            print(output, flush=True)
    return outputs


def report_convention() -> None:
    inputs = [str(_convention_paths(alias)[1]) for alias in ALL_ALIASES]
    _run(
        [
            str(PYTHON),
            "scripts/report_convention_told_control.py",
            "--input",
            *inputs,
            "--output",
            str(ROOT / "reports" / "convention_told_natural_history_v1.json"),
        ]
    )


def report_full_diagnostic() -> None:
    inputs = [
        ROOT / "runs" / "revision_full_diagnostic_qwen_full_v1.jsonl",
        ROOT / "runs" / "revision_full_diagnostic_glm_full_v1.jsonl",
        *[_revision_paths("full_diagnostic", alias)[1] for alias in EXTENSION_ALIASES],
    ]
    _run(
        [
            str(PYTHON),
            "scripts/report_revision_matched_audit_v3.py",
            "--audit",
            "full_diagnostic",
            *[str(path) for path in inputs],
            "--json-output",
            str(ROOT / "reports" / "revision_full_diagnostic_four_model_v2.json"),
            "--md-output",
            str(ROOT / "reports" / "revision_full_diagnostic_four_model_v2.md"),
        ]
    )


def report_source_repeat() -> None:
    historical = [
        f"historical={ROOT / 'runs' / f'revision_source_grounded_{alias}_full_v1.jsonl'}"
        for alias in ("qwen", "glm", "deepseek")
    ]
    new = [
        f"{'repeat2' if alias != 'minimax' else 'first-pass'}={_revision_paths('source_grounded', alias)[1]}"
        for alias in ALL_ALIASES
    ]
    _run(
        [
            str(PYTHON),
            "scripts/report_revision_repeat_stability.py",
            "--historical",
            *historical,
            "--new",
            *new,
            "--output",
            str(ROOT / "reports" / "revision_source_grounded_repeat_v1.json"),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the submission-critical remote-API matrix.")
    parser.add_argument("--phase", choices=("all", "convention", "extension", "source-repeat"), default="all")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    phases = (
        ("convention", ALL_ALIASES),
        ("extension", EXTENSION_ALIASES),
        ("source-repeat", ALL_ALIASES),
    )
    selected = phases if args.phase == "all" else [item for item in phases if item[0] == args.phase]
    if args.dry_run:
        for phase, aliases in selected:
            for alias in aliases:
                model = CONVENTION_MODELS[alias]
                rows = 80 if phase == "convention" else (160 if phase == "extension" else 60)
                calls = 2 * rows if phase == "convention" else 3 * rows
                print(f"{phase}\t{alias}\t{model}\trows={rows}\tfull_calls={calls}")
        return
    if not (os.environ.get("LLM_API_KEY") or os.environ.get("SILICONFLOW_API_KEY")):
        raise SystemExit("Set LLM_API_KEY or SILICONFLOW_API_KEY before starting the matrix.")
    for phase, aliases in selected:
        if phase == "convention":
            _parallel(run_convention, [(alias,) for alias in aliases], args.workers)
            report_convention()
        elif phase == "extension":
            _parallel(
                run_revision,
                [("full_diagnostic", alias) for alias in aliases],
                min(args.workers, len(aliases)),
            )
            report_full_diagnostic()
        else:
            _parallel(
                run_revision,
                [("source_grounded", alias) for alias in aliases],
                args.workers,
            )
            report_source_repeat()


if __name__ == "__main__":
    main()
