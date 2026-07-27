"""Static consistency checks for the submission manuscript."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_REPOSITORY = ROOT.parents[1]
if (DEVELOPMENT_REPOSITORY / "paper/AnonymousSubmission2027.tex").is_file():
    REPOSITORY = DEVELOPMENT_REPOSITORY
else:
    REPOSITORY = ROOT
PAPER = REPOSITORY / "paper/AnonymousSubmission2027.tex"
SUPPLEMENT = REPOSITORY / "paper/supplementary_material.tex"
BIB = REPOSITORY / "paper/aaai2027.bib"


FIRST_USE_EXPANSIONS = {
    "TRI": "temporal referent integrity}\n(TRI)",
    "LLM": "large language model (LLM)",
    "CTA": "Compile-then-act (CTA)",
    "ID": "entity identifier\n(ID)",
    "APIs": "application programming interfaces (APIs)",
    "NLI": "natural-language inference (NLI)",
    "PairAcc": "pair accuracy (PairAcc)",
    "E2E": "end-to-end (E2E)",
    "ITT": "intention-to-treat (ITT)",
}


def _without_comments(text: str) -> str:
    return "\n".join(re.split(r"(?<!\\)%", line, maxsplit=1)[0] for line in text.splitlines())


def _citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite\w*\{([^}]+)\}", text):
        keys.update(key.strip() for key in match.group(1).split(","))
    return keys


def _labels(text: str, command: str) -> set[str]:
    return set(re.findall(rf"\\{command}\{{([^}}]+)\}}", text))


def build_report(paper: Path = PAPER, bib: Path = BIB) -> dict[str, Any]:
    paper_text = _without_comments(paper.read_text(encoding="utf-8"))
    supplement_text = _without_comments(SUPPLEMENT.read_text(encoding="utf-8"))
    normalized_paper = re.sub(r"\s+", " ", paper_text)
    normalized_supplement = re.sub(r"\s+", " ", supplement_text)
    bib_text = _without_comments(bib.read_text(encoding="utf-8"))
    body = paper_text.split("\\begin{document}", 1)[-1]
    checks: dict[str, bool] = {}

    first_use: dict[str, dict[str, int]] = {}
    for acronym, expansion in FIRST_USE_EXPANSIONS.items():
        first = body.find(acronym)
        defined = body.find(expansion)
        first_use[acronym] = {"first": first, "definition": defined}
        checks[f"{acronym}_expanded_at_first_use"] = first >= 0 and first == defined + len(expansion) - len(acronym) - 1

    cited = _citation_keys(paper_text)
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_text))
    references = _labels(paper_text, "ref")
    labels = _labels(paper_text, "label")
    checks["all_citations_have_bibliography_entries"] = cited <= bib_keys
    checks["all_cross_references_have_labels"] = references <= labels
    checks["no_legacy_table_abbreviations"] = not any(
        token in paper_text for token in ("Model / ctl.", " / Gen. &", "CTA/Gated")
    )
    checks["abstract_retains_scope_boundary"] = all(
        phrase in normalized_paper
        for phrase in (
            "controlled diagnostic for selective referent re-resolution",
            "Author-built public-suite retrieval finds no strict native opportunity, but recall is uncalibrated",
            "native-workflow prevalence and open-language coverage remain unresolved",
            "A post-hoc event-order rule performs strongly on authored inventories but transfers poorly",
        )
    )
    checks["abstract_chronology_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "Across a 240-task cross-schema replication",
            "Under equal calls and actor payloads",
            "A post-hoc event-order rule",
        )
    )
    checks["body_chronology_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "Package runs: Qwen primary/frozen; GLM post-primary",
            "Full matched-call confirmation (post-primary)",
            "Source-derived matched-call contrast (post-primary)",
            "Post-hoc event-order rule",
            "Planned or unverified analyses are not results",
        )
    )
    checks["primary_is_explicitly_package_level"] = all(
        phrase in normalized_paper
        for phrase in (
            "primary Qwen package comparison and GLM replication are call-asymmetric mechanism probes",
            "Lifecycle-Gated improves over Generic",
            "primary package comparison call-asymmetric",
        )
    )
    checks["binding_drift_boundary_and_citation_are_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "Concurrent Binding Drift work studies whether a correctly bound primary carry slot remains stable",
            "TRI varies the control state of the same action-target description under the same transition",
            "\\cite{babu2026bindingdrift}",
            "Persistence-policy adaptations",
        )
    )
    checks["selector_visibility_boundary_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "Controllers receive the instruction's natural-language selector",
            "Gold targets, normalized selector fields",
            "pre-/post-refresh winner IDs are withheld",
        )
    )
    checks["code_data_supplement_routing_is_explicit"] = all(
        phrase in paper_text
        for phrase in (
            "anonymous Code and Data Supplement contains prompts, runner interfaces",
            "Complete settings are in the Code and Data Supplement",
        )
    ) and all(
        phrase not in paper_text
        for phrase in (
            "The supplement gives the complete interfaces",
            "Complete E2E,\nmode-slice, schema-transfer, and model-facing SQLite tables are supplementary",
        )
    )
    checks["figure_two_evidence_status_is_explicit"] = (
        "Post-primary audits from frozen \\PrimaryDiagnostic{} and \\NewSchemaReplication{} outputs"
        in normalized_supplement
        and all(
            phrase in normalized_paper
            for phrase in (
                "Policy marginals and matched discrimination on the \\PrimaryDiagnostic{}",
                "Cross-schema paired controller transitions on shared-eligible Preserve rows",
                "Wrong-target writes under fixed-executor replay",
                "Decision-visible minus History-only effects under equal calls",
                "Package runs: Qwen primary/frozen; GLM post-primary",
                "Changed pairs (post-primary audit)",
                "Post-hoc event-order rule",
            )
        )
    )
    checks["no_overstated_tie_or_sample_sufficiency_language"] = not any(
        phrase in paper_text + "\n" + supplement_text
        for phrase in (
            "CTA ties",
            "Qwen's tie",
            "sample-sufficiency",
            "not sample-limited",
        )
    )
    checks["external_extension_has_four_paper_facing_conditions"] = (
        "four-condition, 96-task extension" in normalized_paper
        and "five-condition, 96-task extension" not in paper_text.lower()
    )
    checks["source_anchored_transfer_retains_boundary"] = all(
        phrase in normalized_paper
        for phrase in (
            "connect the controlled diagnostic to source interfaces",
            "public-suite audit below examines native opportunity coverage separately",
            "execution accuracy has no consistent winner",
        )
    )
    checks["conclusion_retains_scope_boundary"] = all(
        phrase in normalized_paper
        for phrase in (
            "The current evidence covers controlled single-refresh scalar workflows",
            "Native-workflow frequency and general runtime behavior remain unmeasured",
        )
    )
    return {
        "status": "zero-API static manuscript audit",
        "paper": str(paper.relative_to(REPOSITORY)),
        "bibliography": str(bib.relative_to(REPOSITORY)),
        "checks": checks,
        "first_use": first_use,
        "missing_bibliography_entries": sorted(cited - bib_keys),
        "missing_labels": sorted(references - labels),
    }


def validate(report: dict[str, Any]) -> None:
    failed = [name for name, passed in report["checks"].items() if not passed]
    if failed:
        raise ValueError(f"manuscript consistency audit failed: {', '.join(failed)}")


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Manuscript Consistency Audit",
        "",
        f"Status: {report['status']}.",
        "",
        "| Check | Result |",
        "|---|---:|",
    ]
    lines.extend(
        f"| `{name}` | {'PASS' if passed else 'FAIL'} |"
        for name, passed in report["checks"].items()
    )
    lines.extend(
        [
            "",
            f"Missing bibliography entries: {json.dumps(report['missing_bibliography_entries'])}",
            f"Missing labels: {json.dumps(report['missing_labels'])}",
            "",
        ]
    )
    return "\n".join(lines)
