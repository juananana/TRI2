from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


RUN_VERSION = "TRI-unified-environment-holdout-v1"
EVIDENCE_STATUS = "planned/unverified"
ENVIRONMENT_COMMITS = {
    "AgentDojo": "089ed468cf3ed0322acc66b0211f26d9d90dbf60",
    "ToolSandbox": "165848b9a78cead7ca7fe7c89c688b58e6501219",
}
ENVIRONMENTS = tuple(ENVIRONMENT_COMMITS)
WRITERS = tuple(f"W{i}" for i in range(1, 13))
ANNOTATORS = tuple(f"A{i}" for i in range(1, 4))
TARGET_PAIRS_PER_ENV = 20
CANDIDATE_PAIRS_PER_ENV = 30
TARGET_CLUSTERS = 40
CONTROLLERS = (
    "ordinary_full_history",
    "matched_history_only",
    "matched_decision_visible",
    "historical_cta",
    "always_lock",
    "always_reevaluate",
)
DEPLOYMENT_MODELS = ("qwen", "glm", "deepseek")

PRIVATE_ARTIFACT_KEYS = {
    "participant_name",
    "full_name",
    "email_address",
    "phone_number",
    "contact_information",
    "compensation_amount",
    "compensation_category",
    "consent_timestamp",
    "recruitment_id",
    "payment_id",
    "worker_platform_id",
}

EXECUTION_STATUSES = {
    "success",
    "wrong_entity_write",
    "invalid_attempt",
    "rejection",
    "api_failure",
    "parse_failure",
}

