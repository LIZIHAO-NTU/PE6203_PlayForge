# C S2: three development runs, redacted review summary

These are the existing `S2_compiler_07`–`09` DeepSeek runs from before the
four-in-a-row scope correction. They all used the same agent source digest
`f2a75511e708ca4a3aa21475acd70dcfd9cf9625d072951f75f2acc39759eccc`.
The later scope correction is verified separately by zero-API tests; these
three results must not be described as new post-correction API runs.

Original S2 specification SHA-256:
`7962532921c161faadb0564e442be667cc6b1aeb3532a7a901a9b2cfdcc1a2bc`.
The private independent acceptance plan stayed outside the Agent workspace;
its SHA-256 was `5d7850731c7b1714f41cee9c4e2bbfaaab6d84f86b4be29e018342e8767cdbe4`
for every recheck. The plan content, model request/response bodies, credentials,
and raw traces are not included here.

| Run | Plan origin | API attempts | Input/output tokens | Game rounds | Agent tests | Independent tests, repeated | Duration |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 07 | Explicit rule compiler | 4 | 28,380 / 12,115 | 2 | 10/10 | 9/9 twice | 112.28 s |
| 08 | Model plan | 4 | 34,763 / 12,124 | 2 | 6/6 | 9/9 twice | 96.56 s |
| 09 | Explicit rule compiler | 3 | 18,352 / 8,824 | 1 | 10/10 | 9/9 twice | 63.87 s |

All three original Agent statuses were `automated_passed_manual_pending`.
Independent rechecks used zero API calls, completed both repetitions, reported
all nine automated checks passed, and verified the source game files were
unchanged. The user later played run 09 and reported manual success; runs 07 and
08 remain manual-pending. The raw automated summaries were not rewritten.

Game file SHA-256 values for cross-checking:

| Run | `index.html` | `game.js` |
| --- | --- | --- |
| 07 | `7b3cc46c401cc34d1cd1026bad721ce7156e5a4a4c04db40f993bb59ad960baf` | `8d0ed2788a1c11bab1b5cc904454c1caa0dc0d30e497bf52a367951d9668c048` |
| 08 | `39e9f0f79b09ceb0ad94498fba93bf52caa764ef97181d4f5d05c15b5c731f85` | `c5ea33f4758f6602893489daf966941fae2cc001ec010582aabc5a05c86e383d` |
| 09 | `3ab532533e65aebfcc3fdcdfeb724e0b055aab58c1b88faa32439970c3d948f8` | `e3dace797e7a8055e3660a2229d5a50af11d98aac840201ea8d64e3f7cddf9ed` |

This is a 3/3 development sample, not a 95% success claim. The frozen S2
original autonomous outcome remains 0/2 and is not part of this table.
