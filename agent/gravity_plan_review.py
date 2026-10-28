"""Fail-closed, pre-freeze replay of explicitly specified drop-token games.

Only the original requirement and the model's draft plan are inputs. Unknown
rules, actions and observations are left for human or model review.
"""
import re
from copy import deepcopy
from functools import lru_cache

from .contracts import compare, test_steps


def _rules(spec):
    if not isinstance(spec, str):
        return None
    # Markdown emphasis is formatting, not a change in the game rule.
    spec = re.sub(r"[*_`]", "", spec)
    lower = spec.lower()
    required = ("player a starts", "lowest empty cell", "turn passes to the other player",
                "three", "horizontal", "vertical", "diagonal", "winner: a",
                "winner: b", "draw", "finished game", "restart", "cell-row-column")
    if not all(fragment in lower for fragment in required):
        return None
    size = re.search(r"\b(?:has|is|with)\s+(\d+)\s+columns\s+and\s+(\d+)\s+rows\b", spec, re.I)
    if not size:
        return None
    columns, rows = map(int, size.groups())
    if not (3 <= columns <= 12 and 3 <= rows <= 12):
        return None
    return columns, rows


def _winner(board, row, col, token):
    height, width = len(board), len(board[0])
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        count = 1
        for sign in (-1, 1):
            y, x = row + sign * dr, col + sign * dc
            while 0 <= y < height and 0 <= x < width and board[y][x] == token:
                count += 1
                y += sign * dr
                x += sign * dc
        if count >= 3:
            return True
    return False


