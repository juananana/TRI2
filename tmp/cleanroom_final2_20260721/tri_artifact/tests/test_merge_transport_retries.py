from __future__ import annotations

import unittest

from scripts.merge_transport_retries import merge


class MergeTransportRetriesTest(unittest.TestCase):
    def test_replaces_only_failed_rows_and_records_provenance(self) -> None:
        good = {"status": "ok", "task": {"id": "a"}, "result": {"errors": [], "success": True}}
        bad = {"status": "api_error", "task": {"id": "b"}, "result": {"errors": ["ssl"]}}
        retry = {"status": "ok", "task": {"id": "b"}, "result": {"errors": [], "success": True}}
        rows = merge([good, bad], [retry])
        self.assertIs(rows[0], good)
        self.assertTrue(rows[1]["result"]["success"])
        self.assertEqual(rows[1]["transport_recovery"]["original_status"], "api_error")


if __name__ == "__main__":
    unittest.main()
