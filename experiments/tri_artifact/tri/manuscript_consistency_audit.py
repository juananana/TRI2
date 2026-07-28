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
    "TRI": "temporal referent integrity",
    "LLM": "large language model",
    "CTA": "Compile-then-act",
    "ID": "entity identifier",
    "APIs": "application programming interfaces",
    "NLI": "natural-language inference",
    "PairAcc": "pair accuracy",
    "E2E": "end-to-end",
    "ITT": "intention-to-treat",
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


def _plain_text(text: str) -> str:
    """Normalize simple LaTeX prose for robust first-use checks."""
    for _ in range(3):
        text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\[A-Za-z]+", " ", text)
    return re.sub(r"\s+", " ", text.replace("{", " ").replace("}", " "))


def build_report(paper: Path = PAPER, bib: Path = BIB) -> dict[str, Any]:
    paper_text = _without_comments(paper.read_text(encoding="utf-8"))
    supplement_text = _without_comments(SUPPLEMENT.read_text(encoding="utf-8"))
    normalized_paper = re.sub(r"\s+", " ", paper_text)
    normalized_supplement = re.sub(r"\s+", " ", supplement_text)
    bib_text = _without_comments(bib.read_text(encoding="utf-8"))
    body = paper_text.split("\\begin{document}", 1)[-1]
    plain_body = _plain_text(body)
    plain_body_folded = plain_body.casefold()
    checks: dict[str, bool] = {}

    first_use: dict[str, dict[str, int]] = {}
    for acronym, expansion in FIRST_USE_EXPANSIONS.items():
        match = re.search(rf"(?<![A-Za-z]){re.escape(acronym)}(?![A-Za-z])", plain_body)
        first = match.start() if match else -1
        defined = plain_body_folded.find(expansion.casefold())
        first_use[acronym] = {"first": first, "definition": defined}
        checks[f"{acronym}_expanded_at_first_use"] = first < 0 or (defined >= 0 and defined <= first)

    cited = _citation_keys(paper_text)
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_text))
    references = _labels(paper_text, "ref")
    generated_text = ""
    generated_dir = paper.parent / "generated"
    if generated_dir.is_dir():
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in generated_dir.glob("*.tex")
        )
        references |= _labels(generated_text, "ref")
    labels = _labels(paper_text + "\n" + generated_text, "label")
    checks["all_citations_have_bibliography_entries"] = cited <= bib_keys
    checks["all_cross_references_have_labels"] = references <= labels
    checks["no_legacy_table_abbreviations"] = not any(
        token in paper_text for token in ("Model / ctl.", " / Gen. &", "CTA/Gated")
    )
    checks["abstract_retains_scope_boundary"] = all(
        phrase in normalized_paper
        for phrase in (
            "a diagnostic built from matched Preserve/Reevaluate pairs",
            "In a post-primary controlled replication across three model backends on 240 authored tasks spanning ten schemas, an author-designed Generic controller",
            "Effects on pairs adapted from public benchmarks varied by model",
            "Limited human agreement audits did not establish open-language transfer",
            "a controlled diagnostic for selective re-resolution",
            "native prevalence and generalization to open-ended language remain unresolved",
        )
    )
    checks["abstract_chronology_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "In a post-primary controlled replication across three model backends on 240 authored tasks spanning ten schemas",
            "A SQLite tool-loop test",
            "With equal calls and identical base actor inputs, exposing a composite decision block",
        )
    )
    checks["body_chronology_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "The Qwen package comparison is primary/frozen, with a later GLM replication",
            "The ten-schema attribution, equal-call contrasts, human agreement audits, and external audits are post-primary",
            "Rule* is post-hoc",
        )
    )
    checks["primary_is_explicitly_package_level"] = all(
        phrase in normalized_paper
        for phrase in (
            "The primary comparison changes the complete controller package and uses different numbers of model calls",
            "Qwen E2E changes from 103/160 for Generic to 157/160 for Lifecycle-Gated",
            "language-template-cluster 95\\% confidence interval (CI) [18.1, 49.4]",
            "the later GLM replication changes from 115/160 to 160/160 (+28.1 points; 95\\% CI [18.1, 38.1])",
            "The equal-call test holds base payloads, states, and tool schemas fixed",
            "estimates the complete block rather than any field",
        )
    )
    checks["theory_certification_scope_is_explicit"] = all(
        phrase in paper_text
        for phrase in (
            "e_0&=q_r(S_0)\\in E",
            "A_P=N^{-1}\\sum_iY_{Pi}",
            "A_R=N^{-1}\\sum_iY_{Ri}",
            "computed over the same $N$ complete",
            "A=1-n/N",
            "worst-case",
            "\\Pr(O,B,U,X)",
        )
    ) and all(
        phrase in supplement_text
        for phrase in (
            "Proposition 1 (support-based observational equivalence)",
            "Proposition 2 (sharp aggregate certification bound)",
            "Proposition 3 (strict TRI-write pathway factorization)",
            "No independence assumption is used",
            "zero aggregate-to-PairAcc selection regret",
        )
    )
    checks["binding_drift_boundary_and_citation_are_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "Binding Drift assumes a primary referent has been committed, then tests persistence, reverification, and error propagation",
            "TRI instead conditions on a correct initial binding, crosses bound and deferred authorization directions under the same transition",
            "neither an official reproduction nor an information-matched CTA baseline",
            "it receives $S_1$ but neither $S_0$ nor the resolved old ID",
            "\\cite{babu2026bindingdrift}",
        )
    )
    checks["selector_visibility_boundary_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "Controllers receive the instruction's natural-language selector",
            "Gold targets, normalized selector fields, and pre- and post-refresh winner IDs are withheld",
        )
    )
    checks["code_data_supplement_routing_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "The artifact contains frozen inventories, prompts, outputs, reports, hashes, and the error taxonomy",
            "The PDF supplement gives the verbatim interface; prompts, payloads, raw outputs, and scoring code are in the anonymous Code and Data Supplement",
        )
    ) and all(
        phrase in normalized_supplement
        for phrase in (
            "Verbatim Matched-Call Interface",
            "Decision-visible adds one field",
            "IDs are never fuzzy-matched or repaired",
        )
    )
    checks["claim_evidence_map_and_result_status_are_explicit"] = (
        "Post-primary audits from frozen \\PrimaryDiagnostic{} and \\NewSchemaReplication{} outputs"
        in normalized_supplement
        and all(
            phrase in normalized_paper
            for phrase in (
                "Claim-to-evidence map",
                "Exact targets within three policy extremes; no internal-mechanism identification",
                "Ten-schema conditional outcomes after correct initial binding"
                if "Ten-schema conditional outcomes after correct initial binding" in normalized_paper
                else "Ten-schema outcomes after correct initial binding",
                "Secondary/frozen 40-task SQLite outcomes for Generic",
                "The Qwen package comparison is primary/frozen",
                "The ten-schema attribution, equal-call contrasts, human agreement audits, and external audits are post-primary",
                "Rule* is post-hoc",
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
        "An extension finds zero substitutions in four conditions over 64--87 eligible opportunities"
        in normalized_paper
        and "five conditions" not in paper_text.lower()
    )
    checks["source_anchored_transfer_retains_boundary"] = all(
        phrase in normalized_paper
        for phrase in (
            "The 30-pair test uses states and tool schemas from STATE-Bench, AgentDojo, and ToolSandbox",
            ("not native tasks or prevalence evidence"
             if "not native tasks or prevalence evidence" in normalized_paper
             else "native behavior, or prevalence"),
            "no method consistently improves execution accuracy",
        )
    )
    checks["conclusion_retains_scope_boundary"] = all(
        phrase in normalized_paper
        for phrase in (
            "Evidence is limited to the tested single-refresh scalar policies and complete-block intervention",
            "does not establish native prevalence, open-language transfer, or the necessity of a unique architecture",
        )
    )
    checks["equal_call_interface_is_self_contained"] = all(
        phrase in normalized_paper
        for phrase in (
            "RQ3: Does Decision Visibility Change Outcomes under Equal Calls?",
            "One compiler call and two actor calls; actor order alternates by task index",
            "Byte-identical instruction, states, selected ID, selector, action, and tool schema",
            "Decision-enforced & Zero-call deterministic transform, not a third actor condition",
            "does not identify any field or framing component separately",
        )
    )
    checks["replication_denominator_is_explicit"] = all(
        phrase in normalized_paper
        for phrase in (
            "40 state clusters across ten schemas",
            "two reference modes crossed with Stable, Flip, and name-collision transitions",
            "yielding 80 changed pairs",
            "PairAcc denominator of 80",
        )
    )
    checks["human_evidence_is_agreement_not_validation"] = all(
        phrase in normalized_supplement
        for phrase in (
            "Blinded Human Agreement Audit",
            "Post-primary descriptive construct audit",
        )
    ) and not any(
        phrase in normalized_paper + " " + normalized_supplement
        for phrase in (
            "human construct evidence",
            "Blind Human Construct Validation",
            "fixed-rater validation result",
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
