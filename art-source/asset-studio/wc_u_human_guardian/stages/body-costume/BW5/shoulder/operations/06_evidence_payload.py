import bpy,json,ast,numpy as np,math,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B4=R.parents[1]/'BW4/r001/armor';base=B4/'ada_armor_checkpoint_FINAL_ART_REVISE.blend';bsha=hashlib.sha256(base.read_bytes()).hexdigest()
tree=ast.parse((R/'operations/03_audit.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'audit_functions','exec'),globals())
query=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';tree=ast.parse(query.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['segment_triangle','self_audit']],type_ignores=[]),'self_functions','exec'),globals())
record={};owned=['BW4_Pauldron_R_'+n for n in ['Cap','Cap_LowerReturn','Lame1','Lame1_LowerReturn','Lame2','Lame2_LowerReturn']]
def setup(src):
 global s,rig,coat
 bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;rig=bpy.data.objects['BW4_Armor_Independent_Rig'];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];s.frame_set(1)
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960;s.render.resolution_y=960
def render(tag,cam='shoulder'):
 s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{tag}.png');bpy.ops.render.render(write_still=True)
def lower():
 action=rig.animation_data.action;rig.animation_data.action=None
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 p=rig.pose.bones['upperarm01.R'];basis=rig.matrix_world@rig.data.bones[p.name].matrix_local;localaxis=(basis.to_3x3().inverted()@Vector((0,1,0))).normalized();p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion(localaxis,math.radians(32));bpy.context.view_layer.update()
 return {'bone':p.name,'world_rotation_axis':[0,1,0],'angle_degrees':32,'bone_local_quaternion':list(p.rotation_quaternion),'wrist_world_m':list(rig.matrix_world@rig.pose.bones['hand.R'].head) if 'hand.R' in rig.pose.bones else None,'source_action_temporarily_unassigned_not_modified':action.name}
setup(base)
record['baseline_self_queries']={}
for n in owned:
 record['baseline_self_queries'][n]={}
 for raw in [True,False]:
  q,tri,b=geom(bpy.data.objects[n],raw);test=self_audit(q,[(i,t) for i,t in enumerate(tri)]);record['baseline_self_queries'][n]['raw' if raw else 'evaluated']=test['confirmed_nonadjacent_transverse_pairs']
record['baseline_lowered_pose']=lower()
setup(R/'shoulder_ordered_surface.blend');names=json.loads(s['BW5_SHOULDER_EXPLICIT_ACTIVE']);render('ordered_matched_rest');render('ordered_matched_rear','rear_three_quarter')
record['self_queries']={}
for n in names:
 record['self_queries'][n]={}
 for raw in [True,False]:
  q,tri,b=geom(bpy.data.objects[n],raw);test=self_audit(q,[(i,t) for i,t in enumerate(tri)]);record['self_queries'][n]['raw' if raw else 'evaluated']={'vertices':len(q),'triangles':len(tri),**test}
record['extra_samples']=[]
for fr in [19.25,19.5,19.75,20.25,20.5,24.5,24.75,25.25,25.5,48.5,49.5,72.5,73.5]:
 s.frame_set(int(fr),subframe=fr-int(fr));bpy.context.view_layer.update();gc=geom(coat);record['extra_samples'].append({'frame':fr,'coat':{n:cross(geom(bpy.data.objects[n]),gc) for n in names}})
s.frame_set(1);record['candidate_lowered_pose']=lower();render('ordered_lowered_reference_context');render('ordered_lowered_rear_context','rear_three_quarter');gc=geom(coat);record['lowered_coat_queries']={n:cross(geom(bpy.data.objects[n]),gc) for n in names}
# Reopen the unaltered action state for final serialization; comparison posing was never saved over it.
setup(R/'shoulder_ordered_surface.blend');s['BW5_SHOULDER_STATUS']='ART_REVISE_SELF_CROSSINGS_REMAIN';s['BW5_SHOULDER_SCOPE']='REJECTED LOCAL CONSTRUCTION. Cap and lowest-lame self-crossings remain despite cleared coat/inter-lame screens. Same 97 MPFB authoring frames plus 13 subframes and separate lowered diagnostic. Not game clips, no human approval. Torso/collar/head/bracer remain BW4 context.'
payload={'source_sha256':bsha,'active_objects':names,'objects':{},'scope':s['BW5_SHOULDER_SCOPE']}
for n in owned:
 o=bpy.data.objects[n];me=o.data;payload['objects'][n]={'vertices':[list(v.co) for v in me.vertices],'faces':[list(p.vertices) for p in me.polygons],'matrix_world':[list(row) for row in o.matrix_world],'hidden_superseded':n not in names,'material_names':[m.name for m in me.materials],'owner_bone':o.get('owner_bone'),'crease_edges':[x.value for x in me.attributes['crease_edge'].data] if 'crease_edge' in me.attributes else None,'properties':{k:o[k] for k in o.keys() if k.startswith('BW5')},'modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render,**({k:getattr(m,k) for k in ['thickness','offset','use_even_offset']} if m.type=='SOLIDIFY' else {})} for m in o.modifiers]}
(R/'records/final_owned_geometry.json').write_text(json.dumps(payload,indent=2))
s.camera=bpy.data.objects['BW4_Camera_shoulder'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_shoulder_work.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_shoulder_checkpoint_ART_REVISE.blend'),copy=True)
record['baseline_sha256_before']=bsha;record['baseline_sha256_after']=hashlib.sha256(base.read_bytes()).hexdigest();assert record['baseline_sha256_before']==record['baseline_sha256_after']
record['scope']=payload['scope'];(R/'records/ordered_additional_geometry_and_pose.json').write_text(json.dumps(record,indent=2))
print('EVIDENCE_PAYLOAD_DONE',flush=True)
