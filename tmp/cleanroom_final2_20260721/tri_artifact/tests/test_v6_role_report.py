from __future__ import annotations

import unittest

from tri.v6_role_report import exact_mcnemar


class RoleReportTest(unittest.TestCase):
    def test_exact_mcnemar_is_two_sided(self) -> None:
        self.assertEqual(exact_mcnemar(0, 0), 1.0)
        self.assertAlmostEqual(exact_mcnemar(0, 7), 0.015625)


if __name__ == "__main__":
    unittest.main()
