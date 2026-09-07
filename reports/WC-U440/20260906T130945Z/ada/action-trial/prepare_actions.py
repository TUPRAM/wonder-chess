"""Ada-only action trial: preserve published source and geometry while posing three clips."""
import hashlib,json,math,runpy,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector

ROOT=Path.cwd()
OUT=Path(__file__).resolve().parent
UID='wc_u_human_guardian'
SOURCE=ROOT/f'art-source/heroes/{UID}/{UID}.blend'
sys.path.insert(0,str(ROOT/'tools/blender'))
from hand_contacts import place_hand
from refine_update_ada import invariants

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def curve_hash(action):
 return digest([[c.data_path,c.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in c.keyframe_points]] for layer in action.layers for strip in layer.strips for bag in strip.channelbags for c in bag.fcurves])
def geometry_hash():
 return digest({o.name:{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'weights':[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],'uv':[[list(v.uv) for v in l.data] for l in o.data.uv_layers]} for o in bpy.data.objects if o.type=='MESH'})
def assign(arm,action,frame):
 arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
def turn(x=0,y=0,z=0):
 return Matrix.Rotation(math.radians(z),3,'Z')@Matrix.Rotation(math.radians(y),3,'Y')@Matrix.Rotation(math.radians(x),3,'X')
def lerp_pose(frame,times,values):
 for index in range(1,len(times)):
  if frame<=times[index]:
   t=(frame-times[index-1])/(times[index]-times[index-1]);t=t*t*(3-2*t)
   return values[index-1].lerp(values[index],t)
 return values[-1]

source_sha=sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+UID];scene=bpy.context.scene
old_invariants=invariants(arm);old_geometry=geometry_hash()
old_actions={a.name:curve_hash(a) for a in bpy.data.actions}
manifest=json.loads((ROOT/f'exports/heroes/{UID}/export_manifest.json').read_text())
affected=['Attack','Hit','Victory'];records=[]
for clip in affected:
 spec=manifest['clips'][clip];start,end=spec['frames'];frames=sorted(set(range(start,end+1,3))|{end})
 original=bpy.data.actions[spec['action']]
 assign(arm,original,start)
 anchor={side:arm.pose.bones['hand_'+side].tail.copy() for side in ('l','r')}
 shoulder_anchor=arm.pose.bones['upperarm_l'].head.copy()
 base_rotation={side:arm.pose.bones['hand_'+side].matrix.to_3x3()@arm.pose.bones['hand_'+side].bone.matrix_local.to_3x3().inverted() for side in ('l','r')}
 baseline={}
 for frame in frames:
  assign(arm,original,frame)
  baseline[frame]={b.name:(b.location.copy(),b.rotation_euler.copy(),b.scale.copy()) for b in arm.pose.bones}
 idle=bpy.data.actions[f'AN_{UID}_Idle'];assign(arm,idle,1)
 idle_right={name:(arm.pose.bones[name].location.copy(),arm.pose.bones[name].rotation_euler.copy()) for name in ('upperarm_r','lowerarm_r','hand_r')}
 new_action=original.copy();new_action.use_fake_user=True
 original_name=original.name;original.name='TRIAL_BASELINE_'+original_name
 new_action.name=original_name
 changed=['upperarm_r','lowerarm_r','hand_r'] if clip=='Attack' else ['upperarm_l','lowerarm_l','hand_l']
 if clip=='Victory':changed+=['upperarm_r','lowerarm_r','hand_r']
 for layer in new_action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in list(bag.fcurves):
     if any(f'pose.bones["{name}"]' in curve.data_path for name in changed):bag.fcurves.remove(curve)
 assign(arm,new_action,start)
 max_clamp=0
 for frame in frames:
  scene.frame_set(frame)
  for name,(location,rotation,scale) in baseline[frame].items():
   bone=arm.pose.bones[name];bone.location=location;bone.rotation_euler=rotation;bone.scale=scale
  bpy.context.view_layer.update()
  amount=max(0,math.sin(math.pi*(frame-start)/(end-start)))
  if clip=='Attack':
   times=[1,8,16,25,40]
   palm=lerp_pose(frame,times,[anchor['r'],Vector((-.46,.10,1.11)),Vector((-.40,.43,1.05)),Vector((-.48,.30,.92)),anchor['r']])
   angles=lerp_pose(frame,times,[Vector((0,0,0)),Vector((0,-28,0)),Vector((-12,75,0)),Vector((-6,38,0)),Vector((0,0,0))])
   rotation=base_rotation['r']@turn(*angles)
   max_clamp=max(max_clamp,place_hand(arm,'r',palm,rotation,1.82))
  else:
   offset=Vector((-.025,.015,-.025)) if clip=='Hit' else Vector((-.05,.05,.11))
   rotation=base_rotation['l']@turn(0,-7*amount,0)
   shoulder_follow=arm.pose.bones['upperarm_l'].head-shoulder_anchor
   max_clamp=max(max_clamp,place_hand(arm,'l',anchor['l']+shoulder_follow+offset*amount,rotation,1.82))
   if clip=='Victory':
    for name,(location,rotation) in idle_right.items():
     arm.pose.bones[name].location=location;arm.pose.bones[name].rotation_euler=rotation
  for name in changed:
   arm.pose.bones[name].keyframe_insert(data_path='location',frame=frame,group=name)
   arm.pose.bones[name].keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
 for layer in new_action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     if any(f'pose.bones["{name}"]' in curve.data_path for name in changed):
      for key in curve.keyframe_points:key.interpolation='LINEAR'
 bpy.data.actions.remove(original)
 widths=[];eye_clearances=[]
 for frame in frames:
  assign(arm,new_action,frame)
  evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());deformed=evaluated.to_mesh()
  try:
   coords=[evaluated.matrix_world@v.co for v in deformed.vertices]
   widths.append(max(v.x for v in coords)-min(v.x for v in coords))
   eyes=min(coords[i].z for i in list(range(1121,1127))+list(range(1194,1200)))
   shield=max(coords[i].z for i in range(2097,2517))
   eye_clearances.append(eyes-shield)
  finally:evaluated.to_mesh_clear()
 records.append({'clip':clip,'frames':spec['frames'],'release_frame':spec['release_frame'],'max_reach_clamp_m':max_clamp,'max_width_m':max(widths),'minimum_eye_above_shield_m':min(eye_clearances)})
 if max_clamp>.025:raise RuntimeError(f'{clip}: support reach clamp {max_clamp}')
 if max(widths)>2:raise RuntimeError(f'{clip}: exceeds one-cell-width silhouette')
 if clip in ('Hit','Victory') and min(eye_clearances)<.035:raise RuntimeError(f'{clip}: shield intrudes into eye line')

