# C / PR #9: initial state and competing win-rule follow-up

B identified two more cases where the three-token fallback could replay the
wrong game: a pre-populated initial board and an additional rule requiring a
line of four or more tokens. The fallback now requires an explicit statement
that all cells start empty and abstains when another initial-state sentence
mentions board cells, tokens, or pieces. It also abstains on a conflicting
`line of four or more tokens` rule. When it abstains, it supplies no reference
paths, compiled plan, or deterministic conflict verdict for that specification.
The original S2 rule remains recognized.

Regression tests cover an initial board with an A token, an additional
pre-placed-token rule, a board that starts with a token, an explicit exception
to empty cells, and the additional four-or-more-token win rule. The tests
failed before the change and passed afterward. The focused gravity-plan suite
passed 27/27.

The zero-model-API, real-browser full suite was run with
`MVP_BROWSER_TESTS=1` and `PLAYWRIGHT_CHANNEL=msedge`. Its first run had one
unrelated `test_dashboard_has_no_mutating_endpoint` connection-aborted error
among 371 tests. That test passed when rerun alone. A fresh full suite then
passed **371/371, zero skipped, zero failures** in 255.245 seconds. The failed
run and final full log are retained locally in
`C:\Users\admin\Documents\PE6203_dev_runs\S2_planner_recovery_20261029\`:

- `initial_win_scope_full_browser_venv.log` SHA-256
  `9FAC3728FC587C1EA1716FF97F79B83F7116913FB26083C2E5271E23401E09D0`
- `initial_win_scope_full_browser_retry.log` SHA-256
  `FFC63ADCC4448029095638D2F39426E406E89377F4615085B7B833D4CAFC3C2A`

This follow-up made no model API calls and does not create a new game outcome.
The earlier three DeepSeek development runs predate both scope fixes. The
frozen S2 autonomous outcome remains 0/2, and PR #9 remains outside the
evaluation version pending review.

## Original S2 file regression after B's counted-cell finding

B pointed out that the original S2 specification says `All 12 cells start
empty.` rather than `All cells start empty.` The recognizer now accepts either
form, but checks that a stated cell count equals columns times rows. An
incorrect count or another initial-state exception still disables the
fallback. A test derived from this S2 sentence and negative count-mismatch
cases failed before the fix and passed afterward. The previous pre-populated
board and competing four-token rule tests still pass.

I also directly checked the original `S2_line_drop_spec.md` entry from the
received `S2_to_C_review_20261028_v2.zip`, without copying the independent
acceptance file into the repository or Agent workspace. Its SHA-256 is
`7962532921c161faadb0564e442be667cc6b1aeb3532a7a901a9b2cfdcc1a2bc`.
On this exact source file, rule recognition is true, reference paths include
horizontal, vertical, diagonal, and draw, and the compiler returns a plan.

The focused gravity-plan suite passed 28/28. A new zero-model-API complete
real-browser run with `MVP_BROWSER_TESTS=1` and Edge passed **372/372, zero
skipped, zero failures** in 232.614 seconds. Local log files are retained at
the path above:

- `counted_empty_targeted.log` SHA-256
  `FA8D28936D8706ECA5703BDF429748698FC0820968A090A4580B81CAF40B1FFC`
- `counted_empty_full_browser.log` SHA-256
  `20C6813B6E701CF89038042F12C7CCC5C877447A73AE99349300B56570570968`

This is a development-branch scope fix, not a new real-model run or a change
to the frozen S2 0/2 result.
