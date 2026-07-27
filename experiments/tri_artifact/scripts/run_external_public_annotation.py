#!/usr/bin/env python3
"""Run the frozen SiliconFlow external-candidate annotation protocol."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = "https://api.siliconflow.cn/v1"
DEFAULT_MODELS = ["Qwen/Qwen3.5-122B-A10B", "Pro/zai-org/GLM-5.1"]
USER_PREFIX = "Annotate this frozen public-dataset candidate. Return JSON only.\n<CANDIDATE>\n"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_annotation(content: str) -> tuple[dict[str, Any] | None, str | None]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"json_parse_error: {exc}"
    if not isinstance(parsed, dict):
        return None, "schema_error: top-level output is not an object"
    required = {"candidate_id", "labels", "evidence", "primary_exclusion_reason", "notes"}
    if not required.issubset(parsed):
        return None, f"schema_error: missing {sorted(required - set(parsed))}"
    return parsed, None


def retryable_transport_failure(row: dict[str, Any]) -> bool:
    error = row.get("transport_or_response_error")
    return row.get("status") == "failed" and isinstance(error, str) and (
        "URLError:" in error
        or "HTTPError:" in error
        or "TimeoutError:" in error
        or "timed out" in error
    )


def call_chat(
    endpoint: str,
    api_key: str,
    model: str,
    system_prompt: str,
    candidate: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    user_content = USER_PREFIX + json.dumps(candidate, sort_keys=True, ensure_ascii=True)
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0,
        "max_tokens": 700,
        "enable_thinking": False,
    }
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def annotate_one(
    candidate: dict[str, Any],
    model: str,
    endpoint: str,
    api_key: str,
    system_prompt: str,
    candidate_inventory_sha256: str,
    system_prompt_sha256: str,
    timeout: int,
) -> dict[str, Any]:
    attempts = 0
    last_error: str | None = None
    response_payload: dict[str, Any] | None = None
    started = time.time()
    for attempt in range(2):
        attempts += 1
        try:
            response_payload = call_chat(
                endpoint, api_key, model, system_prompt, candidate, timeout
            )
            last_error = None
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt == 0:
                time.sleep(2)

    raw_content = ""
    usage: dict[str, Any] = {}
    response_id: str | None = None
    if response_payload is not None:
        response_id = response_payload.get("id")
        usage = response_payload.get("usage", {}) or {}
        try:
            raw_content = str(response_payload["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            last_error = f"response_schema_error: {exc}"

    annotation = None
    parse_error = None
    if raw_content:
        annotation, parse_error = parse_annotation(raw_content)
        if annotation is not None and annotation.get("candidate_id") != candidate["candidate_id"]:
            parse_error = "schema_error: candidate_id mismatch"
            annotation = None

    status = "ok" if last_error is None and parse_error is None and annotation is not None else "failed"
    return {
        "run_version": "TRI-external-public-annotation-v1",
        "candidate_id": candidate["candidate_id"],
        "dataset": candidate["dataset"],
        "source_unit_sha256": candidate["source_unit_sha256"],
        "candidate_inventory_sha256": candidate_inventory_sha256,
        "system_prompt_sha256": system_prompt_sha256,
        "user_prefix_sha256": sha256_bytes(USER_PREFIX.encode("utf-8")),
        "endpoint": endpoint,
        "model": model,
        "temperature": 0,
        "max_tokens": 700,
        "enable_thinking": False,
        "request_attempts": attempts,
        "status": status,
        "transport_or_response_error": last_error,
        "parse_error": parse_error,
        "annotation": annotation,
        "raw_content": raw_content,
        "raw_content_sha256": sha256_bytes(raw_content.encode("utf-8")),
        "response_id": response_id,
        "usage": usage,
        "latency_s": round(time.time() - started, 3),
    }


def parse_args() -> argparse.Namespace:
    artifact_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates",
        type=Path,
        default=artifact_root / "data" / "external_public_annotation_candidates_v1.jsonl",
    )
    parser.add_argument(
        "--system-prompt",
        type=Path,
        default=artifact_root / "reports" / "prompts" / "tri_external_public_annotator_v1.txt",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=artifact_root / "runs" / "external_public_annotation_siliconflow_v1.jsonl",
    )
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--endpoint", default=os.environ.get("LLM_BASE_URL", DEFAULT_ENDPOINT))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--retry-failed-transport",
        action="store_true",
        help="Append a repair attempt only for prior transport/HTTP/timeout failures.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_key = os.environ.get("SILICONFLOW_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        raise SystemExit("Set SILICONFLOW_API_KEY or LLM_API_KEY in the environment.")

    candidate_bytes = args.candidates.read_bytes()
    candidate_inventory_sha256 = sha256_bytes(candidate_bytes)
    candidates = load_jsonl(args.candidates)
    if args.smoke:
        selected: list[dict[str, Any]] = []
        for dataset in sorted({row["dataset"] for row in candidates}):
            selected.extend([row for row in candidates if row["dataset"] == dataset][:2])
        candidates = selected

    system_prompt_bytes = args.system_prompt.read_bytes()
    system_prompt = system_prompt_bytes.decode("utf-8")
    system_prompt_sha256 = sha256_bytes(system_prompt_bytes)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[tuple[str, str], dict[str, Any]] = {}
    if args.output.exists():
        for row in load_jsonl(args.output):
            existing[(row["model"], row["candidate_id"])] = row

    jobs = [
        (candidate, model)
        for candidate in candidates
        for model in args.models
        if (model, candidate["candidate_id"]) not in existing
        or (
            args.retry_failed_transport
            and retryable_transport_failure(existing[(model, candidate["candidate_id"])])
        )
    ]
    print(
        json.dumps(
            {
                "mode": "smoke" if args.smoke else "full",
                "candidate_inventory_sha256": candidate_inventory_sha256,
                "system_prompt_sha256": system_prompt_sha256,
                "jobs": len(jobs),
                "already_present": len(existing),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    if not jobs:
        return

    write_lock = threading.Lock()
    with args.output.open("a", encoding="utf-8") as stream:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [
                pool.submit(
                    annotate_one,
                    candidate,
                    model,
                    args.endpoint,
                    api_key,
                    system_prompt,
                    candidate_inventory_sha256,
                    system_prompt_sha256,
                    args.timeout,
                )
                for candidate, model in jobs
            ]
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                row = future.result()
                with write_lock:
                    stream.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")
                    stream.flush()
                completed += 1
                print(
                    json.dumps(
                        {
                            "completed": completed,
                            "total": len(jobs),
                            "candidate_id": row["candidate_id"],
                            "model": row["model"],
                            "status": row["status"],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )


if __name__ == "__main__":
    main()
