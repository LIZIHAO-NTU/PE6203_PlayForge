# PlayForge — Capability Screening

Date: 2026-10-14. Evaluated release: `1.0.0-beta.2`.

This report is historical. Beta 3 planning improvements and zero-API verification are documented in [PLANNING.md](PLANNING.md); the paid results below remain Beta 2 evidence.

## 1. Decision

The agent generated working artifacts for six simple mechanic families and one new inventory/capacity variant. Every generated artifact passed the selected independent checks. However, self-authored planning remains unreliable: incorrect grid assumptions, cross-test state assumptions and overlong tests still occur. **Keep the offline 2D browser platform; improve planning semantics before promising broader or more complex game support.**

These are feasibility samples, not proof of a 100% game-development success rate. One generation per case/version cannot establish stable generalization, and selected checks do not exhaust the specification.

## 2. Protocol

- Baseline: Beta 1 at Git commit `854ee6b83598e6ec1431e7f81545722b303927ee`; six generated games, 24 API attempts.
- Optimized: Beta 2; the same six specifications, independent plans, per-case limits and feature settings; six generated games, 19 attempts.
- Transfer probe: one new finite-inventory/carrying-capacity variant, frozen before its first generation; four attempts.
- Configured model: `deepseek-flash` at the existing DeepSeek endpoint. Python 3.11.9, Playwright 1.63.0, Edge 155.0.4283.45 on Windows.
- Per case: at most five API attempts, three generation/repair rounds, 420 seconds; browser verification timeout 60 seconds. Transport/format retries count. Batch caps were 30, 24 and 5; actual use was **47 attempts**, within the task-wide 48-attempt cap.
- No manual game-code changes during generation. No game templates, solver, state setters, external agent runtime or engine were added. Independent plans were not supplied to generation or repair.

The shared cap applies within each `benchmark` invocation, not automatically across separate commands. This task tracked the sum before starting each batch. There were no skipped cases or unknown-usage calls. Known usage: 244,811 input tokens and 127,727 output tokens. Pricing fields were not configured, so the actual billed amount is unknown; consult the provider bill.

## 3. Paired results

“Self” means the agent's frozen plan passed, not complete human acceptance. “Independent” means all selected held-out checks passed; they remain partial coverage.

| Case | Baseline calls | Beta 2 calls | Self baseline → new | Independent baseline → new |
|---|---:|---:|---|---|
| Tic-tac-toe | 5 | 2 | Fail → Pass | 5/5 → 5/5 |
| Sokoban | 5 | 4 | Fail → Fail | 5/5 → 5/5 |
| Memory pairs | 2 | 2 | Pass → Pass | 5/5 → 5/5 |
| Brick breaker | 5 | 3 | Fail → Pass | 5/5 → 5/5 |
| Resource shop | 4 | 4 | Fail → Fail | 5/5 → 5/5 |
| Key maze | 3 | 4 | Pass → Fail | 5/5 → 5/5 |
| Total | **24** | **19** | **2/6 → 3/6** | **30/30 → 30/30** |

The new inventory/capacity variant passed 6/6 independent checks but failed planning with more than 18 steps per test, remaining `partial_game_plan_failed`. It must not be counted as a successful autonomous self-verified run.

The observed reduction from 24 to 19 calls is descriptive, not a causal efficiency claim: one stochastic sample per case, changed prompts and changed verification behavior cannot isolate effects. The maze self-test regression is retained explicitly. Neither version received independent-check feedback during generation.

## 4. Changes made

1. **Snapshot interoperability.** The planner describes paths such as `board.4`, but baseline code sometimes returned literal dotted keys while the verifier required nested arrays. `lookup` now reads either representation without mutating the snapshot. Conflicting flat/nested values fail closed; missing or incorrect values remain failures. Prompts prefer fresh nested snapshots.
2. **Actionable planning feedback.** Missing automated/manual requirement coverage now identifies the exact IDs. Prompts clarify individual wait/hold bounds, encourage short covered tests, and require expectations to follow the original grid/rules rather than genre assumptions or unspecified terminal internals.
3. **Evaluation integrity.** Reports separate scheduled, attempted and independently evaluated cases, retain both disagreement directions, record run fingerprints/limits, and reject changed specification/acceptance files. Errors during post-generation evaluation preserve call accounting and are marked as benchmark errors.

