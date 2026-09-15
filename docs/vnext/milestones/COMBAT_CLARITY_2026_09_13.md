# Combat clarity and independent engagement — 13 September 2026

The owner reported that the demo looked as if creatures waited for one another, then authorized attack/skill visualization, nearest-enemy targeting and a recovery investigation. This is owner developmental feedback, not external study or visual release acceptance.

## Candidate contract

The packaged **r13 candidate** provides cosmetic feedback in both the laboratory and solo frontend. Ordinary swings and projectiles overlap independently. Selected creatures show their current target and state; labels identify melee versus ranged. Movement is interpolated along the actual reserved cell path. Presentation never submits combat commands or applies effects. The original owned proxy surface and a new unlit cue material are cooked into this package; exposure is fixed and unit labels remain stable through actions.

Each of the six implemented successor heroes has a distinct signature: Bellback gold protection arc and supported-ally link on actual prevention; Cragstoat amber charge aim and charge movement trail; Root green, board-clipped healing boundary, source pulse and effective-heal pluses; Snapvine pink aim/lash; Prism violet committed row/column markings and beam impacts; Reefglass cyan lane, wave and actual push trail. General effects include impact marks, persistent shield outlines, a head-top stun spiral with orbiting stars, and temporary modifier chevrons. Health and mana retain their authoritative source. Ordinary movement has a separate thin trail and is not labeled a charge. Selected-target rings are cream, distinct from blue active shields.

The optional **Status effect test** uses an explicitly synthetic temporary catalogue to execute real damage/heal/shield/stun/slow effects. It does not add stun or other skills to Bellback or Cragstoat. Reset restores the user's real formation. Status visuals expire from combat state; healing numbers show effective healing, not requested amounts.

The optional **combat_clarity_v1** rules are based on the existing20-mana recipe. Acquire the closest reachable enemy by board distance, with path distance and seeded initiative resolving ties. Keep a living enemy already in attack range; reacquire when out of range or unreachable. Committed swings/casts retain their original lock and interruption rules. Movement may proceed during basic recovery, but a separate readiness deadline prevents movement from allowing extra attacks or early casts. Cast recovery and stun still block actions. The original mana20/cooldown/legacy rule paths remain available.

The canonical recipe is separate from earlier experiments. Removing the new `combat_clarity` source object reproduces every previous parsed catalogue value. Unit stats, prices, ability effects and mana values are preserved. The new rules use a distinct digest, balance version and preparation save path.

## Bounded behavior comparison

Twenty development tournaments per arm, seeds1–20, plus576 fixed mana formations and192 additional fixtures per arm. Every fixed encounter uses replay checks. Reserved holdout seeds remain unused.

| Arm | Timeouts / encounters | Overall timeouts | Capped tournaments |
|---|---:|---:|---:|
| Original20 mana |562 /3776|14.883%|4 /20|
| Nearest-target change only |474 /3902|12.148%|8 /20|
| Nearest target + moving recovery |422 /3898|10.826%|10 /20|

The original20-mana arm exactly reproduces prior tournament/encounter rows for these20 seeds, all576 fixed formation rows,3456 fixed activity rows and192 supplementary fixture rows. This supports preservation of the control's outcomes after the presentation changes. The new rules reduce encounter timeouts but worsen tournament caps in this small development sample. They remain an opt-in playtest candidate and do not pass the pacing gate. No enjoyment or balance promotion follows from these results.

## Verification status

The [final verification inventory](../../../reports/vnext/milestones/combat-clarity-20260913/verification.json) records:

- 230 Python tests and required authoring/generation/staging checks passed. The later package-manifest adjustment separately passed its 10 targeted tests.
- Native combat passed 25,385 assertions. Final r13 packaged automation passed both suites: 2,929 combat-clarity and 581 mana assertions, with zero failed tests.
- Five final r13 engine tournaments reconcile with native results across 222 rounds, 981 encounters and 4,905 result-field comparisons, with zero mismatches. This is result-field reconciliation, not a cross-binary full event-stream claim.
- Final r13 laboratory exercises passed 41 Boolean checks at each of 1280×720 and 1920×1080, including deterministic replay and input projection. The separate status fixture passed all 12 Boolean checks, including actual status geometry appearing and expiring.
- Final r13 solo exercise passed all 20 Boolean checks at 1600×1000, including durable resume, relic persistence, phase cutoff, elimination, a 45-round finish and restart. These are accelerated same-handler checks, not physical pointer/keyboard journeys or human pacing measurements.
- All 61 recorded build inputs remained unchanged through final verification. Exact package identity passed for 86 source files and 49 payload files.
- Both lab resolutions rendered the six hero signatures listed in the cue telemetry with no cue pool overflow; peak use was 180 mesh cues and 3 text cues. The status fixture peaked at 113 mesh cues and 1 text cue. This does not establish final-content frame performance.
- Actual saved 720p/1080p combat and status-active/status-expired images were inspected. Charge aim and tidal wave rendered, but the specific charge-displacement trail and push-displacement trail were not exercised by the final mirrored lab fixture; their rendered end-to-end inspection remains open.
- The normal r13 review launcher executed. Before any final r13 physical input check, Computer Use reported that the owner stopped it with Escape. No further Computer Use actions were issued; manual input remains NOT_COMPLETED.

