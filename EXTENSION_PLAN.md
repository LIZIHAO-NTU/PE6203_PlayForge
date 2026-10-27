# PlayForge — Expansion Plan

Status: bounded 1.1.0 expansion retained; 1.2.0 adds planning/repair feedback and mixed-rule evidence. See RELEASE_1_1.md and RELEASE_1_2.md for failures and limits.

1.2.1 adds bounded cross-test error aggregation, safe blocked-summary metadata and separately measured real repair probes; it does not resolve arbitrary planning/oracle reliability. See RELEASE_1_2_1.md before interpreting success rates.

| Stage | 1.1.0 delivery |
|---|---|
| 0 | Supplied structured expectations checked before freeze; requesting summaries opt-in after observed planning failures, no free-prose parser/oracle |
| A | Native fill/select tools, bounded values, browser events, input-value observations and regression tests |
| B | One platform and one projectile-aiming sample with independent checks; existing continuous-input tools reused |
| C | One local tactical duel and one capped-resource sample; oracle issues retained |
| D | Optional loopback read-only dashboard over existing run evidence; no generation UI or cloud service |
| E | Engines, networking, 3D and persistence deferred |

## 1. Goal

Expand rule and interaction coverage within offline vanilla 2D browser games. Do not equate more game names with better generalization, or add prewritten games, level solvers or game templates. Keep the existing single controller loop and independent acceptance evidence.

## 2. Suggested sequence

| Stage | Candidate work | Expected benefit | Cost and risk | Go/no-go evidence |
|---|---|---|---|---|
| 0 | Structured expected-outcome summaries and assertion agreement checks | Catch contradictions between a correct short explanation and a wrong numeric assertion | Medium; agreement is not proof of the game rules | New held-out arithmetic/terminal variants, no weakening of frozen tests |
| A | Add trusted text-entry and selection actions, with validation, event logs and normal user events | Enable testing word/code puzzles and configurable rules | Low–medium; avoid arbitrary JS, secret entry or hidden answer injection | Correct/incorrect answers, empty input, reset and terminal behavior |
| B | Improve continuous-control testing using existing keys/keys/drag plus bounded observations | Explore simple platformers, aiming and trajectory games | Medium–high; timing and reachability are difficult | Normal movement, collision, failure/restart, one reachable goal; no claim from a screenshot alone |
| C | Evaluate richer discrete state transitions and local two-player rules | Explore small tactics, tile rotation and resource-management games | Medium; test-oracle arithmetic and turn ordering remain weaknesses | Invalid-action no-op, turn ordering, resource conservation, both terminal outcomes |
| D | Optional development-status UI over the existing CLI | Easier teammate use and presentation | Low–medium; must not obscure failures or change course-required startup | Clear running/completed/unverified states; links to game and traces |
| E | Engines, networking, 3D or persistence only after scope confirmation | Potentially broader platform support | High; dependencies, security, deployment and course boundaries change | Written scope confirmation and a separate bounded proof of feasibility |

These are planning estimates, not delivery guarantees. A game may already be generated successfully without being reliably testable by current tools.

## 3. Evaluation before expanding

1. Select one new interaction or rule dimension, not several new frameworks at once.
2. Freeze 3–4 English requirements and independent checks before paying for generation.
3. Include one straightforward example, one rule variant and one mixed-mechanic example.
4. Keep the same model, caps and time budgets for comparisons; preserve first failures and absent artifacts.
5. Run the existing regression suite and previously accepted examples; check for regressions.
6. Report startup, self-plan results, independent selected checks, unresolved manual items, recovery, time and actual API attempts separately.
7. Accept a feature only when its trusted tool behavior is tested and independent outcomes show no clear regression. Small samples still do not establish a universal success rate.

## 4. Model and course compatibility

Do not select a final architecture around an unconfirmed instructor model. Once its endpoint, model ID and supported options are known, verify JSON behavior, request options, timeouts and one full fresh-directory run. Do not claim compatibility from a configured API key or doctor alone.

## 5. Remaining work after 1.1.0

Stage 0 catches structured contradictions, not a simultaneously incorrect summary and assertion. Text/selection tools and narrow B/C samples are implemented, but planning semantics remain a separate limitation. Next evaluate new rule variants and mixed mechanics with preregistered checks, preserve initial failures, and measure repeatability before extending scope. Keep the dashboard optional and E deferred.

## 6. 1.2.0 follow-through

Completed: real 1.1.0 default-mode screening, located draft-validation feedback, evidence-linked repair packets, explicit blocked repair, joint selected-check reporting, and two independently specified text/resource and turn/resource samples. No oracle is inferred from a model explanation. See RELEASE_1_2.md for exact calls, repeatability and unresolved autonomous outcomes.

Remaining: collect more default-mode repetitions and new variants; investigate recurring schema failures without making the accepted DSL more ambiguous; evaluate repair-protocol usage with actual model repairs before claiming behavioral reliability. Interactive generation/cancellation UI and broader external visual evidence remain future work; the current UI is read-only. Model adaptation waits for instructor requirements, as agreed.
