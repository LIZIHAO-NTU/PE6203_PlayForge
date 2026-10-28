"""Pre-freeze review of plans, never post-hoc adjustment to generated game behavior."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import re

from .contracts import compare, require, test_steps, validate_plan


EXECUTION_CONTRACT = {
    "isolation": "Each test runs on its own NEW page at the original initial state.",
    "setup": "Optional setup_steps use ordinary input/observation before this test's check steps.",
    "no_inheritance": "No state or captures carry between tests; repeat all prerequisites locally.",
    "limits": {"combined_setup_and_check_steps": 18, "plan_wait_budget_ms": 45000,
               "individual_wait_or_hold_ms": 2000, "individual_goal_timeout_ms": 8000},
    "safety": "No state setters, injected game scripts or weakening frozen acceptance.",
    "state_hook": "window.__gameTest.getState() is the single read-only observation interface; explicit original-spec aliases may coexist.",
    "temporal": "Apply controls before capturing a stable baseline; assert_stable observes equality over bounded samples after prior input.",
    "test_basis": "A short original-spec quote and outcome basis are reviewable claims, never proof of correctness.",
    "expected_observations": "Optional ordered [{value: literal threshold/expected value}] must agree with and cover every literal assert in combined setup/check order; [] only when none. Legacy step/value records supported. Checked before freeze, never inferred from implementation.",
    "form_inputs": "fill uses ordinary non-secret text controls; select_option uses native select values. No password/file/hidden input or arbitrary script.",
}


def explicit_grid_transition_warnings(plan, original_spec):
    """Check only fully specified one-crate grids; abstain on other game rules.

    This narrow oracle never uses generated code or the held-out acceptance plan.
    """
    if not isinstance(original_spec, str) or not all(fragment in original_spec.lower() for fragment in (
            "outer cell", "inner cells are floor", "blocked actions do not increase moves",
            "crate reaching the goal wins", "after winning, arrows cannot change state")):
        return []
    size = re.search(r"\b(?:a|an)\s+(\d+)\s*x\s*(\d+)\s+grid\b", original_spec, re.I)
    initial = re.search(
        r"initial\s+player\s*=\s*\((\d+)\s*,\s*(\d+)\)\s*,\s*"
        r"crate\s*=\s*\((\d+)\s*,\s*(\d+)\)\s*,\s*"
        r"goal\s*=\s*\((\d+)\s*,\s*(\d+)\)", original_spec, re.I)
    if not size or not initial:
        return []
    width, height = map(int, size.groups())
    start = tuple(map(int, initial.groups()))
    if not 3 <= width <= 20 or not 3 <= height <= 20:
        return []
    player0, crate0, goal = start[:2], start[2:4], start[4:]
    if not all(0 < x < width - 1 and 0 < y < height - 1 for x, y in (player0, crate0, goal)):
        return []
    directions = {"ArrowUp": (0, -1), "ArrowDown": (0, 1),
                  "ArrowLeft": (-1, 0), "ArrowRight": (1, 0)}
    warnings = []
    for test in plan.get("tests", []):
        steps = test_steps(test)
        if any(step.get("action") not in {"key", "click", "assert", "assert_consistent", "capture"}
               or (step.get("action") == "key" and step.get("key") not in directions)
               or (step.get("action") == "click" and step.get("selector") != "#restart")
               for step in steps):
            continue
        player, crate, moves, won = player0, crate0, 0, False
        for index, step in enumerate(steps, 1):
            if step["action"] == "click":
                player, crate, moves, won = player0, crate0, 0, False
                continue
            if step["action"] == "key":
                if won:
                    continue
                dx, dy = directions[step["key"]]
                next_player = (player[0] + dx, player[1] + dy)
                if not (0 < next_player[0] < width - 1 and 0 < next_player[1] < height - 1):
                    continue
                if next_player == crate:
                    next_crate = (crate[0] + dx, crate[1] + dy)
                    if not (0 < next_crate[0] < width - 1 and 0 < next_crate[1] < height - 1):
                        continue
                    crate = next_crate
                    won = crate == goal
                player = next_player
                moves += 1
                continue
            if step["action"] != "assert" or step.get("op") != "eq" or "value" not in step:
                continue
            expected = step["value"]
            states = {"player.x": player[0], "player.y": player[1],
                      "crate.x": crate[0], "crate.y": crate[1],
                      "goal.x": goal[0], "goal.y": goal[1], "moves": moves}
            labels = {"#player-pos": f"{player[0]},{player[1]}",
                      "#crate-pos": f"{crate[0]},{crate[1]}",
                      "#moves": str(moves), "#status": "Won" if won else "Playing"}
            actual = (states.get(step.get("path")) if step.get("source") == "state" else
                      labels.get(step.get("selector")) if step.get("source") == "text" else None)
            if actual is not None and not compare(actual, "eq", expected):
                warnings.append({"test_id": test.get("id"), "kind": "explicit_grid_transition_conflict",
                                 "step": index, "actual_from_spec": actual, "expected": expected,
                                 "blocking_failure_review": True,
                                 "message": "The draft assertion disagrees with a replay of the explicit grid and terminal rules."})
                break
    return warnings


def require_explicit_grid_consistency(plan, original_spec):
    """Reject an evidenced draft contradiction before acceptance is frozen."""
    conflicts = explicit_grid_transition_warnings(plan, original_spec)
    if conflicts:
        details = "; ".join(
            f"{item['test_id']} step {item['step']}: expected {item['expected']!r}, "
            f"explicit grid rules yield {item['actual_from_spec']!r}"
            for item in conflicts[:6])
        raise ValueError("Explicit grid transition conflicts: " + details)


def normalize_explicit_grid_plan(plan, original_spec):
    """Correct literal grid observations from explicit rules before plan freeze.

    The original draft is unchanged. Any non-literal or unsupported scenario abstains.
    """
    corrected = deepcopy(plan)
    changes = []
    for _ in range(180):
        conflicts = explicit_grid_transition_warnings(corrected, original_spec)
        if not conflicts:
            return corrected, changes
        for conflict in conflicts:
            test = next((item for item in corrected["tests"] if item.get("id") == conflict["test_id"]), None)
            if test is None:
                continue
            setup = test.get("setup_steps", [])
            offset = conflict["step"] - 1
            step = setup[offset] if offset < len(setup) else test["steps"][offset - len(setup)]
            previous = step["value"]
            step["value"] = conflict["actual_from_spec"]
            changes.append({"test_id": conflict["test_id"], "step": conflict["step"],
                            "before": previous, "after": step["value"],
                            "basis": "Explicit original-spec grid transition replay"})
    raise ValueError("Explicit grid normalization exceeded bounded correction count")


def explicit_resource_transition_warnings(plan, original_spec):
    """Replay an explicitly specified single-counter purchase loop, if complete."""
    if not isinstance(original_spec, str):
        return []
    initial = re.search(r"Initial\s+coins\s*=\s*(\d+)\s*,\s*power\s*=\s*(\d+)\s*,\s*phase\s*=\s*Playing", original_spec, re.I)
    earn = re.search(r"#earn\s+adds\s+exactly\s+(\d+)\s+coin", original_spec, re.I)
    buy = re.search(r"#buy\s+costs\s+exactly\s+(\d+)\s+coins\s+and\s+adds\s+exactly\s+(\d+)\s+power\s+only\s+if\s+coins\s*>=\s*(\d+)", original_spec, re.I)
    goal = re.search(r"Reach\s+power\s*=\s*(\d+)\s+to\s+win\s+immediately", original_spec, re.I)
    if not all((initial, earn, buy, goal)) or not all(fragment in original_spec.lower() for fragment in (
            "after won, earn and buy clicks do nothing", "#restart restores")):
        return []
    coins0, power0 = map(int, initial.groups()[:2])
    earn_amount = int(earn.group(1))
    cost, power_gain, threshold = map(int, buy.groups())
    target = int(goal.group(1))
    if cost != threshold or min(coins0, power0, earn_amount, cost, power_gain, target) < 0:
        return []
    warnings = []
    for test in plan.get("tests", []):
        steps = test_steps(test)
        if any(step.get("action") not in {"click", "assert", "assert_consistent", "fill", "capture"}
               or (step.get("action") == "click" and step.get("selector") not in {"#earn", "#buy", "#restart"})
               for step in steps):
            continue
        coins, power, won = coins0, power0, False
        captures = {}
        for index, step in enumerate(steps, 1):
            if step["action"] == "fill":
                if step.get("selector") in {"#coins", "#power", "#status"}:
                    warnings.append({"test_id": test.get("id"), "kind": "explicit_resource_invalid_action",
                                     "step": index, "blocking_failure_review": True,
                                     "message": "The plan tries to fill a read-only game status label."})
                break
            if step["action"] == "click":
                selector = step["selector"]
                if selector == "#restart":
                    coins, power, won = coins0, power0, False
                elif not won and selector == "#earn":
                    coins += earn_amount
                elif not won and selector == "#buy" and coins >= cost:
                    coins -= cost
                    power += power_gain
                    won = power >= target
                continue
            if step["action"] == "capture":
                captures[step.get("name")] = {"coins": coins, "power": power,
                                              "phase": "Won" if won else "Playing"}
                continue
            if step["action"] != "assert" or step.get("op") != "eq":
                continue
            states = {"coins": coins, "power": power, "phase": "Won" if won else "Playing"}
            labels = {"#coins": str(coins), "#power": str(power), "#status": states["phase"]}
            actual = (states.get(step.get("path")) if step.get("source") == "state" else
                      labels.get(step.get("selector")) if step.get("source") == "text" else None)
            reference = step.get("value_from")
            if actual is not None and isinstance(reference, dict):
                expected = captures.get(reference.get("capture"), {}).get(reference.get("path"))
                if expected is not None and not compare(actual, "eq", expected):
                    warnings.append({"test_id": test.get("id"), "kind": "explicit_resource_reference_conflict",
                                     "step": index, "actual_from_spec": actual, "expected_from_capture": expected,
                                     "blocking_failure_review": True,
                                     "message": "A captured value cannot remain unchanged after this specified resource action."})
                    break
            elif actual is not None and "value" in step and not compare(actual, "eq", step["value"]):
                warnings.append({"test_id": test.get("id"), "kind": "explicit_resource_transition_conflict",
                                 "step": index, "actual_from_spec": actual, "expected": step["value"],
                                 "blocking_failure_review": True,
                                 "message": "The assertion disagrees with the explicit purchase and terminal rules."})
                break
    return warnings


def normalize_explicit_resource_plan(plan, original_spec):
    corrected = deepcopy(plan)
    changes = []
    for _ in range(180):
        conflicts = explicit_resource_transition_warnings(corrected, original_spec)
        actionable = [item for item in conflicts if item["kind"] == "explicit_resource_transition_conflict"]
        if not actionable:
            return corrected, changes
        for conflict in actionable:
            test = next((item for item in corrected["tests"] if item.get("id") == conflict["test_id"]), None)
            if test is None:
                continue
            setup = test.get("setup_steps", [])
            offset = conflict["step"] - 1
            step = setup[offset] if offset < len(setup) else test["steps"][offset - len(setup)]
            previous = step["value"]
            step["value"] = conflict["actual_from_spec"]
            changes.append({"test_id": conflict["test_id"], "step": conflict["step"],
                            "before": previous, "after": step["value"],
                            "basis": "Explicit original-spec resource transition replay"})
    raise ValueError("Explicit resource normalization exceeded bounded correction count")


def require_explicit_resource_consistency(plan, original_spec):
    conflicts = explicit_resource_transition_warnings(plan, original_spec)
    if conflicts:
        details = "; ".join(f"{item['test_id']} step {item['step']}: {item['kind']}"
                            for item in conflicts[:6])
        raise ValueError("Explicit resource plan conflicts: " + details)


class PlanReviewError(ValueError):
    """A requested pre-freeze review could not establish a usable plan."""


def initial_assertions(test):
    """Only consecutive literal equality observations before any action/time advance."""
    records = []
    for index, step in enumerate(test_steps(test), 1):
        if step["action"] not in {"assert", "assert_consistent"}:
            break
        if step["action"] != "assert" or step.get("op") != "eq" or "value" not in step:
            continue
        if step["source"] not in {"state", "text", "attribute", "count", "enabled", "visible"}:
            continue
        identity = (step["source"], step.get("path"), step.get("selector"), step.get("attribute"))
        records.append((identity, step["value"], index))
    return records


def inspect_plan(plan, original_spec=None):
    """Find contradictions in a draft's own initial assertions, not infer game rules."""
    tests = plan.get("tests", [])
    ordered = sorted(tests, key=lambda t: t.get("purpose") != "initial")
    anchors, warnings = {}, []
    for test in ordered:
        for identity, value, index in initial_assertions(test):
            if identity in anchors and not compare(anchors[identity][0], "eq", value):
                warnings.append({"test_id": test["id"], "kind": "fresh_page_initial_conflict",
                    "step": index, "anchor_test_id": anchors[identity][1],
                    "observation": list(identity), "anchor_value": anchors[identity][0], "expected": value,
                    "message": "Fresh-page initial assertions disagree before any setup/input. Review missing setup or non-deterministic assumptions; not proof of a game bug."})
            else:
                anchors.setdefault(identity, (value, test["id"]))
    gameplay = plan.get("gameplay")
    realtime = isinstance(gameplay, dict) and gameplay.get("interaction_model") in {"real_time", "hybrid"}
    inputs = {"click", "key", "keys", "hover", "drag", "fill", "select_option", "key_until", "move_to"}
    for test in tests:
        basis = test.get("evidence")
        if original_spec is not None and basis:
            quote = " ".join(basis["spec_quote"].split())
            if quote not in " ".join(original_spec.split()):
                warnings.append({"test_id": test["id"], "kind": "unmatched_spec_quote",
                    "blocking_failure_review": False,
                    "message": "The claimed quote is not a verbatim original-spec fragment. Its explanation is not verified evidence."})
        captures, input_index = {}, 0
        for index, step in enumerate(test_steps(test), 1):
            if step["action"] in inputs:
                input_index += 1
            elif step["action"] == "capture":
                captures[step["name"]] = input_index
            elif step["action"] == "sample":
                captures[step["name"] + "_start"] = input_index
                captures[step["name"] + "_end"] = input_index
            ref = step.get("value_from", {})
            if (realtime and test.get("purpose") != "invalid_action" and step["action"] == "assert"
                    and step.get("source") == "state" and step.get("op") == "eq"
                    and ref.get("path") == step.get("path") and ref.get("capture") in captures
                    and captures[ref["capture"]] < input_index):
                warnings.append({"test_id": test["id"], "kind": "stale_temporal_capture", "step": index,
                    "blocking_failure_review": True,
                    "message": "A real-time equality uses a snapshot taken before intervening input. Capture AFTER pause/control changes, or use assert_stable after the action. If this test fails, review rather than blindly rewrite physics; this warning is heuristic, not proof of a bad test."})
    warnings.extend(explicit_grid_transition_warnings(plan, original_spec))
    warnings.extend(explicit_resource_transition_warnings(plan, original_spec))
    return {"warnings": warnings, "execution_contract": EXECUTION_CONTRACT,
            "note": "Heuristic review only. It cannot solve arbitrary maps, prove rules, or guarantee semantic correctness."}


