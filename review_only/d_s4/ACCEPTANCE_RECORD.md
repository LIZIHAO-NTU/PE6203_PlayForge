# S4 Tank Rescue: independent acceptance record draft

Author: D. Independent reviewer/executor: E (static review complete; execution pending). Requirement: ../../examples/d_s4/tank_rescue.md. Acceptance: tank_rescue.acceptance.json. Based on the team acceptance template. Expected values were written before generation; none below are observed game results.

| Metadata | Value |
|---|---|
| Candidate commit / model / switches / call-round-time budgets | Pending team agreement; never include keys |
| Specification and acceptance | Draft; hashes in precheck.json; rehash if revised |
| Formal unseen-case eligibility | Pending; prepared before final code freeze |
| First execution date / unique output directory | Not executed; use a fresh directory |
| Review decision and date | Static semantics passed in [E report](https://github.com/LIZIHAO-NTU/PE6203_PlayForge/blob/013727e8daf682272777fa80a0852fea793a20f3/docs/E_S4_REVIEW.md); status linked by D on 2026-10-27; game execution pending |

Each automated scenario starts on a separate fresh page and uses normal player buttons. Value order: water / moves / delivered / phase.

| ID | Requirement | Player operations | Expected observable result | Method | Actual / verdict / evidence |
|---|---|---|---|---|---|
| T1 | R1/R9 | Load, wait briefly, check enabled buttons, restart in initial state | 2/4/0/Playing; read-only values agree; resources stable during observation; restart preserves initial values | Auto | Not run / unverified / pending |
| T2 | R2/R9 | Pump three times, check after each | 5/3/0/Playing, 5/2/0/Playing, 5/1/0/Playing | Auto | Not run / unverified / pending |
| T3 | R3/R9 | Deliver twice from initial state | Each remains 2/4/0/Playing; no move is spent | Auto | Not run / unverified / pending |
| T4 | R3/R4/R9 | Pump, deliver, attempt deliver again | After valid delivery 1/2/1/Playing; insufficient-water delivery changes nothing | Auto | Not run / unverified / pending |
| T5 | R2/R4/R5/R9 | Pump, deliver, pump, deliver | Intermediate 1/2/1/Playing then 4/1/1/Playing; final 0/0/2/Won, never Lost | Auto | Not run / unverified / pending |
| T6 | R2/R5/R9 | Pump four times | Third 5/1/0/Playing; fourth 5/0/0/Lost | Auto | Not run / unverified / pending |
| T7 | R7/R9 | Pump, deliver, restart | Restore 2/4/0/Playing | Auto | Not run / unverified / pending |
| T8 | R7/R9 | Pump, deliver, pump, deliver; confirm Won, restart | Confirm 0/0/2/Won, then restore 2/4/0/Playing | Auto | Not run / unverified / pending |
| T9 | R7/R9 | Pump four times; confirm Lost, restart | Confirm 5/0/0/Lost, then restore 2/4/0/Playing | Auto | Not run / unverified / pending |
| T10 | R3/R7/R9 | Invalid initial delivery, restart, pump | Restart 2/4/0/Playing; pump 5/3/0/Playing | Auto | Not run / unverified / pending |
| M1 | R8/R9 | Inspect English instructions, native buttons, visible surface and accessible names | Instructions cover all stated rules; button names understandable | Manual | Not run / unverified / pending |
| M2 | R6 | Reach Won and Lost separately; check each Pump and Deliver control | Disabled controls cannot be activated normally; enabled controls do nothing; visible/read-only values remain consistent | Manual | Not run / unverified / pending |

Record all four M2 branches separately: Won x Pump, Won x Deliver, Lost x Pump, Lost x Deliver. Do not force-click disabled controls. During Playing, both action buttons must remain enabled; Restart must be enabled in every phase.

E's review should check reachability, fresh-page independence, exact expectations, setup and step limits, visible DOM values with read-only cross-checks, and missing constraints. No state injection, hidden player actions or result-driven edits to expectations. T5's third action yields water 4, not 5. This finite plan does not prove all possible inputs or games correct.

| Result field | Current value |
|---|---|
| Game generated / started / actual acceptance executed | No / unverified / no |
| Agent self-test status | Not run |
| Independent automated checks | Passed 0, failed 0, unverified 10 of 10; no pass rate |
| Independent manual checks | Passed 0, failed 0, unverified 2 of 2 |
| Both self-test and selected independent checks pass | Unconfirmed |
| API attempts / tokens / elapsed model time for S4 | 0 / 0 / 0 |
| Evidence / trace completeness / manual development intervention | Pending execution |
| Remaining work | Team case eligibility; frozen SHA/configuration; final hashes; actual execution by E |

Preserve first results, failures, absent outputs and missing evidence. Save later reruns separately. Passing all automated checks cannot replace manual checks or establish complete game quality.

Independent-review provenance: E report commit 013727e8daf682272777fa80a0852fea793a20f3 reviews D commit a3ed28a1df0e8eb0a8a457d8c2194f85ff64c772. Requirement SHA-256: 8dfafb3b4238bfca8ad6bcc9b159e05ab9254dc5c60bdd90ce84b4312bbc9607; acceptance SHA-256: 21e4afc3527a7fff5a63197863b5bf27e4164c78af857ef36384d244c1c2b6ee. Both original files are unchanged. No game result is inferred from static review.
