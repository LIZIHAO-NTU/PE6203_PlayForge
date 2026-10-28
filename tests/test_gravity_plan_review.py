"""Pre-freeze checks use only explicit rules and a draft plan, never game code."""
from copy import deepcopy
import json
import unittest

from agent.gravity_plan_review import (gravity_plan_conflicts, gravity_reference_paths,
                                       repair_explicit_gravity_draw_plan)
from agent.runner import run
from test_mvp import TempTest, FakeClient, config, example_bundle, example_plan, verifier_result


SPEC = """An offline two-player game. The board has 3 columns and 3 rows. Rows are
numbered 0–2 from top to bottom; columns 0–2 from left to right. All cells
start empty. Player A starts. Show a legal-move count starting at 0 and status
Playing. A player chooses one column per turn. Their A or B token goes into the
lowest empty cell in that column. The turn passes to the other player unless
that move ends the game. Clicking a full column is invalid and changes nothing.
After a valid drop, check for three tokens in a contiguous horizontal,
vertical, or diagonal line. Status becomes exactly Winner: A or Winner: B.
A win takes precedence over a draw on the last available cell. If the board
fills and neither player has a three-token line, status becomes exactly Draw.
During a finished game every column click is ignored. Restart clears the board
and returns the turn to A, move count to 0, status to Playing.
Controls have IDs drop-0 through drop-2 and restart. Cells have IDs
cell-ROW-COLUMN. Text readouts have IDs turn, moves, status.
"""
FOUR_COLUMN_SPEC = (SPEC.replace("3 columns and 3 rows", "4 columns and 3 rows")
                    .replace("columns 0–2", "columns 0–3")
                    .replace("drop-0 through drop-2", "drop-0 through drop-3"))


def clicks(*columns):
    return [{"action": "click", "selector": f"#drop-{column}"} for column in columns]


def assertion(selector, value, op="eq"):
    return {"action": "assert", "source": "text", "selector": selector,
            "op": op, "value": value}


