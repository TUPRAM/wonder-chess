# AQ1 candidate r06 motion review

**All 154 unique rendered samples were visually inspected through eight chronological contact sheets, with 13 original 512px frames inspected separately.** This is a frame-sequence review, not continuous video playback. The images are real EEVEE renders of candidate `ada_forms_r06.blend`, `AQ1_EDITABLE`; they are not generated reference images, baked export material proof, or Unreal screenshots. Source SHA-256: `a567e3d669d181469b443fbe3794391b88ae479bc05d9c2e8ce4371122c90634`.

## Coverage

| Clip | Authored frames at 60fps | Continuous render samples at 20fps | Total rendered samples viewed |
|---|---:|---:|---:|
| Idle | 1–121 | 41 | 41 |
| Move | 1–61 | 21 | 21 |
| Attack | 1–40 | 14 | 16 |
| Active | 1–37 | 13 | 15 |
| Hit | 1–25 | 9 | 9 |
| Defeat | 1–61 | 21 | 21 |
| Victory | 1–91 | 31 | 31 |

The four additional samples surround Attack 16 and Active 19. All 436 integer-frame measurement records were parsed. `review.json` lists every reviewed sample and its source hash. No mutation of the candidate, its clips, or capture files was performed by this reviewer.

## Findings

1. **Defeat skirt intersection:** at 28, 37, 46 and 61 the brown thigh forms emerge through the ivory skirt rather than under a natural lifted hem. The shape becomes a visibly cut-out white skirt over large exposed thighs. This is the largest observed deformation defect and requires the pending candidate skinning/coverage fix.
2. **Hair crown opening:** Defeat 28 onward exposes a warm skin patch at the crown, especially 46/61. Cover the cranium fully under black hair before acceptance.
3. **Hit torso transition:** Hit 7/10/13 exposes a broad triangular ivory wedge beneath the tilted breastplate and above the dark waist. It reads as separated stacked torso pieces. The outer shoulder and upper sleeve also retain a stiff, angular transition. This view does not prove a mesh hole; review coverage and skinning.
4. **Small Move floor penetration:** the quantitative records show source support-foot minimum Z = **-0.001665 m at frame 54**; negative values occur at frames 7–10 and 52–55. These dips are not obvious in the small render. Do not round them into zero; compare against the intended floor/contact tolerance. Other clips' support minima are approximately +0.012 m.
5. **Defeat grip/thigh proximity:** 37/46/61 places sword guard and hand near the upper thigh/tabard edge, while shield-side fingers become visible as open arcs away from the back grip. Side/back closeups are needed to establish full finger contact or collision. Do not call this a confirmed penetration based on this view alone.

## What reads better / remaining visual limits

- Attack 16 visibly presents the blade extending horizontally outward from the hand; the blade cross-section reads more distinctly than a thin flat slab in this light. The grip remains attached throughout the sampled sequence. The small motion is still predominantly forearm/wrist rotation rather than a large body-led slash; timing was preserved, and this review does not request a gameplay change.
- Active's shield lifts beside the head and the face remains visible in this three-quarter sequence. At frame 19 the face is fully clear. The scalar eye-height-minus-shield-top reaches -0.156684 m at frame 9; that scalar is world-Z only and is not a camera occlusion test.
- Move 16 and 46 visibly alternate lifted and support legs. No gross floor cut or equipment detachment appears in the sampled views; the small measured floor dip remains open above.
- Idle and Victory preserve the same recognizable navy shield, gold crest and pale armor. Victory's restrained shield lift is visible. The pauldrons still read as domed caps, hands as stacked simple finger bands, face as smooth with a broad stare, and skirt as smooth untextured panels in this source-material pass. These forms are not yet equivalent to the approved detailed reference.

The measured source root translation and maximum pose-scale error remain zero across all 436 frames. The measured sword wrist-relative axis error is zero. Those measurements do not establish collision-free geometry, finger contact, surface finish, aesthetic approval, or in-engine import correctness.

## Status

Open defects have been sent to the parent owner for the bounded r07 correction. No r07 or later source is reviewed here. Continuous playback, audio, alternate camera inspection, baked runtime material motion, Unreal candidate proof, and **Pram's art approval remain pending**. The automated record's quantitative pass is retained as its own narrow result and does not approve this art.
