from pathlib import Path
import hashlib,json
root=Path.cwd(); out=root/'exports/heroes/wc_u_dragonkin_guardian'; base=root/'reports/WC-U440/20260906T165532Z/dragonkin'
m=json.loads((out/'export_manifest.json').read_text()); v=json.loads((base/'sora-readback/fbx-video-validation.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(out/name)==value for name,value in m['files'].items())
source=root/'art-source/heroes/wc_u_dragonkin_guardian/wc_u_dragonkin_guardian.blend'
assert sha(source)==m['source_sha256']==v['source_sha256']
r={'status':'SOURCE_EXPORT_TECHNICAL_HANDOFF_UNREAL_AND_CONTINUOUS_ART_GATES_OPEN','unit_id':m['unit_id'],'source_revision':3,'source_path':str(source),'source_sha256':sha(source),'export_manifest_path':str(out/'export_manifest.json'),'export_manifest_sha256':sha(out/'export_manifest.json'),'authoring_units_sha256':m['units_source_sha256'],'rig_revision':m['rig_revision'],'rig_calibration':str(base/'sora/rig-calibration.json'),'bones':27,'lod_triangles':[m['triangles']]+[x['triangles'] for x in m['lods']],'clips':m['clips'],'file_sha256':m['files'],'readback_report':str(base/'sora-readback/fbx-video-validation.json'),'video_frames':v['recorded_frames'],'video_seconds':v['recorded_seconds'],'reviewed_sparse_views':6,'reviewed_sparse_poses':21,'reviewed_96px_silhouettes':2,'continuous_normal_speed_visual_review':False,'Unreal_import_review':False,'source_revision_reimport_references':False,'finished_art_accepted':False,'owned_tool_sha256':{p.name:sha(p) for p in [root/'tools/blender/author_update_dragonkin.py',root/'tools/blender/dragonkin_production_profile.py',root/'tools/blender/verify_update_dragonkin.py']},'semantic_fix':v['semantic_geometry'],'preserved':v['preserved'],'failed_semantic_fixture':str(root/'reports/WC-U440/20260906T165204Z/dragonkin/sora-negative-semantic-fixture/semantic-check.json')}
p=base/'HANDOFF.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
p=base/'HANDOFF.md';assert not p.exists();p.write_text('''# Sora Dragonkin pilot — source/export handoff

Sora revision 3 is frozen for parent-owned Unreal import. This is authored and executed Blender source with actual FBX/movie readback; it does not certify finished art, continuous motion approval or playable packaged content.

- Source: `art-source/heroes/wc_u_dragonkin_guardian/wc_u_dragonkin_guardian.blend`.
- Source SHA256: `'''+m['source_sha256']+'''`.
- Export manifest: `exports/heroes/wc_u_dragonkin_guardian/export_manifest.json`.
- Manifest SHA256: `'''+sha(out/'export_manifest.json')+'''`.
- Actual Blender 5.1.1, four render threads; one own Blender process at a time.
- Separate rig `WC_humanoid_draconic_v1`, 27 established bone names and sockets, separately measured draconic neck/head/shoulders. Actual rest matrices, head/tail coordinates and hierarchy are in `sora/rig-calibration.json`. Same names do not establish compatibility.
- Meter source, +Y forward, +Z up; FBX exported through frozen independent-centimeter-copy profile. No source/actor scale workaround claimed.
- LOD0/1/2: 8474 / 4234 / 2095 triangles; one material, one UV layer. Three 1024-pixel texture maps, one model-derived 640-pixel portrait, three mesh FBXs and seven animation FBXs. Fourteen exact output hashes are in HANDOFF.json and the export manifest.

## Changes and actual inspection

Built an integrated 216-vertex skull/muzzle surface, fitted concentric eye/iris/pupil/glint layers and lids/brows to that actual surface, short swept horns, compact neck crest and throat scales. Broad pale ceremonial armor, royal-blue panels, articulated arm armor with soft visible joints, an engraved oval beacon shield and short blunt fluted mace retain the authored identity. Feet are plantigrade; no wings, tail, copied human head, hidden inventory or stat gear.

The first source exposed sharply folded arm armor. Revision 2 separates rigid upper-arm/forearm sections and smooth joints; revision 3 also curves the horns and lowers the undersleeve below the closed pauldron top. Actual front, side, back, face, three-quarter and gameplay-angle views were inspected. All 21 start/release-or-middle/end poses were inspected via actual renders; their hash-bound montages are `sora/actual-pose-grid-1.png` and `-2.png`. Two actual 96-pixel silhouettes were inspected. Sparse samples do not prove normal-speed continuous quality, all inter-frame clearances or crowded-board readability.

## Executed verification

Production exit 0 and independent verifier exit 0. `sora-readback/fbx-video-validation.json` binds the unchanged saved source and every export. All three mesh FBXs were actually reimported with matching dimensions, triangles, bones, materials, UVs and weighted vertices. All seven animation FBXs were actually reimported using explicit `anim_offset=0.0`; their frame ranges match source.

All 439 authored frames were evaluated for deformed geometry, root and bone scale. Hand and foot IK clamp are zero in every clip. Lowest source geometry stays approximately +2.08 mm above the floor; root translation and scale error are zero. Seven actual MP4 files read back at 384×384 and 60 FPS: 439 total frames, 7.316667 seconds including each clip endpoint. Video metadata verification is not continuous visual approval.

| Clip | Inclusive source frames | Release frame |
|---|---:|---:|
| Idle | 1–121 | — |
| Move | 1–61 | — |
| Attack | 1–40 | 16 (250 ms) |
| Active | 1–40 | 22 (350 ms) |
| Hit | 1–25 | — |
| Defeat | 1–61 | — |
| Victory | 1–91 | — |

The source's previous negative-X active tilt faced the shield downward. The actual r2 fixture failed with outward-normal Z = -0.529919. The corrected r3 source passes at +0.406737; the check reads the actual deformed weapon bone at release. Exact rest skeleton and all six unaffected action curves remain unchanged; only Active changed. This fixes presentation without changing canonical timing or rules.

## Retained failures and boundaries

- Revision 1 and 2 source/export inputs remain under the next revision's `before-source` and `before-exports`, with their original reports at `20260906T164907Z` and `20260906T165204Z`.
- The first semantic audit used Blender's default Python-error behavior, which returned process 0 despite the recorded AssertionError. It is a failed semantic audit, not a pass. The fresh repeated fixture explicitly used `--python-exit-code 2`, retained exit 2 and wrote `sora-negative-semantic-fixture/semantic-check.json`. Final production and verification explicitly use that fail-closed switch.
- LOD generation logged duplicate-face diagnostics, then removed 2 / 22 invalid triangles before final export. Actual clean FBX readbacks match final counts. Those diagnostics are preserved; no failed artifact was relabeled.
- Parent-owned Unreal family calibration, cold load, actual gallery/board footage, material/skeleton/animation/actor reference preservation through a deliberate costume reimport, continuous seven-clip art review, neighbor overlaps, LOD silhouettes, effects/audio synchronization and frame-time measurement remain open.
- Sora's muzzle is intentionally subtle head-on but projects clearly in the actual side view. Elbow/cuff transitions and broad armor shapes still merit close continuous and game-camera review; no finished-hero claim is made.

No shared rig/material, frozen preparation helper, canonical data, existing hero or Unreal binary was modified in this lane. Varek, Iri and Oren production remain gated until the parent releases them after Sora's engine pilot.
''',encoding='utf-8')
print(p)
