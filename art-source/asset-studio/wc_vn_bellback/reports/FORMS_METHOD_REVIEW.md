# Bellback B3-A forms method review

**ART_REVISE. B3-A modeled forms are incomplete. No candidate is ready for human forms approval.** Three real Blender sources and their rendered evidence are preserved. The third attempt changed the construction method, but actual pixels still fail the approved concept. Do not advance topology, UVs, materials, rig, skin, animation, optimization, Unreal import or release for these sources.

The accepted reference record is `reviews/references/accepted_398e068188b44b939e9059e5c3e1742a.json`. Its subject is the sealed r004 reference packet, not any model below. The final status check still reports brief and references `accepted_current`; blockout and subsequent gates remain pending. No approval command or prepared passing candidate was created during modeling.

## What was built and actually inspected

All three attempts ran in isolated Blender 5.1.1 background processes, build `b70da489d7f4`, using trusted local Python and factory startup. The Blender MCP scene query could not connect; the installed headless editor successfully constructed, saved, reopened and rendered the models. This is a modeling-quality limit, not a claim that Blender is unavailable.

| Candidate | Saved source SHA-256 | Actual result |
|---|---|---|
| r001 | `c20f0566dc2065e12e67cecdc28a7cbd088dc66bd8dd7a59a4392632182729f7` | Custom body loft and joined limb forms, separate hollow bell and suspension. Generic toy anatomy, large applied eyes and brows, thin bark strips, pillow-like moss. ART_REVISE. |
| r002 | `7dca34dcb88513be63894fbd5853f39c80f2155baf7b43ec2c54823b017c3496` | Smoother body and stronger legs, fitted bark plates, revised face. Independent parent review agreed that it reads as a smiling frog/plush with leaf overlays. ART_REVISE. |
| r003 | `5a2931e42bbb8523f3e84ba39f02a5ceab0b1fa31abc3e8319fcf6a1c0d6066b` | Changed method: one shaped head cage, recessed muzzle and nostrils, projected grooves displaced into the continuous organic form, applied bark/moss/eyebrow shapes removed. Ragged incisions and unresolved facial structure are major failures. ART_REVISE. |

Each source lives in `stages/blockout/<candidate>/Bellback_forms_<candidate>.blend`. Each has the actual build script, command output, model audit, front/back/left/right clay renders, three-quarter clay and material-ID renders. R003 adds face and paw closeups, isolated bell support/cavity views, a native 96-pixel preview, and twelve stationary linked instances at the runtime lab's fallback camera projection. Individual image provenance and camera settings are in the adjacent JSON files. The model audit's phrase about "applied eyebrow strips" refers to their removal in r003; no eyebrow strip object is present in that source.

## Largest observed failures

1. **Face and identity — major, shape.** The approved aesthetic reference has an aged animal face, a strong projecting muzzle, inset eyes and integrated brow planes. R003 has a flattened oval face, projecting button eyes, shallow nostrils and a thin upward-curving mouth seam. The result still reads as a smiling toy. See `r003/renders/front_clay.png` and `r003/review/face_closeup_clay.png`. Facial planes need a focused sculpt pass with inset orbits, upper/lower lid structure, muzzle projection and jaw transitions established before any detail.
2. **Bark and load-bearing anatomy — major, shape.** The third method creates broken, serrated trenches down the shoulders, limbs and torso. They look like surface damage, not continuous grown bark. Smooth inflated shoulder masses and blocky leg transitions remain visible around the cuts. See both side clay renders and `r003/review/paw_contact_clay.png`. The next method must shape broad root planes and taper continuously into the planted feet; it must not add another layer of strips or apply another point-distance groove field over the existing mesh.
3. **Bell/body relationship — major, shape and presentation.** The hollow shell and carrier are real geometry, but the huge clean bell and boxy saddle pads dominate. The visible suspension does not resemble integrated weathered wood in the concept. See `r003/renders/right_clay.png`, `r003/review/bell_cavity_and_carrier.png`, and the labeled underside/interior captures. Keep the accepted shell dimensions and mechanical clearances while revising the support's actual form transitions and the body's relationship to it. Do not compensate with an arbitrary bell shrink.
4. **Readability — unresolved.** The final crowded proxy makes the bell recognizable, but individual faces, facing direction and organic identity become weak at full board scale. The glossy dark shoulder regions in the material-ID view are also distracting. This proxy uses static copies and flat source-ID materials. It does not measure actual gameplay recognition, material quality, combat overlap, animation clearance or Unreal performance.

