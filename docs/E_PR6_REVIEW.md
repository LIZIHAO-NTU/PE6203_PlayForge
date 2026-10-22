# E independent review: PR #6 controller-consistency tests

## Review scope

Reviewed branch `a/controller-consistency-20261022` at
`9a82cdd080f9d04e71efed6ed603041f979e0d95`, based on main
`8eb314555011435cb44a70b79f11044ec63472d0`. The diff adds a controller test
module, result/method documentation and converts README presentation to
English-only. It does not modify `agent/` or prompts.

## Findings

No blocking correctness findings in the reviewed test logic or result claims.
The nine scenarios distinguish scripted API-shaped responses from real API
calls, check frozen-plan integrity and output/checkpoint/source correspondence,
and preserve the stated limitation that the tests do not establish game-rule
truth. The controlled plan-tamper test also accurately documents detection
without claiming restoration.

The README's English-only conversion is explicit in the final commit title
(`Make README English-only`) and does not alter executable behavior. The
release information links the new method, handoff, results and tests.

## Independent verification

- Focused default run before installing the isolated reproduction environment:
  9 tests, 8 passed and 1 real-browser test skipped; zero failures.
- Full default run: 343 tests, zero failures, 51 opt-in browser tests skipped.
- After installing the pinned requirements and Chromium 153.0.8010.12 into an
  isolated Python 3.11.5 virtual environment, the focused browser-enabled run
  passed 9/9 with zero skips. This independently confirms the focused suite on
  macOS/Chromium, not A's exact Windows/Edge environment or full 343/343
  browser-enabled result.
- The recorded SHA-256 of `tests/test_controller_consistency.py` matches the
  source hash in A's result index. The PR merge-base matches the stated main
  baseline.
- No real model API was called. No S1-S5 evaluation was run.

## Decision

**No blocking issues found; independent review is complete with the browser
reproduction limitation above.** A's browser-enabled result remains attributed
to A's recorded Windows/Edge environment. This review does not approve a final
candidate freeze or establish a game-generation success rate.
