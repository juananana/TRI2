#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
from uuid import uuid4

from scripts.run_end_to_end_decision_decomposition import (
    RecordingChatClient,
    append_row_crash_safe,
    load_and_repair_resume_file,
    run_component,
    utc_now,
)
from tri.end_to_end_decision_decomposition import canonical_json, sha256_path, sha256_text
from tri.public_recall_model_prelabels import (
    ENDPOINT,
    EVIDENCE_STATUS,
    MODEL_IDS,
    RUN_SETTINGS,
    RUN_VERSION,
    SYSTEM_PROMPT,
    actor_payload,
    load_packet,
    parse_model_prelabel,
    prompt_hash,
    settings_hash,
    validate_run_inventory,
    validate_run_row,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / "data" / "public_recall_model_prelabel_packets_v4"
PROTOCOL = ROOT / "reports" / "TRI_public_recall_model_prelabels_protocol.md"
SMOKE_ROWS = 8


def run_task(
    client: RecordingChatClient,
    task: dict,
    index: int,
    stage: str,
    packet_sha256: str,
    protocol_sha256: str,
    health_smoke_sha256: str | None,
    session_id: str,
) -> dict:
    component = run_component(
        client,
        "public_recall_model_prelabel",
        SYSTEM_PROMPT,
        actor_payload(task),
        lambda text: parse_model_prelabel(text, task),
    )
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": stage,
        "timestamp_utc": utc_now(),
        "recording_session_id": session_id,
        "labeler_id": task["labeler_id"],
        "model": client.model,
        "task_index": index,
        "task": task,
        "task_sha256": sha256_text(canonical_json(task)),
        "packet_sha256": packet_sha256,
        "protocol_sha256": protocol_sha256,
        "health_smoke_sha256": health_smoke_sha256,
        "prompt_sha256": prompt_hash(),
        "settings_sha256": settings_hash(),
        "component": component,
        "complete": component.get("parsed") is not None,
    }
    validate_run_row(
        row,
        task,
        index,
        stage,
        packet_sha256,
        protocol_sha256,
        health_smoke_sha256,
    )
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Run frozen public-recall model prelabels.")
    parser.add_argument("--labeler", choices=tuple(MODEL_IDS), required=True)
    parser.add_argument("--stage", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--health-smoke", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    packet = PACKET_ROOT / "model_prelabels" / f"model_prelabel_{args.labeler}.jsonl"
    manifest = PACKET_ROOT / "manifest.json"
    tasks = load_packet(packet, manifest, args.labeler)
    selected = tasks[:SMOKE_ROWS] if args.stage == "smoke" else tasks
    packet_sha256 = sha256_path(packet)
    protocol_sha256 = sha256_path(PROTOCOL)
    output = args.output or ROOT / "runs" / (
        f"public_recall_model_prelabel_{args.labeler}_{args.stage}_v1.jsonl"
    )
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "network_calls": 0,
            "labeler": args.labeler,
            "model": MODEL_IDS[args.labeler],
            "stage": args.stage,
            "rows": len(selected),
            "packet_sha256": packet_sha256,
            "protocol_sha256": protocol_sha256,
            "prompt_sha256": prompt_hash(),
            "settings_sha256": settings_hash(),
            "output": str(output),
        }, indent=2))
        return

    health_smoke_sha256 = None
    if args.stage == "full":
        if args.health_smoke is None:
            raise SystemExit("full prelabel run requires --health-smoke")
        smoke_rows = [
            json.loads(line)
            for line in args.health_smoke.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        health_smoke_sha256 = sha256_path(args.health_smoke)
        validate_run_inventory(
            smoke_rows,
            tasks[:SMOKE_ROWS],
            args.labeler,
            "smoke",
            packet_sha256,
            protocol_sha256,
        )
        if any(not row["complete"] for row in smoke_rows):
            raise SystemExit("model-prelabel health smoke contains incomplete rows")

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not output.exists() and not api_key:
        raise SystemExit("Set LLM_API_KEY at runtime; credentials are never read from files.")
    output.parent.mkdir(parents=True, exist_ok=True)
    session_id = str(uuid4())
    with output.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        rows, recovery = load_and_repair_resume_file(handle)
        if len(rows) > len(selected):
            raise ValueError("model-prelabel resume file exceeds frozen scope")
        for index, row in enumerate(rows):
            validate_run_row(
                row,
                selected[index],
                index,
                args.stage,
                packet_sha256,
                protocol_sha256,
                health_smoke_sha256,
            )
        client = None
        if len(rows) < len(selected):
            if not api_key:
                raise SystemExit("Set LLM_API_KEY to resume the incomplete prelabel run.")
            client = RecordingChatClient(
                model=MODEL_IDS[args.labeler],
                base_url=ENDPOINT,
                api_key=api_key,
                timeout=RUN_SETTINGS["timeout_seconds"],
                max_retries=RUN_SETTINGS["max_retries"],
                retry_backoff=RUN_SETTINGS["retry_backoff_seconds"],
                max_tokens=RUN_SETTINGS["max_tokens"],
                enable_thinking=False,
            )
        for index in range(len(rows), len(selected)):
            assert client is not None
            row = run_task(
                client,
                selected[index],
                index,
                args.stage,
                packet_sha256,
                protocol_sha256,
                health_smoke_sha256,
                session_id,
            )
            append_row_crash_safe(handle, row)
            rows.append(row)
        validate_run_inventory(
            rows,
            selected,
            args.labeler,
            args.stage,
            packet_sha256,
            protocol_sha256,
            health_smoke_sha256,
        )
    print(json.dumps({
        "output": str(output),
        "rows": len(rows),
        "complete_rows": sum(row["complete"] for row in rows),
        "tail_recovery": recovery,
        "sha256": sha256_path(output),
    }, indent=2))


if __name__ == "__main__":
    main()