The positive result is limited: the four planted toes on each paw, asymmetric right branch, broad quadruped stance and dorsal-bell silhouette are present. These features do not cancel the major face and surface failures.

## Approved construction versus aesthetic likeness

The r004 construction packet specifies dimensional envelopes and mechanics. Its source hashes are `fe748c1a1229f9b6c85a8296137753d21d354ca6791f62dd7bab474d57eb4a13` for `construction_spec.json` and `f75caa3650f0360e210ee659b341e053e53a71fefcd0f69d68326b7328cdb9a8` for r003's `construction_geometry.json`. R001's raster reference remains the aesthetic target. The raster is not registered to the mathematical orthographic cameras, so no overlap score, likeness percentage or numerical volume conflict is asserted.

The approved bell profile is large: mouth Z=1.32 m, crown Z=2.20 m, mouth radii X=0.6624 m and Y=0.72 m. The body envelope peaks at Z=1.17 m. R003's actual total bound reaches Z=2.20000005 m and its front reaches Y=1.14999664 m. The r004 mechanical envelope was retained, but merely instantiating those envelopes leaves generic volumes. The concept's weathered, integrated silhouette still has to be sculpted inside the fixed contract. This run did not establish that the approved geometry and concept are irreconcilable.

R003's measured organic floor-contact vertices span X=-0.742024 to +0.742024 m and Y=-0.692520 to +0.767064 m, with Z=0. The source contains seven identification materials; it is a high-density forms study, not production topology. Exact part counts and triangles are in `r003/model_audit.json`. The cavity is open and the clapper exists; the supplementary interior views hide only the parts named in their metadata. No motion-clearance pass was performed.

The crowded camera uses the current lab source's `(0,1900,2700)` cm direction and fallback 1920×1080 viewport with a 1600×880 board region, yielding a 35.781818 m orthographic width. It does not include live Slate layout, runtime UI, actual Unreal lighting or combat. The final corrected captures are under `r003/review_crowded_aligned`; earlier captures are preserved with their floor-occlusion and half-cell-placement errors explicitly recorded. Only the final aligned captures should be used as the static board-spacing reference.

## Precise next operation and stop criteria

The retry limit has been reached. The parent explicitly authorized a third attempt only after a changed method and required a stop if it still failed. The next useful intervention is a focused creature-sculpt session by an operator with direct shape control, using the accepted references and this failure packet. Start with the head, neck and front-leg transitions in neutral clay; keep the existing mechanical bell dimensions as a separate reference object. Build the primary planes deliberately and compare front, profile and three-quarter views before adding bark detail. R002 may be a more useful volume reference than r003, but neither should be treated as approved or blindly continued.

The immediate review should reject a pass if the face still reads as a frog/plush, if bark reads as strips or torn grooves, if inflated shoulder joints remain, or if the bell support continues to read as a platform pasted onto the back. Only after these observed defects are fixed should a fresh complete packet go to the prescribed art reviewer and then Pram for the actual human forms gate. Human approval is not requested for these failed candidates.

Blender source save/reopen/render and evidence hash checks executed successfully. Visual quality failed. Human modeled-forms acceptance, production topology, UV/material acceptance, rigging, skinning, motion, optimization, engine import and packaged-game art acceptance were not run. No downstream asset or canonical gameplay content was changed by this modeling lane.
