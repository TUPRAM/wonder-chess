import bpy,json,hashlib,shutil,sys,math,importlib.util
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];source=R/args[0]
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig']
owned=json.loads(s['BW6_owned_visible_parts']);names=owned+['BW6_BodyFit_Candidate']
def signatures():
 result={}
 for n in names:
  o=bpy.data.objects[n];data={'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'weights':[[[g.group,g.weight] for g in v.groups] for v in o.data.vertices],'world':[list(v) for v in o.matrix_world],'modifiers':[(m.name,m.type,m.show_viewport,m.show_render) for m in o.modifiers]}
  result[n]=hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
 return result
def cameras():return {o.name:{'matrix':[list(v) for v in o.matrix_world],'type':o.data.type,'lens':o.data.lens,'ortho_scale':o.data.ortho_scale} for o in s.objects if o.type=='CAMERA'}
bpy.context.view_layer.update();before=signatures();cams=cameras();action=rig.animation_data.action.name
clay=bpy.data.materials.get('BW6_Review_Clay') or bpy.data.materials.new('BW6_Review_Clay');clay.use_fake_user=True;clay.use_nodes=True;p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.43,.43,.43,1);p.inputs['Roughness'].default_value=.72
for layer in s.view_layers:layer.material_override=None
s['BW6_delivery_status']='ART_REVISE_NOT_COMPLETE_NOT_HUMAN_APPROVED';s['BW6_runtime_scope']='97-frame MPFB authoring study only; seven game clips, Unreal and reimport not executed for these new parts.';s.camera=bpy.data.objects['BW4_Camera_three_quarter']
work=R/'ada_bw6_upper_work.blend';frozen=R/'ada_bw6_upper_checkpoint_r004_ART_REVISE.blend'
assert not frozen.exists(),'Frozen checkpoint already exists; inspect before choosing new revision'
bpy.ops.wm.save_as_mainfile(filepath=str(work));shutil.copy2(work,frozen);sha=hashlib.sha256(frozen.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig'];bpy.context.view_layer.update();assert signatures()==before;assert cameras()==cams;assert rig.animation_data.action.name==action
out={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'work':str(work),'frozen':str(frozen),'sha256':sha,'signatures':before,'cameras':cams,'action':action,'native_save_reopen':'PASS','captures':[],'status':'ART_REVISE'}
s.render.threads=4;s.cycles.samples=20
def shot(label,view,kind='clay'):
 for layer in s.view_layers:layer.material_override=bpy.data.materials['BW6_Review_Clay'] if kind=='clay' else None
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('FINAL_'+label+'.png'));bpy.ops.render.render(write_still=True)
 out['captures'].append({'path':s.render.filepath,'source_sha256':sha,'camera':s.camera.name,'frame':s.frame_current,'kind':kind});(R/'records/final_verification.json').write_text(json.dumps(out,indent=2))
for view in ['front','profile','three_quarter','back']:shot('clay_'+view,view)
for view in ['front','three_quarter','back']:shot('color_layout_'+view,view,'color_layout_only')
lights=[o for o in s.objects if o.type=='LIGHT'];key=max(lights,key=lambda o:o.data.energy);matrix=key.matrix_world.copy();key.location.x=-key.location.x;key.rotation_euler=(Vector((0,0,1.32))-key.location).to_track_quat('-Z','Y').to_euler();shot('reversed_light','three_quarter');key.matrix_world=matrix
# Actual cage display: curve segments are made from the source control edges,
# not painted wireframes. All temporary diagnostics are created after freezing.
collection=bpy.data.collections.new('BW6_TEMP_CAGE_CAPTURE');s.collection.children.link(collection);black=bpy.data.materials.new('BW6_TEMP_CAGE_BLACK');black.diffuse_color=(.004,.004,.004,1)
wire_objects=[]
for n in owned:
 if 'PaddedCoat' in n or 'Bracer' in n or 'Strap' in n:continue
 o=bpy.data.objects[n];curve=bpy.data.curves.new('actual_cage_'+n,'CURVE');curve.dimensions='3D';curve.bevel_depth=.00065;curve.bevel_resolution=0
 for edge in o.data.edges:
  sp=curve.splines.new('POLY');sp.points.add(1)
  for p,index in zip(sp.points,edge.vertices):p.co=(*list(o.matrix_world@o.data.vertices[index].co),1)
 ob=bpy.data.objects.new(curve.name,curve);collection.objects.link(ob);curve.materials.append(black);wire_objects.append(ob)
# Material override would erase the diagnostic edge colors.
for n in owned:
 o=bpy.data.objects[n];o.data.materials.clear();o.data.materials.append(bpy.data.materials['BW6_Review_Clay'])
shot('actual_control_edges_front','front','actual_source_edges');shot('actual_control_edges_back','back','actual_source_edges')
for o in wire_objects:o.hide_render=True
# Reopen unchanged source before independent lowered pose and action frames.
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig'];s.render.threads=4;s.cycles.samples=20
rig.animation_data.action=None
for p in rig.pose.bones:p.matrix_basis.identity()
for side in ['R','L']:
 p=rig.pose.bones['upperarm01.'+side];basis=rig.matrix_world@p.bone.matrix_local;axis=(basis.to_3x3().inverted()@Vector((0,1,0))).normalized();p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion(axis,math.radians(32 if side=='R' else -32))
helper=bpy.data.objects['BW6_R_Cap_SecondaryHinge'];helper.animation_data.action=None;helper.rotation_euler=(0,math.radians(-8),0);helper.location=(0,0,0);bpy.context.view_layer.update()
out['lowered_pose']='Separate32deg anatomical arm-lowering diagnostic with documented -8deg cap support setting; not a changed shared rest pose or runtime action.'
shot('reference_like_lowered_front','front');shot('reference_like_lowered_three_quarter','three_quarter','color_layout_only')
assert hashlib.sha256(frozen.read_bytes()).hexdigest()==sha;assert hashlib.sha256(work.read_bytes()).hexdigest()==sha
(R/'records/final_verification.json').write_text(json.dumps(out,indent=2));print('BW6_FINAL_SAVE_REOPEN_CAPTURES_COMPLETE')
