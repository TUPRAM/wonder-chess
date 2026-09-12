---
name: wca-release
description: "Prepare final asset promotion after current technical and human acceptance; do not publish automatically."
---

# wca-release

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/05_UNREAL_AND_RELEASE.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Check every required gate, dependency hash and current source/export version. Stale evidence blocks release.
2. Assemble approved editable source, rig/metarig, maps, clips, exports, recipes, provenance and known issues.
3. Confirm actual packaged in-context evidence and measured scope; do not infer mobile or online readiness.
4. Present exact candidate hash and intended use for Pram release approval. Never self-issue human signoff.
5. Prepare non-destructive canonical promotion and rollback plan. Do not perform broad deletions or pushes without authorization.
6. Register reusable components only after acceptance and schedule regression checks for shared rig/material changes.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Release candidate manifest, human approval request, rollback and controlled promotion plan.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
