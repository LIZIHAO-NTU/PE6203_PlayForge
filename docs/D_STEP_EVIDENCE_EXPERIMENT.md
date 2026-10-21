# D: Step-by-step execution evidence audit

This PR adds a standalone evaluation tool, tests, a development specification and reproducible evidence. It does not modify agent/ or integrate a production gate. The common development baseline is 4cabc9faf01c859a0d5ee45110c1c624df94e544, not a final frozen candidate.

## Technical question and method

When a test reports passed=true, do its recorded actions and observations support that conclusion? The auditor reads each round's replay.json, checks step coverage, arguments, setup/check stages and results, recomputes supported assertion comparisons, and checks plan and per-round source fingerprints. Recorded failures remain failures; unexecuted tails are not invented. Runs without browser manifests are unverified.

For a complete passing record, five separate copies remove an input, remove an observation, mark an action unsuccessful while retaining its pass flag, duplicate an action, or change its arguments. The original gate and independent auditor are compared. Copies do not change the original game, plan, records or score, and do not count as actual model failures.

## Reproduction from the repository root

Install Python 3.10+ and requirements.txt as described in the project README. The validation environment used Python 3.14.3, Playwright 1.63.0 and Chromium 153.0.8010.12 on Darwin arm64. On Windows, use your virtual environment's Python executable.

### Audit the published real trace: no API or browser

    python -B -m evals.step_evidence_replay --output reports/d_published_reaudit_new

The output directory must not exist. The entry point validates hashes in docs/d_step_evidence/flash-evidence.json, restores six selected original files, and writes an independent audit into the new directory. Evidence is for evaluation, not a game template supplied to the generator. Raw API bodies, keys and formal S1-S5 acceptance answers are excluded.

Expected results: one manifest, six supported passing tests, matching plan/per-round game hashes, and all five controlled anomalies detected. Some original artifacts, including API bodies and screenshots, are not published, so the copied inventory is smaller than the full local report; the entire AUDIT.json need not be byte-identical.

### Audit another existing run: no API

    python -B -m evals.step_evidence audit runs/EXISTING_RUN/run --output reports/d_audit_new

This reads the specified run without generating a game, starting a browser or changing original scores. The run should contain summary.json and traces/attempts/*/evidence/replay.json; each round's game/ should be beside evidence/. Existing output directories cannot be overwritten.

### Calibration and regression

    python -B -m unittest discover -s tests -p 'test_step_evidence*.py' -v

Three real-browser calibration tests skip by default. Install Playwright Chromium and set MVP_BROWSER_TESTS=1 to enable them with the same command. For installed Edge, follow the project's PLAYWRIGHT_CHANNEL=msedge instructions. Browser calibration uses synthetic fixtures and no model API; it is not another autonomous generation sample.

Current PR validation is recorded in d_step_evidence/pr-validation.json. After C's focused fixes were merged during submission preparation, an isolated combination of main c414c91 and these D files passed all 23 focused tests including browser calibration; the default regression discovered 334 tests, with 284 passed and 50 skipped. This compatibility check does not constitute a final candidate freeze.

### Optional real generation: calls the API

    python -B -m evals.step_evidence live --output runs/d_live_new --max-calls 3 --max-rounds 3 --max-seconds 360

This bounded development entry point supports OpenRouter. It reads a locally ignored .env: LLM_API_KEY, LLM_BASE_URL=https://openrouter.ai/api/v1 and your LLM_MODEL. Leave LLM_THINKING empty for providers that do not support that option, and match JSON output settings to model capabilities. The successful historical model was google/gemini-2.5-flash; it is not a final course evaluation model. Never commit .env or keys.

Call, round and time limits are not monetary limits. Format and transport retries count toward the call budget. The tool does not automatically start another experiment. PR preparation and validation made no new real-model requests.

## Evidence, findings and limits

See [results](d_step_evidence/FLASH_RESULT.md), the [evidence index](d_step_evidence/README.md), and flash-runs-summary.json for the sanitized history of three development runs.

The single successful generation produced six scenarios, 46 steps and 32 observations; the natural trace was complete and consistent. Its original status was automated_passed_manual_pending, not full acceptance. All five controlled copy anomalies were detected while the original gate continued accepting their pass flags. This identifies an independent consistency-check boundary, not evidence that the normal verifier actually forged or omitted actions.

Limits: one simple development task and one successful generation; no natural repair loop occurred. Log consistency cannot authenticate physical browser events, defeat a malicious verifier, or establish correct expectations and complete gameplay. Use this audit alongside independent acceptance. C has provided a group review; this PR still requires non-author GitHub review and A's integration decision. Shared production gates remain unchanged.

## English presentation update

The current tool changes only Markdown report labels from the historical audit version to English. The original tool fingerprint remains in the historical evidence metadata; it is not the fingerprint of this presentation update. Original run files and embedded evidence bytes remain unchanged. All 23 focused tests, including three real-browser calibrations, passed after the presentation update. An initial attempt omitted the existing browser-cache path and could not locate Chromium; configuring that path resolved the three infrastructure failures without further source changes.
