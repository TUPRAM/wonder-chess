# 20 versus 10 mana per basic hit — 13 September 2026

The owner authorized the proposed comparison: change basic-hit mana from10 to20 for Snapvine, Prism Organ and Reefglass, while retaining100 maximum mana, zero start, the incoming-damage rule, ability effects, prices, targeting and the three control heroes.

**Recommendation: prefer20 for the next human mana playtest, while keeping it opt-in.** It improves casting frequency and several pacing measures relative to10, but it does not pass the pacing screen. The protected/exposed first-cast difference also becomes smaller for Snapvine and disappears at the median for Prism Organ and Reefglass in the one-star fixed formations. Thus the experiment supports more reliable attack-driven casting; it only partly preserves the original charging tradeoff. No human enjoyment or balance acceptance has occurred.

## Protected inputs and implementation

`data/vnext/catalog.json` gains only `experiments.mana100_hit20_v1`. Removing that new recipe reproduces every original parsed catalogue value, including the prior10-mana recipe. The recipes differ only in `basicAttackGain`:1000 versus2000 centimana. `protected-catalogue-parity.json` and the preserved12-file `source-before.zip` record this boundary.

The canonical generator emits `WonderVNextMana20Catalog()` alongside the original cooldown and10-mana variants. No shared combat-resolution code changes in this batch. Both experiment profiles have distinct version/digest identities. The20-mana package flag is `-WCMana20Experiment`; its default preparation save is `WonderVNext/Solo/mana20-preparation.wcsave`. The new launcher switch is `-Mana20Experiment`. Supplying both experiment switches is rejected before launching.

All other rules remain as in the [first experiment](MANA_EXPERIMENT_2026_09_13.md): actual post-mitigation HP-loss charging;20 incoming mana per event and40 per one-second accounting window; no incoming mana from absorbed shield damage; no outgoing mana from spells; valid targeting before spending; no refund on interruption; charging paused until cast recovery; fresh mana each encounter. Relics retain their existing inverse timing-to-gain transform, with unchanged damage modifiers and incoming caps. Consequently Quick Wick scales a basic from20 to25 mana in this variant, while retaining its existing impact tradeoff.

## Comparison and provenance

Both fresh arms ran100 tournaments with development seeds1–100,576 fixed mana encounters per arm (three focal heroes, protected/exposed placement, three stars, two orientations and16 seeds1001–1016), and the existing192 formation fixtures per arm. Fixed encounters use actual combat and deterministic replay checks. Their inputs are identical across activation rates; army costs differ between focal heroes, so these fixtures do not rank heroes by equal-cost strength.

The10-mana rerun exactly reproduces the earlier recorded CSV rows:100 tournaments,18,955 encounters,576 fixed formations,3,456 fixed activity rows and192,075 tournament activity rows. Both fresh runs report stable source hashes and zero execution failures. The analysis reconciles390,330 activity records for resource conservation. Reserved confirmation seeds900001–900250 remain unused.

| Measurement | 10 mana per hit | 20 mana per hit |
|---|---:|---:|
| Tournaments |100|100|
| Capped tournaments |25|14|
| Encounters |18,955|18,888|
| Encounter timeouts |2,653|2,625|
| Overall timeout rate |13.9963%|13.8977%|
| PvP timeout rate |23.1651%|22.7022%|
| Ghost timeouts / encounters |248 /689|281 /720|
| Neutral timeouts / encounters |0 /7,884|0 /7,843|
| Fixed formation timeouts /576 |39|24|
| Median accelerated simulated minutes |31.7433|31.7188|

Of576 fixed pairs,20-mana fights are shorter in407, longer in118 and unchanged in51; the winner changes in89. These correlated development observations do not establish population-wide significance. The small change in median simulated tournament duration is not a human pacing measurement. Ghost timeouts worsen even as PvP timeouts improve, so the result is not uniformly better across encounter kinds.

Both arms fail the existing below-2% timeout screen. For historical context, the cooldown control on the same100 seeds had14 caps,13.6580% timeouts and24 fixed-formation timeouts. The20-mana candidate recovers the previous cap/fixed-timeout counts without demonstrating superior overall pacing to cooldown activation. That cooldown arm is historical context, not a new third experiment in this batch.

## Casting frequency and formation tradeoff

| One-star fixed first-cast median | Protected,10 | Exposed,10 | Protected,20 | Exposed,20 |
|---|---:|---:|---:|---:|
| Snapvine |13.95s|8.45s|7.95s|6.05s|
| Prism Organ |14.55s|8.75s|7.30s|7.30s|
| Reefglass |12.55s|8.80s|6.30s|6.30s|

Each entry covers32 fixed observations; first-cast medians include only creatures that cast. All focal heroes cast at least once in these one-star groups. Equal medians do not mean every individual seed has equal timing.

| One-star fixed casts per creature | Protected,10 →20 | Exposed,10 →20 |
|---|---:|---:|
| Snapvine |2.563 →3.719|1.313 →1.406|
| Prism Organ |2.469 →3.344|1.281 →1.750|
| Reefglass |1.438 →1.781|1.625 →2.094|

