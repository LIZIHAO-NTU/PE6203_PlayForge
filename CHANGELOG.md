# PlayForge Changelog

## 1.2.1 — 2026-10-17

- Aggregate up to eight first-known draft errors across at most ten isolated tests; preserve the primary error, distinguish incomplete scans and require full validation before acceptance. No expected values or game rules are inferred or weakened.
- Share blocked-response validation between the live runner and controlled repair evaluation. Accept only an optional bounded string summary alongside blocked; continue rejecting edits, extra fields and invalid evidence.
- Add explicit evaluation-only counter fault injection for real code defects and frozen-test contradictions. Keep its call counts and outcomes separate from autonomous game generation; no game templates or model adapters added.
- Run bounded real-model protocol checks and two full trials each for platform and energy-duel games with unchanged held-out checks. Preserve failures and source-version differences; see RELEASE_1_2_1.md.

## 1.2.0 — 2026-10-17

- Add machine-readable planning-error locations (test, setup/check index, combined step), preserving validation rules and legacy plans. Provide structured details to the next planning attempt without inferring or changing expectations.
- Link repair feedback to frozen scenarios, requirements, failed actions and actual/expected evidence. Keep raw traces and existing bounded repair memory; no extra summarizing API call or new framework dependency.
- Support a validated `blocked` response only after failed verification: cite actual failed tests, disallow mixed file edits, preserve best artifacts and report unverified acceptance. Model fallibility remains; this does not independently prove a test defect.
- Add joint self/independent selected-check metrics and two preregistered mixed-rule fixtures. Record real 1.1.0 default-mode baseline, targeted 1.2.0 trials, failures and repeat checks in RELEASE_1_2.md.
- Research-informed implementation uses original code, not copied agent runtimes: SWE-agent tool feedback, Aider test-after-edit discipline and OpenHands selective context principles are discussed with sources in RELEASE_1_2.md.

## 1.1.0 — 2026-10-16

- Adopt ordinary numeric releases; still an experimental course project, not a guarantee of arbitrary-game reliability. Historical Beta labels and results are preserved.
- Compare optional ordered expected-observation summaries with every literal assertion before freezing; retain legacy indexed summaries/plans and immutable frozen checks. Matching wrong values are still possible.
- Real trials exposed planning overhead: requesting summaries is now opt-in with `--structured-expectations`; default planning retains short textual bases without duplicate lists. Supplied contradictory metadata is always rejected. Final default-mode effectiveness is not established by the paid candidate runs.
- Add native bounded `fill` / `select_option` and form-value observations, with real input/change events. Block password/file/hidden controls and avoid forcing disabled/read-only controls.
- Add independent English fixtures for text/numeric puzzles, platform physics, aiming, local tactics and resource budgets; preserve first failures and separately report targeted follow-ups in RELEASE_1_1.md.
- Add an optional read-only loopback run dashboard. Keep existing CLI, single-agent loop, budgets and vanilla offline-game boundaries; no engine, networking, 3D or new backend.

## 1.0.0-beta.4 — 2026-10-16

- Add trusted `assert_stable` with bounded live samples, wait-budget accounting and immutable assertion protection during plan audit/recovery. It checks sampled equality, not continuous stability or full gameplay correctness.
- Request a short original-spec quote and expected-outcome basis per test; validate supplied metadata and warn about unmatched quotes. Legacy plans remain compatible; model explanations are not ground truth.
- Flag potentially stale real-time equality captures across input events; only a corresponding actual failure triggers conservative review, and runtime/infrastructure errors retain priority.
- Add new English requirements, independent checks, a bounded comparison and a single-command rehearsal. Preserve failures and scope limits; see [TEST_RELIABILITY.md](TEST_RELIABILITY.md). [EXTENSION_PLAN.md](EXTENSION_PLAN.md) is proposal only.

## 1.0.0-beta.3 — 2026-10-14

- Add optional per-test `setup_steps` using the trusted input/observation DSL on each fresh page. Setup and check share one 18-step cap and existing wait budgets; checks still require assertions. Preserve legacy plans, record action stages, and protect setup assertions during late recovery.
- Add zero-API initial-state contradiction inspection and opt-in, one-attempt `--plan-audit` before game generation/freezing. Review sees only specification/draft, preserves requirement/test coverage and assertion observation/operator shapes, records original/revised plans, and cannot edit frozen acceptance. `inspect-plan` exposes read-only inspection.
- Route failed initialization conflicts, repeated identical assertion evidence and uncertain diagnosis to `plan_review_required`, retaining artifacts without manufacturing success. Runtime/infrastructure failures remain distinct; conservative stopping can also stop a real implementation bug early.
- 195/195 tests passed, including 33 real-browser tests; all previous 160 retained. No paid API calls or new real-model effectiveness claims. See [PLANNING.md](PLANNING.md).

## 1.0.0-beta.2 — 2026-10-14