Failed attempts and corrections are preserved. The first Python invocation lacked jsonschema; the successful rerun used the installed Unreal Python environment. The first package attempt exposed an Unreal macro collision in a shared helper and an automation-flag API mismatch; both were corrected. An r11 automated lab stage collided with the synthetic status stage, so that run is not counted as a full lab pass. r12 corrected that collision and packaged cue materials. r13 fixes exposure, unstable action labels and Root's displayed range boundary. Finally, the external graphics summary parser initially treated the flat solo Boolean report as a missing nested pass flag. Its original summary is preserved; the corrected summary was reconciled against the raw, already-passing solo report without claiming another game run.

## Review workflow

### Windows File Explorer path correction

The shortened `C:\Users\iputu\AppData\Local\CodexWorktrees\wc\m7` path is redirected inside the Codex app and was reported unavailable by the owner's File Explorer. The actual verified storage path is `C:\Users\iputu\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\CodexWorktrees\wc\m7`. Both resolve to the same files inside Codex; the original user-facing path instruction was incorrect outside the app.

User launchers in `C:\Users\iputu\Documents\Project Support\Wonder Chess` now address the actual script path: `Play Combat Clarity - Lab.cmd` and `Play Combat Clarity - Solo.cmd`. They use the existing r13 launch script and do not copy, move or alter the game package. Use these from File Explorer. Historical abbreviated paths elsewhere in the records remain Codex-context paths.


Open `Launch Combat Clarity.cmd` in the m7 worktree, or run `tools/unreal/launch_milestones.ps1 -Mode Lab -CombatClarity`. For the visuals-only control, use `-Mode Lab -Mana20Experiment -Executable builds/WonderChess-CombatClarity-r13/Windows/WonderChess.exe`. Solo supports the same candidate via `-Mode Solo -CombatClarity` and has its own default preparation save.

Watch normal speed, select a creature to inspect its target/state, then change one placement and replay. Judge which attack/skill was understandable and what remains confusing. Use Status effect test to inspect stun/shield/heal/slow without confusing those effects with the actual roster. These effects are prototype combat communication, not accepted final art, animation, VFX or audio. External human studies, final-content performance, remote-device and release gates remain open.

Next work: complete actual r13 input and charge/push visual inspection; compare normal-speed readability using the unchanged20-mana control and the optional targeting/recovery variant; then investigate the increased tournament caps before any promotion. B1/B2 remain the engineering checkpoint. B3/M2 forms and final animation production, M3 pacing, and later ecosystem/remote/release acceptance remain open. All changes and candidates remain local, uncommitted and unpublished.

Launcher follow-up: the first Windows PowerShell wrapper launch started the game but failed on `Get-FileHash` while writing evidence. The script now hashes through .NET before launching. The corrected Lab wrapper ran successfully with a matching executable hash and `WC_VNEXT_LAB_READY`; package identity remains PASS86/49. The Solo wrapper target was verified but was not executed during this follow-up. See `reports/vnext/milestones/combat-clarity-20260913/launcher-path-fix.json`.

## Owner review and proposed next batches

On 13 September the owner reported: "It looks good to me, what should we do next?" This records positive review of the prototype combat-presentation direction. The owner did not specify every effect observed or a complete solo journey; do not convert this feedback into those missing measurements or final art approval.

1. B1/M3 pacing: compare the existing original20-mana and clarity tournament traces, account for round counts, survivor composition, effective sustain and player damage/elimination, and reproduce a concrete cap cause before changing one rule. Validate unchanged control outcomes, deterministic replay and full tournament endpoints; reject any candidate that improves fight timeouts by worsening caps or removing formation choice. Existing declared pacing gates still apply.
2. B2/M1 solo usability: complete a normal-speed owner journey covering recruitment, three-copy upgrade, facing, scouting, relics, save/resume, elimination and results. Specifically inspect actual Cragstoat charge and Reefglass displacement. Fix observed defects, then obtain a current clean-checkout study build and conduct the already planned external first-use studies. Do not treat one owner session as external study completion.
3. B3/M2 art slice: change Bellback's failed modeling method using the already approved r004 reference. Obtain modeled-form approval, then proceed through the existing topology/material/rig/motion/export/Unreal gates and review it in actual combat. Preserve the six-hero control while preparing the other named pilots. Use demonstrated gaps to choose subsequent hero/ability or trait experiments.