For Snapvine, the median exposure advantage shrinks from5.50 to1.90 seconds. For Prism Organ and Reefglass, its median first-cast advantage disappears in these fixtures. Survival, geometry and subsequent casting can still make formation matter. This is insufficient evidence to claim that the original protection-versus-charge decision remains equally strong for all three heroes.

PvP casts per deployed creature also increase: Snapvine1.846 →2.825, Prism Organ1.690 →2.941, Reefglass1.318 →2.483. These are repeated deployments with compositions that can diverge after battle outcomes. Reefglass has only44 observations in the10-mana arm and29 in the20-mana arm, so its tournament estimates are especially limited; use its fixed formations for the more controlled comparison.

## Executed technical verification

- All230 Python tests and required authoring/generation/staging checks pass. The targeted catalogue suite also checks that changes to starting mana, incoming caps/gain or the proposed hit rate are rejected by the comparison contract.
- Native combat:22,456 assertions pass. The shared mana suite includes581 assertions, including an actual four-hit80-mana/five-hit100-mana/cast fixture and preservation of the other resource rules, hero stats, costs, effects and targeting.
- Unreal5.7.4 Development build/cook/stage/archive succeeds using the installed MSVC14.44 and Windows SDK10.0.22621 toolchain. No toolchain upgrade occurred.
- Packaged Unreal executes all581 shared mana assertions successfully. The Automation JSON and engine log are the evidence; the optional HTML report template is unavailable.
- Ten packaged tournaments per activation rate reconcile with native results:10-mana429 rounds /1,893 encounters;20-mana433 rounds /1,897 encounters. Total862 rounds /3,790 encounters. Every encounter kind, winner, timeout, tick count and survivor count matches, as do tournament counts, cap flags and simulated time. No commands were rejected. Full engine combat-event streams and round hashes are outside this comparison.
- The20-mana laboratory passes41 Boolean checks at1280×720 and1920×1080, with five saved, state-stable rendered captures per resolution. Both combat captures were visually inspected. At tick65, the selected live Prism has40/100 mana and its inspector reports20 per basic hit; the variant label identifies20/HIT. Controls have no mana labels.
- Solo at1600×1000 passes20 same-handler checks, including exact preparation/equipped-relic disk resume, scouting rejection, phase cutoff, elimination spectating, finish at45 rounds and fresh restart. Captain placement8 is retained. The test uses `solo-slot/preparation.wcsave` under the evidence directory; it is an accelerated smoke, not normal-speed human acceptance.
- Exact package identity passes for82 source files and49 payload files. All56 frozen build inputs remain unchanged through execution.

Physical input was attempted by inspecting the actual r10 window and was blocked by its Windows firewall permission dialog. No pointer/keyboard action, permission decision or firewall change was performed. Human participants, r10 independent clean-checkout build, independent clean-machine installation and final-content performance are NOT_RUN. Art, remote and release acceptance remain open.

## Package and next action

Candidate: `builds/WonderChess-Mana20-r10/Windows/WonderChess.exe`.

Inner executable SHA256: `1538f04fda10eb084a02614597325f7173ce6b55f38f0058109d2eb25bdfca80`.

20-mana profile digest: `da01ba8705ed8c7ec4507584f5240e5e4debb17bd123f3741ea534a96a17f5c5`.

From the implementation worktree:

```powershell
& .\tools\unreal\launch_milestones.ps1 -Mode Lab -Mana20Experiment
```

Use `-Mode Solo -Mana20Experiment` for the solo variant. To compare10 mana in the exact same r10 package:

```powershell
& .\tools\unreal\launch_milestones.ps1 -Mode Lab -ManaExperiment -Executable .\builds\WonderChess-Mana20-r10\Windows\WonderChess.exe
```

The default launcher still opens r6, and the original `-ManaExperiment` default still opens preserved r9. Earlier archives, data and reports remain intact. Changes are local, uncommitted and unpublished.

Next, complete physical input after the operator handles the security prompt and use matched normal-speed10/20 fixtures in the planned B1 study. Ask participants to predict casting order, observe before receiving recap explanations, revise a formation independently and explain the cost of exposing each caster. Record whether they notice charging, whether protection still creates a useful choice, whether spells feel too scarce/frequent, and voluntary replay. Keep assistance and losses in the record. Do not infer enjoyment from this bot comparison.

Stop promotion on failed invariants, data/control drift, unresolved input errors or failure of the pacing gate. Do not expand mana to more heroes or swap effects on the strength of this result alone. No third tuning arm has been implemented. The broader B1/B2 human study and B0–M7 acceptance queue remain in [MILESTONE_STATUS.md](MILESTONE_STATUS.md).

Raw evidence: `reports/vnext/milestones/mana20-20260913/verification.json`, `comparison.json`, `mana10-reproduction.json`, `engine-native-reconciliation.json`, package manifest, logs and captures. Native runs: `reports/vnext/milestones/b1-balance/mana20-comparison-mana100-20260913T071628779Z` and `mana20-comparison-mana20-20260913T071628802Z`.
