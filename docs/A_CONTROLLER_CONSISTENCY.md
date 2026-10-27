# A: Controller Stop Conditions and Artifact Consistency

Date: 2026-10-22. Author role: A; independent primary reviewer: E, **review pending**.

Publication: a separate A branch/PR, without a direct merge into main. The result index records the baseline and locally added tests at the original validation time. Later commits and pushes do not retroactively rewrite that historical record; consult GitHub for the latest publication/merge status.

## 1. Question, baseline and scope

When the budget is exhausted, the user interrupts, a later candidate regresses or a test conflict appears, the controller should preserve usable evidence and the better version. A stop or successful startup must not be reported as full game acceptance.

The baseline is GitHub main `8eb314555011435cb44a70b79f11044ec63472d0`. This round adds `tests/test_controller_consistency.py` and documentation without modifying `agent/`, prompts, model configuration, course acceptance answers or B/C/D/E's implementations, and without adding game-generation templates.

No defect requiring a production-code fix was found within the tested boundaries. The deliverable is therefore **reproducible boundary tests and validation findings**, rather than a claim to have added budget control, rollback or logging.

## 2. Control flow and inspection points

```text
Original Markdown → Fixed plan → Generate candidate → Trusted tool verification
                                                           ↓
                                  Record failures, compare and select candidates
                                                           ↓
                               Continue bounded repair, or stop for budget/error/review
                                                           ↓
                                 Preserve game/, summary.json, traces/state.json
```

- `agent/runner.py`: budgets, loop, selection, stopping and final outputs.
- `agent/state.py`: repair history and base round within this run.
- `agent/artifacts.py`: local-resource references and optional syntax checks; not proof of gameplay rules.
- `agent/diagnostics.py`: C's failure routing; this round checks only its integration with the runner.

Key checks: fingerprint the candidate source before verification; the final `game/`, selected candidate and original fingerprint must agree. `selected_round` must correspond to the checkpoint's `repair_base_round`. On normal stops, the plan-file hash must match the summary and checkpoint. Both summaries must agree. Failure states must not claim automatic success, and `full_game_acceptance` must remain unknown in every scenario.

## 3. Nine tests

| ID | Scenario | Required controller result | Method |
|---|---|---|---|
| A1 | Round one has a verified failure; the next request is rejected by the call budget | `budget_exhausted`; exit 4; preserve the verified candidate; no success | Scripted responses and budget guard |
| A2 | Time limit reached after first-round verification | No second code request; preserve candidate; zero remaining time | Controlled virtual monotonic clock, without real waiting |
| A3 | Interrupt during the second-round repair request | `interrupted`; exit 130; preserve the first-round candidate | Inject `KeyboardInterrupt` |
| A4 | Interrupt before first-round verification produces a conclusion | Preserve source as `preserved_unverified_candidate`; do not invent a selected round or pass | Verifier substitute injects an interruption |
| A5 | New candidate has the same score but loses a previously passed check | Keep round one rather than replacing it with round two; record regressed test IDs | Two controlled outcomes, not a gameplay oracle |
| A6 | Deliberately rewrite the fixed plan during verification | Detect the change; `run_error`, exit 4; no success | Controlled tampering with a copy; existing runs untouched |
| A7 | Invalid functional plan followed by failed recovery after startup | `partial_game_plan_failed`; only one recovery attempt; startup does not become functional success | Scripted invalid plans and ProviderError |
| A8 | Selected self-tests pass | `automated_passed_manual_pending`; exit 0; full game acceptance still unknown | Successful control case |
| A9 | C's routing detects a fixed-test conflict | Stop after the first round in a real browser; no second code call; preserve game and plan | Real Edge; scripted model responses |

A6's boundary: it verifies **detection of a rewrite and refusal to claim success**. The controller does not automatically restore the modified plan. The changed file and discrepancy from its original hash remain explicit. This is not a security guarantee against malicious processes and does not establish that plan files remain unchanged in every circumstance.

## 4. Results and sources

- Initial zero-API focused run: 9 discovered, 8 passed, 1 browser check skipped by default.
- With a real browser enabled: focused tests **9/9 passed, zero skips**.
- Full browser regression on the final test version: **343/343 passed, zero skips**, approximately 190.925 seconds; focused run approximately 5.205 seconds. See [a_controller_consistency_results.json](a_controller_consistency_results.json) for results and source fingerprints.
- Local environment: Windows, Python 3.11.9, Playwright 1.63.0 and Edge channel `msedge`. Exact versions are in the result index.
- Real model requests: **0**. ScriptedClient uses test configuration and explicitly blocks provider requests. The full regression allows localhost HTTP tests and blocks unmocked external model requests.

Scripted request counts test budget control; they are not API charges. Real-browser execution verifies fixture integration and does not add real-model generation samples.

## 5. E's independent review

Obtain the actual working tree containing these new tests, or the subsequent PR. Running only the original main cannot establish a review of these additions. Install dependencies according to the README, then run from the repository root:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m unittest discover -s tests -p test_controller_consistency.py -v
```

The default result should be 9 tests: 8 passes + 1 browser skip. To use an already installed Edge, enable browser checks:

```powershell
$env:MVP_BROWSER_TESTS = '1'
$env:PLAYWRIGHT_CHANNEL = 'msedge'
python -B -m unittest discover -s tests -p test_controller_consistency.py -v
```

Expect all 9 to pass. For Playwright-installed Chromium, do not set `PLAYWRIGHT_CHANNEL=msedge`; use the appropriate local cache configuration. These tests need no real key, account balance or `.env`. Full framework regression:

```powershell
python -B -m unittest discover -s tests -v
```

Temporary outputs are under `.codex-tmp/`. Follow workspace rules to remove only temporary files created by your own run; do not delete others' existing runs.

E should independently check and record:

- [ ] Changes are limited to A's tests and documentation, with no incidental changes to teammates' logic.
- [ ] Boundaries between scripted responses, virtual time and real-browser execution are accurate; substitutes are not presented as model capability.
- [ ] Exit codes, game copies, plan hashes and summary/checkpoint correspondence are checked for every state.
- [ ] A6's tampering-detection limitation is clear, and A8 is not full acceptance.
- [ ] Focused tests are reproduced locally, recording Python/browser versions, passes/skips/failures and actual source version.
- [ ] The subsequent PR or handoff explicitly records “no blocker / changes needed / unable to reproduce”; approval is not filled in on the reviewer's behalf.

## 6. Candidate-freeze readiness

Only A's author-side validation is complete in this record. E's independent review, required PR reviews/merges, and team agreement on model, budgets, commands, task eligibility, cross-machine evidence and course delivery requirements remain necessary. Current main does not automatically become a frozen release.

Existing S1 drafts remain pre-freeze references. A new formal S1 is to be authored after the evaluation-candidate freeze and handed to B. A also later independently reviews and executes E's S5. The report/presentation may cite these tests, but must not present existing framework capabilities or C's conflict detection as newly implemented from scratch by A this round.
