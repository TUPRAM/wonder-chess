"""Executed saved-source/FBX/video readback; no source/export modifications."""
import hashlib,json,runpy,sys
from pathlib import Path
import bpy
ROOT=Path(r'C:/Users/iputu/Documents/Wonder Chess')
REPORT=Path(__file__).resolve().parent
UID='wc_u_halfling_warrior'
EXPORT=ROOT/'exports/heroes'/UID
SOURCE=ROOT/'art-source/heroes'/UID/(UID+'.blend')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
before=sha(SOURCE)
sys.argv=['verify_new_family_hero.py','--','--unit',UID,'--report',str(REPORT/'saved-source-fbx')]
runpy.run_path(str(ROOT/'tools/blender/verify_new_family_hero.py'),run_name='__main__')
manifest=json.loads((EXPORT/'export_manifest.json').read_text())
clips=[]
for name,spec in manifest['clips'].items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps=60
    bpy.ops.import_scene.fbx(filepath=str(EXPORT/(spec['action']+'.fbx')),use_anim=True,anim_offset=0.0)
    arms=[obj for obj in bpy.context.scene.objects if obj.type=='ARMATURE']
    assert len(arms)==1 and len(arms[0].data.bones)==27,name
    action=arms[0].animation_data.action
    assert action and abs(action.frame_range[0]-1)<.01 and abs(action.frame_range[1]-spec['frames'][1])<.01,(name,action.frame_range[:])
    path=ROOT/'reports/WC-U440/20260906T160156Z/pippa'/('continuous-'+name+'.mp4')
    movie=bpy.data.movieclips.load(str(path))
    assert movie.fps==60 and movie.frame_duration==spec['frames'][1] and list(movie.size)==[384,384],name
    clips.append(dict(clip=name,fbx_sha256=sha(EXPORT/(spec['action']+'.fbx')),imported_action=action.name,imported_frames=list(action.frame_range),bones=len(arms[0].data.bones),video_path=str(path),video_sha256=sha(path),video_frames=movie.frame_duration,video_fps=movie.fps,video_dimensions=list(movie.size)))
    bpy.data.movieclips.remove(movie)
assert sha(SOURCE)==before==manifest['source_sha256']
result=dict(status='PASS_ACTUAL_BLENDER_FBX_AND_VIDEO_READBACK',unit_id=UID,source_revision=manifest['source_revision'],source_sha256=before,export_manifest_sha256=sha(EXPORT/'export_manifest.json'),blender_version=bpy.app.version_string,clips=clips,recorded_frames=sum(row['video_frames'] for row in clips),recorded_seconds=sum(row['video_frames']/row['video_fps'] for row in clips),source_modified=False,Unreal_import_verified=False,continuous_visual_approval=False,finished_art_accepted=False)
(REPORT/'fbx-video-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('WC_PIPPA_READBACK '+json.dumps({k:v for k,v in result.items() if k!='clips'}),flush=True)

