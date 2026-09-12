# BW4 independent upper-armor candidate — ART_REVISE

The new front plate, side returns and right shoulder construction are executed editable geometry. The front plate is visibly cleaner than frozen BW1 r003 and clears the padded coat in the sampled local motion test. The upper-back plate, shoulder cap and lowest lame still cross the coat. This candidate is retained at **ART_REVISE**, after one initial construction and two substantive corrective revisions. No human approval, game integration or reusable recipe is claimed.

## Retained changes

- A new 110-vertex breastplate cage establishes a single chest surface, a restrained central plane break, a shaped neckline and a lower edge above the buckle. Separate edge returns, side panels and shoulder bridges replace the old implied torso attachments.
- An independently built backplate follows the padded torso more closely than the old floating shell, but its upper armhole corner still fails clearance.
- One anatomical-right cap has an asymmetric flattened crown, rear fullness, a front cutout and two separately editable overlapping lames. Each steel part remains rigid under its declared attachment.
- A separate copy of the continuous coat receives a local right shoulder/underarm allowance of up to 9 mm. Its topology and weights remain intact. The sleeve remains continuous in the inspected raised/reach views; its flared cuff is retained unfinished context.

The cuff/bracer and fixed-hand work belong to the main task. This independent armor file does not change them. The opposite shoulder, lower costume, head and other BW1 pieces are explicitly retained context, not newly completed work.

## Actual geometry and motion findings

Every integer frame of the saved **97-frame MPFB authoring diagnostic** was evaluated against the coat. The test reuses the executed BW2 segment/triangle query, after BVH broad-phase pairing. These are transverse triangle crossings, not a full continuous collision proof; coplanar overlap, tangencies, containment and unrelated part pairs are not certified.

| New shell against coat | First detected frame | Maximum confirmed triangle pairs | Finding |
|---|---:|---:|---|
| Breastplate | None in 1–97 | 0 | Front enclosure improved in this bounded test |
| Backplate | 1 | 84 | Upper-back/armhole fit fails |
| Right cap | 1 | 372 | Medial/rear crown cuts into padded shoulder |
| First lame | None in 1–97 | 0 | This pair clears in this bounded test |
| Second lame | 20 | 95 | Lower edge cuts the sleeve during elbow movement |

Counts are triangle-pair observations, not numbers of distinct artistic defects. Reproduction examples in metric world space:

- Backplate at frame 1: approximately `(0.15646, -0.14999, 1.44858)` m.
- Cap at frame 1: approximately `(0.17947, -0.11021, 1.51163)` m.
- Lowest lame at frame 20: approximately `(0.33652, 0.02313, 1.30484)` m.

The profile still shows excessive forward chest projection. The lifted lower edge now clears the buckle, but exposes unfinished underlayer gaps above the belt. The collar/neck saw edge and broad cuff opening are retained BW1/context defects. Independent visual review agrees these remain important construction issues.

## Evidence and preservation

Authoritative work: `ada_armor_work.blend`. Frozen final: `ada_armor_checkpoint_FINAL_ART_REVISE.blend`. Images beginning `review_final_` and the matched `matched_r003_` images are authoritative. Earlier `initial_`, `rev1_`, and `final_` captures are retained development evidence; `final_` is the intermediate portion of the second correction before contemporaneous waist feedback was incorporated.

`captures/BW1_r003_vs_BW4_FINAL_ART_REVISE.png` compares actual r003 and final geometry with identical saved front, three-quarter, profile and back cameras and lighting. The baseline restores the original coat on a duplicate for the render. The cage diagnostic exposes the actual low-density source edges. Neutral and reversed lighting, isolated plates, sleeve-only poses and a labeled full-body context are included.

`motion/BW4_ARMOR_AUTHORING_DIAGNOSTIC_NOT_GAME_CLIPS.mp4` contains all 97 native source frames at 800×800, 24 FPS. A fresh Blender process reopened and decoded all 97 frames; nine temporal samples were inspected alongside the full-resolution stills. This is not a claim that the seven canonical clips were tested. Pose labels, camera and source hashes are in `motion/source_record.json`.

Save/reopen verification matched every candidate mesh signature. The 55 retained original BW1 mesh records, including positions, faces, stored weights and shape-key coordinates, match the immutable r003 source. The 38 duplicated context meshes own their mesh/key data; candidate rig and action are independent. Source r003 retains SHA-256 `03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8`. Coat and leggings retain their actual positive thickness values of 6 mm and 2 mm with offset −1 and `use_even_offset=False`. The initial candidate-only parent-inverse copy error was diagnosed and corrected before the valid initial construction review; the failed setup file is retained.

## Specific next intervention

Keep the improved breastplate cage and side-return construction. Before any further detail, fit a local padded shoulder form target through the recorded rest, elbow and raised states, then reconstruct the cap's medial/rear opening and the backplate's upper armhole corner against it. Shorten or recut the lowest lame at its measured sleeve crossing rather than increasing its radius everywhere. A separate controlled torso-profile adjustment must reduce forward projection while preserving the demonstrated front clearance. The waist underlayer needs its own enclosure correction.

That is a new localized fit/construction task. The two-revision allowance for this method is exhausted; no additional offset or smoothing pass was performed. The 163-bone MPFB authoring attachment has not been converted to the canonical 27-bone rig. All seven actual game clips, transitions, Unreal import/reimport, gameplay, other-body replay, materials/bakes and human approval remain **NOT_RUN** for this armor candidate.
