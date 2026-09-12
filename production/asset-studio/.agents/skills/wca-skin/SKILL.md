---
name: wca-skin
description: "Initialize, correct and verify deform weights and actual joint motion."
---

# wca-skin

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/04_RIG_SKIN_MOTION.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Inspect runtime cage and approved rig. Choose auto/transferred/manual initialization by body, cloth or rigid part.
2. Normalize deform weights, remove unintended tiny influences, inspect profile influence cap and unweighted vertices.
3. Do not mistake non-skin mask groups for deformation errors. Rigid weapons/plates use deliberate attachment/weight policy.
4. Run the family pose suite and actual shield/weapon grips on both sides. Inspect continuous transitions, not just one pose.
5. Fix source geometry/joint location before adding corrective weights that hide another error. Test runtime-compatible deformation, not only Blender Preserve Volume.
6. Record optional corrective morph/driver implementation requirements; do not claim a Blender driver will run in Unreal.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Weighted candidate, numerical observations, pose images/video and skin gate.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
