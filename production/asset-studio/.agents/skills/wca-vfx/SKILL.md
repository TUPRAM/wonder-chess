---
name: wca-vfx
description: "Design readable skill effects and timing in Unreal; not new combat mechanics."
---

# wca-vfx

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/08_ASSET_CLASS_ROUTES.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Read the existing skill/event semantics, target, timing, lifetime and screen/board scale.
2. Create a shape/timing storyboard and distinct effect language for stun/shield/heal/dash.
3. Use appropriate Niagara/material/mesh/flipbook tools actually available; keep event bindings presentational.
4. Declare pooling, bounds, simultaneous count, overdraw, shadows and reduced-effects behavior.
5. Review full effect sequences and crowded matches; prevent solid shells or particles obscuring units.
6. Run engine/motion/profile gates with genuine captures and do not label a concept frame as a runtime effect.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Effect assets/storyboard, timing/visibility tests and crowded-runtime evidence.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
