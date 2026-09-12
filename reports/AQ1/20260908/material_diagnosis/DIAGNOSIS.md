# AQ1 r06 material transfer diagnosis

Status: read-only source/log/pixel diagnosis. No Blender, Unreal, texture, bake or import asset was modified. The proposed A/B import test has not been executed by this lane.

The most concrete cause is a source image encoding mismatch: the candidate BaseColor contains sRGB-encoded values in a 16-bit PNG, while the installed UE 5.7 image path classifies 16-bit raw color formats as linear. Setting the final texture's `srgb` flag to true does not itself prove correct interpretation of those source pixels.

## Evidence inspected

- Actual Unreal capture: `reports/AQ1/20260908/engine_candidate_motion_r01/wc_u_human_guardian/Idle/frame-00000.png`.
- Actual Blender capture: `reports/AQ1/20260908/baked_r06/material_front.png`.
- Actual candidate export PNGs in `art-source/heroes/wc_u_human_guardian/candidates/AQ1/exports/r06`.
- `reports/AQ1/20260908/import-r01.json`, its native import log, and `tools/unreal/aq1_import_candidate.py`.
- Installed UE 5.7 implementation under `C:/Program Files/Epic Games/UE_5.7/Engine/Source`.

The engine capture visibly loses navy saturation and warm skin color. The PNG headers show all three r06 maps are 1024-square RGB16 PNGs. In contrast, the retained canonical Ada BaseColor and ORM are RGB8 PNGs at the same resolution.

The candidate BaseColor's dominant pixel values match the intended palette exactly at eight-bit inspection precision: navy (37,70,107), skin (166,102,69), ivory (233,226,205), steel (158,170,181), leather (74,48,37). This is not a missing-color bake. See `pixel-diagnosis.json` for source hashes, actual PNG headers and quantitative samples.

## Installed implementation findings

- `Runtime/ImageCore/Public/ImageCore.h:95–121`: gamma interpretation applies to G8/BGRA8; 16/32-bit formats are always linear, and their default gamma space is linear.
- `Runtime/ImageWrapper/Public/IImageWrapper.h:397–409`: the wrapper does not retain gamma metadata; its sRGB guess is based on eight-bit depth.
- `Runtime/ImageWrapper/Private/ImageWrapperBase.cpp:440–454`: decoded images receive the default gamma space for their raw format.
- `Editor/UnrealEd/Private/Factories/EditorFactories.cpp:2874–2876` and `2940–2951`: the generic PNG load uses that image wrapper result and moves its raw data into the import image.
- The candidate importer explicitly sets BaseColor `srgb=True` after import, ORM/Normal false, with normal-map compression and the selected green flip. The material wires ORM R/G/B to AO/roughness/metallic correctly. No shader sampler compilation error was found in the native import log.

If encoded BaseColor components are treated directly as linear values, the predicted linear luminance increase is 4.41× for navy, 2.46× for skin, and 5.58× for leather. Those are transfer-function calculations, not measured framebuffer factors; lighting and tonemapping prevent equating them directly to screenshot pixel ratios. Their direction fits the observed washout.

## ORM findings

Actual texels selected by each dominant BaseColor swatch have these median roughness/metallic values:

| Surface | Roughness | Metallic |
|---|---:|---:|
| Navy cloth/shield face | 0.761 | 0.000 |
| Skin | 0.549 | 0.000 |
| Ivory | 0.831 | 0.000 |
| Steel | 0.471 | 0.780 |
| Leather | 0.659 | 0.000 |

These measurements do not support swapped roughness/metallic channels or metallic cloth in the source PNGs. The stronger shiny impression may be secondary to the much lighter albedo and different gallery illumination; confirm after the color-encoding A/B test before altering material values.

There is a separate transfer difference: the AO median is 0 for skin texels and approximately 0.063 for ivory. The Blender baked material does not connect AO, while the Unreal candidate material does. That can produce stronger dark regions independently; it does not explain the brighter navy/skin. Retain this as a separate AO review issue rather than changing both variables in one experiment.

## Smallest useful experiment

1. Preserve the current RGB16 file/import/capture as the failed-color control.
2. Make an RGB8 copy of the same BaseColor values in a fresh candidate test output; verify PNG IHDR says bit depth 8 and swatches still read (37,70,107), (166,102,69), etc. Do not apply an additional gamma curve to the already encoded values.
3. Import that copy to a fresh candidate texture with `srgb=True`, replace only the candidate BaseColor parameter, and capture the same gallery pose/light/camera. Leave ORM, normals, material graph and world lighting unchanged.
4. If the palette recovers, make eight-bit game-delivery color output an explicit bake/export contract while retaining higher-precision authoring intermediates. Rebuild source hashes/manifests and repeat the candidate reimport check.
5. If a cloth highlight issue remains, isolate it with one temporary constant roughness=0.83/metallic=0 material variant, keeping the BaseColor fix. Investigate sampled ORM/compression only if that comparison changes the cloth materially.

This experiment can confirm or reject the encoding hypothesis without redesigning Ada's materials or compensating for a pipeline defect by darkening the palette.
