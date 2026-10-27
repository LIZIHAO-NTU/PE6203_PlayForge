# PlayForge: Stage Handoff and Next Actions

Updated: 2026-10-22. Scope: PE6203 Project 1, five-person team A–E.

This document records the status and next deliverables. It does not change the existing responsibilities or establish a formal freeze or acceptance pass. Members are asked to reply with their status and estimated completion time by **October 23, 20:00**; this is an adjustable internal suggestion, not a course deadline.

## 1. Shared starting point

- Project: **PlayForge: Build a Coding Agent That Can Build a Game**.
- Verified GitHub main: `8eb314555011435cb44a70b79f11044ec63472d0`.
- B's PRs #1/#2, C's PR #3 and D's PR #5 have been merged.
- C's PR #4 is still a Draft. It adds only the public S3 requirement, without independent acceptance answers. D has recorded an independent static review. The PR description now distinguishes the LF and CRLF file hashes correctly.
- This main tree matches the combined tree that previously passed the full browser regression: **334/334, zero skips**. This is framework regression evidence, not an unseen-game success rate.
- A's new controller tests and documentation are published on a separate A branch/PR. **E's independent review is still pending.** Publication does not mean a merge into main; consult the actual GitHub PR status. The result index preserves `status_at_recording` from the original local validation, rather than acting as a live publication status.

