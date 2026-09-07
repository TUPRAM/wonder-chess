# WC-U410 / WC-U420 native implementation checkpoint

Status: native C++ implementation and execution passed. This is not Unreal asset, packaged-human-play, LAN or frame-time acceptance.

Canonical schema `3.1.0`, balance `alpha_24_v0.4.0`, digest `18ba21c7245750ab01fdc8d37d713daa27e8723a6ffab86b3bd0323a909f2122`.

Implemented in `WonderSimulation.h`, `WonderSimulation.cpp`, and `WonderTournament.cpp`: 24 playable definitions; separate neutral definitions/waves; highest 2/4 trait resolver; Halfling ordinary movement and Dragonkin resistance; ordered damage/stun; Finn's effective attack-rate target priority; eligible Oren shielding; optional absent neutral skills; wave scaling; eight independent neutral combats with nullable ownership; positive absolute-round schedule; separate PvP index and retained pairing/ghost history; authoritative once-only rewards, settlement, neutral counters, cap and restart. Bots use all 24 offers, tier-four progress and public wave formation information through normal commands.

Combat identities include match, round, encounter and side while fitting exactly in JSON's 53-bit integer range. The runtime rejects an overflowing identity instead of publishing rounded/aliased identities.

## Executed evidence

- `native-100-final/runtime-tests.log`: 100 completed actual-combat tournaments, seeds 1–100; **3,292,147 assertions**. 12,748 encounters, 1,771,598 combat events, 1,864 timeout resolutions, 602 ghosts and zero rejected bot commands. Every active-seat count 2–8 appeared.
- The same executable ran all 24 hero skills at three stars, Neris damage-before-surviving-target-stun cases including shield absorption and Mage amplification, Finn targeting and Oren eligibility. It also ran a true forced-cap tournament through round 40 with eight separate combats at all eleven neutral waves, plus empty-roster losses, timeout draws, exact reward application and restart.
- `../../20260906T131459Z/traits-final/build/summary.json`: 174 trait cases, zero failures, 2,535 assertions, 338 combat constructions. Covers all twelve traits, tier-four replacement and duplicate/bench exclusions.
- `../../20260906T131459Z/targeted-final/build/summary.json`: 20 edge cases, zero failures, 1,323,409 assertions, 1,460 combat executions. Includes interruption, released packets, shields, healing, occupancy and determinism fixtures.
- `process.json` records actual compiler/process exits, executable hash, and hashes of the compiled fixture/core/test sources. `summary.json` hashes the evidence CSVs. `git diff --check` passed for the owned native/test files.

The final trait and edge report paths from repository root are `reports/WC-U410/20260906T131459Z/traits-final/build` and `reports/WC-U410/20260906T131459Z/targeted-final/build`.

## Measured tuning findings

Normal tournaments ended in rounds 26–39, median 32. Simulated duration was 1,011.05–1,523.8 seconds, median 1,229.225. Bots finish preparation through policy readiness; these are not measured human match durations or rendered performance.

All 24 heroes and all 24 skills occurred in normal tournaments. Six tier-four traits occurred naturally: Guardian, Halfling, Human, Orc, Ranger and Warrior. Focused fixtures cover all twelve tier-four traits; the remaining six did not occur naturally in this 100-seed batch.

Bots won all 5,810 natural neutral encounters without timeouts. The authored starting wave values are therefore easy against these bot formations and remain **uncalibrated**. Round 40 did not occur naturally; it was executed by the separate high-captain-health forced-cap fixture. No balance data was silently changed to improve the report.

## Reproduction

Use a fresh output directory to preserve retained evidence:

```powershell
pwsh -NoProfile -File tests/runtime/build_and_run.ps1 -Tournaments 100 -OutputDirectory reports/WC-U410/<fresh-UTC>/native
python tests/runtime/summarize_update_native.py reports/WC-U410/<fresh-UTC>/native
pwsh -NoProfile -File tests/runtime/run_trait_combat.ps1 -OutputDirectory reports/WC-U410/<fresh-UTC>/traits
pwsh -NoProfile -File tests/runtime/run_targeted_combat.ps1 -OutputDirectory reports/WC-U410/<fresh-UTC>/targeted
```

The three wrappers now accept isolated output directories, and fixture generation writes into the chosen run instead of overwriting prior build fixtures.