def gravity_plan_conflicts(plan, original_spec):
    """Return evidence of contradictions; never edit a draft or infer game correctness."""
    size = _rules(original_spec)
    if size is None or not isinstance(plan, dict):
        return []
    width, height = size
    conflicts = []
    covered_draw_requirements = set()
    board_contract = plan.get("state_contract", {}).get("board", "")
    declared_row_major = (re.search(r"row-major\s+row\s*0\.\.(\d+)\s*,\s*col\s*0\.\.(\d+)",
                                    board_contract, re.I) if isinstance(board_contract, str) else None)
    row_major = bool(declared_row_major and
                     tuple(map(int, declared_row_major.groups())) == (height - 1, width - 1))
    for test in plan.get("tests", []):
        steps = test_steps(test)
        # Never partially replay a test containing an unfamiliar operation.
        if any(step.get("action") not in {"click", "assert", "capture", "assert_consistent"}
               or (step.get("action") == "click" and step.get("selector") not in
                   {"#restart"} | {f"#drop-{col}" for col in range(width)})
               for step in steps):
            continue
        board = [["" for _ in range(width)] for _ in range(height)]
        turn, moves, status = "A", 0, "Playing"
        for index, step in enumerate(steps, 1):
            action = step["action"]
            if action == "click":
                selector = step["selector"]
                if selector == "#restart":
                    board = [["" for _ in range(width)] for _ in range(height)]
                    turn, moves, status = "A", 0, "Playing"
                elif status == "Playing":
                    col = int(selector.rsplit("-", 1)[1])
                    row = next((r for r in range(height - 1, -1, -1) if not board[r][col]), None)
                    if row is not None:
                        board[row][col] = turn
                        moves += 1
                        if _winner(board, row, col, turn):
                            status = f"Winner: {turn}"
                        elif moves == width * height:
                            status = "Draw"
                        else:
                            turn = "B" if turn == "A" else "A"
                continue
            if action != "assert" or "value" not in step:
                continue
            selector = step.get("selector")
            values = {"#turn": turn, "#moves": str(moves), "#status": status}
            cell = re.fullmatch(r"#cell-(\d+)-(\d+)", selector or "")
            if cell:
                r, c = map(int, cell.groups())
                if 0 <= r < height and 0 <= c < width:
                    values[selector] = board[r][c]
            actual = values.get(selector) if step.get("source") == "text" else None
            board_index = (re.fullmatch(r"board\.(\d+)", step.get("path", ""))
                           if step.get("source") == "state" and row_major else None)
            if board_index:
                flat_index = int(board_index.group(1))
                if 0 <= flat_index < width * height:
                    actual = board[flat_index // width][flat_index % width]
            if actual is None or step.get("op") not in {"eq", "contains"}:
                continue
            if not compare(actual, step["op"], step["value"]):
                conflicts.append({"test_id": test.get("id"), "step": index,
                                  "selector": selector or step.get("path"), "expected": step["value"],
                                  "actual_from_spec": actual,
                                  "kind": "explicit_gravity_transition_conflict",
                                  "message": "Draft assertion conflicts with a replay of the explicit drop, win, draw and restart rules. Revise the plan before generating code."})
                break
            if selector == "#status" and actual == "Draw" and step.get("op") == "eq":
                covered_draw_requirements.update(test.get("requirement_ids", []))
    for requirement in plan.get("requirements", []):
        text = requirement.get("text", "")
        if (requirement.get("verification") == "automated" and
                re.search(r"\bdraw\b", text, re.I) and
                re.search(r"\b(?:board|cells)\b", text, re.I) and
                re.search(r"\b(?:fill|fills|filled|full)\b", text, re.I) and
                requirement.get("id") not in covered_draw_requirements):
            related = next((test.get("id") for test in plan.get("tests", [])
                            if requirement.get("id") in test.get("requirement_ids", [])), None)
            conflicts.append({"test_id": related, "requirement_id": requirement.get("id"),
                              "step": None, "selector": "#status",
                              "expected": "Draw", "actual_from_spec": "no reachable Draw assertion",
                              "kind": "missing_gravity_draw_coverage",
                              "message": "The automated draw requirement needs a reachable exact Draw assertion in a fresh-page test."})
    return conflicts


def _draw_path(width, height, max_states=100000):
    """Find a legal no-win full-board path using the stated rules alone."""
    if width * height > 16:
        return None
    visited = 0

    @lru_cache(maxsize=None)
    def search(cells, turn):
        nonlocal visited
        visited += 1
        if visited > max_states:
            return None
        if all(cells):
            return ()
        # Reverse ordering is arbitrary; it is independent of any held-out plan.
        for col in range(width - 1, -1, -1):
            row = next((r for r in range(height - 1, -1, -1)
                        if not cells[r * width + col]), None)
            if row is None:
                continue
            next_cells = list(cells)
            next_cells[row * width + col] = turn
            board = [next_cells[r * width:(r + 1) * width] for r in range(height)]
            if _winner(board, row, col, turn):
                continue
            tail = search(tuple(next_cells), "B" if turn == "A" else "A")
            if tail is not None:
                return (col,) + tail
        return None

    return search(("",) * (width * height), "A")


def _is_draw_sequence(columns, width, height):
    board = [["" for _ in range(width)] for _ in range(height)]
    turn = "A"
    for col in columns:
        row = next((r for r in range(height - 1, -1, -1) if not board[r][col]), None)
        if row is None:
            return False
        board[row][col] = turn
        if _winner(board, row, col, turn):
            return False
        turn = "B" if turn == "A" else "A"
    return len(columns) == width * height


def repair_explicit_gravity_draw_plan(plan, original_spec):
    """Replace only an invalid pure draw path before the plan is frozen.

    Assertions, requirement IDs and original draft are preserved. Any mixed or
    ambiguous scenario abstains and remains subject to planner review.
    """
    size = _rules(original_spec)
    if size is None or not isinstance(plan, dict):
        return plan, []
    width, height = size
    corrected = deepcopy(plan)
    changes = []
    safe_path = None
    for test in corrected.get("tests", []):
        steps = test.get("setup_steps", []) + test.get("steps", [])
        actions = [step.get("action") for step in steps]
        clicks = [step for step in steps if step.get("action") == "click"]
        if (len(clicks) != width * height or
                any(action not in {"click", "assert"} for action in actions) or
                actions != ["click"] * len(clicks) + ["assert"] * (len(steps) - len(clicks)) or
                any(step.get("selector") not in {f"#drop-{col}" for col in range(width)}
                    for step in clicks) or
                any(step.get("source") != "text" or step.get("selector") not in
                    {"#moves", "#turn", "#status"} or step.get("op") != "eq"
                    for step in steps[len(clicks):]) or
                not any(step.get("selector") == "#status" and step.get("value") == "Draw"
                        for step in steps[len(clicks):])):
            continue
        original_path = tuple(int(step["selector"].rsplit("-", 1)[1]) for step in clicks)
        if _is_draw_sequence(original_path, width, height):
            continue
        if safe_path is None:
            safe_path = _draw_path(width, height)
        if safe_path is None:
            continue
        for step, col in zip(clicks, safe_path):
            step["selector"] = f"#drop-{col}"
        changes.append({"test_id": test.get("id"), "old_columns": list(original_path),
                        "new_columns": list(safe_path),
                        "basis": "Bounded search of explicit original-spec drop/win/draw rules; no game or independent acceptance input"})
        evidence = test.get("evidence")
        if isinstance(evidence, dict) and isinstance(evidence.get("expected_basis"), str):
            evidence["expected_basis"] = (
                "From a fresh board, drop in columns " + ",".join(map(str, safe_path)) +
                ". Every move remains non-winning; the last fills the board, so status is Draw. "
                "This path was computed from explicit rules before code generation; the model draft is archived.")
    return corrected, changes
