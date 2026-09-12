# BW3 collision-first thumb review

**ART_REVISE — the bounded trajectory method was executed and stopped. This is an editable thumb-approach study, not a closed hand, usable sword grip, approved asset, or reusable hand recipe.**

The final glove avoids the detected handle tunneling and self-crossing seen in the earlier attempts. The underlying body still folds at the thumb web, the glove intersects that body locally, and the thumb pad faces away from the handle with a large gap. These failures block extension to the other fingers and real equipment. The initial construction and two corrective iterations are retained; the counter was not reset.

## Saved candidate and protected sources

- Work: [ada_bw3_grip_work.blend](ada_bw3_grip_work.blend), SHA256 `cf15051c9d31885b1c6c4cd2d97de70716f87dbe0e4d3cc667f24a00413d664c`.
- Frozen: [ada_bw3_grip_checkpoint_r001_ART_REVISE.blend](ada_bw3_grip_checkpoint_r001_ART_REVISE.blend), SHA256 `d195b2870e7974665efd3ae03dd3ac88dc5ba2b8a7dbfcc76accbf8b4de3ac60`.
- Immutable C render/audit input: [thumb_route_C_final_method_input.blend](thumb_route_C_final_method_input.blend), SHA256 `2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d`.
- Active scene: `BW3_COLLISION_FIRST`, frame 25; action `BW3_C_ExternalApproach_ART_REVISE`.
- Candidate IDs: `BW3_Derived_Rig`, `BW3_Derived_Body`, `BW3_Derived_Glove`, `BW3_FixedHandFrame_R`, `BW3_Locked_Handle_28mm`.

Native Blender 5.1.1 reopen verified independent mesh, rig, action, camera and body shape-key data, remapped armature targets, and the single wrist -> holder -> fixture chain. The body retains 19,158 indexed vertices and 44 keys (the 38 original keys plus the six existing BW1 additions); the glove retains 2,294 base vertices and its original evaluated contact correspondence. The C action uses LINEAR interpolation. Normal review subdivision is level 1 / render 1. The unchanged BW2 fixture is 28 mm diameter, 109 mm total span and 105 mm usable span; the original pad-map intent and -0.5 to +1.0 mm band are retained. No mesh, weight, rest-rig, shape-key or subdivision correction was made in this run. The modeling change was a staged thumb trajectory and joint-flexion distribution on the independent candidate.

All 498 recorded BW2 files and 62 earlier protected-file checks remain unchanged. Within each reopened candidate, all 69 retained master meshes, their modifiers, the rest rig, three original actions and 110 original object hierarchies match the baseline records. The approved reference, original MPFB controls, head/hair work, sole, retained garment Solidify fixes and game source/skeleton were preserved. The initial unsaved live frame 9 state was recovered separately and proved to contain no asset-data changes relative to saved BW2.

The final work/frozen files differ from the C evidence input in review/UI state. Their candidate source data, action curves, modifiers and hierarchy match exactly; evaluated geometry and fixture matrices also match at 10 recorded poses. See [reopen and preservation](records/reopen_and_preservation.json).

## Diagnosis and executed method

The frozen BW2 diagnosis identified the **distal thumb** as the surface entering the cylinder: evaluated glove entry first appears at 3.50, exceeds0.5 mm at 3.75, and reaches about 13.9069 mm at 14. The same failure occurs with the other fingers explicitly OPEN. In the raw body, thumb/palm crossing already begins at 11.25; the evaluated glove first crosses at 15. Middle/ring crossing is separate and begins at 16.25 on the evaluated glove.

This selected a trajectory intervention before contact fitting. The thumb was given intermediate clearance and sweep poses, then flexion, with the other digits OPEN. Existing small-angle probes were reused, and one reversible proximal-Y probe was restored exactly before the last correction. No whole-hand angle search, finger scaling, distal axial-twist shortcut, fixture repositioning or higher subdivision was used.

| Executed attempt | Change | Actual limitation |
|---|---|---|
| A — initial external route | CMC clearance, then sweep, then MCP/IP flexion; removed the old inward-Y/distal-Z construction | Glove first enters the handle between 15.5–16; endpoint vertex penetration 13.312 mm and 51 self-crossing pairs. The pad itself looks close, demonstrating why pad-only fitting is insufficient. |
| B — correction 1 | Maintained CMC clearance through late flexion | Glove handle entry delayed to 20.5, but endpoint penetration 13.251 mm remained. First entering surface was distal thumb back/side, not the declared pad. The body cage also folded during the base sweep. |
| C — correction 2, retained | Changed the proximal sweep plane using the measured control response and reduced late MCP/IP flexion | Glove clears the sampled handle/self tests, but the body web still folds. Thumb pad is 27.59–31.64 mm away and faces away from the fixture. This is a partial approach/posture, not successful opposition/contact. |

A and B remain separate frozen failed experiments. The evidence does not establish that the existing web weights or rest surface are adequate simply because the glove looks smoother.

## Final C findings

All 145 integer frames were evaluated on both body and glove, in the normal evaluated state and armature-deformed base cage. Matched quarterframe checks at 13.25, 13.50, 13.75, 18.25, 18.50 and 18.75 bring this to 604 unique surface-state evaluations. The separate body/glove fit query covers 145 integer frames.

