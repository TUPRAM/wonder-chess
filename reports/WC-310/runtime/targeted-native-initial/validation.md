# Actual native combat boundary and formation checks

PASS: 20 groups, zero failed, 1,460 actual combat constructions/executions. MSVC compile and process exits were both0; compiler194435226 and `/std:c++20 /O2 /fp:fast /W4` were used. The pure C++ core source SHA256 is `96019f1f3d5b34fc0e79674c958b01551c28d73643c0fd81850322eb2b87988e`.

The matrix completed720 scenarios plus720 observed replays, with 77 supported timeouts and 160,860 events in the720 primary rows. All720 compared replay signatures matched; no checked occupancy, reservation, identity, health or shield invariant failed.

The five formations use six distinct canonical alpha heroes, cost10 at one star,30 at two stars and90 at three stars. Each matchup has equal star and equal acquisition cost. Eight seeds, three star levels, both seat orientations, and self-matchups were executed. Full row data and exact deployment coordinates are preserved in the build CSV files.

Across 240 cross-formation mirror pairs, 29 changed their winner relative to formation A. This is observed position/initiative sensitivity, not a claim that the metagame is solved.

| Formation | Seat appearances | Wins | Losses | Draws | Timeout appearances |
|---|---:|---:|---:|---:|---:|
| shield_heavy | 288 | 127 | 161 | 0 | 40 |
| sustain | 288 | 101 | 187 | 0 | 83 |
| spread_ranged | 288 | 240 | 48 | 0 | 0 |
| paired_mage | 288 | 183 | 93 | 12 | 7 |
| rogue_pressure | 288 | 63 | 225 | 0 | 24 |

The targeted checks actually delivered delayed shield packets to existing shields: stronger replaced amount/expiry/source, equal later refreshed, weaker and equal earlier left amount/expiry/source untouched. Physical mitigation before shield absorption, true-damage overflow/overkill, effective heal cap, defeated-target exclusion, each independent orthogonal corner blocker, a physically empty reserved orthogonal blocker, destination contention, origin retention, movement/dash interruption, an enclosed corner, dash zero damage, and maximum-expiry stun refresh all passed.

## Evidence boundaries

- These are native MSVC executions of current authoritative Combat, not Unreal Automation or packaged network tests.
- Controlled edge fixtures copy the canonical catalog in memory, remove trait bonuses, set deterministic health/damage/range/timing and effect routing, and do not modify canonical files or production code.
- The matrix uses unchanged canonical unit stats, abilities, traits, and rules. All five formations have six distinct heroes and base cost10; all seats use the same star in each scenario.
- The720 matrix rows comprise480 cross-formation oriented scenarios plus240 same-formation rows. Same-formation swapped rows repeat120 identical inputs, leaving600 distinct initial-input scenarios.
- Observation replay reads simulation state and events at each tick; it does not test rendering, networking or user-interface observation. Compared fields are exactly those in Signature().
- Read-only replay checks and all invariant assertions dominate the assertion count; assertion volume is not a quality or performance score.
- Mirror outcomes can change because a seed determines initiative in side insertion order and board route tie-breaking is absolute. The report records these differences without declaring them necessarily defects or balanced outcomes.
- This is a bounded formation sample, not an exhaustive strategy search or proof of solved balance. Frame-time and audio/visual acceptance are outside this harness.
- Empty battles, released projectile after source defeat, expiry-tick shield ordering, and tournament frame-hitch recaps were executed in the separate existing runtime suite; they were not rerun in this new executable.

Rerun from the workspace with `./tests/runtime/run_targeted_combat.ps1`, then `python tests/runtime/analyze_targeted_combat.py`, using the current PowerShell execution policy. This overwrites this harness's build outputs; preserve an earlier evidence bundle before a future source change. `validation.json` binds all current source, canonical input, executable and raw evidence files.
