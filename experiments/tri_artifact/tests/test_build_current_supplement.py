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
                self.assertIn("tri_artifact/paper/AnonymousSubmission2027.tex", names)
                self.assertIn("tri_artifact/paper/aaai2027.bib", names)
                self.assertIn("tri_artifact/paper/aaai2027.bst", names)
                self.assertIn("tri_artifact/paper/aaai2027.sty", names)
                self.assertIn("tri_artifact/paper/supplementary_material.tex", names)
                self.assertIn(
                    "tri_artifact/human_validation/normalized_returns/annotator_1.csv",
                    names,
                )
                self.assertIn("tri_artifact/human_validation/analysis.json", names)
                self.assertFalse(any("annotation_key_private" in name for name in names))
                self.assertFalse(any("private_returns" in name for name in names))
                self.assertFalse(any(name.endswith(".xlsx") for name in names))
                self.assertFalse(any("TRI_AAAI" in name for name in names))
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