- Conduct a bounded real-model capability screening with DeepSeek: six baseline cases, six optimized cases and one new inventory/capacity variant; 47 API attempts in total. Preserve failures and distinguish self-authored tests from held-out checks. See [CAPABILITY.md](CAPABILITY.md).
- Fix observation interoperability for literal dotted snapshot keys; retain nested paths and fail closed on conflicting representations. Clarify nested snapshots, bounded waits and spec-derived test expectations in prompts. Add missing requirement IDs to planning-validation feedback; never weaken frozen assertions.
- Extend benchmark reporting with evaluation denominators, disagreement counts, run fingerprints and frozen-source integrity checks. Record errors during independent evaluation without losing API accounting. Add evaluation-only fixtures, no prewritten game implementation.
- 160/160 framework tests pass, including 27 real-browser tests; all 143 previous tests remain. Small-sample results do not prove generalization or cost improvement. Planning semantics and fresh-page setup remain important limitations.

## 1.0.0-beta.1 — 2026-10-14

- Rename the 0.5 development snapshot to **1.0 Beta 1**, reflecting the integrated research-beta stage; no functional changes in this version-label update.
- Synchronize runtime version and bilingual documentation. Preserve historical version labels and validation records; this is not a stable-release or unseen-game reliability claim.

## 0.5.0 — 2026-10-14

- Integrate hash-bound partial file replacement into the existing single Agent loop, accepting full responses and falling back to full mode after validation failure; reject deletion, path escapes and incorrect base versions.
- Add local-resource structure checks, optional trusted Node syntax checks and conservative candidate selection that protects previously passed checks.
- Add deterministic failure routing and optional model diagnosis, disabled by default and limited to at most one additional actual attempt within the original budget.
- Add repeated verification requiring all passes within a shared timeout, read-only temporal sampling, before/after screenshots, replay manifests and source/runtime fingerprints.
- Add zero-API `replay` and exact `export-run`, preserving independent benchmark acceptance isolation.
- Add optional generic recovery observations, disabled by default and recorded only for verified recovery under the same plan; reject arbitrary instruction injection, corrupt files and concurrent overwrites.
- Pin tested dependency versions and update bilingual instructions. No external coding-agent runtime or game templates are introduced.

See [INTEGRATION.md](INTEGRATION.md) for staged checks, integrated regression and limits. No new paid-model experiment was run; no claim of improved unseen-game success or cost is made.

## 0.4.0 — 2026-10-14

- Add a separate deterministic completion gate: missing, duplicate, unknown or failed test evidence does not pass; startup checks cannot replace core interaction rules.
- Add test-purpose tags and non-destructive quality warnings. Legacy plans remain usable; tags or assertion counts do not prove semantic correctness.
- Add read-only `assert_consistent` to compare actual DOM observations with live state snapshots and locate synchronization errors; no state-mutating test interface is introduced.
- After planning fallback, attempt one functional-plan recovery within the original call/time budget; preserve the original plan, requirements and assertions, then freeze the recovered plan, retest and repair.
- Use the same completion gate for generation, independent evaluation and zero-API rechecks; preserve raw verification results and controller decisions, and expand audit checkpoints.
- Strengthen prompts for a single authoritative state, discrete key input and test expectations; no multi-agent system, game template or external runtime is added.

See [QUALITY.md](QUALITY.md) for results and boundaries. This release adds no paid-model trials and cannot establish improved success on unseen mechanics.

## 0.3.0 — 2026-10-10

Goal: prioritize runnable games across different underlying mechanics, without prewriting an implementation template for a particular game.

- Add real-time/turn-based interaction and rule-invariant analysis, prioritizing mandatory features over visual polish.
- Add coordinate clicks, Canvas scaling, hover, drag, simultaneous keys and more DOM observations.
- Add recent repair working memory, repair from the better candidate, duplicate-code detection and more detailed action records.
- Improve state-contract compatibility, allow manual review alongside automatic checks, and preserve raw responses and acceptance conditions.
- Add explicitly labelled planning-failure fallback; startup-only evidence is not functional success, and `--strict-plan` disables fallback.
- Add four requirement families, preregistered independent checks and a `benchmark` command with a shared API cap.
- Expand installation, configuration, playtesting, evaluation, collaboration, historical notes and safety boundaries.

Validation: 83 framework tests passed; real DeepSeek trials used 20 calls in total. Three families produced launchable games passing selected independent checks; brick-breaker planning failed. The final fallback patch was not retested with the paid model and does not guarantee success on unseen games. See [GENERALIZATION.md](GENERALIZATION.md).

## 0.2.0 — 2026-10-09

- Add feedback-driven `wait_until`, `key_until`, `move_to` and canvas-size observations.
- Add failure categories, plan-risk warnings, requirement-level proportions and a zero-API independent recheck entry point.
- The recorded result was 54 framework tests passed and 7/7 independent checks passed on the existing collector game; this is not an unseen-requirement success rate.
- Preserve the original account in [UPGRADE.md](UPGRADE.md).
