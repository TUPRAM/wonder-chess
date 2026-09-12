---
name: wca-ui
description: "Produce game icons, portraits and interface art with small-size and state validation."
---

# wca-ui

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/08_ASSET_CLASS_ROUTES.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Define actual sizes, states, target contrast, alpha/padding and localization constraints.
2. Use the approved asset for portraits or explicitly verify matching identity; do not show ideal concept art beside a different finished model.
3. Author shape-first icons and separate artwork from live text. Raster art is not editable vector output.
4. Review native and small sizes, team/selection/disabled states, keyboard/touch behavior and reduced motion when relevant.
5. Export correct formats/atlas settings and verify in Unreal screens, not only a graphic editor.
6. Prepare UI-specific gate evidence; skip mesh retopology and skeletal steps unless the asset is actually 3D.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

UI source, icons/portraits/states, size tests and implemented-screen evidence.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
