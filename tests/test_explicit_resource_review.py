import unittest

from agent.plan_review import (explicit_resource_transition_warnings,
                               normalize_explicit_resource_plan)


SPEC = """Initial coins=10, power=1, phase=Playing. #coins and #power show bare integers;
#status shows Playing or Won exactly.
#earn adds exactly 1 coin per click while Playing.
#buy costs exactly 6 coins and adds exactly 1 power only if coins>=6 and phase=Playing.
Insufficient coins: ignore the purchase without changing any value.
Reach power=3 to win immediately. After Won, earn and buy clicks do nothing.
#restart restores coins=10, power=1, phase=Playing and works in every phase.
"""


def click(selector):
    return {"action": "click", "selector": selector}


def expect(path, value):
    return {"action": "assert", "source": "state", "path": path, "op": "eq", "value": value}


class ExplicitResourceReviewTest(unittest.TestCase):
    def test_two_buys_do_not_win_without_more_coins(self):
        plan = {"tests": [{"id": "T1", "steps": [click("#buy"), click("#buy"), expect("power", 3)]}]}
        warnings = explicit_resource_transition_warnings(plan, SPEC)
        self.assertEqual(warnings[0]["actual_from_spec"], 2)

    def test_normalizer_rewrites_only_wrong_literals(self):
        plan = {"tests": [{"id": "T1", "steps": [click("#buy"), click("#buy"), expect("power", 3)]}]}
        fixed, changes = normalize_explicit_resource_plan(plan, SPEC)
        self.assertEqual(fixed["tests"][0]["steps"][-1]["value"], 2)
        self.assertEqual(len(changes), 1)
        self.assertEqual(plan["tests"][0]["steps"][-1]["value"], 3)

    def test_illegal_fill_on_output_label_needs_revision(self):
        plan = {"tests": [{"id": "T1", "steps": [
            {"action": "fill", "selector": "#coins", "text": "10"}, expect("coins", 10)]}]}
        warnings = explicit_resource_transition_warnings(plan, SPEC)
        self.assertEqual(warnings[0]["kind"], "explicit_resource_invalid_action")

    def test_read_only_capture_does_not_hide_bad_terminal_expectation(self):
        plan = {"tests": [{"id": "T1", "steps": [
            click("#buy"), click("#buy"), expect("power", 3),
            {"action": "capture", "name": "before"}, expect("phase", "Won")]}]}
        warnings = explicit_resource_transition_warnings(plan, SPEC)
        self.assertEqual(warnings[0]["kind"], "explicit_resource_transition_conflict")

    def test_capture_reference_after_earn_cannot_claim_terminal_lock(self):
        plan = {"tests": [{"id": "T1", "steps": [
            click("#buy"), click("#buy"),
            {"action": "capture", "name": "before"}, click("#earn"),
            {"action": "assert", "source": "state", "path": "coins", "op": "eq",
             "value_from": {"capture": "before", "path": "coins"}}]}]}
        warnings = explicit_resource_transition_warnings(plan, SPEC)
        self.assertEqual(warnings[0]["kind"], "explicit_resource_reference_conflict")


if __name__ == "__main__":
    unittest.main()
