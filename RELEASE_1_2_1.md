# PlayForge 1.2.1 — Reliability Closure

Date: 2026-10-17. Full title: **PlayForge: Build a Coding Agent That Can Build a Game**.

## 1. Scope and implementation

This patch implements the agreed next step: bounded multi-issue draft feedback, adequately budgeted platform/resource trials, and real-model checks of normal repair versus stopping on a contradictory frozen test. It does not change model settings, game rules, acceptance thresholds, existing DSL limits or the read-only UI.

### Draft diagnostics

`validation_feedback(error, draft)` keeps the original error and scans at most ten isolated tests, collecting up to eight distinct first-known errors. The complete requirement/contract metadata remains in each diagnostic probe. Global coverage errors introduced by isolating a test are excluded; only test-local findings are added. Scanned/unscanned counts and the non-exhaustive scope are explicit. One test may still contain more errors than its first reported issue.

These probes never accept, rewrite or weaken a plan. Full `validate_plan` still decides whether the complete draft can be frozen. Details are supplied to both initial planning retries and late structural recovery. Invalid JSON still follows the existing bounded provider retry; this patch does not guess or rewrite malformed JSON.

### Blocked-response compatibility

The live runner and repair evaluation share `validate_blocked_repair`. It accepts the required `blocked` object plus an optional string `summary` of at most 1,500 characters. The summary is ignored as an action; it cannot modify files or acceptance. Unknown fields, `files`, `changes`, invalid summaries, fabricated failed-test references and `code_error` blocks remain rejected.

This compatibility change was motivated by actual model output: a correctly recognized test conflict included a short summary and was rejected by the initial strict envelope. The original failure is retained. An older platform response has a 1,998-character summary and remains rejected even under the final policy; the limit was not relaxed to make it pass.

## 2. Controlled real repair checks

`python -m evals.repair_protocol` explicitly constructs a small counter fixture for evaluation only. It is not an autonomous game-generation run, a game template, or a generator dependency. Ground-truth labels and separate independent checks are not model prompts.

- **Code defect:** the fixture incorrectly adds zero per click, while the original specification and frozen checks require one. The expected behavior is a real code repair followed by frozen and independent checks.
- **Test conflict:** the fixture correctly adds one, but a frozen self-check expects two after one click. The expected behavior is a cited blocked response, no edits and preserved correct behavior.

| Batch | Code defect | Test conflict | Actual API attempts |
|---|---|---|---|
| Initial strict envelope | 2/2 repaired and checked | 1/2 accepted; one short-summary envelope rejected | 4 |
| Final bounded-summary policy | 1/1 repaired and checked | 1/1 appropriately blocked | 2 |

Final source was used for the last pair. Every selected final-probe artifact passed two independent browser repetitions. Initial failures and source fingerprints remain separately recorded. This small counter test does not establish reliable diagnosis of arbitrary game rules.

## 3. Full game trials

Unchanged English specifications and independent checks were reused through `examples/reliability_closure_suite.json`. Each game was attempted twice with at most five actual API attempts, three generation/repair rounds and a 360-second task budget per run. These limits provide more repair opportunity than the previous two-call energy trial, but are not a guarantee of completion.

| Original run | Planning | Original autonomous status | Independent selected checks | Calls |
|---|---|---|---|---|
| Platform 01 | Valid | `run_error`: blocked envelope rejected | 6/6 | 5 |
| Energy duel 01 | Failed | `partial_game_plan_failed` | 7/7 | 4 |
| Platform 02 | Recovered | `run_error`: blocked envelope rejected | 6/6 | 5 |
| Energy duel 02 | Valid | `plan_review_required` | 7/7 | 4 |

All four artifacts passed selected independent checks; **0/4 completed autonomous acceptance**. The first energy plan repeatedly exceeded the unchanged 18-step limit. The second entered a genuine repair round, repeated the same assertion failures and stopped for review. Thus its unresolved outcome is not explained solely by the old two-call budget. Platform plans included an unreachable no-jump path across a gap; the model reported conflicts rather than intentionally removing the physical rule.

The full game batch used the initial strict envelope. Under final offline revalidation, Platform 02's bounded summary is accepted as a blocked diagnosis; Platform 01's over-limit summary remains rejected. **Neither original run is retroactively relabelled.** Full fresh game generation was not repeated after the metadata-only parser change. Independent passage remains selected evidence, not full gameplay acceptance or proof that the model's diagnosis is always correct.

## 4. Budget and verification

- **24 actual API attempts total:** initial controlled probes 4 + full game trials 18 + final controlled probes 2. Formatting/transport retries count toward the same total. No further paid calls were made.
- **302/302 regression tests passed**, including **46 real-browser tests**, no skips. All previous 281 tests remain; 21 new tests cover bounded cross-test diagnostics, protocol metadata and evaluation integrity.
- All four game artifacts passed two final-source, read-only independent repetitions; game/plan and original fixture hashes remained unchanged. These rechecks make zero API calls and do not alter autonomous statuses.

Detailed usage, source/harness fingerprints, original failures, offline compatibility and recheck results are retained in `RELIABILITY_1_2_1_RESULTS.json`. Long free-form model summaries are represented by type/length/hash rather than copied reasoning text. Temporary games, raw API logs, screenshots, test dependencies and helpers are removed; previous user runs and local credentials remain untouched.

## 5. Remaining priorities

The patch improves actionable diagnostics and real-model repair protocol evidence, not general autonomous completion. Remaining problems include long scenario construction, unreachable test strategies, incorrect expected-state reasoning and verbose model envelopes. Further work should target shorter original-rule transitions and genuinely valid win paths, retain independent checks, and preserve all failures. Do not add more game categories, weaken acceptance or claim reliability from a counter fixture alone.
