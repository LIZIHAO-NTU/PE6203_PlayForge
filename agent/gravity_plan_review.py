"""Fail-closed, pre-freeze replay of explicitly specified drop-token games.

Only the original requirement and the model's draft plan are inputs. Unknown
rules, actions and observations are left for human or model review.
"""
import re
from collections import deque
from copy import deepcopy
from functools import lru_cache

from .contracts import compare, test_steps


def _rules(spec):
    if not isinstance(spec, str):
        return None
    # Markdown emphasis is formatting, not a change in the game rule.
    spec = re.sub(r"[*_`]", "", spec)
    lower = re.sub(r"\s+", " ", spec.lower())
    sentences = re.split(r"(?<=[.!?])\s+", lower)
    required = ("player a starts", "lowest empty cell", "turn passes to the other player",
                "winner: a",
                "winner: b", "draw", "finished game", "restart", "cell-row-column")
    if not all(fragment in lower for fragment in required):
        return None
    size = re.search(r"\b(?:has|is|with)\s+(\d+)\s+columns\s+and\s+(\d+)\s+rows\b", spec, re.I)
    if not size:
        return None
    columns, rows = map(int, size.groups())
    if not (3 <= columns <= 12 and 3 <= rows <= 12):
        return None
    # Every replay begins with an empty board. An omitted or contradictory
    # starting position invalidates all generated paths and assertions.
    empty = re.search(r"\ball\s+(?:(\d+)\s+)?cells\s+start\s+empty\.", lower)
    if not empty or (empty.group(1) and int(empty.group(1)) != columns * rows):
        return None
    initial_marker = r"\b(?:initial(?:ly)?|starting|starts?|begins?|beginning|pre-?filled|pre-?placed|preset)\b"
    board_marker = r"\b(?:board|cells?|tokens?|pieces?)\b"
    if any(re.search(initial_marker, sentence) and re.search(board_marker, sentence)
           and not re.fullmatch(r"all (?:\d+ )?cells start empty\.", sentence.strip())
           for sentence in sentences):
        return None
    # The simulator has a fixed three-token win rule. A bare "three" may mean
    # three board rows while the actual win rule is four. Accept only an
    # explicit matching rule, and abstain on any competing win cardinality.
    three_win = re.search(
        r"\b(?:three|3)\s+(?:of\s+(?:their|the)\s+)?tokens?\s+in\s+a\s+contiguous\s+"
        r"horizontal\s*,\s*vertical\s*,\s*or\s+diagonal\s+line\b", lower)
    other = r"(?:one|two|four|five|six|seven|eight|nine|ten|[124-9]|1[0-9])"
    competing_win = (re.search(rf"\b{other}\s+(?:of\s+(?:their|the)\s+)?tokens?\s+"
                               r"(?:in\s+a\s+contiguous|in\s+a\s+row|in\s+a\s+line)", lower)
                     or re.search(rf"\b{other}\s*(?:-\s*)?(?:token\s+line|in\s+a\s+row)\b", lower)
                     or re.search(rf"\b(?:win|winning|connect)\s+(?:with|requires?|by)?\s*{other}\b", lower)
                     or re.search(rf"\b(?:line|row|sequence)\s+of\s+{other}\s+"
                                  r"(?:or\s+more\s+)?tokens?\b", lower))
    if not three_win or competing_win:
        return None
    return columns, rows


def supports_explicit_gravity_review(spec):
    """True only when the original spec states every transition we replay."""
    return _rules(spec) is not None


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


def gravity_reference_paths(original_spec, max_states=100000):
    """Bounded, rule-derived examples for planning; never reads a game or tests.

    These are candidate input traces, not acceptance verdicts. If the exact
    rules cannot be recognized or a search bound is reached, omit that case.
    """
    size = _rules(original_spec)
    if size is None:
        return {}
    width, height = size
    if width * height > 16:
        return {}
    names = ("horizontal", "vertical", "diagonal", "diagonal")
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    found = {}
    empty = ("",) * (width * height)
    queue = deque([(empty, "A", ())])
    seen = {empty}
    checked = 0
    while queue and len(found) < 3 and checked < max_states:
        cells, turn, path = queue.popleft()
        checked += 1
        for col in range(width):
            row = next((r for r in range(height - 1, -1, -1)
                        if not cells[r * width + col]), None)
            if row is None:
                continue
            next_cells = list(cells)
            next_cells[row * width + col] = turn
            board = [next_cells[r * width:(r + 1) * width] for r in range(height)]
            next_path = path + (col,)
            if _winner(board, row, col, turn):
                for name, (dr, dc) in zip(names, directions):
                    count = 1
                    for sign in (-1, 1):
                        y, x = row + sign * dr, col + sign * dc
                        while 0 <= y < height and 0 <= x < width and board[y][x] == turn:
                            count += 1
                            y += sign * dr
                            x += sign * dc
                    if count >= 3 and name not in found:
                        found[name] = {"columns": list(next_path), "result": f"Winner: {turn}"}
                continue
            state = tuple(next_cells)
            if state not in seen:
                seen.add(state)
                queue.append((state, "B" if turn == "A" else "A", next_path))
    draw = _draw_path(width, height, max_states=max_states)
    if draw is not None:
        found["draw"] = {"columns": list(draw), "result": "Draw"}
    return found


