# PlayForge 1.2.0 — Planning and Repair Evidence

Release: 2026-10-17. Evaluation began: 2026-10-16, Asia/Shanghai.

Full title: **PlayForge: Build a Coding Agent That Can Build a Game**.

## 1. What changed

This release prioritizes the first parts of the agreed roadmap: establish the actual 1.1.0 default-mode baseline, improve planning/repair feedback, and test two mixed mechanics. It preserves the single-agent loop, provider settings, immutable acceptance, native input tools, bounded retries, best-version retention and read-only dashboard. It does not introduce a new model provider, game engine, prewritten game template, arbitrary execution tool or multi-agent runtime.

### Located planning errors

`PlanValidationError` remains a `ValueError` but exposes `location` and `detail`. Validation identifies the test ID, setup/check array index and combined action number. The next planning attempt receives these details alongside the original error and execution contract. Context-local state is reset on both success and failure, including concurrent validation. Accepted semantics, expected values and frozen tests are unchanged.

For example:

~~~text
tests[6] (T7).steps[0] (combined step 1): Invalid state path
~~~

This improves diagnosis, not guaranteed model compliance. Real follow-ups still contained invalid JSON, a test without an assertion and an over-limit goal timeout. The controller rejected them and preserved partial artifacts rather than calling them functional success.

### Evidence-linked repair

`agent/feedback.py` links failed tests to their frozen scenario, related requirements, setup length, failed action and ordinary-input reproduction. Existing compact feedback retains actual/expected observations and recent action logs. Up to three scenarios are included, with a 16,000-character scenario-list bound and explicit omitted counts; full evidence remains in traces. Passed test IDs remain visible as regression constraints.

The original specification and frozen plan remain available. Scenario requirements and model explanations are claims, not independent truth. This is not a whole-prompt token cap or an LLM memory condenser, and no measured cost/latency reduction is claimed.

### Explicit blocked repair

After recorded failed verification, the coder may return only:

~~~json
{"blocked":{"category":"test_issue","reason":"Original-rule and observation evidence","evidence_test_ids":["T1"]}}
~~~

Allowed categories are `test_issue`, `tool_limit`, and `uncertain`. Cited IDs must be actual failed tests. Initial-generation blocks, mixed file edits, nonexistent evidence and a `code_error` block are rejected. A valid block writes no candidate files, preserves the best artifact and frozen plan, and ends with `plan_review_required`, never successful acceptance. It consumes no extra diagnostic call: this is an alternative response to the existing repair call.

This relies on the model recognizing and reporting a conflict. It cannot prevent every incorrect repair or prove the test is wrong. **No paid run in this batch returned `blocked`.** The controller behavior was verified with simulated model responses and an actual browser mismatch/recheck. Real-model adoption remains to be evaluated further.

### Joint selected-check metrics

The benchmark adds `joint_selected_checks_passed` and `joint_selected_checks_rate_over_attempted`. Both self-plan and independent selected checks must pass; absent independent evidence does not count as confirmed success. Full-game/manual acceptance remains separate. Historical reports are not rewritten.

## 2. Real-model results

Model configuration: DeepSeek `deepseek-flash`; same endpoint/settings throughout. Structured expectation requests and plan audit remained off by default. Windows, Edge, Playwright 1.63.0. **30 actual API attempts** in total, including format/transport retries; token usage is retained in `RELIABILITY_1_2_RESULTS.json`, not converted into an invented bill.

| Version/batch | Case | Original autonomous result | Independent selected checks | Calls |
|---|---|---|---|---|
| 1.1.0 baseline | Word lock | Self-pass, but independent failure | Failed | 3 |
| 1.1.0 baseline | Number dial | Selected checks passed, manual pending | Passed | 3 |
| 1.1.0 baseline | Platform hop | Budget exhausted | Passed | 4 |
| 1.1.0 baseline | Aim range | Selected checks passed, manual pending | Passed | 3 |
| 1.1.0 baseline | Tactical duel | Partial game, plan failed | Passed | 3 |
| 1.1.0 supplement | Market budget | Selected checks passed, manual pending | Passed | 3 |
| 1.2.0 follow-up | Word lock | Selected checks passed, manual pending | Passed | 2 |
| 1.2.0 follow-up | Platform hop | Partial game, plan failed | Passed | 4 |
| 1.2.0 mixed rules | Signal vault | Selected checks passed, manual pending | Passed | 3 |
| 1.2.0 mixed rules | Energy duel | Budget exhausted | Passed | 2 |