GitHub repository: [LIZIHAO-NTU/PE6203_PlayForge](https://github.com/LIZIHAO-NTU/PE6203_PlayForge).

## 2. Goals for this stage

Complete the primary deliverables, cross-reviews and candidate configuration first. Then freeze the evaluation candidate, author the tasks and run the formal evaluation. Do not expand game categories, add complex engines or connect the independent auditor directly to production completion decisions at this stage.

Distinguish three states:

1. **Working baseline:** the shared starting point for continued development, currently the main commit above.
2. **Evaluation candidate freeze:** record the code SHA, model, feature switches, budgets and commands. Do not change the candidate while evaluating it.
3. **Final delivery confirmation:** choose the delivered version after reviewing the complete evaluation. Record fixes under a separate version and results rather than carrying forward earlier conclusions.

The evaluation code can be frozen before all formal S1–S5 runs finish. Under the original plan, formal tasks should be authored after the evaluation candidate is frozen.

## 3. Each member's next deliverable

| Member | Observed progress | Next action | Recipient |
|---|---|---|---|
| A: controller and integration | C/D integration checked; controller-consistency tests and records added this round | Ask E to review the tests, results and scope statements on A's separate branch/PR. Collect member updates and prepare the candidate checklist for team confirmation | E reviews A's primary task; the whole team confirms the freeze plan |
| B: requirements and planning | Two PRs merged; planning issues and negative experimental findings recorded; C and the S1 reference drafts reviewed | Confirm primary-task closure and any changes still required in the candidate. Supply conclusions and evidence links for B's report/presentation contribution; no forced new strategy is required | A confirms integration status; the new formal S2 later goes to C |
| C: generation and repair decisions | PR #3 merged; D reviewed and approved; PR #4 description updated | Confirm any remaining repair blockers. If PR #4 is ready, mark it Ready for review and follow the documentation PR process; do not repeat the resolved hash correction | Coordinate PR #4 with A; the team first confirms formal S3 eligibility |
| D: independent verification and evidence | PR #5 merged; static review of 79 expected values in S3 v5 recorded; S4 draft supplied | Review E's primary task, maintain the shared result index and metric definitions, and ask E about the S4 draft review. Do not take over all five task executions | Primary reviewer of E's task; executor of formal S3 |
| E: reproduction and delivery | No primary-task delivery link has been found in the currently visible materials; this does not imply no work has been done | First share actual progress, material links and expected delivery time. Complete clean-environment reproduction, output/export and privacy checks; verify course startup/delivery requirements; review A's task and the S4 draft | D reviews E's task; send A's review feedback to A |

### Suggested minimum contents of E's delivery

- Python, dependency and browser versions in a fresh environment, with installation/startup records.
- Zero-API checks and one explicitly budgeted real-API smoke test; `doctor` cannot replace model-service validation.
- The relationship between the input, output directory, `game/`, `traces/`, summaries and `export-run`.
- Checks for keys, private paths and raw responses in shared materials.
- A validation/fix conclusion for a startup, reproduction or delivery reliability issue. If no issue is found, provide the verification evidence.
- Sources for the instructor's latest startup method, technical scope, model/budget, submission layout and presentation arrangements. Explicitly mark unannounced or unconfirmed items as pending.

Link existing materials directly; do not repeat experiments merely for this checklist. The team still needs evidence that the complete workflow runs on at least two members' computers; framework tests on one machine are not a substitute.

## 4. A's deliverables and cross-review this round

Question: after stopping for budget limits, exceptions, regression or review, are the final game, selected round, fixed plan and logs consistent?

- New tests: [tests/test_controller_consistency.py](../tests/test_controller_consistency.py).
- Technical explanation and E's review checklist: [A_CONTROLLER_CONSISTENCY.md](A_CONTROLLER_CONSISTENCY.md).
- Result index: [a_controller_consistency_results.json](a_controller_consistency_results.json).
- Results: focused tests **9/9, zero skips**; full browser regression after adding the tests **343/343, zero skips**. These results apply to `8eb3145` plus the local additions; the original GitHub main did not already contain 343 tests.
- Model responses are scripted substitutes; one test uses a real browser. No real model calls were made, so these are not new game-generation samples.
- No defect requiring production Agent changes was found within the tested boundaries. This round adds only tests and records. **E's independent review remains pending.**

## 5. Continuing formal S1–S5

| Specification | Author | Independent reviewer and executor |
|---|---|---|
| S1: movement, boundaries or collision | A | B |
| S2: turns and legal/illegal actions | B | C |
| S3: text or numeric input | C | D |
| S4: resources, caps and terminal states | D | E |
| S5: simple real-time objectives or stability | E | A |

1. **Confirm task eligibility first.** The original handbook requires new English specifications after the freeze. This document recommends retaining that rule and treating existing S1/S3/S4 drafts as references. If the team instead uses previously reserved tasks, record their authorship dates, whether they informed targeted optimization, and their evaluation eligibility. Do not describe a renamed old task as newly authored after the freeze. A initiates confirmation; silence is not consent.
2. Authors supply the original requirement, independent acceptance and expected-outcome rationale. After non-author review, finalize them and record actual file hashes before viewing the generated game.
3. The generation Agent receives only the original requirement. Independent acceptance steps, answers and results must not enter planning, generation, review or repair messages. Separate folders alone do not establish technical isolation; executors must verify actual read paths.
4. Each member executes their assigned task, preserving the first run, failures and unverified items. Separate automatic and manual checks; do not delegate all operations to D.
5. Discuss fixes only after all results from this evaluation are archived. Any source/prompt change gets a separate candidate; preserve earlier results.

S3's current **10 automatic + 3 manual** items describe the acceptance draft, not executed passes. D's **6 evidence-supported passes + detection of 5 controlled anomaly categories** describe development-evidence auditing, not S3 performance.

## 6. Team confirmation checklist before freezing

| Item | Recorded status / confirmation needed |
|---|---|
| Required candidate code | Each owner reports closure or specific PRs/blockers; A's tests receive separate PR review, with E's review pending |
| Current main | `8eb314555011435cb44a70b79f11044ec63472d0`, a working baseline only |
| Full evaluation candidate SHA | Agree after required changes are reviewed and merged; this document does not freeze it |
| Model and endpoint | Pending; if using the team's development model first, distinguish it from a confirmed instructor model |
| Call/round/time budgets | Pending team confirmation; the handbook's 5 calls / 3 rounds / 360 seconds are suggestions, not effective instructor rules |
| Main switches and commands | Record actual settings; do not enable plan audit, structured summaries or cross-run memory by default |
| Environment and delivery | E supplies evidence, D reviews; unconfirmed instructor requirements remain pending |
| Task eligibility and acceptance isolation | Reach a team decision under Section 5 and keep acceptance answers isolated |
| Start formal evaluation | Once the above is settled, each specification's executor starts with the shared configuration |

## 7. Shared group-update format

Each person can reply once with the following information; no extra long report is required:

> - My primary-task status: delivered / in progress / blocked.
> - Deliverable and review links: ...
> - Changes still required in the candidate: none / specific PR.
> - Missing reviews or dependencies: ...
> - Next reviewable deliverable and expected time: ...

Each member supplies their own technical conclusions, report sections and presentation evidence. E standardizes formatting rather than writing everyone's content. Use GitHub to version source, tests, reproduction instructions and selected sanitized evidence; do not commit keys, `.env`, caches or duplicate large run archives.
