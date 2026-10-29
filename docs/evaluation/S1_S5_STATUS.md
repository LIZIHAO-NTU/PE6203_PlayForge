# S1-S5 evaluation status

Maintainer: D (513-wys). Updated 2026-10-29. This is a living evidence index and status summary, not a new evaluation run or a declaration of final course eligibility. Updates should amend this file with a dated note; preserve historical outcomes.

## Original evaluated batch

Runtime baseline: `c94e029f25e7fa8d6c90197ad051b60ac88d74b2`. Each case has two independent generation attempts. The numerator below counts generated artifacts, not individual assertions.

| Case | Specification author / independent review owner | Actual generation executor | Original autonomous automatic pass | Artifacts passing all selected independent automatic tests | Per-artifact independent checks | Manual evidence and remaining limits |
|---|---|---|---|---|---|---|
| S1 | A / B | D, centralized execution | 0/2 | 2/2 | 9/9 each, two repetitions | A completed post-run transcription review. B confirmed M1-M4, 4/4 for each artifact. Some checks use personal oral confirmation plus existing screenshots/source; no new network or keyboard-repeat event log. Pre-run independent approval is not retrospectively claimed. |
| S2 | B / C | C | 0/2 | 2/2 | 9/9 each, two repetitions | C reported M1-M3, 3/3 for each original artifact, partly confirmed from existing browser records rather than replaying every route personally. Original self-test failures remain. |
| S3 | C / D | D, centralized execution | 2/2 | 2/2 | 10/10 each, two repetitions | Assistant-operated normal UI observations meet M1-M3 for both artifacts, including separate Won/Lost terminal checks, Enter versus Submit, read-only live-state comparison, and supplementary Restart checks. D's personal signoff is not impersonated. |
| S4 | D / E | D, centralized execution | 1/2 | 2/2 | 10/10 each, two repetitions | E completed M1-M2 for both saved artifacts using normal UI input. Visible English rules and accessible Pump/Deliver/Restart controls were confirmed; separate Won and Lost routes, terminal no-op actions, Restart, and visible/read-only-state agreement passed. |
| S5 | E / A | D, centralized execution | 1/2 | 1/2 | Run 1: 8/9; run 2: 9/9; two repetitions each | A's evidence covers desktop/narrow display, visible movement/coordinates, target and boundary observations, and supplementary speed. E completed the newly clarified Restart checks for both artifacts in Playing and Won: no navigation/reload and visible/read-only state reset agreement passed. Run 1 T8 remains unstable; original scores and qualifications are unchanged. |

D's S1/S3/S4/S5 batch used OpenRouter `deepseek/deepseek-v4.1-flash-1017`: 8/8 launchable, autonomous automatic 4/8 (50%), selected independent automatic 7/8 (87.5%). C's S2 used direct DeepSeek `deepseek-flash`: 2/2 launchable, autonomous 0/2, independent automatic 2/2. A cross-batch descriptive total is 10/10 launchable, autonomous 4/10 (40%), independent automatic 9/10 (90%). These are different provider/model configurations; do not describe that total as one identical-condition experiment or as full gameplay acceptance.

Original failure statuses: S1 run 1 and S4 run 1 `partial_game_plan_failed`; S1 run 2 and S5 run 1 `plan_review_required`; both original S2 runs `plan_review_required`. Independent checks and later playtests do not rewrite these statuses. S1 formal task eligibility and the actual approval chronology remain for A/D to resolve under the team protocol.

## S5 acceptance revision

E reported commit `92b5beb` adding manual observations for Restart during Playing and Won, requiring the same page without navigation/reload and agreement between visible state and a read-only snapshot. E reported contract validation passed with no plan warnings; requirement and suite hashes were unchanged.

- Plan used for D's original S5 execution: SHA-256 `765356bb9c6f27397b318a5ece67a45e3918b17eee51f12ccba2d225ef9a5335`.
- Newly reported acceptance file: SHA-256 `1cf86291dd256cb258dd62d7536502a006846b52a3cff2f235e2517d20b4dd48`.

E has now executed the added Restart observations against both saved S5 artifacts. In each artifact, Restart was checked once from a moved Playing state and once after reaching Won. The URL, `performance.timeOrigin` and navigation-entry count remained unchanged; the read-only state and visible score/phase returned to the initial values. A's existing evidence already covers the other revised manual areas: desktop/narrow presentation, visible movement and `playerX` correspondence, target-zone and boundary observations, and supplementary speed observation. This is a manual coverage supplement only. Keep old results tied to their original plan hash; do not change the run 1 T8 failure, rescore either artifact, or claim a new formal automatic execution.

