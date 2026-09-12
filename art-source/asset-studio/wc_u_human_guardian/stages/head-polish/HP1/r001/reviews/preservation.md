# HP1 independent preservation and source-scope review

Completed: 2026-09-08T14:13:54.131091+00:00

**Protected files: PASS — all 9 files match their recorded SHA-256 hashes.** This recheck includes the FH1 work file and frozen r004 checkpoint, plus all seven MR1/r003/reference files listed in FH1/preservation_before.json. Sizes and modification timestamps remained stable during every read.

**Source scope: PASS WITH LIMITS.** Manual inspection covers all 17 current HP1 operation files, from 00_setup.py through 15_cage_and_audit.py, including 09b_install_portrait_camera.py. All 17 parse as Python. Exact script hashes and the full file results are in preservation.json.

The scripts confine geometry mutations to new HP1 head candidates, copied diagnostic eyes, and separate cage-review copies. They do not write original hair, eyebrows, eyelashes, torso or armor geometry. Original FH1 component data is read for index mappings and section positions. The retained geometry branches back to r011 when r012 is rejected; this observation is from the source, not a runtime verdict.

The only material-node edits in the added scripts belong to the newly created HP1_Cage_Diagnostic_Ink material. Its material slot replaces the copied cage-edge mesh material list. No reviewed statement edits original FH1 materials or existing world nodes. Diagnostic eye materials are unchanged in the reviewed source. Lighting and eye-visibility changes for diagnostic captures target HP1 copies and are explicitly restored.

The later scripts assert the active HP1 stage path. The final audit source explicitly saves the HP1 work file and an r014 checkpoint with copy=True. Camera fitting and cage captures remain separate from artistic acceptance.

**Limits:** This is a filesystem and source review. It does not access Blender, inspect live original-object identity or geometry, evaluate meshes, authenticate execution history, inspect final pixels, or confer artistic/human approval. The live scene audit and visual review remain root's responsibility. Coverage ends at the listed source hashes and timestamp.

[Machine-readable details](preservation.json)
