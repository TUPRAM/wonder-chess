"""Re-export executed meter sources through the measured centimeter-copy profile."""
import bpy,json,hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_alpha import export_fbx_raw as export_fbx
from normalized_fbx import export_normalized_copy
profile_path=root/'tools/blender/profiles/fbx_skeletal_cm_v1.json'
profile=json.loads(profile_path.read_text())
if profile['calibration_status']!='measured_pass':raise RuntimeError('Production reexport requires the measured complete profile')
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids'];records=[]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for uid in ids:
    source=root/f'art-source/heroes/{uid}/{uid}.blend';out=root/f'exports/heroes/{uid}'
    source_hash=sha(source);manifest_path=out/'export_manifest.json';manifest=json.loads(manifest_path.read_text())
    if source_hash!=manifest['source_sha256']:raise RuntimeError(f'{uid}: source changed after last authored manifest')
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
    if abs(scene.unit_settings.scale_length-1)>1e-8:raise RuntimeError(f'{uid}: source units are not meters')
    arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid]
    initial_action=arm.animation_data.action;initial_frame=scene.frame_current
    bones_before={b.name:(list(b.head_local),list(b.tail_local)) for b in arm.data.bones}
    mesh_before=[list(v.co) for v in mesh.data.vertices]
    export_normalized_copy(out/f'SK_{uid}.fbx',[arm,mesh],False,export_fbx)
    for index in (1,2):
        lod=bpy.data.objects[f'SK_{uid}_LOD{index}']
        export_normalized_copy(out/f'SK_{uid}_LOD{index}.fbx',[arm,lod],False,export_fbx)
    for clip,spec in manifest['clips'].items():
        action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
        scene.frame_start=spec['frames'][0];scene.frame_end=spec['frames'][1];scene.frame_set(scene.frame_start)
        export_normalized_copy(out/f'AN_{uid}_{clip}.fbx',[arm],True,export_fbx)
    arm.animation_data.action=initial_action;arm.animation_data.action_slot=initial_action.slots[0];scene.frame_set(initial_frame)
    bones_after={b.name:(list(b.head_local),list(b.tail_local)) for b in arm.data.bones}
    if bones_before!=bones_after or mesh_before!=[list(v.co) for v in mesh.data.vertices] or source_hash!=sha(source):
        raise RuntimeError(f'{uid}: normalization changed the authoring source')
    manifest['fbx_profile']=str(profile_path.relative_to(root));manifest['normalized_export_revision']=1
    manifest['normalized_exporter_sha256']=sha(root/'tools/blender/normalized_fbx.py')
    manifest['normalized_reexport_script_sha256']=sha(Path(__file__))
    manifest['exported_coordinate_units']='centimeters: temporary geometry, rest translation and animation location values multiplied by100; authoring source remains meters'
    manifest['engine_calibration']=profile['evidence']
    manifest['status']='authored_rendered_normalized_exported_pending_current_engine_and_visual_acceptance'
    manifest['files']={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='export_manifest.json'}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    records.append({'unit_id':uid,'source_sha256':source_hash,'source_unchanged':True,'source_revision':manifest['source_revision'],
                    'exported_meshes':3,'exported_animations':7,'manifest_sha256':sha(manifest_path)})
    print('WC_NORMALIZED_HERO_COMPLETE '+uid,flush=True)
report={'status':'all_twelve_normalized_exports_executed','profile':profile,'records':records,
        'mesh_exports':sum(r['exported_meshes'] for r in records),'animation_exports':sum(r['exported_animations'] for r in records)}
(root/'reports/WC-330/normalized-roster-export.json').write_text(json.dumps(report,indent=2)+'\n')
print('WC_NORMALIZED_ROSTER_COMPLETE',len(records),flush=True)
