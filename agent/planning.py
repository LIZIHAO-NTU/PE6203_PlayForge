"""Explicit launch-only degradation; never silently weaken functional acceptance."""
from collections import Counter
from copy import deepcopy
import json

from .contracts import validate_plan, test_steps
from .quality import review_plan


def canonicalize_gameplay_shape(candidate):
    """Move explicitly supplied gameplay fields into their schema location.

    This changes only the JSON shape. It never invents or replaces a model claim.
    The normal contract validator still checks every value after this step.
    """
    if not isinstance(candidate, dict):
        return candidate
    result = deepcopy(candidate)
    keys = ("interaction_model", "input_mode", "core_loop")
    if not any(key in result for key in keys):
        return result
    gameplay = result.get("gameplay")
    if gameplay is None:
        gameplay = {}
        result["gameplay"] = gameplay
    if not isinstance(gameplay, dict):
        raise ValueError("Conflicting gameplay shape: gameplay must be an object")
    for key in keys:
        if key not in result:
            continue
        value = result.pop(key)
        if key in gameplay and gameplay[key] != value:
            raise ValueError("Conflicting gameplay field: " + key)
        gameplay[key] = value
    return result


def validate_recovery(previous, candidate):
    """A late plan may repair structure, not delete existing commitments to pass."""
    plan = validate_plan(candidate)
    if not plan["supported"] or not review_plan(plan)["functional_test_ids"]:
        raise ValueError("Recovery must provide functional interaction checks")
    old_requirements = previous.get("requirements", []) if isinstance(previous, dict) else []
    current = {r["id"]: r for r in plan["requirements"]}
    for requirement in old_requirements if isinstance(old_requirements, list) else []:
        if not isinstance(requirement, dict) or not isinstance(requirement.get("id"), str):
            continue
        rid = requirement["id"]
        if rid not in current:
            raise ValueError("Recovery removed an earlier requirement: " + rid)
        for key in ("text", "verification", "priority"):
            expected = requirement.get(key, "core" if key == "priority" else None)
            if expected is not None and current[rid].get(key, "core" if key == "priority" else None) != expected:
                raise ValueError("Recovery changed an earlier requirement: " + rid)
    def assertions(value):
        found = []
        tests = value.get("tests", []) if isinstance(value, dict) else []
        for test in tests if isinstance(tests, list) else []:
            if not isinstance(test, dict) or not isinstance(test.get("steps"), list):
                continue
            for step in test_steps(test):
                if not isinstance(step, dict) or step.get("action") not in {"assert", "assert_consistent", "assert_stable"}:
                    continue
                found.append(json.dumps(step, sort_keys=True, ensure_ascii=False))
        return Counter(found)
    if assertions(previous) - assertions(plan):
        raise ValueError("Recovery removed or changed an earlier assertion; leave acceptance unverified instead")
    return plan


def startup_only_plan():
    # Generic infrastructure, not a prewritten game or a substitute functional test suite.
    return {"supported": True, "reason": "", "title": "Partial game: functional plan unavailable",
        "development_plan": ["Implement all mandatory original-spec rules in a small runnable game",
                             "Validate startup; leave functional acceptance explicitly unverified"],
        "state_contract": {"phase": "Actual current game phase, read-only"},
        "requirements": [
            {"id": "Startup", "text": "Visible local game surface and error-free browser startup only",
             "verification": "automated", "priority": "core"},
            {"id": "OriginalRules", "text": "ALL mandatory functional and technical requirements in original_spec",
             "verification": "manual", "priority": "core"}],
        "tests": [{"id": "StartupSurface", "requirement_ids": ["Startup"],
                   "description": "Infrastructure only; does not check game rules",
                   "steps": [{"action": "assert", "source": "count",
                              "selector": "canvas, [data-game-surface]", "op": "ge", "value": 1}]}],
        "manual_checks": [{"requirement_id": "OriginalRules",
                           "instruction": "Verify every original-spec rule and technical constraint; no functional acceptance is claimed."}]}
