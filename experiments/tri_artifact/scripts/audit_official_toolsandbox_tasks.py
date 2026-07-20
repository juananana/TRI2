#!/usr/bin/env python3
"""Audit unmodified ToolSandbox scenarios for native TRI opportunities.

This script inventories semantic scenario families, not augmented tool-presentation
variants. It intentionally separates strict TRI eligibility from broader traces that
exercise post-binding reference persistence without an exogenous selector flip.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ENTITY_DATABASES = {"CONTACT", "MESSAGING", "REMINDER"}
ENTITY_ID_FIELDS = {"person_id", "message_id", "reminder_id"}
MUTATION_SIMILARITIES = {
    "addition_similarity",
    "removal_similarity",
    "update_similarity",
}

# This is a frozen, human-reviewed exception to the structural rules below. The
# official task has a natural post-binding pronoun and two state mutations, but
# the intervening transition is the first user-requested action, not an external
# refresh, and no competing selector winner is introduced.
REVIEWED_TRI_LIKE = {
    "update_contact_relationship_with_relationship_twice_multiple_user_turn": {
        "classification": "tri_like_post_binding_preservation",
        "strict_tri_eligible": False,
        "tri_like_eligible": True,
        "review_note": (
            "The agent searches for all friends, changes those stable person IDs to "
            "enemies, and later resolves 'them' to change the same IDs back to friends. "
            "This is post-binding reference persistence across an action-induced state "
            "change, but it has no exogenous refresh, competing entity, or selector flip."
        ),
    }
}


def _enum_name(value: Any) -> str:
    return getattr(value, "name", str(value))


def _extract_json_tool_names(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    traces = parsed if isinstance(parsed, list) else [parsed]
    return sorted(
        {
            trace["tool_name"]
            for trace in traces
            if isinstance(trace, dict) and isinstance(trace.get("tool_name"), str)
        }
    )


def _has_ordered_path(edges: Iterable[tuple[int, int]], start: int, end: int) -> bool:
    if start == end:
        return False
    adjacency: dict[int, set[int]] = {}
    for source, target in edges:
        adjacency.setdefault(source, set()).add(target)
    frontier = list(adjacency.get(start, ()))
    visited: set[int] = set()
    while frontier:
        node = frontier.pop()
        if node == end:
            return True
        if node in visited:
            continue
        visited.add(node)
        frontier.extend(adjacency.get(node, ()))
    return False


def classify_record(record: dict[str, Any]) -> dict[str, Any]:
    """Apply frozen inclusion rules to one extracted scenario record."""
    selection_nodes = record["entity_selection_milestone_indices"]
    mutation_nodes = record["entity_mutation_milestone_indices"]
    edges = [tuple(edge) for edge in record["milestone_edges"]]
    ordered_selection_to_mutation = any(
        _has_ordered_path(edges, selection, mutation) or selection < mutation
        for selection in selection_nodes
        for mutation in mutation_nodes
    )
    ordered_mutation_pair = any(
        _has_ordered_path(edges, first, second) or first < second
        for first in mutation_nodes
        for second in mutation_nodes
        if first != second
    )

    signals = {
        "has_entity_selection_before_mutation": ordered_selection_to_mutation,
        "has_stable_entity_id_in_mutation_gold": bool(record["mutation_entity_id_fields"]),
        "has_two_ordered_entity_mutations": ordered_mutation_pair,
        "has_external_or_user_side_transition": False,
        "has_competing_selector_winner": False,
    }
    reviewed = REVIEWED_TRI_LIKE.get(record["scenario_name"])
    if reviewed is not None:
        classification = reviewed["classification"]
        strict = reviewed["strict_tri_eligible"]
        tri_like = reviewed["tri_like_eligible"]
        note = reviewed["review_note"]
    elif not mutation_nodes:
        classification = "excluded_no_entity_mutation"
        strict = tri_like = False
        note = "No evaluator milestone mutates a contact, message, or reminder entity."
    elif not ordered_selection_to_mutation:
        classification = "excluded_no_prior_entity_selection"
        strict = tri_like = False
        note = "No ordered search/read milestone establishes an entity before mutation."
    elif not record["mutation_entity_id_fields"]:
        classification = "excluded_no_stable_mutation_id"
        strict = tri_like = False
        note = "The mutation evaluator does not expose a stable entity ID."
    elif not ordered_mutation_pair:
        classification = "excluded_no_intervening_transition"
        strict = tri_like = False
        note = "The task binds and mutates an entity but has no state transition before a later mutation."
    else:
        classification = "manual_review_required"
        strict = tri_like = False
        note = "Structural signals require human review; the scenario is not counted automatically."

    return {
        **record,
        **signals,
        "classification": classification,
        "strict_tri_eligible": strict,
        "tri_like_eligible": tri_like,
        "classification_note": note,
    }


def _task_from_user_prompt(prompt: str) -> str:
    marker = "following task you (User A) want User B to complete:"
    if marker in prompt:
        return prompt.split(marker, 1)[1].strip()
    return prompt.strip()


def extract_record(source_group: str, name: str, scenario: Any) -> dict[str, Any]:
    from tool_sandbox.common.execution_context import DatabaseNamespace, RoleType

    sandbox = scenario.starting_context.get_database(
        DatabaseNamespace.SANDBOX,
        drop_sandbox_message_index=False,
        get_all_history_snapshots=True,
    )
    user_prompts = [
        row["content"]
        for row in sandbox.iter_rows(named=True)
        if row["sender"] == RoleType.SYSTEM
        and row["recipient"] == RoleType.USER
        and row["content"]
    ]
    initial_user_messages = [
        row["content"]
        for row in sandbox.iter_rows(named=True)
        if row["sender"] == RoleType.USER
        and row["recipient"] == RoleType.AGENT
        and row["content"]
    ]

    milestones = scenario.evaluation.milestone_matcher.milestones
    read_nodes: list[int] = []
    mutation_nodes: list[int] = []
    mutation_id_fields: set[str] = set()
    milestone_summaries: list[dict[str, Any]] = []
    for index, milestone in enumerate(milestones):
        tool_names: set[str] = set()
        mutations: list[dict[str, Any]] = []
        for constraint in milestone.snapshot_constraints:
            namespace = _enum_name(constraint.database_namespace)
            similarity = getattr(
                constraint.snapshot_constraint,
                "__name__",
                str(constraint.snapshot_constraint),
            )
            rows = (
                []
                if constraint.target_dataframe is None
                else constraint.target_dataframe.to_dicts()
            )
            for row in rows:
                tool_names.update(_extract_json_tool_names(row.get("tool_trace")))
            if namespace in ENTITY_DATABASES and similarity in MUTATION_SIMILARITIES:
                fields = sorted(
                    {field for row in rows for field in row if field in ENTITY_ID_FIELDS}
                )
                mutation_id_fields.update(fields)
                mutations.append(
                    {
                        "database": namespace,
                        "similarity": similarity,
                        "entity_id_fields": fields,
                        "target_row_count": len(rows),
                    }
                )
        if any(tool.startswith(("search_", "get_", "find_")) for tool in tool_names):
            read_nodes.append(index)
        if mutations:
            mutation_nodes.append(index)
        milestone_summaries.append(
            {
                "index": index,
                "tool_names": sorted(tool_names),
                "entity_mutations": mutations,
            }
        )

    edges = scenario.evaluation.milestone_matcher.edge_list
    if edges is None:
        edges = [(index, index + 1) for index in range(max(0, len(milestones) - 1))]
    record = {
        "scenario_name": name,
        "source_group": source_group,
        "official_user_task": _task_from_user_prompt(user_prompts[-1]) if user_prompts else "",
        "initial_user_message": initial_user_messages[-1] if initial_user_messages else "",
        "tool_allow_list": sorted(scenario.starting_context.tool_allow_list or []),
        "categories": sorted(_enum_name(category) for category in scenario.categories),
        "milestone_count": len(milestones),
        "milestone_edges": [list(edge) for edge in edges],
        "entity_selection_milestone_indices": read_nodes,
        "entity_mutation_milestone_indices": mutation_nodes,
        "mutation_entity_id_fields": sorted(mutation_id_fields),
        "milestones": milestone_summaries,
    }
    return classify_record(record)


def load_official_inventory() -> tuple[list[dict[str, Any]], int]:
    from tool_sandbox.common.tool_discovery import ToolBackend
    from tool_sandbox.scenarios import named_scenarios
    from tool_sandbox.scenarios.insufficient_information_scenarios import (
        named_insufficient_information_scenarios,
    )
    from tool_sandbox.scenarios.multiple_tool_call_scenarios import (
        named_multiple_tool_call_scenarios,
    )
    from tool_sandbox.scenarios.multiple_user_turn_scenarios import (
        named_multiple_user_turn_scenarios,
    )
    from tool_sandbox.scenarios.single_tool_call_scenarios import (
        named_single_tool_call_scenarios,
    )

    factories = [
        ("single_tool_call", named_single_tool_call_scenarios),
        ("multiple_tool_call", named_multiple_tool_call_scenarios),
        ("multiple_user_turn", named_multiple_user_turn_scenarios),
        ("insufficient_information", named_insufficient_information_scenarios),
    ]
    records = [
        extract_record(group, name, scenario)
        for group, factory in factories
        for name, scenario in factory(ToolBackend.DEFAULT).items()
    ]
    # Seed-independent count; augmentation changes only tool presentation/order.
    augmented_instance_count = len(named_scenarios(ToolBackend.DEFAULT))
    return records, augmented_instance_count


def _upstream_metadata() -> dict[str, str]:
    import importlib.metadata

    distribution = importlib.metadata.distribution("tool-sandbox")
    direct_url_path = Path(distribution.locate_file("tool_sandbox-0.0.1.dist-info/direct_url.json"))
    metadata = json.loads(direct_url_path.read_text(encoding="utf-8"))
    vcs = metadata.get("vcs_info", {})
    return {
        "package_version": distribution.version,
        "upstream_url": metadata.get("url", "unknown"),
        "commit_id": vcs.get("commit_id", "unknown"),
    }


def build_payload(records: list[dict[str, Any]], augmented_count: int) -> dict[str, Any]:
    classifications = Counter(record["classification"] for record in records)
    groups = Counter(record["source_group"] for record in records)
    return {
        "audit_scope": "unmodified official ToolSandbox semantic scenario families",
        "upstream": _upstream_metadata(),
        "semantic_scenario_family_count": len(records),
        "official_augmented_instance_count": augmented_count,
        "strict_tri_eligible_count": sum(record["strict_tri_eligible"] for record in records),
        "tri_like_eligible_count": sum(record["tri_like_eligible"] for record in records),
        "source_group_counts": dict(sorted(groups.items())),
        "classification_counts": dict(sorted(classifications.items())),
        "interpretation": (
            "Tool presentation augmentations are not independent semantic tasks. Strict eligibility "
            "requires an independent post-binding transition and a later entity mutation with an "
            "observable wrong-target alternative."
        ),
        "scenarios": records,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    upstream = payload["upstream"]
    classifications = payload["classification_counts"]
    candidates = [
        record
        for record in payload["scenarios"]
        if record["tri_like_eligible"] or record["strict_tri_eligible"]
    ]
    lines = [
        "# Official ToolSandbox TRI Prevalence Audit",
        "",
        "## Scope and Frozen Definition",
        "",
        f"- Upstream: `{upstream['upstream_url']}`",
        f"- Pinned commit: `{upstream['commit_id']}`",
        f"- Package version: `{upstream['package_version']}`",
        f"- Semantic scenario families audited: **{payload['semantic_scenario_family_count']}**",
        f"- Official tool-presentation instances: **{payload['official_augmented_instance_count']}**",
        "",
        "The denominator is the semantic scenario family count. Distraction tools and scrambled tool",
        "metadata do not create new referential semantics and therefore are not treated as independent",
        "prevalence observations.",
        "",
        "A strict native TRI opportunity must contain: (1) an entity selection/binding, (2) an",
        "independent later world or user-side state transition, (3) a subsequent mutation whose",
        "referent can either be preserved or reevaluated, (4) stable IDs, and (5) an evaluator that",
        "can expose a wrong-target consequence. A merely stateful task or initial disambiguation task",
        "does not qualify.",
        "",
        "## Result",
        "",
        f"- Strict native TRI opportunities: **{payload['strict_tri_eligible_count']}/{payload['semantic_scenario_family_count']}**",
        f"- Broader TRI-like natural traces: **{payload['tri_like_eligible_count']}/{payload['semantic_scenario_family_count']}**",
        "",
        "The unmodified official suite contains no strict exogenous-refresh/selector-flip TRI task.",
        "Consequently, an unmodified ToolSandbox leaderboard run cannot estimate TRI failure",
        "prevalence. This is a coverage result, not evidence that TRI never occurs in deployed agents.",
        "",
        "One official scenario is a genuine natural-language near match:",
        "",
    ]
    for candidate in candidates:
        lines.extend(
            [
                f"- `{candidate['scenario_name']}`: {candidate['classification_note']}",
                f"  Official task: {candidate['official_user_task']}",
            ]
        )
    lines.extend(
        [
            "",
            "It supports the discourse-side premise that an established group reference can survive",
            "a selector-relevant state change. It cannot test unauthorized substitution because no",
            "competing friend is introduced, and it provides neither Stable/Flip nor",
            "Preserve/Reevaluate controls.",
            "",
            "## Exclusion Accounting",
            "",
            "| Classification | Scenario families |",
            "|---|---:|",
        ]
    )
    for classification, count in sorted(classifications.items()):
        lines.append(f"| `{classification}` | {count} |")
    lines.extend(
        [
            "",
            "## Scientific Interpretation",
            "",
            "1. The official audit does not validate a positive model failure rate because the suite",
            "   has zero strict opportunities.",
            "2. The official near-match independently demonstrates that post-binding reference",
            "   persistence is a natural task pattern rather than a phrase invented only for TRI.",
            "3. The project's 96-task ToolSandbox adaptation must remain labeled a custom adaptation.",
            "   Its null full-history result is a model/controller boundary, not an official score.",
            "4. A small AppWorld adaptation is justified only as a preregistered custom case study with",
            "   frozen transitions and database-diff evaluation; it cannot be called an unmodified",
            "   AppWorld benchmark result.",
            "",
            "The complete per-scenario evidence, tools, milestones, ID fields, and exclusion reasons",
            "are stored in `official_toolsandbox_tri_prevalence_audit.json`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    default_reports = Path(__file__).resolve().parents[1] / "reports"
    parser.add_argument(
        "--json-output",
        type=Path,
        default=default_reports / "official_toolsandbox_tri_prevalence_audit.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=default_reports / "official_toolsandbox_tri_prevalence_audit.md",
    )
    args = parser.parse_args()

    records, augmented_count = load_official_inventory()
    payload = build_payload(records, augmented_count)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(args.json_output)
    print(args.markdown_output)


if __name__ == "__main__":
    main()
