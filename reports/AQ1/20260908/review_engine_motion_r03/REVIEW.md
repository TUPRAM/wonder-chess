# Unreal candidate r03 visual motion review

**All 150 unique real Unreal captures were inspected**, in twelve chronological contact sheets, with eight original-resolution hero crops. This is frame-sequence inspection, not continuous video playback. Coverage: Idle 41, Move 21, Attack 14, Active 13, Hit 9, Defeat 21, Victory 31. Original captures and all source hashes are retained; no pixels were retouched.

## Actual comparison

`matched_idle40_comparison.jpg` compares the canonical baseline, pale r01, gray r02 and corrected-color r03 at matching gallery framing. R03 restores dark navy shield/cloth, warm brown skin, black hair, gold crest/clasps and ivory cloth. Canonical-before to r03 also shows changed geometry: curved shield and raised crest, convex chest/curved armor, shaped knee/foot armor and actual facial/hair shaping. These observed changes do not constitute approval against the user's more detailed reference. Domed cap shoulders, uniform upper sleeves, simple skirt panels and stacked glove fingers remain schematic.

The gray r02 comparison in this task covers only Idle 0 and 40, not all 150 r02 frames. Baseline and r01 full-sequence reviews remain in their earlier review folders.

## Important transient shading finding

The dark blue/gray nose and blotchy chest/shield shading are strong in **Idle captures 0–8**. Hair has pale streaks and clasps are muddy. At **capture 9**, the appearance changes abruptly to a smoother warm face, black hair and clear gold clasps, then remains substantially clearer through Idle 40. See `idle_shading_transition.jpg`, which uses actual crops of captures 0/7/8/9/10/40.

The change is between recorded animation times 0.450 and 0.500s, around 2.111s of capture wall time after the first frame. Capture proceeds slower than playback; these clocks are distinct. This is evidence of a temporal startup appearance problem, not proof of its cause. Texture/shader readiness or streaming is worth investigating before treating frame 0 as the settled normal/AO result. Do not remove the bad frames or claim a complete fix without a fresh readiness check. A final material revision remains under owner diagnosis.

## Persistent geometry/contact observations

- **Move 2–8:** an angular ivory patch enters the lower navy tabard beside its slit, most obvious in `Move_extreme_05.png`. R03 color clarity makes this defect more obvious. Repair actual layer separation or weights, not the screenshot.
- **Hit 1–5:** the leaning chest exposes a broad ivory crescent above the belt (`Hit_extreme_02.png`); armor/waist still read as separated stacked pieces.
- **Active 3–6:** the frontal gallery camera shows shield over the face; `Active_extreme_04.png` hides the face completely. This is the same view-dependent concern seen in r01. Earlier Blender three-quarter clearance does not establish universal clearance.
- **Defeat 10/18:** skirt/tabard lifts and reveals thighs; the older gross Blender r06 skirt cut-through is improved, but panels remain stiff. Pale dotted seam/patch lines persist near thighs/knees. At 18, shield-side finger arcs are visible above/back of the handle; other-angle contact review is required. The crown's former skin aperture is not visible in these engine frames.
- **Attack 4:** blade extends horizontally, remains attached and has a readable point/guard. Wrist/guard geometry still warrants a close review; simple finger stacking is visually apparent.
- **Feet:** Move shows alternating stance/lift; no gross floor cut is obvious in these captures. No actual Unreal contact geometry was measured by this lane, so this is not a zero-penetration pass.
- **Defeat 18→19:** gallery loop returns from held crouch to standing. It is not gameplay resurrection. Small moving-edge ghosts remain capture observations, with no numerical performance inference.

## Provenance and acceptance boundary

The executed `reimport-r03.json` record reports source SHA `cd6bb6ddb3a54aaa15be3112a804caf0820f9ad1162b7cb8ee345f646bef8a67`, reimport true, same mesh/skeleton identities true, and protected scope unchanged. This review reads that record; it does not independently validate placed actors or override the importer’s pending visual status. The engine catalog digest remains `95509d001ca0e6c55fa64a616df6e2e9a01a3809a9b9c82d9bd0a725dad3a1ec`.

The owner reports geometry/actions unchanged during the material revision; these frames are retained as geometry evidence. A later material revision requires its own material appearance/readiness check. Continuous playback, audio, candidate board/crowded camera, alternate angles and **Pram's art approval remain pending**. No numeric art score or finished-hero approval is issued.