class GravityPlanReviewTests(unittest.TestCase):
    def test_reference_paths_are_derived_from_explicit_rules(self):
        paths = gravity_reference_paths(FOUR_COLUMN_SPEC)
        self.assertEqual(len(paths["draw"]["columns"]), 12)
        self.assertEqual(paths["draw"]["result"], "Draw")
        for kind in ("horizontal", "vertical", "diagonal"):
            self.assertIn(kind, paths)
            self.assertIn(paths[kind]["result"], {"Winner: A", "Winner: B"})
            self.assertLessEqual(len(paths[kind]["columns"]), 12)
        self.assertEqual(gravity_reference_paths("A board game with unclear rules."), {})

    def test_alternating_stack_rejects_wrong_top_token(self):
        draft = {"tests": [{"id": "T1", "setup_steps": clicks(0, 0, 0),
                            "steps": [assertion("#cell-0-0", "B")]}]}
        original = deepcopy(draft)
        conflicts = gravity_plan_conflicts(draft, SPEC)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["test_id"], "T1")
        self.assertEqual(conflicts[0]["actual_from_spec"], "A")
        self.assertEqual(draft, original)

    def test_early_win_rejects_impossible_draw_path(self):
        draft = {"tests": [{"id": "T2", "steps": clicks(0, 1, 0, 1, 0, 2, 2, 2, 1)
                            + [assertion("#moves", "9"), assertion("#status", "Draw")]}]}
        conflicts = gravity_plan_conflicts(draft, SPEC)
        self.assertEqual(conflicts[0]["actual_from_spec"], "5")
        self.assertEqual(conflicts[0]["expected"], "9")

    def test_valid_restart_and_final_win_pass(self):
        draft = {"tests": [{"id": "T3", "steps": clicks(0, 1, 0, 1, 0)
                            + [assertion("#status", "Winner: A"),
                               {"action": "click", "selector": "#restart"},
                               assertion("#moves", "0"), assertion("#turn", "A")]}]}
        self.assertEqual(gravity_plan_conflicts(draft, SPEC), [])

    def test_abstains_when_rules_are_incomplete_or_actions_unknown(self):
        draft = {"tests": [{"id": "T4", "steps": clicks(0) + [assertion("#turn", "A")]}]}
        self.assertEqual(gravity_plan_conflicts(draft, "A 3 by 3 board with tokens."), [])
        draft["tests"][0]["steps"].insert(0, {"action": "key", "key": "Space"})
        self.assertEqual(gravity_plan_conflicts(draft, SPEC), [])

    def test_markdown_emphasis_does_not_hide_explicit_rules(self):
        draft = {"tests": [{"id": "T5", "steps": clicks(0, 0, 0)
                            + [assertion("#cell-0-0", "B")]}]}
        emphasized = SPEC.replace("Player A starts", "Player **A** starts")
        self.assertEqual(gravity_plan_conflicts(draft, emphasized)[0]["actual_from_spec"], "A")

    def test_draw_requirement_cannot_be_relabelled_as_win(self):
        draft = {"requirements": [{"id": "RDraw", "verification": "automated",
                                   "text": "A full board without a winning line must show Draw."}],
                 "tests": [{"id": "TDraw", "requirement_ids": ["RDraw"],
                            "steps": clicks(0, 1, 0, 1, 0)
                            + [assertion("#status", "Winner: A")]}]}
        conflicts = gravity_plan_conflicts(draft, SPEC)
        self.assertTrue(any(item["kind"] == "missing_gravity_draw_coverage" for item in conflicts))
        self.assertEqual(conflicts[-1]["requirement_id"], "RDraw")
        self.assertEqual(conflicts[-1]["test_id"], "TDraw")

    def test_win_precedence_word_draw_does_not_require_draw_scenario(self):
        draft = {"requirements": [{"id": "RWin", "verification": "automated",
                                   "text": "A winning move takes precedence over Draw."}],
                 "tests": [{"id": "TWin", "requirement_ids": ["RWin"],
                            "steps": clicks(0, 1, 0, 1, 0)
                            + [assertion("#status", "Winner: A")]}]}
        self.assertEqual(gravity_plan_conflicts(draft, SPEC), [])

    def test_wrong_draw_path_is_replaced_only_before_freeze(self):
        draft = {"requirements": [{"id": "RDraw", "verification": "automated",
                                   "text": "A full board without a winning line must show Draw."}],
                 "tests": [{"id": "TDraw", "requirement_ids": ["RDraw"],
                            "steps": clicks(0, 1, 0, 1, 1, 0, 1, 0, 2, 3, 2, 3)
                            + [assertion("#moves", "12"), assertion("#status", "Draw")]}]}
        original = deepcopy(draft)
        corrected, changes = repair_explicit_gravity_draw_plan(draft, FOUR_COLUMN_SPEC)
        self.assertEqual(draft, original)
        self.assertEqual(len(changes), 1)
        self.assertEqual(gravity_plan_conflicts(corrected, FOUR_COLUMN_SPEC), [])
        self.assertEqual(len([step for step in corrected["tests"][0]["steps"]
                              if step["action"] == "click"]), 12)

    def test_draw_repair_abstains_on_interleaved_assertions(self):
        draft = {"tests": [{"id": "TDraw", "steps": clicks(0, 1)
                            + [assertion("#cell-2-0", "A")]
                            + clicks(0, 1, 1, 0, 1, 0, 2, 3, 2, 3)
                            + [assertion("#status", "Draw")]}]}
        self.assertEqual(repair_explicit_gravity_draw_plan(draft, FOUR_COLUMN_SPEC),
                         (draft, []))

    def test_declared_row_major_board_index_is_checked(self):
        draft = {"state_contract": {"board": "array of 12 strings (row-major row 0..2, col 0..3)"},
                 "tests": [{"id": "TBoard", "steps": clicks(0, 1, 0, 1, 0)
                            + [{"action": "assert", "source": "state", "path": "board.2",
                                "op": "eq", "value": "A"}]}]}
        conflicts = gravity_plan_conflicts(draft, FOUR_COLUMN_SPEC)
        self.assertEqual(conflicts[0]["actual_from_spec"], "")
        draft["tests"][0]["steps"][-1]["path"] = "board.8"
        self.assertEqual(gravity_plan_conflicts(draft, FOUR_COLUMN_SPEC), [])

    def test_declared_state_move_count_catches_win_before_later_click(self):
        draft = {"state_contract": {"moves": "number of legal drops so far"},
                 "tests": [{"id": "T4", "setup_steps": clicks(0, 1, 1, 2, 3, 2, 2, 3),
                            "steps": [{"action": "assert", "source": "state", "path": "moves",
                                       "op": "eq", "value": 8}]}]}
        conflicts = gravity_plan_conflicts(draft, FOUR_COLUMN_SPEC)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["actual_from_spec"], 7)
        self.assertEqual(conflicts[0]["test_id"], "T4")
        draft["tests"][0]["steps"][0]["value"] = 7
        self.assertEqual(gravity_plan_conflicts(draft, FOUR_COLUMN_SPEC), [])

    def test_ambiguous_state_move_field_is_not_assumed_legal_count(self):
        draft = {"state_contract": {"moves": "animation frame count"},
                 "tests": [{"id": "T", "steps": clicks(0) +
                            [{"action": "assert", "source": "state", "path": "moves",
                              "op": "eq", "value": 99}]}]}
        self.assertEqual(gravity_plan_conflicts(draft, FOUR_COLUMN_SPEC), [])


