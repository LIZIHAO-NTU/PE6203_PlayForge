"""Fail-closed, pre-freeze replay of explicitly specified drop-token games.

Only the original requirement and the model's draft plan are inputs. Unknown
rules, actions and observations are left for human or model review.
"""
import re

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
            if action != "assert" or "value" not in step or step.get("source") != "text":
                continue
            selector = step.get("selector")
            values = {"#turn": turn, "#moves": str(moves), "#status": status}
            cell = re.fullmatch(r"#cell-(\d+)-(\d+)", selector or "")
            if cell:
                r, c = map(int, cell.groups())
                if 0 <= r < height and 0 <= c < width:
                    values[selector] = board[r][c]
            actual = values.get(selector)
            if actual is None or step.get("op") not in {"eq", "contains"}:
                continue
            if not compare(actual, step["op"], step["value"]):
                conflicts.append({"test_id": test.get("id"), "step": index,
                                  "selector": selector, "expected": step["value"],
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
