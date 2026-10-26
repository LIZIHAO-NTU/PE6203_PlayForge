# PlayForge: Build a Coding Agent That Can Build a Game

Current version: `1.2.1` — an experimental course-project release, not a production reliability guarantee. Adds bounded multi-issue draft feedback, safe blocked-summary compatibility and a separate controlled real-model repair evaluation. See [RELEASE_1_2_1.md](RELEASE_1_2_1.md) for exact outcomes and unresolved autonomous checks. [RELEASE_1_2.md](RELEASE_1_2.md) preserves the earlier baseline and mixed-rule screening; [EXTENSION_PLAN.md](EXTENSION_PLAN.md) tracks deferred work.

The subsequent four-case real DeepSeek audit on/off comparison is in [AUDIT_COMPARISON.md](AUDIT_COMPARISON.md): 24 API attempts; keep audit opt-in/off by default. The agent implementation was unchanged for that evaluation.

PlayForge is a lightweight game-coding agent for the PE6203 group project: read a Markdown specification, generate vanilla HTML/CSS/JavaScript from scratch, run browser checks, and make bounded repairs from execution feedback.

**Core gameplay before visual polish.** No prewritten game implementations, game templates or built-in solvers. Benchmark families are evaluation samples, not the only games the agent can generate.

This is an experimental course project, not a guarantee of success on arbitrary unseen games. Scope: offline 2D browser games; selected samples include text/numeric puzzles, platform physics, aiming, local tactics and resource budgets, not networked multiplayer, 3D, backends or complex engines.

### Team validation update (2026-10-22)

The integrated production baseline is main `8eb3145`, including B's planning experiment, C's repair-conflict guard and D's standalone evidence auditor. The auditor is not a production completion gate. A adds **9 controller-consistency tests**, without changing `agent/` or prompts: the focused suite passed **9/9**, and the complete browser-enabled suite passed **343/343**, with zero skips and no real model API calls. These results describe that baseline plus A's added test file, not an unknown-game success rate. E's independent review and the team's evaluation freeze remain pending; publication does not imply approval or merge.

- [Team handoff and next actions](docs/TEAM_HANDOFF_20261022.md)
- [A's method and E's reproduction checklist](docs/A_CONTROLLER_CONSISTENCY.md)
- [Recorded results and source fingerprints](docs/a_controller_consistency_results.json)
- [Controller-consistency tests](tests/test_controller_consistency.py)

### Game UI language

Player-facing text defaults to **English**, even when the specification is written in another language. An explicit UI language requirement takes precedence, including bilingual or per-element instructions. Exact required display strings are preserved unless translation is explicitly requested. Technical identifiers, selectors, state keys and contract values are not translated. Planning, optional pre-freeze review and code generation/repair share this policy; frozen tests remain unchanged. No language switcher is added unless requested. This is a prompt policy, not a guarantee of model compliance; verify the generated UI. Existing saved games are unaffected.

Language smoke checks (2026-10-14): a Chinese specification without a UI-language instruction produced English text; an English specification requesting Simplified Chinese produced Chinese text while preserving the exact button label `Again`. Both generated artifacts passed independent language and basic-play checks. Six real DeepSeek API attempts were used in total, including an initial default-language run blocked by a plan-schema error followed by a transport timeout; that blocked run is not counted as a success. These are small smoke checks, not a general compliance rate. Temporary test games were removed. Four prompt-wiring tests were added: the final full regression passed 199/199 tests, including 33 real-browser tests. The first full run had two browser errors (including a screenshot timeout); the affected 29-test group and subsequent full rerun passed without code or test-standard changes.

## 1. How it works

PlayForge keeps one controller loop, with draft review before freezing and explicit setup on each fresh test page. Beta 4 adds trusted sampled stability observations after controls, without rewriting frozen acceptance. See [INTEGRATION.md](INTEGRATION.md), [PLANNING.md](PLANNING.md) and [TEST_RELIABILITY.md](TEST_RELIABILITY.md).

~~~text
Spec → Plan → Generate → Browser verification → Bounded repair
                         Save the better version and traces

~~~

