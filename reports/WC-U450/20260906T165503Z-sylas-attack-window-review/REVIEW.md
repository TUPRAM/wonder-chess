# Sylas alternating basic-cut integration: read-only feasibility review

Status: FEASIBLE, NOT IMPLEMENTED. No game source, canonical data, Blender source, exports or binary assets were changed in this investigation. Root is compiling a separate frozen checkpoint.

Current evidence

- docs/heroes/wc_u_elf_rogue.md requires alternating readable basic cuts, 250 ms basic windup, seven clips and visual-only equipment.
- exports/heroes/wc_u_elf_rogue/export_manifest.json: source_revision 8; Attack frames 1..40 at 60 fps, 0.65 s; release frame 16 (15 frame intervals = 250 ms). Source SHA256 223d2ed2a46e09387479ea854f555f0219ca3b5ce1138658f8956b065416b7d9.
- tools/blender/repair_update_elf_shoulders.py, candidate(): left arm closes the guard during recovery. The retained manifest explicitly says this does not prove alternating successive combat attacks.
- WCBoardPresenter.cpp around 443..523 selects the same Attack asset on a state/action change, then seeks to elapsed time reconstructed from snapshotTick and releaseTick. It permits ordinary animation advancement until the full asset end. A doubled asset alone would therefore leak into a second strike for one authoritative attack.
- Simulation/WonderSimulation.cpp around 589 and 990 allocates actionId from one combat-wide nextAction_ counter for all units and both active and basic actions. actionId modulo 2 cannot alternate Sylas's own basics.
- WCMatchRuntime.cpp currently publishes only a rolling two-second event window. Late spectating and missing snapshots cannot reconstruct a complete committed-attack count from this payload.

Recommended asset layout

Keep the exact AN_wc_u_elf_rogue_Attack identity and seven-clip count. Author one 1.30 s Attack sequence with two complete in-place cycles, sharing an equivalent neutral boundary pose:

| Window | Blender frames | Asset seconds | Sole presentation release |
| --- | --- | --- | --- |
| Right cut | 1..40 | 0.00..0.65 | frame 16 / 0.25 s |
| Left cut | 40..79 | 0.65..1.30 | frame 55 / 0.90 s |

Each release is exactly 250 ms after its own window start. The left window needs its own full anticipation, blade sweep, follow-through and recovery, not the current off-hand guard. Keep root translation zero, existing 27-bone hierarchy/rest pose/socket identities, mesh weights and attached asymmetric equipment. Do not mirror or swap the actual mesh, mantle, document case, lantern or props. Author and inspect the two arms' paths against that unchanged equipment. Both cuts may share the start/end stance if continuity is preserved. The first/last sequence poses should also support gallery looping without a seam.

Store optional presentation_windows metadata in the hero export manifest's Attack clip with name, start_frame, release_frame and end_frame. Keep legacy release_frame=16 as the first presentation marker for tools that only sample one marker; update acceptance sampling to include BOTH windows. This export manifest is not data/asset_manifest.json and has no current JSON schema. Add a narrow validator for window ordering, shared boundary, frame range, positive duration and (release-start)/fps == canonical attack_windup_ms/1000. No combat values or canonical unit/balance schema changes are needed for the layout.

Cooked window metadata without a new UObject type

Use six uniquely named sync markers on the existing AnimSequence, for example WC_Attack_R_Start, WC_Attack_R_Release, WC_Attack_R_End, WC_Attack_L_Start, WC_Attack_L_Release, WC_Attack_L_End. Import them from the export manifest on a dedicated notify track. These are timing metadata, not notify-driven damage or sound events.

Verified installed UE5.7 APIs:
- Engine/Classes/Animation/AnimSequence.h: UPROPERTY AuthoredSyncMarkers is outside WITH_EDITORONLY_DATA.
- Engine/Public/Animation/AnimTypes.h: FAnimSyncMarker.MarkerName and Time are runtime UPROPERTY fields; TrackIndex/Guid alone are editor-only.
- Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h: Blueprint-callable AddAnimationSyncMarker, RemoveAnimationSyncMarkersByName/ByTrack and related track APIs. Its actual implementation validates time and an existing notify track, appends markers and refreshes cache data.
- Runtime reads Animation->AuthoredSyncMarkers. No EditorAssetLibrary metadata tags: those would not be a reliable cooked gameplay source.

Minimal runtime API/change

Add a small presentation helper to parse/validate the marker windows once per loaded Attack asset. The existing importer should populate these markers after FBX import, save the same sequence, and verify marker names/times by readback. WCImportedAssetTests must use validated window extent for this marked asset (1.30 s), while retaining the current 0.65 s expectation for unmarked ordinary clips.

