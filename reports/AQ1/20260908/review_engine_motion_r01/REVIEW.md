# Interim Unreal candidate r01 motion review

**All 150 unique actual Unreal gallery captures were visually inspected**, using 12 chronological contact sheets plus one full Idle frame and eight native-resolution hero crops. This is frame-sequence inspection, not continuous video playback or audio review. Crops use source pixels only, and `contact_sheet_manifest.json` preserves original paths/hashes and the crop rectangle.

Coverage: Idle 41, Move 21, Attack 14, Active 13, Hit 9, Defeat 21, Victory 31. Source: `/Game/WonderChess/Candidates/AQ1/Ada_r01`; capture content digest `95509d001ca0e6c55fa64a616df6e2e9a01a3809a9b9c82d9bd0a725dad3a1ec`. All clips are from the real Unreal gallery at recorded 20Hz steps. This is offline capture, not a performance result.

## Material boundary

The current material is visibly pale/desaturated: skin warmth, dark navy cloth/shield and gold contrast are reduced. Reflective surfaces show broad bright gradients and visible facets. The owner is diagnosing this intermediate material; this review does not approve it or infer the precise normal/texture cause from pixels. Geometry observations below remain useful, but surface finish must be reviewed again after the fix.

## Geometry and motion observations

- **Move captures 2–8:** a sharp ivory patch intrudes through the navy tabard near the lower slit, clearest in `Move_extreme_05.png`. This is a visible costume defect requiring overlap/skin-weight review. The alternating foot lift is present; exact engine foot contact was not measured by this lane.
- **Active captures 3–6:** the frontal gallery camera puts the shield across the face; capture 4 covers the face completely. This differs from the earlier Blender three-quarter view. Keep that distinction explicit; the Blender statement cannot become a camera-independent face-clearance pass.
- **Hit captures 1–5:** a broad ivory crescent opens below the breastplate and above the belt, clearest `Hit_extreme_02.png`. Torso layers appear separated during lean.
- **Defeat captures 10/18:** thigh exposure now follows lifted skirt panels instead of the older r06 source's gross cut-through. However, the tabard/side panels remain stiff and pale seam/patch marks remain at thigh/knee edges. Hair crown skin aperture is not visible in this revision. This one camera cannot certify the back or inner costume.
- **Attack capture 4:** blade reads as a horizontal slash and stays attached to the hand. The guard/fingers remain simple, and surface/tangent appearance is not accepted.
- **Idle/Victory:** full hero and weapons stay in view. Victory's shield lift is restrained and readable. The source's domed shoulders, smooth face and simple costume still differ materially from the detailed approved concept.
- **Defeat 18→19:** the crouch jumps to standing when the gallery clip wraps; this is not gameplay resurrection evidence. Moving captures contain faint edge ghosts; this review does not attribute them or infer frame-time problems.

No final art score is issued. Continuous playback, audio, alternate camera coverage, candidate crowded-board review, corrected material/normal proof, any later revised import, and Pram's art approval remain pending.
