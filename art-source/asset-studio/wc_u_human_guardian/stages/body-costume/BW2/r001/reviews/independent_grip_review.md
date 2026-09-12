# BW2 anatomical-right grip: independent image review

## Initial candidate only

Status: **ART_REVISE — initial calibrated grip, not accepted contact.** This section applies only to the `grip_initial_*` images. It does not assess later corrective passes or certify the final saved candidate.

The reviewer read `production/asset-studio/supplements/BW2/docs/02_GRIP_FRAME_AND_CONTACT.md` and inspected these actual images:

- `captures/locked_handle_open_palm.png`
- `captures/locked_handle_open_side.png`
- `captures/grip_initial_palm.png`
- `captures/grip_initial_side.png`
- `captures/grip_initial_axial.png`
- `captures/grip_initial_back.png`
- `captures/grip_initial_oblique.png`

The BW1 final sword/shield grip images were inspected during the preceding review and supply a qualitative failure baseline. No current or prior modelling scripts, live Blender state, mesh data or contact computation were inspected for this assessment. No Blender calls, scene edits or human approval were performed.

### Visible improvement

The neutral views establish a sensible visible relationship between an open palm and a handle running across the finger bases. In the initial closed images, the fingers now curve over the cylinder instead of forming the disconnected fist below it seen in BW1. The index has a useful start toward wrapping around the side. Preserve that progress and the fixed-handle setup while correcting the remaining digits. The images do not independently verify dimensions, coordinate-frame handedness, bone axes or that the handle was numerically unchanged.

### Remaining defects, ordered for the bounded correction

1. **The thumb does not establish an opposing pad contact.** The palm and oblique projections make its tip look close, but the side and axial views reveal an open C-shaped space rather than complete enclosure. Its long distal form points diagonally along the handle, and its broad pad is not clearly presented squarely toward the opposite cylinder side. Correct opposition and pad orientation, not only the last-joint curl or the nearest visible edge. An attractive silhouette from the palm camera is insufficient.
2. **Finger enclosure remains incomplete and uneven.** The middle and ring distal pads largely perch on the cylinder's upper quadrant instead of visibly continuing around its side. The index wraps farther than those digits. The little finger appears close in one projection, but its pad area is too occluded to establish meaningful contact. Follow each digit from its knuckle through intermediate joints to pad; do not turn five fingertips toward one shared point or move the handle to improve a chosen view.
3. **Joint shaping needs scrutiny as closure increases.** Side and oblique views show angular or flattened transitions across some proximal-to-middle joints, particularly the index/middle silhouettes. These do not yet resemble the severe BW1 collapse, but additional curl could deepen the bends into abrupt corners or pinch the glove. The back view is too smooth and occluded to prove healthy deformation throughout each joint. No self-intersection or full-surface collision pass is established by these images.

The task owner separately reports substantial thumb separation and uneven middle-finger patch distances. Those numerical observations were not recomputed by this reviewer, and they must not be treated as image-derived measurements. They are consistent with withholding contact acceptance even where one camera makes the pads appear close.

### Recommended first corrective emphasis

Keep the fixed handle and useful index relation. Improve one middle-finger pad enclosure first, preserving phalange proportions and a credible knuckle arc; then bring the ring/little into a compatible wrap. Treat thumb-base opposition and pad-facing direction as a separate correction. Compare palm, side and axial images together before judging whether a small contact patch or larger flexion change is appropriate. The author should continue to evaluate declared glove-surface patches and full triangles, because these shaded images cannot resolve sub-millimetre gaps, hidden penetration or cap-only contact.

### Not established by this initial review

All required digit pads in contact; opposing-thumb enclosure; maintained glove thickness; collision-free evaluated surfaces; contact preservation during wrist/elbow/arm movement; actual sword guard/pommel clearance; source-file integrity; save/reopen; second-body reuse; runtime compatibility; any human or forms approval. Later evidence must be reviewed as a separately labelled candidate.

## Integrated candidate review

