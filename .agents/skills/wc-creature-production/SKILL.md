---
name: wc-creature-production
description: Produce animation-ready Wonder Chess creatures with Meshy four-view geometry, color, PBR textures and a verified Unreal rig in one coordinated delivery. Also plan or resume animation, sound and packaged review while preserving Meshy colors.
---

# Wonder Chess creature production

Use the project-local [production handbook](../../../production/creature-pipeline/README.md)
for the owner-selected Meshy → Unreal route. Keep Blender out of this route.
For planning/documentation requests, author only the requested records; do not start
generation, install tools, upload art, change Unreal assets or spend credits.

## Default new-creation outcome — owner amendment, 21 September 2026

A request to create a creature now means **colored, textured and rigged, ready for
animation authoring**. Continue through the [animation-ready contract](../../../production/creature-pipeline/ANIMATION_READY.md).
Do not stop at a gray mesh or present generation success as a completed creature.
Provider operations remain sequential where required: four-view generation with
PBR and optimization, preserve/download, anatomy/material checks, suitable initial
rig, Unreal controls and actual deformation verification. "In one go" describes
the delivery, not a nonexistent combined generation-and-quadruped-rig API.

Use [wc-creature-rigging](../wc-creature-rigging/SKILL.md) for the rig stage and
[texture development](../../../production/creature-pipeline/TEXTURE_DEVELOPMENT.md)
for source maps, imports and subsequent revisions. Reuse accepted references and
their documented alignment tolerance. Prepare one itemized provider budget for
the complete candidate; obtain a missing cap once, then proceed within it. Never
silently replace an explicitly requested fresh generation with an old mesh.

The owner now authorizes preparing isolated G3/G4 candidates for one combined
forms/color/rig review. Intermediate technical checkpoints still apply; they are
not separate mandatory user questions. Fix bounded local issues autonomously;
stop dependent work on unusable anatomy or a missing spending authorization.
Combine a pending shared-look comparison with this candidate review. Final human
acceptance, full animation/audio and game-release acceptance remain distinct.

## Start or resume

1. Read the current user scope, project instructions, handbook entry point and
   asset's latest handoff. Confirm canonical ID/profile from `data/vnext/catalog.json`.
2. Identify the exact candidate and first incomplete/stale G-stage. Check current
   file hashes, existing approvals, running jobs and file ownership before retrying.
3. Read only that stage's linked manual and direct dependencies. Use
   [production engineering](../../../production/creature-pipeline/ENGINEERING.md)
   for G3A construction, G3B deformation, G3C UV/bake, fixed cameras and revision/recovery;
   [toolchain](../../../production/creature-pipeline/TOOLCHAIN.md) for qualified commands.
   Empty templates are not passed checks; register Unreal validators explicitly.
   Use
   [character briefs](../../../production/creature-pipeline/CHARACTER_BRIEFS.md) for
   anatomy-specific decisions; their proposals are not automatic art approvals.
   For new geometry, use [four-view inputs](../../../production/creature-pipeline/FOUR_VIEW.md):
   Main/front, anatomical Left, Back and anatomical Right. Review all four together,
   including inferred views, and preserve slot mapping/hashes. No silent single-image
   fallback or mirroring of asymmetric sides; existing accepted models stay preserved.
   The owner selected Krita for precise scaling, padding and reference-sheet assembly
   on 21 September 2026. Use it by default for those operations without asking again.
   Preserve original art and colors; save layered `.kra` sources and separate PNGs.
   Matching silhouette bounds alone does not establish matching anatomical landmarks.
   Honor the owner's tolerance for small reference misalignment: preserve the
   documented discrepancy and use the authorized bounded Meshy trial to assess it.
   Do not prolong alignment-only revisions or require a proxy after that decision.
4. Preserve the accepted Meshy color maps and palette. Reuse the approved shared
   look; do not copy Bellback's old tint/emissive material recipe. If G1 has not
   passed, prepare its isolated comparison instead of inventing an approved preset.
   Confirm the actual skeletal material renders in PIE; explicit skeletal-mesh
   usage is required. A gray fallback material cannot pass color preservation.
5. Copy and adapt Bellback tooling into a new candidate-specific recipe; preserve
   the original. Replace its paths, bone indices, scale and foot offsets with that
   candidate's measured values. Unreal completes rigs/motion and verifies actual skin.
   Gameplay event authority stays in the canonical runtime.
6. Use [acceptance criteria](../../../production/creature-pipeline/ACCEPTANCE.md)
   and [templates](../../../production/creature-pipeline/templates/README.md).
   Separate authored, executed, visually/listening reviewed and owner-accepted.
7. Honor existing scoped authorization. This skill grants no new paid credits,
   account agreement, external upload or public deployment. Prepare concrete local
   inputs before asking for a missing external decision; don't ask twice unchanged.
8. Present the exact candidate at required look/reference/forms/final gates and
   record the owner's real decision and hashes. Never self-issue human approval.
   For new creations, apply the combined G3/G4 review amendment above; do not
   interrupt after untextured geometry merely to repeat unchanged design questions.
   After two failed critical corrections, change method or seek a focused decision.
9. Update the candidate/handoff and `reports/implementation_state.json` with actual
   state. Deliver the usable source, rig, clips, audio, package/launcher and evidence.

## Relationship to existing skills

Use [wca-orchestrate](../wca-orchestrate/SKILL.md) for AS1 ownership/provenance/review
principles, [wc-unreal-integration](../wc-unreal-integration/SKILL.md) for engine work,
and [wc-release-evidence](../wc-release-evidence/SKILL.md) for relevant package checks.
The handbook is the explicit route amendment to historical Blender-source assumptions.
Do not fabricate old ledger stages or call a bounded creature test a full game release.

## Completion

For animation-ready scope, deliver the full verified material/skin/control bundle
and pose study; full combat clips, audio and a packaged release are later scope.
For game-ready scope, proceed through the authorized work until required technical checks and exact
owner appearance/motion/sound acceptance are recorded for the stated use. Retain
unchanged approvals, preserve rejected/old sources, and name genuine limitations.