- **Model**: understands requirements, plans, generates and edits code via a DeepSeek-compatible API.
- **Tools**: validated file writes, page loading, keyboard/mouse input and DOM/state observations.
- **Loop / Harness**: validation, budgets, logs, version selection and stopping conditions.
- **Repair memory**: recent failures and passed checks, continuing from a better version; not cross-task learning.
- **Planning fallback**: may generate the original-spec game after invalid planning, but only claims startup evidence; disabled by `--strict-plan`.
- **Planning recovery**: one budget-bounded recovery request after startup, then freeze, retest and repair; startup evidence is not reused as functional success.
- **Completion gate**: complete test evidence and input-followed-by-rule assertions, plus DOM/state consistency checks. See [QUALITY.md](QUALITY.md) (Chinese).

## 2. Installation and configuration

Requires Python 3.10+, a model API account and a Playwright browser. Run these Windows PowerShell commands from the repository root.

~~~powershell
git clone https://github.com/LIZIHAO-NTU/PE6203_PlayForge.git PlayForge
cd PlayForge
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m playwright install chromium
./.venv/Scripts/python.exe -m agent configure
~~~

Enter your own API key; input is hidden. The command writes a local plaintext `.env`, which is Git-ignored, without calling the model. It refuses to overwrite an existing `.env`; edit that file locally. Never share keys or account passwords.

Explicit virtual-environment interpreter paths avoid installing dependencies into another Python; activation is unnecessary. On macOS/Linux, use `./.venv/bin/python`. Browser regression testing was performed on Windows with Edge.

| Setting | Description |
| --- | --- |
| `DEEPSEEK_API_KEY` | Your key; `LLM_API_KEY` is also supported and takes precedence. |
| `LLM_BASE_URL` / `LLM_MODEL` | Endpoint and a model ID available to your account. |
| `LLM_THINKING` | DeepSeek-specific; usually leave blank for other providers. |
| `LLM_JSON_MODE` | Request JSON output only if the endpoint supports it. |
| `LLM_MAX_TOKENS` / `LLM_TIMEOUT_SECONDS` | Per-request output and timeout limits, not whole-task budgets. |
| `PLAYWRIGHT_CHANNEL` | Blank: Playwright Chromium; `msedge`: installed Edge. |
| `PRICE_*` / `PRICE_CURRENCY` | Optional prices; without them, report tokens, not invented costs. |

See [.env.example](.env.example). Historical tests used `deepseek-flash`; this is a recorded configuration, not a promise that every account supports it. Other providers may need option adjustments. Compatibility with the instructor's final model remains to be tested.

Environment check — no paid API call

~~~powershell
./.venv/Scripts/python.exe -m agent doctor
~~~

`doctor` checks local configuration, dependencies and browser availability. **It does not verify key validity, balance or model-provider connectivity.**

## 3. Generate and play

~~~powershell
./.venv/Scripts/python.exe -m agent game_design_prompt.md
~~~

**Planning, generation and repair consume API credits.** Defaults: 3 generation/repair rounds including the first version, 8 API attempts, and a 600-second task budget; each browser verification defaults to 60 seconds. Planning, recovery, formatting retries and transport retries all share the API-attempt cap.

Example with an explicit specification and budget

~~~powershell
./.venv/Scripts/python.exe -m agent examples/benchmark/sokoban.md --max-rounds 3 --max-calls 5 --max-seconds 360
~~~

Describe controls, initial state, legal/illegal actions, scoring or win/loss, restart behavior and technical constraints. Do not include keys or private data; you do not need to write a JSON plan.

`--output` selects a new output directory and never overwrites existing results; `--headful` shows the test browser; `--strict-plan` stops after functional planning fails instead of generating a partial result.

### Reliability options

| Option | Default | Behavior |
| --- | --- | --- |
| `--repair-mode auto` | `auto` | Version-bound changed-file repair; full responses still accepted |
| `--repair-mode full` | Optional | Preserve whole-project repair responses |
| `--verify-repeats 2` | `1` | All repeats must pass within one shared test-timeout |
| `--diagnose` | Off | At most one diagnosis API attempt for ambiguous failure, within the shared cap |
| `--syntax-check` | Off | Trusted Node checks for external JS; missing/incomplete checks are labelled |
| `--lessons runs/lessons.json` | Off | Opt-in generic recovery observations, not game source or test answers |

