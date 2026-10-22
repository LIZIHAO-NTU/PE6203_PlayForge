# Team independent acceptance template (draft)

Adapted from the shared S1 draft for S1-S5. Use one record per game. The author writes the requirement, operations and expectations; a non-author reviews before finalization and execution. Case eligibility follows the team's freeze protocol; development cases are not automatically unseen cases.

## Metadata

| Field | Record |
|---|---|
| Case ID / game / requirement file | Pending |
| Author / independent reviewer-executor | Pending |
| Candidate code | Full commit SHA, or pending |
| Requirement and acceptance status | Draft/final; finalization date and both file SHA-256 hashes |
| Model and settings | Model, switches, call/round/time limits; no credentials |
| Execution date / unique result directory | Pending if unexecuted |

## Per-check record

Cover initial state, core actions, invalid/boundary actions, ending and restart. Mark inapplicable mechanisms with a reason. Each check uses a fresh page unless documented otherwise.

| ID | Exact requirement basis | Player operations and starting conditions | Concrete expected observable result | Auto/manual | Actual result | Pass/fail/unverified | Evidence |
|---|---|---|---|---|---|---|---|
| T1 | R... | Fresh-page load | ... | ... | Not run | Unverified | Pending |
| T2 | R... | Exact button/input sequence and counts | ... | ... | Not run | Unverified | Pending |
| M1 | Rule requiring manual review | ... | ... | Manual | Not run | Unverified | Pending |

Give actual locations, numbers, text and behavior; add intermediate expectations when needed. Record preparation/wait conditions. Complete actual results and screenshots/log/result paths after execution. List checks that automation cannot reliably perform as manual; never silently mark them passed.

## Summary

| Field | Record |
|---|---|
| Actually run / generated / started | ... / ... / ... |
| Agent self-test | Original status value |
| Independent automated | Passed ... of planned ...; failed ...; unverified ... |
| Independent manual | Passed ... of planned ...; failed ...; unverified ... |
| Both self-test and selected independent checks pass | Yes/no/unconfirmed, with scope |
| Trace complete / evidence location | Yes/no, missing items and path |
| Manual intervention in development | None/details |
| Actual API attempts / tokens / elapsed time | ... |
| Unresolved issues / reviewer and opinion | ... |

## Counting and isolation

Give only the approved requirement to the generator. Independent acceptance steps/answers must not enter planning, generation or repair messages; verify actual input paths and access. A separate folder in a public repository is not an access-control boundary.

Use ordinary player actions and visible outcomes with read-only cross-checks; never inject state or infer success solely from a screenshot, an open page or self-reported state. Count automatic/manual checks separately. Retain unexecuted, missing-output and missing-evidence entries as unverified within planned counts. A check passes only if all its prescribed observations were completed. No game result means no pass rate.

Keep first-run results and reruns separate. Rechecking one game is not another generation sample. Do not revise expectations after seeing generated results or hand-edit a game to pass. State the checked scope, limitations and original failures.
