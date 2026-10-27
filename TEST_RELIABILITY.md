# PlayForge — Test Reliability and Rehearsal

Date: 2026-10-16. Release: `1.0.0-beta.4`.

## 1. Outcome

The final framework passed **220/220 regression tests, including 37 real-browser tests**. Twenty-one new tests cover stability sampling, budgets, immutable assertions, test-basis metadata, temporal review and null unsupported-gameplay metadata. No prewritten game implementation or solver was added.

The matched four-case comparison delivered games passing all selected independent checks in both conditions (**4/4 before, 4/4 after**). Self-authored acceptance stayed at **3/4 in both conditions**. The new mechanisms work, but this sample does NOT demonstrate a higher autonomous success rate or reduced cost. Resource arithmetic remains a test-oracle weakness.

## 2. Implemented changes

- `assert_stable`: trusted observation starting after previous input, comparing 2–8 live samples over 100–2000 ms. Supports state or ordinary DOM observations, shares the existing 45-second plan wait budget, has no state setters or expected-value overrides. Sampling proves equality only at sampled times, not continuous stability or a correctly working pause/resume control.
- `evidence`: planner requests a short original-spec quote plus expected-outcome basis for each test. Supplied metadata is structurally validated; a non-verbatim quote produces an advisory warning, not an automatic failure or proof of correctness. Legacy plans without this optional field still work.
- Temporal review: real-time/hybrid tests comparing a state path with its old snapshot after intervening input receive a heuristic warning. A corresponding actual failure stops blind repairs while preserving the game and frozen tests. Invalid-action-labelled tests are excluded from this heuristic. Runtime, resource and infrastructure failures retain priority.
- Frozen stability assertions, including sample count/duration, cannot be weakened by late recovery or optional audit. Audit remains off by default. The source/test/plan hashes and repeated-check evidence are preserved in sanitized results.

Example (selectors and state paths still depend on the actual specification):

```json
[
  {"action":"click","selector":"#pause"},
  {"action":"assert","source":"state","path":"phase","op":"eq","value":"Paused"},
  {"action":"assert_stable","source":"state","path":"player.x","duration_ms":300,"samples":3}
]
```

Motion before pausing and after resuming still needs separate checks. This replaces a risky capture-before-pause comparison, not the game rules or other acceptance obligations.

## 3. Frozen English-spec comparison

Baseline commit: `b6fbb8288b115933c8782afb9704e19893fc2bc0` (Beta 3). Four requirements in `examples/reliability_20261016/` cover resources, discrete teleportation, a color sequence and real-time lanes. They are concise functional specifications plus explicit observation contracts, not fully open-ended one-sentence teacher prompts. Independent checks were authored before generation and never sent to the planner, coder, audit or repair model.

For each comparable run: maximum 4 API attempts, 3 generation/repair rounds, 300 seconds, same configured `deepseek-flash`, audit/diagnosis/lessons/syntax checks off. All baseline runs preceded improved runs, with independent stochastic samples and no seed control. A single sample per condition cannot isolate improvement from model randomness.

| Case | Before self-plan | Before independent | After self-plan | After independent |
|---|---:|---:|---:|---:|
| Crystal Workshop | Fail | 6/6 | Fail | 6/6 |
| Portal Shortcut | Pass | 6/6 | Pass | 6/6 |
| Color Code | Pass | 6/6 | Pass | 6/6 |
| Three-Lane Runner, clarified spec | Pass | 6/6 | Pass | 6/6 |

All eight comparable artifacts passed their unchanged independent checks twice in zero-API replays, with game and plan integrity checks passing. These are repeat observations of eight artifacts, not sixteen extra generated games. Screenshot spot checks showed visible English interfaces for the improved portal and runner; they are not complete human gameplay acceptance.

### Protocol correction

The first runner wording did not explicitly fix state-hook field placement/phase casing or which control resumes Paused. Its independent plan made assumptions and failed against the artifact. That original run used 3 API attempts and remains recorded as an excluded pilot; it is not silently relabelled a success. The wording was clarified before either final-condition runner evaluation, keeping the independent plan unchanged. The clarified baseline was rerun using a temporary archive of the original commit, not the improved agent; its spec hash matches the improved run.

### Remaining oracle errors

After two crafts, energy is `7 - 3 - 3 = 1`; charging makes it `3`, not `4`. The improved workshop test's textual explanation correctly stated this ledger, but its assertion expected `4` and later expected residual energy `1` instead of `0`. The game and independent checks followed the actual rules. This shows why an explanation is not a verified oracle. The color planner also omitted the requested basis on all six tests; optional metadata keeps compatibility but does not ensure model adherence.

## 4. Single-command rehearsal

```powershell
python -B -m agent examples/reliability_20261016/pulse_runner.md --output .codex-tmp/dress_rehearsal --max-calls 4 --max-rounds 3 --max-seconds 300
```

This was a separately recorded real-model run from a new output directory, not a replacement for a failed comparison. It used **3 API attempts**, selected round 2 after one repair, finished in **54.547 seconds**, recorded **zero manual interventions**, and returned `automated_passed_manual_pending`. Its original frozen self-plan and the independent six-check plan each passed twice under final-source read-only replay; HTTP returned 200. Local doctor/preflight succeeded, but doctor alone does not test provider connectivity. The real generation is the API connectivity evidence.

After paid runs, a defensive type guard was added for null gameplay metadata in unsupported plans. Final full regression and rehearsal replays use that final source. Valid compared gameplay paths are unchanged; candidate and final source fingerprints are separately recorded rather than falsely reported identical.

Instructor endpoint/model/options are still unknown and untested. Once provided, repeat the provider-specific configuration and fresh-directory rehearsal; current DeepSeek results do not prove instructor-model compatibility.

## 5. Usage and retained evidence

Total: **27/32 API attempts**, **138,941 input tokens**, **63,203 output tokens**, zero unknown-usage calls. Matched before/after runs used 10/11 attempts; the excluded pilot used 3 and the separate rehearsal 3. No calls were made merely to spend the unused budget. Actual monetary cost is unknown because price fields are not configured; provider billing is authoritative.

Retained: this report, `RELIABILITY_RESULTS.json`, the four English specification/acceptance pairs and suite, new framework tests, updated source/docs, and the proposal-only `EXTENSION_PLAN.md`. Temporary dependencies, source archive, generated games, screenshots and raw API logs are cleaned up; existing games/runs are untouched. Sanitized JSON retains hashes, failed frozen tests, observations, outcomes and usage, not API keys or user-specific absolute paths.
