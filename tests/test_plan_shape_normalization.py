"""Pre-freeze plan shape recovery must preserve the model's actual gameplay claims."""
from copy import deepcopy
import json

from agent.runner import run
from agent.prompts import planner_system
from test_mvp import TempTest, FakeClient, config, example_plan, example_bundle, verifier_result


def split_gameplay_plan():
    plan = example_plan()
    plan["gameplay"] = {"invariants": ["A click increments the counter exactly once."]}
    plan["interaction_model"] = "turn_based"
    plan["input_mode"] = "pointer"
    plan["core_loop"] = "Click the counter button and observe the increment."
    return plan


class PlanShapeNormalizationTests(TempTest):
    def test_planner_example_shows_nested_gameplay_fields(self):
        example = planner_system().split("Example JSON structure", 1)[1]
        self.assertIn('"gameplay":{"interaction_model":"turn_based","input_mode":"pointer",', example)

    def test_flat_gameplay_fields_are_canonicalized_before_freeze_without_an_extra_call(self):
        draft = split_gameplay_plan()
        calls = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                calls.append(stage)
                return deepcopy(draft) if stage == "plan" else example_bundle(working=True)

        spec = self.root / "spec.md"
        spec.write_text("A click increments the counter exactly once.", encoding="utf-8")
        output = self.root / "run"
        code = run(config(), spec, output, client_factory=Client,
                   verifier=lambda *a, **kw: verifier_result(True),
                   preflight_fn=lambda **kw: {"ok": True}, max_calls=3)
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        frozen = json.loads((output / "traces/plan.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0, summary)
        self.assertEqual(calls, ["plan", "code_1"])
        self.assertEqual(summary["planning_status"], "valid")
        self.assertEqual(frozen["gameplay"], {
            "interaction_model": "turn_based", "input_mode": "pointer",
            "core_loop": "Click the counter button and observe the increment.",
            "invariants": ["A click increments the counter exactly once."]})
        self.assertEqual(draft["gameplay"], {"invariants": ["A click increments the counter exactly once."]})

    def test_conflicting_nested_and_top_level_gameplay_are_not_silently_overridden(self):
        from agent.planning import canonicalize_gameplay_shape

        draft = split_gameplay_plan()
        draft["gameplay"]["interaction_model"] = "real_time"
        try:
            canonicalize_gameplay_shape(draft)
        except ValueError as error:
            self.assertIn("Conflicting gameplay", str(error))
        else:
            self.fail("Conflicting gameplay fields must remain invalid")