This addendum reviews only the subsequent `grip_integrated_*` evidence. Images inspected directly: `captures/grip_integrated_palm.png`, `captures/grip_integrated_side.png`, `captures/grip_integrated_axial.png`, `captures/grip_integrated_oblique.png`, and `captures/grip_integrated_back.png`.

**Decision: retain this as a visibly improved contact candidate over the initial pose, with ART_REVISE still appropriate.** The task owner reports that declared digit and thumb patch distances now meet the numerical targets. This reviewer did not recompute those values. The images support improved finger enclosure but do not yet establish convincing thumb anatomy or full-surface collision freedom.

### What improved

The middle and ring distal segments now descend farther around the cylinder side; in palm and oblique views they no longer merely perch on its upper quadrant. The index's useful wrap is broadly retained. The visible finger arc therefore encloses the cylinder more convincingly than the initial pose. Preserve this contact arrangement, the locked handle and the original declared pad samples during any further localized correction.

### Remaining defects and uncertainty

- **Sharp thumb-web collapse is visible.** The axial view exposes a long, narrow crease descending from the thumb/handle area into the palm. The palm/oblique views show the thenar region drawn into a narrow upper attachment instead of a soft, substantial thumb-base transition. The crease looks more like a pinched deformation boundary than an intentional glove fold.
- **Opposing thumb-pad orientation remains insufficiently exposed.** The thumb that was visibly floating in the initial candidate is now largely hidden behind the handle in these views. Occlusion is not itself a defect, but these images cannot show whether a broad pad faces the opposite cylinder surface or whether a narrow edge/folded segment is supplying the measured contact. A thumb-side closeup and a handle-hidden diagnostic would resolve this without moving the fixed handle or changing the grasp.
- **Additional web/joint distortion remains.** The back view shows a sharper pinched valley near the middle/ring finger bases than the initial image, and some proximal-to-middle finger transitions remain angular. The grasp has improved more than the anatomy. These areas deserve inspection through open-to-close motion before the glove is considered stable.
- **Skin versus glove cause is unknown from this set.** These captures show one shaded outer surface, not separately labelled skin and glove comparisons. The reviewer cannot determine whether the observed collapse originates in the underlying skin deformation, copied glove weights, glove fit or the pose itself. No claim that a weight transfer or skin correction succeeded is justified from these images.

### Bounded next action

A **local thumb-web correction on the copied candidate** is justified by the visible crease; another whole-hand curl pass is not. First compare skin and glove at the same retained pose. If only the glove collapses, inspect the copied thumb/hand weight distribution and correct that small web region while protecting the thumb pad and all established finger contacts. If the skin collapses too, identify its joint/pose or local weighting cause before editing the glove to disguise it. This is a diagnostic recommendation, not a claim that weights have been proven to be the cause.

After the bounded change, inspect the same five cameras plus the diagnostic thumb view, then rerun the unchanged contact samples and full-surface collision checks. Retain the integrated pre-correction candidate if the edit worsens contact or merely relocates the crease. Anatomical-right local review remains pending; no actual sword substitution, shield adaptation, full character approval, recipe promotion or human approval follows from these static images alone.

## Final diagnostic review and stop decision

**Final decision: stop at ART_REVISE.** This final assessment supersedes the earlier conditional suggestion of a small weight correction. Confirmed surface crossings and the new exposed cage/handle-hidden views show that the failure is more serious than a crease that can safely be assumed cosmetic. No further modelling was performed by this reviewer.

Additional actual pixels inspected:

- `captures/actual_posed_cage_axial.png` and `captures/actual_posed_cage_back.png`.
- `captures/integrated_axial_handle_hidden.png`, `captures/integrated_thumb_side_handle_hidden.png`, and `captures/integrated_thumb_side.png`.
- `captures/grip_retained_reversed_light.png`.
- `captures/comparison_BW2_initial_vs_retained.png`: AS1 comparison, initial closed candidate on the top row and retained integrated candidate on the bottom, in palm/side/axial order.

The handle-hidden axial image exposes the elongated, sharply folded web/palm surface that the cylinder previously obscured. The actual posed cage shows compressed and crossing-looking surface flow in this transition, while the back cage reveals the pinched interdigit valleys. Reversed lighting preserves the defect. The thumb cannot be judged as a healthy opposing digit merely because its selected pad approaches the cylinder. The fingers have improved their visible wrap, but the hand as a connected deforming surface remains invalid for acceptance.