assert geometry_hash()==old_geometry
assert invariants(arm)['rest_skeleton_sha256']==old_invariants['rest_skeleton_sha256']
for name,old in old_actions.items():
 if name.rsplit('_',1)[-1] not in affected:assert curve_hash(bpy.data.actions[name])==old
candidate=OUT/'ada-action-revision8-trial.blend'
assign(arm,bpy.data.actions[f'AN_{UID}_Idle'],1)
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),check_existing=False)
saved=sys.argv
try:
 sys.argv=['audit_motion.py','--','--unit',UID,'--output',str(OUT/'motion-invariants.json')]
 runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
finally:sys.argv=saved
scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.cycles.samples=6;scene.render.image_settings.file_format='PNG'
scene.camera.data.ortho_scale=2.7;scene.camera.location=(3,5,2.7)
scene.camera.rotation_euler=(Vector((0,0,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
for clip in affected:
 folder=OUT/clip;folder.mkdir(exist_ok=True);spec=manifest['clips'][clip]
 for index,frame in enumerate(range(spec['frames'][0],spec['frames'][1],3)):
  assign(arm,bpy.data.actions[spec['action']],frame)
  scene.render.filepath=str(folder/f'{index:04d}.png');bpy.ops.render.render(write_still=True)
 print('WC_ADA_ACTION_TRIAL_RENDERED '+clip,flush=True)
assert sha(SOURCE)==source_sha
(OUT/'result.json').write_text(json.dumps({'status':'BLENDER_ACTION_TRIAL_EXECUTED_NOT_PROMOTED','published_source_sha256':source_sha,'candidate':str(candidate),'candidate_sha256':sha(candidate),'geometry_unchanged':True,'rest_skeleton_unchanged':True,'unchanged_clips':['Idle','Move','Active','Defeat'],'changed_clips':records,'runtime_release_timing_unchanged':True,'production_source_unchanged':True,'Unreal_import_run':False},indent=2)+'\n')
print('WC_ADA_ACTION_TRIAL_COMPLETE',flush=True)
