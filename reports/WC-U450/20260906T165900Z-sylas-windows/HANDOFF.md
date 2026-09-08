# Generic alternating Attack windows checkpoint

Status at latest source freeze: IMPLEMENTED; native focused execution and before/after 100-tournament comparison passed. The first combined Unreal compile failed on one local variable shadow; that correction is saved for the next build. Actual unmarked import retry passed; marked import/cook and viewport verification remain pending root. No Unreal binaries were written by this lane. Root owns protocol6 canonical/source migration, builds and all imports. Source authors own the five required hero revisions: Sylas, Rok, Kesh, Nella and Iri.

Source changes

- CombatUnit.basicAttackOrdinal starts0 and increments exactly once next to existing basic actionId assignment. It is never read by combat decisions, scheduling, effects, packets, RNG or economy. WCMatchRuntime publishes additive public basicAttackOrdinal. Root adopted protocol6 to reject older clients.
- Presentation/WCAttackWindow.h contains pure window validation, ordinal selection, bounded sampling and reconstruction clock. Each window release is validated against the caller's canonical windup. A zero ordinal produces no attack. One missing-snapshot interpolation tick is allowed; elapsed is corrected by the next real snapshot.
- WCAttackPresentation.h/.cpp reads six cooked sync markers generically. Unknown/duplicate/partial/out-of-range windows reject. No hero IDs or250ms constants are embedded in runtime validation.
- WCBoardPresenter reads the authoritative ordinal, keeps the same window across Windup/Recovery, stops the single-node player and samples only that window before skeletal pose evaluation. It adds the presenter tick prerequisite for marked clips. Other clips and unmarked heroes retain normal playback. Reconstructing for round, observed seat or match namespace resets local clocks while the snapshot ordinal preserves correct hand selection. No animation notify drives gameplay.
- Optional -WCWindowAudit writes actual action, ordinal, selected window, snapshot/release tick, elapsed/asset sample and window landmark values at commitment/reconstruction or release crossing. It requests no screenshots and creates no combat events.
- WCImportedAssetTests validates imported window presence/times against the actual source export manifest when available, uses the full authored sequence extent, and samples both windows' start/release/end. Existing7-clip and rig/material/root contracts remain.
- New WonderChess.Presentation.AttackWindowMetadata engine fixture checks absent/malformed/duplicate/unknown marker handling and bounded release sampling. This is a unit fixture, not a real imported-asset or visual claim.
- The profiler conflict-list typo is corrected from WCAnimationReview to the actual WCReviewMotion flag.

Source/export contract

Existing clips.Attack gains optional presentation_windows with exactly two ordered objects:
[{"name":"R","start_frame":1,"release_frame":16,"end_frame":40},
 {"name":"L","start_frame":40,"release_frame":55,"end_frame":79}]

Those numbers are Sylas/Iri's250ms example only. Each hero's actual windup/fps must derive its own releases and lengths. Source windows are contiguous and cover frames[1,end], with a shared neutral boundary. Legacy release_frame remains the first window's release. Required7 clips and exact Attack asset IDs stay unchanged.

Importer and actual failure retained

- tools/unreal/attack_window_contract.py validates manifest shape, integer frame bounds, both complete cycles, both canonical release offsets and actual imported marker/duration readback.
- import_alpha_assets.py validates the plan before selected-hero mutations; installs WC_Attack_R_Start/Release/End and WC_Attack_L_Start/Release/End on owned track WC_Attack_Windows; removes only stale owned marker names; preserves unrelated sync markers; saves the same sequence and records readback.
- Initial actual Neris/Tala import FAILED because the C++ UAnimationBlueprintLibrary class is exposed to Python as AnimationLibrary, not AnimationBlueprintLibrary. Root's retained evidence: reports/WC-U440/20260906T170719Z/neris-tala-motion-import/editor.log lines1226–1241. Some Neris mesh/early clip writes occurred; Neris Active/Tala were not reached. This is not relabeled a pass.
- Corrected from installed Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h line65 UCLASS(meta=(ScriptName="AnimationLibrary")). Importer now uses unreal.AnimationLibrary and checks required callable methods before any selected-hero mutation.
- tools/unreal/probe_attack_window_api.py is an optional read-only reflected API/query probe, writing attack-window-api-probe.json under WC_EDITOR_REPORT_DIR. It loads existing Neris Attack without saving/importing. Root owns its execution and fresh import retry.

