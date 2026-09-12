---
name: wca-rig
description: "Build a versioned authoring rig and explicit game export skeleton."
---

# wca-rig

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/04_RIG_SKIN_MOTION.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Read actual runtime names/rest matrices/sockets and required clips. Verify body-family compatibility.
2. Place joints from anatomy and intended motion rather than armor edges; set roll/poles/rest pose deliberately.
3. Use Rigify or manual controls only when installed/tested. Preserve metarig and rebuilding recipe.
4. Separate author controls/mechanisms from export hierarchy. Retain required non-deforming root/socket helpers.
5. Test IK/FK/control behavior and export bake mapping; do not presume constraints transfer with FBX.
6. Submit rig/hierarchy evidence before formal skinning. A generated rig does not mean the mesh is bound.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Authoring rig/metarig, export skeleton, mapping, control tests and rig gate.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
