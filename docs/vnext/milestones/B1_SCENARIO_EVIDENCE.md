# B1 formation persistence and causal fixture evidence

Final native rerun executed 12 September 2026, 15:43:28–15:43:43 UTC (23:43 Asia/Singapore), against `wonder_vnext_solo_0.1.0`, source catalog digest `6e80932173071ef05e58d90a44db3490cfcfde86d48edf33f4a940ff1748efa0`. The current process record and saved fixtures identify this rerun. This is native technical evidence for B1.1, B1.2, part of B1.4 and the bounded F07 investigation. The B1 participant study, understandable inspection, useful/unfavorable transfer, acquisition in actual shops, and balance promotion remain separate gates.

## Delivered behavior

`Simulation/WonderScenario.h` exposes named formation scenarios, six built-in causal pairs, mirrored pairs, five acquisition-limited F07 fixtures, exact save/load, actual combat replay, event totals, and two factual recap statements. The API uses the existing C++ catalog and combat engine. Fixture source contains canonical stable hero IDs and formation inputs; it contains no duplicated combat stats or alternate targeting rules.

The `WCVNEXT-FORMATION-1` format records profile, catalog schema, balance version, catalog digest, scenario identity/name/intended variable, seed, and both armies. Each recruit records its stable hero/relic IDs, globally unique instance ID, stars, local deployment cell and facing. Reordering a catalog adapter's arrays does not substitute a different hero or relic. A real change of content identity rejects the save.

Inputs are bounded to 64 KiB, 512-byte metadata fields, and one through ten normal recruits per side. Validation rejects unknown/corrupt versions, unknown hero/relic IDs, incompatible or duplicate equipped relics, excessive relic slots, duplicate cross-side instance IDs, invalid stars/facing, occupied or illegal deployment cells, hidden stat scaling, neutral substitutes, bench units, and trailing bytes. The checksum detects accidental corruption and is not authentication. Load parses and validates a candidate before replacing the caller's previous valid scenario.

Causal-pair validation fixes roster order, stable instance identity, hero, stars, relics, seed and intended variable. Every actual cell/facing difference must match one explicit declaration. A mirror swaps armies because the combat engine already rotates side B's local cells and facing by 180 degrees. Mirrored encounters execute independently; identical mirrored winners or timings are not assumed.

## Native execution

