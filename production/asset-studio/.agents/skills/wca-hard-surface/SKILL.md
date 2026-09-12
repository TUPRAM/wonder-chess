---
name: wca-hard-surface
description: "Construct armor, weapons and rigid props with deliberate cross-sections and attachment."
---

# wca-hard-surface

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/02_MODELING_AND_LIKENESS.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Identify outlines, cross-sections, thickness, pivot/contact and adjacent parts from approved references.
2. Build intentional shells/planes and overlap. Use curves, profiles or mesh editing rather than universal rounded caps.
3. Keep Boolean construction editable until topology cleanup; do not fuse armor into skin.
4. Author bevel width and shading by surface purpose. Verify geometry silhouette instead of only smooth normals.
5. Test blade taper, guard/grip/pommel, shield convexity/crest/backing, or equivalent prop functions from side and oblique views.
6. Review neutral clay, material IDs and attachment test. Reject floating fasteners, intersecting hands or melted edges.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Named rigid source parts, assembly/cross-section views, collision/attachment notes and forms evidence.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
