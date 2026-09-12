import bpy,json,hashlib,ast,numpy as np,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1];B4=R.parents[1]/'BW4/r001/armor';src=R/'ada_bw5_shoulder_checkpoint_ART_REVISE.blend';owned=json.loads((R/'records/final_owned_geometry.json').read_text())['objects']
def signature(o):
 h=hashlib.sha256();co=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',co);h.update(co.tobytes());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([[(g.group,round(g.weight,8)) for g in v.groups] for v in o.data.vertices]).encode())
 if o.data.shape_keys:
  for k in o.data.shape_keys.key_blocks:k.data.foreach_get('co',co);h.update(k.name.encode());h.update(co.tobytes())
 return h.hexdigest()
def load(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);return s
s=load(src);context={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in owned};expected={n:signature(bpy.data.objects[n]) for n in owned};action=bpy.data.objects['BW4_Armor_Independent_Rig'].animation_data.action.name
s=load(B4/'ada_armor_checkpoint_FINAL_ART_REVISE.blend');assert all(signature(bpy.data.objects[n])==h for n,h in context.items())
spec=importlib.util.spec_from_file_location('bw5apply',R/'operations/apply_bw5_shoulder.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.apply_bw5_shoulder(s);actual={n:signature(bpy.data.objects[n]) for n in owned};assert actual==expected
s=load(src);assert expected=={n:signature(bpy.data.objects[n]) for n in owned};assert bpy.data.objects['BW4_Armor_Independent_Rig'].animation_data.action.name==action
record={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'work_sha256':hashlib.sha256((R/'ada_bw5_shoulder_work.blend').read_bytes()).hexdigest(),'frozen_reopened_geometry_matches':True,'unchanged_nonowned_meshes_and_shape_key_records':len(context),'apply_replay_exact_mesh_and_weights_match':True,'shared_original_action_name_preserved':action,'status':'ART_REVISE','scope':'Apply replay verifies serialization on independent reopened BW4, not a universal construction recipe or second-body fit.'}
(R/'records/reopen_and_replay.json').write_text(json.dumps(record,indent=2))
names=json.loads(s['BW5_SHOULDER_EXPLICIT_ACTIVE']);s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=960;s.camera=bpy.data.objects['BW4_Camera_shoulder'];s.render.filepath=str(R/'captures/ordered_clay_key.png');bpy.ops.render.render(write_still=True)
key=bpy.data.objects['BW4_Key'];old=key.location.copy();key.location.x=-old.x;key.location.y=-old.y
from mathutils import Vector
key.rotation_euler=(Vector((0,0,1.3))-key.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'captures/ordered_clay_reversed_key.png');bpy.ops.render.render(write_still=True)
s=load(src);s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=960;s.display.shading.color_type='MATERIAL';s.camera=bpy.data.objects['BW4_Camera_shoulder']
black=bpy.data.materials.new('TEMP_BW5_CAGE_BLACK');black.diffuse_color=(.004,.004,.004,1)
for o in s.objects:
 if o.type=='MESH':o.hide_render=o.name not in names
for name in names:
 o=bpy.data.objects[name];o.data.materials.append(black)
 for m in o.modifiers:
  if m.type in ['SUBSURF','SOLIDIFY','BEVEL']:m.show_render=False
 w=o.modifiers.new('Actual raw cage edges','WIREFRAME');w.thickness=.0007;w.use_replace=False;w.use_even_offset=False;w.material_offset=1;w.offset=1
s.render.filepath=str(R/'captures/ordered_actual_control_cage.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(src.read_bytes()).hexdigest()==record['source_sha256'];print('REOPEN_REPLAY_CAGE_REVIEW_DONE')
