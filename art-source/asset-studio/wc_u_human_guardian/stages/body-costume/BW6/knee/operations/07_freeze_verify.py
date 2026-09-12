import bpy,bmesh,json,hashlib,math,ast
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];B=R.parents[1];baseline=B/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend';candidate=R/'ada_bw6_knee_correction2.blend'
names=['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_Leggings','BW4_CONTEXT_BW1_Boot_Pair_SourceFit','BW4_CONTEXT_BW1_FootprintSole_R','BW4_CONTEXT_BW1_Greave_R']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def collect(path,rig_name):
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects[rig_name];rig.animation_data_clear()
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 out={'rest':{b.name:[list(r) for r in b.matrix_local] for b in rig.data.bones},'world':[list(r) for r in rig.matrix_world],'objects':{},'evaluated':{}}
 for n in names:
  o=bpy.data.objects[n];out['objects'][n]={'matrix':[list(r) for r in o.matrix_world],'vertices':sha_bytes(np.array([v.co[:] for v in o.data.vertices],dtype=np.float32).tobytes()),'weights':sha_bytes(repr([[(g.group,g.weight)for g in v.groups]for v in o.data.vertices]).encode()),'keys':len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0}
 for deg in [0,30,60,90,120]:
  rig.pose.bones['lowerleg01.R'].rotation_mode='XYZ';rig.pose.bones['lowerleg01.R'].rotation_euler.x=math.radians(deg);bpy.context.view_layer.update();out['evaluated'][deg]={}
  for n in names:
   e=bpy.data.objects[n].evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();out['evaluated'][deg][n]=np.array([e.matrix_world@v.co for v in m.vertices]);e.to_mesh_clear()
 return out
def sha_bytes(v):return hashlib.sha256(v).hexdigest()
a=collect(baseline,'BW4_Armor_Independent_Rig');b=collect(candidate,'BW6_Knee_Independent_Rig')
result={'baseline':str(baseline),'baseline_sha256':sha(baseline),'candidate':str(candidate),'candidate_sha256':sha(candidate),'source_rig_rest_same':a['rest']==b['rest'],'rig_world_same':a['world']==b['world'],'raw_context_same':a['objects']==b['objects'],'evaluated_context_max_delta_m':{d:{n:float(np.linalg.norm(a['evaluated'][d][n]-b['evaluated'][d][n],axis=1).max()) for n in names}for d in a['evaluated']},'scope':'Exact world-space evaluated context comparison after rig data copy; matching explicit local leg poses, source geometry/actions/rest unchanged on disk.'}
assert result['source_rig_rest_same'] and result['rig_world_same'] and result['raw_context_same'];assert max(v for d in result['evaluated_context_max_delta_m'].values()for v in d.values())<1e-7
bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);s.camera=bpy.data.objects['BW6_KneeCamera_three_quarter'];s['BW6_knee_status']='AUTHORING_ONLY_ART_REVISE';s['BW6_knee_gate']='Unresolved rigid overlap/crossing and deep-flexion coverage; no integration or forms approval.'
work=R/'ada_bw6_knee_work.blend';frozen=R/'ada_bw6_knee_checkpoint_ART_REVISE.blend';bpy.ops.wm.save_as_mainfile(filepath=str(work));bpy.ops.wm.save_as_mainfile(filepath=str(frozen),copy=True);result['work_sha256']=sha(work);result['frozen_sha256']=sha(frozen)
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);owned=json.loads(s['BW6_knee_owned']);result['reopened_owned']={n:{'verts':len(bpy.data.objects[n].data.vertices),'faces':len(bpy.data.objects[n].data.polygons),'modifiers':[m.type for m in bpy.data.objects[n].modifiers]}for n in owned};result['frozen_after_reopen']=sha(frozen)
def render(name):s.render.filepath=str(R/'captures'/name);bpy.ops.render.render(write_still=True)
# Actual undeformed cage geometry and edges, with armature/bone owners retained.
for n in owned:
 o=bpy.data.objects[n]
 for m in o.modifiers:m.show_render=False
 w=o.copy();w.data=o.data.copy();s.collection.objects.link(w);w.name=n+'_ActualCageOverlay';w.color=(.012,.018,.025,1);w.modifiers.clear();md=w.modifiers.new('Actual control edges','WIREFRAME');md.thickness=.0007
for o in s.objects:
 if o.type=='MESH' and o.name not in owned and not o.name.endswith('_ActualCageOverlay'):o.hide_render=True
render('retained_actual_cage.png')
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(31);s.camera=bpy.data.objects['BW6_KneeCamera_three_quarter'];s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.5,.5,.5)
s.display.shading.studiolight_rotate_z=.4;render('retained_clay_key_90.png');s.display.shading.studiolight_rotate_z=math.pi+.4;render('retained_clay_reversed_90.png')
(R/'records/preservation_reopen.json').write_text(json.dumps(result,indent=2));print('KNEE_FROZEN',json.dumps({k:v for k,v in result.items() if k not in ['evaluated_context_max_delta_m','reopened_owned']}))
