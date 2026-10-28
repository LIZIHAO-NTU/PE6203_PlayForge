import unittest

from agent.plan_review import (inspect_plan, normalize_explicit_grid_plan,
                               require_explicit_grid_consistency, validate_audit)


SPEC = """Use a 5x5 grid with x increasing right and y increasing down.
Every outer cell (x=0/4 or y=0/4) is a wall. All nine inner cells are floor.
Initial player=(1,2), crate=(2,2), goal=(3,2).
Arrow keys move one cell per key press. Blocked actions do not increase moves.
A crate reaching the goal wins; after winning, arrows cannot change state.
#restart restores the exact initial state.
"""


def plan(*steps):
    return {"tests": [{"id": "T1", "purpose": "terminal", "steps": list(steps)}]}


def key(value):
    return {"action": "key", "key": value}


def expect(path, value):
    return {"action": "assert", "source": "state", "path": path, "op": "eq", "value": value}


class ExplicitGridReviewTest(unittest.TestCase):
    def test_rejects_assertion_after_winning_push(self):
        draft = plan(key("ArrowRight"), key("ArrowUp"), expect("player.y", 1))
        warnings = inspect_plan(draft, SPEC)["warnings"]
        self.assertTrue(any(w["kind"] == "explicit_grid_transition_conflict" for w in warnings))

    def test_accepts_correct_terminal_lock(self):
        draft = plan(key("ArrowRight"), key("ArrowUp"), expect("player.y", 2),
                     expect("crate.x", 3), expect("moves", 1))
        warnings = inspect_plan(draft, SPEC)["warnings"]
        self.assertFalse(any(w["kind"] == "explicit_grid_transition_conflict" for w in warnings))

    def test_approved_audit_cannot_ignore_deterministic_conflict(self):
        draft = plan(key("ArrowRight"), key("ArrowUp"), expect("player.y", 1))
        warnings = inspect_plan(draft, SPEC)["warnings"]
        with self.assertRaisesRegex(ValueError, "unresolved deterministic"):
            validate_audit({"status": "approved", "reason": "looks fine", "issues": []},
                           draft, required_warnings=warnings)

    def test_planning_retry_receives_conflict_before_freeze(self):
        draft = plan(key("ArrowRight"), key("ArrowUp"), expect("player.y", 1))
        with self.assertRaisesRegex(ValueError, "T1.*step 3"):
            require_explicit_grid_consistency(draft, SPEC)
        require_explicit_grid_consistency(
            plan(key("ArrowRight"), key("ArrowUp"), expect("player.y", 2)), SPEC)

    def test_corrects_only_explicit_grid_expectations_before_freeze(self):
        draft = plan(key("ArrowRight"), key("ArrowUp"), expect("player.y", 1),
                     expect("crate.x", 2), expect("moves", 2))
        corrected, changes = normalize_explicit_grid_plan(draft, SPEC)
        self.assertEqual([step["value"] for step in corrected["tests"][0]["steps"][-3:]],
                         [2, 3, 1])
        self.assertEqual(len(changes), 3)
        self.assertEqual(draft["tests"][0]["steps"][-3]["value"], 1)
        self.assertFalse(inspect_plan(corrected, SPEC)["warnings"])


if __name__ == "__main__":
    unittest.main()
