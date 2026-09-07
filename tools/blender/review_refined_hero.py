"""Execute structural and rendered motion checks on one isolated refined source."""
import argparse, json, runpy, sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import sha, invariants

parser=argparse.ArgumentParser()
parser.add_argument('--unit',required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);out=args.output.resolve();uid=args.unit
refinement=json.loads((out/'refinement.json').read_text());candidate=Path(refinement['candidate'])
assert sha(candidate)==refinement['candidate_sha256']
manifest=json.loads((ROOT/f'exports/heroes/{uid}/export_manifest.json').read_text())
assert manifest['source_sha256']==refinement['source_before_sha256']
bpy.ops.wm.open_mainfile(filepath=str(candidate));arm=bpy.data.objects['Armature'];scene=bpy.context.scene
assert invariants(arm)==refinement.get('verified_candidate_invariants',refinement['preserved_invariants'])
saved=sys.argv
try:
    sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(out/'motion-invariants.json')]
    runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    sys.argv=['inspect_scene.py','--','--collection','EXPORT','--require-skin','--output',str(out/'structure-inspection.json')]
    runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
finally:sys.argv=saved
scene.render.resolution_x=scene.render.resolution_y=384;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.cycles.samples=4
scene.camera.data.ortho_scale=3.15;scene.camera.location=(3,5,2.7)
scene.camera.rotation_euler=(Vector((0,0,1.15))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
records=[]
for clip,spec in manifest['clips'].items():
    folder=out/'motion-frames'/clip;folder.mkdir(parents=True,exist_ok=False)
    frames=list(range(spec['frames'][0],spec['frames'][1],3))
    action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    for index,frame in enumerate(frames):
        scene.frame_set(frame);scene.render.filepath=str(folder/f'{index:04d}.png')
        bpy.ops.render.render(write_still=True)
    records.append({'clip':clip,'source_fps':60,'sample_step_frames':3,'playback_fps':20,
                    'duration_ms':(spec['frames'][1]-spec['frames'][0])*1000//60,
                    'frame_count':len(frames),'source_frames':frames,'frames_directory':str(folder)})
    print('WC_REFINED_HERO_MOTION_RENDERED '+uid+' '+clip,flush=True)
assert sha(candidate)==refinement['candidate_sha256']
(out/'motion-sequences.json').write_text(json.dumps({'status':'ACTUAL_RENDERED_REVIEW_SEQUENCES',
    'unit_id':uid,'candidate_sha256':sha(candidate),'clips':records,'render_size':[384,384],
    'limits':['20fps samples of authored60fps source','No continuous Unreal playback or art acceptance claim']},indent=2)+'\n')
