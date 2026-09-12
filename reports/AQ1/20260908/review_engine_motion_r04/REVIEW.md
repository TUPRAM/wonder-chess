# AQ1 final Unreal gallery r04 review

All **150 actual Unreal frames** were inspected chronologically: Idle 41, Move 21, Attack 14, Active 13, Hit 9, Defeat 21, Victory 31. This is frame-sequence inspection using 12 contact sheets, eight native crop extrema and the full first Idle screenshot. It is **not continuous MP4 playback or audio review**, and it is not Pram's character approval.

The capture runs from 2026-09-08T02:30:01.140Z to 02:30:25.048Z at fixed 20 Hz game steps. Capture wall time is not a performance measurement. All seven clip records report the three actual candidate texture assets fully streamed before capture; recorded readiness waits are 0.136458 seconds for Idle and approximately 0.0063-0.0078 seconds for later clips.

The observed r03 startup shading problem is absent in r04. From Idle capture 0, the skin/nose has coherent warm color, hair is dark without pale streaks, and the crest, clasps, shield and armor have stable material boundaries. All 41 Idle captures preserve that appearance. `matched_startup_and_settled.jpg` compares actual r03/r04 Idle 0 and 40 crops. Both runs record content digest `95509d001ca0e6c55fa64a616df6e2e9a01a3809a9b9c82d9bd0a725dad3a1ec`; this is a capture readiness improvement, not a new geometry or AO revision.

| Sequence | Actual observation / remaining issue |
|---|---|
| Idle / Victory | Coherent navy, ivory, steel, gold and warm skin throughout. Shoulders remain cap-like, sleeves uniformly tubular and the face broadly staring compared with the approved reference. |
| Move | Alternating lift and stance is visible. A sharp ivory patch intrudes into the navy tabard near its slit at captures 2-8, clearest at 5. No gross floor cut seen from this view; no geometry clearance query performed. |
| Attack | Capture 4 reads as a horizontal sword slash and the blade stays attached. Fingers/grip still appear schematic rather than convincing integrated anatomy. |
| Active | Shield obscures the face during captures 3-6; both eyes and face are fully hidden at 4. The earlier Blender three-quarter clearance does not establish clearance from this frontal camera. |
| Hit | At captures 1-5 a broad ivory crescent opens between the breastplate and dark waist/belt, making the torso layers appear disconnected. |
| Defeat | Raised rigid skirt/tabard panels expose the thighs; small pale dotted seams/patch lines remain around thigh/knee at 10/18. The shield hand reads as open arcs at 18; a back view is needed to establish actual palm/grip contact. The old Blender r06 crown skin aperture is not visible. |

The Defeat 18-to-19 crouch-to-stand transition is the looping gallery preview wrapping. It must not be reported as gameplay resurrection. The visible issues above persist from r03; no new gross equipment detachment or missing character material appeared in this final sequence.

Source screenshots remain unchanged. `contact_sheet_manifest.json` records every source frame path/SHA-256 and the unaltered crop rectangle (1150,140,1840,805). Derivatives only crop, resize, assemble and label actual captures; they do not replace editor/runtime evidence.

**Status: frame-sequence review complete; visual defects and owner acceptance remain open.** No packaged game, crowded fight, continuous movie playback, audio, alternate-angle hand contact, numeric art score or budget exception approval is established by this review.
