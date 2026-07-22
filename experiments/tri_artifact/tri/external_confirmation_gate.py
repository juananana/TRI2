from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MIN_APPS = 4
MIN_CLUSTERS = 20
MIN_ROWS = 80


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_gate_report(artifact_root: Path) -> dict[str, Any]:
    data_paths = [
        artifact_root / "data" / "appworld_tri_todoist_mvp_v1.jsonl",
        artifact_root / "data" / "appworld_tri_simple_note_mvp_v1.jsonl",
    ]
    rows = [row for path in data_paths for row in _load_jsonl(path)]
    natural_report = json.loads(
        (artifact_root / "reports" / "appworld_naturalistic_v1.json").read_text(
            encoding="utf-8"
        )
    )

    apps = sorted({row["cluster_id"].split("-")[0] for row in rows})
    clusters = sorted({row["cluster_id"] for row in rows})
    cells = {
        (row["cluster_id"], row["reference_mode"], row["transition"])
        for row in rows
    }
    matched_clusters = sum(
        all(
            (cluster, mode, transition) in cells
            for mode in ("preserve", "reevaluate")
            for transition in ("stable", "flip")
        )
        for cluster in clusters
    )
    independent_writer_fields = {
        row.get("writer_id") or row.get("independent_writer_id") for row in rows
    } - {None, ""}
    independent_writers_verified = bool(independent_writer_fields)

    combined = natural_report["combined"]
    checks = {
        "at_least_four_apps": len(apps) >= MIN_APPS,
        "at_least_twenty_clusters": len(clusters) >= MIN_CLUSTERS,
        "at_least_eighty_inventory_rows": len(rows) >= MIN_ROWS,
        "independent_writers_verified": independent_writers_verified,
        "all_clusters_have_matched_2x2": matched_clusters == len(clusters),
        "existing_ordinary_loop_has_observable_bindings": combined[
            "binding_opportunities"
        ] > 0,
    }
    blocking_checks = (
        "at_least_four_apps",
        "at_least_twenty_clusters",
        "at_least_eighty_inventory_rows",
        "independent_writers_verified",
        "all_clusters_have_matched_2x2",
    )
    decision = "GO" if all(checks[name] for name in blocking_checks) else "NO-GO"
    return {
        "study": "TRI low-intervention external confirmation v2 inventory gate",
        "status": "planned/unverified; zero-API gate",
        "decision": decision,
        "requirements": {
            "min_apps": MIN_APPS,
            "min_clusters": MIN_CLUSTERS,
            "min_inventory_rows": MIN_ROWS,
            "independent_writers_required": True,
        },
        "available_inventory": {
            "apps": apps,
            "app_count": len(apps),
            "clusters": clusters,
            "cluster_count": len(clusters),
            "inventory_rows": len(rows),
            "matched_2x2_clusters": matched_clusters,
            "independent_writers_verified": independent_writers_verified,
        },
        "completed_low_intervention_evidence": {
            "trajectories": combined["rows"],
            "binding_opportunities": combined["binding_opportunities"],
            "conditional_tri_errors": combined["conditional_tri_errors"],
            "preserve_flip_opportunities": combined["preserve_flip_opportunities"],
            "preserve_flip_tri_errors": combined["preserve_flip_tri_errors"],
            "wrong_writes_without_correct_binding": combined[
                "wrong_writes_without_correct_binding"
            ],
        },
        "checks": checks,
        "interpretation": (
            "The existing ordinary full-history AppWorld study is a completed two-cluster null. "
            "It does not satisfy the prospective domain, cluster, or independent-writer gate. "
            "No new API run is authorized; author-written expansion would not exclude the "
            "template-construction alternative explanation."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    available = report["available_inventory"]
    evidence = report["completed_low_intervention_evidence"]
    lines = [
        "# Low-Intervention External Confirmation v2 Gate",
        "",
        f"**Decision: {report['decision']}**",
        "",
        "This is a zero-API feasibility gate, not empirical confirmation.",
        "",
        "## Inventory Check",
        "",
        "| Requirement | Available | Pass |",
        "|---|---:|---:|",
        f"| Applications >= 4 | {available['app_count']} | "
        f"{report['checks']['at_least_four_apps']} |",
        f"| Workflow clusters >= 20 | {available['cluster_count']} | "
        f"{report['checks']['at_least_twenty_clusters']} |",
        f"| Inventory rows >= 80 | {available['inventory_rows']} | "
        f"{report['checks']['at_least_eighty_inventory_rows']} |",
        f"| Independent writers verified | {available['independent_writers_verified']} | "
        f"{report['checks']['independent_writers_verified']} |",
        f"| Every cluster has matched 2x2 | {available['matched_2x2_clusters']}/"
        f"{available['cluster_count']} | {report['checks']['all_clusters_have_matched_2x2']} |",
        "",
        "## Existing Completed Evidence",
        "",
        f"The completed AppWorld ordinary-agent study has {evidence['trajectories']} trajectories, "
        f"{evidence['binding_opportunities']} auditable bindings, and "
        f"{evidence['conditional_tri_errors']} conditional TRI errors. Preserve/Flip is "
        f"{evidence['preserve_flip_tri_errors']}/{evidence['preserve_flip_opportunities']}. "
        f"The {evidence['wrong_writes_without_correct_binding']} wrong writes occur without a "
        "correct, timely initial binding and are not TRI.",
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
    ]
    return "\n".join(lines)
