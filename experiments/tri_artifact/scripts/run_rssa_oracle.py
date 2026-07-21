from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tri.event_graph_controller import compile_oracle_selector
from tri.reference_lifecycle import INVALID
from tri.referential_ssa import (
    compile_oracle_rssa,
    compiler_payload,
    execute_rssa_enforced,
    execute_rssa_free,
    ground_with_selector,
    issue_rssa_handles,
    rssa_program_to_dict,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/temporal_referent_method_upgrade_smoke_v1.jsonl"
PROTOCOL = ROOT / "reports/TRI_rssa_20task_protocol.md"
EXPECTED_MANIFEST_SHA256 = "e651f4db45275877ca09a5e70187baca6d5ee8901bf983bb1ecc3885ef879181"
FORBIDDEN = {
    "binding", "correct_target", "pre_refresh_target", "post_refresh_target",
    "new_leader", "selector", "phenomenon", "style", "template_id", "update",
    "bound_entity_present_after_refresh", "bound_entity_actionable_after_refresh",
    "distractor_referent", "smoke_source", "source_task_id",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def evaluate() -> dict[str, Any]:
    manifest_sha256 = _sha256(MANIFEST)
    if manifest_sha256 != EXPECTED_MANIFEST_SHA256:
        raise ValueError(f"manifest hash changed: {manifest_sha256}")
    tasks = _load(MANIFEST)
    if len(tasks) != 20 or len({task["id"] for task in tasks}) != 20:
        raise ValueError("frozen smoke must contain 20 unique tasks")

    counts: Counter[str] = Counter()
    binding_epochs: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    rows: list[dict[str, Any]] = []
    substitution_cases: list[dict[str, Any]] = []

    for task in tasks:
        payload = compiler_payload(task)
        leaked = sorted(set(payload) & FORBIDDEN)
        counts["payloads_without_forbidden_fields"] += not leaked
        program = compile_oracle_rssa(task)
        selector = compile_oracle_selector(task)
        grounded = ground_with_selector(task, program, selector)
        handles = issue_rssa_handles(task, program, grounded)
        enforced = execute_rssa_enforced(task, program, handles)

        counts["valid_programs"] += 1
        counts["enforced_authorized_target_correct"] += enforced == task["correct_target"]
        counts["composition_role_inventory_correct"] += (
            "final_state" not in task
            or {binding.role for binding in program.bindings}
            == {"action_target", "monitoring_reference"}
        )
        for binding in program.bindings:
            role_counts[binding.role] += 1
            binding_epochs[binding.epoch] += 1
            expected = selector and grounded[binding.name]
            counts["grounded_bindings"] += expected != INVALID

        if (
            task["binding"] == "anchored"
            and task["correct_target"] != INVALID
            and task["post_refresh_target"] != task["pre_refresh_target"]
        ):
            free = execute_rssa_free(task, task["post_refresh_target"])
            substitution_cases.append({
                "task_id": task["id"],
                "actor_proposal": task["post_refresh_target"],
                "free_target": free,
                "enforced_target": enforced,
                "correct_target": task["correct_target"],
                "free_wrong_write": free != task["correct_target"] and free != INVALID,
                "enforced_correct": enforced == task["correct_target"],
            })

        rows.append({
            "task_id": task["id"],
            "smoke_index": task["smoke_index"],
            "program": rssa_program_to_dict(program),
            "grounded_targets": grounded,
            "enforced_target": enforced,
            "correct": enforced == task["correct_target"],
            "compiler_payload_keys": sorted(payload),
            "forbidden_payload_fields": leaked,
        })

    return {
        "kind": "rssa_zero_api_oracle_and_leakage_audit",
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "manifest_sha256": manifest_sha256,
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": _sha256(PROTOCOL),
        "tasks": len(tasks),
        "task_composition": {"scalar": 16, "multi_refresh_role": 4},
        "coverage": dict(sorted(counts.items())),
        "binding_roles": dict(sorted(role_counts.items())),
        "binding_epochs": dict(sorted(binding_epochs.items())),
        "adversarial_shadow_substitution": {
            "eligible_cases": len(substitution_cases),
            "free_wrong_writes": sum(row["free_wrong_write"] for row in substitution_cases),
            "enforced_correct": sum(row["enforced_correct"] for row in substitution_cases),
            "rows": substitution_cases,
        },
        "rows": rows,
        "interpretation": (
            "Implementation and oracle coverage only; this does not measure learned compiler, "
            "grounder, or actor performance."
        ),
    }


def markdown(report: dict[str, Any]) -> str:
    coverage = report["coverage"]
    substitution = report["adversarial_shadow_substitution"]
    total = report["tasks"]
    return "\n".join([
        "# R-SSA Zero-API Oracle and Leakage Audit",
        "",
        f"- Manifest: `{report['manifest']}`",
        f"- Manifest SHA-256: `{report['manifest_sha256']}`",
        f"- Protocol SHA-256: `{report['protocol_sha256']}`",
        f"- Frozen tasks: {total} (16 scalar; 4 multi-refresh/role)",
        "",
        "## Coverage",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Valid oracle programs | {coverage['valid_programs']}/{total} |",
        f"| Enforced authorized target | {coverage['enforced_authorized_target_correct']}/{total} |",
        f"| Correct composition role inventory | {coverage['composition_role_inventory_correct']}/{total} |",
        f"| Compiler payloads without forbidden fields | {coverage['payloads_without_forbidden_fields']}/{total} |",
        f"| Grounded binding instances | {coverage['grounded_bindings']}/24 |",
        "",
        f"Binding roles: `{json.dumps(report['binding_roles'], sort_keys=True)}`",
        "",
        f"Binding epochs: `{json.dumps(report['binding_epochs'], sort_keys=True)}`",
        "",
        "## Adversarial shadow substitution",
        "",
        "For eligible anchored flip cases, the shadow actor is deliberately set to the refreshed",
        "winner while Free and Enforced share the same oracle program and handles.",
        "",
        f"- Eligible cases: {substitution['eligible_cases']}",
        f"- Free wrong writes: {substitution['free_wrong_writes']}",
        f"- Enforced correct writes: {substitution['enforced_correct']}",
        "",
        "This establishes the implementation-level intervention only. It is not learned-model",
        "evidence and cannot be reported as R-SSA empirical performance.",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output", type=Path, default=ROOT / "reports/rssa_oracle_v1.json"
    )
    parser.add_argument(
        "--md-output", type=Path, default=ROOT / "reports/rssa_oracle_v1.md"
    )
    args = parser.parse_args()
    report = evaluate()
    args.json_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.md_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({
        "json": str(args.json_output), "markdown": str(args.md_output),
        "tasks": report["tasks"], "coverage": report["coverage"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