TOOL_EVENT_ORDER = (
    "initial_selection",
    "refresh",
    "target_proposal",
    "mutation",
    "tool_result",
    "final_state_diff",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def assert_anonymous_payload(value: Any, path: str = "root") -> None:
    """Reject identity, consent, and payment fields from distributable holdout data."""
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in PRIVATE_ARTIFACT_KEYS:
                raise ValueError(f"private field leaked into anonymous artifact: {path}.{key}")
            assert_anonymous_payload(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_anonymous_payload(item, f"{path}[{index}]")


def validate_human_provenance(
    provenance: dict[str, Any], candidate_sha256: str
) -> None:
    """Require the ethics and independent-human gate before freezing model inputs."""
    assert_anonymous_payload(provenance)
    if provenance.get("status") != "complete-locked-before-model-calls":
        raise ValueError("human provenance is not complete and locked")
    if provenance.get("candidate_sha256") != candidate_sha256:
        raise ValueError("human provenance candidate hash mismatch")
    if provenance.get("environment_commits") != ENVIRONMENT_COMMITS:
        raise ValueError("human provenance environment commits mismatch")
    if provenance.get("locked_before_model_calls") is not True:
        raise ValueError("human records were not locked before model calls")
    ethics = provenance.get("ethics")
    if not isinstance(ethics, dict) or not (
        ethics.get("confirmed_before_recruitment") is True
        and ethics.get("determination")
        in {"approved", "exempt", "institutional-policy-cleared"}
    ):
        raise ValueError("ethics determination was not confirmed before recruitment")
    writers = provenance.get("writers")
    if not isinstance(writers, dict) or set(writers) != set(WRITERS):
        raise ValueError("human provenance requires exactly W1-W12")
    for writer_id, item in writers.items():
        if not isinstance(item, dict) or not (
            item.get("adult") is True
            and item.get("consented") is True
            and item.get("independent") is True
            and item.get("completed") is True
            and item.get("prior_tri_exposure") is False
            and item.get("saw_tri_templates_or_rule_star") is False
            and item.get("saw_model_outputs_or_results") is False
        ):
            raise ValueError(f"writer independence gate failed for {writer_id}")
    annotators = provenance.get("annotators")
    if not isinstance(annotators, dict) or set(annotators) != set(ANNOTATORS):
        raise ValueError("human provenance requires exactly A1-A3")
    for annotator, item in annotators.items():
        if not isinstance(item, dict) or not (
            item.get("independent") is True
            and item.get("blind") is True
            and item.get("completed") is True
            and item.get("saw_model_outputs_before_lock") is False
        ):
            raise ValueError(f"annotator independence gate failed for {annotator}")


def _ids(state: Any) -> set[str]:
    if not isinstance(state, list):
        raise ValueError("state snapshot must be a list")
    ids = {str(item.get("id")) for item in state if isinstance(item, dict) and item.get("id") is not None}
    if len(ids) != len(state):
        raise ValueError("state IDs must be unique and non-null")
    return ids


def _winner(row: dict[str, Any], suffix: str) -> str:
    value = row.get(f"{suffix}_winner")
    if value is None:
        raise ValueError(f"missing {suffix}_winner for {row.get('cluster_id')}")
    return str(value)


def validate_candidate_rows(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("candidate inventory is empty")
    seen_items: set[str] = set()
    by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        cluster = str(row.get("cluster_id", ""))
        item_id = str(row.get("item_id", ""))
        if not cluster or not item_id or item_id in seen_items:
            raise ValueError(f"duplicate or missing item_id/cluster_id: {item_id}/{cluster}")
        seen_items.add(item_id)
        environment = row.get("environment")
        if environment not in ENVIRONMENTS:
            raise ValueError(f"unknown environment: {environment}")
        if row.get("environment_commit") != ENVIRONMENT_COMMITS[environment]:
            raise ValueError(f"environment commit mismatch for {cluster}")
        assert_anonymous_payload(row)
        for key in (
            "candidate_order",
            "selector",
            "action",
            "action_schema",
            "preflight_state_diffs",
            "s0_state",
            "s1_changed_state",
            "s1_stable_state",
            "stable_winner",
        ):
            if key not in row:
                raise ValueError(f"missing {key} for {cluster}")
        if not isinstance(row["candidate_order"], int) or isinstance(
            row["candidate_order"], bool
        ):
            raise ValueError(f"candidate_order must be an integer for {cluster}")
        s0 = _ids(row["s0_state"])
        changed = _ids(row["s1_changed_state"])
        stable = _ids(row["s1_stable_state"])
        old = _winner(row, "pre_refresh")
        new = _winner(row, "post_refresh")
        if old not in s0 or old not in changed or new not in changed:
            raise ValueError(f"changed row target linkage failed for {cluster}")
        if old == new:
            raise ValueError(f"changed row has no winner change for {cluster}")
        if old not in stable:
            raise ValueError(f"stable state must retain old target for {cluster}")
        if str(row["stable_winner"]) != old:
            raise ValueError(f"stable state must keep the pre-refresh winner for {cluster}")
        preconditions = row["action_schema"].get("preconditions", {})
        if not isinstance(preconditions, dict):
            raise ValueError(f"action preconditions must be an object for {cluster}")
        for state_name, state, target in (
            ("changed old", row["s1_changed_state"], old),
            ("changed new", row["s1_changed_state"], new),
            ("stable old", row["s1_stable_state"], old),
        ):
            record = next(item for item in state if str(item["id"]) == target)
            if any(record.get(field) != expected for field, expected in preconditions.items()):
                raise ValueError(f"{state_name} target is not action-valid for {cluster}")
        preflight = row["preflight_state_diffs"]
        expected_diffs = {
            "changed_old": old,
            "changed_new": new,
            "stable_old": old,
        }
        if not isinstance(preflight, dict) or set(preflight) != set(expected_diffs):
            raise ValueError(f"preflight state diffs are incomplete for {cluster}")
        for diff_name, expected_target in expected_diffs.items():
            diff = preflight[diff_name]
            if not isinstance(diff, list) or not diff:
                raise ValueError(f"preflight state diff is empty for {cluster}/{diff_name}")
            changed_targets = {
                str(item.get("target_id"))
                for item in diff
                if isinstance(item, dict) and item.get("target_id") is not None
            }
            if changed_targets != {expected_target}:
                raise ValueError(
                    f"preflight state diff target mismatch for {cluster}/{diff_name}"
                )
        by_cluster[cluster].append(row)
    shared_fields = (
        "environment",
        "environment_commit",
        "candidate_order",
        "selector",
        "action",
        "action_schema",
        "preflight_state_diffs",
        "s0_state",
        "s1_changed_state",
        "s1_stable_state",
        "pre_refresh_winner",
        "post_refresh_winner",
        "stable_winner",
    )
    for cluster, members in by_cluster.items():
        if len(members) != 2:
            raise ValueError("each candidate cluster must contain exactly two instruction members")
        validate_writer_assignment(members)
        for field in shared_fields:
            if members[0][field] != members[1][field]:
                raise ValueError(f"candidate pair differs on shared field {field}: {cluster}")
    for environment in ENVIRONMENTS:
        clusters = [
            members
            for members in by_cluster.values()
            if members[0]["environment"] == environment
        ]
        orders = [members[0]["candidate_order"] for members in clusters]
        if len(clusters) != CANDIDATE_PAIRS_PER_ENV:
            raise ValueError(
                f"{environment} requires exactly {CANDIDATE_PAIRS_PER_ENV} candidate pairs"
            )
        if sorted(orders) != list(range(CANDIDATE_PAIRS_PER_ENV)):
            raise ValueError(
                f"{environment} candidate_order must be unique 0..{CANDIDATE_PAIRS_PER_ENV - 1}"
            )


def validate_writer_assignment(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 2:
        raise ValueError("each candidate cluster needs two instruction members")
    writers = {str(row.get("writer_id")) for row in rows}
    if len(writers) != 2 or not writers.issubset(WRITERS):
        raise ValueError("pair members must use two distinct frozen writers")
    modes = {str(row.get("reference_mode")) for row in rows}
    if modes != {"preserve", "reevaluate"}:
        raise ValueError("candidate pair must contain Preserve and Reevaluate")


def _majority(values: list[str]) -> str | None:
    counts = Counter(value for value in values if value)
    if not counts:
        return None
    value, count = counts.most_common(1)[0]
    return value if count >= 2 else None


def annotate_clear(row: dict[str, Any]) -> dict[str, Any]:
    required = {"writer_intent", "adjudications", "writer_id", "reference_mode"}
    if not required.issubset(row):
        raise ValueError(f"missing human fields for {row.get('item_id')}")
    adjudications = row["adjudications"]
    if not isinstance(adjudications, dict) or set(adjudications) != set(ANNOTATORS):
        raise ValueError(f"exactly three annotators required for {row.get('item_id')}")
    labels = [str(adjudications[key]) for key in ANNOTATORS]
    majority = _majority(labels)
    writer_intent = str(row["writer_intent"])
    expected_target = str(
        row["pre_refresh_winner"]
        if row["reference_mode"] == "preserve"
        else row["post_refresh_winner"]
    )
    clear = (
        majority is not None
        and majority == writer_intent
        and writer_intent == expected_target
    )
    return {
        **row,
        "annotator_majority": majority,
        "expected_target": expected_target,
        "clear": clear,
        "adjudication_agreement": sum(label == majority for label in labels) / 3 if majority else 0.0,
    }


def select_clear_clusters(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["cluster_id"])].append(annotate_clear(row))
    clear_by_env: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cluster_id, members in grouped.items():
        if len(members) != 2:
            raise ValueError(f"cluster {cluster_id} does not have two members")
        validate_writer_assignment(members)
        if all(member["clear"] for member in members):
            environment = members[0]["environment"]
            clear_by_env[environment].append(
                {
                    "cluster_id": cluster_id,
                    "candidate_order": members[0]["candidate_order"],
                    "members": members,
                }
            )
    for environment in ENVIRONMENTS:
        if len(clear_by_env[environment]) < TARGET_PAIRS_PER_ENV:
            raise RuntimeError(
                f"clear-cluster gate failed for {environment}: "
                f"{len(clear_by_env[environment])}/{TARGET_PAIRS_PER_ENV}"
            )
    selected = []
    for environment in ENVIRONMENTS:
        ordered = sorted(
            clear_by_env[environment], key=lambda item: item["candidate_order"]
        )
        selected.extend(ordered[:TARGET_PAIRS_PER_ENV])
    if len(selected) != TARGET_CLUSTERS:
        raise AssertionError("selection did not produce exactly 40 clusters")
    return selected


def derive_execution_rows(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(clusters) != TARGET_CLUSTERS:
        raise ValueError("execution freeze requires exactly 40 clear clusters")
    rows: list[dict[str, Any]] = []
    for cluster in clusters:
        members = cluster["members"]
        preserve = next(row for row in members if row["reference_mode"] == "preserve")
        reevaluate = next(row for row in members if row["reference_mode"] == "reevaluate")
        base = {
            "cluster_id": cluster["cluster_id"],
            "environment": preserve["environment"],
            "environment_commit": preserve["environment_commit"],
            "candidate_order": preserve["candidate_order"],
            "selector": preserve["selector"],
            "action": preserve["action"],
            "action_schema": preserve["action_schema"],
            "preflight_state_diffs": preserve["preflight_state_diffs"],
            "s0_state": preserve["s0_state"],
            "adjudications": {row["item_id"]: row["adjudications"] for row in members},
        }
        for row_kind, instruction_row, state_key, changed in (
            ("changed_preserve", preserve, "s1_changed_state", True),
            ("changed_reevaluate", reevaluate, "s1_changed_state", True),
            ("stable_preserve", preserve, "s1_stable_state", False),
        ):
            execution = {
                **base,
                "row_id": f"{cluster['cluster_id']}::{row_kind}",
                "row_kind": row_kind,
                "instruction": instruction_row["instruction"],
                "reference_mode_gold": instruction_row["reference_mode"],
                "s1_state": instruction_row[state_key],
                "pre_refresh_target": instruction_row["pre_refresh_winner"],
                "post_refresh_target": instruction_row["post_refresh_winner"] if changed else instruction_row["pre_refresh_winner"],
                "changed_winner": changed,
                "writer_id": instruction_row["writer_id"],
            }
            rows.append(execution)
    if len(rows) != 120:
        raise AssertionError("execution freeze did not produce 120 rows")
    return rows


def freeze_manifest(
    candidates: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    human_provenance: dict[str, Any],
    candidate_sha256: str,
) -> dict[str, Any]:
    validate_human_provenance(human_provenance, candidate_sha256)
    payload = "".join(canonical_json(row) + "\n" for row in rows).encode("utf-8")
    return {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "candidate_rows": len(candidates),
        "selected_clusters": len(selected),
        "execution_rows": len(rows),
        "environment_commits": ENVIRONMENT_COMMITS,
        "selected_cluster_ids": [cluster["cluster_id"] for cluster in selected],
        "candidate_sha256": candidate_sha256,
        "human_provenance_sha256": sha256_text(canonical_json(human_provenance)),
        "human_gate_passed": True,
        "execution_rows_sha256": sha256_bytes(payload),
        "model_calls_allowed": True,
    }


def selection_maximizers(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        raise ValueError("controller result table is empty")
    required = {
        "environment",
        "model",
        "controller",
        "e2e",
        "pairacc",
        "wrong_write_rate",
    }
    if any(not required.issubset(row) for row in results):
        raise ValueError("selection results are missing required fields")
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        groups[(str(row["environment"]), str(row["model"]))].append(row)
    expected_cells = {
        (environment, model)
        for environment in ENVIRONMENTS
        for model in DEPLOYMENT_MODELS
    }
    if set(groups) != expected_cells:
        raise ValueError("controller results require the complete 2-environment x 3-model matrix")
    output = []
    for key, rows in sorted(groups.items()):
        controllers = [str(row["controller"]) for row in rows]
        if len(controllers) != len(set(controllers)) or set(controllers) != set(CONTROLLERS):
            raise ValueError(
                f"{key} must contain each of the six frozen controllers exactly once"
            )
        max_e2e = max(float(row["e2e"]) for row in rows)
        max_pairacc = max(float(row["pairacc"]) for row in rows)
        e2e_set = sorted(row["controller"] for row in rows if float(row["e2e"]) == max_e2e)
        pair_set = sorted(row["controller"] for row in rows if float(row["pairacc"]) == max_pairacc)
        pair_rows = [row for row in rows if row["controller"] in pair_set]
        e2e_rows = [row for row in rows if row["controller"] in e2e_set]
        output.append({
            "environment": key[0],
            "model": key[1],
            "e2e_maximizers": e2e_set,
            "pairacc_maximizers": pair_set,
            "strong_selection_change": not set(e2e_set).intersection(pair_set),
            "pairacc_wrong_write_rate_max": max(
                float(row["wrong_write_rate"]) for row in pair_rows
            ),
            "e2e_wrong_write_rate_min": min(
                float(row["wrong_write_rate"]) for row in e2e_rows
            ),
            "e2e_regret_of_pairacc_maximizers": [
                max_e2e - max(float(row["e2e"]) for row in pair_rows),
                max_e2e - min(float(row["e2e"]) for row in pair_rows),
            ],
            "pairacc_regret_of_e2e_maximizers": [
                max_pairacc - max(float(row["pairacc"]) for row in e2e_rows),
                max_pairacc - min(float(row["pairacc"]) for row in e2e_rows),
            ],
        })
    return {
        "cells": output,
        "promote_practical_selection": sum(
            cell["strong_selection_change"]
            and cell["pairacc_wrong_write_rate_max"]
            <= cell["e2e_wrong_write_rate_min"]
            for cell in output
        ) >= 2,
    }


def summarize_executed_results(
    frozen_rows: list[dict[str, Any]], results: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Validate the complete raw execution matrix and derive selection-table endpoints."""
    if len(frozen_rows) != 120 or len({row.get("row_id") for row in frozen_rows}) != 120:
        raise ValueError("execution summary requires the frozen 120-row inventory")
    frozen_by_id = {str(row["row_id"]): row for row in frozen_rows}
    expected = {
        (environment, model, controller, row_id)
        for environment in ENVIRONMENTS
        for model in DEPLOYMENT_MODELS
        for controller in CONTROLLERS
        for row_id, row in frozen_by_id.items()
        if row["environment"] == environment
    }
    observed: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    required = {
        "environment",
        "model",
        "controller",
        "row_id",
        "execution_status",
        "initial_selection_id",
        "refresh_completed",
        "proposed_target_id",
        "mutated_target_id",
        "tool_trace",
        "tool_result",
        "final_state_diff",
        "collateral_change_count",
        "call_count",
        "input_tokens",
        "output_tokens",
        "latency_ms",
    }
    for result in results:
        assert_anonymous_payload(result)
        if not required.issubset(result):
            raise ValueError("executed result is missing required trajectory fields")
        key = (
            str(result["environment"]),
            str(result["model"]),
            str(result["controller"]),
            str(result["row_id"]),
        )
        if key in observed:
            raise ValueError(f"duplicate executed result: {key}")
        if result["execution_status"] not in EXECUTION_STATUSES:
            raise ValueError(f"unknown execution status: {result['execution_status']}")
        if not isinstance(result["tool_trace"], list):
            raise ValueError("tool_trace must retain ordered real-interface events")
        if not isinstance(result["final_state_diff"], list):
            raise ValueError("final_state_diff must be a list")
        event_names = []
        for event in result["tool_trace"]:
            if not isinstance(event, dict) or event.get("event") not in TOOL_EVENT_ORDER:
                raise ValueError("tool_trace contains an unknown or unstructured event")
            event_names.append(str(event["event"]))
        event_positions = [TOOL_EVENT_ORDER.index(name) for name in event_names]
        if event_positions != sorted(event_positions):
            raise ValueError("tool_trace events are out of order")
        if result["execution_status"] in {
            "success",
            "wrong_entity_write",
            "invalid_attempt",
        } and not set(TOOL_EVENT_ORDER).issubset(event_names):
            raise ValueError("completed tool attempt is missing required trace events")
        if result["execution_status"] == "rejection" and not {
            "initial_selection",
            "refresh",
            "target_proposal",
            "final_state_diff",
        }.issubset(event_names):
            raise ValueError("rejection trace is missing required events")
        if any(
            not isinstance(result[field], (int, float))
            or isinstance(result[field], bool)
            or result[field] < 0
            for field in (
                "collateral_change_count",
                "call_count",
                "input_tokens",
                "output_tokens",
                "latency_ms",
            )
        ):
            raise ValueError("execution resource fields must be non-negative numbers")
        mutated = result["mutated_target_id"]
        if result["execution_status"] in {"success", "wrong_entity_write"}:
            if mutated is None or result["tool_result"] is None:
                raise ValueError("write status requires a mutation target and tool result")
        elif mutated is not None:
            raise ValueError("non-write status cannot claim a mutated target")
        changed_targets = {
            str(item.get("target_id"))
            for item in result["final_state_diff"]
            if isinstance(item, dict) and item.get("target_id") is not None
        }
        if mutated is not None and str(mutated) not in changed_targets:
            raise ValueError("final_state_diff does not contain the mutated target")
        collateral_targets = changed_targets - ({str(mutated)} if mutated is not None else set())
        if int(result["collateral_change_count"]) != len(collateral_targets):
            raise ValueError("collateral_change_count disagrees with final_state_diff")
        observed[key] = result
    if set(observed) != expected:
        missing = len(expected - set(observed))
        extra = len(set(observed) - expected)
        raise ValueError(
            f"executed results do not cover frozen matrix: missing={missing}, extra={extra}"
        )

    summaries: list[dict[str, Any]] = []
    for environment in ENVIRONMENTS:
        environment_rows = {
            row_id: row
            for row_id, row in frozen_by_id.items()
            if row["environment"] == environment
        }
        changed_clusters = {
            str(row["cluster_id"])
            for row in environment_rows.values()
            if row["row_kind"].startswith("changed_")
        }
        if len(environment_rows) != 60 or len(changed_clusters) != 20:
            raise ValueError(f"invalid frozen environment slice: {environment}")
        for model in DEPLOYMENT_MODELS:
            for controller in CONTROLLERS:
                joined = [
                    (task, observed[(environment, model, controller, row_id)])
                    for row_id, task in sorted(environment_rows.items())
                ]

                def e2e(task: dict[str, Any], result: dict[str, Any]) -> bool:
                    return (
                        result["execution_status"] == "success"
                        and str(result["mutated_target_id"])
                        == str(task["post_refresh_target"])
                        and int(result["collateral_change_count"]) == 0
                    )

                for task, result in joined:
                    correct_target = str(task["post_refresh_target"])
                    mutated_target = result["mutated_target_id"]
                    if result["execution_status"] == "success" and str(
                        mutated_target
                    ) != correct_target:
                        raise ValueError("success status disagrees with frozen target")
                    if result["execution_status"] == "wrong_entity_write" and (
                        mutated_target is None or str(mutated_target) == correct_target
                    ):
                        raise ValueError("wrong-write status disagrees with frozen target")

                correct = {
                    task["row_id"]: e2e(task, result) for task, result in joined
                }
                pair_correct = 0
                for cluster_id in changed_clusters:
                    pair_rows = [
                        task
                        for task in environment_rows.values()
                        if task["cluster_id"] == cluster_id
                        and task["row_kind"].startswith("changed_")
                    ]
                    if len(pair_rows) != 2:
                        raise ValueError(f"changed pair is incomplete: {cluster_id}")
                    pair_correct += all(correct[task["row_id"]] for task in pair_rows)
                preserve_opportunities = [
                    (task, result)
                    for task, result in joined
                    if task["row_kind"] == "changed_preserve"
                    and str(result["initial_selection_id"])
                    == str(task["pre_refresh_target"])
                    and result["refresh_completed"] is True
                ]
                substitutions = sum(
                    str(result["mutated_target_id"])
                    == str(task["post_refresh_target"])
                    for task, result in preserve_opportunities
                )
                wrong_writes = sum(
                    result["mutated_target_id"] is not None
                    and str(result["mutated_target_id"])
                    != str(task["post_refresh_target"])
                    for task, result in joined
                )
                summaries.append(
                    {
                        "environment": environment,
                        "model": model,
                        "controller": controller,
                        "rows": 60,
                        "e2e_numerator": sum(correct.values()),
                        "e2e": sum(correct.values()) / 60,
                        "pairacc_numerator": pair_correct,
                        "pairacc_denominator": 20,
                        "pairacc": pair_correct / 20,
                        "conditional_substitution_numerator": substitutions,
                        "conditional_substitution_denominator": len(
                            preserve_opportunities
                        ),
                        "conditional_substitution": (
                            substitutions / len(preserve_opportunities)
                            if preserve_opportunities
                            else None
                        ),
                        "wrong_writes": wrong_writes,
                        "wrong_write_rate": wrong_writes / 60,
                        "invalid_attempts": sum(
                            result["execution_status"] == "invalid_attempt"
                            for _, result in joined
                        ),
                        "rejections": sum(
                            result["execution_status"] == "rejection"
                            for _, result in joined
                        ),
                        "api_or_parse_failures": sum(
                            result["execution_status"]
                            in {"api_failure", "parse_failure"}
                            for _, result in joined
                        ),
                        "collateral_changes": sum(
                            int(result["collateral_change_count"])
                            for _, result in joined
                        ),
                        "calls": sum(int(result["call_count"]) for _, result in joined),
                        "input_tokens": sum(
                            int(result["input_tokens"]) for _, result in joined
                        ),
                        "output_tokens": sum(
                            int(result["output_tokens"]) for _, result in joined
                        ),
                        "latency_ms": sum(
                            float(result["latency_ms"]) for _, result in joined
                        ),
                    }
                )
    return summaries


def summarize_rule_star(
    frozen_rows: list[dict[str, Any]], results: list[dict[str, Any]]
) -> dict[str, Any]:
    """Score the unchanged Rule* as a post-hoc baseline outside controller selection."""
    frozen_by_id = {str(row.get("row_id")): row for row in frozen_rows}
    if len(frozen_by_id) != 120:
        raise ValueError("Rule* summary requires the frozen 120-row inventory")
    by_id: dict[str, dict[str, Any]] = {}
    source_hashes: set[str] = set()
    required = {
        "row_id",
        "rule_source_sha256",
        "execution_status",
        "predicted_target_id",
        "mutated_target_id",
        "final_state_diff",
        "collateral_change_count",
    }
    for result in results:
        assert_anonymous_payload(result)
        if not required.issubset(result):
            raise ValueError("Rule* result is missing required fields")
        row_id = str(result["row_id"])
        if row_id in by_id:
            raise ValueError(f"duplicate Rule* result: {row_id}")
        if result["execution_status"] not in EXECUTION_STATUSES:
            raise ValueError(f"unknown Rule* execution status: {result['execution_status']}")
        if not isinstance(result["final_state_diff"], list):
            raise ValueError("Rule* final_state_diff must be a list")
        if not isinstance(result["collateral_change_count"], int) or isinstance(
            result["collateral_change_count"], bool
        ) or result["collateral_change_count"] < 0:
            raise ValueError("Rule* collateral_change_count must be non-negative")
        source_hashes.add(str(result["rule_source_sha256"]))
        by_id[row_id] = result
    if set(by_id) != set(frozen_by_id):
        raise ValueError("Rule* results do not exactly cover the frozen inventory")
    if len(source_hashes) != 1 or len(next(iter(source_hashes), "")) != 64:
        raise ValueError("Rule* results require one frozen source hash")
    datasets = {}
    for environment in ENVIRONMENTS:
        tasks = [row for row in frozen_rows if row["environment"] == environment]
        correct = {
            task["row_id"]: (
                by_id[task["row_id"]]["execution_status"] == "success"
                and str(by_id[task["row_id"]]["mutated_target_id"])
                == str(task["post_refresh_target"])
                and by_id[task["row_id"]]["collateral_change_count"] == 0
            )
            for task in tasks
        }
        changed_clusters = {
            task["cluster_id"]
            for task in tasks
            if task["row_kind"].startswith("changed_")
        }
        pair_correct = sum(
            all(
                correct[task["row_id"]]
                for task in tasks
                if task["cluster_id"] == cluster_id
                and task["row_kind"].startswith("changed_")
            )
            for cluster_id in changed_clusters
        )
        wrong_writes = sum(
            by_id[task["row_id"]]["mutated_target_id"] is not None
            and str(by_id[task["row_id"]]["mutated_target_id"])
            != str(task["post_refresh_target"])
            for task in tasks
        )
        datasets[environment] = {
            "rows": 60,
            "e2e_numerator": sum(correct.values()),
            "e2e": sum(correct.values()) / 60,
            "pairacc_numerator": pair_correct,
            "pairacc_denominator": 20,
            "pairacc": pair_correct / 20,
            "wrong_writes": wrong_writes,
            "wrong_write_rate": wrong_writes / 60,
        }
    return {
        "evidence_role": "formal post-hoc baseline; excluded from frozen controller selection",
        "rule_source_sha256": next(iter(source_hashes)),
        "datasets": datasets,
    }


def build_writer_forms(rows: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    """Write redacted writer cards; S1, gold, alternate members, and annotations are omitted."""
    validate_candidate_rows(rows)
    by_writer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_writer[str(row["writer_id"])].append(row)
    if set(by_writer) - set(WRITERS):
        raise ValueError("unknown writer in candidate inventory")
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest = {"run_version": RUN_VERSION, "evidence_status": EVIDENCE_STATUS, "forms": {}}
    for writer_id in sorted(by_writer):
        assigned = list(by_writer[writer_id])
        random.Random(20260729 + int(writer_id[1:])).shuffle(assigned)
        lines = [
            f"# Unified environment writing form {writer_id}",
            "",
            "Write one natural English request per card. Do not use external tools, search, AI, or another person.",
            "Only the current records and the required operation order are shown.",
            "",
        ]
        for index, row in enumerate(assigned, 1):
            lines.extend([
                f"## Card {index:02d} [{row['item_id']}]",
                f"Environment: {row['environment']}",
                f"Available action: {row['action']}",
                f"Selection criterion: {row['selector']}",
                "Current records:",
                "```json",
                json.dumps(row["s0_state"], ensure_ascii=True, sort_keys=True),
                "```",
                "Required order: " + (
                    "select one object before refresh, then act on that same object"
                    if row["reference_mode"] == "preserve"
                    else "refresh first, then select one object and act on it"
                ) + ".",
                "Your English request:",
                "",
                "____________________________________________________________",
                "",
            ])
        path = output_dir / f"writer_{writer_id}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        manifest["forms"][writer_id] = sha256_bytes(path.read_bytes())
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return manifest


def build_annotator_form(rows: list[dict[str, Any]], annotator: str, output: Path) -> dict[str, Any]:
    """Write a blind refreshed-state labeling form after writer strings are locked."""
    if annotator not in ANNOTATORS:
        raise ValueError(f"unknown annotator: {annotator}")
    ordered = list(rows)
    random.Random(20260801 + int(annotator[1:])).shuffle(ordered)
    lines = [f"# Blind target annotation form {annotator}", "", "Choose one target ID or CLARIFY. Do not infer pair membership or gold.", ""]
    for index, row in enumerate(ordered, 1):
        lines.extend([
            f"## Item {index:03d}",
            "Instruction:",
            row["instruction"],
            "Refreshed records:",
            "```json",
                json.dumps(row.get("s1_state") or row["s1_changed_state"], ensure_ascii=True, sort_keys=True),
            "```",
            "Target ID or CLARIFY:",
            "",
        ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return {"annotator": annotator, "items": len(rows), "sha256": sha256_bytes(output.read_bytes())}
