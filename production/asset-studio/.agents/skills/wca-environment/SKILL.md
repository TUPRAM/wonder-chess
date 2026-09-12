---
name: wca-environment
description: "Produce modular arena/environment/foliage assets with assembly and scene readability checks."
---

# wca-environment

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/08_ASSET_CLASS_ROUTES.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Define grid, pivots, connectors, module sizes, collision role, style and material/trim reuse.
2. Approve one representative module or plant before procedural variants. Use the static/foliage route, not automatic character rigging.
3. Test assembled corners, stairs, repetition, scale and hero-camera clearance. Keep board information readable.
4. For foliage, author card/mesh/normal/wind masks and inspect masked overdraw, mips, shadows and LOD silhouette.
5. Validate required lightmap UVs only for the selected lighting path and actual asset use.
6. Review complete scene with heroes/UI/effects and profile real conditions rather than isolated prop beauty.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Accepted module/foliage source, kit assembly, pivot/collision tests and scene evidence.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
