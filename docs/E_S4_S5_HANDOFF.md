# E handoff: S4 review and revised S5 draft

## S4: D-authored Tank Rescue

D restored the original Tank Rescue specification and evaluation-only plan in
PR #7 (`d-s4-handoff`). I reviewed D's files, not E's separate Reservoir Relay
substitute. The static review passes; the game and all acceptance checks remain
unexecuted. The full decision and independent rule trace are in
[E_S4_REVIEW.md](E_S4_REVIEW.md).

Reviewed D branch tip: `a3ed28a1df0e8eb0a8a457d8c2194f85ff64c772`.

```text
tank_rescue.md
8dfafb3b4238bfca8ad6bcc9b159e05ab9254dc5c60bdd90ce84b4312bbc9607

tank_rescue.acceptance.json
21e4afc3527a7fff5a63197863b5bf27e4164c78af857ef36384d244c1c2b6ee
```

## S5: revised after A's first review

The nine automated checks cover initial state, approximate speed, both
boundaries, Space no-op outside the target, reachable win, terminal lock and
stability, Restart from Won, simultaneous opposite directions, and Restart
during Playing. The manual check compares visible player movement and target
placement with `playerX` snapshots, including start, intermediate positions,
boundaries and target; it also records a supplementary timed speed check.

The target zone is now x=150..210. Goal movement targets x>=180, centered in
the zone, with 30 canvas pixels of margin on either side. T5 asserts both zone
bounds before Space. This tolerates ordinary polling/frame overshoot but makes
no hard real-time guarantee under arbitrary browser stalls; any overshoot
outside the asserted zone fails instead of being counted as a win.

T2 checks a 500 ms hold against a broad displacement interval of 40..80 pixels
(playerX 70..110 from the initial 30), equivalent to a coarse 80..160 px/s
band around the nominal 120 px/s. This is a regression bound, not precision
timing evidence. Manual timing remains supplementary and must record method and
observed displacement/state.

## Files and hashes

- D's reviewed S4 record: `docs/E_S4_REVIEW.md`
- A's independent PR #6 review: `docs/E_PR6_REVIEW.md`
- E-authored separate S4 substitute, retained but not mixed into D's S4:
  `examples/team_evaluation_20261022/s4_reservoir_relay.md` and its acceptance
- E-authored S5: `examples/team_evaluation_20261022/s5_pulse_target.md` and its
  acceptance JSON
- Draft suite: `examples/team_evaluation_20261022/suite.json`

S5 review-draft hashes after A's requested changes:

```text
s5_pulse_target.md
3907aaa11f0ec23419cdf8b193256739111f9aba9b1b7ac2ea96e72b6a059a96

s5_pulse_target.acceptance.json
765356bb9c6f27397b318a5ece67a45e3918b17eee51f12ccba2d225ef9a5335

suite.json
8faac7e8606f224d4e5b5a70431699c04f2ae82b814c2599af9d6c009f9f283d
```

These hashes identify review drafts, not a group-approved formal freeze.

## Validation and next actions

1. E's independent S4 review is static only. After all group freeze conditions
   are met, E executes D's S4 acceptance plan from the review-only location;
   never copy it into the model-accessible generation workspace.
2. A reviews the revised S5 file hashes and strategy, then owns S5's formal
   execution after the same freeze confirmation.
3. No acceptance JSON, expected results, review-only directory or complete
   repository may enter generation/planning/repair messages. Inspect actual
   paths and messages and record any exposure.
4. Freeze candidate SHA, specification and acceptance hashes, case eligibility,
   model/provider/settings, switches and call/round/time budgets before formal
   runs. Preserve missing results, failures and reruns distinctly.
5. E's assigned delivery/reproduction main task and PR #6 independent review
   are separate work items. PR #6 review is complete with no blocking findings;
   focused browser tests passed 9/9 and the default full run passed 343 tests
   with 51 opt-in browser tests skipped. E's delivery/reproduction work is on
   separate branch `e/delivery-reproduction`, commit `426710f`; the README
   export-command correction and clean-environment evidence are there. These
   S4/S5 materials do not substitute for that main task.

No model API, generated game or formal S4/S5 acceptance execution was used to
prepare this update.
