"""Regression tests for factory_metrics.py (objective FO-2/FO-3 aggregation).

The metrics script is the measurement method named in
docs/governance-frameworks/factory-objectives.md; these tests pin its
contract: pristine-template state reports zero runs honestly, violation
outcomes are counted, and unreadable records are surfaced instead of ignored.
"""

import json
import pathlib
import sys
import tempfile
import unittest

AUTOMATION = pathlib.Path(__file__).resolve().parents[1] / "automation"
sys.path.insert(0, str(AUTOMATION))

import factory_metrics  # noqa: E402


def record(outcome):
    return {"record_type": "factory-run-result", "task_id": "T-1",
            "checks": {}, "outcome": outcome}


class FactoryMetricsTests(unittest.TestCase):
    def test_pristine_template_reports_zero_runs(self):
        with tempfile.TemporaryDirectory() as d:
            missing = pathlib.Path(d) / "does-not-exist"
            summary = factory_metrics.summarize(factory_metrics.collect(missing))
        self.assertEqual(summary["runs_recorded"], 0)
        self.assertIsNone(summary["pass_rate"])

    def test_violation_outcomes_are_counted_not_hidden(self):
        with tempfile.TemporaryDirectory() as d:
            runs = pathlib.Path(d)
            (runs / "a-T1-result.json").write_text(json.dumps(record("pass")))
            (runs / "b-T2-result.json").write_text(
                json.dumps(record("violation: unauthorized writes")))
            summary = factory_metrics.summarize(factory_metrics.collect(runs))
        self.assertEqual(summary["runs_recorded"], 2)
        self.assertEqual(summary["runs_with_violations"], 1)
        self.assertEqual(summary["pass_rate"], 0.5)
        self.assertEqual(summary["violation_files"][0]["file"], "b-T2-result.json")

    def test_unreadable_record_is_surfaced(self):
        with tempfile.TemporaryDirectory() as d:
            runs = pathlib.Path(d)
            (runs / "bad-T3-result.json").write_text("{not json")
            summary = factory_metrics.summarize(factory_metrics.collect(runs))
        self.assertEqual(summary["unreadable_records"], ["bad-T3-result.json"])


if __name__ == "__main__":
    unittest.main()
