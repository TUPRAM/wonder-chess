---
name: wca-audio
description: "Create or integrate game sound assets with provenance, listening and in-context mix tests."
---

# wca-audio

## Inputs and scope

Read the repository instructions, `production/asset-studio/docs/08_ASSET_CLASS_ROUTES.md`, the active asset manifest, current source and direct gate dependencies. Confirm ownership and actual tools. Do not load every manual or modify unrelated gameplay.

## Procedure

1. Define sonic meaning, event time, duration, variant/loop policy, format and license/upload constraints.
2. Generate, synthesize or record through permitted tools; keep dry sources and actual provider/recording metadata.
3. Inspect clipping, clicks, loops, silence and variation; measure declared audio quantities with a real tool.
4. Listen to dry and in-game mixed versions; waveform screenshots alone are not hearing evidence.
5. Test attenuation, repetition, voice count and important-cue masking in a crowded fight.
6. Follow the audio route and human listening gates; do not invent rig/UV work.

## Tools and evidence

Use real existing Blender/Unreal/image/audio tooling only after capability discovery. The included ledger, image helper and Blender scripts are documented in `production/asset-studio/docs/07_TOOLS_AND_COMMANDS.md`. They are not replacement modeling intelligence. Capture source hashes, actual images/video/audio, commands and limitations. Do not treat tool success as human approval.

## Outputs and exit

Audio sources/variants, measured audio observations, listening decisions and engine mix evidence.

Prepare a pending report with `assetctl.py report-template`, populate it from real work, and seal with `prepare` only when required observations exist. Obtain the gate’s prescribed reviewer role. Do not invoke human approval yourself. A missing editor or poor required visual result blocks the affected stage.

## Failure and rollback

Do not overwrite canonical assets. Restore/reuse immutable checkpoints; inspect post-timeout state before retry. Record critical/major defects without relabeling them minor. Two no-improvement attempts require a method review or focused human intervention. End with exact next unblocked work, not an unsupported completion claim.
