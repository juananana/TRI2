from __future__ import annotations

import tempfile
import unittest
import zipfile
import re
from pathlib import Path

from scripts.build_current_supplement import build


class CurrentSupplementTest(unittest.TestCase):
    def test_builds_complete_key_free_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifact.zip"
            build(output)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                self.assertIn(
                    "tri_artifact/data/temporal_referent_v3_language_clusters.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/data/external_public_annotation_candidates_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/TRI_external_public_siliconflow_annotation_addendum.md",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/external_public_annotation_v1.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/external_public_annotation_siliconflow_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/data/source_anchored_external_transfer_tasks_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/source_anchored_external_transfer_v1.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/source_anchored_external_transfer_siliconflow_repaired_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/data/model_authored_linguistic_stress_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/model_authored_linguistic_stress_transport_repaired_v2.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/model_authored_linguistic_evaluate_glm_cta_full_v1.jsonl",
                    names,
                )
                self.assertIn("tri_artifact/paper/AnonymousSubmission2027.tex", names)
                self.assertIn("tri_artifact/paper/aaai2027.bib", names)
                self.assertIn("tri_artifact/paper/aaai2027.bst", names)
                self.assertIn("tri_artifact/paper/aaai2027.sty", names)
                self.assertIn("tri_artifact/paper/supplementary_material.tex", names)
                self.assertIn(
                    "tri_artifact/paper/source_anchored_external_transfer_table.tex",
                    names,
                )
                for figure in (
                    "fig_resolution_policy_phase_space_compact.pdf",
                    "fig_shared_eligible_target_flow_compact.pdf",
                    "fig_wrong_write_decomposition_compact.pdf",
                    "fig_source_model_transfer_fingerprints_compact.pdf",
                    "fig_decision_visibility_effect_sizes_compact.pdf",
                    "fig_enforcement_repairs_harms_compact.pdf",
                ):
                    self.assertIn(f"tri_artifact/paper/Figures/{figure}", names)
                self.assertIn(
                    "tri_artifact/human_validation/normalized_returns/annotator_1.csv",
                    names,
                )
                self.assertIn("tri_artifact/human_validation/analysis.json", names)
                self.assertFalse(any("annotation_key_private" in name for name in names))
                self.assertFalse(any("private_returns" in name for name in names))
                self.assertFalse(any(name.endswith(".xlsx") for name in names))
                self.assertFalse(any("TRI_AAAI" in name for name in names))
                self.assertIn(
                    "tri_artifact/reports/binding_drift_tri_glm_v7_full_v1.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/binding_drift_tri_glm_self_reverify_v7_full_v1.jsonl",
                    names,
                )
                self.assertFalse(
                    any(
                        name.startswith("tri_artifact/external_pilots/appworld_runtime/")
                        for name in names
                    )
                )
                self.assertFalse(
                    any(name.startswith("tri_artifact/runs/") and archive.getinfo(name).file_size == 0 for name in names)
                )
                normalized = archive.read(
                    "tri_artifact/human_validation/normalized_returns/annotator_2.csv"
                ).decode()
                self.assertNotIn("comment", normalized.splitlines()[0])
                rewrites = archive.read(
                    "tri_artifact/human_validation/paraphrase_authoring.csv"
                ).decode()
                self.assertNotIn("author_notes", rewrites.splitlines()[0])
                for name in names:
                    if not name.endswith("/"):
                        data = archive.read(name)
                        self.assertIsNone(re.search(rb"sk-[A-Za-z0-9_-]{20,}", data))
                        self.assertNotIn(b"/Users/", data)


if __name__ == "__main__":
    unittest.main()
