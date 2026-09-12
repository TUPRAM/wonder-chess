# Source notes and boundaries

## Project basis

Primary source: supplied `REVIEW(1).md` and `verification(3).json`, copied byte-for-byte under `evidence/source/`. The scope is the supplied BW1 r003 snapshot. The source `.blend` and movie hashes were measured independently and match the report. Working/frozen Blender files intentionally have different hashes; their reported semantic equality was not independently rerun in Blender here.

The supplied motion clip was decoded, metadata checked, and 22 temporal samples inspected. The video does not establish exact grip millimetres, exact bone transforms, or all-surface collision results. Those numbers and mechanism findings are attributed to the source report, not remeasured from the footage.

No protected list of all 44 original inputs was supplied as 44 independently accessible files. Their unchanged status is a source-reported result; this handoff confirms only the supplied file hashes.

## Technical references consulted, 2026-09-09

These primary references support mechanics, not the proposed artistic design, grip tolerances, or successful execution. Verify actual behavior in the installed Blender/Unreal versions; do not upgrade simply because a web page labels itself latest.

- **S1 — Blender developer documentation, Bone Transform Spaces.** https://developer.blender.org/docs/features/animation/armatures/ . Armature/pose/world-space distinction; world transforms require the armature object's world matrix.
- **S2 — Blender Manual, Child Of Constraint.** https://docs.blender.org/manual/en/latest/animation/constraints/relationship/child_of.html . Parenting-like constraint behavior and inverse handling. The indexed page was accessible through search; direct fetching was inconsistent.
- **S3 — Blender 5.0 Manual, Smooth Corrective Modifier.** https://docs.blender.org/manual/en/5.0/modeling/modifiers/deform/corrective_smooth.html . Rest-source/bind and group-limited deformation correction.
- **S4 — Blender Manual, Solidify Modifier.** https://docs.blender.org/manual/en/5.3/modeling/modifiers/generate/solidify.html . Documents limitations of even-thickness approximation. Cited for the mechanic, not as an instruction to install the development version.
- **S5 — Epic, FBX Morph Target Pipeline.** https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-morph-target-pipeline-in-unreal-engine . Supports morph-target interchange; arbitrary Blender driver behavior is not claimed.
- **S6 — Epic, FBX Animation Pipeline.** https://dev.epicgames.com/documentation/unreal-engine/fbx-animation-pipeline-in-unreal-engine . Skeleton/animation export/import requirements and version compatibility considerations.

No new third-party assets were downloaded. The source-reported license conflict for an unused boot remains unresolved and the asset remains excluded. Existing accepted glove/boot uses remain licensed adaptations rather than from-scratch authoring.

## Proposed additions, not facts about the current asset

The hand-frame construction, 28×105 mm diagnostic cylinder, millimetre contact screens, rigid-prop drift screens, sample pose angles, dedicated knee-control proof and ordered task dependencies are proposed engineering/art interventions. They have not been run on the actual Ada candidate here.

The optional Python helper tests geometry calculations on synthetic points only. It cannot assess aesthetics, an entire mesh, simulation stability, game performance, or the correctness of the user's Blender integration.
