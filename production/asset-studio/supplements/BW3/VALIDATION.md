# BW3 handoff validation

Date: 2026-09-09. Scope: read-only source review and instruction-package preparation.

## Performed here

- Read the supplied BW2 review, verification, and per-frame contact measurements.
- Hashed the two uploaded Blender files, supplied review, comparison PNG, and movie: all five matched the corresponding values in the supplied verification record. See `evidence/LOCAL_SOURCE_CHECKS.json`.
- Recomputed all145 supplied vertex/cylinder penetration records by phase. Closure frames4–24 exceed the existing0.5mm screen; maximum13.906720174744448mm is at frame14. The121 held frames remain within that particular sampled penetration screen.
- Decoded145 frames from the supplied800x800,24fps movie. Inspected ten temporal samples in the retained sheet and frame14 at native resolution. This is not a new all-frame visual or mesh collision review.
- Ran the measurement-summary script against the supplied JSON. Eight read-only summarizer tests passed, including validation of missing/nonfinite/duplicate frame data and the requirement not to waive closure penetration because of its source phase label.
- Parsed both Python files and all package JSON. Checked authored local image references. Copied the original report/verification/measurements/comparison without changing their bytes.
- Created the ZIP, tested its CRC integrity, and checked each packaged file against the SHA256 manifest. Manifest excludes itself.

## Not performed here

No Blender executable, live MCP action, sculpt, weight edit, joint correction, new .blend save/reopen, modifier evaluation, collision calculation from geometry, Unreal import, animation retarget, packaged game test, human approval, or recipe promotion.

The reported375/567 self-crossing counts and local calibration results remain supplied-source findings. This handoff did not independently reproduce them. The eight helper tests are not hand tests, collision tests, or artistic evidence.

The extra local audit files linked inside the original BW2 report were not uploaded and were not invented or reconstructed. Codex must inspect them locally when required. The source videos and references remain evidence of an ART_REVISE asset.

## Artifact boundaries

This ZIP does not include redundant copies of the large .blend files. It expects the user’s existing local BW2 sources. Images are unchanged source extracts or labeled/downsampled comparison sheets, not AI-generated improved results. The fixed-grip document is a proposal requiring explicit adoption before substituting it for the animated-route goal.