Example for stronger repeatability (generation is still paid; no hidden API allowance):

~~~powershell
./.venv/Scripts/python.exe -m agent examples/benchmark/sokoban.md --max-calls 8 --repair-mode auto --verify-repeats 2 --lessons runs/lessons.json
~~~

Repetitions use fresh browser contexts and may take longer or expose intermittent failures; real-time scheduling is not guaranteed identical. Keep optional diagnosis off for the cheapest baseline. Compare features under the same model/spec/budget before claiming reliability improvements.

Each run creates a new `runs/<run_id>/`

~~~text
game/          Generated game source
traces/        Plans, API records, versions and evidence
summary.json   Results and usage
REPORT.md      Findings and manual checks
~~~

Replace the placeholder with the printed run directory

~~~powershell
./.venv/Scripts/python.exe -m agent serve "runs/<run_id>/game"
~~~

Open the [local game page](http://127.0.0.1:8000/). Serving and playing do not call the model; input does not consume API credits per frame. If occupied, add `--port 8001` and use that port. Stop with Ctrl+C.

Read `REPORT.md` and `summary.json`; opening a page or checking an exit code alone is not functional acceptance.

| Status | Description |
| --- | --- |
| `automated_passed_manual_pending` | Selected automated checks passed; full acceptance remains pending. |
| `checks_failed` | Checks failed; a better launchable version may be preserved. |
| `plan_review_required` | Review is unverified, a failed test has an initialization conflict, or repair/diagnosis remains inconclusive. No success claim; an existing game is preserved. |
| `partial_game_plan_failed` | Functional planning/recovery failed; startup-only evidence. |
| `partial_game_evidence_missing` | Valid format, insufficient core-interaction evidence. |
| `unsupported_spec` | Outside the current scope; no silent substitution. |
| `budget_exhausted` / `run_error` / `generation_failed` | Budget, execution or generation failure; inspect the report. |
| `interrupted` | Interrupted; not a completed autonomous run. |

## 4. Multi-game benchmark — paid

~~~powershell
./.venv/Scripts/python.exe -m agent benchmark examples/benchmark/suite.json --max-total-calls 20 --max-calls-per-case 5
~~~

One run per family by default; these families exercise different mechanics

| Game | Mechanics |
| --- | --- |
| Tic-tac-toe | Turns, legal moves, victory and terminal state |
| Sokoban | Grid movement, obstacles and pushing constraints |
| Memory pairs | Hidden information, matching, delays and input locks |
| Brick breaker | Continuous motion, collision, pause and reset |

`--max-total-calls` caps batch API attempts including retries, not money. `--max-calls-per-case` limits each run; `--repeats 2` repeats cases; benchmark `--max-seconds` is per case. Cases without enough budget remain recorded as skipped.

Prewritten held-out checks are not given to the generation model or fed into that run's repairs. Reports separate startup, model-plan and independent-check results. These checks are not exhaustive; some observe game-supplied read-only state.

Reports: `runs/benchmark_*/BENCHMARK.md` and `benchmark.json`; games: `cases/<case_id>/game/`; independent evidence: `acceptance/<case_id>/`. Use the corresponding game directory with `serve`.

Add new specifications and acceptance plans under `examples/benchmark/` and register them in `suite.json`; do not inject ready-made game implementations.

`examples/benchmark/capability_suite.json` contains six simple mechanic families; `transfer_suite.json` adds one inventory/capacity variant. They are evaluation fixtures, not game templates. Benchmark reports now expose scheduled/attempted/evaluated counts and self/independent disagreements; absent evaluation must not be presented as a gameplay failure or silently omitted. Frozen specification/acceptance hashes are checked before and after evaluation.

## 5. Offline rechecks and metrics

Replay an existing run using its recorded active plan, without model calls or changes to its score:

~~~powershell
./.venv/Scripts/python.exe -m agent replay "runs/<run_id>" --verify-repeats 2
~~~

Use `recheck` to select another explicit plan. Repetitions share `--timeout` (default 60 seconds). Evidence includes replay manifests, source hashes, actual actions and before/after screenshots. Screenshots are retained observations, not an automatic visual verdict.

Replay an existing game without editing it or overwriting its original score

~~~powershell
./.venv/Scripts/python.exe -m agent recheck "runs/<run_id>/game" --plan "runs/<run_id>/traces/plan.json"
~~~

Reusing the model's plan does **not** make this independent acceptance. Write independent checks separately. Results go to `rechecks/`; Playwright is required, but no model is called. If `summary.json` has `active_plan: functional_plan.json`, use `traces/functional_plan.json` instead; the original `plan.json` retains startup fallback checks.

Aggregate ordinary runs into JSON/CSV

~~~powershell
./.venv/Scripts/python.exe -m agent summarize runs
~~~

This command makes no model calls and reads only immediate child runs. For benchmarks, summarize `runs/<benchmark-directory>/cases` or read `benchmark.json`. Do not claim a controlled comparison across mixed models, prompts, specifications or budgets.

## 6. Tests and recorded results

Initial Beta 3 implementation validation used simulated models, real browsers and read-only historical artifacts, with zero paid API calls; see [PLANNING.md](PLANNING.md). A subsequent fixed-version, four-case real-model comparison is recorded separately in [AUDIT_COMPARISON.md](AUDIT_COMPARISON.md). Do not reuse Beta 2 paid results or either small sample as a general Beta 3 success rate.

Version 1.0 Beta 2 has a small real DeepSeek screening documented in [CAPABILITY.md](CAPABILITY.md): 13 generations across baseline, optimized and new-variant batches, using 47 API attempts. These small deterministic fixtures do not establish arbitrary unseen-game reliability. Earlier 0.5/0.4/0.3 records below retain their original scope.

Framework tests use mock model responses and spend no API credits

~~~powershell
./.venv/Scripts/python.exe -B -m unittest discover -s tests -v
~~~

Real-browser tests are skipped by default. Enable the full suite

~~~powershell
$env:MVP_BROWSER_TESTS="1"
$env:PLAYWRIGHT_CHANNEL="msedge"
./.venv/Scripts/python.exe -B -m unittest discover -s tests -v
~~~

Leave `PLAYWRIGHT_CHANNEL` blank for Playwright Chromium. Temporary test artifacts belong in `.codex-tmp/`; remove only your task's temporary files, not someone else's work.

### Version 1.2.1 — 2026-10-17

Draft feedback reports up to eight first-known errors across tests, preserving the primary error and indicating unscanned tests. Isolated probes are diagnostics only: full validation still decides acceptance. No assertions, limits or original rules are changed automatically.

A blocked response can carry an optional string `summary` of at most 1,500 characters. This is non-action metadata; files, changes, extra fields, false evidence and oversized/non-string summaries are rejected. The controller returns only the validated blocked diagnosis and preserves original artifacts. See [RELEASE_1_2_1.md](RELEASE_1_2_1.md) for the initially rejected real response and the separately labelled final checks.

Controlled repair evaluation (paid API, not autonomous game generation)

~~~powershell
python -m evals.repair_protocol --output reports/repair_trial --max-calls 4 --repeats 1
~~~

Full game closure trials

~~~powershell
python -m agent benchmark examples/reliability_closure_suite.json --output runs/closure_trial --max-total-calls 20 --max-calls-per-case 5 --max-rounds 3 --max-seconds 360 --repeats 2
~~~

The two command caps are separate: this example allocates at most 24 attempts in total. Counter fixtures are evaluation-only and never offered to the generator. Do not include fault-injection outcomes in normal game success rates. Model settings and public UI scope are unchanged.

### Version 1.2.0 — 2026-10-17

Located validation errors identify the test, setup/check index and combined step. Repair feedback links the failed action to frozen requirements and actual/expected observations; full evidence remains in traces. No new provider, arbitrary script tool, game template or multi-agent framework is added.

After failed verification, the coder may return only a validated `blocked` object citing actual failed tests. The controller preserves the best artifact, leaves the frozen plan unchanged and reports `plan_review_required`, never success. This is model-reported uncertainty, not an independent semantic detector; contradictory repairs can still be missed.

The benchmark now reports `joint_selected_checks_passed` and its attempted-run rate: both self-plan and held-out selected checks must pass. Missing independent evidence does not count as confirmed success. Full gameplay acceptance remains separate. See [RELEASE_1_2.md](RELEASE_1_2.md) and [RELIABILITY_1_2_RESULTS.json](RELIABILITY_1_2_RESULTS.json); no universal success-rate or cost reduction claim is made.

New mixed-rule evaluation

~~~powershell
python -m agent benchmark examples/reliability_1_2/suite.json --output runs/mixed_trial --max-total-calls 8 --max-calls-per-case 4 --max-rounds 3 --max-seconds 300
~~~

### Version 1.1.0 — 2026-10-16

See [RELEASE_1_1.md](RELEASE_1_1.md) and [EXPANSION_RESULTS.json](EXPANSION_RESULTS.json). Supplied structured summaries detect disagreement with literal assertions before freezing; they do not prove arithmetic or interpret arbitrary prose. Requesting these duplicate lists is experimental and **off by default** because real trials showed planning failures; opt in with `--structured-expectations` for generation or benchmark. Supplied mismatches are always rejected, never silently discarded. Native `fill` / `select_option` use real browser events; `source: "value"` observes form values. Password/file/hidden inputs and arbitrary script actions are not added. Input echo alone is not a gameplay check.

Run an expansion suite (paid generation)

~~~powershell
./.venv/Scripts/python.exe -m agent benchmark examples/expansion_1_1/suite.json --output runs/expansion_trial --max-total-calls 30 --max-calls-per-case 5 --max-rounds 3 --max-seconds 360
~~~

Open an existing run in the read-only dashboard (no API calls)

~~~powershell
./.venv/Scripts/python.exe -m agent dashboard runs/expansion_trial/cases/word_lock_01 --port 8005
~~~

Then open `http://127.0.0.1:8005/`; stop with Ctrl+C. The viewer shows recorded results, manual-review items and recent activity, and links to the game/report. It does not launch generation or expose raw API traces. Bind is loopback only; this is not a public deployment or a secure multi-user service. Existing CLI startup remains unchanged.

### Version 1.0 Beta 4 — 2026-10-16

New functionality and bounded real-model results are recorded in [TEST_RELIABILITY.md](TEST_RELIABILITY.md) and [RELIABILITY_RESULTS.json](RELIABILITY_RESULTS.json). The matched four-case comparison confirmed delivery on selected independent checks for both versions, but did not improve the 3/4 self-plan result; arithmetic assertions remain a weakness. Framework regression, paid generation and read-only repeated checks are reported separately. Instructor-model compatibility is still untested.

### Version 1.0 Beta 3 — 2026-10-14

**195/195 framework tests passed, including 33 real-browser tests.** All prior 160 tests remain. This initial framework validation used zero paid API calls; the later paid comparison did not change agent code or rerun this suite.

See [PLANNING.md](PLANNING.md) for regression and read-only replay results. The audit is opt-in (`--plan-audit`), consumes at most one actual API attempt from the existing cap, and runs only before game generation/freezing. `inspect-plan` is zero-API.

### Version 1.0 Beta 2 — 2026-10-14

**160/160 tests passed, including 27 real-browser tests.** All 143 previous tests are retained. These framework tests simulate model responses and are separate from the paid capability screening.

### Version 0.5 baseline — 2026-10-14

**143/143 regression tests passed, including 24 real-browser tests.** All 109 previous tests remain passing. Composed-feature and full/auto compatibility tests use simulated models and real browser interactions, not paid-model generation.

Validation and composed-feature checks are documented in [INTEGRATION.md](INTEGRATION.md). No paid DeepSeek experiment has been performed for 0.5; historical game results below are not its success rate.

### Version 0.4 — 2026-10-14

- **109/109 framework tests passed, including 21 real-browser tests.** This is not a model-generated-game success rate.
- Read-only historical Sokoban replay caught stale state and a missing win transition: original 1/3 checks, previously repaired version 3/3. Games and original scores were unchanged.

Method and limitations: [QUALITY.md](QUALITY.md).

### Version 0.3 — 2026-10-10

- **83/83 framework tests passed**, including real-browser tests, not paid-model generation success.
- **20 DeepSeek API attempts** across two iterative batches. In the refined batch, two tic-tac-toe runs, two Sokoban runs and one memory-pairs run launched, each passing 5/5 selected independent checks.
- Brick breaker failed planning and was not generated; some model-authored expectations were incorrect.
- The final 0.3 fallback and sequence-self-check changes were framework-tested but not paid-retested in these batches. 0.3
- No controlled old-version baseline exists; do not claim improvement percentages or unseen-game reliability.

See [GENERALIZATION.md](GENERALIZATION.md) for historical methodology. Raw `runs/` remain local and are not uploaded; a fresh clone has no historical generated games or logs.

## 7. Structure and collaboration

~~~text
agent/                 Controller, prompts and verification
examples/              Specs and independent plans, not templates
tests/                 Zero-paid-API regression tests
game_design_prompt.md  Default specification
.env.example           Shareable config without keys
GENERALIZATION.md      0.3 design and historical evidence
UPGRADE.md             0.2 historical notes
CHANGELOG.md           Version history
QUALITY.md             0.4 gates, recovery and limitations
INTEGRATION.md         Integrated reliability baseline
CAPABILITY.md          Beta 2 capability screening and limits
CAPABILITY_RESULTS.json Sanitized run-level evidence
PLANNING.md            Beta 3 setup, review and routing
AUDIT_COMPARISON.md    Fixed-version real-model audit comparison
AUDIT_COMPARISON_RESULTS.json Sanitized comparison evidence
TEST_RELIABILITY.md    Beta 4 changes, comparison and rehearsal
RELIABILITY_RESULTS.json Sanitized Beta 4 evidence
RELEASE_1_1.md         1.1.0 changes, evaluation and limits
RELEASE_1_2.md         1.2.0 feedback, real baseline and mixed rules
RELEASE_1_2_1.md       Reliability closure and controlled repair results
RELIABILITY_1_2_1_RESULTS.json Sanitized patch evidence
evals/repair_protocol.py Explicit counter fault-injection evaluation only
RELIABILITY_1_2_RESULTS.json Sanitized 1.2.0 evaluation evidence
examples/reliability_1_2/ Mixed-rule English requirements and held-out checks
EXPANSION_RESULTS.json Sanitized initial/follow-up/replay evidence
examples/expansion_1_1/ Six English specifications and held-out checks
EXTENSION_PLAN.md     Implemented scope and deferred work
~~~

- Each teammate creates their own environment and `.env`; never copy another person's key.
- Share source, specs, tests and documentation, not secrets, raw logs, virtual environments or caches. Logs may contain full prompts and source; redact before sharing.
- Synchronize before editing. Prompts live in `agent/prompts.py`; rerun regression after changing prompts, tools or acceptance, recording version and budget.
- Separate game defects, test defects and tool limitations; never fake state or lower original requirements to pass.
- No manual code edits during autonomous development; playtesting follows the run. The instructor's final rules take precedence.

## 8. Troubleshooting and limits

### Export a run

~~~powershell
./.venv/Scripts/python.exe -m agent export-run "runs/<run_id>" --output "submissions/<name>" --report "path/to/report.pdf"
~~~

This zero-API command copies the current agent, pinned requirements and exact `game/` / `traces/` into a new directory. It excludes local `.env`, dependencies and caches. `--report` must point to your existing PDF; omit it only for an incomplete draft package. The delivery manifest distinguishes current-agent and original-run versions. Inspect traces for private content before sharing.

Exporting does not turn an old or assisted run into a valid autonomous course demonstration. Final live-run commands and course requirements still need confirmation.

- **Playwright missing**: install and run with the same `.venv` interpreter.
- **Browser unavailable**: install Chromium, or set `PLAYWRIGHT_CHANNEL=msedge`, then run `doctor`.
- **API 401/403, missing model or balance**: check your own provider account; `doctor` does not verify these. Never expose keys in screenshots.
- **Output already exists**: choose a new `--output`; old results are protected.
- **Page opens but checks fail**: inspect failed steps; rules, test expectations or interaction strategy may be wrong. Preserve failures.
- **Empty cost**: pricing was not configured, not free. Failed/time-out requests may be billed; provider billing is authoritative.

No networked games, 3D, complex prescribed engines, arbitrary package installation or unrestricted shell execution. Generated code is untrusted; browser/network restrictions are not an audited OS sandbox. Final course API compatibility, scope and required `game/` / `traces/` submission layout must still be aligned with the instructor's requirements; `runs/` is the current development/evaluation layout.
