---
name: wca-unreal
description: "Import and verify approved assets in the actual Unreal project and packaged runtime."
---

# wca-unreal

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/05_UNREAL_AND_RELEASE.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Inspect installed engine/importer and current measured export profile; do not switch version or legacy/Interchange route silently.
2. Import into isolated candidate content folders with explicit skeleton/material choices; preserve canonical asset references.
3. Check meters/centimeters, orientation, normals/tangents, texture channels, sockets, bounds, collision and clip binding.
4. Review actual arena/camera with duplicates, crowded effects and friendly/enemy orientation. Profile named hardware.
5. Perform a deliberate source revision/reimport and verify no reference/pose/material regression.
6. Run the packaged game with accepted content. Missing engine access remains blocked; editor Python is tooling, not gameplay runtime.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Actual import/clip/reimport/package logs, game captures, profile data and engine gate.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
