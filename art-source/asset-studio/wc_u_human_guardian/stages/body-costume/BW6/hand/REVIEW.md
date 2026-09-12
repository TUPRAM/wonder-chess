# BW6 anatomical fixed-glove study — ART_REVISE

2026-09-11. Local Blender 5.1.1 execution. The new palm/thenar and phalangeal construction is retained as an improvement over BW5, **not a finished production grip or forms approval**. The primary armor assignment remains independent.

## Retained output

- Editable work: `ada_bw6_hand_work.blend`.
- Frozen checkpoint: `ada_bw6_hand_checkpoint_ART_REVISE.blend`.
- Both SHA-256: `12831f6a3d9f89c604bbdbfa0db72878a372bc5b5c19ec0fc706d87272ad3cf1`.
- Active object: `BW6_ClosedGlove_Retained`; independent mesh data with one user, one level of review subdivision, no armature or game binding. Previous failures and the new sculpt targets remain separately hidden. Only the candidate and selected sword belong to the visible study allowlist.

Open `captures/BW5_vs_BW6_ANATOMICAL_HAND_ART_REVISE.png` first. It uses the same six preserved camera definitions, with native pixels from the source-bound BW5 and BW6 renders. The displayed comparison includes palm, oblique and side views. `BW6_CAGE_AND_REVERSED_LIGHT_ART_REVISE.png` shows the actual cage and lighting diagnostic; `BW6_ACTUAL_GRIP_CHANNEL_SECTIONS.png` shows evaluated glove/hilt cuts.

## What actually changed

BW5's flat fan-shaped palm, repeated circular finger profiles and hook-like thumb were not tightened or smoothed. A separate volumetric target was constructed from a closed palm surface with independently shaped thenar, hypothenar, thumb-base and knuckle masses. Four distinct three-phalangeal gestures used oriented broad form blocks with rounded edges. These masses were voxel-unified as a **form target**, then reconstructed into an editable surface using Blender's native QuadriFlow. The target's temporary cuff cap was removed, and a bridge restored the exact original 20-point wrist opening.

The result gives the palm and thumb base actual volume, removes the long fan creases and differentiates joint planes. It also exposes the limitations of this block-based form method: long straight phalangeal faces and a bulbous thumb do not yet read as a convincing Ada glove.

| Bounded construction | Executed outcome |
|---|---|
| Initial open-source palm cut/cap target | Rejected. Incomplete cuts/caps produced slab-like transitions. Preserved separately. |
| New closed anatomical-volume target and initial editable reconstruction | Clearer mass construction, but thumb/index joined and little-finger hilt intrusion reached about 2.52 mm evaluated. Raw/evaluated self-crossing pairs: 4/6. |
| Correction 1: separate thumb tip, revise little MCP/proximal route | Raw/evaluated self crossings reached 0/0. Remaining little distal pad penetrated the hilt about 1.55 mm evaluated. |
| Correction 2: revise ring/little distal form target and remesh | Hilt cleared, but whole-hand QuadriFlow introduced 24 raw/27 evaluated self-crossing pairs in previously sound web/knuckle regions. Rejected. |
| Changed reconstruction operation: retain correction-1 cage and transfer only two distal regions | **Retained.** 166 explicitly bounded ring/little distal vertices transferred to the improved target in the same metric rest space. Sound palm/thenar topology, other digits, wrist and equipment stayed fixed. Raw/evaluated self and equipment queries returned zero confirmed crossings. |

The little MCP was deliberately moved forward on the candidate to create a viable proximal route; this is an art/fitting decision, not a claim that the source joint dimensions were exact reference measurements. No finger-bone scaling, pose search, handle movement or shared rig change was used. The second whole-hand retopology failure was not accepted merely because its hilt query passed. No further contact-coefficient tuning was performed.

## Executed checks and limits

`records/retained_geometry.json` contains the full raw/evaluated triangle queries and signed samples against the **actual selected octagonal hilt**, with guard and blade included even when visually hidden.

