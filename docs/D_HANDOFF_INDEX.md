# D team handoff index

Published 2026-10-22 by D (513-wys); E main-task review added 2026-10-26. This is a version-controlled development handoff, not a frozen release or formal game acceptance. S4 was previously only in D's local folder; this submission makes the original available to E. Main-task PR #5 is already merged. This branch adds handoff/review material and does not change agent/ or enable production gates.

## Where each member should look

| Item | Location | Owner / next action | Status |
|---|---|---|---|
| D-authored S4 Tank Rescue requirement | [requirement](../examples/d_s4/tank_rescue.md) | E independently reviews D's original | Draft, no generated game |
| S4 acceptance and record | [review-only folder](../review_only/d_s4/README.md) | E reviews 10 automated + 2 manual checks, records corrections before generation | Unexecuted |
| Unified acceptance template | [template](INDEPENDENT_ACCEPTANCE_TEMPLATE.md) | All case authors/executors use consistent metadata, expectations and result counts | Team draft |
| D's main technical experiment | [method](D_STEP_EVIDENCE_EXPERIMENT.md), [evidence](d_step_evidence/README.md) | C review completed; A coordinated PR #5 merge | Bounded development result, not formal acceptance |
| S3 v5 review and supporting snapshot | [review](d_reviews/S3_REVIEW.md), [review-only files](../review_only/d_s3/) | C owns S3, D reviews/executes after team freeze | 79 expectations checked; manual/game execution pending |
| C repair-fix recheck | [review and reproduction](d_reviews/C_REPAIR_RECHECK.md) | A/B/C can inspect D's preserved counterexamples and results | Two saved boundaries fixed; 7 focused tests passed |
| C non-author review / Windows reproducibility | [attributed review and command](d_reviews/MAIN_TASK_PEER_REVIEW.md) | D retained the UTF-8 compatibility note | Main-task review complete |
| E-authored S4 substitute and S5 | [E branch](https://github.com/LIZIHAO-NTU/PE6203_PlayForge/tree/e/s4-s5-evaluation-specs) | E's proposal remains separate; A reviews/executes E-authored S5 | D has not adopted or reviewed the substitute; S5 not reviewed here |
| E's main technical task | [D independent review](d_reviews/E_DELIVERY_REVIEW.md), [results](d_reviews/e_delivery_review.json), [sanitized tests](d_reviews/e_delivery_tests.log), [probe](../evals/d_review_e_export.py) | E prepares its PR and remaining bounded real API smoke; A coordinates integration | No blocker in scoped 426710f instruction fix; 4/4 delivery and 34/34 browser-enabled integration passed; zero real model calls |
| Final group results / report / presentation | No final results authored yet | Collect actual member results after formal runs | Pending, not fabricated |

## Local-to-GitHub completeness audit

All active D-owned handoff categories now have versioned files or an explicit pending status above. The S4 requirement and acceptance JSON preserve the original local bytes. The S3 capsule preserves original reviewed C input/plan bytes, with browsable LF copies alongside it; English summaries and replay helpers make the prior review usable without a local desktop package. Existing PR #4 review and PR #5 evidence are linked rather than replaced. The source manifest lists each newly published file and its hash.

Historical failed model attempts are already preserved in docs/d_step_evidence/flash-runs-summary.json. Full raw model bodies, credentials, private .env, personal-path logs, repeated repository snapshots, generated cache files, old message drafts and the superseded statistical experiment are not active team inputs. Their archival/local status is retained; they are not represented as additional main-task experiments. The E main-task review above is scoped to the stated commit; no formal S1-S5 result is claimed. Other members' private local files cannot be audited from D's computer; this audit covers D's available materials and the visible shared branches.

## Evaluation separation and freeze

Only the approved requirement may enter generation/planning/repair. review_only/, review reports, acceptance answers and trace capsules must remain outside the model-accessible generation workspace and prompt. Public hosting and folder names do not enforce confidentiality or qualify a case as unseen; preserve exposure history. These drafts predate final freeze. The team must confirm case eligibility, final requirement/acceptance hashes, code SHA, model/configuration, budgets and switches before formal S3/S4 runs.

E can review this D-authored S4 without authoring it. E's independently authored s4_reservoir_relay is kept on E's branch; choosing it would require explicit authorship/selection and non-author review. No teammate branch is overwritten here.

## Reproduction and credentials

Install the project's requirements. Use python -X utf8 -B on Windows and fresh output paths. Main-task replay, S3 static expectation arithmetic and C saved-trace rerouting use zero model API calls. Static arithmetic is not game execution. Check the linked review files for commands and limitations. Do not pass the entire repository to an Agent as a single task input.
