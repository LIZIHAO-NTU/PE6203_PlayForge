# PlayForge — Beta 3: Setup, Plan Review and Failure Routing

Release: `1.0.0-beta.3`.

Follow-up: a later real DeepSeek on/off comparison is recorded in [AUDIT_COMPARISON.md](AUDIT_COMPARISON.md). This document's zero-API statements describe the initial implementation/verification session, not that later evaluation.

This update targets the planning weaknesses observed in [CAPABILITY.md](CAPABILITY.md). It does not expand the game platform, embed game templates, or claim that model-authored tests are now always correct. No paid API calls were made for this update.

## 1. One flow

~~~text
Original spec + execution contract
    → Draft plan and structural validation
    → Deterministic initial-state conflict review (always on, zero API)
    → Optional one-attempt model audit (original spec + draft ONLY)
    → Freeze plan
    → Generate game
    → Fresh page for EACH test → setup_steps → check steps
    → Pass / repair actual errors / stop for review without weakening tests
~~~

## 2. Independent setup

The browser still opens a fresh context/page for every test. Optional `setup_steps` run on that page immediately before `steps`, using the exact same trusted DSL. They are ordinary clicks, keys and observations, not a scenario loader or hidden state mutation. Existing plans without the field still work.

Example (an existing ordinary counter button; not a game implementation template):

~~~json
{
  "id": "T2",
  "description": "A second increment reaches two",
  "requirement_ids": ["R1"],
  "setup_steps": [{"action": "click", "selector": "#increment"}],
  "steps": [
    {"action": "assert", "source": "state", "path": "score", "op": "eq", "value": 1},
    {"action": "click", "selector": "#increment"},
    {"action": "assert", "source": "state", "path": "score", "op": "eq", "value": 2}
  ]
}
~~~

Setup and check together must stay within 18 steps; all waits count toward the existing 45-second plan-wide budget. Check steps must contain an assertion, not only setup. Captures are shared between setup/check within one test and never between tests. Evidence actions record `stage: setup|check`.

## 3. Review before freezing

### Deterministic review

The reviewer compares consecutive literal equality assertions before any input or time advance, preferring tests labelled `initial` as anchors. If one test expects coins=10 on a new page and another expects coins=4 before doing anything, it emits a review warning. It does not edit the plan, invent setup, solve a map, or automatically declare either expected value correct.

Read-only CLI; no API calls:

~~~powershell
python -m agent inspect-plan path/to/plan.json
~~~

Exit code 0 means inspection completed, not that the plan is semantically correct.

On the previous Beta 2 resource-shop plan, this detects `T5` (expected coins 4 rather than initial 10) and `T7` (expected Won rather than initial Playing). It does not detect every problem, including Sokoban/maze legality after inputs and a missing prerequisite hidden behind a capture/wait. Random or auto-changing states can also create false alarms.

### Optional model audit

Enable with `--plan-audit` on ordinary generation or `benchmark`. Default: off. There is at most one actual API attempt, including malformed/transport failure; no automatic audit retry. It shares the existing call/time cap and reserves a call for generation. If insufficient budget remains, record `skipped_budget` rather than pretending review happened.

~~~powershell
python -m agent game_design_prompt.md --plan-audit --max-calls 8
~~~

This command WOULD spend credits if run; it was not run against a paid model during this task. The auditor receives only original specification, valid draft, execution contract and deterministic warnings—never generated game code, execution feedback or held-out acceptance plans. It returns `approved`, `revised` or `unverified`.

Revisions are allowed only BEFORE generation/freezing, with a cited issue and original-spec evidence for each changed test. Requirement IDs/text/priority/verification, test IDs/coverage, state contract and manual checks are preserved. Existing assertion observations/operators cannot be removed or changed; expected values/references and ordinary setup/input sequences may be corrected. Evidence explanations are model claims, not automatically verified truth. Invalid/unverified audits stop before generation as `plan_review_required`.

The draft and audit response are saved separately; only the accepted plan becomes `traces/plan.json`. Once frozen, no new mechanism changes it. Late planning recovery retains the existing stricter assertion-preservation rules and never runs this pre-generation audit against game code. Structurally invalid drafts still use the existing validation/retry/fallback path, not the semantic audit.

## 4. Failure routing

| Evidence | Action |
|---|---|
| Browser/infrastructure failure | Stop infrastructure handling; do not rewrite gameplay |
| Missing resources/runtime errors | Prioritize implementation repair |
| Failed test also has an initial-state conflict warning | Preserve game and frozen plan; request review |
| Same test/step/actual/expected/op repeats after one repair | Stop further blind repair; cause remains unverified |
| Optional diagnosis says test_issue/tool_limit/uncertain | Preserve artifact; no success claim |
| Selected checks genuinely pass | Existing completion gate; full acceptance still pending |

Repeated-assertion stopping requires actual observed values; absent/malformed evidence is not a fingerprint. Runtime/resource/infrastructure errors take precedence. This policy is conservative: an implementation that needed more repairs might be stopped early. `plan_review_required` means unresolved, NOT that the tests are definitely wrong or the game definitely correct. If an artifact exists, it remains playable for review; if pre-generation audit stopped, no game is fabricated.

## 5. Validation

**195/195 framework tests passed, including 33 real-browser tests**, retaining all previous 160 tests. Final full run: 162.169 seconds. Coverage includes setup isolation/capture/budgets, real-browser pre-freeze revision → generation → checks, conflicting initial assumptions, conservative stop behavior, uncertain diagnosis, rejected assertion removal/operator changes, and a one-attempt audit transport policy.

All seven prior Beta 2 artifacts passed their independent acceptance plans twice using the final Beta 3 verifier (shared 60-second budget per artifact), with all source/plan integrity checks passing and zero API calls. Artifacts: tic-tac-toe, Sokoban, memory pairs, brick breaker, resource shop, key maze and inventory delivery. Reports remain local under `runs/planning_beta3_rechecks_20261014/<case_id>_01/`. This verifies backward acceptance behavior, not new model-generated-game reliability.

The prior [CAPABILITY_RESULTS.json](CAPABILITY_RESULTS.json) is left unchanged. These changes do not retroactively convert failed Beta 2 autonomous runs into successes or provide a new unseen-game success rate. Next meaningful experiment is a separately budgeted, same-model comparison with fresh requirements and `--plan-audit` on/off.
