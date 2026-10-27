# PlayForge — 1.0 Beta 1 Integrated Reliability

Release identifier: `1.0.0-beta.1`. The 0.5 development snapshot was renamed without functional changes; the validation below was recorded on that baseline. Beta status does not guarantee arbitrary unseen-game success.

This document preserves the integration baseline. Beta 2 changes and paid screening are in [CAPABILITY.md](CAPABILITY.md); the 143-test record below is historical, not the latest suite count.

Latest Beta 3 planning changes: [PLANNING.md](PLANNING.md).

This version extends one controller loop rather than stacking independent agent frameworks. All game code is still generated from the supplied specification. No external coding-agent runtime, game engine, game template or solver is embedded.

## One coherent flow

~~~text
Spec → Frozen plan → Full first version
                       ↓
Version-bound edit → Artifact checks → Browser evidence → Completion gate
       ↑                                      ↓
       └── Best stable base ← Failure routing / optional diagnosis
                                              ↓
                              Optional recovery observations
~~~

The original specification and frozen plans remain intact. Edits create new candidate directories from an observed repair base; artifact checks, browser observations, completion gates and routing share the same evidence and budgets.

## Safeguards and defaults

| Area | Default | Boundary |
|---|---|---|
| File repair | Auto, with full responses accepted | Hash must match the base; no deletion, rename, path escape or ambiguous merge |
| Artifact checks | On | Local HTML references only; not proof of JavaScript semantics or gameplay |
| Failure routing | On, zero additional API | Observations are not proven root causes |
| Model diagnosis | Off | At most one actual extra attempt per run, from existing budget |
| Browser repetitions | One | Optional 2–3; all must pass within one shared timeout |
| Temporal sampling | Only if planned | Read-only snapshots, at most 8 samples and 2000ms per action |
| Recovery store | Off | Whitelisted principles, verified recovery observations, no code/test answers |
| Node syntax | Off | Trusted `node --check`, no generated host-code execution; only external JS |

`--repair-mode full` restores whole-project response mode. Invalid partial edits request a full response on the next remaining round; they do not touch the base. This fallback consumes an existing round/call, not a hidden retry allowance.

Previously passed checks from a stable, complete-evidence base are protected when selecting a newer candidate. A candidate that regresses one is retained as evidence but not selected merely because another test passed. This is conservative: it can restrict exploration, and does not prove the older version is semantically correct.

## Failure handling

- Missing resources/runtime errors → local implementation repair.
- DOM/state mismatch → align actual live state, never fake observations.
- Assertion/goal/interaction uncertainty → examine original rules and actual evidence before editing.
- Infrastructure or incomplete evidence → stop unverified; rewriting gameplay cannot establish missing observations.

Optional `--diagnose` runs only for an ambiguous failure with another repair round available, at least two remaining API attempts and 15 seconds. Its output must cite actual failed test IDs and may not contain edits. `test_issue` or `tool_limit` stops with `diagnosis_unverified`, never a pass. Invalid diagnosis structure is ignored; API failures preserve the existing candidate. Diagnosis is fallible and may stop too conservatively, so it remains optional.

## Evidence and replay

Each browser evidence directory has `replay.json`: fixed plan content, source hashes, environment/browser versions, viewport, actual inputs/results and before/after screenshots. Sampling adds bounded state sequences and `<name>_start` / `<name>_end` captures for explicit assertions. No hidden game-state setters are introduced.

`replay` uses the original run's active plan; `recheck` accepts a separately selected plan. Neither calls a model nor changes original scores. Replay is repeatable input execution, not a guarantee of identical scheduling. Repetitions use separate contexts; any failure prevents an all-pass result. Benchmark independent checks remain held out, including from diagnosis and lesson storage.

## Bounded memory and reproducibility

`--lessons runs/lessons.json` opts into a small local JSON store. Records require a failed check to pass after changed source under the same frozen plan and a clean completion gate. Only predefined general principles are retrieved for matching failure categories. These are recovery observations, not proof that a proposed diagnosis was the root cause. Arbitrary prose in the editable store cannot become model instructions. Corrupt or concurrently changed stores are preserved and ignored rather than overwritten. Benchmarks do not enable this cross-run store.

Full evidence stays on disk while repair prompts receive compact failures and recent actions; temporal sample arrays are not repeatedly copied into model context. Dependency versions are pinned in `requirements.txt`; runtime metadata includes Python, Playwright, browser and agent-source fingerprints. These support comparisons, not a claim that every OS/browser combination has been tested.

`export-run` copies current agent code and exact game/traces to a new folder, excludes local `.env` and caches, rejects linked artifacts, and records original/current agent versions separately. An existing PDF can be attached; without it the package lacks the report. Exporting does not turn an old or assisted game into a valid live autonomous submission. Final course command/layout, model and engine scope still require confirmation.

## Validation boundaries

2026-10-14: final full regression **143/143 passed**, including **24 real-browser tests**, in 73.488 seconds on Windows / Python 3.11.9 / Edge. The previous 109 tests remain passing, with 34 added regressions. Tests use mock model responses; simulated API-attempt counters are not real charges.

Stage tests exercise edits, routing, repetition, immutable delivery and evidence-backed lessons before the combined regression. Model responses are simulated; real browser tests verify actual interaction. The composed test enables partial repair, repeated checks, optional diagnosis and lesson recording together. A separate synthetic comparison keeps full and auto repair outcomes aligned. These are compatibility checks, not real-model improvement measurements.

No paid model API was called during implementation. Unseen-game success, model-specific output reliability and cost improvements require later controlled paid trials. No performance percentage is inferred from framework tests. Multi-agent orchestration, game template libraries, trained specialist models, mandatory visual judges and a new OS sandbox are intentionally not introduced.
