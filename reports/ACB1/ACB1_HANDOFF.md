# ACB1 — Ada closure and existing 24-hero game continuation

This handoff records the two authorized lanes independently. Ada is **PARKED_ART_REVISE**. The existing 24-hero game completed a normal-speed tournament, results and native restart; one reproduced default-launcher defect is **CLOSED_LOCAL_VERIFIED**. Native input was operated by the agent, with Solo Options pauses for planning. No beta, human playtest, listening or human art approval is issued by this report.

## Ada: PARKED_ART_REVISE

The r016 checkpoint and approved references were preserved. A separate evaluated sculpt target was created in the visible Blender session and edited with bounded local sculpt strokes. An initial construction and two corrective attempts were inspected using the saved cameras. The final correction removed most of a ridge introduced by the first correction and added modest nasal-base support, but did not adequately resolve the padded lower-lid/cheek, uneven medial socket, or nasal-base/philtrum-to-upper-lip shelf.

The target failed before cage reconstruction. The retained editable input cage is unchanged and explicitly labeled pending reconstruction. There was no target projection, new reconstructed facial topology, bilateral extension, contextual head validation, rigging, texture production, or engine integration. Existing in-game Ada remains the internal fallback. No hair-family objects were added to the active head scene.

- Work: `art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1/ada_closure_work.blend`.
- Frozen study: `art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1/ada_closure_checkpoint_ACB1_ART_REVISE.blend`.
- Frozen SHA256: `5deb2ead3d282a6ea0646452f2ee85a35506a5f4b1a1d275b8711623dbe96e2c`.
- [One-page art review](../../art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1/REVIEW.md), [matched primary-camera comparison](../../art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1/captures/comparison_primary_fit.png), [preservation review](../../art-source/asset-studio/wc_u_human_guardian/stages/head-closure/ACB1/reviews/preservation_review.md).

Actual saved evidence includes matched clay front/profile/both three-quarter/primary/reversed-key/openings/underside captures for the baseline and three target states, plus actual input-cage views and labeled comparison sheets. The cage views are not represented as newly reconstructed topology. The evaluated target retained its intended openings and reports no degenerate faces or nonadjacent surface overlaps. The unchanged unsubdivided input cage retains five raw-cage overlap pairs; structural observations are not artistic approval.

The next art intervention should replace the padded socket/cheek and nasal-base-to-lip relationships in one small editable sculpt target. An experienced character sculptor is recommended for that focused intervention before another retopology attempt. This is not authorization to hire, upload art, purchase an asset, or continue the failed bounded method.

## Current game identity

The retained package is `builds/WonderChess-Update24-Checkpoint-r4/Windows/WonderChess.exe`; its whole payload, current canonical inputs and installed-engine receipt were reconciled in [read_only_reconciliation.md](read_only_reconciliation.md). All 31 recorded payload files matched, totaling 604,245,301 bytes. The inner Shipping executable SHA256 is `67b00eeca8f60f6f8bc62df95fb833f1174f3a3c086ef9c452b39ea0262af0f0`.

Current checkout HEAD is `9623fd82f98ff80a90985b9f552d8851ccece30f`; the retained r4 package source checkpoint was committed as `7f50c6c`. The package records Unreal 5.7.4, profile `alpha_24`, balance `alpha_24_v0.4.1`, schema 3.1.0, protocol 6, catalog digest `95509d001ca0e6c55fa64a616df6e2e9a01a3809a9b9c82d9bd0a725dad3a1ec`. The dirty local AQ1 presentation edits and earlier art/tool work were retained. The running r4 binary was not described as containing those later source edits or the head study.

The available PC is a Lenovo 82RG with Ryzen 7 6800H, approximately 16 GB installed memory and RTX 3060 Laptop GPU. The run used 1920×1080, 100% screen scale, TAA and a 60 FPS cap. [Hardware observations](20260909-native-r4/hardware.json) include drivers and Balanced power plan; thermal state was not measured. Blender remained open but idle. No renderer or compiler was run concurrently with the performance capture.

## Closed reproducible issue

**ACB1-GAME-001 — obsolete default package selection: CLOSED_LOCAL_VERIFIED.** Running `tools/unreal/launch_alpha.ps1` without `-Executable` selected the historical `WonderChess-Alpha-Candidate`, even though the current delivery is the 24-hero r4 checkpoint. This risks testing and distributing the wrong roster/build. The fix changes only the default path; explicit package overrides and flags are retained.

