# Projectile glyph import review — 2026-09-06

The dedicated legacy FBX commandlet completed and exited 0 at 14:27:12 Singapore time. It imported and saved only the two authored projectile meshes under `/Game/WonderChess/Effects`, using existing `/Game/WonderChess/Materials/M_WC_Surface` in their single material slot. It did not modify that shared material or the production hero importer.

The measured preset enables scene and unit conversion, disables forced front-axis conversion, uses yaw 90 degrees, translation zero, and uniform scale 1. Actual signed bounds match the authored manifest:

| Asset | X extents (cm) | Dimensions X/Y/Z (cm) | LOD0 triangles |
|---|---|---|---|
| SM_WC_ArrowGlyph | -34 to +42 | 76 / 17 / 2.2 | 64 |
| SM_WC_BoltGlyph | -27 to +35 | 62 / 13 / 3.4 | 76 |

The long axis, positive tip extent, negative tail extent, dimensions, triangle count and assigned material checks pass for both meshes. Source manifest, FBX and saved asset hashes are recorded in `effect-import.json`; actual console output is in `effect-import-console.log`.

The commandlet reported **0 errors and 4 warnings**: a degenerate tangent basis and nearly zero binormal warning for each glyph. The source geometry has no usable UV layer for tangent generation. This was reported to the art lane for a source UV correction. The flat tint material does not establish that the warning is harmless; rendered shading and flight have not been reviewed by this import task. The bounds-check `PASS` is not a warning-free import, rendered acceptance or packaged-flight claim.

No commandlet remains active from this import. The unrelated pre-existing user editor was observed only by process name/id and was not inspected or altered.

## UV correction verified in Unreal

The art lane supplied revision 2 with nondegenerate per-face UV islands and unchanged geometry/dimensions. A separate dedicated commandlet reimported both meshes and exited 0 at 14:39:05 Singapore time. Its commandlet summary reported **0 errors and 0 warnings**; neither tangent-basis nor binormal warning reappeared. The six bounds/count/material checks still pass per mesh. See `effect-import-uv2.json` and `effect-import-uv2-console.log` for the corrected source and saved-asset hashes and actual output. The original `effect-import.json` and console log remain intact as evidence of the first import's warnings.

Unreal shutdown subsequently logged the known lower-priority Interchange feature-flag reset notices. These are distinct from import warnings and did not affect the commandlet result. Rendered flight and packaged use still require their separate presentation checks.
