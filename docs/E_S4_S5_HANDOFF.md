# E handoff: S4 review replacement and S5 draft

## Status and authorship boundary

The team table assigns S4 authorship to D and independent review/execution to
E. D's evidence-audit branch explicitly excludes formal S1-S5 materials, and
no S4 requirement or acceptance files were available. At the user's request,
E reconstructed a complete S4 draft so work can continue.

This reconstructed S4 **must not be described as independently reviewed by E**:
E participated in authoring it. Before formal use, D should either adopt and
confirm the exact S4 text or replace it, and another member should check the
final expectations. E can still execute the frozen S4 as assigned. This keeps
the contribution record accurate.

S5 is E's assigned primary specification. A must independently review and
execute S5. Neither acceptance file may be included in model messages.

## Delivered files

- `examples/team_evaluation_20261022/s4_reservoir_relay.md`
- `examples/team_evaluation_20261022/s4_reservoir_relay.acceptance.json`
- `examples/team_evaluation_20261022/s5_pulse_target.md`
- `examples/team_evaluation_20261022/s5_pulse_target.acceptance.json`
- `examples/team_evaluation_20261022/suite.json`

## S4 rule trace

- Initial: water 6, tanks 0, Playing.
- Pump: `min(10, water + 3)`.
- Legal Fill: `water - 4`, `tanks + 1`.
- Insufficient Fill: no state change.
- Win path: `6/0 -> Fill -> 2/1 -> Pump -> 5/1 -> Fill -> 1/2 Won`.
- Won locks Pump and Fill; Restart returns `6/0 Playing`.

The seven automated scenarios cover initial state, ordinary Pump, the cap,
legal Fill, insufficient Fill, win/terminal lock and restart. One separate
manual check covers visible rules and layout.

## S5 rule trace

- Initial: playerX 30, score 0, Playing.
- Arrow keys move at 120 pixels/second; center is clamped to 10 through 350.
- Space at initial x=30 is a no-op.
- The target zone is 170 through 190. Goal-based ArrowRight movement to at
  least 175 stays within the target under the 25 ms polling interval, then
  Space produces score 1 and Won.
- Won locks movement and Space. A short stability observation checks that the
  position does not continue drifting.
- Restart returns `30/0 Playing`.

The seven automated scenarios cover initial state, continuous movement, both
boundaries, a missed lock, reachable win, terminal stability and restart. One
separate manual check covers canvas visibility and responsive layout.

## Freeze and execution checklist

1. D confirms/adopts S4; a non-author validates the final S4 expectations.
2. A independently reviews S5 and records issues or approval.
3. Resolve review comments before freezing; do not edit expected values after
   seeing generated behavior.
4. Record candidate commit SHA, both file hashes, model/provider/JSON settings,
   all feature flags and limits (`5` calls, `3` rounds, `360` seconds unless
   the group approves different values).
5. Confirm the specifications were not used to tune this candidate and the
   acceptance JSON files are absent from generation/planning/repair messages.
6. Run into a new output directory. Preserve startup, plan, self-check,
   independent-check, manual-check, call/token/time and failure evidence.
7. Report missing output, skipped checks and infrastructure failures in the
   denominator. Do not overwrite or silently rerun the original result.

No model API or formal candidate evaluation was run while preparing these
drafts.

## Draft fingerprints

Branch: `e/s4-s5-evaluation-specs`

Branch point: `8eb3145` (`origin/main`, including merged PR #5 at draft time)

```text
s4_reservoir_relay.md
886ebe763884a1d0a063f1c505f37b6e31556123859c5e21cb2eb5633d498e4d

s4_reservoir_relay.acceptance.json
84ae0ffa4170752887b2f1fe05e5a7e1b1f2490db882f6738bde57bf420f50d2

s5_pulse_target.md
f94b79242588b8cf0c8ebfca5af538bc3bbf74337ea771a6f6fd16ffb482b548

s5_pulse_target.acceptance.json
944b723f5da5674168218ac3ae1833244043e8c07f7b04045a0104fcfc45ead2

suite.json
b859b0f70538851125c573f15158fb3c492afd0b9b64c099c9a42e2144c12bd1
```

These identify the drafts supplied for review, not a group-approved formal
freeze. Any review edit requires recomputing the affected hash before use.

## Offline validation

- `agent.benchmark.load_suite` loaded both cases and reproduced the recorded
  requirement and acceptance hashes.
- Both plans passed `agent.contracts.validate_plan` with no `plan_warnings`.
- `review_plan` found functional evidence and the required invalid-action,
  terminal, reset and DOM/state consistency categories. Its only advisory for
  each plan is that `T1` observes initial state without input; later tests
  provide the functional evidence.
- `python -m unittest tests.test_mvp.ContractTests -v`: 8 passed.
- `PYTHONPATH=.. python -m unittest test_quality -v` from `tests/`: 26 passed,
  including 4 opt-in browser tests skipped by default.
- A broader first attempt also encountered the environment's loopback-bind
  restriction in `ServerTests`; this is unrelated to these data-only files and
  is not reported as a passing browser run.

## Direct handoff to D and A

**To D:** The original S4 files were not present in your evidence-audit branch,
which explicitly excludes formal S1-S5 acceptance materials. I therefore
prepared `s4_reservoir_relay.md` and its frozen acceptance JSON as a
replacement draft. S4 follows your assigned resource-cap/terminal mechanism:
water 6, pump cap 10, fill cost 4, two tanks to Won, insufficient Fill no-op,
terminal lock and Restart. Please review the English rule wording and either
adopt these exact bytes as the S4 draft or replace them. Because I authored
this replacement, it is not an independent E review; a non-author must check
the final S4 expectations before freeze. E can execute the frozen S4 after
that review.

**To A:** S5 is E's primary specification, `s5_pulse_target.md`, with its
independent acceptance plan. It covers initial state, continuous movement,
both boundary clamps, Space no-op outside the target, reachable target win,
post-Won stability/ignored input, and Restart. Please independently review the
rule trace, especially the goal-based movement into x=175..190 and the
short-window stability assertion, then execute the frozen S5. Do not send the
acceptance JSON to the generation or repair agent.

**Shared:** The branch is pushed as
`origin/e/s4-s5-evaluation-specs` at commit `fe0e581`. The acceptance and
specification hashes are listed above. Before either formal run, confirm the
candidate SHA, model/provider/settings, budgets, feature flags and input-data
separation. Preserve original failures and report missing or skipped checks in
the denominator.
