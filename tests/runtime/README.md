# Wonder Chess C++ runtime verification

This harness compiles the same `WonderSimulation.cpp` and `WonderTournament.cpp` used by the Unreal runtime module. It contains no Python gameplay. `generate_catalog_fixture.py` converts the current canonical JSON to a temporary C++ input header so the standalone compiler can receive the same authored numeric fields without adding a second maintained balance source.

From the workspace root on Windows with the installed Visual Studio x64 C++ tools:

```powershell
pwsh -NoProfile -File tests/runtime/build_and_run.ps1 -Tournaments 100
```

Outputs are under `tests/runtime/build/`: the executable, compiler log, execution log, canonical fixture header, per-tournament summary, round economy/settlement rows, preparation-lock roster compositions, normalized bot decision features and accepted replies, and mirror-combat results. Compiler/runtime nonzero status propagates from the script. The build directory is ignored because the header and executable are generated artifacts.

The harness explicitly uses MSVC `/fp:fast`, matching the installed Unreal 5.7 Development response files. An initial `/fp:precise` run diverged in rare floating-point bot utility decisions (seeds 3 and 46), although the combat arithmetic itself remains integer. Rebuilding the same source with `/fp:fast` reproduced the engine's seed 3 divergence. Replay comparisons must include compiler floating-point options, not merely source and data versions. The runtime catalog digest is the generated canonical digest used by the engine; the generator also logs an independent hash of its four numeric inputs.

The tests execute integer arithmetic; authenticated/idempotent/rejected commands; fixed-capacity transactional purchases; deployed-identity and chained upgrades; swaps; shop lock; XP cap; passive XP/interest; twelve authored active abilities; occupancy/reservation invariants on every combat tick; late projectiles after source defeat; same-tick release/stun ordering; shield expiry; interrupted windups; shared first place after simultaneous elimination; fresh restart revisions; and complete all-bot tournaments with actual combat. They also run 32 formation/side swaps to measure ordering sensitivity. The mirror suite records results rather than asserting competitive fairness.

The Unreal automation tests are `WonderChess.Runtime.IntegerContracts` and `WonderChess.Runtime.OneHundredActualCombatTournaments`. They load the real staged catalog through `WCDefinitionRegistry`, run the same core inside Unreal, and write engine evidence to `game/Saved/WonderChessEvidence/`. Actual engine execution is a separate evidence gate from this standalone harness. Neither harness establishes art quality, networking/privacy, presentation, human usability, GPU frame time, or packaged-game acceptance.

## Implementation choices requiring continued review

- Portable SplitMix64 rejection-sampled streams provide private shops, bot tie noise and encounter initiatives. Pairing enumerates all perfect matchings and minimizes immediate rematches, then historical meetings, then an explicit SplitMix64-derived tie value. This preserves the specified lexicographic policy; it does not promise the same tied matchings as the Python SHA256 fixture.
- Cells use row-major order for stable path/dash ties. Encounter-side B rotates both axes. Areas retain their released ground cell. Exact timeout comparison uses small arbitrary-precision positive integers, so it never compares floating-point health-fraction sums.
- The bot evaluator uses the documented normalized feature categories and authored persona weights. Opportunity-cost prototype coefficients are currently 0.35 for gold fraction, 0.25 for interest loss and 0.25 for bench pressure; team/upgrade/trait/role/pair coefficients remain 3/2/1.5/1/0.6. These are explicit unbalanced prototype choices, not measured best values. Tactical placement evaluates up to 24 neighboring relocation/swap candidates using a permitted opponent snapshot and basic protection/support/area-spacing heuristics. No policy can read an opponent shop, bench or gold.
- Public observations are captured on 1500 ms authoritative intervals before bot actions at that tick; bot decisions occur every 700 ms. Reactive reposition candidates stop inside the last 3000 ms. Ready occupies one of the forty allowed command slots.
- The runtime's per-match namespace is transport state. It occupies the high revision bits so commands from a prior restart are rejected. Replay debug hashes include logical revision counters but exclude that process-local namespace, allowing seeded result comparison across separate fresh matches. Hashes cover catalog digest, phase, shop and bot RNG state, economy, roster identity/star/location, offers, lock/readiness, pair history and ghost counts. They are debugging fingerprints rather than persisted save/replay files.
- Profiling fields in `tournaments.csv` describe fixed-step simulation wall time and accumulated unit-state time. They are not render/GPU frame measurements. A timeout is an adjudicated encounter, not a hung combat; its prevalence remains a balance/pace question.

