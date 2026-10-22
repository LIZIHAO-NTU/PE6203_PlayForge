# E independent review: D's S4 Tank Rescue

## Scope

Reviewed D's original files from branch `d-s4-handoff` / PR #7, not E's
separate `Reservoir Relay` substitute:

- Requirement: `examples/d_s4/tank_rescue.md`
- Evaluation-only plan: `review_only/d_s4/tank_rescue.acceptance.json`
- D-authored status and exposure instructions: `review_only/d_s4/README.md`,
  `review_only/d_s4/ACCEPTANCE_RECORD.md`, and `docs/D_HANDOFF_INDEX.md`

The D branch tip reviewed was `a3ed28a1df0e8eb0a8a457d8c2194f85ff64c772`.
SHA-256 values recomputed from those exact Git blobs:

```text
tank_rescue.md
8dfafb3b4238bfca8ad6bcc9b159e05ab9254dc5c60bdd90ce84b4312bbc9607

tank_rescue.acceptance.json
21e4afc3527a7fff5a63197863b5bf27e4164c78af857ef36384d244c1c2b6ee
```

Both hashes match D's precheck record. No API call, game generation or browser
acceptance was run as part of this review.

## Checks and rule trace

- `agent.contracts.validate_plan` passes; `plan_warnings` is empty.
- Ten automated scenarios cover all automated requirements; each scenario is
  within the 18 combined-step limit. `review_plan` reports functional tests
  and no coverage warnings.
- Two manual checks are separately assigned: visible instructions/accessibility
  (R8), and terminal Pump/Deliver behavior in both Won and Lost (R6). The latter
  correctly avoids force-clicking disabled controls and checks all four
  terminal/action combinations.
- T2's three Pumps produce `5/3/0 Playing`, `5/2/0 Playing`, then
  `5/1/0 Playing`: water is capped, but each Playing Pump consumes one move.
- T3's two Deliver actions from `2/4/0 Playing` are no-ops because water is
  below four.
- T4: Pump gives `5/3/0`; Deliver gives `1/2/1 Playing`; the next Deliver is
  an insufficient-water no-op.
- T5: Pump, Deliver, Pump, Deliver gives `5/3/0`, `1/2/1`, `4/1/1`, then
  `0/0/2 Won`. This tests winning on the last move and goal-before-loss order.
- T6: four Pumps give `5/3/0`, `5/2/0`, `5/1/0`, `5/0/0 Lost`.
- T7, T8 and T9 cover Restart during Playing, from Won and from Lost; T10
  covers Restart after an invalid action and subsequent normal play.
- T1 checks initial visible values, consistency against the read-only state,
  stability during observation, enabled controls and Restart behavior.

## Review decision

**Pass for specification and acceptance-plan semantics.** The requirement is
deterministic and the expected arithmetic is consistent. Manual terminal-lock
verification is appropriate because the specification permits either disabled
controls or enabled no-op controls, and the manual procedure checks both
without bypassing normal input.

This is a static independent review, not a game result: the game has not been
generated, the ten automated scenarios and two manual checks remain unexecuted,
and held-out eligibility/final candidate freeze remain team decisions. Keep the
acceptance JSON and review-only directory out of all generation, planning and
repair inputs; inspect actual paths/messages before execution.
