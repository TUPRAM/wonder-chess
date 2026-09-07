"""Repair retained-source texture links without changing Sora5 geometry/actions."""
import argparse,json,shutil,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
import author_update_pippa as execution
from author_alpha import export_fbx
from refine_update_ada import invariants,mesh_geometry_digest
UID='wc_u_dragonkin_guardian';sha,write=execution.sha,execution.write
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve()
if report.exists() or not report.is_relative_to((ROOT/'reports').resolve()):raise ValueError('Fresh report required')
report.mkdir(parents=True);source=ROOT/'art-source/heroes'/UID;out=ROOT/'exports/heroes'/UID
m=json.loads((out/'export_manifest.json').read_text());assert m['source_revision']==5
file=source/(UID+'.blend');assert sha(file)==m['source_sha256']
shutil.copytree(source,report/'before-source');shutil.copytree(out,report/'before-exports')
(report/'executed-repair.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(file));arm=bpy.data.objects['Armature'];before=invariants(arm);geometry=mesh_geometry_digest()
links=[]
for suffix in ('BaseColor','Normal','ORM'):
    name=f'T_{UID}_{suffix}';path=out/(name+'.png')
    assert sha(path)==m['files'][path.name]
    image=bpy.data.images[name];previous=image.filepath
    image.filepath=str(path);image.reload()
    assert Path(bpy.path.abspath(image.filepath)).is_file() and list(image.size)==[1024,1024]
    links.append(dict(image=name,old_path=previous,current_path=str(path),sha256=sha(path)))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
unit=next(u for u in json.loads((ROOT/'data/units.json').read_text())['units'] if u['id']==UID)
arm.data.pose_position='REST'
for suffix in ('','_LOD1','_LOD2'):export_fbx(out/('SK_'+UID+suffix+'.fbx'),[arm,bpy.data.objects['SK_'+UID+suffix]],False)
arm.data.pose_position='POSE';clips=m['clips'];execution.audit_frames(arm,bpy.data.objects['SK_'+UID],clips,report)
execution.render_views(unit,arm,clips,report,out);execution.render_movies(unit,arm,clips,report)
assert invariants(arm)==before and mesh_geometry_digest()==geometry
for spec in clips.values():assert sha(out/(spec['action']+'.fbx'))==m['files'][spec['action']+'.fbx']
execution.use_clip(arm,clips['Idle']);execution.camera_view(unit,'three-quarter');scene.render.resolution_x=scene.render.resolution_y=768
bpy.ops.wm.save_as_mainfile(filepath=str(file))
updated=dict(m);updated.update(source_revision=6,source_sha256=sha(file),report_directory=str(report.relative_to(ROOT)),
    texture_link_repair_script_sha256=sha(__file__),
    files={path.name:sha(path) for path in sorted(out.iterdir()) if path.is_file() and path.name!='export_manifest.json'})
write(out/'export_manifest.json',updated)
write(report/'repair.json',dict(status='TEXTURE_LINK_REPAIR_EXECUTED',source_before_sha256=m['source_sha256'],
    source_after_sha256=updated['source_sha256'],links=links,exact_geometry_digest=geometry,
    preserved_invariants=before,verified_candidate_invariants=invariants(arm),exact_animation_exports_unchanged=7,
    geometry_note='Guards are the Sora5 fit, with no geometry change in this texture-link repair',
    prior_metadata_correction='Sora5 nominal outer_offset_m field was copied from r4; actual executed r5 offset was 0.019*2.08=0.03952 m. No geometry or acceptance decision uses that metadata field.',
    continuous_visual_approval=False,Unreal_reimport=False))
write(report/'completed.json',dict(status='SOURCE_EXPORT_FROZEN_PENDING_UNREAL_REIMPORT',source_revision=6,
    source_sha256=updated['source_sha256'],export_manifest_sha256=sha(out/'export_manifest.json')))
print('WC_SORA_TEXTURE_LINKS_REPAIRED '+updated['source_sha256'],flush=True)
