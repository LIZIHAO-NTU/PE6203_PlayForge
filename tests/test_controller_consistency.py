"""A-owned controller finalization checks, not unseen-game or model evaluations."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from agent.provider import BudgetError, ProviderError
from agent.runner import run
from agent.verification import preflight, verify
from evals.resource_fixture import resource_bundle, resource_plan
from test_mvp import TempTest, config, example_bundle, example_plan, verifier_result


def hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class ControllerConsistencyBase(TempTest):
    def setUp(self):
        super().setUp()
        guard = patch("agent.provider.open_request", side_effect=AssertionError("No real model API"))
        guard.start()
        self.addCleanup(guard.stop)

    def invoke(self, responses, checker, *, browser=False, **options):
        stages, requests, frozen_bytes, original_sources = [], [], [], {}

        class ScriptedClient:
            def __init__(self, cfg, trace, max_calls, deadline):
                self.calls, self.limit = 0, max_calls

            def ask_json(self, stage, system, prompt):
                if self.calls >= self.limit:
                    raise BudgetError("Controlled call budget exhausted")
                self.calls += 1
                stages.append(stage)
                requests.append(json.loads(prompt))
                response = responses[stage]
                if isinstance(response, BaseException):
                    raise response
                return deepcopy(response)

            def usage_summary(self):
                return {"api_attempts": 0, "scripted_model_requests": self.calls,
                        "prompt_tokens": 0, "completion_tokens": 0, "cached_input_tokens": 0,
                        "calls_with_unknown_usage": 0, "estimated_known_usage_cost": None,
                        "currency": "USD", "cost_is_complete": False}

        def observe(game, plan, evidence, **kwargs):
            frozen_bytes.append(plan.read_bytes())
            original_sources[game.resolve()] = hashes(game)
            return checker(game, plan, evidence, **kwargs)

        spec = self.root / "spec.md"
        spec.write_text("Synthetic controller fixture; not a held-out game.", encoding="utf-8")
        before_spec = spec.read_bytes()
        output = self.root / "run"
        exit_code = run(config(), spec, output, client_factory=ScriptedClient, verifier=observe,
                        preflight_fn=preflight if browser else lambda **kw: {"ok": True}, **options)
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        state = json.loads((output / "traces/state.json").read_text(encoding="utf-8"))
        self.assertEqual(spec.read_bytes(), before_spec)
        self.assertEqual(summary, json.loads((output / "traces/summary.json").read_text(encoding="utf-8")))
        self.assertEqual(summary["stop_reason"], state["stop_reason"])
        self.assertEqual(summary.get("active_plan"), state["active_plan"])
        self.assertEqual(summary.get("plan_sha256"), state["plan_sha256"])
        self.assertIsNone(summary["full_game_acceptance"])
        self.assertEqual(summary["usage"]["api_attempts"], 0)
        self.assertNotIn(config().api_key, (output / "REPORT.md").read_text(encoding="utf-8"))
        if summary.get("selected_round") is not None:
            selected = output / state["selected_candidate"]
            self.assertEqual(state["repair_base_round"], summary["selected_round"])
            self.assertEqual(selected, output / "traces/attempts" / f"{summary['selected_round']:02d}" / "game")
            self.assertEqual(hashes(output / "game"), hashes(selected))
            self.assertEqual(hashes(selected), original_sources[selected.resolve()])
        else:
            self.assertIsNone(state["selected_candidate"])
            if summary.get("preserved_unverified_candidate"):
                self.assertEqual(hashes(output / "game"), list(original_sources.values())[-1])
        return exit_code, output, summary, state, stages, requests, frozen_bytes

    def assert_frozen(self, result):
        _, output, summary, _, _, _, snapshots = result
        payload = (output / "traces" / summary["active_plan"]).read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), summary["plan_sha256"])
        self.assertTrue(all(snapshot == payload for snapshot in snapshots))

    def assert_nonpass(self, result, status, exit_code):
        code, _, summary, _, _, _, _ = result
        self.assertEqual(code, exit_code)
        self.assertEqual(summary["status"], status)
        self.assertFalse(summary["automated_checks_passed"])


class ControllerConsistencyTests(ControllerConsistencyBase):
    def responses(self):
        return {"plan": example_plan(), "code_1": example_bundle(False)}

    def test_call_budget_keeps_verified_base_and_never_claims_success(self):
        result = self.invoke(self.responses(), lambda *a, **kw: verifier_result(False), max_calls=2)
        self.assert_nonpass(result, "budget_exhausted", 4)
        self.assert_frozen(result)
        self.assertEqual(result[2]["selected_round"], 1)
        self.assertEqual(result[3]["remaining_calls"], 0)
        self.assertEqual(result[4], ["plan", "code_1"])

    def test_elapsed_budget_keeps_base_without_a_second_model_request(self):
        clock = [0.0]
        def check(*args, **kwargs):
            clock[0] = 61.0
            return verifier_result(False)
        with patch("agent.runner.time.monotonic", side_effect=lambda: clock[0]):
            result = self.invoke(self.responses(), check, max_seconds=60)
        self.assert_nonpass(result, "budget_exhausted", 4)
        self.assert_frozen(result)
        self.assertEqual(result[3]["remaining_seconds"], 0)
        self.assertEqual(result[4], ["plan", "code_1"])

    def test_interrupt_during_repair_preserves_first_verified_candidate(self):
        responses = {**self.responses(), "code_2": KeyboardInterrupt("Controlled interrupt")}
        result = self.invoke(responses, lambda *a, **kw: verifier_result(False))
        self.assert_nonpass(result, "interrupted", 130)
        self.assert_frozen(result)
        self.assertEqual(result[2]["selected_round"], 1)
        self.assertEqual(result[4], ["plan", "code_1", "code_2"])

    def test_interrupt_before_any_verdict_preserves_only_unverified_source(self):
        def interrupted(*args, **kwargs):
            raise KeyboardInterrupt("Controlled verifier interrupt")
        result = self.invoke(self.responses(), interrupted)
        self.assert_nonpass(result, "interrupted", 130)
        self.assert_frozen(result)
        self.assertTrue(result[2]["preserved_unverified_candidate"])
        self.assertNotIn("selected_round", result[2])
        self.assertEqual(hashes(result[1] / "game"), hashes(result[1] / "traces/attempts/01/game"))

    def test_equal_score_regression_does_not_replace_stable_candidate(self):
        plan = example_plan()
        second = deepcopy(plan["tests"][0])
        second.update(id="T2", description="Two input events")
        second["steps"].insert(2, {"action": "click", "selector": "#increment"})
        second["steps"][-1]["value"] = 2
        plan["tests"].append(second)
        checks = []
        def check(*args, **kwargs):
            checks.append(1)
            return {**verifier_result(False), "tests": [
                {"id": "T1", "passed": len(checks) == 1},
                {"id": "T2", "passed": len(checks) == 2}]}
        responses = {"plan": plan, "code_1": example_bundle(False, "/* first */"),
                     "code_2": example_bundle(False, "/* second */")}
        result = self.invoke(responses, check, max_rounds=2)
        self.assert_nonpass(result, "checks_failed", 2)
        self.assert_frozen(result)
        self.assertEqual(result[2]["selected_round"], 1)
        self.assertEqual(result[2]["attempts"][1]["regressed_test_ids"], ["T1"])
        self.assertEqual(len(checks), 2)

    def test_changed_plan_is_detected_not_repaired_or_reported_as_success(self):
        def tamper(game, plan, evidence, **kwargs):
            plan.write_text("{}", encoding="utf-8")
            return verifier_result(True)
        result = self.invoke(self.responses(), tamper)
        self.assert_nonpass(result, "run_error", 4)
        self.assertIn("Frozen plan changed", result[2]["error"])
        self.assertTrue(result[2]["preserved_unverified_candidate"])
        # The controller detects tampering; it does not restore the altered file.
        self.assertNotEqual(hashlib.sha256((result[1] / "traces/plan.json").read_bytes()).hexdigest(),
                            result[2]["plan_sha256"])

    def test_failed_plan_recovery_cannot_upgrade_startup_to_functional_success(self):
        responses = {"plan": {"supported": True}, "code_1": example_bundle(),
                     "plan_recovery": ProviderError("Controlled recovery failure")}
        def startup(*args, **kwargs):
            result = verifier_result(True)
            result["tests"][0]["id"] = "StartupSurface"
            return result
        result = self.invoke(responses, startup, max_calls=5)
        self.assert_nonpass(result, "partial_game_plan_failed", 2)
        self.assert_frozen(result)
        self.assertFalse(result[2]["quality_gate"]["functional_evidence_present"])
        self.assertEqual(result[4].count("plan_recovery"), 1)
        self.assertEqual(result[4], ["plan", "plan", "code_1", "plan_recovery"])

    def test_successful_self_checks_are_not_full_game_acceptance(self):
        responses = {"plan": example_plan(), "code_1": example_bundle()}
        result = self.invoke(responses, lambda *a, **kw: verifier_result(True))
        self.assertEqual(result[0], 0)
        self.assertEqual(result[2]["status"], "automated_passed_manual_pending")
        self.assertTrue(result[2]["automated_checks_passed"])
        self.assert_frozen(result)
        self.assertEqual(result[2]["selected_round"], 1)


@unittest.skipUnless(os.getenv("MVP_BROWSER_TESTS") == "1", "Real-browser A integration; zero model API")
class ControllerConsistencyBrowserTests(ControllerConsistencyBase):
    def test_conflict_pause_preserves_real_browser_candidate_and_fixed_plan(self):
        plan = resource_plan(conflict=True)
        plan["tests"][0]["steps"][3]["value"] = "2"
        plan["tests"][1]["steps"].insert(1, {"action": "assert", "source": "state",
            "path": "energy", "op": "eq", "value": 3})
        result = self.invoke({"plan": plan, "code_1": resource_bundle()}, verify, browser=True)
        self.assert_nonpass(result, "plan_review_required", 2)
        self.assert_frozen(result)
        self.assertEqual(result[4], ["plan", "code_1"])
        self.assertEqual(result[2]["selected_round"], 1)
        self.assertTrue(result[2]["last_repair_route"]["cross_test_conflicts"])


if __name__ == "__main__":
    unittest.main()
