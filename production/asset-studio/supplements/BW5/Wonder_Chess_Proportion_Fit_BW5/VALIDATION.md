# BW5 handoff validation

Status: DOCUMENT_AND_REFERENCE_PREPARATION_ONLY.

## Actually executed

- Parsed 6 JSON records.
- Recomputed and checked 8 projected ratios and their selection-uncertainty intervals.
- Verified 10 native crops against the exact supplied source pixel rectangles.
- Opened/verified 15 PNG files.
- Checked 45 local Markdown/HTML links: no missing targets.
- Compared nine supplied source artifacts with the user's BW4 verification hashes: 7 match; two comparison PNGs differ. The cause of the two image-byte differences was not established.
- Inspected both annotated reference sheets visually. An earlier permission error occurred while saving the first sheet; the operation was rerun successfully and the final files exist.

## Scope of the image measurements

Endpoints were manually selected from the source images. The published intervals are conservative endpoint-selection allowances, not statistical confidence or a recovered 3D fit. Source view/pose/camera differences remain. Hidden body dimensions and total profile shell depth were not invented.

## Not executed

No Blender load, geometry edit, modifier evaluation, actual 3D ratio/clearance measurement, movie decode, collision query, rigging, Unreal import, game animation, runtime test, asset approval, new AI artwork or model training. No supplied .blend file was changed.

The seven matching artifacts are both hand .blend files, both armor .blend files, both MP4s, and the supplied report. This does not rerun the author's 77-source preservation or reopen checks. The two supplied comparison PNGs remain useful user references but are not claimed to be byte-identical to the report's original image artifacts.

## Packaging

SHA256SUMS.json records every payload file other than itself. ZIP CRC and payload hashes are verified after packaging. No fonts, source .blend binaries, movies or downloaded third-party art are bundled.
