# PlayForge — MVP 0.3: Cross-Mechanic Reliability

The goal is to implement correct, runnable core gameplay from unseen requirements, rather than turn every request into the same collector game. The project retains one Agent, a DeepSeek-compatible interface and vanilla offline HTML/CSS/JS, without prewritten game code, engines, templates or built-in solvers.

## Main improvements

1. **Gameplay analysis:** distinguish real-time, turn-based and mixed interactions, plus keyboard/pointer input, and record the core loop and rule invariants. DOM boards and Canvas animation are both possible; not every game needs a moving character, score or pause button.
2. **Core first:** implement all mandatory rules, controls and startup requirements before simple visual polish. A “minimal version” cannot omit original requirements.
3. **Generic interaction tools:** add element-local coordinate clicks, Canvas pixel scaling, hover, drag and simultaneous keys, plus DOM count, attribute and enabled-state observations. `move_to` remains limited to unobstructed continuous movement; it cannot replace Sokoban or maze rules.
4. **Repair working memory:** retain change summaries, failed observations and passed checks from the latest three rounds; continue from the better-tested version to reduce regressions from later rewrites. Source hashes detect duplicate output rather than trusting a model's claim of changes.
5. **Runnable-candidate selection:** prefer complete passes, then visible artifacts without runtime errors, then check-pass counts. This is still not a complete gameplay-quality score.
6. **More complete evidence:** record each test step's action, parameters, result, duration or error; preserve the fixed plan, state, round versions and browser evidence.
7. **Explicit planning-failure fallback:** after two failed functional-plan validations, if the model explicitly identifies the requirement as supported, still try generating from the original requirement with generic startup checks only. Mark the result `partial_game_plan_failed` and functional pass rates unverified; a lower standard is not success. `--strict-plan` retains stop-on-planning-failure behavior. API errors and explicitly unsupported tasks do not take this path.

The state contract can normalize nested descriptions into dotted paths; automated requirements may also carry manual review. Normalization does not alter raw model responses, expected values or game rules. Disabled buttons are recorded as non-activatable no-ops; forced clicks or JavaScript enabling are not used to fake operations.

Legacy test plans remain usable. New plans may include `gameplay` and requirement `priority`; users need not author those fields.

## Why the four test families differ

| Requirement | Underlying logic | Main checks |
|---|---|---|
| Tic-tac-toe | Discrete turns, legal placement, board outcomes | Occupied-cell no-op, win lock, draw, restart |
| Sokoban | Discrete grid, obstacles, pushing constraints | Walls, blocked crates, legal pushes, reaching targets |
| Memory pairs | Hidden information, second selection, asynchronous flip-back | Match counting, mismatch lock, repeated clicks, clearing old timers |
| Brick breaker | Continuous time, collisions, position integration | Paddle movement, ball/brick collision, pause freeze, reset |

These are small, explicit and reproducible feasibility tasks, not representative of every game. Full brick-breaker completion and collision boundaries, all rule permutations in the other games, overall playability and visual/state fidelity need further acceptance. Fixed initial layouts belong to evaluation inputs and do not become Agent game templates.

## Report three result types separately

- **Startup rate:** a visible game surface exists and the selected version has no recorded runtime error. This does not prove complete core rules.
- **Model-plan pass rate:** whether the Agent's own frozen checks all pass; shared misunderstandings remain possible.
- **Independent-check pass rate:** whether separate checks authored before generation pass. They are not supplied to the generating model or fed back into repair for that run, and do not change its original score.

Independent plans primarily use DOM observations; some brick-breaker position checks still read the game's own read-only state interface. They are therefore not complete proofs of game behavior. A model's “looks good” judgment is not acceptance.

Reports list results by mechanic and macro-average per-family pass rates so repeated easy cases do not hide difficult families. One run per family establishes only that trial's feasibility, not a reliable success probability. Version/prompt comparisons must fix requirements, model, budgets, checks and repetition counts. Without an old-version comparison, no percentage improvement can be claimed.

## Usage

Use your own Python environment and `.env`; first install `requirements.txt` and a Playwright browser. Do not share API keys.

```powershell
python -m agent benchmark examples/benchmark/suite.json --max-total-calls 20 --max-calls-per-case 5 --max-rounds 3 --max-seconds 420
```

