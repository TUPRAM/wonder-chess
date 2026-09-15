# B1 controlled balance experiment

Native execution completed for 10 paired seed IDs per arm. The Root75 candidate's provisional numeric screen is **FAIL**. Canonical tuning is unchanged and no human acceptance is claimed.

| Arm / stratum | Encounters | Timeouts | Rate | Median / p90 seconds | Screen |
|---|---:|---:|---:|---:|---|
| control / overall | 1,877 | 237 | 12.627% | 24.65 / 45.00 | fail |
| control / pvp | 1,024 | 207 | 20.215% | 33.75 / 45.00 | fail |
| control / ghost | 75 | 30 | 40.000% | 42.00 / 45.00 | insufficient |
| control / neutral | 778 | 0 | 0.000% | 8.45 / 19.15 | reported_only |
| root75 / overall | 1,899 | 163 | 8.583% | 24.00 / 43.36 | fail |
| root75 / pvp | 1,030 | 152 | 14.757% | 31.93 / 45.00 | fail |
| root75 / ghost | 75 | 11 | 14.667% | 33.75 / 45.00 | insufficient |
| root75 / neutral | 794 | 0 | 0.000% | 8.45 / 18.80 | reported_only |

Round caps: **1/10 control** and **6/10 Root75**. These are separate from combat timeouts; a shorter fight does not guarantee a resolved tournament.

The only experimental tuning edit is `HalfUp(base_pulse * 7500 / 10000)` on Grandmother Root's three star magnitudes, in an in-memory copy of the generated canonical catalog. Timing, geometry, stars, relic evaluation, basic damage, bot policy and timeout adjudication remain the source control. Exact source/executable/evidence hashes are in the companion JSON.

## Recruitment and deployed composition

| Hero | Control / candidate purchases | Control / candidate deployment share |
|---|---:|---:|
| wc_vn_bellback | 1,783 / 1,759 | 24.65% / 24.90% |
| wc_vn_cragstoat | 1,841 / 1,838 | 26.30% / 28.49% |
| wc_vn_grandmother_root | 2,856 / 2,935 | 32.46% / 29.64% |
| wc_vn_snapvine | 1,405 / 1,356 | 15.93% / 15.97% |
| wc_vn_prism_organ | 140 / 137 | 0.66% / 0.99% |
| wc_vn_reefglass | 2 / 5 | 0.00% / 0.01% |

New offer slots, affordability and legal buy feasibility at first observed offer are logged. Actual buys inferred from consumed shop slots reconcile against accepted authoritative bot buy replies for every tournament. Deployment is counted once per live-seat combat lock; ghost copies do not inflate ownership. Star levels represent 1/3/9 acquired copies for investment and deployment-copy totals.

## Fixed-army and charge evidence

Four formation pairs are run at all three star levels, four fixed seeds and both side orientations (192 encounters per arm). Both formations preserve the literal armies and equal represented-copy investment; each pair changes one declared cell component. Every encounter is replayed and compared event by event. `fixture_inputs.csv` stores inputs; `fixtures.csv` stores complete results; `fixture_charge_actions.csv` stores every observed Cragstoat commitment and its resolved-event classification. The JSON preserves each formation/star cohort without treating a placement as a guaranteed improvement.

| Arm / formation | Actor commits | Resolved charges | Encounters with actor charge |
|---|---:|---:|---:|
| control / charge_approach 0 | 19 | 16 | 16/24 |
| control / charge_approach 1 | 60 | 59 | 24/24 |
| control / charge_own_screen 0 | 60 | 59 | 24/24 |
| control / charge_own_screen 1 | 60 | 60 | 24/24 |
| root75 / charge_approach 0 | 20 | 17 | 17/24 |
| root75 / charge_approach 1 | 60 | 60 | 24/24 |
| root75 / charge_own_screen 0 | 60 | 60 | 24/24 |
| root75 / charge_own_screen 1 | 59 | 59 | 24/24 |

In `charge_approach`, formation 0 starts the same Cragstoat in row 3 and formation 1 in row 0, providing room to approach. In `charge_own_screen`, both start Cragstoat in row 0; formation 1 moves Bellback from column 1 to column 3. A screen need not prevent every later charge because units continue moving. These actor-specific counts exclude the opponent's Cragstoat and include all star levels and mirrored orientations.

## Scope and unresolved evidence

- Unchanged provisional bot code revalues the changed healing magnitude; tournament changes include recruitment and matchup drift.
- Encounter counts within tournaments are clustered; no independence or population inference is claimed.
- Healing overheal includes requested minus resolved at logged injured recipients only. Full-health recipients and cancelled tethered pulses emit no heal event; unlogged healing opportunity is unavailable.
- Charge movement landings exclude zero-distance successful charges. Charging sources require a resolved charge damage event. Fixture commitments without resolved events cannot distinguish interruption, changed target, illegal landing, or no remaining recipient with this telemetry.
- Two-second first-death and duplicate-composition summaries are descriptive investigation aids, not adopted acceptance criteria.
- Mirrored side swaps probe orientation sensitivity; stochastic initiative and tie-breaking do not guarantee equal winner rates in a small fixture set.
- Bot-ready simulated tournament timing does not measure human match pacing. Human comprehension, sustain utility and enjoyment remain untested.

The unused confirmation set remains reserved until a candidate is eligible for confirmation. A failed numerical screen does not justify consuming holdout seeds or approving weaker positional sustain. Required next work is to investigate the failed strata and round-cap mechanism, test practical early pressure, instrument charge rejection reasons, and run the separate normal-speed external-player study.
