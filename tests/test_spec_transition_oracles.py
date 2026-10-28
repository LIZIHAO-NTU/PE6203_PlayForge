"""The spec, not a generated game, determines pre-freeze literal corrections."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from agent.contracts import validate_plan
from agent.runner import run
from agent.spec_oracles import normalize_explicit_portal_plan, normalize_explicit_charge_craft_plan
from test_mvp import TempTest, FakeClient, config, example_bundle, example_plan, verifier_result


ROOT = Path(__file__).resolve().parents[1]


def plan_with_steps(steps):
    plan = example_plan()
    plan["tests"][0]["steps"] = steps
    plan["state_contract"] = {step["path"]: "Actual game state" for step in steps
                              if step.get("source") == "state" and "path" in step}
    return plan


class SpecTransitionOracleTests(unittest.TestCase):
    def test_portal_replays_teleport_before_assertion(self):
        spec = (ROOT / "examples/reliability_20261016/portal_grid.md").read_text(encoding="utf-8")
        original = plan_with_steps([
            {"action": "key", "key": "ArrowRight", "hold_ms": 0},
            {"action": "assert", "source": "state", "path": "player.x", "op": "eq", "value": 1},
            {"action": "assert", "source": "state", "path": "player.y", "op": "eq", "value": 0},
            {"action": "assert", "source": "state", "path": "moves", "op": "eq", "value": 1},
        ])
        unchanged = deepcopy(original)
        corrected, changes = normalize_explicit_portal_plan(original, spec)
        self.assertEqual(original, unchanged)
        self.assertEqual([item["after"] for item in changes], [3])
        self.assertEqual(corrected["tests"][0]["steps"][1]["value"], 3)
        validate_plan(corrected)

    def test_portal_abstains_when_walls_or_teleport_rules_are_not_explicit(self):
        spec = "A 4-column, 3-row board. Start the player at (0,1). There are walls and portals."
        plan = plan_with_steps([{"action": "key", "key": "ArrowRight", "hold_ms": 0},
                                {"action": "assert", "source": "state", "path": "player.x", "op": "eq", "value": 1}])
        self.assertEqual(normalize_explicit_portal_plan(plan, spec), (plan, []))

    def test_portal_abstains_when_literal_expectations_are_independently_recorded(self):
        spec = (ROOT / "examples/reliability_20261016/portal_grid.md").read_text(encoding="utf-8")
        plan = plan_with_steps([
            {"action": "key", "key": "ArrowRight", "hold_ms": 0},
            {"action": "assert", "source": "state", "path": "player.x", "op": "eq", "value": 1},
        ])
        plan["tests"][0]["evidence"] = {"expected_observations": [{"value": 1}]}
        self.assertEqual(normalize_explicit_portal_plan(plan, spec), (plan, []))

    def test_charge_craft_replays_cap_and_terminal_lock(self):
        spec = (ROOT / "examples/reliability_20261016/charge_exchange.md").read_text(encoding="utf-8")
        original = plan_with_steps([
            {"action": "click", "selector": "#craft"},
            {"action": "click", "selector": "#charge"},
            {"action": "click", "selector": "#craft"},
            {"action": "click", "selector": "#charge"},
            {"action": "click", "selector": "#craft"},
            {"action": "assert", "source": "state", "path": "energy", "op": "eq", "value": 1},
            {"action": "assert", "source": "state", "path": "phase", "op": "eq", "value": "Won"},
            {"action": "click", "selector": "#charge"},
            {"action": "assert", "source": "state", "path": "energy", "op": "eq", "value": 3},
        ])
        corrected, changes = normalize_explicit_charge_craft_plan(original, spec)
        self.assertEqual([item["after"] for item in changes], [2, 2])
        self.assertEqual(original["tests"][0]["steps"][5]["value"], 1)
        validate_plan(corrected)

    def test_charge_craft_abstains_without_cost_or_terminal_rule(self):
        plan = plan_with_steps([{"action": "click", "selector": "#charge"},
                                {"action": "assert", "source": "state", "path": "energy", "op": "eq", "value": 9}])
        corrected, changes = normalize_explicit_charge_craft_plan(plan, "Charge adds two energy.")
        self.assertEqual(changes, [])
        self.assertEqual(corrected, plan)


class RunnerSpecOracleTests(TempTest):
    def test_portal_correction_is_frozen_before_code_generation(self):
        spec = self.root / "spec.md"
        spec.write_text((ROOT / "examples/reliability_20261016/portal_grid.md").read_text(encoding="utf-8"), encoding="utf-8")
        draft = plan_with_steps([
            {"action": "key", "key": "ArrowRight", "hold_ms": 0},
            {"action": "assert", "source": "state", "path": "player.x", "op": "eq", "value": 1},
        ])
        calls = []

        class Client(FakeClient):
            def ask_json(self, stage, system, prompt):
                self.calls += 1
                calls.append(stage)
                return deepcopy(draft) if stage == "plan" else example_bundle(working=True)

        output = self.root / "run"
        run(config(), spec, output, client_factory=Client,
            verifier=lambda *args, **kwargs: verifier_result(True),
            preflight_fn=lambda **kwargs: {"ok": True}, max_calls=3)
        frozen = json.loads((output / "traces/plan.json").read_text(encoding="utf-8"))
        self.assertEqual(calls, ["plan", "code_1"])
        self.assertEqual(frozen["tests"][0]["steps"][1]["value"], 3)
        self.assertEqual(draft["tests"][0]["steps"][1]["value"], 1)


if __name__ == "__main__":
    unittest.main()