Select one complete window per committed basic action and hold its final pose after recovery. Preserve the SAME chosen window when AttackWindup changes to AttackRecovery for the SAME action. An active spell, hit, defeat, movement or a new basic action interrupts it normally. Runtime play time should be window.start + clamped elapsed time from the existing releaseTick/snapshotTick clock; do not scale the 250 ms release by an arbitrary animation rate. A new quicker attack may interrupt the previous recovery as it already does.

Enforce the window end BEFORE pose evaluation. Merely seeking to the start and allowing a nonlooping 1.30 s asset to run is insufficient. A straightforward single-node implementation sets playing=false for the windowed attack only, drives SetPosition(window.start + clamp(localElapsed, 0, window.duration), false) every presentation update, and restores normal playback for other clips. Keep component pose updates enabled; bPauseAnims is not the correct segment clamp. Installed AnimSingleNodeInstance.cpp confirms SetPosition(..., false) updates the proxy clock without triggering animation notifies. Continuous timing/pose behavior still requires the actual engine check. Root may prefer an equally bounded tested helper with explicit tick ordering.

Alternation identity: exact requirement and smallest robust option

Strict alternation of successive committed basic actions, including across skipped snapshots or scouting, needs one reconstruction-safe ordinal. A client-local counter can alternate observed actions only. A combat-wide actionId parity is incorrect. Counting the last two seconds of damage events is also incorrect, and deriving counts from successful hits excludes cancelled windups.

Recommended small addition: CombatUnit.basicAttackOrdinal starts at zero and increments ONLY at the existing basic-attack commitment branch beside actionId assignment. It is presentation-only: never read by targeting, attack scheduling, damage, packet/effect creation, RNG, economy or outcome logic. Publish it as an additive basicAttackOrdinal field on each combat-unit snapshot. Runtime window index is (ordinal-1) modulo validated window count. Active casts do not increment it; recovery reuses it; each newly constructed combat starts a fresh count. No new damage packet, combat event, stat or balance input is added.

This does require a native CombatUnit field and one additive public snapshot field, plus an explicit network-contract note and tests. It does not require canonical units/rules/traits/schema changes. If the task constrains even presentation state in CombatUnit, the smaller alternative is a presenter-local per-encounter/per-unit counter of distinct basic action IDs; its documented limitation is observation-dependent parity after missed actions/late spectating. That alternative cannot honestly claim strict globally consistent alternation. Do not silently substitute it.

Gallery and review

The existing scene plays the full Attack asset, so the 1.30 s sequence naturally shows right then left. The native movie recorder samples GetPlayLength, so it can capture both windows without adding an eighth clip. Validate the full 1.30 s clip, both release landmarks, the shared midpoint and the loop seam. Runtime evidence must separately show two successive actual basic actions choosing different windows and one authoritative packet per action.

Importer issue to avoid

The legacy tools/unreal/import_animation_revision.py still refuses a canonical alpha list unless it has exactly twelve IDs and caps its list at84. It is not currently compatible with this adopted24 roster. Prefer the already-used selected-hero import_alpha_assets.py wrapper, adding manifest-driven marker installation there. If a protected animation-only path is chosen, explicitly repair and test its24 preflight first; do not infer current compatibility from its old existence.

Meaningful verification needed after implementation

- Invalid/missing/overlapping/out-of-bounds marker windows reject acceptance; ordinary unmarked hero clips retain existing behavior.
- Native actual combat: right/left/right selection for the same hero despite other actors' interleaved basics and intervening active casts; interrupted windup, rapid attack rate, stun/death, phase restart and new match are handled explicitly.
- Exact phase boundary: seek at window start, +250 ms and end; never sample the other window during a single basic action. Same-action Windup->Recovery does not toggle the window.
- Scouting late and low snapshot cadence obtain the same authoritative ordinal/window without replaying old effects.
- Cold editor and cooked Shipping readback preserve the six marker names/times and actual1.30s imported sequence; 60fps, root/scale, skeleton/socket and material checks remain.
- Full continuous source and Unreal Attack review must inspect both arms, mantle/document-case/blade clearance and seam, not just three sampled poses.
- Compare same-seed combat event/packet/outcome fields before/after; each real basic still generates the same one damage application and timing. Record asset/presentation evidence independently from core equivalence.

Alternative mirroring API, verified but not recommended here

UE5.7's UAnimSingleNodeInstance::SetMirrorDataTable does exist, forwards into its proxy, and the proxy calls FAnimationRuntime::MirrorPose with the assigned table. It would require a new calibrated MirrorDataTable for the exact rig, per-action table selection, and special gallery/review loop alternation to show both variants of the same0.65s sequence. Asymmetric weighted costume/props would remain part of the same mesh, but mirrored pose clearance must be inspected. Two authored windows give simpler full-clip review and avoid introducing an unvalidated mirror-table asset.
