# D-authored S4: Tank Rescue

Draft prepared by D on 2026-10-20, published for E's independent review on 2026-10-22. No game has been generated or accepted. The original requirement and acceptance JSON are preserved byte-for-byte; their hashes are in precheck.json. No model API is called to prepare this handoff.

- Generator input: [requirement only](../../examples/d_s4/tank_rescue.md).
- E-only evaluation input: [acceptance JSON](tank_rescue.acceptance.json) and [record](ACCEPTANCE_RECORD.md).
- Status: 10 automated scenarios + 2 manual checks; 84 literal expectations were checked by D's draft arithmetic review, not by E or a generated game.

E should first review each expectation against the requirement, particularly pumping at capacity, insufficient-water no-op, and winning on the last move. Record changes before generation and rehash revised files. D's self-check does not substitute for E's independent review.

The E-authored s4_reservoir_relay on branch e/s4-s5-evaluation-specs is a separate proposal. This upload restores D's earlier original; it does not overwrite or approve E's substitute. E can independently review this D-authored version. Any decision to adopt E's substitute instead must record E as author and obtain a non-author review.

Formal code SHA, model/configuration/budget, final specification/acceptance hashes, and case eligibility remain team decisions. The task was prepared before final freeze and is not automatically a post-freeze unseen case.

Do not give the generator/planner/repair model this folder, the full repository, acceptance JSON or expected-result record. Public version control does not itself enforce evaluation isolation. Use a clean generation workspace containing only the approved requirement and runtime, keep evaluation materials outside model-accessible paths, and check the actual prompt/input paths before execution. Record any exposure instead of claiming an untouched blind test.
