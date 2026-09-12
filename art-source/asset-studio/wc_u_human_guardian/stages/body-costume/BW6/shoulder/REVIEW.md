BW6 anatomical-right shoulder â€” executed local review, ART_REVISE

Retain the r003 steel assembly as a visibly improved authoring candidate. The broad supported cap, raised medial lip, connected overlap rhythm and recut lowest anterior return are better than the BW5/BW4 shoulder. Do not append the failed under-straps, mirror this onto the other side, issue forms approval, or claim runtime compatibility.

Retained editable checkpoint: C:\Users\iputu\Documents\Wonder Chess\art-source\asset-studio\wc_u_human_guardian\stages\body-costume\BW6\shoulder\ada_bw6_shoulder_checkpoint_r003_ART_REVISE.blend
SHA256: c5bcea67a5ce0523948be2c2362c998e6864a8f7dea214fd5d773a8cbe273163
Editable work: C:\Users\iputu\Documents\Wonder Chess\art-source\asset-studio\wc_u_human_guardian\stages\body-costume\BW6\shoulder\ada_bw6_shoulder_work.blend
Independent combined review: ada_bw6_shoulder_r003_combined_review.blend.
Append: operations/append_bw6_shoulder_r003.py, append_bw6_shoulder(scene, rig). It loads precisely 3 steel mesh objects and 8 native helpers. apply_lowered_support_pose() is the companion to the exact frame 1 +/-32-degree anatomical lowered diagnostic. Its tuple-index typo was fixed and the corrected helper was executed successfully (records/r003_body_and_lowered_helper.json). This remains an asset-specific finite authoring implementation.

What changed and why

The initial new 91-vertex cap control surface replaced the failed inherited shell. The cap has its own clavicle/shoulder support and a medial strap pivot; it no longer drops with the entire upper arm. Secondary rigid hinge poses provide the tested rear-root clearance. A rejected broad rotation-driver extension is preserved separately.

The r002 numeric-clear version still looked detached because both lower lames followed the upper arm while the cap stayed supported. The new rest-corrected cap-relative anchor couples both lames to the cap/arm support with a common 0.85 cap influence, preserving the lower plates' relative arrangement. The first mixed .85/.50 support was rejected for mutual intersections. Only the measured anterior return of the lowest lame was recut (rows 1–3, columns 11–12 were the failing region), instead of enlarging the entire assembly. A final 0–4 mm medial-rear cage fit addresses the updated collar without changing the rigid suspension.

The three steel meshes remain Subdivision 1, 3 mm inward Solidify with even-offset disabled, and a 0.4 mm bevel. No canonical bone, shared action, body, cloth, hair, head, or game asset was edited by this shoulder lane. Root-supplied body/coat context was appended independently and Armature references remapped.

Evidence and limits

| Check | Executed result |
|---|---|
| Final geometric revision: all 97 integer frames, 8 earlier critical half frames, lowered pose | Evaluated steel/coat crossings 0; plate/plate crossings 0; raw/evaluated nonadjacent self-crossings 0. Raw cap/collar retains 4 pairs at frame 86. |
| Reopened combined r003: 35 additional half-frame checks 54.5-88.5 | Evaluated steel/coat, plate/plate and tested self-crossings 0. Raw cap/collar 4 pairs at 85.5 and 86.5. |
| Reopened combined r003: steel/body | All 97 + lowered:0 tested crossings against BW6_BodyFit_Candidate. |
| Steel versus new torso shells/turned neck borders | Seven anchor poses1,25,49,73,78,86,97:0 tested crossings. |
| Independent append replay | Evaluated coordinates match exactly at all seven anchor poses; max coordinate error 0.0 m. |
| Rigid suspension measurements | Predeclared proximal points travel up to 8.43 mm for L1 and 10.55 mm for L2 relative to cap; world-transform scale deviation < 6.2e-6. This specifies proposed slot/strap allowance, not a completed physical strap. |
| Cap-eave / first-lame distance screen | 6.60–24.46 mm across all 97 + lowered, versus earlier r002 maxima around 51 mm. Nearest-surface distances do not themselves prove coverage.|
| Motion | Native Blender rendered both fixed views of all 97 frames at 24 fps. Encoded MP4 reopened in fresh Blender; all 97 frames decoded. All five chronological sheets viewed, plus native encoded frame 73. No real-time playback claim. |

