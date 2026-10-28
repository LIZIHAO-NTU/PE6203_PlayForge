# C: S2 planning recovery development check (2026-10-29)

This is development evidence for the C branch based on `c94e029`. It does not
replace the frozen S2 record, authorize a main merge, or count as formal S1–S5
evaluation. The original frozen S2 autonomous outcome remains 0/2.

## Failure and change

DeepSeek sometimes drafted an impossible Connect-3 test plan. Examples included
tests over the 18-step limit, a move count beyond the first winning move, and
`board.0` expectations contradicting its declared `cell-0-0` mapping. The
controller correctly stopped or requested review, but this could consume all
five API calls before any game was generated. One development run also had a
transient API transport failure; that failure remains recorded separately.

- Replay explicit gravity rules before freezing a model's test plan. Check
  declared `moves`, `turn`, `status`, and explicitly mapped board cells as well
  as visible elements.
- Reserve API calls for game generation and repair. When model plan drafts stay
  invalid, compile a bounded test plan from the *original specification* only,
  provided the board, controls, rules, priority and offline interface are all
  explicit. Validate the compiled plan with the same contract and gravity
  checks before code generation. The rejected model draft remains in traces.
- Keep this fallback limited to the fully specified small drop-token game. It
  abstains if required facts are missing and never reads game code or held-out
  acceptance material. It does not turn a failing browser check into a pass.

## Verification

Configuration: `deepseek-flash`, up to five API calls, three generation rounds,
360 seconds, strict plan, and two browser verification repetitions per run.
Each row is an independent, fresh development run on the same final code.

| Run | Agent original status | Plan origin | API attempts | Generation rounds | Independent S2 automated acceptance |
| --- | --- | --- | ---: | ---: | --- |
| `S2_compiler_07` | automated passed; manual pending | explicit rule compiler | 4 | 2 | 9/9, twice |
| `S2_compiler_08` | automated passed; manual pending | model plan | 4 | 2 | 9/9, twice |
| `S2_compiler_09` | automated passed; manual pending | explicit rule compiler | 3 | 1 | 9/9, twice |

The three-run development sample is 3/3 for autonomous automated completion
and 3/3 for independent automated acceptance. It is too small to establish a
95% general success rate. The three manual acceptance items have not been
confirmed for these new games. This does not revise the original frozen S2
score. Earlier exploratory runs `01`–`06` used intermediate code revisions and
must not be pooled with the final three-run sample.

Zero-model-API checks on the final code: 24 gravity-plan tests pass; the full
real-browser suite passes 368/368 with zero skipped. Each independent recheck
used zero API calls, repeated all nine checks twice, and verified the source
game files remained unchanged.

Local raw evidence (not committed to GitHub):
`C:\Users\admin\Documents\PE6203_dev_runs\S2_planner_recovery_20261029\`.
The independent acceptance file remains outside the Agent workspace and this
repository. API credentials remain in an ignored local `.env` and are absent
from this branch.
