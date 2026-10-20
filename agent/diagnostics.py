"""Evidence-based routing. A test failure is not a proven root cause."""
from decimal import Decimal, InvalidOperation
import json

from .contracts import test_steps


def _same_expected_value(left, right):
    # A state contract may intentionally expose strings. Do not equate two
    # different string literals merely because both parse as numbers.
    if isinstance(left, str) and isinstance(right, str):
        return left == right
    if str(left) == str(right):
        return True
    try:
        return Decimal(str(left)) == Decimal(str(right))
    except InvalidOperation:
        return False


def _same_state_expected(left, right):
    if type(left) is str or type(right) is str:
        return type(left) is str and type(right) is str and left == right
    return _same_expected_value(left, right)


def conflicting_state_expectations(result, plan):
    """Find disagreeing same-path state assertions within one action-free segment."""
    if not isinstance(plan, dict):
        return []
    tests = {test.get("id"): test for test in plan.get("tests", []) if isinstance(test, dict)}
    signals = []
    for failure in result.get("tests", []):
        if failure.get("passed") is True or failure.get("failure_kind") != "assertion_mismatch":
            continue
        test = tests.get(failure.get("id"))
        if not test:
            continue
        steps = test_steps(test)
        index = failure.get("failed_step")
        if type(index) is not int or not 1 <= index <= len(steps):
            continue
        failed = steps[index - 1]
        if (failed.get("action") != "assert" or failed.get("source") != "state"
                or failed.get("op") != "eq" or type(failed.get("value")) not in {int, float, str}):
            continue
        for direction in (-1, 1):
            other_index = index - 1 + direction
            while 0 <= other_index < len(steps):
                other = steps[other_index]
                if other.get("action") != "assert":
                    break
                if (other.get("source") == "state" and other.get("op") == "eq"
                        and other.get("path") == failed.get("path")
                        and type(other.get("value")) in {int, float, str}
                        and not _same_state_expected(failed["value"], other["value"])):
                    signals.append({"test_id": failure["id"], "path": failed["path"],
                                    "failed_step": index, "other_step": other_index + 1,
                                    "failed_expected": failed["value"],
                                    "other_expected": other["value"]})
                    break
                other_index += direction
    return signals


def conflicting_display_expectations(result, plan):
    """Locate an adjacent state/DOM disagreement, without inferring the true value."""
    if not isinstance(plan, dict):
        return []
    tests = {test.get("id"): test for test in plan.get("tests", []) if isinstance(test, dict)}
    signals = []
    for failure in result.get("tests", []):
        if failure.get("passed") is True or failure.get("failure_kind") != "assertion_mismatch":
            continue
        test = tests.get(failure.get("id"))
        if not test:
            continue
        steps = test_steps(test)
        index = failure.get("failed_step")
        if type(index) is not int or not 1 <= index <= len(steps):
            continue
        for start in (index - 1, index):
            if not 1 <= start < len(steps):
                continue
            first, second = steps[start - 1:start + 1]
            state, display = (first, second) if first.get("source") == "state" else (second, first)
            if (state.get("action") != "assert" or state.get("source") != "state"
                    or state.get("op") != "eq" or type(state.get("value")) not in {int, float, str}
                    or display.get("action") != "assert" or display.get("source") != "text"
                    or display.get("op") != "eq" or display.get("selector") != "#" + str(state.get("path"))
                    or not isinstance(display.get("value"), str)):
                continue
            if _same_expected_value(state["value"], display["value"]):
                continue
            signals.append({"test_id": failure["id"],
                            "state_step": start if state is first else start + 1,
                            "display_step": start if display is first else start + 1,
                            "state_expected": state["value"],
                            "display_expected": display["value"]})
    return signals


def conflicting_cross_test_expectations(result, plan):
    """Find different literal results after identical fresh-page action prefixes.

    This is a plan-review signal, not proof that either expected value is right.
    Assertions are read-only; other actions, including waits, must match exactly.
    """
    if not isinstance(plan, dict):
        return []
    failed = {test.get("id"): test.get("failed_step") for test in result.get("tests", [])
              if test.get("passed") is not True and test.get("failure_kind") == "assertion_mismatch"
              and type(test.get("failed_step")) is int}
    checkpoints = {}
    for test in plan.get("tests", [])[:10]:
        if not isinstance(test, dict) or not isinstance(test.get("id"), str):
            continue
        actions = []
        for index, step in enumerate(test_steps(test), 1):
            if step.get("action") != "assert":
                actions.append(json.dumps(step, sort_keys=True, ensure_ascii=False))
                continue
            if step.get("op") != "eq" or type(step.get("value")) not in {int, float, str}:
                continue
            source = step.get("source")
            location = step.get("path") if source == "state" else step.get("selector") if source == "text" else None
            if location is None:
                continue
            key = (tuple(actions), source, location)
            checkpoints.setdefault(key, []).append((test["id"], index, step["value"]))
    signals = []
    for (actions, source, location), entries in checkpoints.items():
        for test_id, step, expected in entries:
            if failed.get(test_id) != step:
                continue
            for other_id, other_step, other_expected in entries:
                equivalent = (expected == other_expected if source == "text"
                              else _same_state_expected(expected, other_expected))
                if other_id == test_id or equivalent:
                    continue
                signals.append({"test_ids": [test_id, other_id], "steps": [step, other_step],
                                "source": source, "path_or_selector": location,
                                "action_count": len(actions), "expected_values": [expected, other_expected]})
                break
            if len(signals) >= 8:
                return signals
    return signals