## E manual confirmation update

On 2026-10-29, E replayed the two retained S4 artifacts and the missing S5 Restart observations from the unchanged archive `S1_S3_S4_S5_统一执行_待人工确认_20261028.zip` (SHA-256 `683cd4a4dfb16d60b75be694a3b31f55e917df04cfbd3d8869760f1fd652aa9c`). No game, plan or result file was edited.

- **S4 M1, both artifacts:** visible English instructions described the resource loop and terminal outcomes; Pump, Deliver and Restart were visible, enabled and exposed with accessible names.
- **S4 M2, both artifacts:** ordinary clicks reached a Won state (`water=0`, `delivered=0`, `rescued=2`) and a separate Lost state (`water=5`, `delivered=0`, `rescued=0`). Pump and Deliver remained enabled at both terminals but did not change state. Restart restored the initial state. Visible values agreed with `window.__gameTest.getState()` throughout the sampled routes.
- **S5 added Restart coverage, both artifacts:** Restart from Playing and from Won restored `playerX=30`, `score=0`, `phase=Playing`. The visible score/phase matched the read-only snapshot, while URL, time origin and navigation count remained unchanged, supporting the required no-refresh/no-navigation behavior.

These checks close E's requested manual handoff and the revised-S5 coverage reconciliation. They do not alter the original autonomous or independent automatic outcomes, do not repair the S5 run 1 T8 instability, and are not a new model/API run.

## Separate development results

These are development experiments, excluded from the original S1-S5 scores.

| Experiment | Version / attribution | Recorded result | Limit |
|---|---|---|---|
| D, 11 development samples | C adjusted source `443a16b9cad4c2739d2fc4a41af9dee72405e19e`, OpenRouter DeepSeek | Autonomous 9/11 (81.8%); launch 11/11; selected independent automatic 11/11 | Three assistant-operated UI spotchecks, not full manual acceptance of all 11. Separate from S1-S5 and from the earlier GPT batch. |
| C, earlier S2 development | Reported `ba64470`; dev 03-05 share the same recorded source digest | Autonomous 1/3; only one generated game, independent 9/9 twice | Two failures occurred before generation; retain them in the denominator. Two still earlier failures used different versions. New artifact manual confirmation pending in that handoff. |
| C, S2 compiler 07-09 | Same source digest `f2a75511e708ca4a3aa21475acd70dcfd9cf9625d072951f75f2acc39759eccc`, before four-in-a-row scope correction | Autonomous 3/3; independent 9/9 per artifact, repeated twice; 11 total API attempts | Runs 07/09 used explicit-rule compiler plans; 08 used a model plan. C reported personally playing 09 successfully; 07/08 remain manual pending. Not a post-correction model result or a general success-rate estimate. |
| C, PR #9 corrected scope | `f490862111ca1b839928643815303995c98a9646` | Targeted 25/25 and full real-browser regression 369/369, no skips/failures; zero model API | D read supplied logs and verified their hashes; did not rerun them. B verified the earlier four-in-a-row example now abstains, but reported two further scope counterexamples; C follow-up and B re-review remain pending. A checks integration. The earlier model 3/3 does not apply to this commit. Latest merge status must be checked separately; supplied team messages keep it outside the evaluation version. |

PR #9 changes add bounded explicit gravity-rule plan checks and fallback/correction, plus blocked-summary format tolerance. B found a four-in-a-row task incorrectly received a three-in-a-row fallback; C reported a scope correction. B subsequently confirmed the earlier four-in-a-row example now disables the three-token fallback and the original S2 rules remain recognized, but reported two further counterexamples: a specification with pre-filled initial cells still receives an empty-board fallback, and adding "A win requires a line of four or more tokens" can still enable the three-token fallback. These are B-reported observations, not independently reproduced by D. General abstention for ambiguous/competing rules is therefore not established. C should address initial-state eligibility and contradictory winning conditions, add counterexample regression tests, and obtain B re-review before claiming the scope issue resolved.

## Outstanding work and ownership

1. **D:** E's completed S4/S5 handoff has been read and reconciled with the summary: both S4 M1-M2 confirmations and both S5 Restart supplements are received. This is review of E's documented observations, not an independent D replay; original outcomes and qualifications remain unchanged.
2. **D:** review the assistant-operated S3 evidence for final owner confirmation; no personal signature is invented by this summary. Resolve S1 eligibility/configuration attribution with A and retain the post-run review chronology.
3. **B/A/C, development only:** PR #9 now includes `3b7e598d753ba0d0e40fdc254ff3e9d735787b04`, addressing the two reported counterexamples. B re-reviews that latest fix; C supplies the reported current-version 371-test browser regression's original log; A checks its version, hash and integration evidence. C completes any remaining development-artifact manual confirmations. These do not block recording the original batch.

