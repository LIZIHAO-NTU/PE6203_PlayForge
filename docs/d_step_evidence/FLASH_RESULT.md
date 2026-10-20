# Fast-model development runs: real game and execution evidence

Date: 2026-10-20. The development experiment was retried with faster models. The development requirement, original Agent code, audit logic and acceptance criteria were unchanged; only model selection and the remaining request allowance for the second fast model changed.

## Run history: separate outcomes, no combined success rate

| Run directory | Model | Requests / successful responses | Outcome |
|---|---|---|---|
| d_step_pilot_20261020_01 | deepseek/deepseek-v3.2 | 2/0 | Two planning request timeouts; usage unknown; no game |
| d_step_pilot_20261020_02_flash | google/gemini-2.5-flash-lite | 2/2 | Planning responses took about 8 seconds each; first lacked state_contract, then development_plan items remained invalid after correction; no game |
| d_step_pilot_20261020_03_flash | google/gemini-2.5-flash | 2/2 | Valid plan; real Chromium self-tests passed after first generation |

The two fast-model runs used four requests. Including earlier DeepSeek timeouts, the history contains six request attempts, two with unknown usage. These are not six successful generations.

## Original successful-run results

- Original status: automated_passed_manual_pending, not full game acceptance.
- Total elapsed time: 27.528 seconds; planning API 18.837 seconds, generation API 4.660 seconds.
- API requests: 2; input 8730 tokens, output 4447 tokens. No billing amount was inferred.
- Game location: runs/d_step_pilot_20261020_03_flash/run/game/.
- One original real-browser manifest from round 1, containing six self-tests, 46 steps and 32 observations.
- Independent audit: all six passing conclusions were supported by their steps and observations; no evidence gap was found in this original trace.
- Plan and per-round source fingerprints matched; original run files were unchanged by auditing.

The scenarios cover initial state, collection/scoring, winning, ignored input after winning, restart after winning, and restart from the initial state. They provide a real development trace, are not formal S1-S5 cases, and do not prove full requirement coverage.

## Controlled evidence-copy experiment

Copies of the original passing T2 record were changed separately. The original game, plan, execution manifest and score were preserved.

| Controlled copy | Original gate still accepts overall pass | Independent step audit detects issue |
|---|---|---|
| Remove input action record | Yes | Yes |
| Remove assertion observation | Yes | Yes |
| Mark action unsuccessful, retain pass flag | Yes | Yes |
| Duplicate an action record | Yes | Yes |
| Change action arguments from the frozen plan | Yes | Yes |

The 5/5 result means five predefined controlled record anomalies were detected, not a model error rate. The original gate trusts the verifier to produce complete records; this experiment identifies a boundary where independent step consistency checks can add protection. It does not show that normal execution necessarily omits or fabricates records.

## Supported conclusions and limits

1. One real model-generated game was executed in a real browser and its actual trace was audited.
2. That natural passing trace had complete, consistent steps and observations; no actual false pass was found.
3. In controlled copies, test-level pass flags alone did not expose step-evidence gaps; the independent audit detected all five tested anomaly types.
4. The deliverable is an evaluation tool with bounded evidence, not an applied production-gate patch. C reviews the work; any integration and historical-record compatibility decision belongs with A.

Limits: one simple development requirement and one successful generation cannot establish reliability across all games or models. No natural repair loop occurred, so later-round auditing needs further experiments. Consistent logs do not prove that a verifier is non-malicious or that game rules and test expectations are correct.

## Evidence locations

- Successful run: runs/d_step_pilot_20261020_03_flash/EXPERIMENT.json and run/summary.json.
- Original browser record: run/traces/attempts/01/evidence/replay.json, with local screenshots beside it.
- Audit and copies: audit/AUDIT.json and audit/01_evidence/controlled_mutations.json.
- Published flash-runs-summary.json: sanitized history without keys, raw request bodies or full model responses.

The initial timeout history remains in the local PILOT_RESULT.md; later success does not replace it. No further calls or game corrections are automatic.

## Evidence directly reproducible from this PR

The runs/ paths above are local, Git-ignored history. Selected original bytes are packaged in flash-evidence.json; see README.md for structure, exclusions and the reproduction command. Six supported passes and five controlled anomaly detections can be checked without another API call. The later English report-label update does not alter these original evidence files.
