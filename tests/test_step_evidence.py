"""D step-evidence audit calibration; no paid model calls in any test."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from agent.contracts import test_steps, validate_plan, write_bundle
from agent.quality import completion_gate
from agent.verification import verify
from evals.step_evidence import audit_result, audit_run, audit_test, live, mutation_matrix
from test_mvp import TempTest, example_plan, example_bundle, verifier_result


def complete_record(plan=None):
    plan = plan or example_plan()
    tests = []
    for test in plan["tests"]:
        actions, observations = [], []
        for i, step in enumerate(test_steps(test), 1):
            actions.append({"step": i, "action": step["action"], "arguments": deepcopy(step),
                            "stage": "setup" if i <= len(test.get("setup_steps", [])) else "check",
                            "ok": True, "elapsed_ms": 1})
            if step["action"] == "assert":
                observations.append({"step": i, "actual": step["value"], "expected": step["value"],
                                     "op": step["op"], "passed": True})
        tests.append({"id": test["id"], "passed": True, "actions": actions, "observations": observations})
    return {**verifier_result(True), "tests": tests}


class StepAuditTests(unittest.TestCase):
    def test_complete_record_is_accepted_without_mutation(self):
        plan, record = example_plan(), complete_record()
        before = deepcopy((plan, record))
        report = audit_result(plan, record)
        self.assertTrue(report["step_supported_overall_pass"])
        self.assertEqual((plan, record), before)

    def test_baseline_flag_only_pass_is_unverified_not_proven_game_defect(self):
        plan, record = example_plan(), verifier_result(True)
        self.assertTrue(completion_gate(plan, record, "valid")["passed"])
        report = audit_result(plan, record)
        self.assertFalse(report["step_supported_overall_pass"])
        self.assertEqual(report["unsupported_pass_tests"], 1)

    def test_all_five_controlled_corruptions_are_detected(self):
        plan, record = example_plan(), complete_record()
        before = deepcopy(record)
        matrix = mutation_matrix(plan, record)
        self.assertEqual(len(matrix["cases"]), 5)
        self.assertTrue(all(c["detected"] for c in matrix["cases"]))
        self.assertTrue(all(c["baseline_gate_passed"] for c in matrix["cases"]))
        self.assertEqual(record, before)

    def test_changed_actual_value_cannot_keep_pass(self):
        record = complete_record()
        record["tests"][0]["observations"][-1]["actual"] = 99
        self.assertFalse(audit_result(example_plan(), record)["step_supported_overall_pass"])

    def test_changed_expected_value_cannot_override_frozen_plan(self):
        record = complete_record()
        record["tests"][0]["observations"][-1].update(actual=99, expected=99)
        self.assertFalse(audit_result(example_plan(), record)["step_supported_overall_pass"])

    def test_recorded_failure_remains_failure_without_requiring_unexecuted_tail(self):
        record = {**verifier_result(False), "tests": [{"id": "T1", "passed": False,
                  "failed_step": 2, "actions": [], "observations": []}]}
        report = audit_result(example_plan(), record)
        self.assertEqual(report["tests"][0]["verdict"], "recorded_nonpass")
        self.assertEqual(report["unsupported_pass_tests"], 0)
        self.assertEqual(mutation_matrix(example_plan(), record)["cases"], [])

    def test_missing_duplicate_unknown_test_records_are_not_accepted(self):
        original = complete_record()
        for records in ([], original["tests"] * 2,
                        original["tests"] + [{"id": "unknown", "passed": True}]):
            with self.subTest(records=records):
                self.assertFalse(audit_result(example_plan(), {**original, "tests": records})["step_supported_overall_pass"])

    def test_malformed_records_fail_closed_without_crashing(self):
        for records in (None, [None], ["not a record"]):
            with self.subTest(records=records):
                report = audit_result(example_plan(), {**verifier_result(True), "tests": records})
                self.assertFalse(report["step_supported_overall_pass"])
                self.assertTrue(report["malformed_test_records"])

    def test_setup_stage_and_duration_are_checked(self):
        plan = example_plan()
        plan["tests"][0]["setup_steps"] = [{"action": "click", "selector": "#increment"}]
        record = complete_record(plan)
        self.assertTrue(audit_result(plan, record)["step_supported_overall_pass"])
        record["tests"][0]["actions"][0]["stage"] = "check"
        self.assertFalse(audit_result(plan, record)["step_supported_overall_pass"])
        record = complete_record(plan)
        del record["tests"][0]["actions"][0]["elapsed_ms"]
        self.assertFalse(audit_result(plan, record)["step_supported_overall_pass"])

    def test_disabled_control_noop_is_not_mislabelled_as_tool_failure(self):
        record = complete_record()
        record["tests"][0]["actions"][1]["result"] = {"ignored_disabled": True}
        self.assertTrue(audit_result(example_plan(), record)["step_supported_overall_pass"])

    def test_capture_references_are_checked_against_saved_capture(self):
        plan = example_plan()
        plan["tests"][0]["steps"] = [
            {"action": "capture", "name": "before"},
            {"action": "click", "selector": "#increment"},
            {"action": "assert", "source": "state", "path": "score", "op": "gt",
             "value_from": {"capture": "before", "path": "score"}}]
        steps = plan["tests"][0]["steps"]
        record = {**verifier_result(True), "tests": [{"id": "T1", "passed": True,
            "actions": [{"step": i, "action": s["action"], "arguments": s,
                         "stage": "check", "ok": True, "elapsed_ms": 1,
                         **({"result": {"score": 0}} if i == 1 else {})} for i, s in enumerate(steps, 1)],
            "observations": [{"step": 3, "actual": 1, "op": "gt", "expected": 0, "passed": True}]}]}
        self.assertTrue(audit_result(plan, record)["step_supported_overall_pass"])
        record["tests"][0]["actions"][0]["result"] = {"score": 2}
        self.assertFalse(audit_result(plan, record)["step_supported_overall_pass"])


class ReadOnlyAuditTests(TempTest):
    def prepare(self, with_manifest=True):
        run = self.root / "run"
        run.mkdir()
        (run / "summary.json").write_text(json.dumps({"status": "checks_failed", "usage": {"api_attempts": 0}}))
        if with_manifest:
            game = run / "traces/attempts/01/game"
            write_bundle(example_bundle(), game)
            plan = example_plan()
            from agent.evidence import file_hashes
            path = game.parent / "evidence/replay.json"
            path.parent.mkdir()
            path.write_text(json.dumps({"plan": plan, "result": complete_record(),
                "game_sha256": file_hashes(game),
                "plan_content_sha256": hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()}))
        return run

    def test_audit_preserves_all_original_files_and_uses_no_api(self):
        from agent.evidence import file_hashes
        run = self.prepare()
        before = file_hashes(run)
        with patch("agent.provider.ChatClient.ask_json", side_effect=AssertionError("No API allowed")):
            report = audit_run(run, self.root / "audit")
        self.assertEqual(file_hashes(run), before)
        self.assertTrue(report["original_run_unchanged"])
        self.assertEqual(report["browser_manifests_audited"], 1)
        self.assertEqual(len(report["records"][0]["controlled_probes"]), 5)
        self.assertTrue(report["records"][0]["game_hash_matches"])

    def test_no_manifest_means_not_verified(self):
        report = audit_run(self.prepare(False), self.root / "audit")
        self.assertEqual(report["coverage_status"], "not_verified_no_browser_manifests")

    def test_original_or_existing_output_cannot_be_overwritten(self):
        run = self.prepare()
        for target in (run, run / "nested", self.root):
            with self.subTest(target=target), self.assertRaises(ValueError):
                audit_run(run, target)

    def test_empty_key_prevents_live_request(self):
        from test_mvp import config
        from dataclasses import replace
        with patch("evals.step_evidence.load_dotenv"), patch("evals.step_evidence.Config.from_env",
                return_value=replace(config(), api_key="")), patch("agent.runner.run") as runner:
            with self.assertRaises(ValueError):
                live(self.root / "live")
            runner.assert_not_called()

    def test_live_pilot_budget_cannot_expand_silently(self):
        from test_mvp import config
        from dataclasses import replace
        cfg = replace(config(), base_url="https://openrouter.ai/api/v1")
        with patch("evals.step_evidence.load_dotenv"), patch("evals.step_evidence.Config.from_env", return_value=cfg):
            with self.assertRaises(ValueError):
                live(self.root / "live", max_calls=6)

    def test_live_wrapper_preserves_nonpass_and_records_no_key(self):
        from test_mvp import config
        from dataclasses import replace
        cfg = replace(config(), base_url="https://openrouter.ai/api/v1")
        def runner(config, spec, output, **options):
            output.mkdir()
            (output / "summary.json").write_text(json.dumps({"status": "generation_failed", "usage": {"api_attempts": 0}}))
            return 2
        destination = self.root / "live"
        with patch("evals.step_evidence.load_dotenv"), patch("evals.step_evidence.Config.from_env", return_value=cfg), \
                patch("agent.runner.run", side_effect=runner):
            self.assertEqual(live(destination), 2)
        self.assertNotIn(cfg.api_key, (destination / "EXPERIMENT.json").read_text())
        report = json.loads((destination / "audit/AUDIT.json").read_text())
        self.assertEqual(report["coverage_status"], "not_verified_no_browser_manifests")


@unittest.skipUnless(os.getenv("MVP_BROWSER_TESTS") == "1", "Real-browser calibration, zero model API")
class StepAuditBrowserTests(TempTest):
    def test_real_browser_trace_and_corrupted_copies_are_distinguished(self):
        game = self.root / "game"
        write_bundle(example_bundle(), game)
        plan = example_plan()
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(validate_plan(plan)))
        result = verify(game, plan_path, self.root / "evidence", timeout=30)
        self.assertTrue(result["ok"], result)
        audit = audit_result(plan, result)
        self.assertTrue(audit["step_supported_overall_pass"], audit)
        matrix = mutation_matrix(plan, result)
        self.assertEqual(len(matrix["cases"]), 5)
        self.assertTrue(all(c["detected"] for c in matrix["cases"]))
        # Optional evidence export is explicitly a zero-API calibration fixture, not an Agent-generated game.
        if os.getenv("D_CALIBRATION_EXPORT"):
            export = Path(os.environ["D_CALIBRATION_EXPORT"]).resolve()
            shutil.copytree(self.root, export)
            (export / "AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2))
            (export / "CONTROLLED_RECORD_PROBES.json").write_text(json.dumps(matrix, ensure_ascii=False, indent=2))
            (export / "CALIBRATION_KIND.txt").write_text(
                "Synthetic counter fixture + real Chromium. Zero model API calls. "
                "Controlled record mutations are NOT real model failures or S1-S5 results.\n")

    def test_real_capture_sample_consistency_stability_and_goal_evidence(self):
        game = self.root / "game"
        extra = '''const label=document.createElement('span');label.id='count';label.textContent='0';
document.body.appendChild(label);const old=document.querySelector('#increment').onclick;
document.querySelector('#increment').onclick=()=>{old();label.textContent=String(score)};'''
        write_bundle(example_bundle(extra=extra), game)
        plan = example_plan()
        plan["tests"][0]["steps"] = [
            {"action": "capture", "name": "before"},
            {"action": "click", "selector": "#increment"},
            {"action": "assert", "source": "state", "path": "score", "op": "gt",
             "value_from": {"capture": "before", "path": "score"}},
            {"action": "sample", "name": "after", "samples": 3, "duration_ms": 100},
            {"action": "assert", "source": "state", "path": "score", "op": "eq",
             "value_from": {"capture": "after_end", "path": "score"}},
            {"action": "assert_consistent", "source": "text", "selector": "#count",
             "state_path": "score", "coerce": "number"},
            {"action": "assert_stable", "source": "state", "path": "score", "samples": 3, "duration_ms": 100},
            {"action": "wait_until", "timeout_ms": 500,
             "until": {"source": "state", "path": "score", "op": "eq", "value": 1}}]
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(validate_plan(plan)))
        result = verify(game, plan_path, self.root / "evidence", timeout=30)
        self.assertTrue(result["ok"], result)
        self.assertTrue(audit_result(plan, result)["step_supported_overall_pass"])

    def test_real_browser_failed_interaction_remains_nonpass(self):
        game = self.root / "game"
        write_bundle(example_bundle(), game)
        plan = example_plan()
        plan["tests"][0]["steps"][1]["selector"] = "#does_not_exist"
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(validate_plan(plan)))
        result = verify(game, plan_path, self.root / "evidence", timeout=30)
        self.assertFalse(result["ok"])
        audit = audit_result(plan, result)
        self.assertFalse(audit["step_supported_overall_pass"])
        self.assertEqual(audit["tests"][0]["verdict"], "recorded_nonpass")


if __name__ == "__main__":
    unittest.main()
