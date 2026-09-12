---
name: wca-costume
description: "Build character clothing, layered armor undergarments, hair masses and accessories."
---

# wca-costume

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/02_MODELING_AND_LIKENESS.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. List layer order and attachments; reconcile hems and hair flow across reference views.
2. Model primary garment volumes and large tension/compression folds. Do not distribute random wrinkles uniformly.
3. Preserve believable thickness and motion clearance. Intentional open garment borders are not automatically topology errors.
4. Build hair clumps/braid flow appropriate to gameplay distance; avoid simulation or strands without a concrete need.
5. Declare which parts will deform, attach rigidly, use optional bones or remain static. Test provisional arm/hip motion early.
6. Render neutral assembly and back/side closeups. Preserve identity and material hierarchy rather than merely adding accessories.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Costume/hair parts, layer diagram/notes, clearance evidence and deformation plan.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