class GravityRunnerTests(TempTest):
    def test_sequential_plan_errors_get_third_attempt_when_budget_allows(self):
        spec_path = self.root / "spec.md"
        spec_path.write_text(FOUR_COLUMN_SPEC, encoding="utf-8")
        missing = example_plan()
        missing["requirements"].append({"id": "R2", "text": "Counter is visible", "verification": "automated"})
        oversized = example_plan()
        oversized["tests"][0]["steps"] = ([{"action": "click", "selector": "#increment"}] * 18
                                           + [oversized["tests"][0]["steps"][-1]])
        valid = example_plan()
        stages = []
        prompts = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                stages.append(stage)
                prompts.append(json.loads(prompt))
                if stage == "plan":
                    return deepcopy((missing, oversized, valid)[stages.count("plan") - 1])
                return example_bundle()

        out = self.root / "run"
        code = run(config(), spec_path, out, client_factory=Client,
                   preflight_fn=lambda **kw: {"ok": True},
                   verifier=lambda *a, **kw: verifier_result(True), max_calls=5, strict_plan=True)
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0, summary)
        self.assertEqual(stages, ["plan", "plan", "plan", "code_1"])
        self.assertIn("missing IDs: R2", prompts[1]["validation_feedback"])
        self.assertIn("1..18 steps/test", prompts[2]["validation_feedback"])

    def test_exhausted_invalid_plans_are_reported_as_review_not_runtime_error(self):
        spec_path = self.root / "spec.md"
        spec_path.write_text(FOUR_COLUMN_SPEC, encoding="utf-8")
        invalid = example_plan()
        invalid["requirements"].append({"id": "R2", "text": "Counter is visible", "verification": "automated"})
        stages = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                stages.append(stage)
                return deepcopy(invalid)

        out = self.root / "run"
        code = run(config(), spec_path, out, client_factory=Client,
                   preflight_fn=lambda **kw: {"ok": True}, max_calls=5, strict_plan=True)
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 2)
        self.assertEqual(stages, ["plan", "plan", "plan"])
        self.assertEqual(summary["status"], "plan_review_required")
        self.assertFalse((out / "game").exists())

    def test_last_attempt_rebuilds_conflicting_sequences_without_losing_requirements(self):
        spec_path = self.root / "spec.md"
        spec_path.write_text(SPEC, encoding="utf-8")
        bad = example_plan()
        bad["tests"][0]["steps"] = clicks(0, 0, 0) + [assertion("#cell-0-0", "B")]
        good = deepcopy(bad)
        good["tests"][0]["steps"][-1]["value"] = "A"
        prompts = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                if stage == "plan":
                    prompts.append(json.loads(prompt))
                    return deepcopy(bad if len(prompts) < 3 else good)
                return example_bundle()

        out = self.root / "run"
        code = run(config(), spec_path, out, client_factory=Client,
                   preflight_fn=lambda **kw: {"ok": True},
                   verifier=lambda *a, **kw: verifier_result(True), max_calls=5, strict_plan=True)
        self.assertEqual(code, 0)
        self.assertEqual(len(prompts), 3)
        self.assertNotIn("tests", prompts[2]["previous_plan"])
        self.assertEqual(prompts[2]["previous_plan"]["requirements"], bad["requirements"])
        self.assertIn("rebuild", prompts[2]["planning_recovery_strategy"].lower())
        self.assertEqual(prompts[0]["verified_gravity_scenarios"]["draw"]["result"], "Draw")

    def test_pure_draw_path_is_corrected_before_freeze(self):
        spec_path = self.root / "spec.md"
        spec_path.write_text(FOUR_COLUMN_SPEC, encoding="utf-8")
        bad = example_plan()
        bad["requirements"][0]["text"] = "A full board without a winning line must show Draw."
        bad["tests"][0]["steps"] = (clicks(0, 1, 0, 1, 1, 0, 1, 0, 2, 3, 2, 3)
                                     + [assertion("#moves", "12"), assertion("#status", "Draw")])
        stages = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                stages.append(stage)
                return deepcopy(bad) if stage == "plan" else example_bundle()

        out = self.root / "run"
        code = run(config(), spec_path, out, client_factory=Client,
                   preflight_fn=lambda **kw: {"ok": True},
                   verifier=lambda *a, **kw: verifier_result(True), max_calls=3)
        self.assertEqual(code, 0)
        self.assertEqual(stages, ["plan", "code_1"])
        self.assertTrue((out / "traces/draft_gravity_plan.json").is_file())
        self.assertTrue((out / "traces/gravity_plan_corrections.json").is_file())
        frozen = json.loads((out / "traces/plan.json").read_text(encoding="utf-8"))
        self.assertEqual(gravity_plan_conflicts(frozen, FOUR_COLUMN_SPEC), [])

    def test_conflict_is_returned_to_planner_before_code_exists(self):
        spec_path = self.root / "spec.md"
        spec_path.write_text(SPEC, encoding="utf-8")
        bad = example_plan()
        bad["tests"][0]["steps"] = clicks(0, 0, 0) + [assertion("#cell-0-0", "B")]
        good = deepcopy(bad)
        good["tests"][0]["steps"][-1]["value"] = "A"
        stages = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                stages.append(stage)
                if stage == "plan":
                    return deepcopy(bad if stages.count("plan") == 1 else good)
                return example_bundle()

        out = self.root / "run"
        code = run(config(), spec_path, out, client_factory=Client,
                   preflight_fn=lambda **kw: {"ok": True},
                   verifier=lambda *a, **kw: verifier_result(True), max_calls=3)
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0, summary)
        self.assertEqual(stages, ["plan", "plan", "code_1"])
        self.assertEqual(summary["planning_status"], "valid")
        self.assertEqual(json.loads((out / "traces/plan.json").read_text(encoding="utf-8"))
                         ["tests"][0]["steps"][-1]["value"], "A")
        self.assertTrue((out / "traces/plan.json").is_file())

    def test_repeated_conflict_stops_before_code_generation(self):
        spec_path = self.root / "spec.md"
        spec_path.write_text(SPEC, encoding="utf-8")
        bad = example_plan()
        bad["tests"][0]["steps"] = clicks(0, 0, 0) + [assertion("#cell-0-0", "B")]
        stages = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                stages.append(stage)
                return deepcopy(bad)

        out = self.root / "run"
        code = run(config(), spec_path, out, client_factory=Client,
                   preflight_fn=lambda **kw: {"ok": True}, max_calls=3)
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        self.assertNotEqual(code, 0)
        self.assertEqual(stages, ["plan", "plan"])
        self.assertEqual(summary["status"], "plan_review_required")
        self.assertFalse((out / "traces/plan.json").exists())

    def test_model_audit_cannot_reintroduce_rule_conflict(self):
        spec_path = self.root / "spec.md"
        spec_path.write_text(SPEC, encoding="utf-8")
        good = example_plan()
        good["tests"][0]["steps"] = clicks(0, 0, 0) + [assertion("#cell-0-0", "A")]
        bad = deepcopy(good)
        bad["tests"][0]["steps"][-1]["value"] = "B"
        stages = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                stages.append(stage)
                if stage == "plan":
                    return deepcopy(good)
                if stage == "plan_audit":
                    return {"status": "revised", "reason": "incorrect revision",
                            "issues": [{"test_id": "T1", "reason": "wrongly changed literal",
                                        "spec_evidence": "Player A starts"}], "plan": deepcopy(bad)}
                return example_bundle()

        out = self.root / "run"
        code = run(config(), spec_path, out, client_factory=Client, plan_audit=True,
                   preflight_fn=lambda **kw: {"ok": True},
                   verifier=lambda *a, **kw: verifier_result(True), max_calls=3)
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        self.assertNotEqual(code, 0)
        self.assertEqual(stages, ["plan", "plan_audit"])
        self.assertEqual(summary["status"], "plan_review_required")
        self.assertFalse((out / "traces/plan.json").exists())


if __name__ == "__main__":
    unittest.main()
