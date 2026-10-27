# PlayForge 1.1.0 — Bounded Expansion

Release date: 2026-10-16. Full title: **PlayForge: Build a Coding Agent That Can Build a Game**.

## 1. Scope and version

This release follows the proposed sequence: expected-outcome agreement, form tools, selected new mechanics, then an optional status viewer. It keeps the single-agent controller, existing budgets, immutable frozen assertions and offline vanilla HTML/CSS/JavaScript scope. No prewritten game templates, solver, engine, network service or 3D support was added.

Version `1.1.0` denotes a backward-compatible feature expansion, not an instructor-grade or production reliability claim. Future fixes can use `1.1.1`, additive features `1.2.0`, and incompatible architectural changes `2.0.0`. Historical Beta results keep their original labels.

## 2. Expected outcomes

Optional `test.evidence.expected_observations` is an ordered list of `{"value":...}` records, one per literal `assert` in combined setup/check order. Legacy `{"step":...,"value":...}` records remain supported. Provided lists must cover all literal assertions, preserve value types, agree with their thresholds and fit existing bounds. An empty list is valid only when there are no literal assertions. This runs before freezing; recovery cannot change an existing assertion to make a game pass.

This checks internal agreement, **not** free-prose understanding or game-rule truth. Unit tests demonstrate that two equally wrong numbers still agree. In the resource sample the model omitted the requested evidence/summary, so agreement validation did not apply. Its assertion expected credits `4`, but `buy → earn → buy` gives `5−4+3−4=0`, enters Won, and later actions must do nothing. The original run remains `plan_review_required`, despite passing independently specified checks. The counterexample and per-draft metadata coverage are retained in `EXPANSION_RESULTS.json`.

### Evidence-driven default

Both paid candidate batches requested duplicate summary lists. The initial indexed form caused coverage/index errors; ordered values reduced bookkeeping but did not resolve omissions and contradictions. Therefore requesting this metadata is **off by default** in the final release, enabled explicitly with `--structured-expectations`. Supplied metadata is always validated, even when the flag is off; it is never silently removed. Ordinary plans retain `spec_quote` and `expected_basis`.

The final opt-in wiring/default was regression-tested with simulated model responses and real browsers, **not paid-generated again** after exhausting the 30-attempt cap. Paid candidate outcomes must not be presented as final default-mode performance or as a controlled improvement estimate.

## 3. Trusted form tools

| Tool | Behavior |
|---|---|
| `fill` | Native input/textarea fill, 0–500 characters; empty clears; real input events |
| `select_option` | Select one native option by value, max 200 characters; real change events |
| Observation `source: "value"` | Read the current input/select value; no state mutation |

Password/file/hidden inputs, arbitrary contenteditable controls and custom-widget scripting are not supported. Disabled/read-only controls are not forced. Puzzle answers must be public non-secret task data, never account credentials. No answer is injected into hidden game state. Form-value echo alone is excluded from functional-evidence detection; plans still need an observable rule outcome. Other structural evidence gates remain heuristic, not semantic proof.

## 4. Small real-model evaluation

Environment: DeepSeek `deepseek-flash`, Windows, Edge and Playwright. Six English specifications and six independent plans were fixed before the first API call. Each independent plan has six selected tests and is withheld from generation. Samples cover only small explicit rules; generated state snapshots still need manual authenticity checks.

| Initial sample | Autonomous result | Independent checks | API attempts |
|---|---|---|---|
| Word lock | Selected checks passed, manual pending | 6/6 | 2 |
| Number dial | Selected checks passed, manual pending | 6/6 | 2 |
| Platform hop | Partial game, plan failed | 6/6 | 4 |
| Aim range | Partial game, plan failed | 6/6 | 4 |
| Tactical duel | Partial game, plan failed | 6/6 | 4 |
| Market budget | Plan review required | 6/6 | 3 |

Initial batch: 19 attempts, 6/6 artifacts pass selected independent checks, **2/6 autonomous self-plans pass**. A separately labelled follow-up used the remaining 11 attempts: platform (4), aiming (4), tactics (3). All three artifacts again passed 6/6 independent checks; **0/3 autonomous self-plans passed**, due to metadata coverage/contradiction failures. No original outcome was replaced and no frozen assertion was weakened.

The useful result is feasibility of these input/control/rule combinations, not reliable autonomous completion of broad genres. Planning semantics and metadata overhead remain explicit weaknesses. No instructor-model compatibility, latency/cost improvement or arbitrary unseen-game reliability is claimed.

## 5. Read-only dashboard

~~~powershell
python -m agent dashboard runs/YOUR_RUN --port 8005
~~~

Open `http://127.0.0.1:8005/`; stop with Ctrl+C. It displays recorded status, API attempts, elapsed time, selected round, requirements and recent event labels, plus game/report links. Missing/corrupt evidence is unverified, not successful. The run's original version is distinct from the viewer version. Raw API traces, `.env` and summary-file routes are not served; the viewer does not initiate model calls or accept generation requests.

Desktop screenshot was visually inspected; the real-browser mobile check at width 390 passed without horizontal overflow. The owned temporary preview was stopped at task teardown. Use the command above to view your retained runs; temporary evaluation games/previews were not kept as deliverables.

## 6. Verification and next boundary

Final regression: **254/254 passed, including 44 real-browser tests**, with no skips and no paid API calls. All previous 220 tests were retained; 34 new tests cover agreement/legacy rules, form behavior, echo-only evidence exclusion, experiment mode and read-only UI. All nine artifacts passed two fresh-browser repetitions of their six independent selected tests, with unchanged game/plan hashes and frozen fixtures.

Exact final regression counts, source fingerprints, preserved initial failures, fixture integrity and final repeated-check results are recorded in `EXPANSION_RESULTS.json`. Replays are read-only, make zero API calls and do not promote original failed runs to autonomous success. Two fresh-browser repetitions per artifact check repeatability of the selected tests, not full gameplay acceptance.

Next priority: improve small rule-transition test design and evaluate new variants with frozen independent checks. Do not add more genre labels, a multi-agent framework or a large UI until autonomous planning is more dependable. Networking, 3D, engines and persistence remain deferred.