All actual API attempts, including planning, formatting retries and network retries, share the total call cap. Cases without sufficient budget remain skipped; do not remove them to improve results. A call cap is not a monetary guarantee: charges depend on model prices, tokens and provider billing. The default is one run per family.

For repeated trials, add `--repeats 2` and choose an acceptable total call cap; this still incurs charges. Add new requirement `.md` files and corresponding independent acceptance `.json` files under `examples/benchmark/`, then register them in `suite.json`. Do not inject acceptance plans or historical game code into generation prompts.

Results go into a new `runs/benchmark_*/`:

```text
BENCHMARK.md / benchmark.json       Aggregate results
cases/<case_id>/game/               Complete automatically generated game
cases/<case_id>/traces/             Model plans, execution, repairs and usage
acceptance/<case_id>/               Independent results and screenshots
```

Existing outputs are not overwritten; `.env` and run logs remain Git-ignored. Play a saved result with:

```powershell
python -m agent serve runs/<benchmark_directory>/cases/tic_tac_toe_01/game
```

Framework tests, without paid model calls:

```powershell
python -B -m unittest discover -s tests -v
```

Set `MVP_BROWSER_TESTS=1` to include real-browser regression; `PLAYWRIGHT_CHANNEL=msedge` uses installed Edge. All temporary test files belong in `.codex-tmp/` and should be cleaned after testing. Real generated games and traces are final test evidence, not temporary previews.

## Validation record for this round (2026-10-10)

- Final code: **83/83 framework tests passed**, final verification 44.979 seconds, including real Edge interactions, timeout handling, repair, planning-failure fallback and shared budgets. Model responses are simulated; this check makes no paid API requests.
- Real trials used the locally configured `deepseek-flash`. The first batch used 4 API calls. After generic compatibility fixes for plan-format problems, the second used 16, for **20 total**. Failed calls and retries were neither counted separately outside this total nor hidden.
- First batch: tic-tac-toe generated successfully and passed 5/5 independent checks; Sokoban failed planning validation with no game; the other two tasks did not run. Original record: `runs/benchmark_v03_20261010/`.
- Second batch: 8 scheduled cases, 6 executed. The second memory-pairs and brick-breaker runs were skipped for insufficient budget and remain marked skipped. Results: `runs/benchmark_v03_20261010_refined/`.

| Second-batch mechanic | Actual runs | Launchable games | Independent checks |
|---|---:|---:|---|
| Tic-tac-toe | 2 | 2 | Both 5/5 |
| Sokoban | 2 | 2 | Both 5/5 |
| Memory pairs | 1 | 1 | 5/5; the model plan also passed after one automatic repair |
| Brick breaker | 1 | 0 | Planning failed; no game; not a pass |

Model-authored tic-tac-toe and Sokoban plans contained incorrect expectations: for example, labelling an O-winning sequence as an X win, or treating a walkable upper cell as a wall. Some original runs therefore remain `checks_failed`; independent rechecks did not overwrite these scores. The second Sokoban run preserved a launchable version after exhausting the repair budget; independent passes do not erase that exhausted-budget status.

**The paid trials did not use the final planning-failure fallback or the last test-sequence self-check prompt.** Those patches passed the zero-API framework tests above but were not retested end to end with DeepSeek. This experiment did not establish brick-breaker feasibility, and successes in three families cannot be generalized to every game.

Known combined usage: 95,410 input tokens and 51,710 output tokens; zero calls with unknown usage. Without configured prices, no amount is invented; provider billing is authoritative. Prompts and code changed between batches, so their results are not pooled into a “final-version success rate,” nor used to claim a percentage improvement over 0.2.

## Scope and limits

- Vanilla offline single-player/local-multiplayer 2D browser games only; no networking, 3D, prescribed complex engines or arbitrary dependency installation. Report out-of-scope tasks explicitly rather than silently substituting another task.
- No free-form command execution, complex multi-agent system, long-term vector memory or arbitrary JavaScript test expressions were introduced.
- Generated code remains untrusted. Browser, network and subprocess restrictions are not an audited operating-system sandbox.
- Frozen plans prevent repair from lowering standards, but wrong plans can still cause false failures. Preserve original requirements and assess them alongside independent checks and playtesting.
- Final course startup commands and `game/` / `traces/` submission layout still need alignment with official requirements; historical runs currently live under `runs/`.
