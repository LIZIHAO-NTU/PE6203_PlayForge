"""Conservative pre-freeze replay for fully explicit finite-state rules.

These helpers use the original specification and draft plan only. They abstain if
the required rule grammar or an action in a scenario is not understood.
"""
from copy import deepcopy
import re

from .contracts import compare, test_steps


_DIRECTIONS = {"ArrowUp": (0, -1), "ArrowDown": (0, 1),
               "ArrowLeft": (-1, 0), "ArrowRight": (1, 0)}
_NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                 "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _number(value):
    return int(value) if value.isdigit() else _NUMBER_WORDS.get(value.lower())


def _normalize(plan, original_spec, replay):
    corrected = deepcopy(plan)
    changes = []
    for test in corrected.get("tests", []):
        evidence = test.get("evidence")
        if isinstance(evidence, dict) and "expected_observations" in evidence:
            # This independently recorded sequence must be reconciled as a whole;
            # changing only an assertion would leave contradictory plan metadata.
            continue
        steps = test_steps(test)
        outcomes = replay(steps, original_spec)
        if outcomes is None:
            continue
        setup = test.get("setup_steps", [])
        for index, actual in outcomes:
            step = setup[index] if index < len(setup) else test["steps"][index - len(setup)]
            if step.get("op") != "eq" or "value" not in step:
                continue
            if compare(actual, "eq", step["value"]):
                continue
            prior = step["value"]
            step["value"] = actual
            changes.append({"test_id": test.get("id"), "step": index + 1,
                            "before": prior, "after": actual,
                            "basis": "Replay of fully explicit original-spec transitions before plan freeze"})
    return corrected, changes


def _portal_rules(spec):
    if not isinstance(spec, str) or not all(fragment in spec.lower() for fragment in (
            "arrow presses move one cell", "boundaries block movement",
            "no walls or other rules", "reaching it wins and further movement is ignored",
            "restart resets position and move count")):
        return None
    size = re.search(r"\b(\d+)-column,\s*(\d+)-row\s+board\b", spec, re.I)
    start = re.search(r"Start the player at\s*\((\d+)\s*,\s*(\d+)\)", spec, re.I)
    portal = re.search(r"Entering\s*\((\d+)\s*,\s*(\d+)\)\s+immediately teleports the player to\s*\((\d+)\s*,\s*(\d+)\)", spec, re.I)
    goal = re.search(r"the exit is\s*\((\d+)\s*,\s*(\d+)\)", spec, re.I)
    if not all((size, start, portal, goal)):
        return None
    width, height = map(int, size.groups())
    initial = tuple(map(int, start.groups()))
    entry = tuple(map(int, portal.groups()[:2]))
    target = tuple(map(int, portal.groups()[2:]))
    exit_cell = tuple(map(int, goal.groups()))
    if not 2 <= width <= 20 or not 2 <= height <= 20 or not all(
            0 <= x < width and 0 <= y < height for x, y in (initial, entry, target, exit_cell)):
        return None
    return width, height, initial, entry, target, exit_cell


def _portal_replay(steps, spec):
    rules = _portal_rules(spec)
    if rules is None:
        return None
    width, height, initial, entry, target, exit_cell = rules
    position, moves, won = initial, 0, False
    outcomes = []
    for index, step in enumerate(steps):
        action = step.get("action")
        if action == "key" and step.get("key") in _DIRECTIONS:
            if won:
                continue
            dx, dy = _DIRECTIONS[step["key"]]
            next_position = position[0] + dx, position[1] + dy
            if 0 <= next_position[0] < width and 0 <= next_position[1] < height:
                position = target if next_position == entry else next_position
                moves += 1
                won = position == exit_cell
        elif action == "click" and step.get("selector") == "#restart":
            position, moves, won = initial, 0, False
        elif action in {"assert", "assert_consistent", "capture"}:
            if action == "capture":
                continue
            states = {"player.x": position[0], "player.y": position[1],
                      "moves": moves, "phase": "Won" if won else "Playing"}
            labels = {"#moves": str(moves), "#status": states["phase"]}
            actual = (states.get(step.get("path")) if step.get("source") == "state" else
                      labels.get(step.get("selector")) if step.get("source") == "text" else None)
            if actual is not None:
                outcomes.append((index, actual))
        else:
            return None
    return outcomes


def normalize_explicit_portal_plan(plan, original_spec):
    """Correct known literal portal outcomes; leave all other scenarios untouched."""
    return _normalize(plan, original_spec, _portal_replay)


def _charge_craft_rules(spec):
    if not isinstance(spec, str) or not all(fragment in spec.lower() for fragment in (
            "no crystals", "after winning both actions are ignored",
            "restart restores the initial state", "no timer, movement, levels or extra rules")):
        return None
    initial = re.search(r"start with\s+(\d+)\s+energy and no crystals", spec, re.I)
    charge = re.search(r"Charge adds\s+(\d+)\s+energy,\s+capped at\s+(\d+)", spec, re.I)
    craft = re.search(r"Craft costs\s+(\d+)\s+energy and gives one crystal,\s+but has no effect if energy is insufficient", spec, re.I)
    goal = re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+crystals wins\b", spec, re.I)
    if not all((initial, charge, craft, goal)):
        return None
    energy0 = int(initial.group(1))
    gain, cap = map(int, charge.groups())
    cost = int(craft.group(1))
    target = _number(goal.group(1))
    if target is None or not 0 <= energy0 <= cap <= 100 or not 0 < gain <= 100 or not 0 < cost <= 100 or not 1 <= target <= 20:
        return None
    return energy0, gain, cap, cost, target


def _charge_craft_replay(steps, spec):
    rules = _charge_craft_rules(spec)
    if rules is None:
        return None
    energy0, gain, cap, cost, target = rules
    energy, crystals, won = energy0, 0, False
    outcomes = []
    for index, step in enumerate(steps):
        action = step.get("action")
        if action == "click":
            selector = step.get("selector")
            if selector == "#restart":
                energy, crystals, won = energy0, 0, False
            elif selector == "#charge":
                if not won:
                    energy = min(cap, energy + gain)
            elif selector == "#craft":
                if not won and energy >= cost:
                    energy -= cost
                    crystals += 1
                    won = crystals >= target
            else:
                return None
        elif action in {"assert", "assert_consistent", "capture"}:
            if action == "capture":
                continue
            states = {"energy": energy, "crystals": crystals,
                      "phase": "Won" if won else "Playing"}
            labels = {"#energy": str(energy), "#crystals": str(crystals),
                      "#phase": states["phase"]}
            actual = (states.get(step.get("path")) if step.get("source") == "state" else
                      labels.get(step.get("selector")) if step.get("source") == "text" else None)
            if actual is not None:
                outcomes.append((index, actual))
        else:
            return None
    return outcomes


def normalize_explicit_charge_craft_plan(plan, original_spec):
    """Replay a completely specified charge/craft ledger before freezing tests."""
    return _normalize(plan, original_spec, _charge_craft_replay)
