# Three-hero mana experiment — 13 September 2026

Owner instruction: try mana for Snapvine, Prism Organ and Reefglass, keeping Bellback, Cragstoat and Grandmother Root as the control and leaving damage, prices and targeting unchanged.

## Decision from the measured first arm

**REVISE; retain as an opt-in experiment. Do not promote this tuning to the default.** The resource implementation passes native contracts and the paired simulations, but this zero-start/10-per-basic tuning delays signature skills and increases tournament caps in the development sample. No human enjoyment or balance acceptance has occurred. Package and presentation evidence is recorded separately below and in `reports/vnext/milestones/mana-20260913/verification.json`.

## Exact implementation contract

- The original canonical catalogue fields remain JSON-value identical; only an `experiments.mana100_v1` recipe is added. `protected-catalogue-parity.json` records the comparison against the preserved pre-change source.
- Default `WonderVNextCatalog()` remains cooldown based. Generated `WonderVNextManaCatalog()` changes only the three named abilities' mana configuration and the experiment's content/balance identity. `-WCManaExperiment` selects it after staged-byte verification.
- 100 maximum mana, zero starting mana. Values are integer centimana. A landed basic attack earns 10, once per attack. Actual hostile HP loss earns 10 per 10% maximum HP lost after armor, resistance, directional protection and shields.
- Incoming mana is capped at 20 per damage event and 40 per non-overlapping one-second accounting window. A new window begins with the first eligible damage event after the previous window expires. These are window caps, not a sliding-window claim.
- Skill damage grants no outgoing mana; healing and shield application grant none. Shield absorption grants no incoming mana. Dead creatures gain none; held mana is recorded and cleared at death. A new encounter starts fresh.
- Full mana waits for a valid target/geometry and an available action. Spend at commitment; interruption does not refund it. Gain pauses until that committed cast's original recovery tick, including when interrupted. The old first-cast/cooldown timers do not gate mana casting. Basic attack recovery remains respected.
- Cooldown relic modifiers become inverse mana-gain modifiers for these three heroes. Example: Quick Wick's 0.8 timing factor gives 12.5 mana per basic while retaining its existing damage reduction. Incoming caps still apply. All existing magnitude, range, radius, duration, cast-time and non-mana cooldown transforms remain unchanged.
- The frontend adds a camera-aligned blue mana bar and numeric charge to the nameplate only for mana users, displays charge/cast/recovery readiness in the scrollable inspector and labels the experiment. Mana solo saves default to a separate filename and carry a distinct content identity. Existing cooldown saves are not overwritten by the experiment.

## Comparison design

Both arms use tournament seeds 1–100 and unchanged bot/economy policies. Later compositions can diverge after different battle outcomes, so tournament statistics are system-level observations. Reserved confirmation seeds 900001–900250 remain unused.

The fixed comparison has 576 encounters per arm: three focal heroes × protected/exposed placement × three star levels × both side orientations × 16 seeds (1001–1016). Identical army inputs and seeds are replayed with full event parity. Each focal hero faces the same Bellback/Root/Cragstoat opponent template; costs differ across focal heroes, so this is not an equal-cost ranking of heroes. The runner additionally retains its existing 192 formation fixtures per arm.

| Metric | Cooldown control | Mana100 v1 |
|---|---:|---:|
| Tournaments | 100 | 100 |
| Capped tournaments | 14 | 25 |
| Encounters | 18685 | 18955 |
| Encounter timeouts | 2552 | 2653 |
| Fixed formation timeouts / 576 | 24 | 39 |
| Overall timeout rate | 13.6580% | 13.9963% |
| Median accelerated tournament minutes | 31.255 | 31.743 |

The overall rate moves from 13.6580% to 13.9963%; caps move from 14 to 25. Fixed formation timeouts rise from 24 to 39. The mana arm is slower in 406/576 fixed pairs, faster in 165 and unchanged in 5; the winner changes in 137. These correlated development samples do not establish population-wide significance. Both variants fail the existing below-2% pacing screen.

| PvP creature observations | Control instances | Mana instances | Median first commitment, control → mana | Casts per instance, control → mana |
|---|---:|---:|---:|---:|
| Snapvine | 20919 | 21399 | 1.95s → 13.95s | 4.093 → 1.846 |
| Prism Organ | 1229 | 1276 | 1.50s → 14.55s | 3.936 → 1.690 |
| Reefglass | 37 | 44 | 2.55s → 12.55s | 2.730 → 1.318 |

First-commit medians include only creatures that cast. Instances are repeated deployments, not independent players or matches. Reefglass has only 37/44 PvP observations; use the fixed formations for its positional investigation instead of claiming a general balance conclusion.

In one-star fixed formations, protected → exposed first-commit medians in the mana arm are Snapvine 13.95 → 8.45 s, Prism Organ 14.55 → 8.75 s, and Reefglass 12.55 → 8.80 s. Thus exposure accelerates charging as intended, while protection can delay a defining ability. It does not follow that exposing a caster wins more often: survival and total casts also change.

## Verification and preserved failures

