"""Sora4 costume-only elbow guard refinement on the actual imported source3.

Keeps the complete rest skeleton, seven action curves, textures and animation
exports unchanged. Produces fresh geometry/view evidence for Unreal reimport.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
import author_update_pippa as execution
from author_alpha import export_fbx
from refine_update_ada import components,invariants
UID='wc_u_dragonkin_guardian'
sha,write=execution.sha,execution.write

p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve()
if report.exists() or not report.is_relative_to((ROOT/'reports').resolve()):raise ValueError('Use a fresh report path')
report.mkdir(parents=True);source=ROOT/'art-source/heroes'/UID;out=ROOT/'exports/heroes'/UID
manifest=json.loads((out/'export_manifest.json').read_text())
assert manifest['source_revision'] in (3,4),'Expected the calibrated source or retained first guard revision'
revision=manifest['source_revision']+1
source_file=source/(UID+'.blend');assert sha(source_file)==manifest['source_sha256']
shutil.copytree(source,report/'before-source');shutil.copytree(out,report/'before-exports')
(report/'executed-refinement.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(source_file));current_invariants=invariants(bpy.data.objects['Armature'])
geometry_source=source_file
if revision==5:
    geometry_source=ROOT/manifest['report_directory']/'before-source'/(UID+'.blend')
    assert sha(geometry_source)==manifest['refinement_source_before_sha256'],'Expected retained Sora3 geometry'
    bpy.ops.wm.open_mainfile(filepath=str(geometry_source))
assert invariants(bpy.data.objects['Armature'])==current_invariants
scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
unit=next(u for u in json.loads((ROOT/'data/units.json').read_text())['units'] if u['id']==UID)
h=unit['height_m'];arm=bpy.data.objects['Armature'];before=invariants(arm);mesh=bpy.data.objects['SK_'+UID]
execution.use_clip(arm,manifest['clips']['Idle']);bpy.context.view_layer.update()
changes=[]
for name in ('SK_'+UID,'COSTUME_SK_'+UID):
    obj=bpy.data.objects[name];matched=[]
    for part in components(obj):
        if part['count']!=144 or len(part['groups'])!=1 or not part['groups'][0].startswith('lowerarm_'):continue
        center=Vector(part['center_m'])/h
        if abs(center.z-.615)>.00001 or abs(center.y-.008)>.00001:continue
        sign=1 if center.x>0 else -1
        bone=arm.pose.bones[part['groups'][0]]
        deform=bone.matrix@bone.bone.matrix_local.inverted();inverse=deform.inverted()
        posed_center=deform@(center*h)
        for index in part['indices']:
            vertex=obj.data.vertices[index];delta=vertex.co/h-center
            # A shallow outer elbow plate follows the existing forearm bone.
            # Keep the soft continuous sleeve beneath it; remove the round ball.
            if revision==5:
                posed=posed_center+Vector((sign*.019+delta.x*(.008/.034),delta.y*(.033/.035),delta.z*(.043/.035)))*h
                vertex.co=inverse@posed
            else:
                vertex.co=Vector((center.x+sign*.021+delta.x*(.008/.034),
                                  center.y+delta.y*(.033/.035),center.z+delta.z*(.043/.035)))*h
        selected=set(part['indices'])
        for polygon in obj.data.polygons:
            if not all(index in selected for index in polygon.vertices):continue
            polygon.use_smooth=True
            for loop in polygon.loop_indices:
                uv=obj.data.uv_layers.active.data[loop].uv
                # Preserve intra-swatch coordinates, change slate cloth to pearl armor.
                uv.x=(uv.x*4%1)/4;uv.y=(uv.y*4%1)/4
        matched.append(part['groups'][0])
    assert sorted(matched)==['lowerarm_l','lowerarm_r'],(name,matched)
    obj.data.update();changes.append(dict(object=name,guard_bones=matched,removed_ball_silhouette=True,
        outer_offset_m=.021*h,guard_half_dimensions_m=[.008*h,.033*h,.043*h]))
assert invariants(arm)==before
for level in (1,2):
    old=bpy.data.objects.get(f'SK_{UID}_LOD{level}')
    if old:
        data=old.data;bpy.data.objects.remove(old,do_unlink=True)
        if data.users==0:bpy.data.meshes.remove(data)
arm.data.pose_position='REST';execution.UID=UID
export_fbx(out/f'SK_{UID}.fbx',[arm,mesh],False);lods=execution.clean_lods(unit,mesh,arm,out)
arm.data.pose_position='POSE';clips=manifest['clips']
execution.audit_frames(arm,mesh,clips,report)
execution.render_views(unit,arm,clips,report,out);execution.render_movies(unit,arm,clips,report)
assert invariants(arm)==before,'Costume refinement changed a rig or animation curve'
for clip,spec in clips.items():assert sha(out/(spec['action']+'.fbx'))==manifest['files'][spec['action']+'.fbx']
for suffix in ('BaseColor','Normal','ORM'):
    filename=f'T_{UID}_{suffix}.png';assert sha(out/filename)==manifest['files'][filename]
execution.use_clip(arm,clips['Idle']);execution.camera_view(unit,'three-quarter')
scene.render.resolution_x=scene.render.resolution_y=768
bpy.ops.wm.save_as_mainfile(filepath=str(source_file));mesh.data.calc_loop_triangles()
updated=dict(manifest);updated.update(source_revision=revision,geometry_revision=revision,geometry_source_revision=revision,
    source_sha256=sha(source_file),triangles=len(mesh.data.loop_triangles),lods=lods,
    refinement_script_sha256=sha(__file__),refinement_source_before_sha256=manifest['source_sha256'],
    report_directory=str(report.relative_to(ROOT)),units_source_sha256=sha(ROOT/'data/units.json'),
    engine_calibration=['reports/WC-U440/20260906T170048Z/sora-engine-pilot'],
    files={path.name:sha(path) for path in sorted(out.iterdir()) if path.is_file() and path.name!='export_manifest.json'})
write(out/'export_manifest.json',updated)
write(report/'refinement.json',dict(status='COSTUME_ONLY_REFINEMENT_EXECUTED',source_before_sha256=manifest['source_sha256'],
    source_after_sha256=updated['source_sha256'],geometry_base_path=str(geometry_source),geometry_base_sha256=sha(geometry_source),
    fitted_in_actual_idle_pose=revision==5,preserved_invariants=before,verified_candidate_invariants=invariants(arm),
    exact_unchanged_animation_exports=7,exact_unchanged_texture_exports=3,changes=changes,
    engine_reimport_reference_preservation='NOT_RUN',continuous_visual_approval=False))
write(report/'completed.json',dict(status='SOURCE_EXPORT_FROZEN_PENDING_UNREAL_REIMPORT',unit_id=UID,
    source_revision=revision,source_sha256=updated['source_sha256'],export_manifest_sha256=sha(out/'export_manifest.json')))
print('WC_SORA_ELBOW_REFINED '+json.dumps(updated['source_sha256']),flush=True)
