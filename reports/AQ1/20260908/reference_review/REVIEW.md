# Ada AQ1 r07: reference and matched-render assessment

Status: a visibly improved candidate with substantial remaining reference differences. This is an agent's read-only visual assessment, not Pram's approval. The evidence does not support calling Ada a finished match for the selected illustration or starting a bulk hero rollout.

## What was actually inspected

The approved illustration in `art-source/heroes/wc_u_human_guardian/candidates/AQ1/approved_reference.png`; the `after_matched_r07` front, three-quarter, face, grip and back material renders; the `before_relinked` three-quarter, face and grip renders; and actual Unreal `engine_candidate_motion_r03/.../Idle/` captures at frames 0, 8, 9, 30 and 40. The later-frame inspection is a correction to the initial assessment based on frame 0 alone.

The before/after camera contracts are equal: the same listed camera locations, targets, orthographic scales, 900-square output, Cycles samples, AgX transform and exposure. This makes the matched Blender views useful for shape comparison. The approved illustration is a painted direction reference, not a Blender/Unreal screenshot or photometrically matched control.

## Visible improvement over the retained before asset

- The new face has a continuous nose bridge and cheek/chin transition. The old wedge nose, very coarse head outline and simple cutout mouth are visibly reduced. Separate upper/lower lips and a more deliberate hair silhouette can be seen in the closeup.
- The chest now wraps around the ribcage. The old floating flat breastplate and sharply faceted shoulder blocks have been replaced with curved surfaces. The coat, leg armor and boots have clearer continuous volumes than the old block-based silhouette.
- The shield is now visibly convex, with a peaked kite crown, shaped rim and raised sun. Its face and edge no longer read as the old uniformly extruded flat panel.
- The sword has a real central ridge and edge planes, a tapered point, a shaped gold guard and a more practical downward idle orientation. The old blade and crossguard read as broad flat extrusions.
- The right grip has a visible palm, an opposing thumb and finger curl around the handle. It is more coherent than the earlier pinched loop-like grip, although it remains unfinished in closeup.

These are improvements visible in actual renders. They do not rely on triangle count, object names or exporter success.

## Three largest remaining differences from the selected reference

1. **Face, hair and expression.** The reference's cheek, eyelid, brow and mouth relationships create a calm, alert guardian. The candidate still has a comparatively neutral, almost blank expression; the eyes read pale gray and their eyelid borders are jagged in the closeup. The nose and lips have more volume than before but still lack the reference's controlled facial planes. The large swept hair sections read as a few smooth helmet-like masses rather than the reference's layered waves and braided gathering. The rear braid exists, but the gathering above it is substantially simplified. A small uneven color boundary below the jaw also needs inspection.

2. **Armor and tailored costume construction.** The candidate is smoother, but the pauldrons still read as simple caps, the sleeve volumes as straight tapered tubes, and the broad skirt as a smooth flared shell. The reference has fitted overlapping shoulder plates, clear wrist/ankle construction, structural cloth folds, visible quilting, shaped hems and a more grounded stance. The current knee and toe pieces are particularly simple. The rear render also shows a skin-colored patch at the collar and irregular exposed ivory edges beneath the backplate; their construction or texture cause requires inspection. Adding small decoration alone would not resolve these larger form differences.

3. **Equipment finish and hand contact.** The new shield outline and blade volume are closer to the reference, but broad triangular tonal bands remain on the navy shield face, and its bright perimeter is uneven. The gold boss is rounder and more bulbous than the reference relief. At hand scale, finger bands remain repetitive, the opposing thumb has angular sections, small dark gaps remain around the handle, and the wrist/cuff connection is not convincingly finished. The guard has scattered bright/dark bake-looking marks in the closeup. The reference's fitted armored gauntlet and clean forged edge treatment are not yet reproduced.

The next detailed art revision should address those three areas in that order, using clay and material closeups. Preserve the current candidate as evidence; do not substitute an approval score for Pram's decision.

## In-engine palette and face shading boundary

The inspected Unreal r03 frames have substantially richer navy, warm skin and leather than the earlier washed-out r01 capture. Root reports both an RGB8 BaseColor delivery correction and a candidate material-slot correction before these captures; the combined result should not be presented as an isolated one-variable proof.

A localized cool/dark noisy region is visible around the nose/eyes in frames 0 and 8. It visibly clears in frame 9; frames 30 and 40 show clean warm skin and a clear nose, with stable equipment detail. The earlier assessment that this persisted as final skin shading is therefore superseded. Judge the settled material appearance from frames 30 and 40 while retaining the startup frames as separate evidence.

The remaining classification is **transient startup material/detail readiness, cause pending**. This image review does not identify whether texture residency, material readiness, another rendering transition or a different mechanism caused it. No AO source change was executed. The prior AO-versus-normal hypothesis was based on the first frame and does not establish the cause of the observed temporal transition; an AO adjustment is not warranted by that still alone. A readiness check should retain and inspect both initial and settled frames rather than relabel the first frame as final skin quality or silently discard the transient. These later frames do not change the geometric/reference differences described above.

## Actual color-encoding regression

`color_encoding_probe_r02/color-encoding-results.json` reports `PASS_ACTUAL_BAKE_SAVE_RELOAD` in Blender 5.1.1. This review verified the four recorded PNG hashes and the recorded probe/helper source hashes against the available files.

- Navy BaseColor: actual RGB8 PNG center is exactly `(37,70,107)`; encoded-byte error is 0. Reloaded texture sampled through a shader and baked into a linear readback produces a maximum linear error of approximately `0.000006591`.
- Linear ORM: floating-point authoring image and RGB16 intermediate retain `(0.77,0.83,0)` through save and shader readback; maximum linear error is approximately `0.000000763`.
- The prior r01 regression failure remains retained. Its navy PNG bytes were already correct; the failing assertion incorrectly interpreted byte-image `Image.pixels` as shader-linear data. Revision 2 uses actual shader sampling as the oracle.

This pass establishes the tested Blender bake/save/shader-reload behavior for those two samples. It does not independently certify Unreal material parity, all atlas texels, animation quality, reference likeness, or final art acceptance.