- Native combat suite: 22,320 assertions passed in `native-contract-final`, including mana spending, interruption, caps, shield interactions, death/reset, relic transformations and per-tick resource conservation. This final run includes the Unreal-safe shared test-helper name.
- Both native experiment runs compiled/exited successfully, with source hashes stable. The analysis reconciles 387,803 creature-activity rows across tournaments and the fixed mana formations.
- Authoring: 229 Python tests and all required validation/generation/staging checks passed using bundled Python 3.12 plus task-local jsonschema dependencies. The initial default Python lacked Pillow; bundled Python initially lacked jsonschema. Failed logs remain preserved; no user-global Python installation was changed.
- Native fixture failures preserved: duplicate generated-header include, premature stun observation while the enemy was recovering from a basic, and a shield fixture whose enemy retained a different in-range target. The corrected fixture constrains actual attack range and verifies real shield absorption. These are test-fixture corrections, not a concealed mana balance change.
- Preserved r7/r8 package checks:445 shared mana assertions passed inside packaged Unreal. Each archive completed10 control and10 mana tournaments. r7 reconciled with native results over856 rounds /3,745 encounters. Later display revisions do not alter shared simulation inputs.
- Corrected visual-test weakness: r7 used an owned preparation ID during combat and could validate a palette preview instead of the live creature. r8 selects the actual combat ID and checks its name, battle-state label and exact mana value; Prism's captured live value is20/100 at tick65. r7's original inspector test is not accepted as live-selection evidence.
- Presentation revision: r8 captures showed the small mana bar obscured by the nameplate, with the full inspector below the scroll fold. r9 moves the bar above the nameplate in camera space and adds numeric mana directly to that label. Full-roster crowded presentation/performance remains a later gate.
- Physical pointer testing was blocked by the Windows firewall permission dialog. No security action or firewall change was performed. Scripted same-handler exercises and engine-rendered captures are separate evidence; they do not certify physical input or human usability.
- The packaged Automation JSON and engine logs record the test pass. Unreal could not find its optional HTML report template; no HTML report is claimed.

## Final r9 package checkpoint

`builds/WonderChess-Mana-r9/Windows` is the final opt-in archive from this experiment. Unreal5.7.4 Development build/cook/stage/archive succeeded. Exact package verification passes across82 source files and49 payload files, with all56 frozen build inputs unchanged through execution. Inner executable SHA256: `5052d358b812528e21e6812e56064ba08521f433f458a94092a0c3228a7a8d70`. The package contains both activation variants; its manifest binds the base catalogue, while the mana process verifies the derived experiment identity `1446245d77df94c98eff3fe6b5d53d83629aa12b248dd1bbade05971c6099a1a`.

- Final packaged mana contracts:445 assertions passed.
- Final packaged/native reconciliation:10 control plus10 mana tournaments,856 rounds /3,745 encounters, with exact outcome/timing/survivor comparisons and no rejected commands. Full engine combat event streams and round hashes are not part of this comparison.
- Laboratory:41 Boolean checks pass at1280×720 and1920×1080; five newly rendered, state-stable captures per resolution. Both combat captures were visually inspected: mana numbers and blue bars are visible on the three converted heroes, while the controls have no mana label. The full inspector remains scrollable. These are proxy-art captures, not art acceptance.
- Solo:20 same-handler checks pass at1600×1000, including preparation disk resume, equipped relic resume, scouting rejection, combat cutoff, elimination spectating, tournament finish at45 rounds and fresh restart. Captain placement8 is preserved; a completed smoke tournament is not a win or pacing acceptance. It used the separate evidence slot `solo-r9-slot/preparation.wcsave`.
- Legacy native regression:10 tournaments /446,047 assertions passed. All229 Python tests and required authoring checks passed earlier against unchanged authoring/simulation inputs. Subsequent changes were limited to the laboratory exercise, mana presentation and launcher archive selection.

R9 was built and run on the development computer. An independent clean checkout for r9, independent clean-machine installation, full-content performance, physical input and human playtesting are not claimed. Earlier r5/r6 clean-checkout results remain historical.

From the implementation worktree, open the mana laboratory with:

```powershell
& .\tools\unreal\launch_milestones.ps1 -Mode Lab -ManaExperiment
```

Use `-Mode Solo -ManaExperiment` for the solo variant. For the exact same r9 executable with cooldown activation, omit the mana switch and explicitly pass `-Executable .\builds\WonderChess-Mana-r9\Windows\WonderChess.exe`. The launcher without either option continues to open r6. All changes remain local, uncommitted and unpublished.

## Next experiment to discuss

The next recommendation at this first checkpoint was **20 mana per landed basic attack**, holding the three-hero selection,100 maximum, zero start, incoming rule, damage, prices, targeting and the three control heroes fixed. The owner subsequently authorized it; the implemented r10 comparison and its measured limitations are in [MANA20_COMPARISON_2026_09_13.md](MANA20_COMPARISON_2026_09_13.md). No starting-mana change, healing change or skill-effect swap accompanied that comparison. Human normal-speed testing remains open.

## Evidence locations

- Detailed comparison: `reports/vnext/milestones/mana-20260913/comparison.json`.
- Control: `reports/vnext/milestones/b1-balance/mana-activation-control-20260913T061630085Z`.
- Mana: `reports/vnext/milestones/b1-balance/mana-activation-mana100-20260913T061630085Z`.
- Preserved sources, tests, build logs and package verification: `reports/vnext/milestones/mana-20260913/`.
