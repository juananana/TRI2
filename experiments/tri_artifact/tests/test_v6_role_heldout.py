from __future__ import annotations

import unittest
from collections import Counter
from pathlib import Path

from tri.v6_role_heldout_eval import heldout_rows, load, smoke_rows


class RoleHeldoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = load(Path("data/temporal_referent_v3_unseen_domains.jsonl"))
        cls.rows = heldout_rows(source)

    def test_balanced_and_unique(self) -> None:
        self.assertEqual(len(self.rows), 40)
        self.assertEqual(len({row["id"] for row in self.rows}), 40)
        self.assertEqual(Counter(row["domain"] for row in self.rows), {
            "projects": 10,
            "expenses": 10,
            "inventory": 10,
            "deployments": 10,
        })
        self.assertEqual(Counter(row["binding"] for row in self.rows), {
            "anchored": 20,
            "dynamic": 20,
        })
        self.assertEqual(set(Counter(row["update"] for row in self.rows).values()), {8})
        self.assertEqual(len({row["template_id"] for row in self.rows}), 20)

    def test_smoke_has_both_modes_and_two_updates(self) -> None:
        smoke = smoke_rows(self.rows)
        self.assertEqual(len(smoke), 4)
        self.assertEqual({row["binding"] for row in smoke}, {"anchored", "dynamic"})
        self.assertEqual({row["update"] for row in smoke}, {"flip", "remove"})


if __name__ == "__main__":
    unittest.main()
