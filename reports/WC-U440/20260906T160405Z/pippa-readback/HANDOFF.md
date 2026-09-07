# Pippa pilot source/export handoff

Pippa `wc_u_halfling_warrior` is **authored, Blender-executed and export-verified**, revision **7**, and frozen for the root-owned Unreal pilot import. This is not finished-art or packaged-play acceptance.

Source: `C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_halfling_warrior\wc_u_halfling_warrior.blend`
Source SHA256: `556a04fe6118487c8cd872e82c0c43bad5724ebbbd4fcfea6345f6adea3bcf22`
Export manifest: `C:\Users\iputu\Documents\Wonder Chess\exports\heroes\wc_u_halfling_warrior\export_manifest.json`
Manifest SHA256: `c7b2e8a1bec9fc6c6ebb899b6160187665782da4e429e5d7c11dc8238eaf03e3`

Rig: `humanoid_small` / `WC_humanoid_small_v1`,27 bones, metre source,60 fps. LOD triangles:10246 /5118 /2540. One material,1024px BaseColor/Normal/ORM,640px portrait;14 hashed export files. Curved hands and both original wooden props are weighted within the same mesh; equipment is visual only.

The fresh readback is `fbx-video-validation.json`; the companion `saved-source-fbx/published-verification.json` covers the saved mesh/skin and all3 mesh FBXs. The subsequent seven animation FBXs also imported successfully with the installed importer's offset explicitly set to0. The earlier mesh-only report correctly leaves animation FBX verification false for its narrower scope; the combined report records the later check.

Production views, snapshots and seven movies: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T160156Z\pippa`. Movies contain439 frames at60 fps (7.3167 seconds including endpoint samples). All439 actual deformed frames passed root/scale/floor checks, and both IK clamps remained0. The source remained byte-identical throughout the independent verification.

## Visual review and limits

Viewed final front/side/back/three-quarter/face/game-angle renders, both96px silhouettes, and21 sampled clip poses. The leaf club, orchard buckler, quilted green jacket, red scarf, defined adult face and curls provide authored details. Floor gap, raised freckle shapes, disconnected/angular sleeve shoulders and upward defeat gaze were corrected through retained revisions. The final96px game-angle silhouette foreshortens the club and merges part of the buckler/forearm, so actual Unreal crowd/team comparison remains open.

The seven continuous movies were generated and their frames/rates verified. This agent did not certify normal-speed continuous playback from the sparse still review. Actual Unreal material response, all clip deformation/contact, LOD silhouettes, busy combat, both team orientations, and skill/audio synchronization remain open. No final attractiveness score or finished-hero claim is assigned.

## Retained failures and fixes

Revision5 failed exact LOD FBX triangle parity. Revision6 explicit triangulation narrowed the discrepancy; the installed FBX importer calls Mesh.validate, which removed duplicate faces created by decimation. A read-only probe established4 LOD1 and20 LOD2 invalid triangles. Revision7 validates the owned reduced source meshes before export, so all3 FBXs now match exactly. Shared authoring utilities were not edited.

The first revision7 animation verifier saw imported frames2..122 because Blender5.1's FBX importer defaults anim_offset=1. Its failed run is retained. The final fresh verification uses the documented installed default override anim_offset=0 and passed all seven authored frame ranges; no source/export or runtime timing was altered for that repair.

## Next owned checkpoint

Root may import the frozen current Pippa export manifest. Require actual skeletal/portrait/material/all7-clip import checks, inspect gallery/board placement at1.12m height and replay the shield active. Finn/Nella/Milo remain unexecuted until the root releases the pilot gate. New family helper `tools/blender/halfling_production_profile.py` and Pippa author helper `tools/blender/author_update_pippa.py` are frozen/read-only inputs for that checkpoint.