The initial baseline batch used its 16-call cap before the market case could run. That original skipped row is retained. Market was subsequently run as a separate three-call supplement using an archived 1.1.0 implementation. Tracked source content matches the base commit after newline normalization; raw fingerprints differ due to newlines and an unreferenced copied helper. The supplement is explicitly recorded and excluded from the matched word/platform comparison.

Across six distinct baseline cases: self checks passed 4/6, independent selected checks 5/6, joint checks 3/6. Across four candidate cases: self checks passed 2/4, independent selected checks 4/4, joint checks 2/4. **These are different case sets and cannot be used as an improvement percentage.** Each matched pair also has only one stochastic run per version.

The word follow-up no longer showed the observed counter error. Platform planning remains unresolved; the energy duel's first game passed independent checks but failed a self check, and its remaining repair call could not run under the two-call allocation. Both remain unverified autonomous outcomes. Frozen independent checks never entered generation or repair prompts.

## 3. Preserved counterexample

The baseline word game initially counted every non-empty answer, including the correct one, as required. Its frozen self-test incorrectly expected zero attempts after a first correct answer. The agent changed the implementation to satisfy that test and then reported self-pass. Independent checks caught the rule violation. Two read-only repetitions confirm: the initial artifact passes selected independent checks; the repaired artifact fails them. Original statuses remain unchanged.

This is why the release adds a truthful stop path and joint evidence reporting instead of allowing post-hoc test edits. The new path is an engineering safeguard, not a solved general rule oracle.

## 4. Mixed-rule scope

- **Signal Vault:** public text/code clues, native selection, answer costs, attempt counting, capped recharge, terminal locks and reset. Seven independent selected tests, with visible counters and state consistency observations.
- **Energy Duel:** local alternating turns, attack costs, capped charging, insufficient-resource no-ops, both reachable winners, terminal lock and reset. Seven selected tests, mostly observing public DOM counters.

## 5. Verification

**281/281 framework tests passed, including 45 real-browser tests, no skips and no paid API calls.** All previous 254 tests remain; 27 new tests cover located errors, context isolation, feedback integrity, blocked repairs, evidence validation, joint metrics and mixed fixtures. A browser test confirms a deliberately wrong frozen expectation remains failed while the preserved game passes a separately correct plan.

All ten final artifacts were replayed twice through the unchanged independent plans under final 1.2.0 code. Nine passed; the known bad baseline word repair remained failed. Its initial artifact also passed twice. All game/plan and fixture integrity checks passed. Replays make zero API calls and do not replace original autonomous results. Raw intermediate games, screenshots, API logs and dependencies are task-temporary; sanitized evidence and fixtures are retained.

## 6. External ideas and boundaries

- **SWE-agent:** explicit command documentation and format-error guidance informed actionable validation locations. Reference: [historical command documentation](https://swe-agent.com/0.7/config/commands/). PlayForge still uses its own validated browser-action DSL; no SWE-agent runtime or commands were copied.
- **Aider:** automatic lint/test-after-edit reinforces the existing verify-after-change loop. Reference: [linting and testing](https://aider.chat/docs/usage/lint-test.html). That loop already existed here; this release does not claim to invent it or enable arbitrary model-chosen host commands.
- **OpenHands:** preserving important goals, technical constraints and failure context informed selective scenario feedback alongside raw traces. Reference: [Context Condenser](https://docs.openhands.dev/sdk/guides/context-condenser). No OpenHands SDK, extra summarizing model or reported external performance gains are imported.

## 7. Deferred work

Still deferred: interactive generation/cancellation UI, broader visual/black-box validation, more repeated mixed variants, multiple-error draft feedback, instructor-specific model adaptation, networking, 3D and engines. The existing dashboard remains read-only; CLI startup and model settings are unchanged. Next prioritize the remaining schema/oracle weaknesses and real-model repair-protocol behavior before claiming broader support.
