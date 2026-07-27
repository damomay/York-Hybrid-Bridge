from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from york_decoder_qualification import DEFAULT_FIXTURES, run_qualification, write_report


class YorkDecoderQualificationTests(unittest.TestCase):
    def test_all_recovered_fixtures_pass(self) -> None:
        report = run_qualification(DEFAULT_FIXTURES)
        self.assertEqual(report["summary"]["result"], "PASS")
        self.assertGreaterEqual(report["summary"]["total"], 14)
        self.assertEqual(report["summary"]["confidence_percent"], 100.0)

    def test_report_files_are_written_to_qualification_folder(self) -> None:
        report = run_qualification(DEFAULT_FIXTURES)
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = write_report(report, Path(tmp))
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(data["report_type"], "york_decoder_qualification")

    def test_bad_expected_value_is_reported_as_mismatch(self) -> None:
        payload = json.loads(DEFAULT_FIXTURES.read_text(encoding="utf-8"))
        payload["fixtures"] = [payload["fixtures"][0]]
        payload["fixtures"][0]["expected"]["power"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixtures.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            report = run_qualification(path)
            self.assertEqual(report["summary"]["result"], "FAIL")
            self.assertIn("power", report["results"][0]["differences"])


if __name__ == "__main__":
    unittest.main()
