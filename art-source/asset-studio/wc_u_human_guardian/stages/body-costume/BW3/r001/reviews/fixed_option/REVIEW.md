# BW3 optional fixed-grip source assessment

**Recommendation: a separately adopted fixed closed grip is compatible with the behavior authored in Ada's current game source. It is not adopted here, does not cure the failed animated-thumb study, and is not yet verified on a new candidate in Unreal.** If the final authorized animated-thumb correction remains ART_REVISE, offer this narrower production route for explicit selection instead of continuing equivalent pose adjustments.

The inspected handoff is `production/asset-studio/supplements/BW3/docs/04_FIXED_GRIP_OPTION.md` (the actual filename does not contain GAME). Its proposal requires a newly constructed, noncollapsed closed hand, actual weapon fit, correct runtime-rest conversion, wrist continuity, and seven-clip engine review. It does not permit freezing the failed intersecting grip and relabeling it accepted.

## Freshly inspected source

Opened `art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend` read-only in a separate Blender 5.1.1 background process with `--factory-startup --disable-autoexec`. File SHA-256 before and after was `54f04b8f28fd819eb22b7a4f6c8051484c6466513e6cd43d419c835b67d950b3`. No source was saved, no live Blender session accessed, and no game was run.

The manifest identifies source revision 9 and animation revision 8. The actual armature has **27 bones, including hand_r/hand_l and child weapon_r/weapon_l, with no finger/thumb bones**. Each of the seven actual actions has 162 bone location/rotation curves. There are no non-bone action paths, digit curves, shape keys, object drivers, pose constraints, or other actions in this source.

All half-frames across each full clip were evaluated, including endpoints: **865 pose samples total**. For each pose, actual evaluated mesh points weighted entirely to each hand were transformed back into that evaluated hand's frame. This includes the body hand components, equipment, combined mesh, and both LODs. Their maximum motion relative to their hand was **0.0006671 mm**, consistent with float evaluation noise. Weapon-joint matrices relative to the corresponding hand varied by at most **2.68221e-7 per matrix element**. The actions do not open or close fingers, and the sword does not animate out of the hand in this authored source.

| Actual action | Source frames, 60 fps | Duration | Half-frame samples | Hand / equipment behavior observed |
|---|---:|---:|---:|---|
| Idle | 1–121 | 2.00 s | 241 | Fixed relative to hand |
| Move | 1–61 | 1.00 s | 121 | Fixed relative to hand |
| Attack | 1–40 | 0.65 s | 79 | Fixed relative to hand |
| Active | 1–37 | 0.60 s | 73 | Fixed relative to hand |
| Hit | 1–25 | 0.40 s | 49 | Fixed relative to hand |
| Defeat | 1–61 | 1.00 s | 121 | Fixed relative to hand; no authored drop |
| Victory | 1–91 | 1.50 s | 181 | Fixed relative to hand |

The 52 source equipment vertices assigned to hand_r comprise handle, guard, and blade islands; all 52 are rigidly weighted to hand_r. The 420 left-hand equipment vertices are rigidly weighted to hand_l. The current game uses equipment geometry within its skeletal mesh; the existence of weapon_r/weapon_l socket bones does not mean the sword is currently a separately detachable object.

This is animation/geometry inspection, **not a claim that the current hand shape is visually convincing or that a visible open-looking gap cannot exist**. It establishes invariant hand geometry and no authored release/opening behavior. No new native render or packaged pixel review was performed in this bounded source assessment.

## Runtime source and existing checkpoint evidence

- `game/Source/WonderChessRuntime/Private/WCBoardPresenter.cpp:481` maps actual combat presentation to Idle, Move, Attack, Active, Hit, Defeat, and Victory; line 524 plays the corresponding skeletal animation. The inspected path has no finger-opening or weapon-drop override.
- `game/Source/WonderChessRuntime/Private/WCBoardPresenter.cpp:544` derives attack/cast animation time from authoritative releaseTick minus windup. `tools/blender/author_alpha.py:463` likewise derives the manifest's release_frame from attack windup or ability cast milliseconds. **Attack frame 16 and Active frame 19 are event timing, not sword-release instructions.**
- `game/Source/WonderChessRuntime/Private/WCFrontEnd.cpp:647` exposes all seven clips in the gallery, including Defeat and Victory, with manual rotation and turntable controls. `game/Source/WonderChessRuntime/Private/WCFrontEndScene.cpp:182` loads and loops the selected action on the hero component. A fixed hand must therefore survive gallery close inspection and rotation as well as board motion.
- `WCFrontEndScene.cpp:26` resolves the default canonical `/Game/WonderChess/Heroes/` folder; its optional AQ1 override is a distinct candidate path. No BW3 replacement is present or authorized by this review.
- The actual source geometry and construction support the same reading: `tools/blender/author_alpha.py:373` assigns Ada's sword to hand_r; `tools/blender/refine_update_ada.py:133` identifies and refines those existing single-hand-weighted equipment islands without changing their topology or weights.