def compile_explicit_gravity_plan(original_spec):
    """Compile a small rule-complete plan when model drafts remain invalid.

    Applies only to a fully specified, bounded drop-token game. Every expected
    state and sequence is derived from the original spec's explicit rules.
    The normal verifier and independent acceptance still decide whether the
    generated game works.
    """
    size = _rules(original_spec)
    if size is None:
        return None
    width, height = size
    lower = re.sub(r"[*_`]", "", original_spec).lower()
    interface = (f"drop-0 through drop-{width - 1}", "restart", "turn", "moves",
                 "status", "cell-row-column", "offline", "full column",
                 "ignored", "win takes precedence over a draw")
    if not all(fragment in lower for fragment in interface):
        return None
    paths = gravity_reference_paths(original_spec)
    if not {"horizontal", "vertical", "diagonal", "draw"} <= paths.keys():
        return None
    if width * height + 6 > 18:
        return None

    def click(col):
        return {"action": "click", "selector": f"#drop-{col}"}

    def claim(selector, value, source="text"):
        return {"action": "assert", "source": source, "selector": selector,
                "op": "eq", "value": value}

    def sequence(kind):
        return [click(col) for col in paths[kind]["columns"]]

    def test(tid, requirements, description, steps):
        return {"id": tid, "requirement_ids": requirements,
                "description": description, "steps": steps}

    bottom = f"#cell-{height - 1}-0"
    final_turn = "A" if width * height % 2 else "B"
    turn_after_column = "A" if height % 2 == 0 else "B"
    horizontal = paths["horizontal"]
    tests = [
        test("T1", ["R1", "R7"], "Fresh board, count and turn",
             [claim("[id^='cell-']", width * height, "count"),
              claim(bottom, ""), claim(f"#cell-0-{width - 1}", ""),
              claim("#turn", "A"), claim("#moves", "0"), claim("#status", "Playing"),
              {"action": "assert", "source": "state", "path": "moves",
               "op": "eq", "value": 0}]),
        test("T2", ["R2", "R7"], "A legal drop follows gravity and passes the turn",
             [click(0), claim(bottom, "A"), claim("#moves", "1"),
              claim("#turn", "B"), claim("#status", "Playing")]),
        test("T3", ["R3"], "A full column ignores further clicks",
             [click(0) for _ in range(height)] +
             [claim("#moves", str(height)), click(0),
              claim("#moves", str(height)), claim("#turn", turn_after_column),
              claim("#status", "Playing"), claim("#drop-0", True, "enabled")]),
        test("T4", ["R4", "R6", "R7"], "Horizontal win locks further drops",
             sequence("horizontal") +
             [claim("#status", horizontal["result"]),
              claim("#turn", horizontal["result"][-1]),
              claim("#moves", str(len(horizontal["columns"]))),
              click(0), claim("#status", horizontal["result"]),
              claim("#moves", str(len(horizontal["columns"])))]),
        test("T5", ["R4"], "Vertical win",
             sequence("vertical") +
             [claim("#status", paths["vertical"]["result"]),
              claim("#moves", str(len(paths["vertical"]["columns"])))]),
        test("T6", ["R4"], "Diagonal win",
             sequence("diagonal") +
             [claim("#status", paths["diagonal"]["result"]),
              claim("#moves", str(len(paths["diagonal"]["columns"])))]),
        test("T7", ["R5", "R6", "R7"], "A full non-winning board draws and locks input",
             sequence("draw") +
             [claim("#status", "Draw"), claim("#moves", str(width * height)),
              claim("#turn", final_turn), click(0),
              claim("#status", "Draw"), claim("#moves", str(width * height))]),
        test("T8", ["R8"], "Restart during play allows an immediate new drop",
             [click(0), click_restart(), claim(bottom, ""),
              claim("#turn", "A"), claim("#moves", "0"), claim("#status", "Playing"),
              click(0), claim(bottom, "A"), claim("#moves", "1")]),
        test("T9", ["R8"], "Restart after win allows an immediate new drop",
             sequence("horizontal") +
             [click_restart(), claim(bottom, ""), claim("#turn", "A"),
              claim("#moves", "0"), claim("#status", "Playing"),
              click(0), claim(bottom, "A")]),
        test("T10", ["R8"], "Restart after draw allows an immediate new drop",
             sequence("draw") +
             [click_restart(), claim("#turn", "A"), claim("#moves", "0"),
              claim("#status", "Playing"), click(0), claim(bottom, "A")]),
    ]
    requirements = [
        {"id": "R1", "text": f"Initial {width} by {height} board is empty; A moves first, count 0 and Playing status.",
         "verification": "automated", "priority": "core"},
        {"id": "R2", "text": "A valid column click places one token in its lowest empty cell and advances the legal-move count and turn.",
         "verification": "automated", "priority": "core"},
        {"id": "R3", "text": "A full column remains clickable but further drops change no game state.",
         "verification": "automated", "priority": "core"},
        {"id": "R4", "text": "Three contiguous horizontal, vertical or diagonal tokens win immediately for the mover.",
         "verification": "automated", "priority": "core"},
        {"id": "R5", "text": "A full board without a winning line shows exactly Draw.",
         "verification": "automated", "priority": "core"},
        {"id": "R6", "text": "After any ending, column clicks are ignored and the finished state remains unchanged.",
         "verification": "automated", "priority": "core"},
        {"id": "R7", "text": "The active turn shows the next player; a finished game retains the final mover.",
         "verification": "automated", "priority": "core"},
        {"id": "R8", "text": "Restart clears the board, restores A, count 0 and Playing, and permits the next drop immediately.",
         "verification": "automated", "priority": "core"},
        {"id": "R9", "text": "Board, controls and readouts are readable and usable at normal desktop size.",
         "verification": "manual", "priority": "visual"},
        {"id": "R10", "text": "The page works offline without a server, network or external assets; Restart does not reload the page.",
         "verification": "manual", "priority": "core"},
        {"id": "R11", "text": "On the final cell, a winning line takes precedence over a draw.",
         "verification": "manual", "priority": "core"},
    ]
    heading = re.search(r"(?m)^#\s+(.+)$", original_spec)
    title = heading.group(1).strip()[:200] if heading else "Explicit gravity game"
    return {"supported": True, "reason": "", "title": title,
            "development_plan": ["Build an offline HTML/CSS/JS drop-token game from the original specification.",
                                 "Implement gravity, alternating turns, line wins, draw and Restart.",
                                 "Expose the required visible cells, controls and read-only state hook."],
            "state_contract": {"turn": "displayed turn A or B",
                               "moves": "number of legal drops so far",
                               "status": "status shown to player"},
            "requirements": requirements, "tests": tests,
            "manual_checks": [
                {"requirement_id": "R9", "instruction": "At desktop size confirm board, drop controls, turn, count, status and Restart are readable, aligned and clickable."},
                {"requirement_id": "R10", "instruction": "Disconnect network, open the page locally, and confirm play and Restart work without a page reload or remote resources."},
                {"requirement_id": "R11", "instruction": "If the last empty cell also creates a line of three, confirm Winner for the mover is shown rather than Draw."},
            ]}


def click_restart():
    return {"action": "click", "selector": "#restart"}


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
            if step.get("source") == "state":
                path = step.get("path")
                description = plan.get("state_contract", {}).get(path, "")
                if isinstance(description, str):
                    label = description.lower()
                    mapped_cell = (re.search(r"(?:cell text for|maps to|=|->)\s+#?cell-(\d+)-(\d+)\b",
                                             description, re.I)
                                   if re.fullmatch(r"board\.\d+", path or "") else None)
                    if mapped_cell:
                        mapped_row, mapped_col = map(int, mapped_cell.groups())
                        if 0 <= mapped_row < height and 0 <= mapped_col < width:
                            actual = board[mapped_row][mapped_col]
                    if path == "moves" and (
                            ("legal" in label or "valid" in label)
                            and ("drop" in label or "move" in label or "count" in label)):
                        actual = moves
                    elif path == "turn" and "turn" in label:
                        actual = turn
                    elif path == "status" and ("status" in label or "result" in label):
                        actual = status
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
