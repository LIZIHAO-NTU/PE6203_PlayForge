# D public reproduction evidence

These are development experiments, not formal S1-S5 acceptance.

| File | Purpose |
|---|---|
| FLASH_RESULT.md | Natural-run results, controlled-copy results and limitations |
| flash-runs-summary.json | Sanitized DeepSeek timeout, Flash-Lite format failure and Flash success history; failures are preserved |
| flash-evidence.json | Original successful-run metadata and six selected original files, with UTF-8 text and SHA-256 hashes |
| pr-validation.json | Focused tests, offline reproduction and zero new model-call validation |
| pr-validation.log | Validation logs with personal absolute paths replaced |

The capsule preserves byte-checked copies of summary.json, two final game/ files, two per-round traces/attempts/01/game/ files, and evidence/replay.json. The original run ID is d_step_pilot_20261020_03_flash.

Historical tool and specification fingerprints are in original_experiment. The historical working-tree inventory is preserved; it does not mean every historical untracked document is included in this PR. Generated game code is evaluation evidence and is not supplied in normal generator messages.

Raw model requests/responses, API keys, .env, full browser screenshots and formal independent acceptance materials are excluded. A hash of an omitted body does not imply the body is published. Full local evidence is retained separately; reviewers can recompute the selected audit findings without a model API.

From the repository root:

    python -B -m evals.step_evidence_replay --output reports/d_public_reaudit_new

Use a fresh output directory each time. The tool validates files and records outside the generation path. Log consistency does not prove game-rule correctness or independently authenticate maliciously fabricated logs. The English report-label update is documented separately from the historical tool fingerprint in ../D_STEP_EVIDENCE_EXPERIMENT.md.
