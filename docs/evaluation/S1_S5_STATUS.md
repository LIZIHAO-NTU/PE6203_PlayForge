# S1-S5 evaluation status

Maintainer: D (513-wys). Updated 2026-10-29. This is a living evidence index and status summary, not a new evaluation run or a declaration of final course eligibility. Updates should amend this file with a dated note; preserve historical outcomes.

## Original evaluated batch

Runtime baseline: `c94e029f25e7fa8d6c90197ad051b60ac88d74b2`. Each case has two independent generation attempts. The numerator below counts generated artifacts, not individual assertions.

| Case | Specification author / independent review owner | Actual generation executor | Original autonomous automatic pass | Artifacts passing all selected independent automatic tests | Per-artifact independent checks | Manual evidence and remaining limits |
|---|---|---|---|---|---|---|
| S1 | A / B | D, centralized execution | 0/2 | 2/2 | 9/9 each, two repetitions | A completed post-run transcription review. B confirmed M1-M4, 4/4 for each artifact. Some checks use personal oral confirmation plus existing screenshots/source; no new network or keyboard-repeat event log. Pre-run independent approval is not retrospectively claimed. |
| S2 | B / C | C | 0/2 | 2/2 | 9/9 each, two repetitions | C reported M1-M3, 3/3 for each original artifact, partly confirmed from existing browser records rather than replaying every route personally. Original self-test failures remain. |
| S3 | C / D | D, centralized execution | 2/2 | 2/2 | 10/10 each, two repetitions | Assistant-operated normal UI observations meet M1-M3 for both artifacts, including separate Won/Lost terminal checks, Enter versus Submit, read-only live-state comparison, and supplementary Restart checks. D's personal signoff is not impersonated. |
| S4 | D / E | D, centralized execution | 1/2 | 2/2 | 10/10 each, two repetitions | Pre-run static review exists. E's manual confirmation for both saved generated artifacts has not yet been received. |
| S5 | E / A | D, centralized execution | 1/2 | 1/2 | Run 1: 8/9; run 2: 9/9; two repetitions each | A supplied playtest, narrow-display, live-coordinate and speed evidence. Run 1 T8 remains unstable (pass/fail repetitions); layout and timing-procedure limitations remain. E subsequently revised manual instructions; coverage reconciliation is pending, not an automatic rescore. |

D's S1/S3/S4/S5 batch used OpenRouter `deepseek/deepseek-v4.1-flash-1017`: 8/8 launchable, autonomous automatic 4/8 (50%), selected independent automatic 7/8 (87.5%). C's S2 used direct DeepSeek `deepseek-flash`: 2/2 launchable, autonomous 0/2, independent automatic 2/2. A cross-batch descriptive total is 10/10 launchable, autonomous 4/10 (40%), independent automatic 9/10 (90%). These are different provider/model configurations; do not describe that total as one identical-condition experiment or as full gameplay acceptance.

Original failure statuses: S1 run 1 and S4 run 1 `partial_game_plan_failed`; S1 run 2 and S5 run 1 `plan_review_required`; both original S2 runs `plan_review_required`. Independent checks and later playtests do not rewrite these statuses. S1 formal task eligibility and the actual approval chronology remain for A/D to resolve under the team protocol.

## S5 acceptance revision

E reported commit `92b5beb` adding manual observations for Restart during Playing and Won, requiring the same page without navigation/reload and agreement between visible state and a read-only snapshot. E reported contract validation passed with no plan warnings; requirement and suite hashes were unchanged.

- Plan used for D's original S5 execution: SHA-256 `765356bb9c6f27397b318a5ece67a45e3918b17eee51f12ccba2d225ef9a5335`.
- Newly reported acceptance file: SHA-256 `1cf86291dd256cb258dd62d7536502a006846b52a3cff2f235e2517d20b4dd48`.

This entry records E's supplied message, not an independent inspection of that new file or proof that both games passed the new steps. Compare the revision with A's existing observations and supplement only missing evidence. Keep old results tied to their original plan hash. Do not change the T8 failure or require regeneration merely to supplement manual observations.

## Separate development results

These are development experiments, excluded from the original S1-S5 scores.

| Experiment | Version / attribution | Recorded result | Limit |
|---|---|---|---|
| D, 11 development samples | C adjusted source `443a16b9cad4c2739d2fc4a41af9dee72405e19e`, OpenRouter DeepSeek | Autonomous 9/11 (81.8%); launch 11/11; selected independent automatic 11/11 | Three assistant-operated UI spotchecks, not full manual acceptance of all 11. Separate from S1-S5 and from the earlier GPT batch. |
| C, earlier S2 development | Reported `ba64470`; dev 03-05 share the same recorded source digest | Autonomous 1/3; only one generated game, independent 9/9 twice | Two failures occurred before generation; retain them in the denominator. Two still earlier failures used different versions. New artifact manual confirmation pending in that handoff. |
| C, S2 compiler 07-09 | Same source digest `f2a75511e708ca4a3aa21475acd70dcfd9cf9625d072951f75f2acc39759eccc`, before four-in-a-row scope correction | Autonomous 3/3; independent 9/9 per artifact, repeated twice; 11 total API attempts | Runs 07/09 used explicit-rule compiler plans; 08 used a model plan. C reported personally playing 09 successfully; 07/08 remain manual pending. Not a post-correction model result or a general success-rate estimate. |
| C, PR #9 corrected scope | `f490862111ca1b839928643815303995c98a9646` | Targeted 25/25 and full real-browser regression 369/369, no skips/failures; zero model API | D read supplied logs and verified their hashes; did not rerun them. B reviews scope correction, A checks integration. The earlier model 3/3 does not apply to this commit. Latest merge status must be checked separately; supplied team messages keep it outside the evaluation version. |

PR #9 changes add bounded explicit gravity-rule plan checks and fallback/correction, plus blocked-summary format tolerance. B found a four-in-a-row task incorrectly received a three-in-a-row fallback; C reports the correction now abstains for ambiguous or competing winning lengths. This limited rule support is not proof of general planning correctness.

## Outstanding work and ownership

1. **E:** complete and return the original S4 manual checks for both saved artifacts. This is the main missing original-case manual handoff.
2. **D/E, with A's evidence:** reconcile the revised S5 instructions with the existing playtest evidence and record the remaining qualifications. Do not treat an instruction update as executed acceptance.
3. **D:** review the assistant-operated S3 evidence for final owner confirmation; no personal signature is invented by this summary. Resolve S1 eligibility/configuration attribution with A and retain the post-run review chronology.
4. **B/A/C, development only:** B reviews the PR #9 scope fix; A checks integration and supplied browser evidence; C completes any remaining new-development-artifact manual confirmations. These do not block recording the original batch.

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