The separately executed geometry audit was read, not recomputed by this image reviewer. `integrated-independent/integrated_geometry_audit.json` and `web_weight_diagnosis.json` bind their findings to `grip_integrated_contact_r001.blend`, SHA256 `9509750f833cec0c8cac90cd866215a732baed67571d1d444c7b718f441f877d`. They report **375 confirmed nonadjacent transverse triangle-crossing pairs in the retained linear-skinning glove**:

| Region pairing | Confirmed crossing pairs |
|---|---:|
| Middle / ring | 167 |
| Palm or wrist / thumb | 88 |
| Middle / thumb | 58 |
| Index / thumb | 52 |
| Within individual digits | 10 |
| Total | 375 |

These are triangle-pair counts, not 375 distinct anatomical wounds, vertices or contact patches. Shared-vertex triangle pairs were excluded; coplanar overlap and tangential contact were not classified. The same audit reports 567 pairs in the underlying linear-skinned body, so a glove-only transfer correction must not be assumed sufficient. The unsaved dual-quaternion trial still had 368 glove crossing pairs and approximately **0.7205 mm maximum handle penetration**, exceeding the stated 0.5 mm screen. That trial is rejected; a slightly smaller crossing count does not make it acceptable.

The separate pad contact screens therefore do not establish a valid grasp. Preserve the calibrated frame/handle contract, controlled captures and the useful finger-wrap progress as evidence of what worked. Preserve the invalid integrated pose as a clearly marked study, not an approved reusable grip. The next method needs explicit collision-free thumb-base and interdigit volume construction, with joint/weight and surface causes distinguished; it should not be another unconstrained curl search. The actual sword was **not adapted**, and no shield propagation, runtime skeleton decision, second-body fit, reusable-recipe promotion or human approval occurred.

## Protected r003 contextual baseline captures

At the task owner's request, this reviewer performed a separate **read-only background Blender render operation**, without using the live editor and without saving a `.blend`. This is documented separately from the preceding independent visual judgments.

Input baseline: `BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend`, SHA256 `03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8`.

Diagnostic camera/light/material source: frozen `ada_bw2_grip_checkpoint_r001_ART_REVISE.blend`, SHA256 `d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf`.

The baseline retained `BW1_DIAGNOSTIC_RANGE_ART_REVISE` and was evaluated at **frame 1**, with only `BW1_Glove_Pair_SourceFit` and `BW1_Sword_Handle_R` visible as meshes. The old handle and finger pose were not moved. BW2 diagnostic cameras, lighting, clay materials, world and rendering settings were appended/applied only in the unsaved render process. Camera matrix round-trip differences were at most `1.1920928955078125e-7`; there was no image warping. Both protected input hashes were verified unchanged before and after rendering.

Actual rendered and inspected files:

- `baseline-r003/BW1_r003_frame1_palm.png`
- `baseline-r003/BW1_r003_frame1_side.png`
- `baseline-r003/BW1_r003_frame1_axial.png`
- `baseline-r003/comparison_BW1_r003_vs_BW2.png`

**Frame 1 is the original open contextual hand, not a closed-grip failure.** The comparison's top row is that unmodified open hand with its original faceted handle; the bottom row is the BW2 integrated closed candidate with its diagnostic handle. It provides honest scene history under matched cameras but must not be presented as an exact same-pose contact improvement or as the prior BW1 isolated closed-grip experiment. The separate BW2 initial-versus-retained sheet is the relevant contact-correction comparison.

The AS1 helper produced both sheets by labelled downsampling only and reports `registered: false` and no quality score. Per-image hashes, input hashes, render settings, original pose matrices, action and camera metadata are in `baseline-r003/capture_metadata.json` and `baseline-r003/comparison_metadata.json`. The background job's first attempt stopped before creating any images because of a material-list mapping error; the corrected job rendered all three views, verified preservation and exited successfully. No protected or candidate `.blend` was saved in either process.
