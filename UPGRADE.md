# PlayForge — MVP 0.2: Observation-Based Acceptance and Independent Rechecks

> This is the historical 0.2 record, preserving its features and test results. The version current when this note was maintained was 1.0 Beta 3 (`1.0.0-beta.3`). For installation/use, see [README.md](README.md); planning changes: [PLANNING.md](PLANNING.md); prior screening: [CAPABILITY.md](CAPABILITY.md); integrated baseline: [INTEGRATION.md](INTEGRATION.md); historical 0.3 trials: [GENERALIZATION.md](GENERALIZATION.md).

This is a moderate extension of the original MVP focused on trustworthy testing and failure diagnosis. It retains the DeepSeek connection, existing configuration and startup method, without adding a complex UI, multi-agent system or game engine.

## 1. Why prioritize this upgrade?

In the first real trial, some tests moved for a fixed time and then checked score or victory even though the player had not reached the target. Blindly asking the model to repair those failures could waste calls or make it modify an otherwise reasonable game to satisfy the test.

The upgrade lets tests act on current observations and assert only after an explicit goal. For example, use real arrow keys to follow the current star until the score reaches 10, reread the star position, then continue checking 20 and 30 points.

## 2. Specific extensions

| Extension | Purpose | Boundary |
|---|---|---|
| `wait_until` | Wait for a real state/UI condition | Bounded timeout, never infinite waiting |
| `key_until` | Use normal keys until an observed condition holds | No internal-state mutation |
| `move_to` | Read actor/target coordinates and follow with directional keys | Unobstructed top-down 2D movement only; no pathfinding/platforming |
| `surface` assertions | Check actual canvas/DOM dimensions | Does not prove collision or rendered-content correctness |
| Failure categories | Distinguish goal timeouts, assertion mismatches, state-interface, interaction and runtime errors | Categories describe observations, not proven root causes |
| Plan-risk warnings | Flag potential false failures from fixed-duration movement followed by score/victory checks | Heuristics, not automatic test edits |
| `recheck` command | Independently retest a saved game with zero API calls | No game repair or rewrite of original autonomous-development scores |
| Reporting | Record Agent version, automated requirement-pass proportions, failure categories and plan warnings | Requirement-pass proportions are not complete game success rates |

Planning prompts also correct a manual-check example that referenced a nonexistent requirement and discourage invented Start buttons, fixed-time collision assumptions and incorrect canvas-size checks. Repair prompts require inspecting the actual action trajectory and original requirement first; fake state and weakened acceptance are prohibited.

Each goal action is limited to 8 seconds; explicit waits and goal budgets across the plan are limited to 45 seconds, with an overall browser-process timeout as well. Failures remain failures, and the model cannot modify the fixed acceptance plan during execution.

## 3. Usage

### Generate a new game from scratch (uses the configured API)

Run from the project directory with your existing Python environment and `.env`:

```powershell
python -m agent game_design_prompt.md --max-rounds 2 --max-calls 5 --max-seconds 360
```

For a virtual environment, replace `python` with `.venv\Scripts\python.exe`. The new actions are in the planning prompt for the model to select as appropriate; not every game should use `move_to`. Leave manual checks for aspects unsuitable for automatic verification.

### Recheck a previously saved example (no API calls)

```powershell
python -m agent recheck runs/live_test_20261009_01/game --plan examples/collector_acceptance.json
```

Outputs go into a new `rechecks/` subdirectory. Add `--headful` to watch, or `--output` for a new, nonexistent output directory.

`collector_acceptance.json` is a regression plan written against the existing example's observation fields and controls, for independent acceptance only. It is not a game template supplied to the model and cannot verify every unseen game unchanged. Other games may first use their own `traces/plan.json`, but existing plan defects do not disappear automatically.

## 4. Validation results

Validation date: 2026-10-09. Environment: Windows, Python 3.11, Playwright and locally installed Edge.

- **54/54 framework tests passed**, 33.027 seconds total. Model responses were simulated, with no real model-service connection. Coverage includes real-browser interaction, repair loops, timeout cleanup and safety constraints.
- **7/7 independent checks** on the existing star-collector game passed in **18.343 seconds**. Coverage includes actual canvas size, initial layout, horizontal/vertical movement, scoring and star relocation, three collections and victory lock, pause/resume, restart while paused and restart after victory.
- Independent rechecks executed 11 observation-driven goal operations through normal keyboard events, without teleporting the actor, setting scores or changing game code.
- Appearance, full-square boundary containment, smoothness and state-interface fidelity remain manual checks.
- No DeepSeek API calls were made; `.env`, the original game, old plan and historical results were unchanged.

These results show the new tools work, not that the upgraded Agent's unseen-game success rate improved. Next, evaluate different requirements and repeated real-model runs, recording model, prompt hash, Agent version and budgets separately. Do not combine independent recheck results with autonomous-development scores.

Browser screenshots and debugging output from this round were temporary validation materials and were removed. Reproducible code, tests and the acceptance plan remain; rerun the zero-API command above to regenerate evidence.

## 5. Retained deliverables

Existing project files remain, with updates to core code, version, prompts, summary fields, README and ignore rules. Additions:

- `agent/recheck.py`: independent recheck entry point.
- `tests/test_upgrade.py`: automatic regressions for the additions.
- `examples/collector_acceptance.json`: the existing example's independent acceptance plan.
- `UPGRADE.md`: this upgrade note.

This remains an offline 2D browser-game prototype, not a complete course-delivery system or security-audited execution sandbox.