Verification retained here

- python-tests-final.log: full current suite144 tests passed. This includes five new authored/import-readback contract fixture tests; other lanes added tests during the session.
- Python compiler checks for importer/helper/probe passed.
- native-01: actual MSVC build passed; focused fixture failed because it referenced a nonexistent hero ID. Preserved unchanged. Corrected test uses existing canonical Sylas, Rowan, Ada and Neris, with HP multiplied100 only in this explicitly controlled observation fixture.
- native-02/focused.log: PASS8208 checks; actual basics219, active casts38, recovery samples3954, stun samples200, delivered basic damage events208. Each delivered basic action has one recorded commitment and one damage event at release plus canonical travel. The difference between commitments and deliveries is not relabeled as all successful attacks.
- Pure sampler tests cover both250ms releases, no crossing into the second window, duplicate recovery identity, global action-ID interleaving, missing-snapshot clamp, scouting reconstruction and a new combat's first cut.
- native-02/source snapshots bind baseline pre-ordinal core and current core to the exact same generated catalog fixture. Both native runtime harnesses completed 100 full actual-combat tournaments and compared all CSV fields except measured wall_ms. See process.json/equivalence.json and the completed counts below.
- Native CPU results do not establish animation pose evaluation, cold/cooked marker survival, physical LAN, packaged human play or frame-time acceptance.

Root continuation

1. Build the combined protocol6 C++ checkpoint. Run WonderChess.Presentation.AttackWindowMetadata and relevant current data/asset tests.
2. Execute the corrected marker API probe/import retry in fresh evidence. Import authored window revisions serially as each source owner freezes them.
3. Cold-load each marked Attack and verify six markers, full duration, both canonical offsets and all original rig/material/clip checks. Source-manifest-required windows must not be missing after cooking.
4. Run an actual rendered combat with -WCWindowAudit: observe right/left succession, release position, recovery hold, interruption, scouting away/back and restart. Compare ordinal logs to real public snapshots and basic event IDs. One selected cut must never run into the next cut for the same action.
5. Review complete source/Unreal Attack movies for both cuts and seam, including asymmetric weapon/mantle/case/lantern clearance. No source/visual completeness claim is made by this C++ checkpoint.

Actual follow-up: root reran the selected import with the corrected reflected API. reports/WC-U440/20260906T171007Z/neris-tala-motion-import-python-api-fixed/import-selected.json records Neris6 and Tala5 with7clips each, both prior skeleton identities preserved, and empty Attack marker dictionaries matching their unmarked sources. This verifies actual AnimationLibrary query/owned-marker-cleanup/save path execution. Creation of six nonempty markers and cooked readback still require the first authored window asset. Original partial-write failure remains retained.

Completed native equivalence: native-02/process.json status PASS_NATIVE_EXECUTION_AND_EQUIVALENCE_ONLY, all four compile/focused/baseline/current exit codes0. Both baseline and current complete100 actual-combat tournaments, each3,379,152 assertions,12,597 encounters and1,815,540 combat events. Both retain1844 combat timeouts and524 ghost encounters; this is equivalence, not a tuning/visual acceptance claim. equivalence.json compares623,936 CSV rows across8 files: all semantic fields equal, excluding only tournaments.csv wall_ms. The other7 CSV files are byte-identical, including bot decisions, compositions, round economy/state hashes (which incorporate shop/bot RNG state), encounter outcomes, abilities and traits. No performance improvement inference is made from wall times under concurrent work.

Combined Unreal compile checkpoint: root's actual Editor build exited 6 after 139.65 seconds; retained log reports/WC-U430/20260906T171201Z/editor-build-protocol6-windows/build.log. The sole reported error was C4456 at WCImportedAssetTests.cpp:361: local Bounds shadowed an earlier mesh bounds variable. The authored frame range variable is now ClipFrames. Root's accompanying review also identified unchecked integral double-to-uint64 conversion for the new public ordinal: the presenter now requires 0 <= basicAttackOrdinal <= 9007199254740991, finite and integral, before casting. Owned-file git diff --check passed after both corrections. These are saved source fixes awaiting the next actual Editor build; the failed build remains a failure.
