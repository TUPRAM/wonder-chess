---
name: wca-retopo
description: "Build or validate motion-ready/runtime topology from approved forms."
---

# wca-retopo

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/03_TOPOLOGY_UV_BAKING.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Preserve approved source; choose whether rebuilding is necessary or existing clean modeling already suffices.
2. Create runtime cage using controlled snapping/shrinkwrap/Poly Build or equivalent verified tools; avoid projecting onto wrong nearby surfaces.
3. Plan loops around actual deformation regions and retain distinctive silhouettes. Do not enforce quads on every rigid planar surface.
4. Inspect degenerates, doubles, normals and declared boundaries; do not weld all separate clothing/equipment into one solid.
5. Run early representative joint or assembly tests before UV/texture work. Correct topology/volume when weighting cannot fix it.
6. Record source/runtime differences and intended deterministic triangulation. Mark incomplete geometric checks explicitly.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Runtime cage, wireframes, topology observations and early pose/assembly evidence.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
