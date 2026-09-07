# WC-310 / WC-320 runtime implementation and executed evidence

**Runtime checkpoint: passed the implemented C++ contract suite and 100 actual Unreal-hosted all-bot tournaments. Overall playable-alpha acceptance remains separate.** This report covers the runtime lane only; it does not certify final hero art, a packaged human tournament, 2H6B networking, UI quality, audio quality or render performance.

**Later source checkpoint:** presentation event metadata was added after the engine batch reported below. A fresh standalone100 run passed with 2,641,338 assertions and exactly unchanged tournament outcomes and all 17,728 round/seat rows. The original engine batch remains evidence for its original source snapshot; a new engine100 run is pending. See `post-event-metadata/comparison-to-prior-engine.json`, its full CSV archive and hashes. The new metadata records actual basic/ability origin, damage type, authored radius and captured effect center; it does not change combat decisions.

## Implemented source

- `game/Source/WonderChessRuntime/Public/Simulation/WonderSimulation.h`: immutable definition structs, command/reply protocol, persistent seats, public observation type, combat snapshots/events and match interfaces.
- `game/Source/WonderChessRuntime/Private/Simulation/WonderSimulation.cpp`: 50 ms integer combat, all six effect primitives, every selector used by the twelve authored alpha abilities, trait snapshots, reservations/pathfinding, released packet ordering, shields/stuns/stat records, and exact timeout adjudication.
- `game/Source/WonderChessRuntime/Private/Simulation/WonderTournament.cpp`: eight persistent seats, independent seeded shops, transactional purchase/merge/sale/move/swap/reroll/lock/XP/ready, pair enumeration, odd-count ghost copies, simultaneous settlement, ranking/ties/cap, restart namespaces, and seven authored bot personas using the same commands.
- `game/Source/WonderChessRuntime/Private/Simulation/WonderSimulationTests.cpp`: Unreal automation that loads the staged canonical catalog and executes arithmetic/transaction checks plus 100 full combat tournaments.
- `tests/runtime/`: the standalone MSVC harness, fixture generator and exact launch/build instructions.

All numeric hero/rule/persona input comes from the canonical data. No unit-specific combat shortcut supplies an off-screen outcome. Rendering and networking adapters consume the core's state; they do not generate its hits or wins. The rule engine is native C++; Python only prepares standalone fixture input. The exact active catalog digest is `3154592665ce21dc65e5afb06f3769655c8be9ec4157fa6779427c8b8fcc092f`.

## Executed verification

Final standalone command:

```powershell
pwsh -NoProfile -File tests/runtime/build_and_run.ps1 -Tournaments 100
```

It exited 0 under Visual Studio 2022 17.14.31 / MSVC 14.44.35207 with C++20, `/O2`, and `/fp:fast`. The supplied source was also compiled in Unreal Engine 5.7.4. The integration/toolchain lane executed `WonderChess.Runtime.IntegerContracts` and `WonderChess.Runtime.OneHundredActualCombatTournaments`; both passed, along with its two separate data tests. Engine CSV evidence is copied here rather than inferred from the standalone pass.

| Evidence | Final result |
|---|---:|
| Standalone canonical tournaments | 100 / 100 completed |
| Unreal canonical tournaments | 100 / 100 completed |
| Actual encounters, each suite | 7,118 |
| Resolved effect events counted by standalone suite | 1,390,777 |
| Timeout adjudications, each suite | 1,437 (20.19% of encounters) |
| Ghost encounters, each suite | 524 |
| Bot command submissions, each suite | 69,656 |
| Bot command rejections, each suite | 0 |
| Active-seat counts reached | Every count from 2 through 8 |
| Standalone assertions, including per-tick invariants | 2,640,033 |
| Mirror formation/side pairs | 32; no changed team outcome in these specific tested formations |
| Standalone versus engine tournament-row mismatches | 0 / 100 |
| Standalone versus engine per-round seat-row mismatches | 0 / 17,728 |

All twelve authored abilities were observed executing their actual effect type in controlled native combat fixtures. Other checks cover additive arithmetic; ownership and idempotency; atomic rejects; full-bench merging; three-star copy/value conservation; deterministic survivor identity/location; swaps and deployment limits; lock preservation including empty shop slots; XP cap/passive XP; interest; distinct-definition traits; late projectiles after source defeat; same-tick stun/release ordering; shield expiry before impacts; interrupted windups; empty formations; zero survivors with shared first; and stale commands rejected after a fresh restart namespace. Bot command/reroll budgets and normalized features were checked in the full tournament suite. Test assertion totals include repeated invariant checks; they are not a claim of millions of distinct designed test scenarios.

Match simulation time ranged from **14m 12.45s to 19m 20.50s**, with a median of **17m 00.65s**. Thirty seeds reached round 24; reaching that round is distinct from asserting that all thirty required cap ranking. Timeout prevalence and ordering sensitivity remain balance questions. The mirror result is narrow evidence for the supplied formations, not a competitive fairness conclusion.

The named host CPU was read from Windows: **AMD Ryzen 7 6800H with Radeon Graphics**. Final standalone per-match wall time was 564–2,591 ms, median 775 ms, total 85.587 s across the 100 runs. Other editor/integration work ran concurrently. These are accelerated CPU simulation measurements, not GPU/render frame times or a 1080p/60 FPS certification.

## Investigated discrepancy and exact build boundary

The first standalone run used MSVC's default `/fp:precise`. It completed 100 tournaments but produced 7,121 encounters, differing from Unreal in seeds 3 and 46. Inspection showed Unreal's actual response files use `/fp:fast`. Recompiling identical source with that flag reproduced the engine seed 3 result exactly. After aligning the harness flag and canonical digest, the complete 100-seed rerun matched every tournament summary and every one of 17,728 round/seat rows, including economy, damage, wins, placements, settlement IDs and pre/post hashes.

The cause was rare floating-point **bot utility** thresholds. Combat health/damage/time/timeout comparison remains integer. Replay guarantees are therefore scoped to the tested Windows/MSVC build options. The first run and its original logs/hashes remain under `initial-fp-precise/`; they were not overwritten or passed off as the final engine-matching run.

## Evidence inventory and limits

- `runtime-tests.log`, `compile.log`: final standalone execution and compiler output.
- `tournaments.csv`, `mirror-combats.csv`: readily inspectable summaries.
- `standalone-100-evidence.zip`: full summaries, round economy/settlement rows, preparation-lock compositions, and bot observations/features/actions/replies/balances. These logs are data from actual executions.
- `engine-tournaments.csv`, `engine-rounds.csv`, `catalog-digest.txt`: actual Unreal automation output copied from `game/Saved/WonderChessEvidence/`.
- `parity-and-summary.json`: independently compared engine/standalone row counts and metrics.
- `standalone-sha256.json`: final source/test/artifact hashes and compiler boundary.
- `adapter-review.md`: a read-only integration review snapshot sent to the root owner, with concrete authority, restart, presentation and verification-harness findings. Its source hashes distinguish it from subsequent fixes.

No known failing runtime fixture remains in this snapshot. Bot evaluation and tactical placement are bounded prototype heuristics, documented in `tests/runtime/README.md`; they have not been accepted by human playtests or a balance study. Save/replay serialization, broader formation/seed bias studies, complete status-key adversarial permutations, command transport under measured packet loss, and human-facing usability remain separate work or validation. No standalone test executable is offered as the requested Unreal game package. The integration owner must provide the actual packaged executable, 1H7B and 2H6B evidence, finished-asset status and frame-time results in the final product handoff.