| Requirement | Result |
|---|---|
| Glove self-crossing and whole-surface handle query | No detected transverse self-crossing or ideal-cylinder penetration on the tested raw/evaluated glove states. This is a limited query result, not complete hand acceptance. |
| Underlying body web | **FAIL.** Raw cage first crosses at 13.75 (13.5 clear); evaluated body at 19 (18.75 clear). At 25, raw body has 9 within-thumb crossing pairs; evaluated body has 14 pairs: 9 palm/thumb, 4 within-thumb and 1 palm/palm. |
| Body/handle query | No detected ideal-cylinder penetration in the tested body states. |
| Body/glove fit | **FAIL.** OPEN already has 137 cross-object pairs, concentrated at wrist/cuff and middle fingertip. Frame25 has 163: 127 in the wrist/cuff band, 12 middle-tip, and 24 new palm/thenar pairs. Only 42 touch exact glove boundary vertices; neither the broad cuff band nor neighboring anatomical regions were automatically exempted. |
| Thumb contact and orientation | **FAIL.** Original nine pad samples remain about 27.591–31.635 mm outside during the intended held interval, 0/9 in the original band. Mean pad normal dot direction toward the cylinder is about −0.912: it faces away. |
| Other fingers | Intentionally OPEN throughout; their closure/contact and middle/ring repair were **NOT EXECUTED**. Their nonintersection in this posture is not a repaired grip. |
| Fixture stability | Preserved. Maximum sampled endpoint drift about 0.000489 mm; axis drift 0.00001532 degrees. No per-frame relocation or scaling. |
| Real sword, guard, pommel, bracer | **NOT RUN**, because the local grip failed. |
| Human approval / runtime / recipe | No human approval issued. AUTHORING_ONLY; no import, runtime compatibility, replay, second-body test or recipe promotion. |

The frame ranges were not shortened to conceal defects. Frames 1–24 retain the intended approach interval; frames 25–145 contain the retained partial thumb pose through the copied wrist/arm carrying test. They **do not satisfy held-grip requirements**. The movie states OTHER FINGERS OPEN / NOT A GRIP.

The checks use deterministic evaluated triangulation, exclude ordinary shared-vertex adjacency, and confirm transverse intersections after BVH candidate pairing. Cylinder queries include triangle interiors against the ideal capped cylinder corresponding to the unchanged 96-sided fixture; circumradius versus polygon-face radius differs by approximately 0.0075 mm. Discrete samples, near-coplanar/tangential cases, open wrist boundaries and self-crossing body surfaces do not establish continuous collision freedom or containment. Nonfinite/degenerate screens and glove/body queries are reported separately. Counts are triangle pairs for reproduction, not a severity score or a count of distinct defects.

## Images and motion

[Matched BW2/C comparison](reviews/route_C_visual/comparison_verified_BW2_thumb_vs_C_final_labels.png): other fingers OPEN, fixture hidden, same camera and lighting. The changed thumb posture is explicitly labeled; this is not a rebuilt-web claim.

The [visual review folder](reviews/route_C_visual/) contains matched saved-camera views, reversed lighting, fixture-hidden diagnostics, body/glove isolation and differentiated combined views, actual posed body/glove cages, and a closeup of the still-folded underlying web. Source/camera/render metadata accompanies the images.

[Watch the complete 145-frame diagnostic](reviews/route_C_visual/BW3_C_thumb_approach_OTHER_FINGERS_OPEN_NOT_A_GRIP.mp4). The 800×800, 24 fps movie was rendered from the immutable C input, encoded and decoded through native Blender. All 145 decoded frames passed the file check. Root inspected all 145 native frames in five unskipped sheets, plus frames 19, 25 and 97 at native resolution; live Blender playback was also operated and observed through computer use. The movie shows the incomplete approach and all carrying motion, without cutting away from the transition.

See [numerical C review](reviews/route_C/REVIEW.md), [full C measurements](reviews/route_C/route_C_results.json), [glove/body fit](reviews/route_C/glove_body_fit_results.json), [onset diagnosis](reviews/onset/REVIEW.md), and [A](reviews/route_A/REVIEW.md)/[B](reviews/route_B/REVIEW.md) failure records.

## Stop and next decision

**Do not extend C into a full grip or fit the sword.** Trajectory clearance was improved, but the required body web and opposing contact remain unsolved. The early raw-body reproducer is triangles 6361/6486 (vertices [3630,3627,3637] against [3642,3640,3211]); the evaluated-body pair is 17040/17547. A further animated-hand task needs a focused body-web/control intervention and a thumb pad-facing construction, with local weights versus rest-surface support diagnosed at the recorded crossing region. Another broad angle search or glove-only cosmetic patch is not justified. No weight/rest-surface repair is claimed here.

For Ada's game-production requirement, the [separate fixed-grip assessment](reviews/fixed_option/REVIEW.md) is now grounded in actual source inspection: the canonical 27-bone rig has no digit bones; all seven actions keep the hand/equipment rigid relative to the hand through 865 sampled half-frames. A fixed hand may therefore be the narrower production choice. **That route has not been adopted or built.** It still requires a deliberately nonintersecting closed surface, wrist integration, actual equipment fit and all seven game-animation checks. The current canonical sword handle is materially different from the 28 mm fixture; fixture success cannot establish that equipment fit.

Independent sleeve, costume, boot or gameplay work can continue under a separately scoped task. None was launched to mask this grip failure.

