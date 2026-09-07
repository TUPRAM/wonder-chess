"""Read-only saved-source, actual FBX and video verification for released Halflings."""
import argparse
import json
from pathlib import Path
import runpy
import sys
import bpy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_update_pippa import sha,write,camera_view,use_clip
from refine_update_ada import invariants,digest
VERIFIER_SHA=sha(__file__)

p=argparse.ArgumentParser();p.add_argument('--unit',choices=('wc_u_halfling_ranger','wc_u_halfling_rogue','wc_u_halfling_mage'),required=True)
p.add_argument('--report',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
uid=a.unit;report=a.report.resolve()
if report.exists() or not report.is_relative_to((ROOT/'reports').resolve()):raise ValueError('Use fresh reports path')
report.mkdir(parents=True)
(report/'executed-verifier.py').write_bytes(Path(__file__).read_bytes())
out=ROOT/'exports/heroes'/uid;source=ROOT/'art-source/heroes'/uid/(uid+'.blend')
before=sha(source)
sys.argv=['verify_new_family_hero.py','--','--unit',uid,'--report',str(report/'saved-source-fbx')]
runpy.run_path(str(ROOT/'tools/blender/verify_new_family_hero.py'),run_name='__main__')
manifest=json.loads((out/'export_manifest.json').read_text());clips=[];preserved=None
prior=ROOT/manifest['report_directory']/'before-source'/(uid+'.blend')
if prior.exists():
    signatures=[]
    for candidate in (prior,source):
        bpy.ops.wm.open_mainfile(filepath=str(candidate));arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid]
        palette={}
        for polygon in mesh.data.polygons:
            uv=mesh.data.uv_layers.active.data[polygon.loop_start].uv
            for index in polygon.vertices:palette[index]=int(uv.x*4)+4*int(uv.y*4)
        retained=[]
        for vertex in mesh.data.vertices:
            weights=sorted((mesh.vertex_groups[group.group].name,round(group.weight,7)) for group in vertex.groups)
            if any(name=='head' for name,weight in weights):continue
            retained.append((tuple(round(value,7) for value in vertex.co),palette[vertex.index],weights))
        signatures.append(dict(animation_and_rig=invariants(arm),non_head_vertices=len(retained),non_head_geometry_sha256=digest(sorted(retained))))
    face_revisions={'wc_u_halfling_ranger':5,'wc_u_halfling_rogue':3,'wc_u_halfling_mage':2}
    if manifest['source_revision']==face_revisions[uid]:
        assert signatures[0]==signatures[1], 'Face-only revision changed prior rig/actions/non-head geometry'
        preserved=dict(status='PASS_EXACT_RETAINED_ACTIONS_RIG_AND_NON_HEAD_GEOMETRY',before_source_sha256=sha(prior),signature=signatures[1])
for name,spec in manifest['clips'].items():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=60
    bpy.ops.import_scene.fbx(filepath=str(out/(spec['action']+'.fbx')),use_anim=True,anim_offset=0.0)
    arms=[obj for obj in bpy.context.scene.objects if obj.type=='ARMATURE']
    assert len(arms)==1 and len(arms[0].data.bones)==27,name
    action=arms[0].animation_data.action
    assert action and abs(action.frame_range[0]-1)<.01 and abs(action.frame_range[1]-spec['frames'][1])<.01,(name,action.frame_range[:])
    path=ROOT/manifest['report_directory']/('continuous-'+name+'.mp4')
    movie=bpy.data.movieclips.load(str(path))
    assert movie.fps==60 and movie.frame_duration==spec['frames'][1] and list(movie.size)==[384,384],name
    clips.append(dict(clip=name,fbx_sha256=sha(out/(spec['action']+'.fbx')),imported_action=action.name,imported_frames=list(action.frame_range),
        bones=len(arms[0].data.bones),video_path=str(path),video_sha256=sha(path),video_frames=movie.frame_duration,video_fps=movie.fps,video_dimensions=list(movie.size)))
    bpy.data.movieclips.remove(movie)
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;arm=bpy.data.objects['Armature']
unit=next(u for u in json.loads((ROOT/'data/units.json').read_text())['units'] if u['id']==uid)
use_clip(arm,manifest['clips']['Idle']);scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='FLAT';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(0,0,0)
scene.display.shading.background_type='WORLD';scene.world.color=(1,1,1)
scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False
bpy.data.objects['PRESENTATION_Ground'].hide_render=True
scene.render.film_transparent=False;scene.render.resolution_x=scene.render.resolution_y=96
scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
silhouettes=[]
for view in ('front','game-angle'):
    camera_view(unit,view);scene.render.filepath=str(report/f'silhouette96-{view}.png');bpy.ops.render.render(write_still=True)
    image=bpy.data.images.load(scene.render.filepath,check_existing=False);pixels=list(image.pixels)
    dark=sum(max(pixels[i:i+3])<.15 for i in range(0,len(pixels),4));light=sum(min(pixels[i:i+3])>.8 for i in range(0,len(pixels),4))
    assert list(image.size)==[96,96] and 100<dark<96*96*.75 and light>96*96*.20, 'Silhouette lacks a separated foreground/background'
    silhouettes.append(dict(view=view,path=scene.render.filepath,sha256=sha(scene.render.filepath),dark_pixels=dark,light_pixels=light))
    bpy.data.images.remove(image)
assert sha(source)==before==manifest['source_sha256']
result=dict(status='PASS_ACTUAL_BLENDER_FBX_AND_VIDEO_READBACK',unit_id=uid,source_revision=manifest['source_revision'],
    source_sha256=before,export_manifest_sha256=sha(out/'export_manifest.json'),blender_version=bpy.app.version_string,clips=clips,
    recorded_frames=sum(row['video_frames'] for row in clips),recorded_seconds=sum(row['video_frames']/row['video_fps'] for row in clips),
    source_modified=False,Unreal_import_verified=False,continuous_visual_approval=False,finished_art_accepted=False)
result['face_refinement_preserved']=preserved
result['silhouettes']=silhouettes
assert sha(__file__)==VERIFIER_SHA, 'Verification script changed during execution'
result['verification_script_sha256']=VERIFIER_SHA
write(report/'fbx-video-validation.json',result)
print('WC_HALFLING_READBACK '+json.dumps({k:v for k,v in result.items() if k!='clips'}),flush=True)