def validate_audit(value, draft, required_warnings=None):
    """Allow evidence-explained plan edits ONLY before any game exists or tests freeze."""
    require(isinstance(value, dict), "Audit must be an object")
    status = value.get("status")
    require(isinstance(status, str) and status in {"approved", "revised", "unverified"}, "Invalid audit status")
    require(not set(value) - {"status", "reason", "issues", "plan"}, "Audit contains unexpected fields")
    require(isinstance(value.get("reason"), str) and 0 < len(value["reason"]) <= 1500, "Audit needs a short reason")
    issues = value.get("issues")
    require(isinstance(issues, list) and len(issues) <= 10, "Audit needs bounded issues")
    old_tests = {t["id"]: t for t in draft["tests"]}
    for issue in issues:
        require(isinstance(issue, dict) and set(issue) == {"test_id", "reason", "spec_evidence"}, "Invalid audit issue")
        require(isinstance(issue["test_id"], str) and (issue["test_id"] in old_tests or issue["test_id"] == "plan"), "Audit cites an unknown test")
        for key in ("reason", "spec_evidence"):
            require(isinstance(issue[key], str) and 0 < len(issue[key]) <= 2000, "Audit needs original-spec evidence")
    if status != "revised":
        require("plan" not in value, "Only a revised audit may include a plan")
        require(status != "approved" or not issues, "Approved audit cannot contain unresolved issues")
        require(status != "approved" or not any(
            warning.get("kind") in {"explicit_grid_transition_conflict", "explicit_resource_transition_conflict",
                                    "explicit_resource_reference_conflict",
                                    "explicit_resource_invalid_action"}
            for warning in (required_warnings or [])),
            "Approved audit left unresolved deterministic grid conflicts")
        return draft, value
    require(bool(issues), "Revised audit needs cited issues")
    revised = validate_plan(value.get("plan"))
    require(revised["supported"], "Audit cannot substitute unsupported for the original plan")
    old_requirements = {r["id"]: r for r in draft["requirements"]}
    new_requirements = {r["id"]: r for r in revised["requirements"]}
    require(set(old_requirements) == set(new_requirements), "Audit cannot add/remove requirement commitments")
    for rid, old in old_requirements.items():
        new = new_requirements[rid]
        require(all(old.get(k, "core" if k == "priority" else None) == new.get(k, "core" if k == "priority" else None)
                    for k in ("text", "verification", "priority")), "Audit changed a requirement commitment: " + rid)
    require(revised["state_contract"] == draft["state_contract"], "Audit cannot change the observation contract")
    require(revised.get("manual_checks", []) == draft.get("manual_checks", []), "Audit cannot discard manual checks")
    new_tests = {t["id"]: t for t in revised["tests"]}
    require(set(new_tests) == set(old_tests), "Audit must retain every test ID")
    cited = {i["test_id"] for i in issues}
    for tid, old in old_tests.items():
        if old != new_tests[tid]:
            require(tid in cited, "Each edited test needs a specific issue: " + tid)
            require(old["requirement_ids"] == new_tests[tid]["requirement_ids"], "Audit cannot move test coverage")
        def assertion_shapes(test):
            return Counter(json.dumps({k: v for k, v in step.items() if k not in {"value", "value_from"}}, sort_keys=True)
                           for step in test_steps(test) if step["action"] in {"assert", "assert_consistent", "assert_stable"})
        require(not (assertion_shapes(old) - assertion_shapes(new_tests[tid])),
                "Audit cannot remove assertions or weaken/change observation operators: " + tid)
    require(any(old_tests[tid] != new_tests[tid] for tid in old_tests), "Revised audit did not change a test")
    return revised, value


def failure_fingerprint(result):
    """Identify repeated identical assertion evidence; never diagnose root cause."""
    if result.get("runtime_errors") or result.get("infrastructure_error") or result.get("artifact_errors"):
        return None
    records = []
    for test in result.get("tests", []):
        if test.get("passed") is True:
            continue
        observations = test.get("observations", [])
        if test.get("failure_kind") != "assertion_mismatch" or not observations:
            return None
        last = observations[-1]
        if not all(k in last for k in ("actual", "expected", "op")):
            return None
        records.append({"id": test["id"], "step": test.get("failed_step"),
                        **{k: last[k] for k in ("actual", "expected", "op")}})
    return hashlib.sha256(json.dumps(sorted(records, key=lambda x: x["id"]), sort_keys=True).encode()).hexdigest() if records else None
