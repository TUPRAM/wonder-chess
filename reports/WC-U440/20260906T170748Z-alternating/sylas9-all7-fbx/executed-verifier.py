"""Independently import selected actual animation FBXs without editing sources."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--unit',required=True);p.add_argument('--clips',nargs='+',required=True);p.add_argument('--report',type=Path,required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=args.report.resolve();out.mkdir(parents=True,exist_ok=False);folder=ROOT/f'exports/heroes/{args.unit}';m=json.loads((folder/'export_manifest.json').read_text());rows=[]
for clip in args.clips:
    spec=m['clips'][clip];path=folder/(spec['action']+'.fbx');assert hashlib.sha256(path.read_bytes()).hexdigest()==m['files'][path.name];bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=60;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.import_scene.fbx(filepath=str(path),use_anim=True,anim_offset=0)
    arms=[o for o in scene.objects if o.type=='ARMATURE'];assert len(arms)==1 and len(bpy.data.actions)==1;arm=arms[0];action=bpy.data.actions[0];assert len(arm.data.bones)==m['bones'];assert list(action.frame_range)==spec['frames'];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    for frame in range(spec['frames'][0],spec['frames'][1]+1):
        scene.frame_set(frame);assert all(math.isfinite(c) for bone in arm.pose.bones for row in bone.matrix for c in row)
    rows.append({'clip':clip,'frames':spec['frames'],'fps':60,'bones':len(arm.data.bones),'frames_evaluated':spec['frames'][1]-spec['frames'][0]+1,'fbx_sha256':m['files'][path.name]})
record={'status':'PASS_ACTUAL_ANIMATION_FBX_READBACK','unit_id':args.unit,'source_revision':m['source_revision'],'animation_revision':m['animation_revision'],'source_sha256':m['source_sha256'],'blender_version':bpy.app.version_string,'clips':rows,'limits':['Actual imported frame range, bone count and finite pose verification','Not continuous visual or Unreal acceptance']};(out/'animation-fbx-readback.json').write_text(json.dumps(record,indent=2)+'\n');(out/'executed-verifier.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(record))
