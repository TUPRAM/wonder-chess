---
name: wca-reference
description: "Reconcile AI views into a measured construction pack and set up Blender references."
---

# wca-reference

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/01_CONCEPT_AND_REFERENCES.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Classify aesthetic master, construction candidate, material reference and rejected baseline. Assign authority by part.
2. Reconcile angled front views, inconsistent details, occlusions and mirror ambiguities into explicit design decisions.
3. Choose neutral pose, world floor, origin, axes, scale and landmarks. Keep inherited game/export conventions unless a migration is approved.
4. Calibrate image transforms with uniform scaling and known crops; do not distort separate regions to fake similarity.
5. Run the hash-checked reference_setup helper only with actual calibrated matrices and a new candidate destination. Never reset the live scene.
6. Use a consistent 3D blockout to produce real orthographic projections when AI views disagree. Prepare reference gate for Pram.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Reconciled view/part pack, calibrated reference spec and candidate .blend; human reference gate.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
