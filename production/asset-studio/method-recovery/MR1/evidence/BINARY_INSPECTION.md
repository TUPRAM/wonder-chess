# Read-only inspection of the uploaded Blender file

## Scope
The supplied `ada_clay_study_r003.blend` was hashed, decompressed in memory with the system Zstandard library, and its binary block directory and embedded DNA structure definitions were read. No Blender program, Python `bpy`, .blend text block, handler or driver was executed. No geometry was changed or re-saved.

The complete stream contained 4,932 blocks. Field-size totals matched the DNA size declarations for the ID, Object, Mesh, Collection and modifier structures used to read this inventory. Treat this as an offline saved-data inspection, not dependency-graph evaluation.

Source SHA-256: `15f7fdc7c842d57ff05873a7cd988637411ad8985eadf852757ebbd62877043b`.
File-format header: `BLENDER17-01v0501`. This is not a claim about the current installed Blender build.

## Saved records
- 106 Object records.
- 88 Mesh records, including inactive/experimental content.
- 0 armature records and 0 action records in this file.
- `ADA_Head_Continuous`: 22,764 base vertices, 22,512 stored polygons.
- `ADA_Head_r003_Failed_Proof`: 34,540 base vertices, 34,234 stored polygons.
- `ADA_Fitted_Eye_L` and `ADA_Fitted_Eye_R`: 1,153 base vertices each.
- 18 `ADA_Overlapping_Lock_*` objects, each with 1,280 stored base vertices.
- `ADA_Scalp_Supported_Sweep_01`: 4,000 stored base vertices.
- Named cameras: CAM_front, CAM_profile, CAM_three_quarter, CAM_face, CAM_back.

The raw inventory is in `source_inventory.json`. Restriction fields are recorded as raw integers; active viewport/render visibility also depends on collections, view layers and other context that must be checked in Blender.

## Do not confuse these numbers
The submitted report says **53 visible meshes and 189,972 evaluated triangles**. The offline totals above include saved experiments and count data at a different stage. They do not contradict, replace or independently verify that evaluated visible result.

## What this establishes for the task
There is real retained and experimental geometry to separate, and the source is not a tiny handful of low-resolution primitives. A method proof should address editable form control rather than assume more samples will produce likeness. Named components are useful starting identifiers; never use a vertex count as a permanent part-selection API.

## Not performed
No modifier evaluation, skin/deformation test, normals repair, render, continuous image review, proof of all hidden flags, artistic approval, or Unreal operation. The original .blend and .blend1 hashes were checked again after preparation; neither file was modified.