Run from the implementation checkout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests/runtime/run_vnext_scenarios.ps1
```

The executed MSVC C++20 suite passed **2,732 assertions**, including every truncated prefix and every single-byte corruption of the equipped/starred round-trip fixture, rechecksummed malformed semantic payloads, stable-ID resolution, transactional rejection, actual per-tick combat invariants, damage/healing reconciliation, causal-input validation, and durable local-file failure/recovery checks.

The run covers **29 named scenario records and 28 unique combat inputs**: six pairs in both orientations (24 records) and five F07 acquisition fixtures. F07-L5 and F07-L6 share the same combat input and signature, with different acquisition contexts. Each record was repeated, saved to a `.wcf` file, read back, and replayed with an identical full-event/result signature. These repetitions are not independent balance samples. The 29 records produced **2,421 authoritative events**, with **zero deadlines** in this small selected fixture set. This does not establish the below-2% tournament target or any PvP/ghost stratum result.

Evidence is under `reports/vnext/native-scenarios/`:

- `process.json`: actual compile/test exits, UTC endpoints, source hashes and executable hash.
- `compile.log`, `tests.log`: actual compiler and test output.
- `scenario-results.tsv`: identity, seeds, acquisition bounds, replay signature, result, deadline, timing and per-side totals.
- `scenario-events.tsv`: exact event identity/tick, stable source and target hero IDs, committed action identity, effect/mechanic, cells and damage/healing accounting.
- `fixtures/*.wcf`: 29 exact saved scenario records used by the executed tests.
- `disk-test-*`: retained native disk fixtures for interrupted writes, corruption, recovery and failed I/O.

The scenario seeds 41001–41006 and 42007 identify these authored fixtures. They are development inputs and are not labeled held out.

## Local slot and Lab integration

`WonderScenarioFile.h/.cpp` adds a local slot using the project's existing save-file pattern: exclusive OS write lock, bounded read, flushed staging write, read-back validation, retained previous bytes, then atomic publication. An invalid existing primary is preserved. Load first tries the committed primary, then a validated `.previous` snapshot with an explicit recovery message. Neither `.pending` nor `.previous.pending` is offered as a save.

Native disk checks exercise a Unicode path, exact replacement/backup, later combat parity, empty/partial/complete abandoned staging, missing/corrupt/incompatible/oversized saves, both backups failing, staging and backup I/O failures, a parent that is already a file, invalid current formations, and competing Windows writer lock. Failed operations preserve the last committed primary or current formation as applicable. These are executed file-boundary fixtures, not an unperformed power-cut or clean-machine acceptance claim.

The new `Private/WCVNextScenarios.cpp` provides Lab handlers for next scenario, formation A/B selection, actual A/B replay comparison, mirrored current formation, and save/load at `Saved/WonderVNext/Lab/formation.wcf`. Loading changes the board only after native validation and checking the Lab's supported seed/instance-allocation range. Successful load refreshes replay inputs and clears stale combat/presentation selection; rejected load preserves them. Comparison runs both original fixtures and says explicitly that player board edits are excluded. The visible strike-screen comparison identifies each first struck creature from actual events.

These handlers require the corresponding root-owned Lab header declarations and Slate buttons/text binding. Native compilation does not validate Slate geometry, clicks, packaged execution or human usability; root-owned package evidence records those separately.

## What the formations actually changed

All values below are the unmirrored pair's actual event totals. Health values are engine subunits. A/B denotes the two formations, not the two combat sides.

| Pair | Only declared input change | Actual observed A/B relationship |
|---|---|---|
| F01 Guard | Bellback faces forward/backward | Guard prevention 6,071 / 0. Both formations lose at 14.85 seconds; healing absorbs the difference in incoming loss. Protection does not imply victory. |
| F02 Approach | Cragstoat starts at `(3,0)` / `(3,3)` | Two charge hits in each; 2 / 1 charge movements. An adjacent release can hit without a movement event. Outcomes resolve at 23.90 / 24.10 seconds. |
| F03 Grove | Root starts at `(3,2)` / `(0,0)` | Effective healing 28,000 / 42,000; both lose. The separated position survives longer in this encounter. A supposedly protected starting position is not assumed to be the stronger answer. |
| F04 Strike screen | Opposing Bellback moves `(4,3)` / `(1,3)` | The first strike hits Bellback at tick 56 / Root at tick 51. Total strike hits 2 / 3. The attacker loses / wins in the unmirrored input. |
| F05 Crossfire | Opposing Root and Snapvine spread | Beam-recipient hits 4 / 2; the attacker still loses both. Coverage and winning are distinct observations. |
| F06 Tide | Reefglass faces forward/right | Pushes 1 / 0. The forward-facing tide moves Bellback from encounter `(3,4)` to `(3,6)` at tick 58. Both formations lose. |

Every pair has an actual mechanic-dependent difference, not merely a different hash. The mirrored F04 attacker wins both forms: initiative/side sensitivity changes the winner relationship. The event report preserves this finding. It prevents teaching the unmirrored winner as a universal result and remains an input to further formation review.

`RunScenario` reconciles each damage event's resolved amount with absorbed damage, health loss and overkill, and reconstructs final health from authoritative damage/healing events. Recap displays the actual result, duration, survivors, guard prevention, effective healing, charge hits and pushes. The signature includes all `CombatEvent` fields and the final result. It is a replay identity, not a cryptographic authenticity guarantee.

`grovePulses` counts recipient healing events; a pulse affecting three injured allies counts three. `chargeLandings` counts actual movement events; a released adjacent hit may move zero cells. `deliveredOverheal` counts requested minus effective healing for delivered healing events only. Fully healthy excluded recipients produce no event, so it is not a measurement of all potential unused healing. First meaningful action excludes plain movement; first death is reconciled from the health ledger.

## F07 acquisition boundary

The defender is the same one-star Bellback, Root and Cragstoat formation (purchase investment 4). A cost-1 response at level 3 cannot assume Snapvine, Prism or Reefglass access. Both sides must fit the stated capacity and purchase budget; responses obey their maximum recruit-cost bound. Stars represent 1/3/9 purchased copies. No fixture grants a relic.

| Input | Level | Response purchase investment / budget | Access constraint | Executed outcome |
|---|---:|---:|---|---|
| F07-L3-pressure | 3 | 4 / 4 | Two-star Cragstoat plus Bellback; all cost 1 | Response wins at 24.05 s, one survivor |
| F07-L3-width | 3 | 3 / 4 | Two one-star Cragstoats plus Bellback; one gold unspent | Response wins at 23.90 s, one survivor |
| F07-L4-angle | 4 | 5 / 5 | Snapvine, Cragstoat, Bellback; cost-3 shop weight 10% | Response wins at 22.15 s, two survivors |
| F07-L5-crossfire | 5 | 6 / 6 | Prism, Cragstoat, Bellback; cost-4 shop weight 2% | Response wins at 17.10 s, three survivors |
| F07-L6-crossfire | 6 | 6 / 6 | Same roster as level 5; cost-4 shop weight 5% | Identical combat to level 5; acquisition probability is the changed context |

These are selected native examples of legal purchase investment and nonzero offer access. The budget counts represented recruit purchases; it does not include XP, rerolls, waiting, or foregone alternatives. It does not simulate seeing the needed offers, earning enough gold at a particular round, completing a three-copy upgrade in time, or recognizing the response unaided. The level-5 and level-6 identical fight is one combat input under two acquisition contexts, not independent evidence.

At level 3 the defender's physical screen and Root healing execute; directional guard prevention happens to remain zero because the observed incoming attacks do not produce that link's protection. These early wins do not establish defeat of every guarded-sustain arrangement. Broader defending formations, actual acquisition logs and human adaptation remain necessary before declaring the early-counter decision resolved.

## Still open

This library does not fabricate charge opportunity/failure reasons hidden inside the combat engine, infer an unobserved alternative outcome, issue human acceptance, or promote Root75. Shared engine inspection is owned separately. The factual events support charge commitments/landings/releases and observed targets; proving every no-attempt cause requires an authoritative engine projection.

The six pair differences establish a usable technical investigation set. They do not yet establish that each creature has a comprehensible useful and unfavorable placement on unfamiliar inputs, that players can explain it at normal speed, or that B1 is accepted. Those are the human and transfer tasks in `B0_EXECUTION_CONTRACT.md` and the development roadmap.
