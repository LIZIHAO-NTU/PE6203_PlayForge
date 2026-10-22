# D recheck of merged C repair fixes

Date: 2026-10-21. Code: c414c91176876d0030ce295ccabf4b4fa4a90e1b (merged PR #3). Two earlier D controlled browser records were reclassified using the merged route_failure, outside the active development checkout. Both now return stop_test_review and original files remain unchanged. These previously missed boundaries were fixed in the tested cases.

D also ran tests/test_c_repair_guard.py: 7/7 passed, zero skipped, including a real-browser runner-stop/game-preservation calibration. No model API was called. D did not rerun the full browser suite; A's 311/311 is attributed to A, not a new D result. No claim of complete diagnostic correctness or formal S3 acceptance follows.

See c_guard_recheck.json, c_guard_focused.log and c_guard_evidence.json. The capsule contains the original plan/result UTF-8 bytes with hashes; it excludes screenshots and raw API bodies. These are constructed counterexamples, not naturally occurring model mistakes.

Re-evaluate on the relevant checkout without API or another browser run:

    python -X utf8 -B -m evals.d_review_c_guard --output reports/d_c_guard_new.json

The output must not exist. The script verifies capsule hashes and checks both resulting stop_test_review actions. Changing the checked-out diagnostics version can change the result; record the actual code SHA. No production routing code is changed by this handoff.
