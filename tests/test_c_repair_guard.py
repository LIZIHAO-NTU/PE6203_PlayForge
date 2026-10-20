"""C repair-route checks against contradictory frozen expectations; no model API."""
import unittest
import json
import os
import tempfile
from pathlib import Path

from agent.diagnostics import route_failure
from agent.feedback import repair_feedback
from agent.runner import run
from evals.resource_fixture import resource_bundle, resource_plan
from test_mvp import config


def assertion(source, value, *, path="energy", selector="#energy"):
    return {"action": "assert", "source": source, "op": "eq", "value": value,
            **({"path": path} if source == "state" else {"selector": selector})}


def result(failed_id="T1", step=2):
    return {"ok": False, "tests": [{"id": failed_id, "passed": False,
            "failure_kind": "assertion_mismatch", "failed_step": step}]}


class CRepairGuardTests(unittest.TestCase):
    def test_adjacent_state_display_conflict_pauses_even_when_second_assertion_fails(self):
        plan = {"tests": [{"id": "T1", "steps": [assertion("state", 3), assertion("text", "2")]}]}
        route = route_failure(result(), plan=plan)
        self.assertEqual(route["action"], "stop_test_review")
        self.assertEqual(route["display_conflicts"][0]["display_step"], 2)

    def test_string_state_3_and_3_point_0_is_a_conflict(self):
        plan = {"tests": [{"id": "T1", "steps": [assertion("state", "3"), assertion("state", "3.0")]}]}
        route = route_failure(result(), plan=plan)
        self.assertEqual(route["action"], "stop_test_review")

    def test_numeric_state_3_and_3_point_0_is_equivalent(self):
        plan = {"tests": [{"id": "T1", "steps": [assertion("state", 3), assertion("state", 3.0)]}]}
        self.assertEqual(route_failure(result(), plan=plan)["action"], "review_failure")

    def test_cross_test_text_3_and_3_point_0_is_a_conflict(self):
        plan = {"tests": [
            {"id": "T1", "steps": [{"action": "click", "selector": "#attack"}, assertion("text", "3")]},
            {"id": "T2", "steps": [{"action": "click", "selector": "#attack"}, assertion("text", "3.0")]}]}
        observed = {"ok": False, "tests": [{"id": "T1", "passed": True},
            {"id": "T2", "passed": False, "failure_kind": "assertion_mismatch", "failed_step": 2}]}
        self.assertEqual(route_failure(observed, plan=plan)["action"], "stop_test_review")

    def test_distinct_action_sequences_do_not_create_false_conflict(self):
        plan = {"tests": [
            {"id": "T1", "steps": [{"action": "click", "selector": "#attack"}, assertion("state", 3)]},
            {"id": "T2", "steps": [{"action": "click", "selector": "#restart"}, assertion("state", 5)]}]}
        self.assertEqual(route_failure(result(), plan=plan)["action"], "review_failure")

    def test_missing_failed_step_observation_is_not_invented(self):
        observed = result(step=3)
        observed["tests"][0].update(actions=[{"step": 1, "action": "click"}],
                                     observations=[{"step": 1, "actual": 5}])
        plan = {"tests": [{"id": "T1", "description": "energy", "requirement_ids": ["R1"],
                 "steps": [{"action": "click", "selector": "#attack"}, assertion("state", 3), assertion("state", 3)]}],
                "requirements": [{"id": "R1", "text": "Attack costs 2 energy"}]}
        packet = repair_feedback(observed, plan)["failed_tests"][0]
        self.assertIsNone(packet["failure_observation"])


@unittest.skipUnless(os.getenv("MVP_BROWSER_TESTS") == "1", "Opt-in real browser; zero API calls")
class CRepairBrowserTests(unittest.TestCase):
    def test_runner_stops_before_editing_for_conflicting_frozen_checks(self):
        plan = resource_plan(conflict=True)
        plan["tests"][0]["steps"][3]["value"] = "2"
        plan["tests"][1]["steps"].insert(1, assertion("state", 3))
        stages = []

        class ScriptedClient:
            def __init__(self, *args): self.calls = 0
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                stages.append(stage)
                return plan if stage == "plan" else resource_bundle()
            def usage_summary(self):
                return {"api_attempts": 0, "prompt_tokens": 0, "completion_tokens": 0,
                        "cached_input_tokens": 0, "calls_with_unknown_usage": 0,
                        "estimated_known_usage_cost": 0, "currency": "USD",
                        "cost_is_complete": True, "scripted_responses": self.calls}

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec = root / "spec.md"
            spec.write_text("Energy starts at 5; each attack costs 2.", encoding="utf-8")
            output = root / "run"
            exit_code = run(config(), spec, output, client_factory=ScriptedClient,
                            preflight_fn=lambda **kw: {"ok": True}, max_rounds=3)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 2)
            self.assertEqual(stages, ["plan", "code_1"])
            self.assertEqual(summary["status"], "plan_review_required")
            self.assertTrue(summary["last_repair_route"]["cross_test_conflicts"])
            self.assertTrue((output / "game" / "index.html").is_file())


if __name__ == "__main__":
    unittest.main()
