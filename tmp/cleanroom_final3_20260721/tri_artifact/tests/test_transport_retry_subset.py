from __future__ import annotations

import unittest

from scripts.make_transport_retry_subset import failed_task_ids


class TransportRetrySubsetTest(unittest.TestCase):
    def test_selects_status_or_internal_errors(self) -> None:
        rows = [
            {"status": "ok", "task": {"id": "a"}, "result": {"errors": []}},
            {"status": "api_error", "task": {"id": "b"}, "result": {"errors": ["api"]}},
            {"status": "ok", "task": {"id": "c"}, "result": {"errors": ["closed"]}},
        ]
        self.assertEqual(failed_task_ids(rows), {"b", "c"})


if __name__ == "__main__":
    unittest.main()
