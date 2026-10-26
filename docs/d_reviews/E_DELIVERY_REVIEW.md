# D independent review of E delivery/reproduction work

Date: 2026-10-26. Reviewer: D (513-wys). Reviewed E branch e/delivery-reproduction at exact commit 426710fbc1cd07c95443f2882575ad0ac9a5a04c; merge-base 8eb314555011435cb44a70b79f11044ec63472d0.

## Decision and scope

**No blocking issue found in the three-file export-instruction fix.** E should submit the scoped branch as a PR for team integration. This review does not merge E's code or approve final freeze.

D is the designated reviewer of E's main task. This is separate from D's S3 case review/execution and E's S4 case review/execution. Earlier D checks of C's repair boundaries were additional assistance.

## Independent checks

The old export command referred to game_design_prompt.md, which the export did not include. The old text already said to supply a requirement separately, so the change clarifies the command/input handoff; it does not fix a model-generation algorithm. E now uses SPECIFICATION.md and explicitly instructs the recipient to supply the approved requirement there. Both exported README copies agree.

D extracted baseline and candidate Git archives into separate directories. The active D branch and original E files were not edited. A synthetic fixture was exported from each version. Three new instruction checks are false on baseline and true on candidate. All 16 candidate checks hold: source/game/trace bytes preserved; nested artifacts retained; root .env excluded; original/exporter versions distinguished; no fabricated PDF/course acceptance; both README copies consistent; existing/nested output and linked artifacts rejected; CLI and export help load from the new export without the source-checkout PYTHONPATH.

A fake private marker confirms traces are copied verbatim, as E documents. Excluding root .env does not automatically redact trace bodies or guarantee safe public sharing. This is a disclosed boundary, not a newly introduced defect in E's change. No real key or private user data was used in this probe.

| D verification | Result | Scope |
|---|---|---|
| DeliveryTests | 4/4 passed, zero skips | Synthetic artifacts |
| Browser-enabled test_integration.py | 34/34 passed, zero skips, 11.745 seconds | Real Chromium calibration; simulated model responses |
| Baseline/candidate export probe | All 16 candidate checks true; three new instruction checks false on baseline | No real generation or model call |

D reused the existing Python 3.14.3 / Playwright 1.63.0 / Chromium 153.0.8010.12 environment and isolated source/export directories. E's clean Python 3.11.5 installation was not repeated by D and remains attributed to E. D did not rerun the full repository suite. API counts printed by fake-client integration tests are simulated. New real model API calls: **0**. No formal S1-S5 evaluation was run.

## Remaining readiness items

- E explicitly reports the bounded real API smoke as not run. This handoff does not demonstrate provider connectivity or real generation. E should complete the agreed bounded smoke, or the team should explicitly decide how equivalent evidence will satisfy that requirement. D's zero-API review cannot fill that gap.
- The group still needs to confirm the teacher's launch command, output layout, post-run export permission, final model/settings/budget and case eligibility. An export helper is not course approval.
- E's branch is based on an earlier main. A/team integration and candidate regression follow PR preparation; this review covers the stated commit, not later edits or an integrated release.

These are readiness items, separate from approving the narrow export-instruction patch. Do not invent a code defect or claim the whole E task and final freeze are complete.

## Evidence and reproduction

See e_delivery_review.json for version, source hashes and per-check results; e_delivery_tests.log for sanitized tests; evals/d_review_e_export.py for D's independent probe. With project dependencies installed, use a new output directory:

    python -X utf8 -B evals/d_review_e_export.py --checkout /path/to/E-checkout --output reports/e_export_candidate_new

Run the same helper against the stated baseline for comparison. Exit zero means the probe completed; read each boolean in review.json rather than treating it as a blanket pass. The fixture and privacy marker are synthetic. The probe invokes no provider API and refuses an existing output directory. No desktop delivery package was created or updated.