All **10 current FBX files** (seven animations plus mesh/LODs) match `exports/heroes/wc_u_human_guardian/export_manifest.json`. All **seven current animation .uasset hashes** match Ada's rows in `reports/WC-U440/20260907T165200Z-closeout/asset-matrix-complete-inputs/hero-clips-168.csv`. `reports/implementation_state.json` retains the 24-hero `builds/WonderChess-Update24-Checkpoint-r4/Windows/WonderChess.exe` delivery record.

The prior import report `reports/WC-U440/20260906T160431Z/ada9-import/import-wc_u_human_guardian.json` records the same seven lengths and prior skeleton identity retention. This is prior report evidence. Its lack of imported content binary hashes remains explicit in the closeout CSV; matching that later CSV does not manufacture a new import binding or packaged verification. Current Unreal binaries were hashed, not decoded or executed here.

## Prerequisites before an explicitly selected fixed route

1. **Resolve the actual equipment contract.** The canonical source's identified 16-vertex handle has mesh-space dimensions **77.3136 × 77.3136 × 209.3000 mm** (across-corners section, not a claim of circular diameter). Its guard is 229.320 mm wide. The BW3 fixture is 28 mm in diameter and 109 mm long. They are materially different fits. Either construct the fixed hand for the retained intended weapon, or explicitly select a separate Ada equipment candidate and preserve canonical equipment. A successful 28 mm proxy fit cannot be reused as evidence for the current sword.
2. Preserve the MPFB open source and failed BW2/BW3 studies. Start a separate derived hand from noncollapsed geometry. Remodel/sculpt the closed thumb/web/fingers into a collision-free shape; do not freeze the intersecting posed mesh. Recheck complete hand and glove self-intersection, their mutual clearance, actual handle/guard/pommel clearance, wrist opening, normals, and silhouette. Remap contact regions if topology changes.
3. Reconcile the **163-bone MPFB authoring rig with the actual 27-bone runtime rig** using measured grip/rest/object matrices and consistent units, with the source's uniform scale included exactly once. Use the documented rigid evaluated-surface placement only after constructing an acceptable fixed surface; it is not an inverse of blended finger skinning. Verify a zero-pose round trip and actual target-hand movement.
4. Use the intended runtime hand joint for the rigid grip and deliberately construct the wrist/cuff transition. Remove any duplicate baked-plus-live finger deformation from the derivative. Preserve shared skeleton/socket interfaces. The current sword's hand_r weighting and a future separate attachment must not both transform one sword.
5. Review all seven actual source actions and transitions on the derived candidate, then perform isolated Unreal import/reimport and normal-speed board/gallery review with actual equipment. Inspect the wrist seam, front/back of fingers, thumb web, guard, pommel, scale, normals, and bounds. This requires actual images/motion; the numerical source audit is not a substitute.

Only then can the result be submitted for development-use review as a **fixed game grip**. It would not pass the BW3 opening/closing requirement, certify the original animated thumb, or establish a reusable animated-hand recipe. A later release/open-hand feature would need a new compatible solution.

## Files produced in this directory

- `actual_game_grip_source_audit.json`: actual rest matrices, component indices/bounds, all seven action paths, sample counts, and measured hand-relative invariance.
- `source_provenance.json`: fresh source/export/content hashes, exact prior report references, current delivery record, and untested boundaries.
- `inspect_game_grips.py`, `inspect_game_grips.log`, `collect_source_provenance.py`: executed read-only inspection recipe and log.

All outputs of this task are confined to BW3/r001/reviews/fixed_option. No modeling method was adopted, no geometry/action/runtime source was changed, and no human or art approval was issued.