The focused launch-resolution test reproduced three failed identity checks on the original launcher and passed all four after the change, including execution from a different working directory. Exact original/fixed launcher bytes and results are retained in `20260909-default-launcher/baseline/` and `fixed/`.

The repaired default was then actually invoked **without `-Executable`**. PID 32260 ran the r4 inner Shipping executable with the exact hash above, normal speed 1 and no `WCExercise`. Its native menu was inspected, followed by the gallery, return to title and native Quit. The [native launch record](20260909-default-launcher/native-launch.json) contains the invocation, process command line and hash; [capture 30](20260909-native-r4/captures/30_default_launch_menu.png) shows the actual menu. Both game PIDs were confirmed absent after native Quit. This closes local default-path launch behavior, not clean-machine distribution or beta acceptance.

No runtime C++ or cooked asset was changed for this fix, so a new Unreal package is not required. The old package directories remain intact.

## Native game audit

[Interaction journal](20260909-native-r4/interaction_journal.md) separates actual agent input, acknowledgements, preparation pauses and limits. The first run used PID 36432, seed 846842640, one interactive seat and seven bots, normal simulation speed, no scripted game command injection. Native captures, engine snapshots, replies and frame records are in `20260909-native-r4/`.

Observed: standalone launch/settings/solo entry; reduced-motion persistence and restoration; purchases; native select/place; five deployed heroes and two active traits; three-copy Liora upgrade; shop lock; scouting and home return; player elimination in round 13; continued bot spectating; PvE recap; and actual ghost encounters. Early failed placement attempts were affected by short preparation deadlines and agent turnaround; later native placement worked, so a reproducible selection defect was not established. The weak early player formation makes this run unsuitable for balance or newcomer-difficulty conclusions.

The first tournament completed at **round 38**, with Highbanner first at 4 HP and the player eighth. [Capture 26](20260909-native-r4/captures/26_results_screen.png) shows actual final standings. First finished-state observation was **1,804.716 wall seconds** after the namespace began, approximately 30 minutes 5 seconds, including unidentified Options pauses; this is not measured active simulation or uninterrupted human-match duration. The agent selected **New tournament**, and the fresh namespace 2 used authority seed **2061823456**, round 1, eight positive-health seats, zero placements, player 10 gold / level 3 / XP 0 / empty roster. Native purchase of Rok cost one gold; native Sell returned the player to 10 gold and an empty bench. That restarted match reached round 2 and was then quit normally. Captures [28](20260909-native-r4/captures/28_restart_round_one.png) and [29](20260909-native-r4/captures/29_native_sell.png) complement the authoritative reset and reply records.

The repaired default launch also received native gallery inspection of all **24 grid cards and portraits** across four rows, recorded in [31](20260909-native-r4/captures/31_gallery_top.png), [33](20260909-native-r4/captures/33_gallery_row_two.png), [34](20260909-native-r4/captures/34_gallery_row_three.jpg), and [35](20260909-native-r4/captures/35_gallery_final_row.jpg). No detail hero was selected. This is card-display coverage only: 72 star-stat combinations, complete skill text, individual 3D models and continuous animation/contact remain unreviewed in this run.

Feature-to-evidence inventory (bounded observations do not approve untested subfeatures):

