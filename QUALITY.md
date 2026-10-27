# PlayForge — MVP 0.4 Quality Checks and Planning Recovery

The goal is to reduce outcomes that start successfully but lack verified rules, while retaining the single Agent, existing DeepSeek-compatible interface and call budget. No game-specific implementation or solver is prewritten. These checks are ordinary Python controller logic and require no separate Agent tool installation.

## Completion conditions

`agent/quality.py` recomputes completion from actual evidence rather than trusting a verifier's single `ok` flag:

- Visible startup passes, with no runtime or infrastructure errors.
- Every test in the fixed plan has exactly one result: no missing, unknown or duplicate IDs, and all explicitly pass.
- The functional plan is valid and contains at least one core-rule assertion after an input event. Page visibility or equality between display and snapshot alone cannot replace expected behavior.

A pass means the selected automatic checks passed; full game acceptance remains unmeasured. Structural gates do not prove expected values are correct or that the model fully understood the original requirement. Human playtesting and preregistered independent evaluation remain necessary. Independent evaluation is not fed back into generation or repair for that run.

`review_plan` only warns; it does not rewrite the plan. Warnings cover observation-only tests, missing labelled invalid-action/reset/terminal scenarios and missing display/state cross-checks. Legacy plans do not need tags to run. Tags are review clues, not coverage proof; do not add game features for inapplicable categories.

## Read-only consistency checks

After actual operations, the new action reads the DOM and the game's live snapshot without modifying state:

```json
{"action":"assert_consistent","source":"text","selector":"#moves","state_path":"moves","coerce":"number"}
```

Supported observations: `text`, `count`, `attribute`, `enabled` and `surface`. Parameters match the existing DSL: `attribute` needs an attribute name; `surface` needs a property. Coercion permits only `none` or bounded numeric conversion, never arbitrary expressions.

For example, if the page shows a crate's new position but `getState()` returns its old position, the check produces `state_dom_mismatch` and passes that evidence to repair. Ordinary `assert` checks against original-rule expectations are still necessary: both sides can agree and both be wrong. Do not compare continuously moving coordinates observed at different times as a stable consistency check, or add UI absent from the original requirement merely for testing.

## Bounded recovery after planning failure

1. Try the original two functional-planning attempts; `--strict-plan` still stops on failure.
2. Non-strict mode may generate a game from the original requirement and check startup first; this is not functional success.
3. If startup succeeds and at least one call and 15 seconds remain, make one functional-plan recovery request. It receives only the original requirement, previous invalid plan and structural errors, not game source or independent benchmark checks.
4. The controller validates recovery: it must not delete existing requirements, change their text/priority/verification method, or delete/modify original assertion objects. Core interaction checks are required. Otherwise, preserve the unverified status.
5. On recovery, freeze the new plan at `traces/functional_plan.json` and immediately retest existing code; if checks fail, continue repair within remaining rounds. Preserve the previous startup plan and raw responses. Do not overwrite historical results or compare candidate scores against the old startup-only results.

Recovery has one logical request, although the API adapter can still retry internally. All actual attempts count toward the original `--max-calls`, and time counts toward `--max-seconds`; no hidden allowance is added. Failed recovery or insufficient budget preserves the game as `partial_game_plan_failed`. A structurally valid plan without core interaction evidence records `partial_game_evidence_missing`, rather than repeatedly changing code to hide insufficient testing.

This is conservative structural recovery, not automatic correction of wrong rule expectations. Contradictory original assertions remain unverified; expectations cannot be changed to manufacture a pass. Independent requirement review may be investigated later; this release adds no extra reviewer-model calls.

## Records and reproduction

- `summary.json` adds `quality_gate`, `plan_quality`, `active_plan`, `planning_recovery_attempted`, `planning_recovered` and initial/current plan hashes.
- Each round preserves raw verification, gate-enriched results, state and step-by-step action evidence. Plans and verification results before/after recovery are kept separately.
- `traces/state.json` records the active plan, repair memory, better version and remaining budget. It is an audit checkpoint, not a guarantee of automatic resumption after a process crash.
- Commands and default budgets are unchanged. After functional-plan recovery, zero-API rechecks should use the file identified by `active_plan` in `summary.json`.
- A single authoritative state, snapshot/render consistency and ignoring repeated discrete key events where appropriate are generation-prompt requirements; compliance still needs actual testing.

## Validation boundaries

Framework tests use simulated model responses; browser tests perform actual Edge operations without spending model credits. They cover discovering and repairing a rule error after planning recovery, shared-budget exhaustion, preserved artifacts after recovery failure, unchanged requirements, missing/duplicate evidence and stale snapshots despite a working display. No new paid DeepSeek end-to-end experiment was added, so no unseen-game success rate or percentage improvement is reported.

2026-10-14: the final full regression passed 109/109 tests, including 21 real-browser tests, in 52.180 seconds. The same three read-only checks were also replayed on historical Sokoban artifacts: original version 1/3, detecting `state_dom_mismatch` and a failed completion assertion; previously repaired version 3/3. Replay changed neither historical game nor development score and is not the new release's autonomous generation success rate. Temporary dependencies and test artifacts were removed at task completion.
