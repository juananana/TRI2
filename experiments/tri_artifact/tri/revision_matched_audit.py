from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable


RUN_VERSION = "TRI-revision-matched-audit-v1"
EVIDENCE_STATUS = "post-primary; protocol frozen before own calls"
BOOTSTRAP_SEED = 20260726
BOOTSTRAP_SAMPLES = 10_000
AUDITS = ("full_diagnostic", "human_rewrite", "source_grounded")
CONDITIONS = ("history_only", "decision_visible", "decision_enforced")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return ("\n".join(canonical_json(row) for row in rows) + "\n").encode("utf-8")


def exact_target(value: object) -> str | None:
    if value is None:
        return None
    target = str(value).strip()
    if target.lower() in {
        "invalid",
        "invalid_bound_entity",
        "unavailable",
        "missing",
        "reject",
    }:
        return "INVALID_BOUND_ENTITY"
    return target or None


def _pair_key(task_id: str) -> str:
    key = re.sub(r"-(explicit|implicit)_(anchor|dynamic)-", r"-\1_MODE-", task_id)
    if key == task_id:
        key = re.sub(r"__(preserve|reevaluate)__", "__MODE__", task_id)
    return key


def _record_id(record: dict[str, Any]) -> str:
    for key in ("id", "entity_id", "reminder_id"):
        if record.get(key) is not None:
            return str(record[key])
    raise ValueError("state record has no stable ID")


def _normal_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for source in records:
        row = dict(source)
        row["id"] = _record_id(row)
        normalized.append(row)
    return normalized