The game must still pass the separate packaged 1H7B and real-process 2H6B, asset, audio, UI, accessibility, performance and human playtest requirements before this runtime work can support an accepted playable-alpha claim.

## Packaged/network evidence reader

The integrated Unreal verification recorder is enabled by `-WCExercise`, `-WCProfile`, or `-WCShots`. `-WCEvidenceDir=<absolute path>` keeps each actual process export in an explicit directory. `-WCExercise` uses normal human command RPCs and records four probes: an out-of-order sequence rejection, an original shop-lock request, its exact duplicate, and changed-payload ID reuse rejection. `-WCRestartOnce` additionally makes the host request one restart two wall seconds after results; both match namespaces retain separate JSON/CSV/screenshots. These switches are instrumentation, not proof of a completed execution. `-WCFast=N` is saved as simulation speed and must be disclosed for accelerated runs.

Audit distinct host/client exports after their actual execution:

```powershell
python tests/runtime/audit_network_evidence.py <host-session.json> <client-session.json> --require-complete --output <paired-audit.json>
python tests/runtime/summarize_frame_evidence.py <session.json> --output <frame-summary.json>
```

The paired reader verifies process IDs, authority roles, human seat bindings, recorded privacy observations, actual probe results, common combat ticks, per-round settlement state and final standings. Missing shared observations remain `NOT_RUN`; they are not treated as passing comparison. It inspects received GameState/client-RPC data, not captured network packets. The frame reader separately filters the exact twelve-visible-living-unit/four-live-encounter condition and reports absent GPU samples or missing 1080p coverage. The Python reader unit test uses explicitly synthetic exports solely to check the analyzer; it never counts as gameplay/network evidence.

`-WCAuthorityChecks` together with `-WCExercise` additionally sends an observed stale revision, sells an actual public opponent unit through the authenticated local controller, and attempts a purchase during actual combat. With `-WCRestartOnce`, it replays the exact accepted first-match request in the new namespace before new commands. These checks require real rejection replies and unchanged owner-private state; a phase/round transition during the observation makes that probe `NOT_RUN`. The default four-probe exercise remains available without the extra flag.

The extra flag also records human-to-bot takeover resource snapshots in a host-only local evidence file. These snapshots include private resources for verification and are never inserted into replicated public state. Resource comparison is conclusive only if no command sequence change, accepted bot decision or phase/round boundary occurred between the two sampled states; otherwise it is `INCONCLUSIVE`. The sampler does not replace a precise atomic Logout trace.

`-WCExitAfter=<wall seconds>` records the real process exit request before calling the platform exit path. Use different host/client durations for actual disconnect checks. An intentional disconnect run must use the separate transition reader because the host correctly ceases to have two human seats after takeover:

```powershell
python tests/runtime/audit_session_transitions.py restart <first-match-session.json> <second-match-session.json> --output <restart-audit.json>
python tests/runtime/audit_session_transitions.py client-loss <host-session.json> <departed-client-session.json> --output <takeover-audit.json>
python tests/runtime/audit_session_transitions.py host-loss <departed-host-session.json> <client-latest-session.json> --output <host-loss-audit.json>
python -m unittest discover -s tests/runtime -p 'test_*audit.py' -v
```

The transition reader follows retained client match files when automatic menu travel changes the latest namespace. Its checks do not establish visible error messaging or physical-LAN networking. Actual launch procedures and source-verified packet-emulation switches are recorded in `reports/WC-310/runtime/packaged-verification-commands.md`.
