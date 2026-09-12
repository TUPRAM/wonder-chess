# BW4 current game contract and separate hilt proposal

The fixed closed-hand route is consistent with the current authored Ada source. The actual sword handle remains an oversized fitting constraint. A smaller, separately labeled hilt has been constructed for the user's equipment decision; it is **UNSELECTED**, has not been fitted to a hand, and is not a canonical replacement.

## Fresh source inspection

Opened `art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend` read-only in Blender 5.1.1 with factory startup and automatic script execution disabled. SHA-256 before and after remains `54f04b8f28fd819eb22b7a4f6c8051484c6466513e6cd43d419c835b67d950b3`, identical to BW3's previously inspected source. The source and the live Blender session were never saved or edited by this audit.

- Exactly 27 bones; no finger, thumb, or other digit bones.
- Seven actual actions: Idle 1–121, Move 1–61, Attack 1–40, Active 1–37, Hit 1–25, Defeat 1–61, Victory 1–91, at 60 fps.
- Reran all 865 half-frame source evaluations. The hand-bound geometry and equipment retain their relationships within 0.0006671 mm floating-point variation; weapon joints retain their relationship to the hand. No authored opening or weapon drop is present.
- Each action has 162 bone transform curves, with no non-bone action paths, digit curves, shape-key animation, object drivers, or pose constraints in this source.
- Current `WCBoardPresenter.cpp` still selects all seven clips and plays the corresponding skeletal animation. Its attack release handling is authoritative event timing, not an equipment-drop instruction. Current `WCFrontEndScene.cpp` still plays the selected gallery clip. These code paths were read, not executed.
- Fresh engine execution, import, packaged gameplay, and new-hand clip review were not performed by this source-contract task.

Full current results are in `actual_game_grip_source_audit.json`. Exact equipment geometry, source vertex IDs, face indices, world coordinates, hand-bind coordinates, and relevant rest matrices are in `actual_hilt_and_bind.json`.

## Actual equipment, measured in metres with unit scale 1

The equipment object and armature both have identity world transforms. All 52 sword vertices are already rigidly weighted to `hand_r`; adding a second socket/parent-driven deformation to these vertices would double-transform the sword.

| Part | Source construction and measured size |
|---|---|
| Handle | 16 vertices, two octagonal rings and end caps; constant 77.314 × 77.314 mm across-corners section, about 71.428 mm across flats; 209.300 mm overall length |
| Exposed handle | 164.900 mm below the lowest guard surface; the upper 44.400 mm overlaps the guard region |
| Guard | Separate 16-vertex island; 229.320 × 65.520 × 49.140 mm world bounds |
| Blade | Separate 20-vertex island; 124.124 × 43.680 × 540.540 mm world bounds |
| Pommel | No separate pommel island or modeled pommel feature identified; the handle has a flat capped lower end |

These are measurements of the source geometry, not dimensions inferred from the reference illustration. The section is faceted, not an ideal 77 mm cylinder. A fit around the old 28 mm BW2/BW3 fixture does not demonstrate fit around this hilt.

The 77.3 mm cross-section is close to the approximately 85 mm palm width reported by the root's clean open MPFB glove extraction. That makes a conventional closed, opposing-thumb grip doubtful without an oversized glove or distorted digits. This is a fitting assessment; a new closed hand has not yet been modeled or tested here.

## Reviewable, unselected equipment proposal

`ada_bw4_hilt_proposal_UNSELECTED_REVIEW.blend` contains separate actual and proposed hilt assemblies. Both preserve the blade and guard geometry. The proposal changes only the handle: 30 × 26 mm across-corners octagonal section, with 110 mm exposed below the guard. The original upper endpoint is retained, so the total handle remains 154.400 mm including the 44.400 mm guard overlap. No pommel is added. This is a documented starting fit proposal, not a size recovered from Ada's painting.

The authoritative diagnostic image is `actual_vs_unselected_hilt_proposal_review.png`. It was rendered by Blender, opened and inspected directly. The blade is explicitly hidden from this closeup for readable labels; its geometry remains in the saved proposal file. The initial `actual_vs_unselected_hilt_proposal.png` was overexposed and is retained as a failed diagnostic presentation, not review evidence.

`hilt_proposal_geometry.json` supplies both proposal coordinates in canonical world space and transformed `hand_r` bind space, the unchanged face connectivity, explicit dimensions, and separate presentation offsets. Mesh vertices in the `.blend` remain in canonical bind/world coordinates; the assembly parents apply display-only translation. Remove or ignore those display offsets when reusing the proposal. The root must obtain the user's equipment selection before final fitting to changed geometry.

The proposal was saved and reopened in a fresh background process. All six actual/proposed meshes independently own their mesh data. Coordinates match the explicit records within 1e-7 m; the canonical source hash remains unchanged. See `hilt_proposal_reopen.json` and `hilt_proposal_review_manifest.json`.

## Wrist and bind-space advice

The actual `hand_r` rest origin is `(-0.573300004, 0.063700005, 0.828099847)` m. Its rest basis columns are approximately:

```
X = ( 0.995037317, -0.000000011, -0.099503815)
Y = (-0.092450216,  0.369799942, -0.924500108)
Z = ( 0.036796559,  0.929111302,  0.367964745)
```

The exact 4×4 hand, lower-arm, and weapon matrices are in the JSON. MPFB's `wrist.R` origin, orientation, and uniform armature scale differ from these. Do not treat its metric hand frame or pose-bone local coordinates as this game bind frame. Establish a deliberate rigid alignment from the newly constructed local glove frame to the destination hand frame. Include the source world scale once; do not scale the glove to compensate for the hilt.

For a newly authored rigid glove with local metric coordinates `q`, a verified hand-local alignment `C`, destination armature world `A_d`, destination rest bone `R_d`, and mesh world `M_d`, store `v_d = inverse(M_d) A_d R_d C q` and bind the fixed palm/digits 100% to `hand_r`. Their evaluated world position should then be `A_d P_d(t) C q`. Check an explicit rest round trip and actual posed vertices. This is valid for a rigid part, not an inverse of mixed-weight MPFB finger or cuff deformation.

Preserve the game rest pose. Model the wrist/cuff transition separately, because the rigid hand formula does not repair a blended cuff or guarantee sleeve coverage. The bracer should follow the lower arm, while the fixed glove follows `hand_r`. No bone, socket, action, source mesh, runtime file, or shared profile was changed in this task.

## Remaining decisions and untested boundaries

1. The user must select the separately proposed hilt if it will be used for final fitting. The canonical hilt remains the default until that decision.
2. The root's hand construction still needs plausible geometry, web and neighboring-digit clearance, actual hilt contact, guard clearance, and wrist coverage.
3. All seven actions and transitions must be reviewed on that actual new geometry. The old source's rigid invariance is not a new candidate pass.
4. Unreal import/reimport and packaged review remain separate unrun gates. No human art approval or reusable-recipe claim is issued.