def _normal_task(
    *,
    audit_id: str,
    task_id: str,
    source: str,
    pair_id: str,
    mode: str,
    instruction: str,
    initial_state: list[dict[str, Any]],
    refreshed_state: list[dict[str, Any]],
    selector: str,
    action: str,
    action_schema: dict[str, Any],
    pre_target: str,
    post_target: str,
    correct_target: str,
    update: str,
    actionable: bool,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    initial = _normal_records(initial_state)
    refreshed = _normal_records(refreshed_state)
    return {
        "id": task_id,
        "audit_id": audit_id,
        "source": source,
        "pair_id": pair_id,
        "state_cluster_id": pair_id,
        "reference_mode_gold": mode,
        "instruction": instruction,
        "s0_summary": {"source": source, "records": initial},
        "initial_selected_id": pre_target,
        "initial_state": initial,
        "refreshed_state": refreshed,
        "selector": selector,
        "action": action,
        "action_schema": action_schema,
        "pre_refresh_target": pre_target,
        "post_refresh_target": post_target,
        "correct_target": correct_target,
        "update": update,
        "actionable_core": actionable,
        "metadata": metadata or {},
    }


def build_full_diagnostic(source: Path) -> list[dict[str, Any]]:
    tasks = []
    for row in load_jsonl(source):
        mode = "preserve" if row["binding"] == "anchored" else "reevaluate"
        tasks.append(
            _normal_task(
                audit_id="full_diagnostic",
                task_id=f"revision-full-{row['id']}",
                source="Matched Timing Diagnostic",
                pair_id=f"full::{_pair_key(row['id'])}",
                mode=mode,
                instruction=row["instruction"],
                initial_state=row["initial_state"],
                refreshed_state=row["refreshed_state"],
                selector=row["selector"],
                action=row["action"],
                action_schema=row["action_schema"],
                pre_target=row["pre_refresh_target"],
                post_target=row["post_refresh_target"],
                correct_target=row["correct_target"],
                update=row["update"],
                actionable=row["correct_target"] != "INVALID_BOUND_ENTITY",
                metadata={"source_task_id": row["id"], "binding": row["binding"]},
            )
        )
    return sorted(tasks, key=lambda row: (row["pair_id"], row["reference_mode_gold"]))


def _human_majorities(root: Path) -> dict[str, dict[str, Any]]:
    validation = root / "human_validation"
    with (validation / "annotation_key_private.csv").open(encoding="utf-8-sig", newline="") as handle:
        keys = {
            row["item_id"]: row
            for row in csv.DictReader(handle)
            if row["variant"] == "human_rewrite"
        }
    returns: list[dict[str, str]] = []
    for index in range(1, 4):
        path = validation / "normalized_returns" / f"annotator_{index}.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            returns.append({row["item_id"]: row["response"].strip() for row in csv.DictReader(handle)})
    by_source: dict[str, dict[str, Any]] = {}
    for item_id, key in keys.items():
        counts = Counter(values.get(item_id, "") for values in returns)
        counts.pop("", None)
        majority = counts.most_common(1)[0][0] if counts and counts.most_common(1)[0][1] >= 2 else None
        by_source[key["source_task_id"]] = {
            "human_item_id": item_id,
            "human_majority": exact_target(majority),
            "human_majority_determinate": majority is not None,
            "human_majority_actionable": majority not in {None, "REJECT", "CLARIFY"},
        }
    return by_source


def build_human_rewrite(source: Path, root: Path) -> list[dict[str, Any]]:
    majority = _human_majorities(root)
    tasks = []
    for row in load_jsonl(source):
        mode = "preserve" if row["binding"] == "anchored" else "reevaluate"
        metadata = {"source_task_id": row["id"], "binding": row["binding"]}
        metadata.update(majority.get(row["id"], {}))
        tasks.append(
            _normal_task(
                audit_id="human_rewrite",
                task_id=f"revision-human-{row['id']}",
                source="independent human rewrite of authored task",
                pair_id=f"human::{_pair_key(row['id'])}",
                mode=mode,
                instruction=row["instruction"],
                initial_state=row["initial_state"],
                refreshed_state=row["refreshed_state"],
                selector=row["selector"],
                action=row["action"],
                action_schema=row["action_schema"],
                pre_target=row["pre_refresh_target"],
                post_target=row["post_refresh_target"],
                correct_target=row["correct_target"],
                update=row["update"],
                actionable=row["correct_target"] != "INVALID_BOUND_ENTITY",
                metadata=metadata,
            )
        )
    return sorted(tasks, key=lambda row: (row["pair_id"], row["reference_mode_gold"]))


def _patched(records: list[dict[str, Any]], patch: dict[str, Any]) -> list[dict[str, Any]]:
    result = json.loads(json.dumps(records))
    for row in result:
        if _record_id(row) == str(patch["entity_id"]):
            row[patch["field"]] = patch["new_value"]
            return result
    raise ValueError("source-grounded refresh patch target is missing")


def _source_action_schema(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": row["write_tool"],
        "target_parameter": {
            "add": "product_id",
            "update": "product_id",
            "remove": "product_id",
            "append": "file_id",
            "share": "file_id",
            "delete": "file_id",
            "delete_email": "email_id",
            "reschedule": "event_id",
            "cancel_event": "event_id",
        }[row["action"]],
    }


def _toolsandbox_states(row: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    field = row["rank_field"]
    descending = bool(row["descending"])
    initial_values = (30, 20, 10) if descending else (10, 20, 30)
    refreshed_values = (20, 30, 10) if descending else (20, 10, 30)
    ids = (row["initial_target_id"], row["refreshed_target_id"], "REM-C")
    initial = [
        {"id": target, field: value, "editable": True}
        for target, value in zip(ids, initial_values)
    ]
    refreshed = [
        {"id": target, field: value, "editable": True}
        for target, value in zip(ids, refreshed_values)
    ]
    return initial, refreshed


def build_source_grounded(source_anchored: Path, toolsandbox: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    external = [row for row in load_jsonl(source_anchored) if row["transition"] == "changed"]
    for row in external:
        mode = row["timing"]
        instruction = " ".join(message["content"] for message in row["messages"])
        tasks.append(
            _normal_task(
                audit_id="source_grounded",
                task_id=f"revision-source-{row['task_id']}",
                source=row["repository"],
                pair_id=f"source::{row['repository']}::{row['cluster_id']}",
                mode=mode,
                instruction=instruction,
                initial_state=row["source_entities"],
                refreshed_state=_patched(row["source_entities"], row["refresh_patch"]),
                selector=row["selector"],
                action=row["action"],
                action_schema=_source_action_schema(row),
                pre_target=row["initial_winner_id"],
                post_target=row["refreshed_winner_id"],
                correct_target=row["expected_target_id"],
                update="changed",
                actionable=True,
                metadata={
                    "repository": row["repository"],
                    "source_relpath": row["source_relpath"],
                    "source_sha256": row["source_sha256"],
                    "source_tool_schema": {"read": row["read_tool"], "write": row["write_tool"]},
                },
            )
        )

    raw_toolsandbox = [row for row in load_jsonl(toolsandbox) if row["transition"] == "flip"]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in raw_toolsandbox:
        grouped[(row["cluster_id"], row["paraphrase_id"])].append(row)
    keys: list[tuple[str, str]] = []
    clusters = sorted({key[0] for key in grouped})
    paraphrases = sorted({key[1] for key in grouped})
    for paraphrase in paraphrases:
        for cluster in clusters:
            key = (cluster, paraphrase)
            if key in grouped:
                keys.append(key)
            if len(keys) == 10:
                break
        if len(keys) == 10:
            break
    if len(keys) != 10:
        raise ValueError(f"expected ten deterministic ToolSandbox pairs, found {len(keys)}")
    for key in keys:
        pair = grouped[key]
        if len(pair) != 2 or {row["reference_mode"] for row in pair} != {"preserve", "reevaluate"}:
            raise ValueError(f"invalid ToolSandbox pair: {key}")
        for row in pair:
            initial, refreshed = _toolsandbox_states(row)
            tasks.append(
                _normal_task(
                    audit_id="source_grounded",
                    task_id=f"revision-source-{row['scenario_id']}",
                    source="ToolSandbox",
                    pair_id=f"source::ToolSandbox::{key[0]}::{key[1]}",
                    mode=row["reference_mode"],
                    instruction=row["instruction"],
                    initial_state=initial,
                    refreshed_state=refreshed,
                    selector=row["selector"],
                    action="postpone",
                    action_schema={"tool": "postpone_reminder", "target_parameter": "reminder_id"},
                    pre_target=row["initial_target_id"],
                    post_target=row["refreshed_target_id"],
                    correct_target=row["correct_target_id"],
                    update="changed",
                    actionable=True,
                    metadata={
                        "repository": "ToolSandbox",
                        "cluster_id": row["cluster_id"],
                        "paraphrase_id": row["paraphrase_id"],
                        "source_tool_schema": {"read": "search_reminders", "write": "postpone_reminder"},
                    },
                )
            )
    return sorted(tasks, key=lambda row: (row["pair_id"], row["reference_mode_gold"]))


def validate_inventory(tasks: list[dict[str, Any]], audit_id: str) -> dict[str, Any]:
    expected_rows = {"full_diagnostic": 160, "human_rewrite": 50, "source_grounded": 60}
    errors: list[str] = []
    if len(tasks) != expected_rows[audit_id]:
        errors.append(f"expected {expected_rows[audit_id]} rows, found {len(tasks)}")
    if len({row["id"] for row in tasks}) != len(tasks):
        errors.append("duplicate task IDs")
    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in tasks:
        pairs[row["pair_id"]].append(row)
        if row["audit_id"] != audit_id:
            errors.append(f"audit mismatch: {row['id']}")
        ids0 = {_record_id(item) for item in row["initial_state"]}
        ids1 = {_record_id(item) for item in row["refreshed_state"]}
        if row["pre_refresh_target"] not in ids0:
            errors.append(f"missing initial target: {row['id']}")
        if row["actionable_core"] and row["correct_target"] not in ids1:
            errors.append(f"missing actionable gold: {row['id']}")
        if row["update"] == "changed" and row["pre_refresh_target"] == row["post_refresh_target"]:
            errors.append(f"changed row has unchanged winner: {row['id']}")
    complete_pairs = 0
    changed_pairs = 0
    for pair_id, pair in pairs.items():
        if len(pair) == 2 and {row["reference_mode_gold"] for row in pair} == {"preserve", "reevaluate"}:
            complete_pairs += 1
            preserve = next(row for row in pair if row["reference_mode_gold"] == "preserve")
            reevaluate = next(row for row in pair if row["reference_mode_gold"] == "reevaluate")
            shared = ("initial_state", "refreshed_state", "selector", "action", "action_schema")
            if any(preserve[key] != reevaluate[key] for key in shared):
                errors.append(f"pair differs beyond discourse: {pair_id}")
            if preserve["pre_refresh_target"] != reevaluate["pre_refresh_target"] or preserve["post_refresh_target"] != reevaluate["post_refresh_target"]:
                errors.append(f"pair target states differ: {pair_id}")
            if (
                preserve["pre_refresh_target"] != preserve["post_refresh_target"]
                and all(row["actionable_core"] for row in pair)
            ):
                changed_pairs += 1
                if preserve["correct_target"] == reevaluate["correct_target"]:
                    errors.append(f"changed pair lacks opposite gold: {pair_id}")
    if audit_id == "full_diagnostic" and (complete_pairs != 80 or changed_pairs != 32):
        errors.append(f"full diagnostic pair counts are {complete_pairs}/{changed_pairs}, expected 80/32")
    if audit_id == "human_rewrite" and complete_pairs != 7:
        errors.append(f"human rewrite has {complete_pairs} complete pairs, expected 7")
    if audit_id == "source_grounded":
        source_counts = Counter(row["source"] for row in tasks)
        if source_counts != {"STATE-Bench": 20, "AgentDojo": 20, "ToolSandbox": 20}:
            errors.append(f"source rows are unbalanced: {dict(source_counts)}")
        if complete_pairs != 30 or changed_pairs != 30:
            errors.append(f"source-grounded pair counts are {complete_pairs}/{changed_pairs}, expected 30/30")
    if errors:
        raise ValueError("; ".join(errors[:20]))
    return {
        "audit_id": audit_id,
        "rows": len(tasks),
        "clusters": len(pairs),
        "complete_pairs": complete_pairs,
        "changed_pairs": changed_pairs,
        "source_rows": dict(sorted(Counter(row["source"] for row in tasks).items())),
        "cluster_sizes": dict(sorted(Counter(len(pair) for pair in pairs.values()).items())),
    }


def allowed_ids(task: dict[str, Any]) -> set[str]:
    ids = {_record_id(row) for row in task["initial_state"] + task["refreshed_state"]}
    ids.add("INVALID_BOUND_ENTITY")
    return ids


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(f"json_parse_error: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("schema_error: top-level value must be an object")
    return value


def parse_compiler_exact(text: str, task: dict[str, Any]) -> dict[str, Any]:
    value = parse_json_object(text)
    if set(value) != {"reference_mode", "bound_target_id", "selector"}:
        raise ValueError("schema_error: compiler keys are not exact")
    mode = value["reference_mode"]
    if mode not in {"preserve", "reevaluate"}:
        raise ValueError("schema_error: invalid reference_mode")
    target = exact_target(value["bound_target_id"])
    if mode == "reevaluate" and target is not None:
        raise ValueError("schema_error: reevaluate bound_target_id must be null")
    if mode == "preserve" and target not in allowed_ids(task):
        raise ValueError("schema_error: preserve bound_target_id is not an exact state ID")
    selector = value["selector"]
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError("schema_error: selector must be nonempty")
    return {"reference_mode": mode, "bound_target_id": target, "selector": selector.strip()}


def parse_actor_exact(text: str, task: dict[str, Any]) -> dict[str, Any]:
    value = parse_json_object(text)
    if set(value) != {"action", "target_id"}:
        raise ValueError("schema_error: actor keys are not exact")
    target = exact_target(value["target_id"])
    if target not in allowed_ids(task):
        raise ValueError("schema_error: target_id is not an exact state ID")
    if not isinstance(value["action"], str) or not value["action"].strip():
        raise ValueError("schema_error: action must be nonempty")
    return {"action": value["action"].strip(), "target_id": target}


def _action_valid(task: dict[str, Any], target: str | None) -> bool:
    if target is None or target == "INVALID_BOUND_ENTITY":
        return False
    record = next((row for row in task["refreshed_state"] if _record_id(row) == target), None)
    if record is None:
        return False
    preconditions = task.get("action_schema", {}).get("preconditions", {})
    return all(record.get(key) == value for key, value in preconditions.items())


def enforced_target(
    compiler: dict[str, Any] | None,
    visible: str | None,
    task: dict[str, Any],
) -> str | None:
    if compiler and compiler.get("reference_mode") == "preserve":
        target = exact_target(compiler.get("bound_target_id"))
        return target if _action_valid(task, target) else "INVALID_BOUND_ENTITY"
    return exact_target(visible)


def validate_run_row(row: dict[str, Any], require_complete: bool = False) -> None:
    if row.get("run_version") != RUN_VERSION or row.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("invalid revision-run provenance")
    task = row.get("task", {})
    if task.get("audit_id") not in AUDITS:
        raise ValueError("invalid revision audit task")
    if row.get("logical_calls_planned") != 3:
        raise ValueError("revision task must plan three logical calls")
    actors = row.get("actors", {})
    if set(actors) != {"history_only", "decision_visible"}:
        raise ValueError("matched actors are incomplete")
    outcomes = row.get("outcomes", {})
    if set(outcomes) != set(CONDITIONS):
        raise ValueError("outcomes are incomplete")
    expected = enforced_target(
        (row.get("compiler") or {}).get("parsed"), outcomes["decision_visible"], task
    )
    if outcomes["decision_enforced"] != expected:
        raise ValueError("offline enforcement is inconsistent")
    payloads: dict[str, dict[str, Any]] = {}
    for condition, actor in actors.items():
        attempts = actor.get("attempts", [])
        if attempts and attempts[-1].get("request"):
            messages = attempts[-1]["request"].get("messages", [])
            payloads[condition] = json.loads(messages[1]["content"])
    if set(payloads) == {"history_only", "decision_visible"}:
        visible = dict(payloads["decision_visible"])
        decision = visible.pop("compiler_decision", None)
        if payloads["history_only"] != visible:
            raise ValueError("actor payloads differ beyond compiler_decision")
        if decision != row["compiler"].get("parsed"):
            raise ValueError("visible actor did not receive the shared decision")
    if require_complete and (
        not row.get("complete")
        or row.get("logical_calls_completed") != 3
        or row.get("compiler", {}).get("parsed") is None
        or any(actor.get("parsed") is None for actor in actors.values())
    ):
        raise ValueError("health-smoke row is incomplete")


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def _bootstrap(
    clusters: dict[str, list[dict[str, Any]]],
    statistic: Callable[[list[dict[str, Any]]], float | None],
    seed: int,
    samples: int,
) -> list[float | None]:
    names = sorted(clusters)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        sample = [row for _ in names for row in clusters[rng.choice(names)]]
        value = statistic(sample)
        if value is not None:
            values.append(value)
    return [_percentile(values, 0.025), _percentile(values, 0.975)]


def _target(row: dict[str, Any], condition: str) -> str | None:
    return exact_target(row.get("outcomes", {}).get(condition))


def _gold(row: dict[str, Any], human: bool = False) -> str | None:
    if human:
        return exact_target(row["task"].get("metadata", {}).get("human_majority"))
    return exact_target(row["task"]["correct_target"])


def _measure(
    rows: list[dict[str, Any]],
    clusters: dict[str, list[dict[str, Any]]],
    condition: str,
    eligible: Callable[[dict[str, Any]], bool] = lambda row: True,
    human: bool = False,
    seed: int = BOOTSTRAP_SEED,
    samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, Any]:
    use = [row for row in rows if eligible(row)]
    count = sum(_target(row, condition) == _gold(row, human) for row in use)

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        selected = [row for row in sample if eligible(row)]
        if not selected:
            return None
        return sum(_target(row, condition) == _gold(row, human) for row in selected) / len(selected)

    return {
        "numerator": count,
        "denominator": len(use),
        "rate": count / len(use) if use else None,
        "ci95_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _pair_measure(
    clusters: dict[str, list[dict[str, Any]]],
    condition: str,
    changed_only: bool,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    eligible = {
        key: pair
        for key, pair in clusters.items()
        if len(pair) == 2
        and {row["task"]["reference_mode_gold"] for row in pair} == {"preserve", "reevaluate"}
        and (
            not changed_only
            or (
                pair[0]["task"]["pre_refresh_target"] != pair[0]["task"]["post_refresh_target"]
                and all(row["task"]["actionable_core"] for row in pair)
            )
        )
    }

    def correct(pair: list[dict[str, Any]]) -> bool:
        return all(_target(row, condition) == _gold(row) for row in pair)

    count = sum(correct(pair) for pair in eligible.values())
    interval_clusters = eligible

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        pairs = [sample[index:index + 2] for index in range(0, len(sample), 2)]
        return sum(correct(pair) for pair in pairs) / len(pairs) if pairs else None

    return {
        "numerator": count,
        "denominator": len(eligible),
        "rate": count / len(eligible) if eligible else None,
        "ci95_cluster": _bootstrap(interval_clusters, statistic, seed, samples),
    }


def _event_rate(
    rows: list[dict[str, Any]],
    clusters: dict[str, list[dict[str, Any]]],
    condition: str,
    mode: str,
    event: str,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    def eligible(row: dict[str, Any]) -> bool:
        task = row["task"]
        compiler = row.get("compiler", {}).get("parsed") or {}
        return (
            task["reference_mode_gold"] == mode
            and task["pre_refresh_target"] != task["post_refresh_target"]
            and compiler.get("reference_mode") == mode
            and (
                mode != "preserve"
                or exact_target(compiler.get("bound_target_id")) == task["pre_refresh_target"]
            )
        )

    use = [row for row in rows if eligible(row)]
    desired = (
        (lambda row: _target(row, condition) == row["task"]["post_refresh_target"])
        if event == "substitution"
        else (lambda row: _target(row, condition) == row["task"]["pre_refresh_target"])
    )
    count = sum(desired(row) for row in use)

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        selected = [row for row in sample if eligible(row)]
        return sum(desired(row) for row in selected) / len(selected) if selected else None

    return {
        "numerator": count,
        "denominator": len(use),
        "rate": count / len(use) if use else None,
        "ci95_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _wrong_write_measure(
    rows: list[dict[str, Any]],
    clusters: dict[str, list[dict[str, Any]]],
    condition: str,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    use = [row for row in rows if row["task"]["actionable_core"]]

    def wrong(row: dict[str, Any]) -> bool:
        target = _target(row, condition)
        return target not in {None, "INVALID_BOUND_ENTITY"} and target != _gold(row)

    count = sum(wrong(row) for row in use)

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        selected = [row for row in sample if row["task"]["actionable_core"]]
        return sum(wrong(row) for row in selected) / len(selected) if selected else None

    return {
        "numerator": count,
        "denominator": len(use),
        "rate": count / len(use) if use else None,
        "ci95_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _paired_difference(
    clusters: dict[str, list[dict[str, Any]]],
    statistic: Callable[[list[dict[str, Any]], str], float | None],
    seed: int,
    samples: int,
) -> dict[str, Any]:
    rows = [row for pair in clusters.values() for row in pair]
    left, right = statistic(rows, "history_only"), statistic(rows, "decision_visible")
    estimate = None if left is None or right is None else right - left

    def difference(sample: list[dict[str, Any]]) -> float | None:
        sample_left = statistic(sample, "history_only")
        sample_right = statistic(sample, "decision_visible")
        return None if sample_left is None or sample_right is None else sample_right - sample_left

    return {
        "left": "history_only",
        "right": "decision_visible",
        "difference": estimate,
        "ci95_cluster": _bootstrap(clusters, difference, seed, samples),
    }


def build_report(
    rows: list[dict[str, Any]],
    seed: int = BOOTSTRAP_SEED,
    samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot report an empty revision audit")
    for row in rows:
        validate_run_row(row)
    audits = {row["task"]["audit_id"] for row in rows}
    if len(audits) != 1:
        raise ValueError("one report may contain only one revision audit")
    audit_id = next(iter(audits))
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
    models = []
    for model, model_rows in sorted(by_model.items()):
        clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in model_rows:
            clusters[row["task"]["pair_id"]].append(row)
        metrics: dict[str, Any] = {}
        for condition in CONDITIONS:
            metrics[condition] = {
                "all_e2e": _measure(model_rows, clusters, condition, seed=seed, samples=samples),
                "actionable_e2e": _measure(
                    model_rows,
                    clusters,
                    condition,
                    eligible=lambda row: bool(row["task"]["actionable_core"]),
                    seed=seed,
                    samples=samples,
                ),
                "reject_slice": _measure(
                    model_rows,
                    clusters,
                    condition,
                    eligible=lambda row: not row["task"]["actionable_core"],
                    seed=seed,
                    samples=samples,
                ),
                "changed_pairacc": _pair_measure(clusters, condition, True, seed, samples),
                "complete_pairacc": _pair_measure(clusters, condition, False, seed, samples),
                "preserve_substitution": _event_rate(
                    model_rows, clusters, condition, "preserve", "substitution", seed, samples
                ),
                "reevaluate_premature_lock": _event_rate(
                    model_rows, clusters, condition, "reevaluate", "lock", seed, samples
                ),
                "human_majority": _measure(
                    model_rows,
                    clusters,
                    condition,
                    eligible=lambda row: bool(
                        row["task"].get("metadata", {}).get("human_majority_determinate")
                    ),
                    human=True,
                    seed=seed,
                    samples=samples,
                ),
                "human_actionable_majority": _measure(
                    model_rows,
                    clusters,
                    condition,
                    eligible=lambda row: bool(
                        row["task"].get("metadata", {}).get("human_majority_actionable")
                    ),
                    human=True,
                    seed=seed,
                    samples=samples,
                ),
                "fixed_executor_wrong_writes": _wrong_write_measure(
                    model_rows, clusters, condition, seed, samples
                ),
            }
        source_slices: dict[str, Any] = {}
        for source in sorted({row["task"]["source"] for row in model_rows}):
            source_rows = [row for row in model_rows if row["task"]["source"] == source]
            source_clusters = {
                key: pair
                for key, pair in clusters.items()
                if pair[0]["task"]["source"] == source
            }
            source_slices[source] = {
                condition: {
                    "pairacc": _pair_measure(source_clusters, condition, True, seed, samples),
                    "e2e": _measure(source_rows, source_clusters, condition, seed=seed, samples=samples),
                }
                for condition in CONDITIONS
            }
        failures = {
            "incomplete_tasks": sum(not row.get("complete") for row in model_rows),
            "compiler": sum(row.get("compiler", {}).get("parsed") is None for row in model_rows),
            "history_actor": sum(
                row.get("actors", {}).get("history_only", {}).get("parsed") is None for row in model_rows
            ),
            "visible_actor": sum(
                row.get("actors", {}).get("decision_visible", {}).get("parsed") is None for row in model_rows
            ),
        }

        def actionable_rate(sample_rows: list[dict[str, Any]], condition: str) -> float | None:
            selected = [row for row in sample_rows if row["task"]["actionable_core"]]
            return (
                sum(_target(row, condition) == _gold(row) for row in selected) / len(selected)
                if selected
                else None
            )

        def changed_pair_rate(sample_rows: list[dict[str, Any]], condition: str) -> float | None:
            sample_pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in sample_rows:
                sample_pairs[row["task"]["pair_id"]].append(row)
            eligible_pairs = [
                pair
                for pair in sample_pairs.values()
                if len(pair) == 2
                and {row["task"]["reference_mode_gold"] for row in pair}
                == {"preserve", "reevaluate"}
                and all(row["task"]["actionable_core"] for row in pair)
                and pair[0]["task"]["pre_refresh_target"]
                != pair[0]["task"]["post_refresh_target"]
            ]
            return (
                sum(all(_target(row, condition) == _gold(row) for row in pair) for pair in eligible_pairs)
                / len(eligible_pairs)
                if eligible_pairs
                else None
            )

        differences = {
            "actionable_e2e": _paired_difference(clusters, actionable_rate, seed, samples),
            "changed_pairacc": _paired_difference(clusters, changed_pair_rate, seed, samples),
        }
        models.append(
            {
                "model": model,
                "rows": len(model_rows),
                "clusters": len(clusters),
                "cluster_sizes": dict(sorted(Counter(len(pair) for pair in clusters.values()).items())),
                "metrics": metrics,
                "source_slices": source_slices,
                "decision_visible_minus_history": differences,
                "failures": failures,
                "enforcement": {
                    "repairs": sum(
                        _target(row, "decision_visible") != _gold(row)
                        and _target(row, "decision_enforced") == _gold(row)
                        for row in model_rows
                    ),
                    "harms": sum(
                        _target(row, "decision_visible") == _gold(row)
                        and _target(row, "decision_enforced") != _gold(row)
                        for row in model_rows
                    ),
                },
                "logical_calls": {
                    "planned": sum(row.get("logical_calls_planned", 0) for row in model_rows),
                    "completed": sum(row.get("logical_calls_completed", 0) for row in model_rows),
                    "http_attempts": sum(
                        len(component.get("attempts", []))
                        for row in model_rows
                        for component in [row.get("compiler", {}), *row.get("actors", {}).values()]
                    ),
                },
            }
        )
    return {
        "report_version": "TRI-revision-matched-audit-report-v1",
        "evidence_status": EVIDENCE_STATUS,
        "audit_id": audit_id,
        "bootstrap": {"unit": "pair/workflow cluster", "seed": seed, "samples": samples},
        "models": models,
        "boundary": (
            "Matched actor evidence only. Human rewrites retain authored task semantics; source-grounded "
            "contrasts are controlled interventions, not native benchmark prevalence or open-language proof."
        ),
    }


def _fmt(metric: dict[str, Any]) -> str:
    if metric["rate"] is None:
        return f"NA ({metric['numerator']}/{metric['denominator']})"
    lo, hi = metric["ci95_cluster"]
    interval = "NA" if lo is None or hi is None else f"[{100 * lo:.1f}, {100 * hi:.1f}]"
    return f"{100 * metric['rate']:.1f}% ({metric['numerator']}/{metric['denominator']}), CI {interval}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Revision Matched Audit: {report['audit_id']}",
        "",
        f"**Evidence status:** {report['evidence_status']}.",
        "",
        report["boundary"],
        "",
    ]
    for model in report["models"]:
        lines.extend(
            [
                f"## {model['model']}",
                "",
                f"Rows/clusters: {model['rows']}/{model['clusters']}; cluster sizes: {model['cluster_sizes']}.",
                "",
                "| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for condition in CONDITIONS:
            metric = model["metrics"][condition]
            lines.append(
                f"| {condition} | {_fmt(metric['changed_pairacc'])} | {_fmt(metric['actionable_e2e'])} | "
                f"{_fmt(metric['reject_slice'])} | {_fmt(metric['preserve_substitution'])} | "
                f"{_fmt(metric['reevaluate_premature_lock'])} | {_fmt(metric['human_majority'])} | "
                f"{_fmt(metric['fixed_executor_wrong_writes'])} |"
            )
        if model["source_slices"]:
            lines.extend(["", "### Source slices", ""])
            for source, values in model["source_slices"].items():
                lines.append(
                    f"- {source}: History PairAcc {_fmt(values['history_only']['pairacc'])}; "
                    f"Visible PairAcc {_fmt(values['decision_visible']['pairacc'])}."
                )
        lines.extend(
            [
                "",
                f"Visible-minus-history changed PairAcc: "
                f"{model['decision_visible_minus_history']['changed_pairacc']}.",
                f"Visible-minus-history actionable E2E: "
                f"{model['decision_visible_minus_history']['actionable_e2e']}.",
                f"Failures: {model['failures']}; enforcement repairs/harms: "
                f"{model['enforcement']['repairs']}/{model['enforcement']['harms']}.",
                f"Logical calls completed/planned: {model['logical_calls']['completed']}/"
                f"{model['logical_calls']['planned']}; HTTP attempts: {model['logical_calls']['http_attempts']}.",
                "",
            ]
        )
    lines.append("Negative, null, mixed, parse-failure, transport-failure, and enforcement-harm outcomes are retained.")
    lines.append("")
    return "\n".join(lines)
