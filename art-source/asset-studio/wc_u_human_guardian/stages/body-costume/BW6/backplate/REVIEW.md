# BW6 backplate — local review candidate

2026-09-11. Executed in Blender 5.1.1. The upper backplate/armhole correction is **locally viable for assembly review**. No human forms approval, runtime compatibility or completed-Ada claim is issued.

The former shell crossed the padded coat at rest and every sampled pose. The recorded source had 261 transverse pairs at frame1 and 320 at frame49. The conflict was in the broad upper shell at approximately Z 1.406–1.472 m; the separate neck/hem borders and the body query were clear. Actual posterior body, coat and shell sections were inspected before editing.

## Retained construction

The failed upper three-row shell was removed and replaced with six section rows that establish a narrower, concave armhole and controlled posterior planes over the scapular coat volume. The lower plate was not pushed backwards. Its center-up lower hem is preserved exactly at **18.0 mm above the lateral hem**. A quiet central ridge continues through the new upper planes.

One initial construction and two substantive corrective revisions were executed:

1. **Upper-shell recut:** cleared coat/body at frames 1,20,49,73,97, with zero raw/evaluated self crossings. Additional assembly queries exposed 172 shell/neck-border and 222 shell/hem-border crossing pairs.
2. **Connected edge bands:** replaced both separate overlaid border meshes with raised bands in the actual plate surface. Narrow band curvature caused 214 evaluated inner-wall self crossings, although the raw cage and coat/body checks were clear. This version was rejected.
3. **Wider edge bands — retained:** broadened the two local strips while retaining the 3.5 mm shell wall. The inner-wall failure cleared. Thirty interior band control points were repositioned; the initial candidate's other 150 control positions and the exact original hem boundary stayed unchanged. The bands are stylized connected edge construction, not historically exact rolled rims.

The final source is one separately editable object, `BW6_BackPlate_Rebuilt`, with 240 cage vertices / 210 faces, one review subdivision level, one 3.5 mm inward Solidify wall and rigid `spine01` weighting. The former backplate and two border objects remain hidden. This avoids exclusions that would merely conceal their overlapping geometry.

## Executed evidence

- **All 97 integer authoring frames:** zero confirmed transverse pairs for the retained plate against itself, evaluated coat, body, front plate, navy waist and both source side enclosures. Raw cage self query: zero.
- Raw cage has 58 intentional perimeter edges, no other nonmanifold edges, loose vertices or zero-area faces. The raw cage is an open shell control surface.
- At frame49, 35 posterior ray samples measured inner-shell/coat separation of **3.96–25.26 mm**, mean **10.14 mm**. The larger central space bridges the spine trough; it is not a constant clearance claim. Actual outer/inner cuts are retained in the section board.
- Both work and frozen candidate were reopened. Front, coat, body, navy waist, belt and both side-enclosure geometry/weights/world transforms match the root source. All original camera matrices/settings and sampled rig rest/pose matrices match. Candidate mesh, rig data and action are independently owned.
- A source-bound **97-frame authoring movie** was rendered and encoded, then reopened natively; 800×800 dimensions and all 97 frames were verified. Decoded frames 1,25,49,73,97 are included; frame49 and frame73 were visually inspected along with the original rest/pose captures. This is sampled visual review plus full integer-frame geometry checks, not a claim that every movie frame was visually approved.
- The append helper was actually executed against the original root context without saving it. It loads the one owned mesh, uses the existing rigid owner and hides the three replaced source objects. Source bytes remained unchanged.

The geometric query detects nonadjacent noncoplanar transverse intersections. It does not prove all containment, coplanar overlap, tangency or mathematically continuous motion. The separate new shoulder, bracer and current root's later side/coat changes still need combined assembly checks. Source shoulders shown in this lane's movie are unchanged context.

## Review files

- `ada_bw6_backplate_work.blend`
- `ada_bw6_backplate_checkpoint_REVIEW.blend`
- `captures/BW6_BACKPLATE_BEFORE_AFTER.png` — matched native back/profile pair views; coat is color-coded for fit inspection.
- `captures/retained_actual_cage_back.png`
- `captures/retained_uniform_clay_key.png` and `retained_uniform_clay_reversed_key.png`
- `captures/BW6_BACKPLATE_SECTION_BOARD.png`
- `motion/BW6_BACKPLATE_97_AUTHORING_ONLY.mp4`
- `records/retained_all97_audit.json`, `reopen_preservation_sections.json`, and `append_helper_test.json`

**Frozen SHA-256:** `9081f10ab60f36b29d8400b33056efc4e1bfbfa881e42438683fa56db378ec75`.

**Work SHA-256:** `d14ee53ad802caeba6a37dcc838747c60f44d4920f58754a01d3148ccb061b83`. Both reopen to identical candidate geometry; file bytes differ because Blender's work/copy save state differs.

**Preserved root source:** `../armor/ada_bw6_torso_recut_neck.blend`, SHA-256 `c9db4556de382b5a7670c38f060d1b0648c8aa6e02db0c9c65f5a6c08a33ae04`.

## Remaining review boundaries

The armhole and layer exposure are improved, but side fastenings/shoulder attachments remain a combined-assembly design decision. The broad back planes and subdued ridge need review against Ada's approved style; this local fit pass is not a claim of final silhouette likeness. The approximately 25 mm central posterior gap should be assessed in profile with the full assembly, rather than reduced by flattening the padded body.

No seven-game-clip test, shared skeleton modification, Unreal import, export/reimport, human approval or reusable recipe promotion occurred. The master MPFB, head/hair, hands, lower body/sole and game files were not edited. The source coat's retained 6 mm inward wall and even-offset setting were preserved.

To combine, load `append_backplate.py` in the root-owned assembly and call `append_backplate()`. It does not save. Keep the returned owned-object list for combined clearance checks; do not re-enable the replaced backplate/neck/hem overlay meshes.
