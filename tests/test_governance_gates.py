"""Regression tests for governed-factory P1 governance fixes.

Guards two Codex P1 findings on the provider-neutral governed factory:

  P1-1 (gatekeeper.check_action): an authorized implementation/source write
        (implementation_authorized == True) must be ALLOWED, not fail closed.
  P1-2 (governed_factory.task_needs_human): tasks using the documented
        task-schema Gate Impact values ("advances gate" / "blocks gate")
        must trigger a human gate stop.
"""

import pathlib
import sys
import unittest

AUTOMATION = pathlib.Path(__file__).resolve().parents[1] / "automation"
sys.path.insert(0, str(AUTOMATION))

import gatekeeper  # noqa: E402
import governed_factory  # noqa: E402


class GatekeeperAuthorizedWriteTests(unittest.TestCase):
    def test_authorized_source_write_is_allowed(self):
        for prefix in gatekeeper.PROTECTED_SOURCE_PREFIXES:
            ok, msg = gatekeeper.check_action(
                "write", prefix + "thing", {"implementation_authorized": True}
            )
            self.assertTrue(ok, f"{prefix}: {msg}")

    def test_unauthorized_source_write_still_blocked(self):
        ok, _ = gatekeeper.check_action(
            "write", "src/app.py", {"implementation_authorized": False}
        )
        self.assertFalse(ok)

    def test_planning_write_allowed(self):
        ok, _ = gatekeeper.check_action("write", "docs/x.md", {})
        self.assertTrue(ok)

    def test_unknown_path_write_fails_closed_even_when_authorized(self):
        ok, _ = gatekeeper.check_action(
            "write", "random/x", {"implementation_authorized": True}
        )
        self.assertFalse(ok)


class TaskNeedsHumanGateTests(unittest.TestCase):
    def test_documented_gate_values_stop(self):
        self.assertTrue(governed_factory.task_needs_human({"Gate Impact": "advances gate"}))
        self.assertTrue(governed_factory.task_needs_human({"Gate Impact": "blocks gate"}))

    def test_phrasal_gate_impact_stops(self):
        self.assertTrue(
            governed_factory.task_needs_human(
                {"Gate Impact": "blocks Gate 1 until compliance review exists"}
            )
        )

    def test_non_gate_impact_does_not_stop(self):
        self.assertFalse(governed_factory.task_needs_human({"Gate Impact": "none"}))

    def test_planning_only_override_preserved(self):
        self.assertFalse(
            governed_factory.task_needs_human(
                {"Gate Impact": "advances gate", "Status": "planning only"}
            )
        )


if __name__ == "__main__":
    unittest.main()
