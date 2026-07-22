from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tri.v3_exact_predecessor_report import (
    bootstrap_clusters,
    build_report,
    compiler_fields,
    is_api_error,
    is_parse_error,
    markdown,
    summarize_pair,
    summarize_run,
)


def row(
    task_id: str,
    *,
    binding: str = "anchored",
    phenomenon: str = "explicit",
    update: str = "flip",
    template_id: str = "anchor-t1",
    binding_time: str = "pre_refresh",
    bound_target_id: str | None = "A",
    success: bool = True,
    status: str = "ok",
    errors: list[str] | None = None,
) -> dict:
    return {
        "model": "Example/GLM-5.1",
        "status": status,
        "task": {
            "id": task_id,
            "binding": binding,
            "phenomenon": phenomenon,
            "update": update,
            "template_id": template_id,
            "pre_refresh_target": "A",
        },
        "result": {
            "mode": "compile_then_act",
            "compiled_ledger": {
                "binding_time": binding_time,
                "bound_target_id": bound_target_id,
            },
            "success": success,
            "errors": errors or [],
        },
    }


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.write_text("".join(json.dumps(item) + "\n" for item in rows), encoding="utf-8")
    return path


class ExactPredecessorReportTests(unittest.TestCase):
    def test_errors_and_stage_attribution_are_separate(self) -> None:
        api = row("api", status="error", success=False)
        parse = row("parse", success=False, errors=["invalid JSON ledger"])
        actor = row("actor", success=False)
        compiler = row("compiler", binding_time="post_refresh", success=False)

        self.assertTrue(is_api_error(api))
        self.assertFalse(is_parse_error(api))
        self.assertTrue(is_parse_error(parse))
        self.assertTrue(compiler_fields(actor)["actor_failure"])
        self.assertTrue(compiler_fields(compiler)["compiler_induced_failure"])
        self.assertFalse(compiler_fields(compiler)["actor_failure"])

    def test_run_summary_uses_itt_and_all_requested_slices(self) -> None:
        rows = [
            row("one", template_id="anchor-t1"),
            row("two", binding="dynamic", phenomenon="implicit", update="stable",
                template_id="dynamic-t1", binding_time="post_refresh", bound_target_id=None,
                success=False),
            row("three", success=False, errors=["invalid JSON ledger"]),
            row("four", status="error", success=False),
        ]
        with tempfile.TemporaryDirectory() as directory:
            report = summarize_run(write_jsonl(Path(directory) / "exact.jsonl", rows), 100, 7)

        self.assertEqual(report["n_tasks"], 4)
        self.assertEqual(report["itt_correct"], 1)
        self.assertEqual(report["api_errors"], 1)
        self.assertEqual(report["parse_errors"], 1)
        self.assertEqual(report["final_failures"], 3)
        self.assertEqual(report["actor_failures"], 1)
        self.assertEqual(report["compiler_binding_correct"], 2)
        self.assertEqual(report["anchored_n"], 3)
        self.assertEqual(report["anchored_bound_id_correct"], 1)
        self.assertEqual({item["binding"] for item in report["binding_slices"]}, {"anchored", "dynamic"})
        self.assertEqual({item["phenomenon"] for item in report["explicitness_slices"]}, {"explicit", "implicit"})
        self.assertEqual({item["update"] for item in report["update_slices"]}, {"flip", "stable"})
        self.assertEqual({item["template_id"] for item in report["template_slices"]}, {"anchor-t1", "dynamic-t1"})

    def test_cluster_bootstrap_samples_whole_templates(self) -> None:
        lo, hi = bootstrap_clusters(
            {"a": [1, 1], "b": [0, 0]},
            lambda values: sum(values) / len(values),
            samples=1000,
            seed=7,
        )
        self.assertEqual((lo, hi), (0.0, 1.0))

    def test_pair_delta_is_exact_minus_comparator_and_is_task_id_matched(self) -> None:
        exact_rows = [
            row("one", template_id="a", success=True),
            row("two", template_id="b", success=False),
        ]
        comparator_rows = [
            row("two", template_id="b", success=True),
            row("one", template_id="a", success=False),
            row("unpaired", template_id="b", success=True),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = summarize_pair(
                write_jsonl(root / "exact.jsonl", exact_rows),
                write_jsonl(root / "other.jsonl", comparator_rows),
                "comparator", 100, 7,
            )

        self.assertEqual(summary["n_paired"], 2)
        self.assertEqual(summary["unpaired_exact"], 0)
        self.assertEqual(summary["unpaired_comparator"], 1)
        self.assertEqual(summary["delta_exact_minus_comparator"], 0.0)

    def test_build_report_has_two_comparisons_per_model_and_markdown(self) -> None:
        rows = [row("one", template_id="a"), row("two", template_id="b", success=False)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exact = tuple(write_jsonl(root / f"exact-{i}.jsonl", rows) for i in range(2))
            untyped = tuple(write_jsonl(root / f"untyped-{i}.jsonl", rows) for i in range(2))
            lifecycle = tuple(write_jsonl(root / f"lifecycle-{i}.jsonl", rows) for i in range(2))
            report = build_report(exact, untyped, lifecycle, samples=100, seed=7)

        self.assertEqual(len(report["runs"]), 2)
        self.assertEqual(len(report["paired_comparisons"]), 4)
        self.assertIn("Explicitness Slices", markdown(report))
        self.assertIn("Delta is exact historical", markdown(report))


if __name__ == "__main__":
    unittest.main()
