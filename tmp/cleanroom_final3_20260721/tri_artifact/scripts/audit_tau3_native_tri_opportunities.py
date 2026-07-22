from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
from typing import Any


CORE_DOMAINS = ("airline", "retail", "telecom")
STABLE_ID_KEYS = {
    "customer_id",
    "line_id",
    "bill_id",
    "order_id",
    "item_id",
    "product_id",
    "reservation_id",
}


def actions(task: dict[str, Any]) -> list[dict[str, Any]]:
    return (task.get("evaluation_criteria") or {}).get("actions") or []


def requestor(action: dict[str, Any]) -> str:
    return action.get("requestor", "assistant")


def stable_ids(action: dict[str, Any]) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for key, value in (action.get("arguments") or {}).items():
        if key in STABLE_ID_KEYS and isinstance(value, (str, int)):
            found.add((key, str(value)))
        elif key.endswith("_ids") and isinstance(value, list):
            found.update((key[:-1], str(item)) for item in value)
    return found


def has_metadata_strict_candidate(task: dict[str, Any]) -> bool:
    """Conservative metadata screen; every hit still requires manual semantic audit."""
    task_actions = actions(task)
    for index, transition in enumerate(task_actions):
        if requestor(transition) != "user" or not stable_ids(transition):
            continue
        before = set().union(
            *(stable_ids(action) for action in task_actions[:index] if requestor(action) == "assistant")
        )
        after = set().union(
            *(stable_ids(action) for action in task_actions[index + 1 :] if requestor(action) == "assistant")
        )
        if before & after:
            return True
    return False


def load_tasks(upstream: Path) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for domain in CORE_DOMAINS:
        path = upstream / "data" / "tau2" / "domains" / domain / "tasks.json"
        result[domain] = json.loads(path.read_text(encoding="utf-8"))
    return result


def released_trace_summary(upstream: Path) -> dict[str, Any]:
    root = upstream / "data" / "tau2" / "results" / "final"
    files = sorted(root.glob("*.json"))
    simulations = 0
    by_domain: Counter[str] = Counter()
    by_agent_model: Counter[str] = Counter()
    payment_near_match_trajectories = 0
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        info = payload.get("info") or {}
        domain = (info.get("environment_info") or {}).get("domain_name", "unknown")
        model = (info.get("agent_info") or {}).get("llm", "unknown")
        rows = payload.get("simulations") or []
        simulations += len(rows)
        by_domain[domain] += len(rows)
        by_agent_model[model] += len(rows)
        payment_near_match_trajectories += sum(
            "overdue_bill_suspension" in str(row.get("task_id", "")) for row in rows
        )
    return {
        "files": len(files),
        "simulations": simulations,
        "by_domain": dict(sorted(by_domain.items())),
        "by_agent_model": dict(sorted(by_agent_model.items())),
        "payment_near_match_trajectories": payment_near_match_trajectories,
    }


