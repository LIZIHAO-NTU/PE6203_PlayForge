# D-authored S4: Tank Rescue

Draft prepared by D on 2026-10-20, published for E's independent review on 2026-10-22. No game has been generated or accepted. The original requirement and acceptance JSON are preserved byte-for-byte; their hashes are in precheck.json. No model API is called to prepare this handoff.

- Generator input: [requirement only](../../examples/d_s4/tank_rescue.md).
- E-only evaluation input: [acceptance JSON](tank_rescue.acceptance.json) and [record](ACCEPTANCE_RECORD.md).
- Status: 10 automated scenarios + 2 manual checks; 84 literal expectations were checked by D's draft arithmetic review, not by a generated game. E has since independently passed the static specification/plan review.

[E's independent static review](https://github.com/LIZIHAO-NTU/PE6203_PlayForge/blob/013727e8daf682272777fa80a0852fea793a20f3/docs/E_S4_REVIEW.md) at commit 013727e passes specification/plan semantics, contract and coverage checks for D's original a3ed28a files. D verified both original hashes remain unchanged on 2026-10-27. This completes pre-run static review, not game acceptance. E still executes after team freeze. If files change, obtain review again and rehash them.

The E-authored s4_reservoir_relay on branch e/s4-s5-evaluation-specs is a separate proposal. This upload restores D's earlier original; it does not overwrite or approve E's substitute. E can independently review this D-authored version. Any decision to adopt E's substitute instead must record E as author and obtain a non-author review.

Formal code SHA, model/configuration/budget, final specification/acceptance hashes, and case eligibility remain team decisions. The task was prepared before final freeze and is not automatically a post-freeze unseen case.

Do not give the generator/planner/repair model this folder, the full repository, acceptance JSON or expected-result record. Public version control does not itself enforce evaluation isolation. Use a clean generation workspace containing only the approved requirement and runtime, keep evaluation materials outside model-accessible paths, and check the actual prompt/input paths before execution. Record any exposure instead of claiming an untouched blind test.
