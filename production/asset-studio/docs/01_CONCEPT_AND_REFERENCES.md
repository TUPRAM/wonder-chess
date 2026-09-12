# Phase 1 — Concept, inspiration and a usable reference pack

## 1. Intake before image generation

Declare asset kind, tactical/visual role, viewing distance, approximate size, target camera, animation needs, attachment points, material families and intended reuse. For a hero, read the game record so the visual role supports the skill. For a prop, record placement and grid/pivot interfaces. For a VFX asset, record event meaning and visibility duration.

Separate design anchors into: identity (must not drift), functional constraints (must work), style rules (must cohere), and negotiable details. For Ada the face, swept black hair/braid, protective silhouette, ivory/navy/steel and sun shield are anchors. The concept's mirrored-looking view or inconsistent trim is not a command to create contradictory geometry.

Create a part inventory before asking for many images. Each part needs a stable ID, semantic role, symmetry class, geometry/material treatment, parent attachment, dimensional relationship, authoring source, runtime export policy and risk. Example: `shield_shell`, `shield_rim`, `shield_sun_crest`, `shield_grip`, `hand_l`. Do not later find a hand by exact vertex count.

## 2. Concept prompt contract

A prompt packet is structured input, not a stream of adjectives. It contains:

- Identity and function: adult human guardian; self-protection; calm, alert.
- Visual anchors: actual face/pose/equipment reference IDs.
- Shape language: broad planted silhouette, layered rounded steel with deliberate planar breaks.
- Costume construction: underlayer, armor shell, straps, tabard, footwear; explain overlap.
- Material/palette constraints: avoid an unrestricted list of colorful materials.
- Framing: single subject, full body, equipment not cut off; desired view and pose.
- Negative constraints: no random accessory changes, extra limbs, mirrored gear, text in art, bloom hiding construction.
- Output role: creative candidate, construction candidate, closeup, material study or final 3D-derived portrait.

Generate a small exploratory set (proposed three) and select one identity. This is the creative stage. After selection, fidelity takes precedence over inventing a different hero at every view.

## 3. Required reference coverage for a hero

| Packet | Required coverage | Important restriction |
|---|---|---|
| Identity | One clean full-body three-quarter master | Artistic target, not an orthographic measurement |
| Construction body | Front, back and true side; both sides if asymmetric | Same neutral pose, scale and costume |
| Equipment-free body | Front and side without shield/sword occlusion | Keep body/costume identity unchanged |
| Head | Front, profile, three-quarter, back hair | Expression and anatomy consistent |
| Hands | Palm/back neutral, side/thumb, actual held-object grip | Open hand and grip are separate pose states |
| Torso | Front/side/back, underlayer and armor overlap | Do not expose fictitious hidden anatomy as observed |
| Legs/feet | Knee/boot front and side, sole/contact surface where useful | Keep gait clearance and scale consistent |
| Costume/hair | Major layers and locks; attachment/overlap detail | Not every thread becomes geometry |
| Equipment | Isolated front/side/back, cross-section/handle contact | Generate/author independent pieces, not fused to skin |
| Detail | Emblem, buckle, closure, chosen material swatches | Detail is subordinate to readable primary forms |

A hero might need 12–20 useful views/crops; this is a planning envelope, not a mandatory generation quota. A simple crate needs far fewer. Crop existing information first. Generate a missing view only when it resolves a modeling decision. Do not produce forty inconsistent illustrations for the sake of file count.

## 4. Continuity strategy

Use the chosen identity image as actual image input to the available tool. Record prompt/settings/provider/version and image ID when returned. Never assume a text reference to a file means the generator consumed its pixels. One provider seed cannot guarantee identical costume across new viewpoints.

Create view candidates through controlled reference editing when available. Compare face shape, hair part, emblem geometry, armor segmentation, garment hem, belt, handedness and proportions. Reject identity drift early. Label generated backs/soles or interiors as proposed construction until approved; they are invented completions, not recovered facts.

The strongest geometric anchor is a coherent 3D blockout: reconcile approximate artwork into one volume, render real orthographic views, then use those projections to constrain later refinements. This breaks the cycle of trying to satisfy several contradictory AI images. The approved blockout is not final art, but its camera geometry is real.

## 5. Reference authority and conflict resolution

Classify each input as aesthetic master, construction candidate, approved construction, material study, anatomy reference, rejected example or engine evidence. A rejected render must never become the automatic likeness target just because it is easier to recreate.

Choose a precedence for each component. Example: face closeup controls expression; construction front/side controls proportions; selected equipment sheet controls sword cross-section. When sources conflict, write a small decision and update all affected views. Do not average inconsistent shoulders into an arbitrary shape.

A reference labeled “front” can still be perspective/three-quarter. No exact front/side overlay metric is valid until camera, pose and proportions are compatible. Do not warp the reference differently for each body part just to make the model score better.

## 6. Neutral construction pose

Choose A-pose or T-pose based on the intended skeleton and garment clearance; neither is automatically superior. Define arms, palms, elbows, knees, feet and expression. An A-pose might begin with arms lowered about 35–45 degrees from horizontal and slight elbow bend, but these are candidate values to agree with the rig plan, not a universal standard. Show hands unoccluded and fingers separable for modeling.

Use a neutral closed-mouth expression unless the identity requires otherwise. Keep shield and sword as separate object references during anatomy work, then review actual grip poses. Facial expression, animation rest pose and marketing pose must not be conflated.

## 7. Blender setup

Inspect the current file, units, transforms and handedness before adding references. Preserve the repo's existing +Y-forward/+Z-up convention if still valid; do not change it simply because Blender's standard front hotkey looks along a different axis.

Set a world floor, origin, height marker, centerline and measurement landmarks. Use orthographic cameras with explicit transforms, not screen orientation assumptions. Import reference images as non-rendering empties in a dedicated locked collection. Record image dimensions, image hashes, image display size, plane transform and model height. A helper is included, but it requires already chosen calibration matrices.

Use common ground and head-height alignment and uniform scale. Background padding should not distort body-height comparisons. Store cropped source bounds and crop transform, rather than measuring whitespace. Keep input resolution native; increasing image dimensions does not create new construction information.

## 8. Reference gate

Require: chosen identity; a reconciled view set; left/right convention; part inventory; unresolved-geometry decisions; dimensions/camera; rights and private-upload review. Pram approves that this is the intended character before complex modeling begins.

For Ada, the supplied illustration remains aesthetic intent. The supplied full-body panels are not certified orthographic references. Included crops are native copies, not new views. The rejected 3D screenshot is a diagnosis baseline and is missing the feet; do not derive total height from it.