The transverse query confirms BVH candidate pairs with segment/triangle intersections. Self pairs sharing vertices are excluded; tangency, coplanar overlap, containment, and mathematically continuous collision freedom are not established. These are the MPFB authoring diagnostic frames, not Idle/Move/Attack/Active/Hit/Defeat/Victory game clips. The authored cap support action must not be described as a general pose solver.

Final root coat source: C:\Users\iputu\Documents\Wonder Chess\art-source\asset-studio\wc_u_human_guardian\stages\body-costume\BW6\armor\ada_bw6_torso_simple_clamped.blend
Source SHA256: 296fcd3802eea49bf5569d9ddc0f62c11db3be751f181b74c35189b41bdb49a5
The root owner explicitly retained this garment at ART_REVISE for coat self/body problems. Those are not cleared by the shoulder checks. The supplied context shows pinched shoulder/underarm cloth, unfinished collar and torso closures; those were not edited or approved here.

Actual visual review

Viewed native r003_clay.png, r003_reversed_clay.png, r003_actual_cage.png, the matched baseline comparison, all five review/r003/chronological_dualview_*.png sheets (97 decoded frames), and motion/r003/decoded/frame_0073.png. Also viewed local shared-support/recut lowered and raised closeups. The cap and lower lames keep a coherent rigid silhouette in the inspected motion, with no visible plate spikes. The leading upturned lip and nested edges are a meaningful improvement. Remaining visual issues are a broad dark opening under the lateral cap edge, no accepted visible attachment/closure construction, and a still smooth broad cap that needs the reference's restrained structural edge treatment after support is resolved. New collar/coat defects in context are separately attributable to root work. No human approval was recorded.

Comparison uses the same saved cameras and lowered skeletal pose, but the torso/coat context has deliberately changed between BW5 and BW6. It is a shoulder comparison, not a claim that every differing pixel is caused by shoulder editing.

Movie: motion/r003/BW6_SHOULDER_DUAL_VIEW_AUTHORING_NOT_GAME_CLIPS.mp4
Movie SHA256: 7b9022528fc61cae5594932660c2a2d50cb93c06693bf5aecfd9fe3ee5aa86f8
Dimensions 1280 × 640, 97 frames, 24fps. Source binding and decoded hashes: motion/r003/source_record.json and video_verification.json.

Separate under-strap study â€” failed, do not append

Frozen failure: C:\Users\iputu\Documents\Wonder Chess\art-source\asset-studio\wc_u_human_guardian\stages\body-costume\BW6\shoulder\ada_bw6_shoulder_understrap_checkpoint_ART_REVISE.blend
SHA256: 0ed7c3b8fe8104836af365df2e31bf2fdb16c79d32db965897c70117ba0cf43c
Initial four-station straps cut through the plate overlaps. A twelve-station route measured against actual steel inner sections improved positioning, then a pre-bent path before the two overlap edges reduced those crossings. These used one initial construction and two substantive routing corrections. They did not solve the supported range.

The final 119-pose check (97 integer, 21 half frames 68.5-88.5, lowered) reports all crossings with no terminal exemptions:

| Strap | First-lame conflicts | Coat conflicts | Body / tested self |
|---|---|---|---|
| Rear | 24 sampled poses, worst 28 triangle pairs|38 sampled poses, worst 112|0 / 0|
| Front | 55 sampled poses, worst 60 triangle pairs|Lowered only, 4 pairs|0 / 0|

Both straps clear the cap and lowest lame in those samples. Those partial successes do not approve the straps. Native reopen reproduces final strap coordinates exactly at frame 56. Viewed captures/strap_failed_exposed_lowered.png and strap_failed_exposed_56_cage.png, with steel intentionally hidden and Hook deformation retained, exposing the failed route rather than concealing it. The support polyline varies about 7% in length; this was an authoring deformation test, not a validated inextensible leather/slot mechanism.

Recommendation

Continue integration review with r003 steel only. Preserve the clean cage and improved plate rhythm. Clear the remaining raw medial cap/collar overlap locally. The under-straps need a new connection construction: explicit sliding attachments at verified rigid anchors, or shorter independent straps joined through a slot, with its free path solved against the posed sleeve. Repeating inward offsets on the same Hook ribbon is not supported. Keep the strap study ART_REVISE and keep independent torso/armor work moving. Seven game clips, transitions, skeleton/export compatibility, Unreal import and runtime checks remain unrun in this lane.
