"""Read saved Dragonkin source, all ten FBXs and actual seven recorded movies.

No source, export or Unreal asset mutation. Technical evidence cannot approve art.
"""
import argparse
import json
from pathlib import Path
import runpy
import sys
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from author_update_pippa import sha,write,camera_view,use_clip
from dragonkin_production_profile import RIG_REVISION
from refine_update_ada import invariants,action_curve_digest
VERIFIER_SHA=sha(__file__)

p=argparse.ArgumentParser();p.add_argument('--unit',choices=('wc_u_dragonkin_guardian',),required=True)
p.add_argument('--report',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
uid=a.unit;report=a.report.resolve()
if report.exists() or not report.is_relative_to((ROOT/'reports').resolve()):raise ValueError('Use fresh reports path')
report.mkdir(parents=True);(report/'executed-verifier.py').write_bytes(Path(__file__).read_bytes())
out=ROOT/'exports/heroes'/uid;source=ROOT/'art-source/heroes'/uid/(uid+'.blend');before=sha(source)
sys.argv=['verify_new_family_hero.py','--','--unit',uid,'--report',str(report/'saved-source-fbx')]
runpy.run_path(str(ROOT/'tools/blender/verify_new_family_hero.py'),run_name='__main__')
manifest=json.loads((out/'export_manifest.json').read_text());clips=[];preserved=None
prior=ROOT/manifest['report_directory']/'before-source'/(uid+'.blend')
if prior.exists() and manifest['source_revision']==3:
    signatures=[]
    for candidate in (prior,source):
        bpy.ops.wm.open_mainfile(filepath=str(candidate));arm=bpy.data.objects['Armature']
        signatures.append(dict(rest=invariants(arm)['rest_skeleton_sha256'],
            actions={name:action_curve_digest(bpy.data.actions[spec['action']]) for name,spec in manifest['clips'].items()}))
    assert signatures[0]['rest']==signatures[1]['rest'],'Refinement changed calibrated rest skeleton'
    changed=[name for name in manifest['clips'] if signatures[0]['actions'][name]!=signatures[1]['actions'][name]]
    assert changed==['Active'],('Unexpected changed actions',changed)
    preserved=dict(status='PASS_REST_AND_SIX_ACTIONS_UNCHANGED',before_source_sha256=sha(prior),
        rest_skeleton_sha256=signatures[1]['rest'],changed_actions=changed)
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
assert arm.data.name==RIG_REVISION
unit=next(u for u in json.loads((ROOT/'data/units.json').read_text())['units'] if u['id']==uid)
use_clip(arm,manifest['clips']['Active'],manifest['clips']['Active']['release_frame'])
weapon=arm.pose.bones['weapon_l']
shield_front=(weapon.matrix@weapon.bone.matrix_local.inverted()).to_3x3()@Vector((0,1,0))
write(report/'semantic-check.json',dict(status='PASS' if shield_front.z>.25 else 'FAIL',
    check='actual shield outward normal tilts upward at active release',normal=list(shield_front),
    source_sha256=before,minimum_upward_component=.25))
assert shield_front.z>.25, 'Beacon Shield must tilt its actual outward face upward at release'
semantic=dict(active_release_frame=manifest['clips']['Active']['release_frame'],
    shield_front_normal_at_release=list(shield_front),shield_upward_tilt_verified=True,
    continuous_gesture_quality_approved=False)
use_clip(arm,manifest['clips']['Idle']);scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='FLAT';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(0,0,0)
scene.display.shading.background_type='WORLD';scene.world.color=(1,1,1)
scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False
bpy.data.objects['PRESENTATION_Ground'].hide_render=True
scene.render.film_transparent=False;scene.render.resolution_x=scene.render.resolution_y=96
scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard';silhouettes=[]
for view in ('front','game-angle'):
    camera_view(unit,view);scene.render.filepath=str(report/f'silhouette96-{view}.png');bpy.ops.render.render(write_still=True)
    image=bpy.data.images.load(scene.render.filepath,check_existing=False);pixels=list(image.pixels)
    dark=sum(max(pixels[i:i+3])<.15 for i in range(0,len(pixels),4));light=sum(min(pixels[i:i+3])>.8 for i in range(0,len(pixels),4))
    assert list(image.size)==[96,96] and 100<dark<96*96*.75 and light>96*96*.20,'Invalid silhouette foreground/background'
    silhouettes.append(dict(view=view,path=scene.render.filepath,sha256=sha(scene.render.filepath),dark_pixels=dark,light_pixels=light))
    bpy.data.images.remove(image)
assert sha(source)==before==manifest['source_sha256']
assert sha(__file__)==VERIFIER_SHA,'Verification script changed during execution'
result=dict(status='PASS_ACTUAL_BLENDER_FBX_AND_VIDEO_READBACK',unit_id=uid,source_revision=manifest['source_revision'],
    source_sha256=before,export_manifest_sha256=sha(out/'export_manifest.json'),blender_version=bpy.app.version_string,clips=clips,
    recorded_frames=sum(row['video_frames'] for row in clips),recorded_seconds=sum(row['video_frames']/row['video_fps'] for row in clips),
    rig_revision=RIG_REVISION,source_modified=False,Unreal_import_verified=False,continuous_visual_approval=False,
    finished_art_accepted=False,silhouettes=silhouettes,semantic_geometry=semantic,preserved=preserved,verification_script_sha256=VERIFIER_SHA)
write(report/'fbx-video-validation.json',result)
print('WC_DRAGONKIN_READBACK '+json.dumps({k:v for k,v in result.items() if k!='clips'}),flush=True)