| System | Current classification | Evidence / remaining scope |
|---|---|---|
| Launch/menu/settings | Verified this run, bounded | Actual launch, menu, Solo, reduced-motion save/readback/restoration; clean-machine prerequisites not tested |
| Hero gallery | Verified this run, bounded card display | All 24 grid cards/portraits inspected in four rows; detail views, 72 star-stat combinations and continuous 3D motion not tested |
| Shopping/bench | Verified this run, bounded | Buy, acknowledged three-copy merge, lock, and restart buy/sell returning 10 gold / empty bench; reroll/full-bench merge/rejected-input breadth remains open |
| Formation | Verified this run, bounded | Native select/place, five-unit capacity display, scouting/home; swap/drag/max-capacity rejection not established |
| Traits | Verified this run, bounded | Distinct Guardian 2 and Ranger 2 displayed on five-hero formation; every tier/tooltips/snapshot combination not tested |
| Combat | Verified this run, bounded | Actual visible and off-screen encounter records, PvP/PvE/ghosts; full skill/movement/interruption coverage not claimed |
| Tournament | Verified this run, one complete seeded tournament | Round 1 through round 38 final standings, player elimination and continued bot settlement/spectating; all survivor-count and settlement fixtures not rerun |
| Player journey | Verified this run, bounded native lifecycle | Agent-controlled start/purchases/formation/elimination/spectating/results/New tournament/buy/sell/Quit; no unassisted human/newcomer claim |
| Networking | Blocked for physical gate; historical report only for loopback | User has one PC; no actual physical 2H6B or remote 8H0B in this run |
| Assets/audio | Sampled display observed; audio listening NOT_RUN | Sampled native images are not continuous motion/contact or audible review; art-major defects stay open |
| Performance | Completed recorded-sample analysis, no beta performance approval | 119,892 recorded frames across three namespaces, including 106,155 from the completed tournament; all recorded spikes retained, unidentified Options pauses and writer omissions disclosed |

The [current encounter review](20260909-native-r4/current_encounter_review.md) binds a fixed prefix of this run through round 20: 104 settled outcomes, including nine PvP timeouts. Its round-14 Starwatch/Sunstride trace reconciles 233 distinct action events to final HP-loss/absorption totals. Damage continued at ticks 792 and 795 before the configured tick-800 cutoff; no healing was recorded. This supports an active fight reaching the limit, not a frozen final standoff. The separate Highbanner/Hearthkeeper fight finished at tick 422 and did not time out. The partial event review is not a final tournament count or a balance recommendation.

## Post-run performance, validation and preservation

[Final analysis](20260909-native-r4/run_analysis.md) is **COMPLETE_READ**, with zero parse errors or inputs changing during read. It includes all 119,892 recorded frame samples: namespace 0 has 9,407, the completed namespace 1 has 106,155, and the partial restarted namespace 2 has 4,330. An exact repeated namespace-0 CSV header is recorded as a structural diagnostic, not a frame. The initial analysis and identical spike data were preserved before this parser correction.

| Completed tournament subset | Samples | Frame p95 ms | Frame p99 ms | Maximum ms | >50 ms | >100 ms |
|---|---:|---:|---:|---:|---:|---:|
| All recorded namespace 1 | 106,155 | 16.667 | 16.754 | 185.648 | 311 | 196 |
| Recorded combat | 70,551 | 16.667 | 16.756 | 167.337 | 186 | 139 |
| Recorded settlement | 8,276 | 16.667 | 36.312 | 185.648 | 81 | 37 |
| At least 12 visible units in combat | 5,654 | 16.672 | 17.228 | 155.405 | 51 | 44 |

These are frame intervals under the named 1080p/60 FPS configuration. CPU, render-thread and available GPU timings are separate fields in the full analysis. No spike is removed as an outlier. Solo Options pauses are not explicitly marked by the source writer and remain in these subsets. The writer also omits the first five seconds of each namespace and stops profiling after completion/abort; later analysis cannot recover those frames. Namespace 0 is reused on return to the frontend, so its clocks/latest session summary must not be treated as one uninterrupted match. The recorded hitch tail and incomplete active-play separation remain investigation work. One paused agent session and one laptop do not pass the proposed three-tournament/multiple-machine beta performance gate.

[Repository validation](20260909-validation/validation.json) records exact commands, logs, timestamps and exit codes: **400** specification/data checks, **154** Python unit tests, **28** generated documents and **6** catalog artifacts all passed. The scoped diff check passed. The separate focused launcher test passed **4/4**. No game recompile or new package was needed for a default-path-only fix, and these repository checks do not establish gameplay or visual quality.

The existing GameUserSettings file ended with the exact original SHA256 `9223aae0895632fb0a3f081f6697b8f3e59ff56cdcff2fe0f1fa8ae31c07dfd9`; no filesystem restoration was needed. Existing profile values and ShowcaseHero were preserved. Old packages, the r016 checkpoint, approved references, failed art experiments and unrelated dirty work remain retained. The [final post-exit preservation record](final_preservation.json) rechecked all 31 package files, the profile, frozen r016, frozen ACB1 and its work file. Current task status is recorded in [implementation_state.json](../implementation_state.json).

## Listening handoff — NOT_RUN

