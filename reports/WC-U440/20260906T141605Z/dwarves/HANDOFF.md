# Borin, Tessa and Dagna source/export handoff

AUTHORED_EXECUTED_EXPORTED_SOURCE_READBACK_PASS_ENGINE_ACCEPTANCE_PENDING

All three existing heroes were refined from their actual revision6 sources. This is authored, Blender-executed and exported work; it is not finished-hero or Unreal acceptance.

| Hero | LOD0 / LOD1 / LOD2 triangles | Changed clips | Source revision |
|---|---|---|---|
| wc_u_dwarf_guardian | 5670 / 2835 / 1416 | Attack, Active | 7 |
| wc_u_dwarf_ranger | 4748 / 2373 / 1187 | Attack, Active | 7 |
| wc_u_dwarf_warrior | 4176 / 2088 / 1043 | Attack, Active | 7 |

All three use the retained 27-bone `WC_family_v1` stocky skeleton, one material, existing 1024px BaseColor/Normal/ORM atlases and the measured `fbx_skeletal_cm_v1.json` centimeter-copy export. Nine mesh FBXs,21 animation FBXs and3 model-matched portraits were updated at their stable paths. The nine existing texture PNGs are byte-for-byte preserved.

Actual readback:21 MP4 files,60fps,384×384,1332 frames,22.2seconds. All-frame mesh checks passed; five unedited clips per hero and the rest skeleton match preserved revision6 byte-derived curve signatures. The three 35-pose sheets and six geometry views per hero were visually inspected. Videos are darker Workbench previews; material response requires current Unreal review.

Borin maximum new support reach clamp17.18mm; Tessa0mm; Dagna19.49mm against25mm check. Earlier Borin47.97mm and Dagna36.23mm trial failures are retained; corrected motions were rerun and exported only after passing.

Source paths: `art-source/heroes/<stable_id>/<stable_id>.blend` and retained new `<stable_id>_revision7.blend`. Exports: `exports/heroes/<stable_id>`. Production source SHA256 and all export hashes are in each `export_manifest.json` and `source-export-video-validation.json`.

Exact root continuation: import/reimport these3 stable hero folders using the existing Unreal importer, validate9 mesh and21 animation assets, review all21 clips continuously with the actual materials, gallery framing and all stars, then inspect both team orientations and a crowded strategy camera at1080p/720p. Check noted small-silhouette ambiguity and Dagna face occlusion; do not mark those acceptance cells from the rendered file count.

Current release gates not established here: continuous normal-speed visual approval, current Unreal reimport, LOD silhouette acceptance, gallery/stat/skill synchronization, mixed-team combat visibility, audio synchronization, packaged play and performance.

See `handoff.json`, `source-export-video-validation.json`, per-hero `motion-invariants.json`, `structure-inspection.json`, `geometry-sheet.png`, `pose-sheet.png`, `continuous_<clip>.mp4`, and `export-result.json`. The prior source inspections and initial geometry/failure evidence remain under `reports/WC-U440/20260906T140743Z/dwarves`.