def route_failure(result, plan_review=None, repeated_failure=False, plan=None):
    kinds = sorted({t.get("failure_kind", "unclassified") for t in result.get("tests", [])
                    if t.get("passed") is not True})
    action = "repair_code"
    instruction = "Repair only the observed implementation defect; preserve all original requirements and fixed tests."
    display_conflicts = conflicting_display_expectations(result, plan)
    state_conflicts = conflicting_state_expectations(result, plan)
    cross_test_conflicts = conflicting_cross_test_expectations(result, plan)
    if result.get("ok"):
        action, instruction = "complete", "Selected checks passed; full acceptance is still separate."
    elif result.get("infrastructure_error"):
        action, instruction = "stop_infrastructure", "Host/browser failure is not fixed by rewriting gameplay."
    elif result.get("artifact_errors") or result.get("runtime_errors"):
        instruction = "Fix missing local resources or the recorded runtime error before changing game rules."
    elif not result.get("quality_gate", {}).get("functional_evidence_present", True):
        action, instruction = "stop_unverified", "A functional plan is missing; do not edit game rules to manufacture evidence."
    elif result.get("quality_gate", {}).get("evidence_complete") is False:
        action, instruction = "stop_unverified", "The verifier did not return complete evidence; do not treat this as a gameplay diagnosis."
    elif any(w["test_id"] in {t["id"] for t in result.get("tests", []) if t.get("passed") is not True}
             for w in (plan_review or {}).get("warnings", []) if w.get("blocking_failure_review", True)):
        action, instruction = "stop_test_review", "A failed test has a fresh-page or temporal-capture review warning. Preserve the game and frozen tests; review the plan rather than blindly rewriting gameplay. This is not proof the game is correct."
    elif display_conflicts:
        action, instruction = "stop_test_review", "Adjacent frozen state and display assertions disagree on a named value. Preserve the game and frozen tests for plan review; neither assertion alone proves the game is correct."
    elif state_conflicts:
        action, instruction = "stop_test_review", "Frozen state assertions disagree on one value without an intervening action. Preserve the game and tests for review; neither assertion proves the correct behavior."
    elif cross_test_conflicts:
        action, instruction = "stop_test_review", "Frozen tests expect different values after identical fresh-page action sequences. Preserve the game and tests for rule review; neither expectation alone proves a code or test defect."
    elif repeated_failure:
        action, instruction = "stop_test_review", "Identical assertion evidence repeated after repair. Preserve the best artifact; root cause remains unverified, not automatically a test bug."
    elif set(kinds).intersection({"assertion_mismatch", "goal_timeout", "interaction_error"}):
        action = "review_failure"
        instruction = ("Check original rules, actual/expected observations and legal reachability first. "
                       "Do not alter tests, fake state, move targets or change speeds merely to satisfy a test. "
                       "If implementation is wrong, repair locally; if uncertain, say so.")
    elif set(kinds).intersection({"state_contract_error", "state_dom_mismatch"}):
        instruction = "Align the read-only snapshot and DOM with real live state; do not fake either observation."
    return {"action": action, "failure_kinds": kinds, "instruction": instruction,
            "display_conflicts": display_conflicts, "state_conflicts": state_conflicts,
            "cross_test_conflicts": cross_test_conflicts}


def validate_diagnosis(value, result):
    if not isinstance(value, dict) or not isinstance(value.get("category"), str) or value["category"] not in {"code_error", "test_issue", "tool_limit", "uncertain"}:
        raise ValueError("Invalid diagnosis category")
    reason = value.get("reason")
    ids = value.get("evidence_test_ids")
    failed = {t["id"] for t in result.get("tests", []) if t.get("passed") is not True}
    if not isinstance(reason, str) or not 1 <= len(reason) <= 1500:
        raise ValueError("Diagnosis needs a short evidence-based reason")
    if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in failed for i in ids):
        raise ValueError("Diagnosis must cite actual failed test IDs")
    if set(value) - {"category", "reason", "evidence_test_ids"}:
        raise ValueError("Diagnosis may not contain edits or revised tests")
    return value


def validate_blocked_repair(response, result, has_base):
    """Shared live/probe protocol: no edits and only actual failed-test evidence."""
    if (not isinstance(response, dict) or "blocked" not in response
            or set(response) - {"blocked", "summary"} or not has_base
            or not isinstance(result, dict) or "tests" not in result):
        raise ValueError("Blocked response requires prior failed verification and no proposed file edits")
    if "summary" in response and (not isinstance(response["summary"], str) or len(response["summary"]) > 1500):
        raise ValueError("Optional blocked summary must be a string of at most 1500 characters")
    blocked = validate_diagnosis(response["blocked"], result)
    if blocked["category"] == "code_error":
        raise ValueError("A demonstrated code error should be repaired, not labelled blocked")
    return blocked
