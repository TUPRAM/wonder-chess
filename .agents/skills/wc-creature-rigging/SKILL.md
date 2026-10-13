---
name: wc-creature-rigging
description: Rig, repair or validate Wonder Chess creature skeletons, skin weights, elbow and foot controls, spines, tails and rigid attachments in Unreal. Use for animation-ready handoffs, auto-rig assessment and ground-contact defects on Meshy creatures; no Blender production.
---

# Wonder Chess creature rigging

## Scope and inputs

Use the [creature handbook](../../../production/creature-pipeline/README.md),
[animation-ready contract](../../../production/creature-pipeline/ANIMATION_READY.md)
and G4 sections of the [Unreal manual](../../../production/creature-pipeline/UNREAL_RIG_AND_VALIDATION.md).
Read the candidate handoff, mesh/map hashes, construction inventory and intended
motion. Keep canonical gameplay unchanged. Planning-only requests do not execute
rigging. One writer owns the candidate's skeleton, skin, controls and Unreal assets.

## Procedure

1. Inspect the actual mesh: units, axes, rest pose, separate limbs, joint clearance,
   rigid regions, UVs and material slots. Inventory existing skins/bones before
   replacing anything. Preserve source files and prior rigs in separate revisions.
2. Select a supported route from actual anatomy. Recheck provider capability.
   Meshy's documented rigging API targets humanoids; quadrupeds use its website
   route when supported. Smart Rig is not proof of animation-library support.
   Never send a quadruped to a humanoid endpoint merely because it is callable.
   Use an existing authorized batch budget; this skill grants no new credits.
   If the provider fails without an export, record the failure and charge. When
   local rig completion is authorized, build the skeleton/skin in Unreal on the
   preserved source mesh and UVs. Label it as an Unreal rig, not a Meshy export;
   validate it under the same checks. Do not silently resubmit a paid job.
3. Preserve rigged FBX/GLB, maps, task/settings, hashes and actual cost. A successful
   auto-rig is a starting result. Check skin weights, not just the skeleton overlay.
4. Import into isolated Unreal content. Map semantic roles to actual bones and
   parents; record rest transforms. Check scale once through the full parent chain.
   Adapt existing tools with measured values, never Bellback bone indices/sole offsets.
5. Provide editable root/body, spine, head and appropriate limb/appendage controls.
   Grounded limbs need foot targets and bend-direction controls; a long tail needs
   inspectable chain controls. Record control spaces, limits and reset behavior.
   Preserve rigid stone/shell/bell shapes under deformation; correct specific
   weights in Unreal. Do not claim per-toe/facial controls unless actually present.
6. Author a short inspection sequence: rest, alternating foot lift, both elbows
   and knees bending, body compression, spine turn, head turn and tail sweep as
   applicable. Use a visible measured floor. Test contact surfaces of the actual
   skinned mesh; bone endpoints alone do not prove paws avoid the floor.
7. Check invalid/non-normalized weights, unsupported influences, missing bones,
   joint collapse, volume loss, rigid-part drift, clipping, bounds and materials.
   Record sample coverage, errors and unresolved limitations; never invent a pass.
   Save, close, reopen, manipulate the controls and recapture actual deformation.
8. Deliver the editable source rig, semantic bone/control manifest, pose sequence,
   measured report, viewed captures/video, texture linkage and exact reopen path.
   Distinguish animation-ready from finished locomotion/combat/game integration.
   Return evidence to the production candidate and implementation ledger.

## Failure and revisions

Keep good geometry/colors when only weighting is defective. Topology/vertex-order
changes invalidate affected skin/UV evidence; skeleton/rest-pose changes invalidate
controls and dependent clips. Preserve previous versions and recheck affected work.
After two failed critical corrections, change method with evidence. Do not spend
on repeated auto-rig attempts without a suitable authorized allowance.

Technical passage is not owner appearance/motion approval. For a new creature,
include the rig study in the combined forms/color/rig review authorized by the
production skill. Do not self-issue approval or force an extra intermediate question.
