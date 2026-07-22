#!/usr/bin/env python3
"""Small, credential-safe benchmark for API relays configured in CC Switch."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


DB_PATH = Path.home() / ".cc-switch" / "cc-switch.db"

TASKS = [
    {
        "id": "code_trace",
        "prompt": (
            "Act as a coding assistant. Without running code, evaluate this Python program:\n"
            "def f(x, a=[]):\n    a.append(x)\n    return len(a)\n"
            "print(f(1), f(2), f(3, []), f(4))\n"
            "Return exactly one compact JSON object with keys output and reason. "
            "output must be the four printed integers as a space-separated string."
        ),
        "score": lambda s: int(bool(re.search(r'\"output\"\s*:\s*\"1 2 1 3\"', s))),
    },
    {
        "id": "debugging",
        "prompt": (
            "A binary search over ascending integers uses: while lo < hi; mid=(lo+hi)//2; "
            "if a[mid] < target: lo=mid; else: hi=mid. It can loop forever. "
            "Return exactly one compact JSON object with keys bug and corrected_update. "
            "corrected_update must contain only the corrected assignment for the faulty branch."
        ),
        "score": lambda s: int(bool(re.search(r'lo\s*=\s*mid\s*\+\s*1', s))),
    },
    {
        "id": "constraint_reasoning",
        "prompt": (
            "Five jobs A-E must be ordered once each. Constraints: B before A; D immediately "
            "after B; A before C; E after C. Return exactly the lexicographically smallest valid "
            "order as a compact JSON object {\"order\":[...]}; no markdown or extra keys."
        ),
        "score": lambda s: int(bool(re.fullmatch(
            r'\s*\{\s*\"order\"\s*:\s*\[\s*\"B\"\s*,\s*\"D\"\s*,\s*\"A\"\s*,\s*\"C\"\s*,\s*\"E\"\s*\]\s*\}\s*', s
        ))),
    },
]


def parse_codex_config(config: str) -> tuple[str, str]:
    model_match = re.search(r'^model\s*=\s*"([^"]+)"', config, re.MULTILINE)
    base_match = re.search(r'^base_url\s*=\s*"([^"]+)"', config, re.MULTILINE)
    if not model_match or not base_match:
        raise ValueError("missing model or base_url")
    return model_match.group(1), base_match.group(1).rstrip("/")


def load_providers(only_names: Optional[list[str]] = None) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    sql = (
        "SELECT id, app_type, name, settings_config FROM providers "
        "WHERE app_type IN ('codex', 'claude-desktop')"
    )
    params: list[str] = []
    if only_names:
        sql += " AND name IN ({})".format(",".join("?" for _ in only_names))
        params.extend(only_names)
    rows = conn.execute(sql, params).fetchall()
    providers = []
    for row in rows:
        settings = json.loads(row["settings_config"])
        if row["app_type"] == "codex" and settings.get("auth", {}).get("OPENAI_API_KEY"):
            try:
                model, base_url = parse_codex_config(settings.get("config", ""))
            except ValueError:
                continue
            providers.append({
                "id": row["id"], "kind": "codex", "name": row["name"],
                "base_url": base_url, "model": model,
                "key": settings["auth"]["OPENAI_API_KEY"],
            })
        elif row["app_type"] == "claude-desktop":
            env = settings.get("env", {})
            if env.get("ANTHROPIC_AUTH_TOKEN") and env.get("ANTHROPIC_BASE_URL"):
                providers.append({
                    "id": row["id"], "kind": "claude", "name": row["name"],
                    "base_url": env["ANTHROPIC_BASE_URL"].rstrip("/"),
                    "model": "claude-opus-4-7", "key": env["ANTHROPIC_AUTH_TOKEN"],
                })
    conn.close()
    return providers


def endpoint(base_url: str, suffix: str) -> str:
    if base_url.endswith("/v1"):
        return base_url + suffix.removeprefix("/v1")
    return base_url + suffix


def stream_request(provider: dict, prompt: str, timeout: int) -> dict:
    if provider["kind"] == "codex":
        url = endpoint(provider["base_url"], "/v1/responses")
        body = {"model": provider["model"], "input": prompt, "stream": True,
                "max_output_tokens": 220}
        headers = {"Authorization": f"Bearer {provider['key']}",
                   "Content-Type": "application/json", "Accept": "text/event-stream"}
    else:
        url = endpoint(provider["base_url"], "/v1/messages")
        body = {"model": provider["model"], "messages": [{"role": "user", "content": prompt}],
                "stream": True, "max_tokens": 220, "temperature": 0}
        headers = {"x-api-key": provider["key"], "anthropic-version": "2023-06-01",
                   "Content-Type": "application/json", "Accept": "text/event-stream"}

    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    started = time.perf_counter()
    first_token_ms = None
    chunks: list[str] = []
    usage: dict = {}
    response_model = None
    status = None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            for raw_line in response:
                line = raw_line.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data_text = line[5:].strip()
                if data_text == "[DONE]":
                    continue
                try:
                    event = json.loads(data_text)
                except json.JSONDecodeError:
                    continue
                event_type = event.get("type", "")
                delta = ""
                if event_type == "response.output_text.delta":
                    delta = event.get("delta", "")
                elif event_type == "content_block_delta":
                    delta = event.get("delta", {}).get("text", "")
                if delta:
                    if first_token_ms is None:
                        first_token_ms = round((time.perf_counter() - started) * 1000)
                    chunks.append(delta)
                response_model = event.get("response", {}).get("model", response_model)
                response_model = event.get("message", {}).get("model", response_model)
                candidate_usage = event.get("response", {}).get("usage") or event.get("usage")
                if candidate_usage:
                    usage.update(candidate_usage)
    except urllib.error.HTTPError as exc:
        error_body = exc.read(1200).decode("utf-8", "replace")
        return {"ok": False, "status": exc.code, "error": error_body[:500],
                "duration_ms": round((time.perf_counter() - started) * 1000)}
    except Exception as exc:
        return {"ok": False, "status": status, "error": f"{type(exc).__name__}: {exc}",
                "duration_ms": round((time.perf_counter() - started) * 1000)}
    return {"ok": True, "status": status, "first_token_ms": first_token_ms,
            "duration_ms": round((time.perf_counter() - started) * 1000),
            "text": "".join(chunks).strip(), "usage": usage, "response_model": response_model}


def query_balance(provider: dict, timeout: int) -> Optional[dict]:
    url = endpoint(provider["base_url"], "/v1/usage")
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {provider['key']}"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
        allowed = ("remaining", "balance", "unit", "is_active", "isValid")
        result = {key: data[key] for key in allowed if key in data}
        quota = data.get("quota")
        if isinstance(quota, dict):
            result["quota"] = {key: quota[key] for key in ("remaining", "unit") if key in quota}
        return result or None
    except Exception:
        return None


def summarize(
    provider: dict,
    results: list[dict],
    before: Optional[dict],
    after: Optional[dict],
) -> dict:
    successful = [item for item in results if item["result"].get("ok")]
    scores = [item["score"] for item in successful]
    first_tokens = [item["result"]["first_token_ms"] for item in successful
                    if item["result"].get("first_token_ms") is not None]
    durations = [item["result"]["duration_ms"] for item in successful]
    return {
        "id": provider["id"], "kind": provider["kind"], "name": provider["name"],
        "base_url": provider["base_url"], "configured_model": provider["model"],
        "success_rate": len(successful) / len(results),
        "quality_score": sum(scores) / len(TASKS),
        "median_first_token_ms": round(statistics.median(first_tokens)) if first_tokens else None,
        "median_duration_ms": round(statistics.median(durations)) if durations else None,
        "balance_before": before, "balance_after": after, "tasks": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("codex", "claude", "all"), default="all")
    parser.add_argument("--exclude-host", action="append", default=[])
    parser.add_argument("--only-name", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--output", type=Path, default=Path("relay_benchmark_results.json"))
    args = parser.parse_args()

    providers = load_providers(args.only_name)
    if args.kind != "all":
        providers = [provider for provider in providers if provider["kind"] == args.kind]
    providers = [
        provider for provider in providers
        if not any(host in provider["base_url"] for host in args.exclude_host)
    ]
    if args.only_name:
        providers = [provider for provider in providers if provider["name"] in args.only_name]

    report = {"started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "providers": []}
    for provider in providers:
        print(f"Testing {provider['kind']} / {provider['name']} / {provider['base_url']}", flush=True)
        before = query_balance(provider, min(args.timeout, 15)) if provider["kind"] == "codex" else None
        task_results = []
        for task in TASKS:
            result = stream_request(provider, task["prompt"], args.timeout)
            score = task["score"](result.get("text", "")) if result.get("ok") else 0
            task_results.append({"task": task["id"], "score": score, "result": result})
            print(f"  {task['id']}: status={result.get('status')} score={score} "
                  f"ttft={result.get('first_token_ms')}ms total={result.get('duration_ms')}ms", flush=True)
        after = query_balance(provider, min(args.timeout, 15)) if provider["kind"] == "codex" else None
        report["providers"].append(summarize(provider, task_results, before, after))
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote sanitized results to {args.output}")


if __name__ == "__main__":
    main()
