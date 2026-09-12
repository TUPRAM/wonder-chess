# Source notes

## Attached project evidence

- S1: `../evidence/BW2_REVIEW_ORIGINAL.md` — copied byte-for-byte from the supplied REVIEW(2).md. It includes source calibration, contact, surface failures, carrying scope and recommended next intervention.
- S2: `../evidence/BW2_contact_measurements.json` — source measurements across145 frames. Original source is a diagnostic .blend; the report describes its geometry-equivalence binding to the delivered inspection pose. No new mesh was evaluated here.
- S3: `../evidence/BW2_verification_original.json` — supplied artifact hashes and gate states. Links within it to unprovided local audits have not been read here.
- A1: `../evidence/BW2_phase_analysis.json` — deterministic recomputation over S2, performed for this handoff.
- Images: provided six-view comparison and ten extracted video frames. These are screenshots of the rejected BW2 candidate, not new 3D work or generated ideal references.

Source claims are identified as reported. New workflow, diagnostics, acceptance ordering and the fixed-grip branch are proposals.

## Primary technical references checked for this handoff

**W1 — Blender Armature modifier.** Preserve Volume changes deformation representation, not an authored promise of collision-free behavior. Check the installed version before changing a modifier.
`https://docs.blender.org/manual/en/5.0/modeling/modifiers/deform/armature.html`

**W2 — Blender shape-key workflow (5.1 manual, English content on the internationalized page).** Shape keys store positions on shared topology; changes to topology require care. Used to support the independent candidate/corrective policy, not to claim a supplied corrective is functional.
`https://docs.blender.org/manual/id/5.1/animation/shape_keys/workflow.html`

**W3 — Blender BVHTree API.** Proximity/overlap APIs are available; installed API and the repository's narrow-phase crossing implementation still need inspection.
`https://docs.blender.org/api/main/mathutils.bvhtree.html`

**W4 — Epic skeletal mesh sockets.** Bone-relative attachments and mesh-specific socket options. The live documentation version is not an instruction to upgrade the local engine.
`https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-sockets-in-unreal-engine`

These references were checked as documentation, not executed against the user's Blender or Unreal installation. No new plugin or runtime library is required by this supplement.

## No new model capabilities claimed

No armature editor, sculpt solver, inverse-skinning implementation, collision engine, or protected approval service was created here. The included Python script summarizes supplied measurements only. Existing local tools remain subject to their real scope and validation.