- Cage: 1,999 vertices / 2,019 faces. Evaluated: 8,035 vertices / 16,028 triangles. These counts describe authoring geometry, not quality or a runtime budget.
- Exactly 20 intended wrist boundary edges; no other nonmanifold edges, loose vertices or zero-area faces reported.
- Raw and evaluated: **0 confirmed nonadjacent transverse self-crossing pairs; 0 hilt, guard or blade crossing pairs; 0 sampled inside-hilt vertices**.
- Closest sampled hilt distance: **1.048 mm raw / 1.127 mm evaluated**. This establishes sampled separation, **not holding contact**.
- Native save/reopen of both files passed. Exact wrist-position error: **0.0 m**. Mesh independence, source-equipment geometry/transforms, six camera matrices/scales and work/frozen geometry equality were checked.

The crossing query excludes shared-vertex pairs and does not classify all coplanar/tangent cases. Vertex-distance samples do not bound every point of every triangle. The intentional wrist opening means the glove is not a closed solid. No mathematically complete collision-free claim is made.

New provisional contact patches were declared using anatomical target segments, bounds and palmar normals before scoring; no BW5 evaluated IDs or favorable nearest-vertex samples were reused. Their color views are `provisional_pad_regions_*.png`. Patch boundaries, especially thumb/index proximity, still need a dedicated anatomical correspondence review before fitting. None passed the prior −0.5 to +1.0 mm contact band:

| Evaluated patch | Samples | Minimum / median / maximum distance (mm) | Samples in band |
|---|---:|---:|---:|
| Index | 43 | 1.27 / 4.58 / 8.58 | 0 |
| Middle | 51 | 1.32 / 4.96 / 8.32 | 0 |
| Ring | 60 | 2.71 / 4.18 / 6.74 | 0 |
| Little | 68 | 2.81 / 4.20 / 7.12 | 0 |
| Thumb | 60 | 2.16 / 4.50 / 10.44 | 0 |

These regions differ from BW5, so their medians are not a like-for-like improvement score. The whole-surface clearance result remains separate from the failed contact screen.

## Remaining defects and next action

1. **Major — thumb/thenar shape.** It reads as a large rounded knob. The opposing distal thumb plane and pad contact are not sufficiently clear. Separate the thenar mound from the thumb's two phalanges through deliberate local surface construction; preserve the now-rounded web.
2. **Major — mechanical digits.** Long straight faces and parallel C-shaped routes remain. Knuckles need more specific widths, asymmetry and transitions into the palm. Do not tighten repeated ring profiles or globally remesh the sound hand again.
3. **Major — loose contact.** The glove surrounds the hilt but the measured surface patches do not establish a firm hold. First establish convincing distal pads/opposition; then fit the reviewed patches against the unchanged hilt with whole-surface checks.
4. **Unproved — wrist/cuff and game use.** The exact wrist interface is preserved, but its new bridge includes long triangles and has not been reviewed in a forearm assembly or deformed through game motion.

**Recommendation:** retain this anatomical construction as the next editable starting point; perform a focused thumb distal-plane and knuckle/pad surface intervention. Preserve successful regions and transfer local targets into the existing cage. The current bounded assignment stops at **ART_REVISE**. It does not block torso, shoulder or other independent work.

## Preserved sources and unrun gates

BW4 frozen, BW5 frozen and BW5 work match their preexisting hashes in `records/reopen_and_preservation.json`. The selected 30×26 mm hilt, 110 mm exposed length, unchanged blade/guard and their registration remain exactly equal to BW5; the full handle extends under the guard and is about 154.4 mm long. Master MPFB body/keys, canonical skeleton/actions, head/hair, body/armor, references, prior candidates and game files were not edited in this lane.

Game bind-space conversion, seven clips/transitions, wrist deformation, Unreal, reimport, runtime contact, recipe replay and second-body fitting are **NOT_RUN**. No new movie was generated for this rejected static form; the saved cameras, actual clay/cage/section images and source-bound queries are the evidence. No human approval, canonical replacement, production release or reusable-recipe promotion was issued.

The bounded anatomical research used the primary author's indexed [Proko hand-muscle lesson](https://www.proko.com/course-lesson/how-to-draw-hands-muscle-anatomy-of-the-hand/) for distinguishing palm muscle masses. Direct page retrieval timed out; no full-lesson or video-viewing claim is made. The original local MPFB-compatible glove supplied actual proportion and wrist observations. No asset download, private-art upload, purchase or new modeling toolkit occurred.