No listening answer or direct audible inspection was received. Music-component state, rendered frames and synthesized/recorded audio files are not a listening pass. For the next actual listening session, use the verified [r4 launcher](../../builds/WonderChess-Update24-Checkpoint-r4/Windows/WonderChess.exe), or from the Wonder Chess repository run:

```powershell
& './tools/unreal/launch_alpha.ps1' -Mode Play
```

Observe title/menu music and button feedback; then Play > Solo and listen to purchases, attacks, ability releases/impacts, shields/heals/stuns, round transitions, elimination and results. In Options, test master/music/effects sliders and inspect the reduced-motion setting while preserving the original values afterward. Record missing sounds, clipping, excessive overlap, timing mismatch or fatigue with the round, hero/action and actual volume/settings values. Include actual output device and whether the review was performed by Pram or another listener. Audio remains **NOT_RUN** until that observation exists.

## Remaining priorities and prerequisites

This queue distinguishes reproduced defects from unverified gates. Open beta-critical gaps do not become passes because the launcher is fixed.

| Priority | Severity / status | Owner | Reproduction or prerequisite |
|---:|---|---|---|
| 1 | S1 wrong-build launch, CLOSED_LOCAL_VERIFIED | Tooling | Original default selected old package; focused regression and actual no-override r4 launch/menu now pass |
| 2 | S0 if reproduced; economy/selection breadth still open | Runtime + interactive reviewer | Basic native buy/sell/place/merge now observed; reroll/drag/swap/capacity, full-bench merge and rejected near-deadline actions still need matching replies |
| 3 | S1 investigation; timeout cause unresolved | Simulation | Replay current or historical named PvP/ghost timeouts with target/path/idle/effective damage/heal/shield traces before balance edits |
| 4 | S1 beta gate blocked by hardware | Network + two operators | Two physical Windows PCs with matching whole packages; actual 2H6B at 1x, then paired evidence audit |
| 5 | S0/S1 recovery implementation gap | Network + product | Specify authenticated seat reservation/reclaim and exactly one controller; current source rejects in-match joins and uses bot takeover |
| 6 | S1 eight-human implementation gap | Network + build | Current two-human cap, host lifecycle and missing dedicated-server target need a bounded implementation plan and tests; do not merely raise a limit |
| 7 | S1 if significant; representative performance breadth open | Runtime + performance reviewer | Three normal-speed tournaments, busy encounters, all-gallery and transitions on declared machine classes; no concurrent render/build load |
| 8 | S1 if blocking; audio and continuous asset review open | Audio/art reviewer | Actual listening and per-hero/neutral continuous motion/contact/VFX review at gameplay and gallery sizes |
| 9 | S1 if misleading; bot opportunity diagnosis open | Simulation/bots | Record offer/affordability/candidate/bench-to-field denominators before interpreting Neris/Dagna usage or changing stats |
| 10 | S1 beta content gate; Ada ART_REVISE | Character modeler + user | Focused successful sculpt intervention, reconstruction and user development-use review; keep existing runtime fallback |

Next three executable tasks after this closure:

1. **Targeted timeout and interaction diagnosis.** Use the matching source/catalog and retained named encounters. Add only the missing telemetry needed to distinguish path stalls, target acquisition, shield/heal equilibrium and insufficient damage; include native transaction edge cases in a fresh isolated evidence run. Preserve balance until a cause is reproduced.
2. **Physical 2H6B.** Obtain a second actual Windows PC and operator. Use the existing `docs/current/PHYSICAL_LAN_WC_U460.md` and `tests/runtime/run_physical_lan.ps1`, identical r4 payload/provenance, the host's observed private IPv4, fresh directories and `-InputMode manual -SimulationSpeed 1 -Launch -Visible`. Record both independent devices and complete match evidence. Same-PC loopback cannot satisfy this task.
3. **Remote 4H4B → 8H0B and recovery.** Record the hosting/build/distribution choice and authenticated seat-identity/grace/handover contract first. Implement the currently absent multi-human admission/reclaim path with exactly-once authority fixtures, then test independent devices with impairment and private-state checks. No public deployment, paid service, account creation or engine upgrade is authorized by this handoff.

The user has confirmed only this PC is available. Physical networking remains blocked; audio listening remains unverified without direct listening evidence. Proposed ACB1 beta gates and historical regression reports are not current release results.
