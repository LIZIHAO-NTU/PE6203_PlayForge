# PlayForge — Plan-Audit On/Off Comparison

Date: 2026-10-14. Fixed agent: `1.0.0-beta.3`, commit `1f8c548a279718ebea6221da4bbe30d0752463ae`.

## 1. Decision

**Keep `--plan-audit` opt-in/off by default.** In this small DeepSeek sample, the current review path did not improve independently confirmed delivery. It sometimes found real mistakes, but two invalid review responses blocked game generation and an approved review missed turn/winner errors. Improve review response reliability and failure handling before enabling it by default or expanding the game platform.

Agent source and prompts were NOT changed during or after the comparison. The existing default was already off, so no implementation change was needed to apply this decision. No GitHub push was performed for this evaluation-only task.

## 2. Frozen protocol

- Four new requirements: one-way grid gate, stamp exchange arithmetic, last-stone-loses terminal rules, and energy/bridge combination. Each has six independent selected checks, authored before either condition ran.
- Eight end-to-end task attempts: each requirement once with audit off and once on. These are independent stochastic drafts, not the same draft reused. No seed control or repeated generation per condition.
- Order: gate off/on, exchange on/off, stones off/on, energy on/off. Two pairs per order reduce but do not remove time/cache effects.
- Per task: six API attempts, three generation/repair rounds, 420 seconds; verifier timeout 60 seconds. The audit consumes part of the same six-attempt cap, not extra calls.
- Same model/configuration, agent-source fingerprint, specifications and acceptance hashes, repair mode `auto`, one verification repetition, diagnosis/syntax checks/lessons disabled. Only the assigned audit switch differs.
- Independent checks were not supplied to the generation/review model or used for repair in this comparison.
- Configured model `deepseek-flash`; Python 3.11.9, Playwright 1.63.0, Edge 155.0.4283.45, Windows. No game templates, solvers or manually edited generated games.

All eight assigned tasks ran. Actual use: **24/48 API attempts**, 119,910 input tokens and 67,408 output tokens; no unknown-usage calls. The unused budget was not spent on retries or new conditions. Price fields were not configured, so actual monetary cost is unknown; consult provider billing.

## 3. Results

“Independent delivery” means an artifact exists and all selected independent checks passed. It is not complete human gameplay acceptance. Missing artifacts remain missing evidence, not proof of an incorrect implementation.

| Measure | Audit off | Audit on |
|---|---:|---:|
| Assigned | 4 | 4 |
| Artifacts produced | 4 | 2 |
| Independent evaluated | 4 | 2 |
| Independently confirmed delivery | 4/4 | 2/4 |
| Independent pass among evaluated | 4/4 | 2/2 |
| Self-plan passed | 2/4 | 0/4 |
| API attempts | 12 | 12 |
| Actual audit attempts | 0 | 3 |
| Repeated identical assertion events after repair | 2 | 1 |
| Invalid code-bundle rounds | 1 | 0 |
| Sum elapsed including stops/acceptance | 216.874 | 165.061 |

The lower audit-on time includes two early stops before code generation; it is NOT a speed improvement. Fewer repairs also coincide with fewer generated artifacts, not proof of better diagnosis. Both arms used 12 attempts, but produced different numbers of independently checked artifacts; token/cache differences do not establish a money-saving claim.

| Requirement | Off: calls; self; independent | On: calls; audit; self; independent |
|---|---|---|
| One-way gate | 2; pass; 6/6 | 2; invalid review; fail; no artifact |
| Stamp exchange | 3; fail; 6/6 | 2; invalid revision; fail; no artifact |
| Last stone loses | 3; pass after repair; 6/6 | 4; approved; fail; 6/6 |
| Energy bridge | 4; fail; 6/6 | 4; not applicable; startup-only; 6/6 |

Audit actually ran in **three of four on assignments**: two responses were rejected; one was approved. Energy planning was structurally invalid before review, so its audit status is `not_applicable`; its result must not be attributed to an executed semantic audit.

## 4. What failed

### Gate: response contract failure