No new API calls or game edits were made to create this summary. Original artifacts, result files and private acceptance material remain separate from generation/repair inputs. Do not upload keys, .env, raw model traces or independent acceptance answers to this public status index.

## Evidence index and provenance

D inspected the following supplied materials. Names identify retained handoffs, not public download links; no claim is made that all their contents are in GitHub.

- `S1_S3_S4_S5_统一执行_待人工确认_20261028.zip`: original D run records, selected independent checks and manifest. Original archive SHA-256 `683cd4a4dfb16d60b75be694a3b31f55e917df04cfbd3d8869760f1fd652aa9c`.
- `A_S1_S5_Review_20261029.zip`: A's post-run S1 review and S5 personal/supplementary evidence, with limitations retained.
- `S1_B_人工检查交接_20261029.zip`: B's confirmed original S1 M1-M4 results and evidence scope.
- `S2_C_handoff_20261028(1).zip` plus C's later supplied confirmation: original S2 results and completed manual confirmation. The older archive itself still records then-pending signoff.
- `S3_D_操作检查及证据_20261029.zip`: D's supplementary assistant-operated UI observations, live-state evidence and unchanged-game checks. SHA-256 `ef97b28ae8023197875aee8e567975814af1fd0719e1fa9c3e1f127233a2f258`.
- `S2_C_DeepSeek_dev_handoff_20261029.zip`: earlier development iterations, patch and summaries; supplied manifest verified.
- `C_S2_PR9_f490862_handoff_20261029.zip`: corrected-scope regression logs and redacted three-run summary. Log SHA-256: targeted `ab91bba99c9d8ddb197a2943d6bea5560306006947b3922c2a00c1f848d8cb47`; full browser `542bdcaba8c08eaa629cb19d7ebd05d713476ec3644afb031e73e103d019feda`.

## Update log

- 2026-10-29: Initial consolidated status. B's S1 manual handoff received; original and development outcomes separated; C's corrected-commit browser evidence received; E's S5 instruction revision recorded with original hashes preserved. S4 manual handoff remains outstanding.

- 2026-10-29, subsequent B review: original four-in-a-row counterexample corrected, but pre-filled initial-board and alternative four-or-more winning-rule counterexamples remain reported. C acknowledged the review; no further fix is claimed here. Earlier 25/25 and 369/369 logs retain their original scope and do not establish coverage of these new cases. PR #9 remains outside the evaluation version per supplied team messages; original scores unchanged.

- 2026-10-29, E manual update: completed S4 M1-M2 for both retained artifacts and the revised S5 Restart checks for both artifacts in Playing and Won. S5 visual/movement/coordinate/target/boundary/speed coverage remains attributed to A's existing evidence; E supplied the previously missing no-refresh Restart and state-reset observations. Original automatic results, T8 instability and batch scores remain unchanged.

## Latest development and handoff reconciliation

PR #10 has been merged; this document on main is the maintained summary. E's S4 two-artifact manual handoff and S5 no-refresh Restart supplement are received and recorded above. Do not continue listing those as missing or overwrite A's retained S5 limitations. D reviewed E's documented scope, not a new personal replay. The separately reported `92b5beb` S5 acceptance-file revision is still not independently located or inspected by D; A requested E push it and provide a file/commit link. That file-synchronization question is distinct from E's now-received observation record.

PR #9 remains Draft and unmerged when checked by D on 2026-10-29. Its branch includes `3b7e598d753ba0d0e40fdc254ff3e9d735787b04` (seeded-board and competing-win-rule abstention). A reports both new counterexamples now disable fallback and the focused rules suite passed 18/18; B's latest re-review remains pending. A also confirmed the earlier f490862 logs and hashes agree with the 369-test record. A requested C provide the original 371-test browser log for the newer version before advancing review; receipt of that log is not claimed here. These are version-specific development checks, not new generated-game scores. Earlier 25/25, 369/369 and real-model 3/3 results retain their original versions. No claim is made that the real-model 3/3 was repeated on 3b7e598.

- 2026-10-29, D reconciliation: E's completed manual handoff reviewed; PR #10 merge and PR #9 latest branch commit checked on GitHub. Current development follow-up is B re-review, C latest-version browser-log delivery and A evidence/integration review. Frozen runtime baseline and original scores remain unchanged.
