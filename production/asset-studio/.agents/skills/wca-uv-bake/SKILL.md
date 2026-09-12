---
name: wca-uv-bake
description: "Unwrap, plan texture density and bake approved source detail onto runtime geometry."
---

# wca-uv-bake

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/03_TOPOLOGY_UV_BAKING.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Confirm approved forms/cage and explicit triangle/normal convention. Snapshot inputs and invalidate old bakes after changes.
2. Mark seams by visibility/construction; plan face/emblem allocation and declared mirror/stack exceptions.
3. Review checker density/distortion and padding at the intended smaller mips. Do not maximize occupancy at any cost.
4. Create high/low groups and cage/ray recipe. Isolate thin/overlapping parts to avoid cross-projection.
5. Bake actual normal/AO or needed channels, record tangent basis/normal orientation and color-space routing.
6. Inspect contact seams, rims, fingers and mip bleeding with actual maps. A flat neutral normal is not evidence of a detailed bake.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

UV layout, bake source/cage/recipe, output maps, hashes and native/mip inspection images.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