The reviewer returned `status=revised` and issues but omitted the mandatory complete `plan`. The controller rejected it as `Missing supported boolean` and stopped before generating code. Manual tracing found no executable expected-value contradiction in the seven draft tests; some descriptions were awkward, but their actual input/expected sequences were consistent with the specification.

### Exchange: useful detection, unusable revision

The off plan's `T3` clicks Buy at initial coins=7, then wrongly expects coins=7/stamps=0. The correct result is coins=4/stamps=1. A code repair did not change this contradictory assertion, and the conservative routing stopped rather than manufacturing a pass.

In the on draft, `T3` compares numeric stamp state with a string, and `T4` assumes three purchases are affordable from seven coins at cost three. The reviewer corrected those errors but added redundant setup assertions to `T5`, increasing its combined steps from 18 to 20. The revision violated the existing cap and was rejected. We did not remove assertions or raise limits after seeing this failure.

### Stones: incorrect approval

After A takes two then B takes two, one stone remains and it is A's turn. Audited tests `T4`/`T5` expect B; `T5` also consequently expects the wrong loser/winner. The reviewer approved this draft. The resulting game followed the original rules and passed independent checks, but failed its self-plan twice. In the off condition, a genuine restart implementation bug was repaired and both check sets passed.

### Energy: map assumptions and schema limits

The off plan's `T2`, `T3`, `T5`, `T6` assume the initial right move enters a closed bridge and spends energy. It should be blocked for zero cost, so later positions, switching and exhaustion expectations are wrong. `T2` additionally compares the combined position text to scalar x. One repair response was an invalid bundle; a later valid repair left the same assertions failing, and the independent artifact remained correct on selected checks.

The on condition exhausted its planning/late-recovery schema attempts on the 18-step limit, never ran the audit, and retained startup-only self-verification. Its game still passed the independent selected checks. It is not a successful autonomous self-verified run.

## 5. Wrong-test counts and limitations

Manual review counted **distinct erroneous test IDs**, not failed attempts or individual assertions. Off had five confirmed erroneous tests across four available functional plans (23 tests reviewed). On had two confirmed erroneous tests in its only available frozen functional plan (six tests reviewed). Its rejected exchange draft also had two confirmed errors. Blocked or startup-only conditions are not assigned zero semantic errors.

These denominators and available cases differ, so **5 versus 2 is not an error-reduction rate**. Review was performed after runs by the same assistant that authored the fixtures, not blinded external adjudication. Evidence and labels are recorded per run in [AUDIT_COMPARISON_RESULTS.json](AUDIT_COMPARISON_RESULTS.json).

The drafts were independently sampled, not paired copies of one draft. One sample per requirement/condition cannot estimate a reliable success-rate difference or isolate audit effects from planner randomness. Independent acceptance covers selected rules, not every possible gameplay branch. No arbitrary-unseen-game guarantee follows.

## 6. Verification and retained evidence

All four new acceptance plans were structurally validated before spending credits. Source/specification/acceptance hashes and paired budgets/settings were checked unchanged. All six generated artifacts passed their independent checks again in **two zero-API repetitions each**, with source/plan integrity checks passing. This is repeated testing of the same six artifacts, not twelve extra generation samples.

Screenshot spot checks confirmed energy-bridge rendering at a zero-energy win and stones showing the correct losing actor/winner. They are not full human interactive acceptance. Agent code was unchanged, so this task did not rerun or claim a new 195-test framework result; that earlier record remains in [PLANNING.md](PLANNING.md).

Final shared files: this report, sanitized JSON, and the four specification/acceptance pairs plus suite in `examples/audit_comparison/`. Raw logs, protocol, original plans, games and screenshots stay local in `runs/audit_comparison_20261014/`, including `repeat_acceptance/`. Temporary dependencies/scripts were removed; secrets are not included in shared results.

## 7. Next decision

Do not enable review by default or add engines/networking/3D based on this batch. The most useful next implementation would be a smaller structured review response (specific test edits rather than regenerating a whole plan), local limit/commitment validation, and a clear unverified-artifact path when review fails. Any fallback must keep unresolved tests unresolved, never silently treat the original plan or game as passed. Compare such a change in a new, separately authorized experiment; do not patch and rerun only this batch's failures to improve the published score.
