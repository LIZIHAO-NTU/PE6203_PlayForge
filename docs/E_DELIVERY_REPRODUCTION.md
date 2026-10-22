# E: Delivery and clean-environment reproduction

## Scope

E's main task is to make PlayForge reproducible and make run exports
understandable without changing the autonomous game-generation workflow. This
work checks the documented clean install, zero-API diagnostics, `export-run`
contents, trace preservation, version distinction and privacy exclusions.

## Issue found and correction

`agent/delivery.py` generated an export README whose command ran
`python -m agent game_design_prompt.md`, while the same README said the Markdown
specification must be supplied separately and `export_run` did not include that
file. Following the command in a new export would therefore fail with a missing
input file.

The generated instructions now use `SPECIFICATION.md` and explicitly say to
supply the approved requirement at that path before running the command. The
specification remains intentionally separate from the exported artifacts.
`DeliveryTests.test_export_keeps_exact_artifacts_and_excludes_credentials`
now asserts the command/input instructions and confirms that the unshipped
`game_design_prompt.md` is not implied to exist.

## Clean-environment record

- OS / architecture: macOS 15.4, arm64.
- Python: 3.11.5.
- Installed from repository pins: Playwright 1.63.0, pyee 13.0.1,
  greenlet 3.5.6 and typing_extensions 4.16.0.
- Browser: Playwright Chromium 153.0.8010.12.
- `doctor`: Python/dependency/browser checks passed; no API key configured;
  `network_api_tested=false`.
- `python -m agent --help` and `python -m agent export-run --help` both ran.
- The test environment was a new `.venv` under `/tmp/pe6203-e-delivery`; no
  environment or browser cache is part of the commit.

## Verification

- `PYTHONPATH=.. python -B -m unittest test_integration.DeliveryTests -v`
  from `tests/`: 4/4 passed.
- `MVP_BROWSER_TESTS=1 ./.venv/bin/python -B -m unittest discover -s tests
  -p test_integration.py -v`: 34/34 passed, zero skips.
- The tests use synthetic runs and model stubs. No real API key was configured
  or used; no model connectivity or real game generation was tested.
- Export checks confirm `game/` and `traces/` hashes match the source, `.env`
  is excluded, the source is unchanged, the original run's agent version is
  distinguished from the exporter version, and no course-acceptance claim is
  fabricated.
- Export intentionally copies traces verbatim. Traces may contain prompts,
  generated source or private data other than the configured key, so they must
  be inspected before sharing. The manifest and README do not claim automatic
  redaction or course compliance.

## Status and remaining limits

The export command mismatch is corrected and covered. Clean local installation,
browser availability, CLI diagnostics and the integration suite are verified
without API use. A real bounded API smoke remains **not run** because this
environment has no configured provider key; do not count it as an attempted or
successful generation. Course-specific packaging layout, final teacher model
and presentation requirements remain for the group to confirm.