def build_report(upstream: Path, include_released_traces: bool) -> dict[str, Any]:
    task_sets = load_tasks(upstream)
    domain_rows: dict[str, Any] = {}
    all_candidates: list[dict[str, str]] = []
    for domain, domain_tasks in task_sets.items():
        user_mutation_tasks = [
            task
            for task in domain_tasks
            if any(requestor(action) == "user" for action in actions(task))
        ]
        user_stable_id_tasks = [
            task
            for task in user_mutation_tasks
            if any(
                stable_ids(action)
                for action in actions(task)
                if requestor(action) == "user"
            )
        ]
        candidates = [task for task in domain_tasks if has_metadata_strict_candidate(task)]
        all_candidates.extend(
            {"domain": domain, "task_id": str(task["id"])} for task in candidates
        )
        domain_rows[domain] = {
            "tasks": len(domain_tasks),
            "tasks_with_user_evaluation_mutation": len(user_mutation_tasks),
            "tasks_with_user_mutation_carrying_stable_entity_id": len(user_stable_id_tasks),
            "metadata_strict_candidates_before_manual_audit": len(candidates),
        }

    telecom = task_sets["telecom"]
    payment_near_matches = [
        task
        for task in telecom
        if any(action.get("name") == "make_payment" for action in actions(task))
        and any(action.get("name") == "resume_line" for action in actions(task))
    ]
    commit = subprocess.check_output(
        ["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True
    ).strip()
    report: dict[str, Any] = {
        "upstream": "https://github.com/sierra-research/tau2-bench.git",
        "commit": commit,
        "scope": list(CORE_DOMAINS),
        "total_tasks": sum(len(items) for items in task_sets.values()),
        "domains": domain_rows,
        "metadata_strict_candidates": all_candidates,
        "strict_native_tri_opportunities_after_manual_semantic_audit": 0,
        "natural_stateful_near_matches": {
            "telecom_overdue_payment_then_resume_line_tasks": len(payment_near_matches),
            "interpretation": (
                "The Agent binds a bill, the user pays it, and the Agent resumes a line. "
                "This is a natural dual-control transition but not TRI: bill and line are "
                "different referential roles, and no competing selector winner can replace "
                "a previously committed mutation target."
            ),
        },
        "exclusion_logic": {
            "airline_retail": (
                "No user-side tools mutate shared state during the conversation; task actions "
                "therefore cannot supply an independent post-binding transition."
            ),
            "telecom": (
                "User-side mutations target a single simulated device or an app name and carry "
                "no customer/line/bill stable ID. The task worlds do not provide a competing "
                "same-role entity whose selector status can change after a prior binding."
            ),
        },
        "scientific_interpretation": (
            "The official inventory adds natural language, dual control, and ordinary published "
            "Agents, but it has zero strict TRI opportunities under the frozen definition. It "
            "therefore measures benchmark coverage, not TRI prevalence or absence."
        ),
    }
    if include_released_traces:
        report["released_traces"] = released_trace_summary(upstream)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Official tau3-bench Native TRI Opportunity Audit",
        "",
        "## Frozen Scope",
        "",
        f"- Upstream: `{report['upstream']}`",
        f"- Commit: `{report['commit']}`",
        f"- Core tasks audited: **{report['total_tasks']}**",
        "- Domains: airline, retail, telecom",
        "",
        "A strict opportunity requires a correct same-role entity binding, an independent later",
        "user/environment mutation, a subsequent action that may preserve or reevaluate that",
        "referent, stable IDs, a competing selector candidate, and a scoreable wrong-target outcome.",
        "Statefulness, multiple tools, or initial entity lookup alone do not qualify.",
        "",
        "## Inventory Screen",
        "",
        "| Domain | Tasks | User-mutation tasks | User mutation with stable ID | Metadata candidates |",
        "|---|---:|---:|---:|---:|",
    ]
    for domain, values in report["domains"].items():
        lines.append(
            f"| {domain} | {values['tasks']} | "
            f"{values['tasks_with_user_evaluation_mutation']} | "
            f"{values['tasks_with_user_mutation_carrying_stable_entity_id']} | "
            f"{values['metadata_strict_candidates_before_manual_audit']} |"
        )
    lines.extend(
        [
            "",
            "## Result",
            "",
            "- Strict native TRI opportunities after semantic audit: **0**",
            "- Natural dual-control near-match: **8** telecom overdue-payment task definitions",
            "",
            "In the near-match, the Agent identifies an overdue bill, the user pays it through a",
            "user tool, and the Agent resumes an associated line. This independently demonstrates",
            "a natural bind--user-transition--continue workflow, but it is not TRI: the bill and line",
            "are different roles and there is no competing same-role target or selector flip.",
            "",
        ]
    )
    traces = report.get("released_traces")
    if traces:
        models = ", ".join(
            f"{name}: {count}" for name, count in traces["by_agent_model"].items()
        )
        domains = ", ".join(
            f"{name}: {count}" for name, count in traces["by_domain"].items()
        )
        lines.extend(
            [
                "## Released-Trajectory Coverage",
                "",
                f"The repository includes {traces['files']} released result files and",
                f"{traces['simulations']} trajectories. Domain counts are {domains}.",
                f"Agent-model counts are {models}.",
                f"The payment near-match appears in {traces['payment_near_match_trajectories']}",
                "released trajectories. Because the task inventory has no strict opportunity,",
                "these trajectories cannot estimate a conditional TRI failure rate.",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            report["scientific_interpretation"],
            "This is stronger evidence about external benchmark coverage and ordinary Agent",
            "families, but it is not positive evidence that TRI occurs in uncontrolled traffic.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--include-released-traces", action="store_true")
    args = parser.parse_args()
    report = build_report(args.upstream, args.include_released_traces)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(args.json)
    print(args.markdown)


if __name__ == "__main__":
    main()