No acceptance thresholds, expected values or frozen model assertions were lowered. Existing generated games and original scores were not edited. New files under `examples/benchmark/` contain requirements and test plans only, not game implementations.

## 5. Verification

- **160/160 framework tests passed**, including **27 real-browser tests**; all prior 143 tests remain. Final full run: 137.681 seconds. Model calls in framework tests are simulated and cost zero API credits.
- Each of the seven Beta 2 artifacts passed **two repeated independent verifications**, within a shared 60-second budget per artifact. All source/plan integrity checks passed. These repetitions test the same artifacts, not seven additional generations.
- A zero-API replay of the original first-round flat-snapshot tic-tac-toe against its original self-plan improved from 0/6 to 3/6 checks after the reader fix. The remaining failures persisted. Original source/plan hashes and score remained unchanged; this isolates reader compatibility, not model-generation improvement.
- Screenshot spot checks covered key-maze terminal rendering, brick-breaker first collision and resource-shop winning counters. They supplement traces, not full interactive human acceptance.

## 6. Unresolved weaknesses

### Priority 1: planning semantics

Sokoban still assumes an inner floor is a wall. Resource-shop tests assume the previous test's state survives, although every test starts on a fresh page. Maze planning includes incompatible expectations about a locked door. The inventory probe still exceeds the DSL step limit. Structural validation and stronger prompts alone do not reliably catch these errors.

Next useful work: require each test to declare/reproduce its own initial setup, review legal transition sequences before freezing, and use bounded diagnosis when fixed-test failures are ambiguous. Such review is itself fallible and must never rewrite expectations to match generated code or turn uncertainty into success. This evaluation did not add a paid review stage.

### Priority 2: depth and variability

The independent brick checks cover startup, movement, pause, one collision and reset—not all-brick victory or every life-loss scenario. The tiny maze and one-crate Sokoban do not establish larger-level planning. There is only one requirement per family per version; model/backend sampling variation is not characterized.

## 7. Expansion decision

Keep vanilla offline local 2D browser games. Resource economy, key/door combination and finite inventory/capacity are promising **evaluation directions**, not newly guaranteed supported genres. Do not add 3D, networking, a backend, remote assets or an engine on the strength of these samples.

Before deeper expansion, choose two new requirements for a target family and generate each three times with fixed budgets. A possible internal gate is at least 5/6 full mandatory-check passes with no repeated critical-rule bug and no regression in established cases. This is a small engineering gate, not statistical proof of reliability. Agree on a new API budget before running it.

## 8. Evidence and reuse

[CAPABILITY_RESULTS.json](CAPABILITY_RESULTS.json) contains sanitized per-run usage, hashes, settings, outcomes and repeat-verification summaries. Full API traces, generated games and screenshots stay local under these ignored directories:

~~~text
runs/capability_baseline_20261014/
runs/capability_beta2_20261014/
runs/capability_transfer_20261014/
runs/capability_repeat_20261014/
runs/capability_snapshot_recheck_20261014/
~~~

Same-suite screening commands (these test the currently checked-out version and incur new API charges; separate invocations do not automatically share a total budget):

~~~powershell
python -m agent benchmark examples/benchmark/capability_suite.json --max-total-calls 24 --max-calls-per-case 5 --max-rounds 3 --max-seconds 420
python -m agent benchmark examples/benchmark/transfer_suite.json --max-total-calls 5 --max-calls-per-case 5 --max-rounds 3 --max-seconds 420
~~~

To reproduce the baseline, use its recorded commit in a separate checkout; do not reset or overwrite an active teammate's work. A fresh GitHub clone contains fixtures and sanitized results, not the historical generated games.
